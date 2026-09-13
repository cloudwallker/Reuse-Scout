#!/usr/bin/env python3
"""校验并构建本地 Reuse Scout ZIP 和 SHA-256（仅开发用途，Python 3.9+）。

仅打包 validate_skill.PACKAGE_FILES 声明的文件；包内 metadata.version 须匹配 --version。
不安装、不联网、不发布。命令行输出沿用结构校验器的有限敏感字符串脱敏规则。
固定 ZIP 顺序、时间、权限并使用无压缩存储，避免压缩库版本影响字节。
输出目录需支持硬链接，以原子、排他方式放置完整文件；失败时清理本次产物。
构建期间应保持源目录不变；本工具不提供针对并发恶意文件替换的隔离。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile

if __package__:
    from . import validate_skill
else:
    # -I 隔离模式不将脚本目录加入 sys.path，仍从明确的同目录文件加载校验器。
    spec = importlib.util.spec_from_file_location(
        "reuse_scout_validator", Path(__file__).resolve().with_name("validate_skill.py"))
    validate_skill = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validate_skill)


class BuildError(RuntimeError):
    """源结构、分发边界或本地构建操作失败。"""

    def __init__(self, message: str):
        super().__init__(validate_skill._redact(message))


class _ArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        # argparse 自身会在非法值、未知参数和 usage 中拼入用户输入。
        super()._print_message(validate_skill._redact(message) if message else message, file)


def _print_redacted(message: str, file=None):
    print(validate_skill._redact(message), file=file)


def _version(value: str) -> str:
    number = r"(?:0|[1-9][0-9]*)"
    pattern = number + r"\." + number + r"\." + number
    pattern += r"(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?"
    if len(value) > 80 or not re.fullmatch(pattern, value):
        raise ValueError("版本应为安全的三段数字及可选预览后缀，如 0.1.1-preview.1")
    return value


def _within(path: Path, boundary: Path) -> bool:
    try:
        path.relative_to(boundary)
        return True
    except ValueError:
        return False


def _source_stat(path: Path):
    info = path.lstat()
    reparse = getattr(info, "st_file_attributes", 0) & getattr(
        stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if stat.S_ISLNK(info.st_mode) or reparse:
        raise BuildError("源路径不得使用符号链接、联接或其他重解析点：" + str(path))
    return info


def _check_ancestors(path: Path):
    for ancestor in reversed((path, *path.parents)):
        _source_stat(ancestor)


def _source_files(root: Path) -> dict[str, Path]:
    package = root / validate_skill.PACKAGE
    _check_ancestors(package)
    # 校验器还需要读取仓库示例和许可，不允许这些输入通过链接改变边界。
    for relative in (*validate_skill.EXAMPLE_FILES, "LICENSE", "THIRD_PARTY_NOTICES.md"):
        path = root / relative
        if path.exists() or path.is_symlink():
            _check_ancestors(path)
    # 先检查原始路径的链接，再统一解析比较边界（Windows 短路径可展开为长路径）。
    boundary = package.resolve()
    pending = [package]
    found = {}
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            info = _source_stat(path)
            if not _within(path.resolve(), boundary):
                raise BuildError("源路径越出技能分发目录：" + str(path))
            if stat.S_ISDIR(info.st_mode):
                pending.append(path)
            elif stat.S_ISREG(info.st_mode):
                found[path.relative_to(package).as_posix()] = path
            else:
                raise BuildError("分发源必须是普通文件或目录：" + str(path))
    extras = sorted(set(found) - set(validate_skill.PACKAGE_FILES))
    if extras:
        raise BuildError("技能包含未声明的额外文件：" + ", ".join(extras))
    return found


def _require_package_version(skill: Path, version: str):
    # 结构校验已通过；复用成熟 YAML 解析器读取版本，不按文本匹配元数据。
    try:
        lines = skill.read_text(encoding="utf-8-sig").splitlines()
        if not lines or lines[0].strip() != "---":
            raise ValueError("frontmatter missing")
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
        meta = validate_skill.yaml.load("\n".join(lines[1:end]),
                                        Loader=validate_skill.UniqueSafeLoader)
    except (UnicodeError, ValueError, StopIteration, RecursionError,
            validate_skill.yaml.YAMLError):
        raise BuildError("无法解析 SKILL.md frontmatter；请保持源目录不变后重试") from None
    metadata = meta.get("metadata") if isinstance(meta, dict) else None
    declared = metadata.get("version") if isinstance(metadata, dict) else None
    if not isinstance(declared, str) or not declared.strip():
        raise BuildError("SKILL.md metadata.version 必须为非空字符串")
    if declared != version:
        raise BuildError("SKILL.md metadata.version 与 --version 必须完全一致")


def build_release(root: Path, version: str, output_dir: Path = None) -> tuple[Path, Path]:
    """返回 ZIP 与校验和路径；拒绝覆盖，结构错误抛 BuildError，依赖错误原样传递。"""
    version = _version(version)
    # absolute 不解析链接，确保预检有机会拒绝链接形式的源目录及其祖先。
    root = Path(os.path.abspath(root))
    _source_files(root)
    errors = validate_skill.validate(root)
    if errors:
        raise BuildError("\n".join(errors))
    sources = _source_files(root)
    if set(sources) != set(validate_skill.PACKAGE_FILES):
        raise BuildError("校验后源文件清单发生变化；请保持源目录不变后重试")
    _require_package_version(sources["SKILL.md"], version)
    root = root.resolve()
    output = (Path(output_dir) if output_dir is not None
              else root / ".test-artifacts/releases").resolve()
    if _within(output, root / "skills"):
        raise BuildError("输出目录不得位于 skills 分发目录内")
    name = "reuse-scout-" + version + ".zip"
    zip_path = output / name
    checksum_path = output / (name + ".sha256")
    for destination in (zip_path, checksum_path):
        if os.path.lexists(destination):
            raise BuildError("拒绝覆盖已有产物：" + str(destination))

    output.mkdir(parents=True, exist_ok=True)
    installed = []
    try:
        with tempfile.TemporaryDirectory(prefix=".reuse-scout-build-", dir=output) as temporary:
            stage = Path(temporary)
            staged_zip = stage / name
            with zipfile.ZipFile(staged_zip, "x", compression=zipfile.ZIP_STORED) as archive:
                for relative in sorted(validate_skill.PACKAGE_FILES):
                    entry = zipfile.ZipInfo("reuse-scout/" + relative, (1980, 1, 1, 0, 0, 0))
                    entry.create_system = 3
                    entry.external_attr = (stat.S_IFREG | 0o644) << 16
                    entry.compress_type = zipfile.ZIP_STORED
                    archive.writestr(entry, sources[relative].read_bytes())
            digest = hashlib.sha256(staged_zip.read_bytes()).hexdigest()
            staged_checksum = stage / checksum_path.name
            staged_checksum.write_bytes((digest + "  " + name + "\n").encode("ascii"))
            # 同目录文件系统上的硬链接原子创建且不覆盖；ZIP 不会以部分内容出现。
            for source, destination in ((staged_zip, zip_path),
                                        (staged_checksum, checksum_path)):
                os.link(source, destination)
                installed.append(destination)
    except BaseException:
        for destination in reversed(installed):
            destination.unlink()
        raise
    return zip_path, checksum_path


def main(argv=None) -> int:
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, type=_version,
                        help="版本号，如 0.1.1-preview.1")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="源仓库根目录，默认为脚本所属仓库")
    parser.add_argument("--output-dir", type=Path,
                        help="输出目录，默认为源仓库的 .test-artifacts/releases")
    args = parser.parse_args(argv)
    try:
        zip_path, checksum_path = build_release(args.root, args.version, args.output_dir)
    except validate_skill.DependencyError as exc:
        _print_redacted(str(exc), file=sys.stderr)
        return 2
    except (BuildError, OSError, RuntimeError) as exc:
        _print_redacted("本地构建失败：" + str(exc), file=sys.stderr)
        return 1
    _print_redacted("本地分发包：" + str(zip_path))
    _print_redacted("SHA-256：" + str(checksum_path))
    _print_redacted("仅完成本地构建；不代表宿主行为验收或远程发布。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
