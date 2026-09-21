# Reuse Scout 0.2.0-preview.1

发布类型：**预发布**。目标仓库：[cloudwallker/Reuse-Scout](https://github.com/cloudwallker/Reuse-Scout)，标签 `v0.2.0-preview.1`。这是第二版迭代；此前源码预览没有创建 GitHub Release。

## 本版变化

- 包内引用按精确文件名核对，避免 Windows 上通过、Linux 解包后断链；保留路径安全与编码文件名支持。
- 异常 YAML 标量返回受控诊断，校验器 CLI 参数错误复用脱敏规则。
- 搜索允许必要的脱敏技术条件；决定性判断必须读取直接来源，预算不足时保留未知。
- 分开说明证据性质和执行状态；本地静态阅读不代表测试通过，缺少平台或许可材料时明确证据不足。
- 增加固定合成验收材料，更新模板、示例、双语介绍与验证记录。

手动调用、默认只研究、功能/故障路线、四档预算和九文件技能包保持不变；没有新增运行时依赖。

## 安装与更新

下载 `reuse-scout-0.2.0-preview.1.zip` 和同名 `.sha256`，核对摘要后安装解压出的完整 `reuse-scout/` 目录。Codex 放入项目的 `.agents/skills/`，Claude Code 放入 `.claude/skills/`；详见[安装说明](https://github.com/cloudwallker/Reuse-Scout/blob/v0.2.0-preview.1/docs/INSTALL.md)。

更新时先把旧副本完整备份到扫描目录之外，再完整替换并重启宿主，不合并新旧文件。克隆仓库也可从已发布的标签取得同一版本。

Codex：`使用 $reuse-scout，快速模式。检查当前项目是否已有可复用实现，只研究。`

Claude Code：`/reuse-scout 快速模式。检查当前项目是否已有可复用实现，只研究。`

## 验证与限制

实际命令、正负例、跳过原因、打包核对及合成演练分别记录在[测试报告](https://github.com/cloudwallker/Reuse-Scout/blob/v0.2.0-preview.1/docs/TEST_REPORT.md)。发布以最终提交的 Windows/Linux × Python 3.9/3.12 四项 CI 成功为条件，实际结果须核对对应提交的 [Actions 记录](https://github.com/cloudwallker/Reuse-Scout/actions/workflows/validate.yml)。

Codex 和 Claude Code 的原生发现、字段共存、调用策略、预算及只读行为仍未完成真实宿主验收。固定合成资料、文本演练与结构测试不能替代这些证据。未执行四配置比较或完整用量测量，不宣称效果提升或 Token/费用节省；纯指令约束不是权限沙箱。

技能采用 MIT 许可，随包保留 LICENSE 与 THIRD_PARTY_NOTICES.md。SHA-256 用于内容核对，不证明发布者身份。
