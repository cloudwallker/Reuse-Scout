"""仅在临时合成目录验证本地分发包构建，不证明宿主行为或远程发布。"""

import contextlib
import hashlib
import importlib
import io
import os
import posixpath
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "build_release.py"
PACKAGE = Path("skills/reuse-scout")
VERSION = "0.1.1-preview.1"
FILENAME = "reuse-scout-0.1.1-preview.1.zip"
MEMBERS = (
    "LICENSE", "SKILL.md", "THIRD_PARTY_NOTICES.md", "agents/openai.yaml",
    "assets/report-template.md", "references/budgets-and-fallbacks.md",
    "references/bug-investigation.md", "references/evidence-and-safety.md",
    "references/feature-reuse.md",
)


def make_fixture(root):
    report = (
        "---\nkind: template\nvalidation_status: not-run\nsynthetic: true\n"
        "---\n# 合成报告\n未执行。\n"
    )
    content = {name: "# 合成参考\n本文件仅用于测试。\n" for name in MEMBERS}
    content["SKILL.md"] = (
        "---\nname: reuse-scout\ndescription: 合成测试技能\n"
        "disable-model-invocation: true\nmetadata:\n  version: '0.1.1-preview.1'\n"
        "---\n# 合成技能\n"
        "[参考](references/feature-reuse.md)\n"
    )
    content["references/feature-reuse.md"] += (
        "\n[root](../SKILL.md)\n[peer][peer]\n\n[peer]: bug-investigation.md\n"
    )
    content["references/bug-investigation.md"] += (
        "\n[unused]: ../assets/report-template.md\n"
    )
    content["agents/openai.yaml"] = (
        "interface:\n  display_name: Reuse Scout\n  short_description: 合成描述\n"
        "  default_prompt: '使用 $reuse-scout 研究'\n"
        "policy:\n  allow_implicit_invocation: false\n"
    )
    content["assets/report-template.md"] = report
    for name, text in content.items():
        target = root / PACKAGE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        (root / name).write_bytes((root / PACKAGE / name).read_bytes())
    (root / "examples").mkdir()
    for name in ("feature-reuse.md", "bug-investigation.md", "offline-report.md"):
        (root / "examples" / name).write_text(
            report.replace("kind: template", "kind: example"), encoding="utf-8")
    (root / "README.md").write_text("开发仓库说明，不可分发。", encoding="utf-8")
    (root / "requirements-dev.txt").write_text("合成开发依赖", encoding="utf-8")


class BuildReleaseTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "尚未实现 tools/build_release.py")
        self.builder = importlib.import_module("tools.build_release")
        self.temp = tempfile.TemporaryDirectory(prefix="reuse-scout-release-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.package = self.root / PACKAGE
        self.output = Path(self.temp.name) / "output"
        make_fixture(self.root)

    def cli(self, *args, script=SCRIPT, isolated=False):
        command = [sys.executable, "-X", "utf8"]
        if isolated:
            command.extend(["-I", "-S"])
        command.extend([str(script), *args])
        return subprocess.run(command, cwd=self.temp.name, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              check=False)

    def build_cli(self, *args):
        return self.cli("--root", str(self.root), "--version", VERSION,
                        "--output-dir", str(self.output), *args)

    def assert_no_artifacts(self):
        if self.output.exists():
            self.assertEqual([], list(self.output.iterdir()))

    def test_source_files_accept_equivalent_resolved_boundary(self):
        canonical_root = self.root.with_name("canonical-source").resolve()
        original_resolve = Path.resolve

        def resolve_alias(path, *args, **kwargs):
            # 模拟 Windows 将整条路径的短名祖先展开；目录遍历和 lstat 仍使用真实夹具。
            try:
                relative = path.relative_to(self.root)
            except ValueError:
                return original_resolve(path, *args, **kwargs)
            return canonical_root / relative

        with mock.patch.object(Path, "resolve", new=resolve_alias):
            try:
                sources = self.builder._source_files(self.root)
            except self.builder.BuildError as exc:
                self.fail("等价路径别名不应被拒绝：" + str(exc))
        self.assertEqual({name: self.package / name for name in MEMBERS}, sources)

    def test_source_files_reject_resolved_escape(self):
        root = self.root.resolve()
        package = root / PACKAGE
        escaped = package / "LICENSE"
        original_resolve = Path.resolve

        def resolve_escape(path, *args, **kwargs):
            if path == escaped:
                return package.with_name("reuse-scout-outside") / "LICENSE"
            return original_resolve(path, *args, **kwargs)

        with mock.patch.object(Path, "resolve", new=resolve_escape):
            with self.assertRaisesRegex(self.builder.BuildError, "源路径越出"):
                self.builder._source_files(root)
        self.assert_no_artifacts()

    @unittest.skipUnless(os.name == "nt", "Windows 短路径测试")
    def test_windows_short_path_root_builds_archive(self):
        import ctypes
        from ctypes import wintypes

        get_short_path = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
        get_short_path.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        get_short_path.restype = wintypes.DWORD
        long_root = self.root.resolve()
        required = get_short_path(str(long_root), None, 0)
        if not required:
            self.skipTest("当前平台无法获取合成目录短路径：" + str(ctypes.get_last_error()))
        buffer = ctypes.create_unicode_buffer(required)
        written = get_short_path(str(long_root), buffer, required)
        self.assertTrue(0 < written < required, "获取 Windows 合成目录短路径失败")
        short_root = Path(buffer.value)
        if short_root == long_root:
            self.skipTest("当前临时目录未提供不同的 Windows 8.3 短路径")
        self.assertTrue(short_root.samefile(long_root))
        self.assertEqual(long_root, short_root.resolve())
        result = self.cli("--root", str(short_root), "--version", VERSION,
                          "--output-dir", str(self.output))
        self.assertEqual(0, result.returncode, result.stderr)
        with zipfile.ZipFile(self.output / FILENAME) as archive:
            self.assertEqual(["reuse-scout/" + name for name in MEMBERS],
                             archive.namelist())

    def test_archive_has_only_nine_declared_files_and_round_trips_bytes(self):
        result = self.build_cli()
        self.assertEqual(0, result.returncode, result.stderr)
        with zipfile.ZipFile(self.output / FILENAME) as archive:
            self.assertEqual(["reuse-scout/" + name for name in MEMBERS],
                             archive.namelist())
            extracted = Path(self.temp.name) / "unpacked"
            archive.extractall(extracted)
            for name in MEMBERS:
                self.assertEqual((self.package / name).read_bytes(),
                                 (extracted / "reuse-scout" / name).read_bytes())
            # Resolve every local Markdown target in the ZIP namespace itself.
            archive_members = set(archive.namelist())
            markdown = MarkdownIt("commonmark")
            checked = set()
            for source in archive_members:
                if not source.endswith(".md"):
                    continue
                environment = {}
                tokens = markdown.parse(archive.read(source).decode("utf-8-sig"), environment)
                targets = []

                def visit(items):
                    for token in items:
                        if token.type in ("link_open", "image"):
                            targets.append(token.attrGet(
                                "href" if token.type == "link_open" else "src"))
                        if token.children:
                            visit(token.children)

                visit(tokens)
                targets.extend(reference["href"] for reference
                               in environment.get("references", {}).values())
                for target in targets:
                    if target is None:
                        continue
                    parts = urlsplit(target)
                    if parts.scheme or parts.netloc or not parts.path:
                        continue
                    destination = posixpath.normpath(posixpath.join(
                        posixpath.dirname(source),
                        unquote(parts.path).replace("\\", "/")))
                    self.assertIn(destination, archive_members,
                                  source + " links to missing ZIP member " + target)
                    checked.add((source, target))
            self.assertGreaterEqual(len(checked), 4)
            self.assertGreaterEqual(len({source for source, _ in checked}), 3)
            self.assertIsNone(archive.testzip())
        expected_hash = hashlib.sha256((self.output / FILENAME).read_bytes()).hexdigest()
        self.assertEqual(expected_hash + "  " + FILENAME + "\n",
                         (self.output / (FILENAME + ".sha256")).read_text("ascii"))
        self.assertEqual([FILENAME, FILENAME + ".sha256"],
                         sorted(path.name for path in self.output.iterdir()))

    def test_archive_is_reproducible_despite_source_timestamps(self):
        first, _ = self.builder.build_release(self.root, VERSION, self.output)
        for path in self.package.rglob("*"):
            if path.is_file():
                os.utime(path, (1700000000, 1700000000))
        second, _ = self.builder.build_release(
            self.root, VERSION, Path(self.temp.name) / "another-output")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(second) as archive:
            for member in archive.infolist():
                self.assertEqual((1980, 1, 1, 0, 0, 0), member.date_time)
                self.assertEqual(0o100644, member.external_attr >> 16)

    def test_cli_default_root_comes_from_script_and_default_output_from_root(self):
        tools_dir = self.root / "tools"
        tools_dir.mkdir()
        shutil.copyfile(SCRIPT, tools_dir / SCRIPT.name)
        shutil.copyfile(SCRIPT.with_name("validate_skill.py"),
                        tools_dir / "validate_skill.py")
        result = self.cli("--version", VERSION, script=tools_dir / SCRIPT.name)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue((self.root / ".test-artifacts/releases" / FILENAME).is_file())

    def test_invalid_structure_produces_no_archive(self):
        (self.package / "agents/openai.yaml").write_text(
            "policy:\n  allow_implicit_invocation: true\n", encoding="utf-8")
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assertIn("FIELD", result.stderr)
        self.assert_no_artifacts()

    def test_links_to_nonexistent_exact_zip_members_block_archive(self):
        skill = self.package / "SKILL.md"
        original = skill.read_text(encoding="utf-8")
        for index, target in enumerate(("references/FEATURE-REUSE.md", "references/feature-reuse.md.")):
            with self.subTest(target=target):
                self.output = Path(self.temp.name) / ("output-" + str(index))
                skill.write_text(original + "[invalid](" + target + ")\n", encoding="utf-8")
                result = self.build_cli()
                self.assertEqual(1, result.returncode)
                self.assertIn("LINK", result.stderr)
                self.assert_no_artifacts()

    def test_help_example_uses_current_preview_version(self):
        result = self.cli("--help")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("0.2.0-preview.1", result.stdout)

    def test_package_version_is_required_and_must_be_nonempty_string(self):
        skill = self.package / "SKILL.md"
        valid = skill.read_text(encoding="utf-8")
        metadata = "metadata:\n  version: '0.1.1-preview.1'\n"
        variants = (
            "", "metadata: {}\n", "metadata:\n  version: ''\n",
            "metadata:\n  version: '  '\n", "metadata:\n  version: null\n",
            "metadata:\n  version: true\n", "metadata:\n  version: 123\n",
            "metadata:\n  version: []\n", "metadata:\n  version: {}\n",
        )
        for index, replacement in enumerate(variants):
            with self.subTest(index=index):
                self.output = Path(self.temp.name) / ("version-case-" + str(index))
                skill.write_text(valid.replace(metadata, replacement), encoding="utf-8")
                result = self.build_cli()
                self.assertEqual(1, result.returncode, result.stderr)
                self.assert_no_artifacts()

    def test_package_version_must_exactly_match_requested_release_version(self):
        skill = self.package / "SKILL.md"
        valid = skill.read_text(encoding="utf-8")
        for index, declared in enumerate(("9.8.7", " 0.1.1-preview.1 ")):
            with self.subTest(declared=declared):
                self.output = Path(self.temp.name) / ("mismatch-case-" + str(index))
                skill.write_text(valid.replace("'0.1.1-preview.1'", repr(declared)),
                                 encoding="utf-8")
                result = self.build_cli()
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertIn("metadata.version", result.stderr)
                self.assert_no_artifacts()

    def test_missing_required_file_produces_no_archive(self):
        (self.package / "LICENSE").unlink()
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assert_no_artifacts()

    def test_extra_files_are_rejected_even_when_not_markdown(self):
        for name in ("extra.md", "cache.pyc", "assets/private.bin"):
            with self.subTest(name=name):
                extra = self.package / name
                extra.write_bytes(b"synthetic extra file")
                result = self.build_cli()
                self.assertEqual(1, result.returncode)
                self.assertIn("额外文件", result.stderr)
                self.assert_no_artifacts()
                extra.unlink()

    def test_extra_file_errors_redact_synthetic_credentials(self):
        secret = "ghp_" + "A" * 36
        (self.package / (secret + ".bin")).write_bytes(b"synthetic extra file")
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertIn("[redacted]", result.stderr)
        with self.assertRaises(self.builder.BuildError) as caught:
            self.builder.build_release(self.root, VERSION, self.output)
        self.assertNotIn(secret, str(caught.exception))
        self.assert_no_artifacts()

    def test_argument_errors_redact_synthetic_credentials(self):
        secret = "ghp_" + "A" * 36
        for option in ("--version", "--unknown"):
            with self.subTest(option=option):
                result = self.build_cli(option, secret)
                self.assertEqual(2, result.returncode)
                self.assertNotIn(secret, result.stdout + result.stderr)
                self.assert_no_artifacts()

    def test_operation_errors_redact_synthetic_credential_paths(self):
        secret = "ghp_" + "A" * 36
        result = self.build_cli("--root", str(self.root / secret))
        self.assertEqual(1, result.returncode)
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertIn("[redacted]", result.stderr)
        self.assert_no_artifacts()

    def test_success_output_redacts_synthetic_credential_paths(self):
        secret = "ghp_" + "A" * 36
        self.output = Path(self.temp.name) / secret
        result = self.build_cli()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertIn("[redacted]", result.stdout)
        self.assertTrue((self.output / FILENAME).is_file())

    def test_existing_zip_or_checksum_is_never_overwritten(self):
        self.output.mkdir()
        for name in (FILENAME, FILENAME + ".sha256"):
            with self.subTest(name=name):
                existing = self.output / name
                existing.write_bytes(b"existing artifact")
                result = self.build_cli()
                self.assertEqual(1, result.returncode)
                self.assertEqual(b"existing artifact", existing.read_bytes())
                self.assertEqual([existing], list(self.output.iterdir()))
                existing.unlink()

    def test_output_cannot_be_inside_skills_distribution_directory(self):
        for output in (self.package, self.package / "releases", self.root / "skills/build"):
            with self.subTest(output=output):
                result = self.cli("--root", str(self.root), "--version", VERSION,
                                  "--output-dir", str(output))
                self.assertEqual(1, result.returncode)
                self.assertFalse((output / FILENAME).exists())

    def test_version_rejects_paths_and_unsafe_names(self):
        for version in ("../escape", "1.2.3/x", r"1.2.3\x", "1.2.3:stream", "", ".",
                        "1.2.3\nother", "v1.2.3", "01.2.3", "1.2.3-" + "x" * 80):
            with self.subTest(version=version):
                result = self.build_cli("--version", version)
                self.assertEqual(2, result.returncode)
                self.assert_no_artifacts()

    def test_missing_version_is_argument_error(self):
        result = self.cli("--root", str(self.root))
        self.assertEqual(2, result.returncode)
        self.assert_no_artifacts()

    def test_missing_dependencies_exit_two_without_output(self):
        result = self.cli("--root", str(self.root), "--version", VERSION,
                          "--output-dir", str(self.output), isolated=True)
        self.assertEqual(2, result.returncode)
        self.assertIn("requirements-dev.txt", result.stderr)
        self.assert_no_artifacts()

    def test_nonexistent_root_is_operation_failure(self):
        result = self.build_cli("--root", str(self.root / "missing"))
        self.assertEqual(1, result.returncode)
        self.assert_no_artifacts()

    def test_output_parent_file_is_operation_failure(self):
        self.output.write_bytes(b"existing file")
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assertEqual(b"existing file", self.output.read_bytes())

    def symlink_or_skip(self, link, target, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            self.skipTest("当前平台无法创建合成符号链接：" + str(exc))

    def test_internal_file_symlink_is_rejected(self):
        link = self.package / "references/feature-reuse.md"
        link.unlink()
        self.symlink_or_skip(link, self.package / "references/bug-investigation.md")
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assertIn("链接", result.stderr)
        self.assert_no_artifacts()

    def test_external_file_symlink_is_rejected(self):
        link = self.package / "LICENSE"
        link.unlink()
        self.symlink_or_skip(link, self.root / "LICENSE")
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assert_no_artifacts()

    def test_package_directory_symlink_is_rejected(self):
        target = self.root / "real-package"
        self.package.rename(target)
        self.symlink_or_skip(self.package, target, directory=True)
        result = self.build_cli()
        self.assertEqual(1, result.returncode)
        self.assert_no_artifacts()

    @unittest.skipUnless(os.name == "nt", "Windows 联接测试")
    def test_windows_directory_junction_is_rejected(self):
        link = self.package / "references"
        target = self.root / "real-references"
        link.rename(target)
        command = "New-Item -ItemType Junction -Path '{}' -Target '{}' | Out-Null".format(
            str(link).replace("'", "''"), str(target).replace("'", "''"))
        created = subprocess.run(["powershell", "-NoProfile", "-Command", command],
                                 capture_output=True, check=False)
        if created.returncode:
            self.skipTest("当前平台无法创建合成联接")
        try:
            result = self.build_cli()
            self.assertEqual(1, result.returncode)
            self.assertIn("链接", result.stderr)
            self.assert_no_artifacts()
        finally:
            # rmdir 仅移除该已确认的临时联接，不递归删除其目标。
            link.rmdir()

    def test_archive_write_failure_leaves_no_partial_artifacts(self):
        with mock.patch.object(zipfile.ZipFile, "writestr", side_effect=OSError("disk full")):
            with contextlib.redirect_stderr(io.StringIO()):
                code = self.builder.main(["--root", str(self.root), "--version", VERSION,
                                          "--output-dir", str(self.output)])
        self.assertEqual(1, code)
        self.assert_no_artifacts()

    def test_checksum_install_failure_rolls_back_zip(self):
        original_link = os.link

        def fail_checksum(source, destination, *args, **kwargs):
            if str(destination).endswith(".sha256"):
                raise OSError("synthetic checksum install failure")
            return original_link(source, destination, *args, **kwargs)

        with mock.patch.object(os, "link", side_effect=fail_checksum):
            with contextlib.redirect_stderr(io.StringIO()):
                code = self.builder.main(["--root", str(self.root), "--version", VERSION,
                                          "--output-dir", str(self.output)])
        self.assertEqual(1, code)
        self.assert_no_artifacts()


if __name__ == "__main__":
    unittest.main()
