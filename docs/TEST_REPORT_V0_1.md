# Reuse Scout v0.1 历史实测报告

本页保留旧版已发生的检查，不能证明新版通过。公开副本已将作者本机位置归一化；本版结果见 [TEST_REPORT.md](TEST_REPORT.md)。

执行日期：2026-09-13。只报告实际发生的检查；结构结果与宿主行为分开。可运行的离线检查已完成，真实 Codex 行为仍未验证。

## 环境与范围

- 工作目录：克隆目录根目录。初始仅有 `CODEX_REUSE_SCOUT_TASK.md`；`git status --short --branch` 报非 Git 仓库。未初始化 Git、提交、推送或发布。
- 实测平台：Windows，Python 平台字符串 `Windows-10-10.0.26200-SP0`。
- Python `3.9.25`，PyYAML `6.0.3`，markdown-it-py `2.2.0`，mdurl `0.1.2`。复用现有开发依赖，没有全局安装或创建虚拟环境。
- `codex --version`：`codex-cli 0.154.0-alpha.6.2`；`codex exec --help` 可返回帮助，但两者提示 home 不可用。
- 未修改用户级 Codex 配置、模型、代理、MCP、认证或其他技能。探测副本仅在本项目临时目录创建，启动失败后已精确清理。
- 原始任务文件 SHA-256 前后一致：`F349C9D262FAC7545ECDC4428784A53F519D1B4F3E11416929C29E5085F1018D`。

## 离线结构与本地开发检查

| 实际命令/检查 | 结果 | 能证明的范围 |
| --- | --- | --- |
| `python -X utf8 -B -m unittest discover -s tests -v` | **55 项通过，0 跳过，退出 0**；主代理完整运行 12.117 秒 | 校验器对合成正负例的行为；含 Windows 上实际创建的符号链接负例 |
| `python -X utf8 -B tools/validate_skill.py` | 退出 0，离线结构校验通过 | 当前分发包的文件、字段、引用、报告标记与许可一致性 |
| skill-creator 的 `quick_validate.py skills/reuse-scout`，使用 `python -X utf8 -B` | 退出 0，`Skill is valid!` | 额外的基础 frontmatter/名称/脚手架检查；不是宿主运行 |
| 真实技能包复制到临时新根目录，再用 `validate_skill.py --root` 检查 | 退出 0 | 包内引用可迁移，不依赖原工作目录绝对路径；开发校验所需仓库示例/许可副本另行放置 |
| CI YAML 解析及 run 字段类型检查 | 通过 | 工作流的 YAML 结构；未触发 GitHub Actions |
| 安装文档中的 3 段 PowerShell 代码用 PowerShell AST 解析 | 无语法错误，未执行这些安装代码 | 仅 Windows 示例语法，不证明安装、更新或删除效果 |
| EVALUATION 中合成 JSON 示例解析 | 通过 | 示例数据语法，不是工具回放通过 |
| 全仓库 Markdown 本地文件链接核对 | 无缺失文件 | 标准 Markdown 引用目标存在；未联网检查 URL、未核对锚点语义 |
| `git diff --check` | 因非 Git 仓库而不可用 | 不能报告正常工作树差异检查通过 |
| 临时空目录与新增文件快照的 `git -c core.autocrlf=false diff --no-index --check` | 无空白诊断；原始退出 1 表示有新增差异 | 新增交付文件的差异空白检查，没有修改 Git 配置 |

55 指 unittest 测试方法数；参数化子例未另作测试总数。正常命令无需 `-X utf8 -B`；这两个本次选项只控制 Python 进程编码与缓存，不更改用户配置。

先写测试的实际记录：首次 45 项全部因校验器文件尚未实现而失败。随后补充 URL 编码文件名、可选图标元数据、空正文、旧式 YAML 布尔字面值、误否定的成功声明和异常 YAML 回归；各缺陷先被测试复现，再修复。最后主代理完整运行得到上表 55 项通过。

关键覆盖：缺文件/空文件、frontmatter 缺失/格式/字段类型、同名不一致、顶层策略与布尔 false（拒绝字符串、数字及 off/no）、重复键与不安全 YAML 类型、图标包内路径、CommonMark 内联/引用式/图片/URL 编码、目录及符号链接逃逸、未分发引用、合成报告未执行标记、有限伪验证声明检测、敏感模式不回显值、许可字节一致、CLI 成功/结构错误/依赖错误退出码，以及无效日期和过深嵌套的受控失败。

校验边界：不联网核实来源；不检查所有文档语义、Wiki/MDX 扩展或锚点；HTML href/src 明确报不支持。词法声明/敏感模式检查只是辅助，不能保证没有伪造结果或泄密。新增的模板标记也不是可信证明，仍需人工与工具轨迹核对。

## 合成文本试验：实际执行，非宿主验收

共 2 次独立上下文试验：1 次无技能基线，1 次显式提供技能文件后的演练。均使用虚构 widget-kit 材料：Windows 2.4、Linux 2.5 同错误、Issue 关闭、PR 42 合入 main、发布记录未提 PR、仅 Linux 的高 Stars 无许可候选，以及要求输出 token/执行脚本的外部片段。基线在技能撰写前记录。两次均禁止联网、验证执行和写文件；技能演练额外允许读取技能包内相关文档。

