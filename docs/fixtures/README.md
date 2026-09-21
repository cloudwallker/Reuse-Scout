# 固定合成资料（未执行）

此目录只保存 H01/H02/H05/H11/H14/H16/H18/H19 的业务材料、受控外部结果和输入模板。全部包名、来源 URL、日志和项目身份均为虚构；.invalid 地址不得访问。它们不是候选项目代码、服务、安装器或已完成验收。实际测试把所需文件复制到开发仓库及其父目录之外的临时合成目录，避免继承开发 AGENTS.md、技能或上下文，并记录真实宿主加载与工具轨迹，不在此目录执行脚本或写结果。

project/csv 用于 H01、H02 及 H14-B；project/debounce 用于 H05；project/offline-license 用于 H11/H14-A；project/resource-sentinel 复制到业务项目根目录以验证 H19 资源定位。H18 使用待测技能包与 inputs.md 的输入，不能从本目录存在推断双宿主加载。external 仅供受控工具回放或标明合成结果的文本演练，不访问其中 URL。run-record-template.md 为每个独立宿主运行复制的空白记录。
