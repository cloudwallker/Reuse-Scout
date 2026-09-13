# 发布顺序

目标仓库：[cloudwallker/Reuse-Scout](https://github.com/cloudwallker/Reuse-Scout)。准备版本 `0.1.1-preview.1`，计划标签 `v0.1.1-preview.1`（尚未创建）。**只有维护者明确允许后才能推送、创建远程标签或发布 GitHub Release。** 本地打包不等于已发布。

## 1. 确认支持范围

首批适配 Codex 和 Claude Code，公共正文配合宿主策略。支持声明以 [兼容性矩阵](COMPATIBILITY.md) 和 [实际报告](TEST_REPORT.md) 为准；其他 Agent 不标为已验证。

## 2. 检查源码和许可

在克隆根目录确认技能版本、CHANGELOG 与发布说明一致，只将 `skills/reuse-scout/` 纳入技能 ZIP，保留 LICENSE 和 THIRD_PARTY_NOTICES.md，根目录与包内副本保持字节一致。

核对 Git 暂存清单，排除本地 `.agents/skills/reuse-scout/`、`.claude/skills/reuse-scout/`、一次性执行记录及 `.test-artifacts/`、虚拟环境、缓存、私有日志和本机地址。忽略规则不影响已跟踪文件，需人工确认。复查实际引入范围、名称与署名。

源码仓库保留共享 AGENTS.md、源码、测试、依赖清单、实际使用的锁文件和长期文档；不笼统忽略 JSON、TXT、MD 或宿主配置目录。原始需求、历史测试报告与发布说明可保留供追溯；一次性执行计划留在本地，其长期约束归入设计和本流程。当前项目不需要额外凭据配置模板。

## 3. 本地验证

```text
python -m unittest discover -s tests -v
python tools/validate_skill.py
git diff --check
```

非 Git 目录不能把最后一项记为通过，使用临时快照 no-index 检查并说明限制。安装说明需语法与合成文件操作检查，不能替代宿主验收。另核对公共文档本地链接、个人路径、CI YAML、许可副本及包解压后的引用迁移；逐项记录实际结果和未执行项。

## 4. 宿主验收和 CI

按 [EVALUATION](EVALUATION.md) 为每宿主执行 H01—H20，记录版本、模型、技能 SHA、加载证据、工具轨迹和文件变化。没有安全且可用的隔离环境时保留未验证；不得复制真实凭证或修改用户设置来凑验收。

在远程操作获授权且源码已进入目标仓库后，运行现有 Windows/Linux × Python 3.9/3.12 四项 CI 矩阵，核对真实运行记录。本地 Windows 运行或 YAML 解析不等于远程 CI 通过。

预览版可完整披露未验证项，由维护者决定是否接受；正式支持声明等待对应验收。效果或费用优势没有比较数据前不宣传。

## 5. 本地预览包

在克隆根目录运行：

```text
python tools/build_release.py --version 0.1.1-preview.1
```

默认输出：

```text
.test-artifacts/releases/reuse-scout-0.1.1-preview.1.zip
.test-artifacts/releases/reuse-scout-0.1.1-preview.1.zip.sha256
```

拒绝覆盖既有输出；重新构建可用 `--output-dir` 指定新目录，或确认后手动移走旧产物。构建期间保持源不变。输出文件系统须支持硬链接，如常规 NTFS/Linux 文件系统，以排他方式放置完整产物。

解包到临时目录，核对 `reuse-scout/` 前缀下的 9 文件、源字节、许可、元数据与引用可迁移性。SHA-256 用于核对内容，不证明发布者身份或宿主行为。

## 6. 等待明确发布允许

先给维护者查看 [发布说明](RELEASE_NOTES.md)、修改清单、真实测试结果、未验证项、ZIP 和 SHA-256。允许范围应包含目标仓库、版本与公开产物。

只有获得允许后，才保护本地修改并完成提交/推送、远程标签和 GitHub Release；预览版勾选预发布，上传 ZIP 与 `.sha256`，使用已审阅说明。再核对标签对应提交、下载附件与本地摘要，记录实际链接。未获允许时保持本地准备状态。
