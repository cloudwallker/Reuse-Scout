#!/usr/bin/env python3
"""Reuse Scout 离线结构校验（Python 3.9+，仅开发时需要依赖）。

支持 CommonMark 内联/引用式链接、图片及未使用的引用定义，解码 URL 路径后
检查目标文件；不联网验证 HTTP(S)/mailto，不验证锚点内容。代码块不作为链接。
HTML href/src 不在支持范围内，明确报错；不支持 Wiki/MDX 等扩展语法。
可选图标字段必须引用包内文件；brand_color 只检查非空字符串类型。
本包 frontmatter 检查 description/compatibility 的字符数、license 类型，以及
Codex / Claude Code 手动调用策略；不覆盖两宿主或 Agent Skills 的完整规范。
YAML 布尔值仅接受 true/false（含 YAML 约定的首字母或全大写形式），拒绝
YAML 1.1 的 yes/no/on/off，避免把 PyYAML 宽松解析误认为宿主兼容性。
报告标记和敏感串仅作有限词法检查，不证明报告真实、没有泄密或宿主行为正确。
"""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import os
from pathlib import Path
import posixpath
import re
import sys
from typing import Any
from urllib.parse import unquote, urlsplit


try:
    import yaml
    from markdown_it import MarkdownIt
except ImportError:
    yaml = None
    MarkdownIt = None


PACKAGE = Path("skills/reuse-scout")
PACKAGE_FILES = (
    "SKILL.md", "agents/openai.yaml", "references/feature-reuse.md",
    "references/bug-investigation.md", "references/evidence-and-safety.md",
    "references/budgets-and-fallbacks.md", "assets/report-template.md",
    "LICENSE", "THIRD_PARTY_NOTICES.md",
)
EXAMPLE_FILES = (
    "examples/feature-reuse.md", "examples/bug-investigation.md",
    "examples/offline-report.md",
)
SECRET_PATTERNS = (
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("api-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
)
CLAIMS = re.compile(r"本地验证通过|测试全部通过")
# 只承认直接修饰当前成功声明的有限否定词组；不理解任意自然语言。
# 必须紧邻声明（允许引号/Markdown 标记），不能因前文“没有失败”而豁免。
NEGATIONS = re.compile(
    r"(?:(?:不得|不能|不可|禁止|不要)(?:声称|宣称|写成|写|标记为)?"
    r"|并非|不是|不代表|(?:没有|尚未|未能|未|不)(?:声称|宣称|证明|证实))"
    r"[\s\"'“「『`*_]*$"
)
CLAUSE_BOUNDARY = re.compile(r"[。；;！？!?\n，,]|但是|然而|不过|但")


class _ArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        # argparse includes supplied option names and values in its diagnostics.
        super()._print_message(_redact(message) if message else message, file)


class DependencyError(RuntimeError):
    """开发依赖缺失；CLI 将其与结构错误分开报告。"""


if yaml is not None:
    class UniqueSafeLoader(yaml.SafeLoader):
        """保留 SafeLoader 行为，并拒绝重复或不可哈希的映射键。"""

    def _unique_mapping(loader, node, deep=False):
        loader.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            try:
                duplicate = key in result
            except TypeError:
                raise yaml.constructor.ConstructorError(
                    None, None, "映射键必须可哈希", key_node.start_mark)
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    None, None, "不允许重复映射键", key_node.start_mark)
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)

    def _explicit_boolean(loader, node):
        if node.value.lower() not in ("true", "false"):
            raise yaml.constructor.ConstructorError(
                None, None, "布尔值必须明确使用 true 或 false", node.start_mark)
        return loader.construct_yaml_bool(node)

    UniqueSafeLoader.add_constructor("tag:yaml.org,2002:bool", _explicit_boolean)


def _redact(text: str) -> str:
    for _, pattern in SECRET_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text


def _within(path: Path, boundary: Path) -> bool:
    try:
        path.relative_to(boundary)
        return True
    except ValueError:
        return False


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


