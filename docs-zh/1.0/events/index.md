---
title: "事件流"
description: "八大事件族，以及各自由谁响应 — 1.0"
---
<em class="lead">八大事件族，以及各自由谁响应</em>

生产方要说的所有内容都以事件的形式到达，共分为八个事件族。每个
事件族绑定一种[事件模式](../basic/patterns/index.md)，并附加各自的规则；每个事件族都面向消费方的不同部分：

| 事件族 | 事件 | 模式 | 消费方 |
| --- | --- | --- | --- |
| [运行与步骤](../events/lifecycle.md) | `RUN_STARTED` · `RUN_FINISHED` · `RUN_ERROR` · `STEP_STARTED` · `STEP_FINISHED` | lifecycle | 客户端自身 |
| [文本消息](../events/text-messages.md) | `TEXT_MESSAGE_*` | streaming | UI |
| [工具调用](../events/tool-calls.md) | `TOOL_CALL_*` | streaming | 应用程序 |
| [推理](../events/reasoning.md) | `REASONING_*` | streaming | UI |
| [状态](../events/state.md) | `STATE_SNAPSHOT` · `STATE_DELTA` · `MESSAGES_SNAPSHOT` | snapshot–delta | 应用状态存储 |
| [活动](../events/activity.md) | `ACTIVITY_SNAPSHOT` · `ACTIVITY_DELTA` | snapshot–delta | UI |
| [子智能体](../events/subagents.md) | `SUBAGENT_STARTED` · `SUBAGENT_FINISHED` · `SUBAGENT_ERROR` | lifecycle | 客户端自身 |
| [透传](../events/passthrough.md) | `RAW` · `CUSTOM` | standalone | 应用程序，需选择加入 |

这些事件族所包含的 31 种事件类型在[事件模型](../basic/index.md)中有
完整列举，其结构形态即 [schema](../schema.md) 所定义。对生产方而言，
只有运行生命周期是必需的——其余每个事件族都是一项特性，生产方在有内容
要借助它表达时才发出。消费方 MUST 接受所有这些事件：来自某个消费方用不
到之事件族的事件，仍然是格式良好的事件，而非[无法识别的内容](../basic/processing.md)。

- [运行与步骤](../events/lifecycle.md) — 运行如何开始与结束，以及步骤如何标记其各阶段。
- [文本消息](../events/text-messages.md) — 会话本身，随生成过程流式传输。
- [工具调用](../events/tool-calls.md) — 智能体提议，应用程序定夺。
- [推理](../events/reasoning.md) — 流式传输的模型思考，以及随其往返的加密制品。
- [状态](../events/state.md) — 可被替换或修正的共享状态与会话。
- [活动](../events/activity.md) — UI 在转录之外渲染的结构化进度。
- [子智能体](../events/subagents.md) — 归属、所有权、嵌套，以及委派工作如何终结。
- [原始与自定义事件](../events/passthrough.md) — 两个逃生舱口，及其限制。
