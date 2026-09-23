# Reuse Scout

**中文简介：** 供 Codex 和 Claude Code 手动调用的工程研究技能，先检查当前项目，再整理功能复用或故障调查的证据与适配建议。

**English overview:** A manually invoked research skill for Codex and Claude Code that inspects the current project before collecting evidence and suggesting reuse or debugging approaches.

## 使用 / Usage

产品文件在 `skills/reuse-scout/`。复制整个目录到宿主支持的技能目录后调用；技能默认只研究，不修改目标项目。

Product files are in `skills/reuse-scout/`. Copy the full directory to your host's skills location and invoke it explicitly. By default it researches without changing the target project.

```text
git clone https://github.com/cloudwallker/Reuse-Scout.git
```

## 许可 / License

见 [LICENSE](LICENSE)。 / See [LICENSE](LICENSE).
