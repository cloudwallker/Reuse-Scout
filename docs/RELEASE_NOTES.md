# Reuse Scout 0.1.1-preview.1

发布说明草稿：尚未发布，等待维护者明确允许。目标仓库：[cloudwallker/Reuse-Scout](https://github.com/cloudwallker/Reuse-Scout)。

文中的版本文档链接将在计划标签 `v0.1.1-preview.1` 随版本发布后生效；当前仅为可审阅草稿。

## 本版变化

- 首批适配 Codex 和 Claude Code，共享研究正文，分别声明手动调用。
- 保留本地优先、功能/故障路线、四档预算、证据状态和默认只研究边界。
- 安装从克隆根目录开始，覆盖两宿主项目级/用户级安装、调用、启停、更新、回退与卸载。
- 补充字段长度/类型和调用策略校验，增加技能 ZIP 与 SHA-256 构建工具。

## 安装入口

安装完整技能目录并保留许可：Codex 放入 `.agents/skills/`，Claude Code 放入 `.claude/skills/`，详见 [安装说明](https://github.com/cloudwallker/Reuse-Scout/blob/v0.1.1-preview.1/docs/INSTALL.md)。

Codex：`使用 $reuse-scout，快速模式。检查当前项目是否已有可复用实现，只研究。`

Claude Code：`/reuse-scout 快速模式。检查当前项目是否已有可复用实现，只研究。`

## 验证与限制

本地检查的命令、结果与范围见 [测试报告](https://github.com/cloudwallker/Reuse-Scout/blob/v0.1.1-preview.1/docs/TEST_REPORT.md)。真实宿主发现、字段共存、手动入口、禁止自动触发、预算和只读行为仍需独立验收；GitHub 四项 CI 矩阵的实际执行结果记录在测试报告中。

这是预览版，不声明所有 Agent 兼容，不将纯指令约束当成权限沙箱。未完成四方比较或完整用量测量，不宣称效果提升或 Token/费用节省。技能采用 MIT 许可，随包保留上游版权与条款。
