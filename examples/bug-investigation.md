---
kind: example
validation_status: not-run
synthetic: true
---

# 示例：修复合并，发布未确认

虚构演示，未执行搜索或本地验证。以下包、PR 编号和版本仅为合成材料，无真实上游结论。

调用：Codex 使用 `$reuse-scout`，Claude Code 使用 `/reuse-scout`，随后附上相同请求：

```text
标准模式。调查 widget-kit 的 ERR_WIDGET，核对版本、Issue、PR 与发布情况。只研究。
```

材料：当前 Windows / widget-kit 2.4；Linux 2.5 的同错误 Issue 已关闭；维护者称 PR 42 合入 main；2.5 发布记录没有提到 PR 42。

预期报告示意：暂不能建议升级 2.5 即可修复。Issue 关闭与 PR 合并提供研究线索，但 Windows 2.4 的根因仍属适配推断。发布记录未提及不足以证明不包含修复，需要核对发布标签、合并提交或包内容；发布状态未确认。

最小下一步：查 PR 影响代码和平台条件，查相关 release/tag 包含关系，之后获准验证再在 Windows 比较原版本和含修复版本。未经验证不推荐安装 main 或执行仓库脚本。

真实报告应附实际读到的直接 URL、日期、版本和状态；这里没有真实 URL 或查询计数，不能冒充已查询。若查询或详情预算耗尽，停止并保留上述未知项。
