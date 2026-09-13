# Codex 安装与使用

核对日期：2026-09-13。面向本地 Codex CLI / IDE 扩展。官方依据：[Build skills](https://learn.chatgpt.com/docs/build-skills)；实际验收状态见 [测试报告](TEST_REPORT.md)。

## 安装

从 [公共安装步骤](INSTALL.md) 克隆仓库并进入根目录。PowerShell 使用 `$reuseHost = 'codex'`，Bash 使用 `reuse_host=codex`；项目级目标为 `.agents/skills/reuse-scout/`，用户级可选 `~/.agents/skills/reuse-scout/`。

Codex 从当前目录向仓库根目录检查 `.agents/skills`。同名技能不会合并；检查实际来源，避免调用旧副本。只复制 `skills/reuse-scout/` 完整目录，保留 agents/openai.yaml。

## 发现与调用

在目标项目启动新的 Codex 会话，使用 `/skills` 或输入 `$` 检查条目和来源。如果安装或更新没有显示，重启后复查。

```text
使用 $reuse-scout，快速模式。检查当前项目是否已有可复用的 CSV 导出能力，只研究，不修改代码。
```

```text
使用 $reuse-scout，标准模式。调查依赖错误，核对当前版本、平台、Issue、修复 PR 和发布状态。
```

```text
使用 $reuse-scout，离线模式。只根据当前项目与我提供的材料给建议，禁止外部查询。
```

深入模式也是自然语言约定，不是 CLI 参数。模式预算见 [README](../README.md)。

## 仅手动调用、禁用和启用

本包 agents/openai.yaml 保留顶层策略：

```yaml
policy:
  allow_implicit_invocation: false
```

这项 Codex 策略保留显式调用，禁止按提示匹配隐式调用。SKILL.md 中的 `disable-model-invocation: true` 是 Claude Code 适配字段，不能替代这里的策略；字段共存是否被当前 Codex 正确解析需独立验收。

完全禁用可结束相关会话，将已确认副本移到所有扫描目录之外；重新启用时原位恢复，在新会话复查。

也可自行在现有 `~/.codex/config.toml` 中为该技能新增或修改 `[[skills.config]]` 条目，将 `path` 设为安装步骤获得的 SKILL.md 绝对路径、`enabled` 设为 `false`。不要覆盖配置文件或重复同一路径条目。重新启用只改该项 `enabled = true` 或移除自建条目，重启后检查。本文不执行这些配置操作。

## 更新、回退和卸载

按 [公共更新步骤](INSTALL.md#更新回退和卸载) 从目标版本的克隆目录完整替换 `.agents/skills/reuse-scout/`，旧版备份到扫描目录之外。禁用配置的目标路径与状态应一并核对。

回退使用完整旧备份。卸载只移出或删除已确认副本，并清理自己为该路径建立的禁用条目。保留父级技能目录、其他技能及其他 Codex 配置；新会话确认结果。

## 验收

在合成项目中按 [EVALUATION](EVALUATION.md) 执行 H01—H20。记录版本、技能摘要、加载证据、工具轨迹和文件变化，不能由名称出现或回答风格推断行为通过。
