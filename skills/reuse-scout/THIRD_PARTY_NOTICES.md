# 来源与第三方声明

Reuse Scout 参考并面向手动调用进行整合；工程研究方法不宣称全部原创，也未证明优于上游。本项目按需求独立撰写技能，不拼接上游提示词、不包含完整 ECC 或其 Agent 框架，不代表获得上游或 OpenAI 背书。

## 参考来源

- [PavedPath Code](https://github.com/Jia-Ethan/pavedpath-code/tree/97a319fcfd3f9b68976690e04f3b511d6171a300)，Jia-Ethan，MIT。参考问题定位、直接工程证据、版本适配和验证边界。已读 README、SKILL、agents/openai.yaml、两份 references 和 LICENSE。
- [ECC search-first](https://github.com/affaan-m/ECC/blob/8321021c54d670126ce3b2969d5deb880b4b0c2a/skills/search-first/SKILL.md)，Affaan Mustafa，MIT。参考本地优先、相关渠道探测及采用/适配/组合/自研判断。只审阅该技能与根 LICENSE。
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)：核对本地目录、斜杠调用与 `disable-model-invocation`；仅作契约参考，不将官方文档纳入本项目 MIT 授权。
- [Agent Skills 格式规范](https://agentskills.io/specification)：核对公共字段与目录格式；不声称实现各宿主完整 schema。
- [Codex 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)：核对原生目录、元数据、显式调用及启停契约；没有复制完整文档，也未将官方文档视为本项目 MIT 授权内容。

读取日期：2026-09-13。以上 SHA 是仓库 commit，不是文件 blob；未确认标签。四档数量预算、默认只研究、报告状态是本项目设计选择，尚无优越性实测。

入口和参考文档有流程层面的参考与改写关系，为随包保留来源和许可义务，以下保留两个上游的完整 MIT 文本。根目录与独立技能包分发同一份声明及本项目 LICENSE；不要只复制 SKILL.md。实际引用范围变化或发布前应重新核对许可。

## PavedPath Code — MIT

```text
MIT License

Copyright (c) 2026 Jia-Ethan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## ECC — MIT

```text
MIT License

Copyright (c) 2026 Affaan Mustafa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 仅开发时使用的库

[PyYAML](https://github.com/yaml/pyyaml/blob/6.0.3/LICENSE)（MIT）、[markdown-it-py](https://github.com/executablebooks/markdown-it-py/blob/v2.2.0/LICENSE)（MIT）及其 mdurl 依赖仅由开发环境安装；本项目分发包不捆绑其代码。它们的许可随各自软件包提供。普通调用技能不需要这些库。
