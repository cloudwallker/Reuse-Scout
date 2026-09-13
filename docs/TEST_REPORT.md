# Reuse Scout 0.1.1-preview.1 实测报告

执行日期：2026-09-13。下列原始检查记录截至上传前准备阶段；其中 Git 状态、未提交/推送等描述是对应阶段的事实。维护者随后已授权检查后上传源码，中英文介绍不列宿主验收状态，本报告保留实际记录；后续检查与上传状态另行追加。离线结构、合成文件操作、宿主探测和比较评测分别报告。

## 环境与范围

- 所有开发命令从克隆目录根目录执行；公开说明使用相对路径，不保留作者本机地址。
- Windows，Python `3.9.25`、PyYAML `6.0.3`、markdown-it-py `2.2.0`、mdurl `0.1.2`。复用现有开发依赖，没有全局安装或创建虚拟环境。
- Codex CLI `0.154.0-alpha.6.2`；Claude Code `2.1.267`。版本和帮助可读取，不代表技能已经加载。
- 未修改用户配置、模型、代理、MCP、认证或其他技能。实际加载的 `.agents/skills/reuse-scout/` 旧副本未自动更新；维护源为 `skills/reuse-scout/`，旧副本已精确加入忽略规则。
- 当前目录仍不是 Git 仓库；未初始化 Git。原始任务文件保留，旧版结果另见 [v0.1 历史报告](TEST_REPORT_V0_1.md)，不能作为当前版本的行为证明。

本次使用的 `-X utf8 -B` 只控制 Python 进程编码和缓存。测试数据均在临时合成目录中创建，没有执行候选项目代码。

## 单元测试与结构检查

| 实际命令/检查 | 结果 | 能证明的范围 |
| --- | --- | --- |
| `python -X utf8 -B -m unittest discover -s tests -v` | **93 项通过，0 跳过，退出 0；24.542 秒** | 68 个校验器测试方法、25 个打包器测试方法；子例未另计数量 |
| `python -X utf8 -B tools/validate_skill.py` | 退出 0 | 当前包的字段、引用、合成报告标记、有限敏感模式和许可一致性 |
| skill-creator 的 `quick_validate.py skills/reuse-scout`，使用 `python -X utf8 -B` | **退出 1，未通过** | 该工具的字段白名单拒绝 `disable-model-invocation`；不是宿主运行结果 |
| 独立复核打包器最终修复及相关文档 | 未发现新的实质缺陷；25 项打包测试再次通过 | 代码与文档审阅，不是两宿主验收 |

先写测试的实际记录：校验器从原 55 项扩到 68 项，新增检查在旧实现上产生 42 个预期失败子例，修复后通过。打包器实现前的 19 项测试全部因工具缺失而失败；审阅又发现版本未强制一致、部分 CLI 输出未复用脱敏规则，补到 25 项后出现 11 个预期失败子例，再修复。最终主代理完整运行得到上表 93 项通过。

新增覆盖包括 description/compatibility 长度及类型、Claude 手动调用布尔字段、用户入口可用性，以及打包成员白名单、符号链接和 Windows junction 拒绝、版本匹配、输出不覆盖、失败回滚、解包字节、SHA-256 和有限输出脱敏。原 YAML/Markdown 安全解析、路径逃逸、示例标记及 CLI 退出码检查继续保留。

额外基础工具报错为 `Unexpected key(s) in SKILL.md frontmatter: disable-model-invocation`。保留 Claude Code 官方支持的字段，没有修改用户安装的校验工具来消除失败。项目自己的规则覆盖所需字段，但不能代替各宿主的真实解析；两字段共存列入 H18。

校验器不联网核实来源，不检查所有文档语义或锚点，也不保证识别所有伪验证声明或敏感内容。打包器要求输出文件系统支持硬链接；构建期间应保持源不变，不宣称防御并发恶意文件替换。

## 安装说明的合成文件操作

| 实际检查 | 结果 | 限制 |
| --- | --- | --- |
| README 与通用安装文档的 PowerShell 代码块 AST 解析 | 4 块无语法错误 | 未执行 README 的虚拟环境安装代码 |
| Codex/Claude Code × 项目级/用户级，共 4 组合成目录 | 首次复制字节一致；重复目标被拒绝；完整更新不残留旧文件；回退恢复旧字节；卸载后保留其他技能哨兵 | 用户目录查询和目标输入替换为合成目录，不是真实用户级安装 |
| `bash --version` | WSL 返回 `Bash/Service/CreateInstance/E_ACCESSDENIED` | 未运行 Bash 语法检查、Linux 复制步骤或 Linux 测试 |

