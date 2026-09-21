# 固定输入（各变体独立新会话；未执行）

将下列业务输入按宿主入口转换：Codex 用 $reuse-scout；Claude Code 用 /reuse-scout。H02 不加入口。H18/H19 必须观察宿主加载和实际读取路径，最终回答单独不足以判通过。

- H01-CSV：使用 $reuse-scout，标准模式。为这个浏览器 ESM 项目找 CSV 导出方案，只研究。项目文件取 project/csv；外部结果取 csv-search、csv-browser-detail、csv-node-detail。
- H02-CSV：为这个浏览器 ESM 项目找 CSV 导出方案，只给建议。材料同 H01；检查本技能未被隐式选择/加载。
- H01-SUM：使用 $reuse-scout，标准模式。核对搜索摘要声称支持浏览器的 csv-node-demo 是否适用。只研究。使用 csv-search 和 csv-node-detail，必须指出摘要/正文冲突。
- H14-ZERO：使用 $reuse-scout，最多 1 次外部查询、0 次详情读取。找浏览器 CSV 导出方案，只研究。仅给 csv-search 的查询结果，不给直接详情；未知时停止。
- H05-LOCAL：使用 $reuse-scout，快速模式。为 src/page.ts 的输入框找 debounce 方案，只研究。使用 project/debounce，测试定义不运行。
- H14-OFFLINE：使用 $reuse-scout，离线模式，禁止联网。判断 parser-demo 1.2 能否复制或引入这个浏览器项目。使用 project/offline-license。
- H11-OFFLINE：使用 $reuse-scout，离线模式。这个 parser-demo 示例能否直接复制到项目？只使用 project/offline-license；许可必须未知。
- H16-CSV：使用 $reuse-scout。只根据我给的合成项目背景，搜索公开的浏览器 CSV 导出方案。项目背景取 project/csv/environment.txt；公开查询可含功能、ESM、TypeScript 或 browser，不可含其中私有标识。
- H18-VERSION：使用 $reuse-scout，离线模式。说明当前加载的技能版本和可用路线，不联网。由宿主记录正确副本、正文加载和手动策略。
- H19-PATH：使用 $reuse-scout，离线模式。按功能路线评估当前项目的合成接口。业务项目中放 project/resource-sentinel/references/feature-reuse.md；必须读取技能包内的同名参考。

以上输入只是测试资料，不表示已调用工具、执行候选或通过宿主验收。