class _HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.has_link = False

    def handle_starttag(self, tag, attrs):
        if any(name.lower() in ("href", "src", "srcset") for name, _ in attrs):
            self.has_link = True

    handle_startendtag = handle_starttag


def validate(repo_root: Path) -> list[str]:
    """返回不含匹配凭证值的错误列表；空列表仅表示离线结构检查通过。"""
    if yaml is None or MarkdownIt is None:
        raise DependencyError("缺少开发依赖：请在项目虚拟环境安装 requirements-dev.txt")

    errors: list[str] = []
    root = Path(repo_root).resolve()
    package = root / PACKAGE
    texts: dict[Path, str] = {}
    data: dict[Path, bytes] = {}
    members: set[str] = set()

    def issue(code: str, path: Path, message: str, line: int = 0):
        try:
            label = path.relative_to(root).as_posix()
        except ValueError:
            label = "<包外路径>"
        location = _redact(label) + (":" + str(line) if line else "")
        errors.append(f"{code} {location}: {message}")

    if not root.is_dir():
        issue("PATH", root, "仓库目录不存在")
        return errors
    try:
        if package.resolve() != package:
            issue("PATH", package, "技能包目录及祖先不得通过符号链接改变分发边界")
            return errors
    except (OSError, RuntimeError):
        issue("PATH", package, "无法解析技能包路径")
        return errors

    def read(path: Path, boundary: Path, required: bool = False):
        if path in texts:
            return
        try:
            if not _within(path.resolve(), boundary):
                issue("PATH", path, "文件或符号链接逃逸允许目录")
                return
            if not path.is_file():
                issue("FILE", path, "必要文件缺失或不是普通文件")
                return
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig")
        except (OSError, RuntimeError, UnicodeError):
            issue("READ", path, "无法读取 UTF-8 文本文件")
            return
        data[path] = raw
        texts[path] = text
        if required and not text.strip():
            issue("FILE", path, "必要文件为空")

    for relative in PACKAGE_FILES:
        read(package / relative, package, required=True)
    for relative in (*EXAMPLE_FILES, "LICENSE", "THIRD_PARTY_NOTICES.md"):
        read(root / relative, root, required=True)

    # 不跟随目录符号链接；包外链接在读取文件内容之前拒绝。
    if package.is_dir():
        for directory, dirs, files in os.walk(package, followlinks=False):
            for name in dirs + files:
                path = Path(directory) / name
                try:
                    safe = _within(path.resolve(), package)
                except (OSError, RuntimeError):
                    safe = False
                if not safe:
                    issue("PATH", path, "目录项或符号链接逃逸技能包")
                    continue
                if name in files:
                    members.add(path.relative_to(package).as_posix())
                if name in files and (path.suffix.lower() in (".md", ".yaml", ".yml")
                                      or path.name == "LICENSE"):
                    read(path, package)

    def parse_yaml(path: Path, text: str, line_offset: int = 0):
        try:
            return yaml.load(text, Loader=UniqueSafeLoader)
        except (yaml.YAMLError, RecursionError, ValueError, AttributeError, IndexError, OverflowError) as exc:
            mark = getattr(exc, "problem_mark", None)
            line = mark.line + 1 + line_offset if mark is not None else 0
            # 不输出解析异常的原文、问题行或键值，避免泄露合成/真实凭证。
            issue("YAML", path, "YAML 无效、嵌套过深、包含重复键或使用不安全类型", line)
            return None

    def frontmatter(path: Path):
        text = texts.get(path)
        if text is None:
            return None, "", 0
        lines = text.splitlines(keepends=True)
        if not lines or lines[0].strip() != "---":
            issue("FRONTMATTER", path, "缺少起始 frontmatter 分隔符")
            return None, text, 0
        end = next((index for index in range(1, len(lines))
                    if lines[index].strip() == "---"), None)
        if end is None:
            issue("FRONTMATTER", path, "frontmatter 缺少结束分隔符")
            return None, "", 0
        value = parse_yaml(path, "".join(lines[1:end]), line_offset=1)
        if not isinstance(value, dict):
            issue("FRONTMATTER", path, "frontmatter 必须为 YAML 映射")
            value = None
        return value, "".join(lines[end + 1:]), end + 1

    skill = package / "SKILL.md"
    meta, skill_body, skill_offset = frontmatter(skill)
    if meta is not None:
        if not skill_body.strip():
            issue("BODY", skill, "SKILL.md 正文不得为空")
        if meta.get("name") != "reuse-scout":
            issue("FIELD", skill, "name 必须与包名 reuse-scout 一致")
        description = meta.get("description")
        if not _string(description) or len(description) > 1024:
            issue("FIELD", skill, "description 必须为 1–1024 字符的非空字符串")
        if "compatibility" in meta:
            compatibility = meta["compatibility"]
            if not _string(compatibility) or len(compatibility) > 500:
                issue("FIELD", skill, "compatibility 必须为 1–500 字符的非空字符串")
        if "license" in meta and not _string(meta["license"]):
            issue("FIELD", skill, "license 必须为非空字符串")
        if meta.get("disable-model-invocation") is not True:
            issue("FIELD", skill, "disable-model-invocation 必须为布尔 true")
        if "user-invocable" in meta and meta["user-invocable"] is not True:
            issue("FIELD", skill, "user-invocable 如提供必须为布尔 true")
        if "metadata" in meta:
            extra = meta["metadata"]
            if not isinstance(extra, dict) or any(
                    not isinstance(key, str) or not isinstance(value, str)
                    for key, value in extra.items()):
                issue("FIELD", skill, "metadata 必须为字符串键和值组成的映射")

    agent = package / "agents/openai.yaml"
    icons: list[str] = []
    if agent in texts:
        config = parse_yaml(agent, texts[agent])
        if not isinstance(config, dict):
            issue("FIELD", agent, "openai.yaml 顶层必须为映射")
        else:
            interface = config.get("interface")
            if not isinstance(interface, dict):
                issue("FIELD", agent, "interface 必须为映射")
            else:
                for key in ("display_name", "short_description", "default_prompt"):
                    if not _string(interface.get(key)):
                        issue("FIELD", agent, key + " 必须为非空字符串")
                for key in ("icon_small", "icon_large", "brand_color"):
                    if key not in interface:
                        continue
                    if not _string(interface[key]):
                        issue("FIELD", agent, key + " 必须为非空字符串")
                    elif key in ("icon_small", "icon_large"):
                        icons.append(interface[key])
                prompt = interface.get("default_prompt")
                if isinstance(prompt, str) and not re.search(
                        r"\$reuse-scout(?![A-Za-z0-9_-])", prompt):
                    issue("FIELD", agent, "default_prompt 必须引用 $reuse-scout")
            policy = config.get("policy")
            if not isinstance(policy, dict):
                issue("FIELD", agent, "policy 必须为顶层映射")
            elif policy.get("allow_implicit_invocation") is not False:
                issue("FIELD", agent, "policy.allow_implicit_invocation 必须为布尔 false")

    bodies = {skill: (skill_body, skill_offset)}
    reports = [(package / "assets/report-template.md", "template")]
    reports.extend((root / relative, "example") for relative in EXAMPLE_FILES)
    for path, kind in reports:
        status, body, offset = frontmatter(path)
        bodies[path] = (body, offset)
        if status is not None:
            if status.get("kind") != kind:
                issue("REPORT", path, "kind 必须为 " + kind)
            if status.get("validation_status") != "not-run":
                issue("REPORT", path, "validation_status 必须为 not-run")
            if status.get("synthetic") is not True:
                issue("REPORT", path, "synthetic 必须为布尔 true")
        if path in texts and "未执行" not in body:
            issue("REPORT", path, "正文必须明确标记未执行")
        for clause in CLAUSE_BOUNDARY.split(body):
            previous_end = 0
            for match in CLAIMS.finditer(clause):
                if not NEGATIONS.search(clause[previous_end:match.start()]):
                    issue("CLAIM", path, "合成材料包含未否定的成功声明；需人工复核")
                previous_end = match.end()

    parser = MarkdownIt("commonmark")
    # 让解析器保留 file/javascript 等目的地址，由下面的统一策略明确拒绝。
    parser.validateLink = lambda _url: True

    def check_link(path: Path, target: str, line: int,
                   base: Path = None, local_only: bool = False):
        decoded = unquote(target)
        if (decoded.startswith(("/", "\\"))
                or re.match(r"^[A-Za-z]:", decoded)
                or any(ord(char) < 32 for char in decoded)):
            issue("LINK", path, "链接使用绝对、盘符、UNC 或控制字符路径", line)
            return
        try:
            # 先拆分 URL，避免把文件名中的 %23 / %3F 误认为锚点或查询。
            parts = urlsplit(target)
        except ValueError:
            issue("LINK", path, "无法解析链接地址", line)
            return
        if parts.scheme:
            if local_only or parts.scheme.lower() not in ("http", "https", "mailto"):
                issue("LINK", path, "链接使用不支持的 URI 协议", line)
            return
        if not parts.path:
            if local_only:
                issue("LINK", path, "图标必须引用包内的实际文件", line)
            return
        try:
            decoded_path = unquote(parts.path).replace("\\", "/")
            source_base = (base or path.parent).relative_to(package).as_posix()
            member = posixpath.normpath(posixpath.join(source_base, decoded_path))
            resolved = ((base or path.parent) / decoded_path).resolve()
            if not _within(resolved, package):
                issue("LINK", path, "本地链接逃逸技能包或指向未分发文件", line)
            elif not resolved.is_file() or member not in members:
                issue("LINK", path, "本地链接目标文件不存在或指向目录", line)
        except (OSError, RuntimeError, ValueError):
            issue("LINK", path, "无法解析本地链接路径", line)

    for icon in icons:
        check_link(agent, icon, 0, base=package, local_only=True)

    for path, text in sorted(texts.items()):
        for secret_type, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                issue("SECRET", path, "疑似敏感字符串类型=" + secret_type,
                      text.count("\n", 0, match.start()) + 1)
        if path.suffix.lower() != ".md" or not _within(path, package):
            continue
        body, offset = bodies.get(path, (text, 0))
        environment: dict[str, Any] = {}
        tokens = parser.parse(body, environment)

        def visit(items, inherited_line=1):
            for token in items:
                line = token.map[0] + 1 + offset if token.map else inherited_line
                if token.type in ("link_open", "image"):
                    target = token.attrGet("href" if token.type == "link_open" else "src")
                    if target is not None:
                        check_link(path, target, line)
                if token.type in ("html_inline", "html_block"):
                    html = _HTMLLinks()
                    html.feed(token.content)
                    if html.has_link:
                        issue("HTML", path, "HTML 链接未受支持，请使用 Markdown 链接", line)
                if token.children:
                    visit(token.children, line)

        visit(tokens)
        for reference in environment.get("references", {}).values():
            line = reference.get("map", [0])[0] + 1 + offset
            check_link(path, reference["href"], line)

    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        original, distributed = root / name, package / name
        if original in data and distributed in data and data[original] != data[distributed]:
            issue("LICENSE", distributed, "与仓库根目录同名文件字节不一致")
    return list(dict.fromkeys(errors))


def main(argv=None) -> int:
    argument_parser = _ArgumentParser(description=__doc__)
    argument_parser.add_argument("--root", type=Path,
                                 default=Path(__file__).resolve().parents[1],
                                 help="待校验仓库根目录，默认为脚本所属仓库")
    args = argument_parser.parse_args(argv)
    try:
        errors = validate(args.root)
    except DependencyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"离线结构校验失败：{len(errors)} 项问题。", file=sys.stderr)
        return 1
    print("离线结构校验通过；不代表 Codex / Claude Code 宿主行为、语义真实性或无泄密保证。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
