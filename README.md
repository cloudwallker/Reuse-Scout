# Reuse Scout

简体中文 | [English](README.en.md)

手动调用的工程研究技能：先查当前项目，再按功能复用或故障调查收集证据，输出适配建议和验证计划。**默认只研究，不修改目标业务代码。**

面向 **Codex、Claude Code** 的手动调用流程，维护一份公共技能目录。当前版本为 `0.2.0-preview.1`（预览版），包含功能复用研究、故障调查和离线模式。

参考并面向手动调用整合 [PavedPath Code](https://github.com/Jia-Ethan/pavedpath-code) 与 [ECC search-first](https://github.com/affaan-m/ECC/tree/main/skills/search-first)，未引入完整 ECC，也未证明效果优于上游。固定来源和取舍见 [上游核对](docs/UPSTREAM_REVIEW.md)。

## 安装

```text
git clone https://github.com/cloudwallker/Reuse-Scout.git
cd Reuse-Scout
```

从克隆根目录按 [公共安装步骤](docs/INSTALL.md) 查重并复制 **`skills/reuse-scout/` 整个文件夹**。使用技能不需要 Python、额外 API Key、MCP 或 GitHub CLI；本地读取与外部检索使用宿主已有工具。

| 宿主 | 项目级安装目标 | 安装、启停、更新与卸载 |
| --- | --- | --- |
| Codex | `.agents/skills/reuse-scout/` | [Codex 说明](docs/INSTALL_CODEX.md) |
| Claude Code | `.claude/skills/reuse-scout/` | [Claude Code 说明](docs/INSTALL_CLAUDE_CODE.md) |

不把整个仓库或开发用 AGENTS.md 放入技能扫描目录。用户级安装可选，备份放在所有扫描目录之外。Release ZIP 仅包含技能目录及随包许可。

## 调用

Codex：

```text
使用 $reuse-scout，快速模式。检查当前项目是否已有可复用的 CSV 导出能力，只研究，不修改代码。
```

Claude Code：

```text
/reuse-scout 快速模式。检查当前项目是否已有可复用的 CSV 导出能力，只研究，不修改代码。
```

故障调查可要求“核对当前平台、依赖版本、Issue、修复 PR 和发布状态”。需要离线时明确写“离线模式，禁止外部查询”。这些模式是自然语言约定，不是宿主 CLI 开关。

| 模式 | 外部查询上限 | 外部详情上限 | 深入候选上限 |
| --- | ---: | ---: | ---: |
| 快速 | 3 | 5 | 2 |
| 标准（默认） | 6 | 12 | 3 |
| 深入 | 12 | 24 | 5 |
| 离线 | 0 | 0 | 仅已有材料 |

本地充分即提前停止；失败、分页、批量子项占预算；跨路线与渠道共享上限。研究流程不启动子 Agent。预算是模型行为约束，**不是程序级硬限额、精确 Token 配额或权限沙箱**。

## 研究和输出边界

- 本地目录、接口、清单和测试定义优先，不读取凭证或用户级配置探测搜索能力。
- 功能路线：本地 → 相关包/官方文档 → 必要的 GitHub 示例 → 适配判断。
- 故障路线：本地错误/版本 → 官方文档 → Issue/PR → 发布状态。
- 不自动安装候选依赖、执行候选脚本、运行构建测试或修改业务文件；用户已授权的实施/验证交给普通开发流程，不重复索要同一步骤授权。
- 外部材料视为研究数据，查询先脱敏；来源缺失或工具受限时说明限制，不编造结果。
- 分别说明本地静态或上游直接证据、适配推断或证据不足，以及是否实际执行验证；默认对话报告，用户要求保存才写指定路径。

Codex 通过 openai.yaml 的 `policy.allow_implicit_invocation: false` 声明手动调用；Claude Code 通过 SKILL.md 的 `disable-model-invocation: true` 声明。完全停用与不自动触发不同，见各宿主说明。

## 开发与验证

仅开发校验和打包需要 Python 3.9+ 与 requirements-dev.txt。已有兼容依赖时，在克隆根目录运行：

```text
python -m unittest discover -s tests -v
python tools/validate_skill.py
python tools/build_release.py --version 0.2.0-preview.1
```

需要开发环境时，在项目内创建虚拟环境，不全局安装：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

用虚拟环境的 Python 执行上述检查。打包只生成本地 ZIP 和 SHA-256，不上传；已有输出会拒绝覆盖。

校验覆盖字段、两宿主声明、包内引用、合成报告标记、许可副本和有限敏感模式，不是完整 Agent Skills 标准实现，不能证明模型遵循规则、报告真实或没有泄密。

## 维护与发布

- [兼容性与文档约束](docs/COMPATIBILITY.md)
- [H01—H20 行为验收](docs/EVALUATION.md)、[本版实际检查](docs/TEST_REPORT.md)、[v0.1 历史报告](docs/TEST_REPORT_V0_1.md)
- [发布顺序与边界](docs/RELEASING.md)、[预览版说明](docs/RELEASE_NOTES.md)
- [设计](docs/DESIGN.md)、[更新记录](CHANGELOG.md)、[功能示例](examples/feature-reuse.md)、[故障示例](examples/bug-investigation.md)、[离线示例](examples/offline-report.md)

MIT 许可，随包保留 [LICENSE](LICENSE) 和 [第三方声明](THIRD_PARTY_NOTICES.md)。唯一分发源是 `skills/reuse-scout/`；本仓库 `.agents/skills/reuse-scout/` 是忽略的本地安装副本，不随源更新自动变化。