复制使用安装文档中的 PowerShell 段落；更新、回退和卸载按文档步骤在已确认边界的临时目录中移动文件，未操作真实技能。测试脚本曾因 Windows 换行转换造成字节比较失败，改为比较实际源字节后四组通过；没有据此修改产品代码。

## 当前版本的真实 CLI 探测：未完成宿主验收

在仓库以外的临时合成工作区放置技能副本，不继承本项目 AGENTS.md。子进程仅保留必要系统环境变量，不传入 API/provider 凭证；没有重新设置 HOME/CODEX_HOME、复制认证或修改用户设置来继续尝试。

Codex 使用 `exec --ephemeral --ignore-user-config --sandbox read-only --skip-git-repo-check --json`，将 `--cd` 指向临时工作区，并明确要求离线、只读调用。实际退出 **1**：

```text
Error finding codex home: Could not find home directory
```

没有建立会话，不能判断技能发现、显式调用或行为。

Claude Code 使用 `--bare`、隔离设置来源、严格空 MCP 配置、禁止会话持久化与受限工具，以非交互模式调用 `/reuse-scout`。首次关闭设置来源；后续启用项目设置，分别测试最小对照技能和当前完整包。三次均返回：

```text
Unknown command: /reuse-scout
```

三次进程虽然退出 **0**，但均未发现调用入口；`num_turns: 0`、`duration_api_ms: 0`，后两次对照的认证来源均为 `none`。这是没有进入模型轮次的受限发现探测，**不能记为成功调用**。最小对照也失败，因此不能将原因归给本技能；当前探测配置没有建立有效的宿主验收环境。

两宿主的 H01—H20 均保持**未验证**，包括发现/字段共存、显式调用、禁止自动触发、启停、资源定位、跨轮授权、预算/限流、外部提示注入、只读边界与报告保存。[EVALUATION.md](EVALUATION.md) 的 40 个宿主/用例槽位不是 40 次已执行测试。

## 本地预览包

实际运行 `python -X utf8 -B tools/build_release.py --version 0.1.1-preview.1`，退出 0，生成：

```text
.test-artifacts/releases/reuse-scout-0.1.1-preview.1.zip
.test-artifacts/releases/reuse-scout-0.1.1-preview.1.zip.sha256
```

ZIP 为 **25,982 字节、9 个文件**，均位于 `reuse-scout/` 前缀下。实际解包后逐文件核对源字节；在新临时根目录补齐开发校验所需的仓库级示例和许可副本，再运行校验器，迁移检查通过。校验摘要与 `.sha256` 内容一致：

```text
ea63de6099876f40d78eceee3aab74679766ba4369f7cffbcd4423a267ad6833
```

这证明当前本地产物的内容一致性，不证明发布者身份或宿主行为；构建没有上传任何内容。

## 最终文档与工作区核对

- 公开 Markdown 的本地文件引用均存在，未发现作者本机地址或替换字符/连续问号编码异常；未联网验证所有 URL，也未核对锚点语义。发布说明中的计划版本链接要等标签创建后才生效。
- CI YAML 解析、run 字段类型及四项矩阵声明检查通过；EVALUATION 的合成 JSON 代码块可解析。这些不是 CI 或工具回放通过。
- 根目录与技能包内的 LICENSE、THIRD_PARTY_NOTICES.md 分别字节一致；本地加载的旧副本与修改前快照一致。当前 ZIP 再次与源逐文件字节核对一致。
- 原始任务文件 SHA-256 仍为 `F349C9D262FAC7545ECDC4428784A53F519D1B4F3E11416929C29E5085F1018D`。
- `git diff --check` 因非 Git 仓库不可用。修改前快照与当前交付文件临时快照的 no-index 检查，最初将 CRLF 中的 CR 报为行尾空白；以进程参数 `-c core.autocrlf=false -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol` 重查，保留其余空白检查，最终无诊断、原始退出 1 表示存在差异。没有修改 Git 配置。

