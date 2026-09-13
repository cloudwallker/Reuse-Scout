"""仅测试临时合成仓库中的离线结构契约，不代表真实宿主行为。"""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "validate_skill.py"
PACKAGE = Path("skills/reuse-scout")
REFERENCES = (
    "feature-reuse.md", "bug-investigation.md",
    "evidence-and-safety.md", "budgets-and-fallbacks.md",
)
EXAMPLES = ("feature-reuse.md", "bug-investigation.md", "offline-report.md")
VALID_SKILL = (
    "---\nname: reuse-scout\ndescription: 合成测试技能\n"
    "disable-model-invocation: true\n---\n# 合成技能\n"
)
VALID_AGENT = (
    "interface:\n  display_name: Reuse Scout\n  short_description: 合成描述\n"
    "  default_prompt: '使用 $reuse-scout 研究'\n"
    "policy:\n  allow_implicit_invocation: false\n"
)


def report(kind):
    return (
        "---\nkind: " + kind + "\nvalidation_status: not-run\nsynthetic: true\n"
        "---\n# 合成材料\n未执行：此材料仅为示例。\n"
    )


def make_fixture(root):
    files = {PACKAGE / "SKILL.md": VALID_SKILL,
             PACKAGE / "agents/openai.yaml": VALID_AGENT,
             PACKAGE / "assets/report-template.md": report("template")}
    for name in REFERENCES:
        files[PACKAGE / "references" / name] = "# 合成参考\n参考内容。\n"
    for name in EXAMPLES:
        files[Path("examples") / name] = report("example")
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        files[Path(name)] = "合成许可文字，仅用于测试。\n"
        files[PACKAGE / name] = files[Path(name)]
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "尚未实现 tools/validate_skill.py")
        spec = importlib.util.spec_from_file_location("validator_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.validate = module.validate
        self.temp = tempfile.TemporaryDirectory(prefix="reuse-scout-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / PACKAGE
        make_fixture(self.root)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def append_skill(self, content):
        with (self.package / "SKILL.md").open("a", encoding="utf-8") as stream:
            stream.write("\n" + content + "\n")

    def assert_invalid(self, marker):
        errors = self.validate(self.root)
        self.assertTrue(errors, "损坏的合成包必须失败")
        self.assertIn(marker, "\n".join(errors))
        return errors

    def cli(self, *args, isolated=False, cwd=None):
        command = [sys.executable, "-X", "utf8"]
        if isolated:
            command.extend(["-I", "-S"])
        command.extend([str(SCRIPT), *args])
        return subprocess.run(command, cwd=cwd or self.root, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              env=dict(os.environ, PYTHONIOENCODING="utf-8"), check=False)

    def test_valid_minimal_package(self):
        self.assertEqual([], self.validate(self.root))

    def test_required_files_missing_or_empty(self):
        paths = [PACKAGE / "SKILL.md", PACKAGE / "agents/openai.yaml",
                 PACKAGE / "assets/report-template.md", Path("LICENSE"),
                 PACKAGE / "LICENSE", Path("THIRD_PARTY_NOTICES.md"),
                 PACKAGE / "THIRD_PARTY_NOTICES.md"]
        paths += [PACKAGE / "references" / name for name in REFERENCES]
        paths += [Path("examples") / name for name in EXAMPLES]
        for relative in paths:
            for content in (None, " \n\t"):
                with self.subTest(path=str(relative), empty=content is not None):
                    make_fixture(self.root)
                    if content is None:
                        (self.root / relative).unlink()
                    else:
                        self.write(relative, content)
                    self.assert_invalid(relative.as_posix())

    def test_skill_frontmatter_missing(self):
        self.write(PACKAGE / "SKILL.md", "# 缺少 frontmatter\n")
        self.assert_invalid("frontmatter")

    def test_skill_frontmatter_unclosed(self):
        self.write(PACKAGE / "SKILL.md", "---\nname: reuse-scout\n")
        self.assert_invalid("frontmatter")

    def test_skill_body_must_not_be_empty(self):
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("# 合成技能", "  "))
        self.assert_invalid("BODY")

    def test_skill_frontmatter_must_be_mapping(self):
        self.write(PACKAGE / "SKILL.md", "---\n- reuse-scout\n---\n# 技能\n")
        self.assert_invalid("frontmatter")

    def test_name_must_match_package(self):
        for value in ("another-scout", "12", "false", "null", "[]"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("reuse-scout", value))
                self.assert_invalid("name")

    def test_name_missing(self):
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("name: reuse-scout\n", ""))
        self.assert_invalid("name")

    def test_description_must_be_nonempty_string(self):
        for value in ("''", "'   '", "null", "true", "42", "[]", "{}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("合成测试技能", value))
                self.assert_invalid("description")

    def test_description_missing(self):
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("description: 合成测试技能\n", ""))
        self.assert_invalid("description")

    def test_description_character_length_boundaries_are_valid(self):
        for value in ("a", "a" * 1024, "中", "中" * 1024):
            with self.subTest(character=value[0], length=len(value)):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("合成测试技能", value))
                self.assertEqual([], self.validate(self.root))

    def test_description_exceeding_1024_characters_is_rejected(self):
        for value in ("a" * 1025, "中" * 1025, "' " + "中" * 1024 + "'"):
            with self.subTest(character=value[0]):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("合成测试技能", value))
                self.assert_invalid("description")

    def test_optional_compatibility_character_length_boundaries_are_valid(self):
        for value in ("a", "a" * 500, "中", "中" * 500):
            with self.subTest(character=value[0], length=len(value)):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "compatibility: " + value + "\ndescription:"))
                self.assertEqual([], self.validate(self.root))

    def test_optional_compatibility_must_be_nonempty_string(self):
        for value in ("''", "'   '", "null", "true", "42", "[]", "{}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "compatibility: " + value + "\ndescription:"))
                self.assert_invalid("compatibility")

    def test_optional_compatibility_exceeding_500_characters_is_rejected(self):
        for value in ("a" * 501, "中" * 501, "' " + "中" * 500 + "'"):
            with self.subTest(character=value[0]):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "compatibility: " + value + "\ndescription:"))
                self.assert_invalid("compatibility")

    def test_optional_license_nonempty_string_is_valid(self):
        for value in ("MIT", "详见 LICENSE", "'123'"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "license: " + value + "\ndescription:"))
                self.assertEqual([], self.validate(self.root))

    def test_optional_license_must_be_nonempty_string(self):
        for value in ("''", "'   '", "null", "true", "42", "[]", "{}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "license: " + value + "\ndescription:"))
                self.assert_invalid("license")

    def test_disable_model_invocation_must_be_present(self):
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
            "disable-model-invocation: true\n", ""))
        self.assert_invalid("disable-model-invocation")

    def test_disable_model_invocation_requires_boolean_true(self):
        for value in ("false", "'true'", "'false'", "1", "0", "null", "[]", "{}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "disable-model-invocation: true", "disable-model-invocation: " + value))
                self.assert_invalid("disable-model-invocation")

    def test_optional_user_invocable_boolean_true_is_valid(self):
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
            "description:", "user-invocable: true\ndescription:"))
        self.assertEqual([], self.validate(self.root))

    def test_optional_user_invocable_requires_boolean_true(self):
        for value in ("false", "'true'", "'false'", "1", "0", "null", "[]", "{}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "user-invocable: " + value + "\ndescription:"))
                self.assert_invalid("user-invocable")

    def test_legacy_yaml_invocation_booleans_are_rejected(self):
        for key in ("disable-model-invocation", "user-invocable"):
            for value in ("yes", "on", "YES", "On"):
                with self.subTest(key=key, value=value):
                    content = VALID_SKILL.replace("disable-model-invocation: true\n", "")
                    self.write(PACKAGE / "SKILL.md", content.replace(
                        "description:", key + ": " + value + "\ndescription:"))
                    self.assert_invalid("YAML")

    def test_frontmatter_field_errors_do_not_echo_synthetic_values(self):
        fake = "ghp_" + "C" * 36
        for key, value in (("description", fake + "a" * 1024),
                           ("compatibility", fake + "a" * 500),
                           ("license", "[" + fake + "]"),
                           ("disable-model-invocation", fake),
                           ("user-invocable", fake)):
            with self.subTest(key=key):
                content = VALID_SKILL
                if key == "description":
                    content = content.replace("合成测试技能", value)
                elif key == "disable-model-invocation":
                    content = content.replace("disable-model-invocation: true",
                                              "disable-model-invocation: " + value)
                else:
                    content = content.replace("description:", key + ": " + value + "\ndescription:")
                self.write(PACKAGE / "SKILL.md", content)
                errors = self.assert_invalid("FIELD")
                self.assertIn(key, "\n".join(errors))
                self.assertNotIn(fake, "\n".join(errors))

    def test_metadata_string_mapping_is_valid(self):
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
            "description:", "metadata:\n  version: '0.1'\n  author: synthetic\ndescription:"))
        self.assertEqual([], self.validate(self.root))

    def test_metadata_requires_string_mapping(self):
        for value in ("null", "[]", "scalar", "{version: 1}", "{true: text}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace(
                    "description:", "metadata: " + value + "\ndescription:"))
                self.assert_invalid("metadata")

    def test_duplicate_yaml_keys_are_rejected(self):
        cases = [(PACKAGE / "SKILL.md", VALID_SKILL.replace(
            "name: reuse-scout", "name: other\nname: reuse-scout")),
            (PACKAGE / "agents/openai.yaml", VALID_AGENT + "policy:\n  allow_implicit_invocation: false\n"),
            (PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(
                "allow_implicit_invocation: false", "allow_implicit_invocation: true\n  allow_implicit_invocation: false"))]
        for relative, content in cases:
            with self.subTest(path=str(relative)):
                make_fixture(self.root)
                self.write(relative, content)
                self.assert_invalid("YAML")

    def test_malformed_yaml_indentation_is_rejected(self):
        self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(
            "  short_description:", "   short_description:"))
        self.assert_invalid("YAML")

    def test_unsafe_yaml_tags_are_not_executed(self):
        self.write(PACKAGE / "agents/openai.yaml", "!!python/object/apply:builtins.str ['synthetic']\n")
        self.assert_invalid("YAML")

    def test_agent_root_and_interface_are_mappings(self):
        for content in ("[]\n", "interface: []\npolicy:\n  allow_implicit_invocation: false\n"):
            with self.subTest(content=content):
                self.write(PACKAGE / "agents/openai.yaml", content)
                self.assert_invalid("openai.yaml")

    def test_interface_requires_nonempty_strings(self):
        for key, value in (("display_name", "Reuse Scout"),
                           ("short_description", "合成描述"),
                           ("default_prompt", "'使用 $reuse-scout 研究'")):
            for replacement in ("null", "false", "0", "''", "[]"):
                with self.subTest(key=key, value=replacement):
                    self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(value, replacement))
                    self.assert_invalid(key)
            self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace("  " + key + ": " + value + "\n", ""))
            self.assert_invalid(key)

    def test_prompt_must_reference_exact_skill_name(self):
        self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace("$reuse-scout", "$different"))
        self.assert_invalid("default_prompt")

    def test_optional_icons_resolve_from_package_root(self):
        self.write(PACKAGE / "assets/synthetic.svg", "<svg></svg>\n")
        self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(
            "interface:\n", "interface:\n  icon_small: ./assets/synthetic.svg\n"
            "  icon_large: assets/synthetic.svg\n  brand_color: '#224466'\n"))
        self.assertEqual([], self.validate(self.root))

    def test_optional_interface_fields_require_nonempty_strings(self):
        for key in ("icon_small", "icon_large", "brand_color"):
            for value in ("null", "false", "7", "[]", "{}", "''"):
                with self.subTest(key=key, value=value):
                    self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(
                        "interface:\n", "interface:\n  " + key + ": " + value + "\n"))
                    self.assert_invalid(key)

    def test_optional_icons_reject_missing_absolute_external_and_escape(self):
        self.write("outside.svg", "<svg></svg>\n")
        for target in ("assets/missing.svg", "/absolute.svg", "C:/synthetic.svg",
                       "../../outside.svg", "https://example.invalid/icon.svg", "#anchor"):
            with self.subTest(target=target):
                self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(
                    "interface:\n", "interface:\n  icon_small: '" + target + "'\n"))
                self.assert_invalid("LINK")

    def test_policy_must_be_top_level(self):
        self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace(
            "policy:\n  allow_implicit_invocation: false", "  policy:\n    allow_implicit_invocation: false"))
        self.assert_invalid("policy")

    def test_policy_value_is_boolean_false_not_false_like(self):
        for value in ('"false"', "'false'", "0", "true", "null", "[]", "{}"):
            with self.subTest(value=value):
                self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace("false", value))
                self.assert_invalid("allow_implicit_invocation")

    def test_legacy_yaml_policy_booleans_are_rejected(self):
        for value in ("off", "no", "OFF", "No"):
            with self.subTest(value=value):
                self.write(PACKAGE / "agents/openai.yaml", VALID_AGENT.replace("false", value))
                self.assert_invalid("YAML")

    def test_policy_or_value_missing(self):
        for content in (VALID_AGENT.split("policy:")[0],
                        VALID_AGENT.split("policy:")[0] + "policy: {}\n"):
            with self.subTest(content=content):
                self.write(PACKAGE / "agents/openai.yaml", content)
                self.assert_invalid("policy")

    def test_commonmark_links_references_images_and_encoded_paths(self):
        self.write(PACKAGE / "assets/合成 image (1).png", "合成图片占位内容")
        self.append_skill(
            "[内联](references/feature-reuse.md#scope)\n"
            "[引用][ref]\n[ref]: references/bug-investigation.md \"参考\"\n\n"
            "![图片](assets/%E5%90%88%E6%88%90%20image%20%281%29.png)\n"
            "[查询](references/evidence-and-safety.md?view=1#section)\n"
            "[网络](https://example.invalid/page) [邮件](mailto:test@example.invalid) [锚点](#section)")
        self.assertEqual([], self.validate(self.root))

    def test_links_in_code_are_not_references(self):
        self.append_skill("`[代码](missing.md)`\n\n```md\n[代码](missing.md)\n```\n")
        self.assertEqual([], self.validate(self.root))

    def test_encoded_hash_is_a_filename_character(self):
        # %23 表示文件名里的 #，不能先解码再当成 URL 锚点切掉。
        self.write(PACKAGE / "references/synthetic#part.md", "# 合成\n")
        self.append_skill("[编码文件名](references/synthetic%23part.md)")
        self.assertEqual([], self.validate(self.root))

    def test_broken_inline_reference_image_and_unused_definition(self):
        for content in ("[缺失](references/missing.md)", "![缺失](assets/missing.png)",
                        "[缺失][target]\n\n[target]: missing.md", "[unused]: missing.md"):
            with self.subTest(content=content):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL + content + "\n")
                self.assert_invalid("LINK")

    def test_nested_reference_paths_resolve_from_source(self):
        self.write(PACKAGE / "references/feature-reuse.md", "[模板](../assets/report-template.md)\n")
        self.assertEqual([], self.validate(self.root))

    def test_unshipped_repository_file_is_rejected(self):
        self.write("docs/unshipped.md", "合成仓库文件\n")
        self.append_skill("[未分发文件](../../docs/unshipped.md)")
        self.assert_invalid("LINK")

    def test_absolute_drive_unc_and_traversal_links_are_rejected(self):
        targets = ("/etc/passwd", "C:/synthetic/file.md", "C:synthetic.md",
                   "//server/share/file.md", r"%5C%5Cserver%5Cshare%5Cfile.md",
                   "../../../outside.md", "%2E%2E/%2E%2E/outside.md",
                   "%2Fabsolute.md", "file:///C:/synthetic/file.md", "javascript:alert(1)")
        for target in targets:
            with self.subTest(target=target):
                self.write(PACKAGE / "SKILL.md", VALID_SKILL + "[非法](<" + target + ">)\n")
                self.assert_invalid("LINK")

    def test_directory_link_is_rejected(self):
        self.append_skill("[目录](references/)")
        self.assert_invalid("LINK")

    def test_raw_html_links_are_explicitly_unsupported(self):
        self.append_skill('<a href="missing.md">未支持</a>')
        self.assert_invalid("HTML")

    def test_symlink_escape_is_rejected(self):
        outside = self.root / "outside.md"
        outside.write_text("合成包外文件", encoding="utf-8")
        link = self.package / "references/escape.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("当前宿主未授予创建符号链接能力：" + type(exc).__name__)
        self.append_skill("[逃逸](references/escape.md)")
        self.assert_invalid("PATH")

    def test_symlinked_package_escape_is_rejected(self):
        outside = self.root / "outside-package"
        self.package.rename(outside)
        try:
            self.package.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("当前宿主未授予创建符号链接能力：" + type(exc).__name__)
        self.assert_invalid("PATH")

    def test_template_and_examples_require_explicit_status(self):
        paths = [(PACKAGE / "assets/report-template.md", "template")]
        paths += [(Path("examples") / name, "example") for name in EXAMPLES]
        for relative, kind in paths:
            for field in ("kind: " + kind, "validation_status: not-run", "synthetic: true"):
                with self.subTest(path=str(relative), field=field):
                    make_fixture(self.root)
                    self.write(relative, report(kind).replace(field + "\n", ""))
                    self.assert_invalid(field.split(":")[0])

    def test_report_status_types_and_values_are_strict(self):
        for old, new in (("kind: template", "kind: example"),
                         ("validation_status: not-run", "validation_status: passed"),
                         ("synthetic: true", "synthetic: 'true'"),
                         ("synthetic: true", "synthetic: 1")):
            with self.subTest(value=new):
                self.write(PACKAGE / "assets/report-template.md", report("template").replace(old, new))
                self.assert_invalid(old.split(":")[0])

    def test_legacy_yaml_synthetic_booleans_are_rejected(self):
        for value in ("yes", "on", "YES", "On"):
            with self.subTest(value=value):
                self.write(PACKAGE / "assets/report-template.md", report("template").replace(
                    "synthetic: true", "synthetic: " + value))
                self.assert_invalid("YAML")

    def test_unexecuted_marker_must_be_in_body(self):
        self.write(PACKAGE / "assets/report-template.md", report("template").replace(
            "synthetic: true", "synthetic: true\nnote: 未执行").replace("未执行：此材料仅为示例。", "仅为示例。"))
        self.assert_invalid("未执行")

    def test_false_success_claims_are_rejected(self):
        for claim in ("本地验证通过", "测试全部通过", "**本地验证通过**"):
            with self.subTest(claim=claim):
                self.write("examples/feature-reuse.md", report("example") + claim + "。\n")
                self.assert_invalid("CLAIM")

    def test_explicitly_negated_success_words_are_allowed(self):
        self.write("examples/feature-reuse.md", report("example") +
                   "不得声称本地验证通过；不能写测试全部通过。\n")
        self.assertEqual([], self.validate(self.root))

    def test_each_success_claim_needs_its_own_negation(self):
        self.write("examples/feature-reuse.md", report("example") +
                   "不能声称本地验证通过，但测试全部通过。\n")
        self.assert_invalid("CLAIM")

    def test_negating_failure_does_not_negate_success_claim(self):
        for claim in ("没有发现失败因此本地验证通过。", "没有失败所以测试全部通过。"):
            with self.subTest(claim=claim):
                self.write("examples/feature-reuse.md", report("example") + claim + "\n")
                self.assert_invalid("CLAIM")

    def test_licenses_and_notices_must_match_bytes(self):
        for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
            with self.subTest(name=name):
                make_fixture(self.root)
                self.write(PACKAGE / name, "不同合成文字\n")
                self.assert_invalid(name)

    def test_license_line_ending_difference_is_detected(self):
        (self.package / "LICENSE").write_bytes(b"synthetic\r\n")
        (self.root / "LICENSE").write_bytes(b"synthetic\n")
        self.assert_invalid("LICENSE")

    def test_synthetic_secret_patterns_are_redacted(self):
        fake = "ghp_" + "A" * 36
        self.append_skill("合成负例：" + fake)
        errors = self.assert_invalid("SECRET")
        self.assertNotIn(fake, "\n".join(errors))
        self.assertIn("SKILL.md:", "\n".join(errors))

    def test_yaml_parse_errors_do_not_echo_sensitive_values(self):
        fake = "ghp_" + "B" * 36
        self.write(PACKAGE / "agents/openai.yaml", "interface: [" + fake + "\n")
        errors = self.assert_invalid("YAML")
        self.assertNotIn(fake, "\n".join(errors))

    def test_deep_yaml_is_a_controlled_redacted_failure(self):
        value = "synthetic-deep-value"
        nested = "[" * 1500 + value + "]" * 1500
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("合成测试技能", nested))
        try:
            errors = self.assert_invalid("YAML")
        except RecursionError:
            self.fail("过深 YAML 应返回受控校验错误，不得抛出 RecursionError")
        self.assertNotIn(value, "\n".join(errors))
        result = self.cli("--root", str(self.root))
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("YAML", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertNotIn(value, result.stdout + result.stderr)

    def test_invalid_yaml_timestamp_is_a_controlled_redacted_failure(self):
        value = "2026-13-01"
        self.write(PACKAGE / "SKILL.md", VALID_SKILL.replace("合成测试技能", value))
        try:
            errors = self.assert_invalid("YAML")
        except ValueError:
            self.fail("无效 YAML 日期应返回受控校验错误，不得抛出 ValueError")
        self.assertNotIn(value, "\n".join(errors))
        result = self.cli("--root", str(self.root))
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("YAML", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertNotIn(value, result.stdout + result.stderr)

    def test_invalid_utf8_is_reported_without_traceback(self):
        (self.package / "references/feature-reuse.md").write_bytes(b"\xff\xfe")
        self.assert_invalid("READ")

    def test_cli_success_and_failure_exit_codes(self):
        passed = self.cli("--root", str(self.root))
        self.assertEqual(0, passed.returncode, passed.stdout + passed.stderr)
        (self.package / "SKILL.md").unlink()
        failed = self.cli("--root", str(self.root))
        self.assertEqual(1, failed.returncode, failed.stdout + failed.stderr)

    def test_cli_missing_dependencies_exit_two(self):
        result = self.cli("--root", str(self.root), isolated=True)
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("依赖", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_cli_bad_arguments_exit_two(self):
        result = self.cli("--unknown-argument")
        self.assertEqual(2, result.returncode)

    def test_cli_default_root_is_script_repository_not_cwd(self):
        copied = self.root / "tools/validate_skill.py"
        copied.parent.mkdir()
        shutil.copy2(SCRIPT, copied)
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        result = subprocess.run([sys.executable, str(copied)], cwd=elsewhere,
                                capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