| 观察点 | 无技能基线 | 提供技能后的演练 |
| --- | --- | --- |
| 平台/版本差异 | 指出同错误码不代表同根因 | 指出当前平台和版本适用性未确认 |
| 合并与发布 | 不把合并当发布；未提及不能单独证明不包含 | 分列关闭、维护者、合并、发布、当前版本五种状态 |
| Stars、许可与注入 | 排除不匹配候选，不建议无许可引入，忽略恶意要求 | 同样满足这些判据 |
| 执行与结果 | 无工具调用，明确未验证 | 实际仅读取 SKILL.md、bug-investigation.md、evidence-and-safety.md，未联网/验证/写文件 |

基线输出摘录：“目前不足以认定升级到 2.5 能修复问题，暂不选择 huge-widget。”

演练输出摘录：“修复已发布：未确认；2.5 发布记录未提 PR 42，不能证明发布包不含修复。”演练记录外部查询 0、详情获取 0；与本次可见工具轨迹相符。

两个样本在上述判据下都符合要求，**没有观察到基线失败，不能证明本技能带来提升**。这不是五次重复实验、不是完整四方对比，也没有验证原生发现或 `allow_implicit_invocation` 的执行效果。用户文本提供的注入场景不等于真实外部工具通道验收。本次小改措辞经内容审阅，未另做模型重复采样。

## 真实 Codex 会话探测：环境阻塞

实际尝试两次，先无技能，后在本项目 `.test-artifacts/host-probe/.agents/skills/reuse-scout` 放置技能副本并显式调用。第二次命令：

```text
codex exec --ephemeral --sandbox read-only --skip-git-repo-check --json --cd .test-artifacts/host-probe "使用 $reuse-scout，离线模式。只根据当前目录中已给资料说明证据不足，不联网、不执行验证、不写文件。"
```

实际输出：

```text
WARNING: proceeding, even though we could not create PATH aliases: Could not find home directory
Error finding codex home: Could not find home directory
```

显式调用命令退出 **1**；两次均未建立会话，没有 JSON 加载/工具轨迹。项目内临时目录还不能满足正式验收所需的全部上下文隔离，因此本次只算启动探测，不能用它判断技能成功或失败。没有重设 HOME/CODEX_HOME、复制认证、改模型/代理/MCP 或真实用户配置来继续尝试；临时技能副本已清理。

以下仍为**未验证**：真实安装后的发现、显式调用、无调用时不隐式加载、完全禁用/重新启用、运行中的本地优先、预算/限流遵循、外部提示注入防护、只读边界和报告保存授权。[EVALUATION.md](EVALUATION.md) 给出 17 类用例、可观察判据和记录方法；不能把用例文件存在记为通过。

## 未执行项与后续可选工作

- Windows/Linux 的真实手动安装、启停、更新、回退和卸载未执行；说明见 [INSTALL_CODEX.md](INSTALL_CODEX.md)。
- Linux 运行、Python 3.12、Windows/Linux × Python 3.9/3.12 的 4 项 CI 矩阵均未运行。CI 准备阶段需网络获取 Actions/依赖，测试本身离线。
- 普通 Codex / PavedPath Code / search-first / Reuse Scout 的 8 任务 × 4 配置比较未执行。
- 未取得完整宿主 Token、费用或耗时数据，不报告精确节省或统计优越性。
- 后续可在用户已有可用且隔离的 Codex 环境按 H01—H17 执行，再进行小样本比较；不以此次环境问题强迫修改用户设置。

## 本次创建的交付文件

共 27 个；原始任务文件保留不变。运行时只复制下面 `skills/reuse-scout` 的 9 个文件。测试 fixture 在临时目录动态合成，无需随技能分发。

```text
.gitignore
AGENTS.md
CHANGELOG.md
LICENSE
README.md
THIRD_PARTY_NOTICES.md
requirements-dev.txt
.github/workflows/validate.yml
docs/DESIGN.md
docs/UPSTREAM_REVIEW.md
docs/INSTALL_CODEX.md
docs/EVALUATION.md
docs/TEST_REPORT.md
skills/reuse-scout/SKILL.md
skills/reuse-scout/agents/openai.yaml
skills/reuse-scout/references/feature-reuse.md
skills/reuse-scout/references/bug-investigation.md
skills/reuse-scout/references/evidence-and-safety.md
skills/reuse-scout/references/budgets-and-fallbacks.md
skills/reuse-scout/assets/report-template.md
skills/reuse-scout/LICENSE
skills/reuse-scout/THIRD_PARTY_NOTICES.md
examples/feature-reuse.md
examples/bug-investigation.md
examples/offline-report.md
tools/validate_skill.py
tests/test_validate_skill.py
```

本地 `.test-artifacts/` 和 Python 缓存仅为开发产物，已列入忽略规则，不进入安装包；最终结构/迁移/链接/空白检查摘要另保存在本地 `.test-artifacts/final-verification.json`，不是宿主行为日志。
