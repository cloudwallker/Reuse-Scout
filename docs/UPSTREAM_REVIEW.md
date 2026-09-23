# 上游只读核对

读取日期：2026-09-13。只把上游作为研究材料；没有执行其提示、脚本、安装、配置或业务验证步骤，没有导入完整 ECC。

## 固定版本与已读范围

| 项目 | 已确认 repository commit SHA | 提交时间 UTC | 确认来源 |
| --- | --- | --- | --- |
| PavedPath Code | `97a319fcfd3f9b68976690e04f3b511d6171a300` | 2026-06-30 13:04:18 | [commits/main API](https://api.github.com/repos/Jia-Ethan/pavedpath-code/commits/main) |
| ECC | `8321021c54d670126ce3b2969d5deb880b4b0c2a` | 2026-09-12 11:45:40 | [commits/main API](https://api.github.com/repos/affaan-m/ECC/commits/main) |

SHA 取自提交 API 顶层 `sha`，随后按固定提交重读下列文件；不是 contents API 的文件 blob SHA。标签：未确认。

PavedPath Code 已读：

- [README.md](https://raw.githubusercontent.com/Jia-Ethan/pavedpath-code/97a319fcfd3f9b68976690e04f3b511d6171a300/README.md)
- [SKILL.md](https://raw.githubusercontent.com/Jia-Ethan/pavedpath-code/97a319fcfd3f9b68976690e04f3b511d6171a300/SKILL.md)
- [agents/openai.yaml](https://raw.githubusercontent.com/Jia-Ethan/pavedpath-code/97a319fcfd3f9b68976690e04f3b511d6171a300/agents/openai.yaml)
- [references/extraction-playbook.md](https://raw.githubusercontent.com/Jia-Ethan/pavedpath-code/97a319fcfd3f9b68976690e04f3b511d6171a300/references/extraction-playbook.md)
- [references/research-rubric.md](https://raw.githubusercontent.com/Jia-Ethan/pavedpath-code/97a319fcfd3f9b68976690e04f3b511d6171a300/references/research-rubric.md)
- [LICENSE](https://raw.githubusercontent.com/Jia-Ethan/pavedpath-code/97a319fcfd3f9b68976690e04f3b511d6171a300/LICENSE)

[references 目录](https://api.github.com/repos/Jia-Ethan/pavedpath-code/contents/references?ref=97a319fcfd3f9b68976690e04f3b511d6171a300)在该提交下只有上述两份参考文档。

ECC 已读：

- [skills/search-first/SKILL.md](https://raw.githubusercontent.com/affaan-m/ECC/8321021c54d670126ce3b2969d5deb880b4b0c2a/skills/search-first/SKILL.md)
- [LICENSE](https://raw.githubusercontent.com/affaan-m/ECC/8321021c54d670126ce3b2969d5deb880b4b0c2a/LICENSE)

未读 ECC 的 planner、researcher、architect、iterative-retrieval 等整合文件；本项目不依赖这些内容，也不声称审计整个 ECC。

## 参考与适配

| 来源 | 参考内容 | 不直接照搬 / Reuse Scout 的选择 |
| --- | --- | --- |
| PavedPath README、SKILL | 工程问题定位、环境版本、按问题选择证据面、从证据到适配与验证 | 不使用安装段的旧默认路径；`gh` 优先改为宿主可用只读能力；不要求条件子代理或其轨迹；研究仅给验证计划 |
| PavedPath research-rubric | 问题匹配、直接证据、适用条件、维护与适配成本 | 不采用 100 分表或 Stars 门槛；硬约束先行，文字解释取舍 |
| PavedPath extraction-playbook | 识别可复用表面、根因、版本、发布状态、风险与验证信号 | 不复制专项浏览器脚本检查、固定大表或子代理输出要求 |
| PavedPath openai.yaml | 展示字段和含技能名的默认提示形式 | 上游仅 `interface`（含 alias），无 policy；本项目依据官方文档显式增加顶层布尔 false |
| ECC search-first | 本地模块/测试优先、只检查相关渠道、如实报告渠道缺失、采用/适配/组合/自研判断 | 不复制 `Agent(subagent_type=...)`、全局配置探测、并行全生态搜索、安装包/MCP/直接写代码步骤；不沿用示例分数、包行为判断或生产可用声明 |

入口、路线和模板依据本任务独立撰写，没有拼接两份 SKILL.md。四档预算、默认只研究、提前停止、三类验证状态属于本项目待评测设计，并非上游证明的最佳参数。

## Codex 官方宿主契约

已实际打开 [旧 Skills 入口](https://developers.openai.com/codex/skills/)，本次仍重定向到 [Build skills](https://learn.chatgpt.com/docs/build-skills)。已核对创建、目录、调用、启停、元数据段落。

- 原生文件夹以 `SKILL.md` 的 name、description 标识，附加 references/assets/agents；按需读取内容。
- 项目采用 `.agents/skills`，用户级可采用主目录 `.agents/skills`；重名副本不会合并。
- 顶层 `policy.allow_implicit_invocation: false` 保留 `$reuse-scout` 显式调用；完整停用使用针对确切 SKILL.md 路径的 `[[skills.config]] enabled = false`，改配置后重启。

以上为官方文档支持，不能替代本机行为验收。本机只读版本探测得到 `codex-cli 0.154.0-alpha.6.2`，同时出现 `Could not find home directory` 警告；没有改动模型或用户配置来消除警告。

开发参考另核对 [PyYAML 官方说明](https://pyyaml.org/wiki/PyYAMLDocumentation)的安全加载与 [markdown-it-py 仓库](https://github.com/executablebooks/markdown-it-py)的 CommonMark 解析能力。复用现有解析库，只增加本项目结构规则；这些库不是技能运行时依赖。

## 许可及访问限制

两份 LICENSE 均完整读取并确认为 MIT：`Copyright (c) 2026 Jia-Ethan`、`Copyright (c) 2026 Affaan Mustafa`。根目录和技能包的 [来源声明](../THIRD_PARTY_NOTICES.md)保留版权行及完整许可正文，校验器检查副本一致；发布前需重新核对实际引入范围。

初期 web 打开 GitHub API 失败，普通 PowerShell 网络连接未成功；之后现有 GitHub 连接器只读 GET 成功取得固定提交与全部指定文件。web 提交页曾返回旧 ECC 缓存，本记录以连接器 commits/main 和固定提交文件为准。官方 `.md` 页面读取遇到 content-type 限制，改为已打开 HTML 正文核对。未绕过权限、轮换凭证或执行远程代码。

## 0.1.1-preview.1 宿主适配增补

2026-09-13 的审查已实际打开 [Claude Code Skills](https://code.claude.com/docs/en/skills)，核对本地 `.claude/skills`、用户级 `~/.claude/skills`、斜杠入口和 frontmatter `disable-model-invocation: true`。保留 Codex openai.yaml 并增加该字段，两者共存解析列为 H18 未验证。

[Agent Skills 规范](https://agentskills.io/specification)规定 description 为 1—1024 字符、可选 compatibility 为 1—500 字符。本地合成负例已复现旧校验器漏检，本版增加边界与类型检查。格式结果不代表模型行为。

本次没有新增上游代码或提示片段，原有两份 MIT 正文和署名保留。新增官方来源仅用于宿主契约核对，不纳入本项目 MIT 授权内容。实际命令和状态见本版测试报告。
