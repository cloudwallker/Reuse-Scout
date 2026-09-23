# 兼容性与公共文档约束

第二版整理日期：2026-09-21；宿主约定沿用 2026-09-13 的文档核对，未以新版原生验收重新证明。首批适配 Codex、Claude Code 的本地直接目录安装，共用 `skills/reuse-scout/`。真实宿主验收尚未完成，不标注“所有 Agent 兼容”。

| 项目 | Codex | Claude Code |
| --- | --- | --- |
| 项目级技能根 | `.agents/skills/` | `.claude/skills/` |
| 用户级技能根 | `~/.agents/skills/` | `~/.claude/skills/` |
| 直接安装后调用 | `$reuse-scout` | `/reuse-scout` |
| 手动调用策略 | openai.yaml 顶层 `policy.allow_implicit_invocation: false` | SKILL.md frontmatter `disable-model-invocation: true` |
| 公共正文与引用 | 相同 | 相同 |
| 元数据结构 | 本仓库校验器检查 | 本仓库校验器检查 |
| 原生发现/策略/工具行为 | 未验证 | 未验证 |

依据：[OpenAI Skills](https://learn.chatgpt.com/docs/build-skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[Agent Skills 格式](https://agentskills.io/specification)。宿主行为仍需按 [评估设计](EVALUATION.md) 在目标环境中核对。

保留 Codex 配置并增加 Claude Code 字段，是文档支持的适配方案；H18 单独验证两字段共存解析。不能由自定义校验器通过推断宿主接受所有字段。云端同步、插件市场和其他 Agent 不在本版已验证声明内。

## 公共文档约束

1. 公共正文采用“用户明确调用本技能”与宿主已有能力；`$` 和 `/` 入口在各宿主文档说明。
2. 文档从实际 GitHub 克隆地址和根目录出发，源使用 `./skills/reuse-scout`，目标由用户提供；不写作者盘符、用户名或设备位置。
3. 宿主约定目录如 `~/.claude/skills` 可保留。配置需要绝对路径时，由用户从安装步骤取得的真实目标填写。
4. 只维护 `skills/reuse-scout/`；本地副本按更新步骤完整替换，不合并、不自动同步，不将仓库开发说明纳入技能包。
5. 结构、文件操作、合成文本、真实宿主、比较评测分开记录，保留版本、日期、来源、权限和未执行项。
6. 用户已明确授权后续实施时，保留授权并交给普通开发流程，不因默认只研究重复阻塞同一步骤；H20 验证这一转换。

## 工具和校验范围

技能不提供文件或联网工具，使用宿主已有能力；不可用时按证据收敛，不强制 MCP 或全局安装。

本包校验契约包括固定名称、description 1—1024 字符、可选 compatibility 1—500 字符、可选 license 非空字符串、metadata 字符串映射和两宿主手动策略；不是各宿主完整 schema 实现。

本机 skill-creator 的 quick_validate.py 使用较窄字段白名单，不认识 `disable-model-invocation`。该拒绝单独记录，不删掉必需的 Claude Code 字段来迎合检查，也不将此拒绝当成 Codex 宿主解析结论。原生行为需 H01—H20 独立证据。
