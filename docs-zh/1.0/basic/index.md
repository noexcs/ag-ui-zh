---
title: "事件模型"
description: "事件信封、其通用字段、标识符，以及每个事件的地图 — 1.0"
---
<em class="lead">事件信封、其通用字段、标识符，以及每个事件的地图</em>

基础协议是每个实现无论使用哪些特性都要说的部分：

- **事件模型** — 本页：每个事件共享的信封、其通用字段，以及把事件
  关联在一起的标识符。
- **[运行输入](../basic/run-input.md)** — 唯一一条流向另一方的消息。
- **[元数据](../basic/metadata.md)** — 附着于一切上的开放通道，以及它的
  合并方式。
- **[能力](../basic/capabilities.md)** — 智能体在运行前关于自身声明的
  内容，以及一个声明带来什么义务。
- **[事件模式](../basic/patterns/index.md)** — 事件组合成事件流的方式。
- **[传输](../basic/transports/index.md)** — 事件流如何被封装与投递。
- **[处理模型](../basic/processing.md)** — 消费方对不认识的材料怎么处理。
- **[版本化与兼容性](../basic/versioning.md)** — 与更旧或更新的通信方
  打交道。

所有实现 MUST 支持事件模型和事件模式。运行生命周期之外的
[事件族](../events/index.md) 是特性：生产方发出它有内容可说的
那些。

## 事件 {#events}

每个事件都是一个 JSON 对象，共享一个信封，由模式定义为 `BaseEvent`：

- `type` — REQUIRED。判别字段，取值为 `EventType` 的 31 个值之一。
  本规范中的每条规则都通过这个字段附着到事件上。
- `timestamp` — OPTIONAL。事件创建的时间。资料性：消费方 MUST NOT
  用它来对事件排序——到达顺序才是协议的顺序。按惯例，单位是
  Unix epoch 以来的毫秒数。
- `rawEvent` — OPTIONAL。本事件翻译自的提供方原生事件，原样携带。
  消费方 MUST NOT 从它推导协议行为。
- `metadata` — OPTIONAL。见[通用字段](#general-fields)。

可以归属到子智能体工作的事件额外携带一个 OPTIONAL 的 `subagentRunId`
（模式中的 `Attributable`）；[子智能体规则](../events/subagents.md)
约束它。运行作用域的事件——`RUN_STARTED`、`RUN_FINISHED`、`RUN_ERROR`、
`MESSAGES_SNAPSHOT`——描述整个运行或整个对话，不携带归属。

## 通用字段 {#general-fields}

### `metadata` {#metadata}

附着于一切上的开放通道：按键开放，一个键之下可以是任意 JSON 值，
跨构建某个项的那些事件逐次累积——逐键进行、最后一次写入获胜、不递归——
并按事件族指定合并目标，另有一个保留键 `ag-ui`。它有独立的一页：
[元数据](../basic/metadata.md)。

### 缺失就是缺失 {#absent-means-absent}

一个没有值的可选字段 MUST 被省略，而非以 `null` 发送。

这适用于每个可选字段，包括携带任意 JSON 的字段，例如 `rawEvent`、
`RUN_FINISHED.result` 和 `forwardedProps`。整个可选字段为 `null` 时
MUST 被省略。必需的 JSON 载荷可以是 `null`，例如 `CUSTOM.value`
或 `STATE_SNAPSHOT.snapshot`。

::::
这不是风格偏好。一个必须同时接受两种写法的消费方，不得不在所有地方
把二者视为相等，而每种这样的容忍一旦发布就是永久的。协议携带的是
每个实现都能表示的那一种写法。
::::

一个 *按键开放对象之下的* `null` 值——一个元数据值、`state` 内部的
某个东西——是数据，MUST 被保留。只有代替整个缺失字段的 `null`
才被禁止。

协议已经发布了对某个可选位置上 `null` 的容忍之处，由兼容性垫片
处理，而非由本规则处理。见[版本化与兼容性](../basic/versioning.md)。

## 标识符 {#identifiers}

- `threadId` 标识一个会话。它由应用铸造，跨运行保持稳定。
- `runId` 标识一次运行。它 MUST NOT 被同一会话中的另一次运行复用。
- `messageId` 标识一条消息。它跨越运行边界——后一次运行中的快照
  MAY 通过其 id 重述一条消息——因此它 MUST 在其会话内唯一。
- `toolCallId` 标识一次工具调用，并把它的结果以及涉及它的任何中断
  关联回它。
- `subagentRunId` 是一次子智能体*调用*的不透明句柄，而不是子智能体
  定义的可复用名称：同一子智能体的两次调用携带两个不同的值。

所有标识符都是不透明字符串：消费方 MUST NOT 从中解析出结构。

## 事件 {#the-events}

31 个事件类型，分为八个事件族：

| 族 | 事件 | 模式 |
| --- | --- | --- |
| [运行与步骤](../events/lifecycle.md) | `RUN_STARTED` `RUN_FINISHED` `RUN_ERROR` `STEP_STARTED` `STEP_FINISHED` | lifecycle |
| [文本消息](../events/text-messages.md) | `TEXT_MESSAGE_START` `TEXT_MESSAGE_CONTENT` `TEXT_MESSAGE_END` `TEXT_MESSAGE_CHUNK` | [streaming](../basic/patterns/streaming.md) |
| [工具调用](../events/tool-calls.md) | `TOOL_CALL_START` `TOOL_CALL_ARGS` `TOOL_CALL_END` `TOOL_CALL_CHUNK` `TOOL_CALL_RESULT` | [streaming](../basic/patterns/streaming.md) |
| [推理](../events/reasoning.md) | `REASONING_START` `REASONING_END` `REASONING_MESSAGE_START` `REASONING_MESSAGE_CONTENT` `REASONING_MESSAGE_END` `REASONING_MESSAGE_CHUNK` `REASONING_ENCRYPTED_VALUE` | [streaming](../basic/patterns/streaming.md) |
| [状态](../events/state.md) | `STATE_SNAPSHOT` `STATE_DELTA` `MESSAGES_SNAPSHOT` | [snapshot–delta](../basic/patterns/snapshots.md) |
| [活动](../events/activity.md) | `ACTIVITY_SNAPSHOT` `ACTIVITY_DELTA` | [snapshot–delta](../basic/patterns/snapshots.md) |
| [子智能体](../events/subagents.md) | `SUBAGENT_STARTED` `SUBAGENT_FINISHED` `SUBAGENT_ERROR` | lifecycle |
| [透传](../events/passthrough.md) | `RAW` `CUSTOM` | standalone |

## 模式 {#schema}

协议的完整结构由位于 [`/spec/1.0/schema.json`](../schema.json) 的
JSON Schema 定义。它是唯一事实来源：TypeScript、Python 和 .NET 的模型
从它生成，本文档提及某个字段时是在指名模式所定义的东西，绝不重述
它的形状。

模式刻意不说本文档所说的话：顺序、生命周期、归属、错误处理与兼容性
是行为性的，模式无法表达它们。若两者在结构上出现分歧，以模式为准，
且本文档存在 bug。