上述最终核对摘要保存在本地 `.test-artifacts/final-release-verification.json`。

## 尚待完成的发布前事项

- 在已有可用且隔离的 Codex、Claude Code 环境分别完成真实安装和 H01—H20，再更新兼容性声明。当前只称优先适配的预览版本，不称所有 Agent 已验证可用。
- Linux、Python 3.12 以及 Windows/Linux × Python 3.9/3.12 的四项 GitHub Actions 矩阵未运行。工作流已包含本地打包检查，没有 Release 发布步骤。
- 本次未重新执行合成模型文本试验；旧版的两份样本只保存在历史报告。四方比较、完整 Token/费用/耗时测量仍未执行，不报告效果提升或节省比例。
- 按 [发布顺序](RELEASING.md) 审阅支持范围、发布说明、包和摘要；推送、远程标签及 Release 等待维护者明确允许。

本地 `.test-artifacts/` 中保存合成操作、CLI 探测和打包检查摘要，已列入忽略规则，不进入技能安装包，也不应作为公开原始日志上传。

## 上传前文件规范整理后的复核

2026-09-13，经维护者确认，仅整理忽略规则与维护文档，未修改技能、工具或测试源码，也未修改许可证。原始需求、历史报告和发布草稿保留。一次性发布计划保留本地并精确忽略，长期约束归入 DESIGN 与 RELEASING，公开引用已同步。

| 本次实际检查 | 结果与范围 |
| --- | --- |
| `python -X utf8 -B -m unittest discover -s tests -v` | 93 项通过、0 跳过，29.313 秒，退出 0 |
| `python -X utf8 -B tools/validate_skill.py` | 离线结构校验通过，退出 0 |
| 临时合成 Git 仓库中的 `git check-ignore --no-index` | 18 个正反例符合预期；覆盖本地副本、计划、缓存，以及应保留的共享配置、JSON/TXT、锁文件和长期文档 |
| README/安装文档 PowerShell AST | 5 个代码块无语法错误，含 ZIP 源目录替换行；未执行真实安装 |
| 公开文档引用与路径扫描 | 56 处本地引用目标存在，不指向被忽略计划；未发现个人绝对路径 |
| 许可、原始任务及现有预览 ZIP | 许可副本一致，原始任务哈希不变；ZIP 与技能源仍逐文件一致 |

当前目录仍不是 Git 仓库，已跟踪文件、暂存区和历史无法核查；合成 Git 仓库仅用于测试忽略规则，未初始化项目仓库。本次没有重新运行宿主验收、Bash/Linux 检查、远程 CI 或额外基础校验器，也未重新生成持久预览包；这些项目的既有未验证或失败状态保持不变。未删除本地文件、提交、推送或发布。

## 首次 GitHub 源码上传前检查

2026-09-13，维护者明确授权检查后上传到 `cloudwallker/Reuse-Scout`，并要求中英文介绍不列宿主验收未验证状态、测试报告保留事实。新增 README.en.md 与中英文切换入口；保留原有技能、工具、许可证和验收记录。

- 本次完整运行 `python -X utf8 -B -m unittest discover -s tests -v`：93 项通过、0 跳过，24.244 秒，退出 0。
- 本次 `python -X utf8 -B tools/validate_skill.py` 退出 0；`python -X utf8 -B tools/build_release.py --version 0.1.1-preview.1 --output-dir .test-artifacts/github-upload-build` 退出 0。
- 生成 ZIP 的 9 个成员与当前源逐文件字节一致，SHA-256 与前述预览包相同。构建产物仅保留本地，不纳入源码上传。
- 独立只读复核未发现阻塞源码上传、校验或打包的实质缺陷。GitHub 官方仓库 API 确认 CI 的 checkout@v7 与 setup-python@v7 标签存在。
- 目标远程初始没有 refs；本项目已初始化 Git，准备首次源码提交。上传仅包含经审查的项目文件，排除本地安装副本、缓存、临时记录和构建产物；不是创建 GitHub Release。
- 提交前敏感模式/个人路径扫描未命中，未发现超过 1 MiB 的候选文件；扫描不代表完整安全保证。原始需求与历史报告保留。

此处只记录上传前已发生的检查。远程提交和 CI 结果以对应 GitHub 实际记录及后续补充为准，不把本地通过记为远程通过。
