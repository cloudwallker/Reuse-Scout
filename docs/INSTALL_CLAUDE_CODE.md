# Claude Code 安装与使用

核对日期：2026-09-13。面向本地 Claude Code。官方依据：[Extend Claude with skills](https://code.claude.com/docs/en/skills)；实际验收状态见 [测试报告](TEST_REPORT.md)。

## 安装

从 [公共安装步骤](INSTALL.md) 克隆仓库并进入根目录。PowerShell 使用 `$reuseHost = 'claude-code'`，Bash 使用 `reuse_host=claude-code`；项目级目标为 `.claude/skills/reuse-scout/`，用户级可选 `~/.claude/skills/reuse-scout/`。

完整复制 `skills/reuse-scout/`，保留 references、assets 与许可。不需要额外 MCP、Python 依赖或把正文粘贴到 CLAUDE.md。agents/openai.yaml 是 Codex 附加元数据，不是 Claude Code 调用策略文件。

检查同名用户级、项目级和插件技能的来源，不套用 Codex 的重名处理方式。本文覆盖本地直接目录安装；云端同步和插件分发需另行验收。

## 发现与调用

在目标项目启动新 Claude Code 会话，输入 `/` 查找 reuse-scout。直接目录安装后的命令如下；缺失时核对目标直接包含 SKILL.md、来源与版本，然后重启复查。

```text
/reuse-scout 快速模式。检查当前项目是否已有可复用的 CSV 导出能力，只研究，不修改代码。
```

```text
/reuse-scout 标准模式。调查依赖错误，核对当前版本、平台、Issue、修复 PR 和发布状态。
```

```text
/reuse-scout 离线模式。只根据当前项目与我提供的材料给建议，禁止外部查询。
```

深入模式也写在命令后。`$reuse-scout` 是 Codex 示例，不是 Claude Code 的原生命令。

## 仅手动调用、禁用和启用

SKILL.md frontmatter 包含：

```yaml
disable-model-invocation: true
```

按官方文档，该字段禁止 Claude 自动加载，保留用户 `/reuse-scout` 调用。不要设置 `user-invocable: false`，否则隐藏用户入口；本包没有设置该字段。只研究和搜索预算仍是模型行为约束，不构成工具权限沙箱。

完全禁用时结束相关会话，将已确认副本移到所有扫描目录之外；恢复目录即可重新启用，在新会话复查。无需改用户配置；若用户自行建立过该技能的可见性覆盖，应同时核对对应条目。

已加载的正文可能跨轮保留在上下文中。验收“不调用”和“已禁用”必须用新会话，移动文件不能抹去旧会话文本。

## 更新、回退和卸载

按 [公共更新步骤](INSTALL.md#更新回退和卸载) 从目标版本的克隆目录完整替换 `.claude/skills/reuse-scout/`，避免旧资源残留。备份放在所有扫描目录之外。

回退使用完整旧备份。卸载只移出或删除这一已确认目录；保留 `.claude/skills`、其他技能和宿主设置。自行创建的仅针对本技能的可见性覆盖单独清理。每次操作后以新会话检查来源与命令。

## 验收

按 [EVALUATION](EVALUATION.md) 执行 H01—H20，使用 `/reuse-scout` 入口，重点检查手动策略、元数据共存、相对引用定位及后续实施授权。文件复制成功不代表 Claude Code 行为通过。
