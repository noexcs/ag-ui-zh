---
title: "Schema 参考"
description: "1.0 Schema 的全部定义，每个一个锚点 —— 生成页面，请勿手改"
---

<!-- 本页由 schema.json 生成 — 请勿手改；修改 schema 后重新生成 -->

本页面由机读 schema 生成
[`schema.json`](schema.json) —— 结构的事实来源 —— 因此规范正文可以链接一个定义而不必重述它。请勿手工编辑：修改 schema 后重新生成。

每个定义的锚点是其名称的小写形式。

## 事件 {#events}
事件联合类型、其判别字段，以及全部事件。其字段来源的混入见 [混入](#mixins)。

### EventType {#eventtype}
每个事件都携带的判别字段。

**取值：**

`TEXT_MESSAGE_START` · `TEXT_MESSAGE_CONTENT` · `TEXT_MESSAGE_END` · `TEXT_MESSAGE_CHUNK` · `TOOL_CALL_START` · `TOOL_CALL_ARGS` · `TOOL_CALL_END` · `TOOL_CALL_CHUNK` · `TOOL_CALL_RESULT` · `STATE_SNAPSHOT` · `STATE_DELTA` · `MESSAGES_SNAPSHOT` · `ACTIVITY_SNAPSHOT` · `ACTIVITY_DELTA` · `RAW` · `CUSTOM` · `RUN_STARTED` · `RUN_FINISHED` · `RUN_ERROR` · `STEP_STARTED` · `STEP_FINISHED` · `REASONING_START` · `REASONING_MESSAGE_START` · `REASONING_MESSAGE_CONTENT` · `REASONING_MESSAGE_END` · `REASONING_MESSAGE_CHUNK` · `REASONING_END` · `REASONING_ENCRYPTED_VALUE` · `SUBAGENT_STARTED` · `SUBAGENT_FINISHED` · `SUBAGENT_ERROR`

### TextMessageStartEvent {#textmessagestartevent}
开启一条流式文本消息。内容以 TEXT_MESSAGE_CONTENT 事件到达，消息以 TEXT_MESSAGE_END 关闭。

**字段：**

- `type` — `"TEXT_MESSAGE_START"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 标识该流所构建的消息，并将后续的内容事件和结束事件关联到它。
- `role` — [`TextMessageRole`](#textmessagerole)，可选。 消息的发送者。role 缺省表示 assistant；该含义具有规范性，并在正文中说明，因为校验器将 default 视为文档而非行为。 默认值： `"assistant"`.
- `name` — `string`，可选。 作者可选的显示名称，供在一个 role 中区分多个参与者的 provider 使用。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### TextMessageContentEvent {#textmessagecontentevent}
向流式文本消息追加一个片段。

**字段：**

- `type` — `"TEXT_MESSAGE_CONTENT"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 该片段所属的消息。
- `delta` — `string`, **必填**。 要追加的片段。可以为空字符串：provider 会发送空的增量作为保活，也会在工具调用正在决策期间发送，拒绝它们会终止工作正常的运行。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### TextMessageEndEvent {#textmessageendevent}
关闭一条流式文本消息。

**字段：**

- `type` — `"TEXT_MESSAGE_END"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 被关闭的消息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### TextMessageChunkEvent {#textmessagechunkevent}
一种代替开始、内容和结束序列的简写形式，供无法提前知道消息从何处开始的生产方使用。每个字段都是可选的，因为延续 chunk 会省略未改变的内容；一个无字段的 chunk 延续的是哪条消息是一个顺序问题，由正文规范来回答。

**字段：**

- `type` — `"TEXT_MESSAGE_CHUNK"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`，可选。 该 chunk 所属的消息。缺省时延续当前已打开的消息。
- `role` — [`TextMessageRole`](#textmessagerole)，可选。 消息的发送者，位于打开该消息的 chunk 上。
- `delta` — `string`，可选。 要追加的片段。可以是空字符串。
- `name` — `string`，可选。 作者可选的显示名称。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ToolCallStartEvent {#toolcallstartevent}
打开一个工具调用。参数以 TOOL_CALL_ARGS 事件到达，该调用以 TOOL_CALL_END 关闭。

**字段：**

- `type` — `"TOOL_CALL_START"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `toolCallId` — `string`, **必填**。 标识该调用，并将之后的 args、end 和 result 事件与之关联。
- `toolCallName` — `string`, **必填**。 正在被调用的工具。
- `parentMessageId` — `string`，可选。 承载该调用的 assistant 消息。缺省表示生产方未将其归属于某条消息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ToolCallArgsEvent {#toolcallargsevent}
追加一个工具调用参数的片段。

**字段：**

- `type` — `"TOOL_CALL_ARGS"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `toolCallId` — `string`, **必填**。 这些参数所属的调用。
- `delta` — `string`, **必填**。 参数的一个片段，各片段拼接为该调用的参数文本——惯例上是一个 JSON 文档，但协议并不校验它（参见 FunctionCall.arguments）。刻意采用 string 而非解析后的 JSON：片段本身并不是一个文档。可以为空字符串。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ToolCallEndEvent {#toolcallendevent}
关闭一个工具调用，表示其参数已完整。

**字段：**

- `type` — `"TOOL_CALL_END"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `toolCallId` — `string`, **必填**。 被关闭的调用。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ToolCallChunkEvent {#toolcallchunkevent}
一种代替工具调用的 start、args 和 end 序列的简写形式。每个字段都是可选的，原因与 TEXT_MESSAGE_CHUNK 相同。

**字段：**

- `type` — `"TOOL_CALL_CHUNK"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `toolCallId` — `string`，可选。 该 chunk 所属的调用。缺省时延续当前已打开的调用。
- `toolCallName` — `string`，可选。 被调用的是哪个工具，位于打开该调用的 chunk 上。
- `parentMessageId` — `string`，可选。 承载该调用的 assistant 消息。
- `delta` — `string`，可选。 参数的一个片段。可以为空字符串。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ToolCallResultEvent {#toolcallresultevent}
承载工具返回的内容。新建一条 tool 消息，而不是追加到现有消息上，因此它有自己的 messageId。

**字段：**

- `type` — `"TOOL_CALL_RESULT"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 该工具结果所变成的 tool 消息。
- `toolCallId` — `string`, **必填**。 被应答的调用。
- `content` — `string` | 由 [`ContentPart`](#contentpart) 组成的数组, **必填**。 工具返回的内容：要么是纯文本，要么是有序的 parts 列表，与本事件新建的 tool 消息上完全一致。返回结构化数据的工具会将其序列化为文本；媒体则作为各自的 part 传输。
- `role` — `"tool"`，可选。 仅为与其新建的消息保持对称而存在；其值固定，因此生产方可以省略它。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### StateSnapshotEvent {#statesnapshotevent}
整体替换 agent 状态。当增量无法表达该变更时发送，或用于重新同步消费方。

**字段：**

- `type` — `"STATE_SNAPSHOT"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `snapshot` — [`State`](#state), **必填**。 完整的新状态。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### StateDeltaEvent {#statedeltaevent}
增量地变更 agent 状态。

**字段：**

- `type` — `"STATE_DELTA"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `delta` — [`JsonPatch`](#jsonpatch), **必填**。 该变更，作为针对当前状态的 RFC 6902 patch。此处的结构有效性并不意味着 patch 可以应用：一个格式良好的操作可能指向不存在的路径，而 RFC 6902 将其留给应用者处理。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### MessagesSnapshotEvent {#messagessnapshotevent}
生产方所拥有的全部消息的完整集合，按顺序排列。它是会话范围的，而非简单的覆盖：消费方可能保留一些没有任何生产方跟踪的消息，因此快照究竟如何与这些消息对账属于行为层面的约定，应写入正文说明。由于它是会话范围的，它不可能归属于某一个子智能体，因此它本身不携带归属信息；但它会通过消息本身确立其中每条消息由哪个子智能体拥有。

**字段：**

- `type` — `"MESSAGES_SNAPSHOT"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `messages` — 由 [`Message`](#message) 组成的数组, **必填**。 生产方正在声明的消息，按顺序排列。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### ActivitySnapshotEvent {#activitysnapshotevent}
报告不属于会话内容的结构化进度，例如 UI 会将其渲染为自身组件的步骤。

**字段：**

- `type` — `"ACTIVITY_SNAPSHOT"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 本事件所描述的活动消息。
- `activityType` — `string`, **必填**。 这是哪种活动。开放的字符串：取值集合归生产方所有，而非归协议所有。
- `content` — `object`, 按 key 开放, **必填**。 活动的负载，按 key 开放。
- `replace` — `boolean`，可选。 本快照是否覆盖活动的现有内容。缺省表示会覆盖，且该含义具有规范性；只有显式的 false 才是要求消费方保留已有内容。它不要求进行合并——ACTIVITY_DELTA 才是内容增量变更的方式。消费方如何处理不覆盖的快照属于行为层面的约定，应写入正文说明。 默认值： `true`.

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ActivityDeltaEvent {#activitydeltaevent}
增量变更活动消息的内容。

**字段：**

- `type` — `"ACTIVITY_DELTA"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 被变更的活动消息。
- `activityType` — `string`, **必填**。 这是哪种活动。
- `patch` — [`JsonPatch`](#jsonpatch), **必填**。 该变更，为针对活动内容的 RFC 6902 补丁。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### RawEvent {#rawevent}
原样透传提供方原生事件，供需要协议未建模之细节的消费方使用。

**字段：**

- `type` — `"RAW"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `event` — 任意 JSON 值, **必填**。 提供方自己的事件。可为任意 JSON 值，且为必填：一个唯一用途就是承载该事件的事件若缺少它便什么都说明不了。
- `source` — `string`，可选。 事件来自哪个提供方或框架。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### CustomEvent {#customevent}
协议为应用自定义事件提供的扩展点。消费方对这类事件所做的一切处理都在协议范围之外。

**字段：**

- `type` — `"CUSTOM"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `name` — `string`, **必填**。 该自定义事件是什么。必填：缺少它，消费方就无法路由该值。
- `value` — 任意 JSON 值, **必填**。 负载。可为任意 JSON 值，且为必填。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### RunStartedEvent {#runstartedevent}
开启一个运行。作用域为运行，因此不携带子智能体归属信息。

**字段：**

- `type` — `"RUN_STARTED"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `threadId` — `string`, **必填**。 该运行（run）所属的会话。
- `runId` — `string`, **必填**。 标识该运行。
- `protocolVersion` — `string`，可选。 本生产方所使用的协议版本，例如 "1.0"——是生产方自身的版本，而非对输入中版本的复述，正因如此二者才构成一次协商：每一方都声明自身版本，消费方在降级发生的那一刻就能察觉。缺省表示该生产方来自协议尚未携带版本的时期。
- `parentRunId` — `string`，可选。 当某个智能体以独立运行（而非在一个运行内作为子智能体）的方式调用另一个智能体时，派生本运行的那个运行。
- `input` — [`RunAgentInput`](#runagentinput)，可选。 启动本运行的请求，原样回显，以便未发起该请求的消费方仍能看到智能体被要求做什么。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### RunFinishedEvent {#runfinishedevent}
结束一个未失败的运行。作用域为运行，因此不携带子智能体归属信息。

**字段：**

- `type` — `"RUN_FINISHED"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `threadId` — `string`, **必填**。 该运行（run）所属的会话。
- `runId` — `string`, **必填**。 被结束的运行。
- `result` — 任意 JSON 值（`null` 除外），可选。 运行的返回值（如果有的话）。可为任意 JSON 值。
- `outcome` — [`RunFinishedOutcome`](#runfinishedoutcome)，可选。 运行结束的原因。缺省表示成功，因此在引入 outcome 之前编写的每个生产方均已符合规范。
- `usage` — 由 [`TokenUsage`](#tokenusage) 组成的数组，可选。 该运行的 token 用量，每个提供方和模型各一条目，因此调用过多个模型的运行会将它们分开保留。只想要总数的消费方可对条目求和。运行是核算边界：用量涵盖在运行内发出的每一次模型调用，包括其子智能体发出的调用；以独立运行方式（通过 parentRunId）被调用的智能体在其自身的终结事件上报告自己的用量；而恢复被中断运行的运行只报告它自身发出的调用，不包括被中断运行的调用。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### RunErrorEvent {#runerrorevent}
结束一个失败的运行。作用域为运行，因此不携带子智能体归属信息；未结束运行便失败的子智能体改报 SUBAGENT_ERROR。

**字段：**

- `type` — `"RUN_ERROR"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `message` — `string`, **必填**。 出错内容的说明，供人阅读。
- `code` — `string`，可选。 机器可读的错误码。开放的字符串：协议不定义任何词表。
- `usage` — 由 [`TokenUsage`](#tokenusage) 组成的数组，可选。 在失败前累计的 token 用量，适用于在终止前完成了一次或多次模型调用的运行。作用域与 RUN_FINISHED 相同：该运行自身的调用，包括子智能体在内。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### StepStartedEvent {#stepstartedevent}
在运行中打开一个命名的步骤，面向其框架中存在值得呈现的步骤概念的生产方。

**字段：**

- `type` — `"STEP_STARTED"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `stepName` — `string`, **必填**。 步骤的名称。用于标识该步骤：与之匹配的 STEP_FINISHED 携带相同的名称。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### StepFinishedEvent {#stepfinishedevent}
关闭一个命名的步骤。

**字段：**

- `type` — `"STEP_FINISHED"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `stepName` — `string`, **必填**。 被关闭的步骤。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningStartEvent {#reasoningstartevent}
打开一段推理。一个跨度可包含多条推理消息。

**字段：**

- `type` — `"REASONING_START"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 被打开的跨度。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningMessageStartEvent {#reasoningmessagestartevent}
打开一条流式推理消息。

**字段：**

- `type` — `"REASONING_MESSAGE_START"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 此流所构建的推理消息。
- `role` — `"reasoning"`, **必填**。 固定值，且为必填而非提供默认值。该必填性承袭自 SDK，而非刻意选择。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningMessageContentEvent {#reasoningmessagecontentevent}
向一条流式推理消息追加一个片段。

**字段：**

- `type` — `"REASONING_MESSAGE_CONTENT"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 此片段所属的推理消息。
- `delta` — `string`, **必填**。 要追加的片段。可以是空字符串。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningMessageEndEvent {#reasoningmessageendevent}
关闭一条流式推理消息。

**字段：**

- `type` — `"REASONING_MESSAGE_END"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 被关闭的推理消息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningMessageChunkEvent {#reasoningmessagechunkevent}
一种简写形式，替代推理消息的开始、内容和结束序列。

**字段：**

- `type` — `"REASONING_MESSAGE_CHUNK"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`，可选。 此块所属的推理消息。缺省时，继续向已打开的消息追加。
- `delta` — `string`，可选。 要追加的片段。可以是空字符串。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningEndEvent {#reasoningendevent}
关闭一段推理。

**字段：**

- `type` — `"REASONING_END"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `messageId` — `string`, **必填**。 被关闭的跨度。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningEncryptedValueEvent {#reasoningencryptedvalueevent}
承载供应商的不透明、加密推理工件；消费方将其存储并在后续轮次中原样返回，而无法读取其内容。

**字段：**

- `type` — `"REASONING_ENCRYPTED_VALUE"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `subtype` — [`ReasoningEncryptedValueSubtype`](#reasoningencryptedvaluesubtype), **必填**。 entityId 所指代事物的种类，它决定 value 的存储位置。
- `entityId` — `string`, **必填**。 value 的归属对象：依据 subtype 而定，为消息 id 或工具调用 id。
- `encryptedValue` — `string`, **必填**。 供应商的不透明工件。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### SubagentStartedEvent {#subagentstartedevent}
宣布一次子智能体调用已开始。该子智能体此后产出的一切内容都通过携带其 subagentRunId 进行归属，因此消费方无需重放事件流即可对这些工作进行分组。仅由 BaseEvent 构成，而非使用 Attributable，因为此处 subagentRunId 用于标识子智能体，而非将事件归属于某个子智能体；对外层子智能体的归属由 parentSubagentRunId 表达。

**字段：**

- `type` — `"SUBAGENT_STARTED"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid), **必填**。 被宣布的调用。
- `name` — `string`, **必填**。 子智能体的名称，可在多次调用间复用，与 subagentRunId 不同。
- `description` — `string`，可选。 此子智能体的用途，供消费方展示。
- `parentSubagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 生成此调用的子智能体调用，用于嵌套委托。缺省表示由父智能体直接生成。
- `parentToolCallId` — `string`，可选。 生成此子智能体的工具调用，适用于将智能体以工具形式暴露给模型的用法。使消费方无需读取 rawEvent 即可将子智能体关联到该调用。
- `parentMessageId` — `string`，可选。 承载该生成性工具调用的消息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### SubagentFinishedEvent {#subagentfinishedevent}
结束本次运行中某次子智能体调用的区段，原因要么是工作已完成，要么是其已挂起、等待外部输入。

**字段：**

- `type` — `"SUBAGENT_FINISHED"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid), **必填**。 被关闭的调用。
- `result` — 任意 JSON 值（`null` 除外），可选。 子智能体的返回值（若有）。可为任意 JSON 值，与 RUN_FINISHED.result 对应。
- `outcome` — [`SubagentFinishedOutcome`](#subagentfinishedoutcome)，可选。 区段结束的原因。缺省表示成功。挂起的子智能体既非成功也非失败，因此需要以自身的值来表示，而非从后续的中断推断得出。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### SubagentErrorEvent {#subagenterrorevent}
报告一次子智能体调用已失败。运行可以继续：父智能体可自由处理失败了的子智能体，这正是该事件不是 RUN_ERROR 的原因。

**字段：**

- `type` — `"SUBAGENT_ERROR"` ([`EventType`](#eventtype)), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。
- `subagentRunId` — [`SubagentRunId`](#subagentrunid), **必填**。 失败的调用。
- `message` — `string`, **必填**。 出错内容的说明，供人阅读。
- `code` — `string`，可选。 机器可读的错误码。为开放式字符串。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseEvent`](#baseevent)；组合而来的字段已列于上方。

### Event {#event}
任意 AG-UI 事件。每个成员都是规范性的（normative）：不存在可选层级，也不存在消费方可拒绝实现的事件。按 type 属性判别。

**成员：**

- [`TextMessageStartEvent`](#textmessagestartevent)
- [`TextMessageContentEvent`](#textmessagecontentevent)
- [`TextMessageEndEvent`](#textmessageendevent)
- [`TextMessageChunkEvent`](#textmessagechunkevent)
- [`ToolCallStartEvent`](#toolcallstartevent)
- [`ToolCallArgsEvent`](#toolcallargsevent)
- [`ToolCallEndEvent`](#toolcallendevent)
- [`ToolCallChunkEvent`](#toolcallchunkevent)
- [`ToolCallResultEvent`](#toolcallresultevent)
- [`StateSnapshotEvent`](#statesnapshotevent)
- [`StateDeltaEvent`](#statedeltaevent)
- [`MessagesSnapshotEvent`](#messagessnapshotevent)
- [`ActivitySnapshotEvent`](#activitysnapshotevent)
- [`ActivityDeltaEvent`](#activitydeltaevent)
- [`RawEvent`](#rawevent)
- [`CustomEvent`](#customevent)
- [`RunStartedEvent`](#runstartedevent)
- [`RunFinishedEvent`](#runfinishedevent)
- [`RunErrorEvent`](#runerrorevent)
- [`StepStartedEvent`](#stepstartedevent)
- [`StepFinishedEvent`](#stepfinishedevent)
- [`ReasoningStartEvent`](#reasoningstartevent)
- [`ReasoningMessageStartEvent`](#reasoningmessagestartevent)
- [`ReasoningMessageContentEvent`](#reasoningmessagecontentevent)
- [`ReasoningMessageEndEvent`](#reasoningmessageendevent)
- [`ReasoningMessageChunkEvent`](#reasoningmessagechunkevent)
- [`ReasoningEndEvent`](#reasoningendevent)
- [`ReasoningEncryptedValueEvent`](#reasoningencryptedvalueevent)
- [`SubagentStartedEvent`](#subagentstartedevent)
- [`SubagentFinishedEvent`](#subagentfinishedevent)
- [`SubagentErrorEvent`](#subagenterrorevent)

由判别字段  `type`.

## 消息 {#messages}
消息联合类型，以及会话历史承载的各消息类型。

### TextMessageRole {#textmessagerole}
流式文本消息可取的角色。排除 tool，因为 tool 由 TOOL_CALL_RESULT 承载，而非作为文本流式传输。

**取值：**

`developer` · `system` · `assistant` · `user`

### DeveloperMessage {#developermessage}
来自应用开发者的指令。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 在会话内标识该消息。
- `role` — `"developer"`, **必填**。 消息的发送者。每个消息定义都将其收窄为单个取值。
- `name` — `string`，可选。 作者可选的显示名称。
- `encryptedValue` — `string`，可选。 属于该消息的提供商不透明制品，由消费方存储并在后续轮次中返回。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。
- `content` — `string`, **必填**。 指令。REQUIRED：一条没有任何内容的 developer 消息什么也没有表达。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseMessage`](#basemessage), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### SystemMessage {#systemmessage}
来自系统的指令。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 在会话内标识该消息。
- `role` — `"system"`, **必填**。 消息的发送者。每个消息定义都将其收窄为单个取值。
- `name` — `string`，可选。 作者可选的显示名称。
- `encryptedValue` — `string`，可选。 属于该消息的提供商不透明制品，由消费方存储并在后续轮次中返回。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。
- `content` — `string`, **必填**。 指令。REQUIRED。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseMessage`](#basemessage), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### AssistantMessage {#assistantmessage}
来自智能体的消息。Content 为可选，因为一个轮次可能仅由工具调用构成。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 在会话内标识该消息。
- `role` — `"assistant"`, **必填**。 消息的发送者。每个消息定义都将其收窄为单个取值。
- `name` — `string`，可选。 作者可选的显示名称。
- `encryptedValue` — `string`，可选。 属于该消息的提供商不透明制品，由消费方存储并在后续轮次中返回。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。
- `content` — `string`，可选。 智能体所说的内容（若它有所发言）。
- `toolCalls` — 由 [`ToolCall`](#toolcall) 组成的数组，可选。 该轮次发出的工具调用。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseMessage`](#basemessage), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### UserMessage {#usermessage}
来自应用使用者的消息。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 在会话内标识该消息。
- `role` — `"user"`, **必填**。 消息的发送者。每个消息定义都将其收窄为单个取值。
- `name` — `string`，可选。 作者可选的显示名称。
- `encryptedValue` — `string`，可选。 属于该消息的提供商不透明制品，由消费方存储并在后续轮次中返回。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。
- `content` — `string` | 由 [`ContentPart`](#contentpart) 组成的数组, **必填**。 使用者所发送的内容：要么是纯文本，要么是用于多模态消息的有序 parts 列表。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`BaseMessage`](#basemessage), [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ToolMessage {#toolmessage}
工具返回的内容，以会话中的消息形式存在。它独立存在而非组合 BaseMessage，因为它不携带 name。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 标识该消息。
- `role` — `"tool"`, **必填**。 固定值。此处直接声明而非继承，因为该消息并未组合 BaseMessage。
- `content` — `string` | 由 [`ContentPart`](#contentpart) 组成的数组, **必填**。 工具返回的内容：要么是纯文本，要么是有序 parts 列表。返回结构化数据的工具会将其序列化为文本；媒体则以各自的 parts 形式传输。
- `toolCallId` — `string`, **必填**。 本条消息所回应的调用。
- `error` — `string`，可选。 工具失败时的原因（当它确实失败时）。与 content 并存而非替代 content，以便部分结果能在失败之后保留下来。
- `encryptedValue` — `string`，可选。 提供方不透明的制品，归属于该消息。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ActivityMessage {#activitymessage}
不属于会话内容的结构化进度信息，被物化为消息以保持在序列中的位置。它独立存在而非组合 BaseMessage，因为其 content 是 object 而非 string。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 标识该消息。
- `role` — `"activity"`, **必填**。 固定值。此处直接声明而非继承，因为该消息并未组合 BaseMessage。
- `activityType` — `string`, **必填**。 该活动的种类。开放的字符串：取值集合由生产方定义。
- `content` — `object`, 按 key 开放, **必填**。 活动的负载，按 key 开放。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`Attributable`](#attributable)；组合而来的字段已列于上方。

### ReasoningMessage {#reasoningmessage}
智能体推理的一段内容，被物化为消息。它独立存在而非组合 BaseMessage，因为它不携带 name。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 标识该消息。
- `role` — `"reasoning"`, **必填**。 固定值。此处直接声明而非继承，因为该消息并未组合 BaseMessage。
- `content` — `string`, **必填**。 推理文本。
- `encryptedValue` — `string`，可选。 提供方不透明的推理制品，归属于该消息。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`Attributable`](#attributable)；组合而来的字段已列于上方。

### Message {#message}
会话中的任意消息。以 role 作为判别字段。

**成员：**

- [`DeveloperMessage`](#developermessage)
- [`SystemMessage`](#systemmessage)
- [`AssistantMessage`](#assistantmessage)
- [`UserMessage`](#usermessage)
- [`ToolMessage`](#toolmessage)
- [`ActivityMessage`](#activitymessage)
- [`ReasoningMessage`](#reasoningmessage)

由判别字段  `role`.

### Role {#role}
已实体化消息可具有的所有角色。

**取值：**

`developer` · `system` · `assistant` · `user` · `tool` · `activity` · `reasoning`

## 运行输入 {#run-input}
发起一次运行的请求，以及仅由它承载的类型。行为规则：[运行输入](basic/run-input.md)。

### TextPart {#textpart}
文本 part。

**字段：**

- `type` — `"text"`, **必填**。 判别字段。
- `id` — `string`，可选。 在所在消息内标识该 part。optional，且目前尚无任何地方读取它：预先保留，以便一旦 assistant 消息也携带 parts，流式 part 就能与其在历史中的条目相匹配。
- `text` — `string`, **必填**。 文本。
- `metadata` — 任意 JSON 值（`null` 除外），可选。 关于该 part 的额外信息。与媒体 part 一样不受约束。文本搜索命中在此携带其来源与标题，而不是协议另行建模一种搜索结果 part。

封闭对象：schema 会拒绝此处未列出的成员。

### DataSource {#datasource}
内联携带的字节。

**字段：**

- `type` — `"data"`, **必填**。 判别字段。
- `value` — `string`, **必填**。 字节，base64 编码。在 2020-12 中，contentEncoding 是注解而非约束，因此格式错误的字符串在此仍能通过校验；拒绝它是解码器的工作。 编码： `base64`.
- `mimeType` — `string`, **必填**。 这些字节是什么。此处 REQUIRED（与 URL source 不同），因为没有其他信息能告诉消费方如何读取它们。

封闭对象：schema 会拒绝此处未列出的成员。

### UrlSource {#urlsource}
通过 URL 引用的字节，由需要的一方自行获取。

**字段：**

- `type` — `"url"`, **必填**。 判别字段。
- `value` — `string`, **必填**。 该 URL。刻意不限制为 URI 格式，以免生产方已在使用的 scheme 在这里被拒绝。
- `mimeType` — `string`，可选。 资源是什么，前提是生产方知道。OPTIONAL，因为响应会说明。

封闭对象：schema 会拒绝此处未列出的成员。

### FileSource {#filesource}
字节已在 provider 处，由 provider 签发的 handle 指代：一个 OpenAI 或 Anthropic 文件 ID、一个 Gemini 文件 URI、或一个仅该 provider 可读的存储 URL。字节不传输，也不发生任何获取。只有签发该 handle 的 provider 才能解析它；无法解析它的对端会丢弃该 part，就像丢弃任何它无法使用的 part 一样。

**字段：**

- `type` — `"file"`, **必填**。 判别字段。
- `value` — `string`, **必填**。 该 handle，与 provider 签发时完全一致。不透明：消费方 MUST NOT 获取它、解析它或从中读出 scheme。
- `provider` — `string`，可选。 该 handle 由谁签发，前提是生产方知道。OPTIONAL：agent 已经知道自己在与哪个 provider 通信。若存在，SHOULD 是 TokenUsage.provider 所用的小写 vendor id（openai、anthropic、google），以便对端在发送前就能判断一个 handle 是否为自己可用。
- `mimeType` — `string`，可选。 文件是什么，前提是生产方知道。OPTIONAL，因为持有字节的 provider 知道。

封闭对象：schema 会拒绝此处未列出的成员。

### PartSource {#partsource}
媒体 part 的字节从何而来：内联携带、以 URL 引用，或已存在于提供方处并使用其签发的 handle。

**成员：**

- [`DataSource`](#datasource)
- [`UrlSource`](#urlsource)
- [`FileSource`](#filesource)

由判别字段  `type`.

### ImagePart {#imagepart}
图像 part。

**字段：**

- `type` — `"image"`, **必填**。 判别字段。
- `id` — `string`，可选。 标识该片段（part）在其所属消息中的身份。可选，目前尚无任何读取方：与文本片段（text part）一样作为预留。
- `source` — [`PartSource`](#partsource), **必填**。 图像的来源。
- `metadata` — 任意 JSON 值（`null` 除外），可选。 关于该 part 的额外信息。不受约束而非 object：继承自 SDK，它们将其声明为 unknown 而非 record；在 README 的已知分歧中列出，而非在此处解决。

封闭对象：schema 会拒绝此处未列出的成员。

### AudioPart {#audiopart}
音频 part。

**字段：**

- `type` — `"audio"`, **必填**。 判别字段。
- `id` — `string`，可选。 标识该片段（part）在其所属消息中的身份。可选，目前尚无任何读取方：与文本片段（text part）一样作为预留。
- `source` — [`PartSource`](#partsource), **必填**。 音频的来源。
- `metadata` — 任意 JSON 值（`null` 除外），可选。 关于该片段的额外信息。不受约束，与其他媒体片段一致。

封闭对象：schema 会拒绝此处未列出的成员。

### VideoPart {#videopart}
视频 part。

**字段：**

- `type` — `"video"`, **必填**。 判别字段。
- `id` — `string`，可选。 标识该片段（part）在其所属消息中的身份。可选，目前尚无任何读取方：与文本片段（text part）一样作为预留。
- `source` — [`PartSource`](#partsource), **必填**。 视频的来源。
- `metadata` — 任意 JSON 值（`null` 除外），可选。 关于该片段的额外信息。不受约束，与其他媒体片段一致。

封闭对象：schema 会拒绝此处未列出的成员。

### DocumentPart {#documentpart}
文档 part。

**字段：**

- `type` — `"document"`, **必填**。 判别字段。
- `id` — `string`，可选。 标识该片段（part）在其所属消息中的身份。可选，目前尚无任何读取方：与文本片段（text part）一样作为预留。
- `source` — [`PartSource`](#partsource), **必填**。 文档的来源。
- `metadata` — 任意 JSON 值（`null` 除外），可选。 关于该片段的额外信息。不受约束，与其他媒体片段一致。

封闭对象：schema 会拒绝此处未列出的成员。

### ContentPart {#contentpart}
消息体的一部分：使用者在用户消息中发送的内容，或工具在工具消息中返回的内容。按 type 判别。命名依据 part 是什么而非方向，因为同一个 part 会随用户消息进入模型，并随工具结果从流中流出。

**成员：**

- [`TextPart`](#textpart)
- [`ImagePart`](#imagepart)
- [`AudioPart`](#audiopart)
- [`VideoPart`](#videopart)
- [`DocumentPart`](#documentpart)

由判别字段  `type`.

### Tool {#tool}
一个 agent 可以调用的工具。

**字段：**

- `name` — `string`, **必填**。 工具的名称，即 agent 调用它时所使用的名称。
- `description` — `string`, **必填**。 该工具做什么，供 agent 决定何时使用它。
- `parameters` — 任意 JSON 值（`null` 除外），可选。 描述该工具参数的 JSON Schema。以不透明方式携带：协议不约束也不校验它。OPTIONAL，因为所有三个 SDK 都已这样处理，且不接受参数的工具没有可声明的东西；缺失的 schema 与空的 schema 对 agent 意味着同一件事。
- `metadata` — [`Metadata`](#metadata)，可选。 关于该工具的额外信息，供那些将其自身的渲染或路由信息附加到工具上的消费方使用。

封闭对象：schema 会拒绝此处未列出的成员。

### Context {#context}
一段具名的环境信息，为本次运行提供给 agent，独立于会话。

**字段：**

- `description` — `string`, **必填**。 该 context 是什么，供 agent 解释。
- `value` — `string`, **必填**。 context 本身。

封闭对象：schema 会拒绝此处未列出的成员。

### ResumeEntry {#resumeentry}
对一个中断的回答，随从该中断继续的运行发送。

**字段：**

- `interruptId` — `string`, **必填**。 正在被回答的中断。
- `status` — `"resolved"` | `"cancelled"`, **必填**。 中断是被应答了还是被放弃了。
- `payload` — 任意 JSON 值（`null` 除外），可选。 智能体所请求、并将据此执行的答案。可为任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 关于响应的信封信息，例如签名或路由键；与之相对，payload 才是答案本身。

封闭对象：schema 会拒绝此处未列出的成员。

### RunAgentInput {#runagentinput}
运行一个 agent 的请求。也会作为 RUN_STARTED.input 原样回传。仅 threadId、runId 和 messages 为 REQUIRED：这三者是各 SDK 已经达成一致的字段，且对 tools 和 context 而言，缺失的 key 与空数组意味着同一件事，因此要求它们不会拦住任何生产方可能出错的点。

**字段：**

- `threadId` — `string`, **必填**。 该运行（run）所属的会话。
- `runId` — `string`, **必填**。 标识该运行。
- `protocolVersion` — `string`，可选。 该消费方所支持的协议版本，例如 "1.0"。缺失表示该输入产生于协议携带版本之前——正文中的版本规则规定各方对此应如何处理。以带内方式发送而非由传输层携带，使录制的交互保持自描述性。
- `parentRunId` — `string`，可选。 生成本次运行的那次运行。
- `state` — [`State`](#state) （`null` 除外），可选。 本次运行起始的状态。
- `messages` — 由 [`Message`](#message) 组成的数组, **必填**。 迄今为止的会话，按顺序排列。
- `tools` — 由 [`Tool`](#tool) 组成的数组，可选。 agent 可调用的工具。缺失表示没有。
- `context` — 由 [`Context`](#context) 组成的数组，可选。 本次运行的环境信息。缺失表示没有。
- `forwardedProps` — 任意 JSON 值（`null` 除外），可选。 应用特有的值，原封不动地透传给 agent。任意 JSON 值。
- `resume` — 由 [`ResumeEntry`](#resumeentry) 组成的数组，可选。 当本次运行是从某次先前运行继续而来时，针对那些结束了该先前运行的 interrupt 的回答。

封闭对象：schema 会拒绝此处未列出的成员。

## 结果与中断 {#outcomes-and-interrupts}
运行与子智能体如何报告结束，以及被中断的运行在等待什么。行为规则：[中断与恢复](basic/patterns/interrupt-resume.md)。

### RunFinishedSuccessOutcome {#runfinishedsuccessoutcome}
运行已完成。等同于 outcome 缺省。与所有其他对象一样是封闭对象，这也使其无法携带挂起兄弟对象的 interrupts——若一次成功中仍有未决的中断，那将是矛盾而非扩展。已完成的运行仍可能遗留前端工具调用，等待应用回答；pendingToolCallIds 即用于列出它们。

**字段：**

- `type` — `"success"`, **必填**。 判别字段。
- `pendingToolCallIds` — 由 `string` 组成的数组，可选。 本次运行发起且未获回答的工具调用——运行中没有 TOOL_CALL_RESULT——供应用在下一次输入的 messages 中回答，按它们发起的顺序排列。缺失或为空表示生产方没有指定任何项，由消费方从流中推导该列表；否则它就是该列表，且与流一致。之所以放在 success outcome 上而非事件上，是因为因前端工具调用而停止的运行是一个已完成的运行：应用是否继续该会话是其自身的决定，因此生产方只报告它知道的，不多不少。 每一项： 一个工具调用 id，与 TOOL_CALL_START 所携带的相同。

封闭对象：schema 会拒绝此处未列出的成员。

### Interrupt {#interrupt}
运行在可以继续之前需要从外部获得的某样东西，例如一项批准或一个缺失的值。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 标识该中断。resume 条目按此 id 回答它。
- `reason` — `string`, **必填**。 运行停止的原因。是开放的 string 而非枚举：协议不试图对代理可能需要输入的每一种原因进行分类。
- `message` — `string`，可选。 供回答者阅读的人类可读提示。
- `toolCallId` — `string`，可选。 当该中断是工具批准时，它所涉及的工具调用。
- `responseSchema` — `object`, 按 key 开放，可选。 描述该中断期望的回答的 JSON Schema，使消费方能够为其构建表单。以不透明方式携带：协议不对其进行约束或校验。之所以限制为 object，是因为 TypeScript 与 Python 都如此声明它；.NET 将其保存为任意 JSON，而委托制定此 schema 的工单将它列在任意 JSON 字段之列。跟随那两个对其进行约束的语言，能防止 schema 接受参考客户端会拒绝的文档，代价是拒绝 JSON Schema 同样允许的布尔 schema——表示“任意回答”的裸 true。已作为已知分歧记录在案，而非已定论。
- `expiresAt` — `string`，可选。 该中断不再可回答的时间点。刻意不加约束而非采用 date-time 格式，因为生产方对其表示方式本就不一致，在此收紧会拒绝目前尚能工作的流。文档化的约定是 ISO 8601，比较此值的消费方会把它解析为日期，因此一个不是日期的值会让该中断看起来永久不过期。
- `metadata` — [`Metadata`](#metadata)，可选。 附加在此中断上的额外信息。

封闭对象：schema 会拒绝此处未列出的成员。

组合了  [`Attributable`](#attributable)；组合而来的字段已列于上方。

### RunFinishedInterruptOutcome {#runfinishedinterruptoutcome}
运行已暂停，正在等待其外部的某事。恢复意味着启动一个新运行，其 resume 条目回答这些中断。

**字段：**

- `type` — `"interrupt"`, **必填**。 判别字段。
- `interrupts` — 由 [`Interrupt`](#interrupt) 组成的数组 （最小 1 项）, **必填**。 运行正在等待的内容。至少一个：没有任何可回答内容的 interrupt outcome 会让消费方无事可做。

封闭对象：schema 会拒绝此处未列出的成员。

### RunFinishedCancelledOutcome {#runfinishedcancelledoutcome}
运行在未完成之前被运行它的一方停止，且并非失败。既非 success 也非 interrupt：没有产生任何结果，也没有在等待什么，因此该会话上的下一次运行是普通的新运行，而非恢复。与其兄弟值一样封闭：已取消的运行没有可携带的中断。之所以在 1.0 之前的 schema 中就已命名，是因为消费方不认识的 outcome 会被剥离并被读作 success——后来添加的取消结果会被每个 1.0 消费方当作已完成的运行处理。

**字段：**

- `type` — `"cancelled"`, **必填**。 判别字段。

封闭对象：schema 会拒绝此处未列出的成员。

### RunFinishedOutcome {#runfinishedoutcome}
运行结束的原因。

**成员：**

- [`RunFinishedSuccessOutcome`](#runfinishedsuccessoutcome)
- [`RunFinishedInterruptOutcome`](#runfinishedinterruptoutcome)
- [`RunFinishedCancelledOutcome`](#runfinishedcancelledoutcome)

由判别字段  `type`.

### SubagentFinishedSuccessOutcome {#subagentfinishedsuccessoutcome}
子智能体完成了它的工作。等价于 outcome 缺失。

**字段：**

- `type` — `"success"`, **必填**。 判别字段。

封闭对象：schema 会拒绝此处未列出的成员。

### SubagentFinishedSuspendedOutcome {#subagentfinishedsuspendedoutcome}
子智能体已暂停，等待外部输入。对本流是终结的，对子智能体本身不是：一旦这些中断被回答，后续的运行可以继续同一次调用。

**字段：**

- `type` — `"suspended"`, **必填**。 判别字段。
- `interruptIds` — 由 `string` 组成的数组，可选。 该子智能体自身发起的运行级中断。可以为空或缺失：因某个后代中断而挂起的子智能体自身不持有任何中断。 每一项： 一个 Interrupt.id。

封闭对象：schema 会拒绝此处未列出的成员。

### SubagentFinishedOutcome {#subagentfinishedoutcome}
子智能体的一段运行结束的原因。在低一层的位置镜像了 RunFinishedOutcome。

**成员：**

- [`SubagentFinishedSuccessOutcome`](#subagentfinishedsuccessoutcome)
- [`SubagentFinishedSuspendedOutcome`](#subagentfinishedsuspendedoutcome)

由判别字段  `type`.

## 公共类型 {#common-types}
以上各节共享的全部类型。

### Metadata {#metadata}
附加到事件、消息、工具调用、工具、中断或恢复（resume）条目的额外信息。按 key 开放：任意 key 下允许任意 JSON 值，包括 null，因为此处的 null 是有意义的数据。对象本身可以缺省，但存在时绝不等于 null。key ag-ui 保留供协议自身使用；保留是约定式的，因为校验某个 key 的值形态将与按 key 开放相矛盾。

**类型：** `object`, 按 key 开放

### SubagentRunId {#subagentrunid}
某一个子智能体调用的不透明句柄，而非子智能体定义的可复用名称：同一子智能体的两次调用携带两个不同的值。命名上镜像下一层的 runId，正如子智能体的名称镜像 agentId。

**类型：** `string`

### State {#state}
智能体状态。任意 JSON 值：协议承载状态但不解释状态，因此对象、数组、字符串和数字都是合法的。

**类型：** 任意 JSON 值

### JsonPointer {#jsonpointer}
按 RFC 6901 定义的 JSON Pointer。要么是空字符串，表示整个文档；要么是斜杠开头的引用令牌序列，其中波浪线转义为 ~0、斜杠转义为 ~1。没有前导斜杠的值，或波浪线后跟 0 或 1 以外任何字符的值，都不是 JSON Pointer。

**类型：** `string` 匹配  `^(/([^/~]|~[01])*)*$`

### AddOperation {#addoperation}
将 value 插入 path。RFC 6902 第 4.1 节。

**字段：**

- `op` — `"add"`, **必填**。 add 操作的判别字段。
- `path` — [`JsonPointer`](#jsonpointer), **必填**。 值要插入的位置。
- `value` — 任意 JSON 值, **必填**。 要插入的值。任意 JSON 值，包括 null——null 也是可合法添加的内容。

开放对象：超出这些成员的字段在协议上合法，且不会被剥离。

### RemoveOperation {#removeoperation}
删除 path 处的值。RFC 6902 第 4.2 节。

**字段：**

- `op` — `"remove"`, **必填**。 remove 操作的判别字段。
- `path` — [`JsonPointer`](#jsonpointer), **必填**。 要删除的内容。

开放对象：超出这些成员的字段在协议上合法，且不会被剥离。

### ReplaceOperation {#replaceoperation}
替换 path 处的值。RFC 6902 第 4.3 节。

**字段：**

- `op` — `"replace"`, **必填**。 replace 操作的判别字段。
- `path` — [`JsonPointer`](#jsonpointer), **必填**。 要替换的内容。
- `value` — 任意 JSON 值, **必填**。 替换值。任意 JSON 值，包括 null。

开放对象：超出这些成员的字段在协议上合法，且不会被剥离。

### MoveOperation {#moveoperation}
将 from 处的值移动到 path。RFC 6902 第 4.4 节。

**字段：**

- `op` — `"move"`, **必填**。 move 操作的判别字段。
- `from` — [`JsonPointer`](#jsonpointer), **必填**。 值被移出的来源位置。
- `path` — [`JsonPointer`](#jsonpointer), **必填**。 值被移入的目标位置。

开放对象：超出这些成员的字段在协议上合法，且不会被剥离。

### CopyOperation {#copyoperation}
将 from 处的值复制到 path。RFC 6902 第 4.5 节。

**字段：**

- `op` — `"copy"`, **必填**。 copy 操作的判别字段。
- `from` — [`JsonPointer`](#jsonpointer), **必填**。 值被复制自的来源位置。
- `path` — [`JsonPointer`](#jsonpointer), **必填**。 值被复制到目标位置。

开放对象：超出这些成员的字段在协议上合法，且不会被剥离。

### TestOperation {#testoperation}
断言 path 处的值等于 value。RFC 6902 第 4.6 节。

**字段：**

- `op` — `"test"`, **必填**。 test 操作的判别字段。
- `path` — [`JsonPointer`](#jsonpointer), **必填**。 要比较的内容。
- `value` — 任意 JSON 值, **必填**。 目标必须与之相等的值。任意 JSON 值，包括 null。

开放对象：超出这些成员的字段在协议上合法，且不会被剥离。

### JsonPatchOperation {#jsonpatchoperation}
单个 RFC 6902 操作。恰好一个操作形状必须匹配，由 op 判别。与协议自身的对象不同，操作是开放的：RFC 6902 第 4 节要求操作未定义的成员被忽略而非被拒绝，因此携带多余 value 的 remove 也是有效补丁。RFC 中有两条规则是值之间的关系而非形状，因此没有静态 schema 能表达它们，此处两者均不检查：其 from 是 path 的真前缀的 move（第 4.4 节），以及其 pointer 在目标文档中无法解析的任意操作。两者都应由应用方拒绝。

**成员：**

- [`AddOperation`](#addoperation)
- [`RemoveOperation`](#removeoperation)
- [`ReplaceOperation`](#replaceoperation)
- [`MoveOperation`](#moveoperation)
- [`CopyOperation`](#copyoperation)
- [`TestOperation`](#testoperation)

由判别字段  `op`.

### JsonPatch {#jsonpatch}
按 RFC 6902 定义的 JSON Patch 文档，被 STATE_DELTA.delta 和 ACTIVITY_DELTA.patch 引用：应用于目标文档的有序操作序列。空数组是有效的无操作补丁。这些操作是否真正适用于其目标文档，是 RFC 6902 留给应用方在运行时判断的问题；此处的结构有效性对此不说明任何问题。

**类型：** 由 [`JsonPatchOperation`](#jsonpatchoperation) 组成的数组

### FunctionCall {#functioncall}
工具调用的 name 与 arguments。

**字段：**

- `name` — `string`, **必填**。 正在被调用的工具。
- `arguments` — `string`, **必填**。 arguments 以 JSON 字符串形式存在，而非解析后的 JSON。按原样保留，因为模型可能发出不是合法 JSON 的 arguments，而在协议边界处丢失它们会将故障从必须处理它的消费方那里隐藏起来。

封闭对象：schema 会拒绝此处未列出的成员。

### ToolCall {#toolcall}
由一条 assistant 消息发出的调用。自身不携带子智能体归属，而是继承其所在消息的归属，因为多个调用可以共享同一个父消息。

**字段：**

- `id` — `string`, **必填**。 标识该调用。回应的工具消息会将其作为其 toolCallId 携带。
- `type` — `"function"`, **必填**。 协议所建模的唯一一种调用类型。
- `function` — [`FunctionCall`](#functioncall), **必填**。 被调用的目标，以及调用所用的参数。
- `encryptedValue` — `string`，可选。 提供方不透明的制品，归属于该调用。
- `metadata` — [`Metadata`](#metadata)，可选。 附加在该调用上的额外信息。放在此处而非并入其所在消息，因为多个调用可以共享同一个父消息，合并它们会使结果依赖于它们的顺序。

封闭对象：schema 会拒绝此处未列出的成员。

### TokenUsage {#tokenusage}
某一提供商和某一模型的 token 计数，采用协议自身的核算口径：每个计数要么是总数，要么是某个总数的具名组成部分，因此来自不同提供商的条目相加时不会重复计数。inputTokens 和 outputTokens 是总数；reasoningTokens、cachedInputTokens 和 cacheWriteInputTokens 是它们的一部分，而非额外的累加；totalTokens 是两个总数之和。所有字段都是标签或数字——不含任何承载内容或标识性的信息，没有提示词、补全或消息，也没有会话、运行和用户标识符。

**字段：**

- `provider` — `string`，可选。 哪个提供商处理了该请求。
- `model` — `string`，可选。 哪个模型处理了该请求。
- `inputTokens` — `integer` （最小 0，最大 9007199254740991），可选。 该次调用被计费的每一个提示 token：从提供商缓存读取的 token、写入提供商缓存的 token，以及音频或其他非文本输入都计入此项。cachedInputTokens 和 cacheWriteInputTokens 对该数字进行细分，而绝不累加到该数字上——当某个提供商在与更小的 input 计数并列报告其缓存计数时，生产方会在该条目发出前把这些计数加到其中。与 timestamp 一样设有上限，原因也相同：超出 JSON 安全整数范围的计数无法在往返之后保持原样，消费方会悄无声息地读到与生产方写入不同的数字。
- `outputTokens` — `integer` （最小 0，最大 9007199254740991），可选。 生成的每一个 token；在提供商区分推理 token 时，包含推理部分。reasoningTokens 对该数字进行细分，而绝不累加到该数字上——当某个提供商在与更小的补全计数并列报告推理 token 时，生产方会将其加到其中。
- `totalTokens` — `integer` （最小 0，最大 9007199254740991），可选。 inputTokens 加 outputTokens，按上述口径。生产方 MAY 自行计算该值，而非复制提供商的总数；并且仅当该总数的统计口径相同时，才复制提供商的总数，因此消费方可以把该字段读作另外两个字段的总和。
- `reasoningTokens` — `integer` （最小 0，最大 9007199254740991），可选。 提供商区分推理 token 时，用于推理的输出 token。是 outputTokens 的一部分，而非额外累加。
- `cachedInputTokens` — `integer` （最小 0，最大 9007199254740991），可选。 从提供商缓存读取的输入 token。是 inputTokens 的一部分，而非额外累加，且与 cacheWriteInputTokens 互不相交。
- `cacheWriteInputTokens` — `integer` （最小 0，最大 9007199254740991），可选。 本次调用写入提供商缓存的输入 token（在提供商区分该情况时）。是 inputTokens 的一部分，而非额外累加，且与 cachedInputTokens 互不相交。之所以单列为一个字段，是因为提供商对缓存写入与缓存读取的定价不同，因此计算费用的消费方离不开它。

封闭对象：schema 会拒绝此处未列出的成员。

### ReasoningEncryptedValueSubtype {#reasoningencryptedvaluesubtype}
REASONING_ENCRYPTED_VALUE 归属于消息还是工具调用。

**取值：**

`tool-call` · `message`

### SubagentInfo {#subagentinfo}
描述一个可被父 agent 调用的子智能体。

**字段：**

- `name` — `string`, **必填**。 子智能体的唯一名称或标识。
- `description` — `string`，可选。 该子智能体专长于什么。帮助客户端构建 agent 选择界面。

封闭对象：schema 会拒绝此处未列出的成员。

### IdentityCapabilities {#identitycapabilities}
关于该 agent 的基本元数据。对发现界面、agent 市场以及调试有用。当你希望客户端显示 agent 信息，或多个 agent 可用且用户需要选择其一时，应设置这些字段。

**字段：**

- `name` — `string`，可选。 在 UI 和 agent 选择器中显示的人类可读名称。
- `type` — `string`，可选。 驱动该 agent 的框架或平台（例如 "langgraph"、"mastra"、"crewai"）。
- `description` — `string`，可选。 该 agent 做什么——帮助用户和路由逻辑决定何时使用它。
- `version` — `string`，可选。 agent 的语义化版本号（例如 "1.2.0"）。可用于兼容性检查。
- `provider` — `string`，可选。 维护该 agent 的组织或团队。
- `documentationUrl` — `string`，可选。 指向 agent 文档或主页的 URL。
- `metadata` — [`Metadata`](#metadata)，可选。 用于存放集成特定身份信息的任意键值对。

封闭对象：schema 会拒绝此处未列出的成员。

### TransportCapabilities {#transportcapabilities}
声明该 agent 支持哪些传输机制。客户端据此选择最优的连接策略。仅对你实际处理的传输方式将标志置为 true——不支持的省略或置为 false。

**字段：**

- `streaming` — `boolean`，可选。 若 agent 通过 SSE 流式返回响应，则置为 true。大多数 agent 会启用此项。
- `websocket` — `boolean`，可选。 若 agent 接受持久化的 WebSocket 连接，则置为 true。
- `httpBinary` — `boolean`，可选。 若 agent 支持 AG-UI 二进制协议（基于 HTTP 的 protobuf），则置为 true。
- `pushNotifications` — `boolean`，可选。 若 agent 能在运行结束后通过 webhook 发送异步更新，则置为 true。
- `resumable` — `boolean`，可选。 若 agent 支持通过序列号恢复被中断的流，则置为 true。

封闭对象：schema 会拒绝此处未列出的成员。

### ToolsCapabilities {#toolscapabilities}
工具调用能力。区分局 agent 自身提供的工具（列在 items 中）和客户端在运行时通过 RunAgentInput.tools 传入的工具。当你的 agent 能够调用函数、搜索网页、执行代码等时启用此项。

**字段：**

- `supported` — `boolean`，可选。 若 agent 能够进行任何工具调用，则置为 true。置为 false 可明确表示工具调用已禁用，即使 items 中存在工具。
- `items` — 由 [`Tool`](#tool) 组成的数组，可选。 该 agent 自身提供的工具（完整的 JSON Schema 定义）。这些与通过 RunAgentInput.tools 传入的客户端提供工具是不同的。
- `parallelCalls` — `boolean`，可选。 若 agent 能在单个步骤内并发调用多个工具，则置为 true。
- `clientProvided` — `boolean`，可选。 若 agent 接受并使用客户端在运行时提供的工具，则置为 true。

封闭对象：schema 会拒绝此处未列出的成员。

### OutputCapabilities {#outputcapabilities}
输出格式支持。当你的 agent 能返回符合某个 JSON schema 的响应时启用 structuredOutput，这便于程序化消费。

**字段：**

- `structuredOutput` — `boolean`，可选。 若 agent 能生成匹配所提供 schema 的结构化 JSON 输出，则置为 true。
- `supportedMimeTypes` — 由 `string` 组成的数组，可选。 agent 能生成的 MIME 类型（例如 ["text/plain", "application/json"]）。若 agent 只生成纯文本则省略。

封闭对象：schema 会拒绝此处未列出的成员。

### StateCapabilities {#statecapabilities}
状态与记忆管理能力。这些字段告知客户端 agent 如何处理共享状态，以及会话上下文是否在多次运行之间持久保留。

**字段：**

- `snapshots` — `boolean`，可选。 若 agent 会发出 STATE_SNAPSHOT 事件（全量状态替换），则置为 true。
- `deltas` — `boolean`，可选。 若 agent 会发出 STATE_DELTA 事件（JSON Patch 增量更新），则置为 true。
- `memory` — `boolean`，可选。 若 agent 拥有超出当前会话的长期记忆（例如向量存储、知识库，或跨会话召回），则置为 true。
- `persistentState` — `boolean`，可选。 若状态在同一会话内的多次运行之间保持保留，则置为 true。为 false 时，状态在每次运行时重置。

封闭对象：schema 会拒绝此处未列出的成员。

### MultiAgentCapabilities {#multiagentcapabilities}
多智能体协作能力。当你的 agent 能够编排工作或把工作移交给其他 agent 时启用这些字段。

**字段：**

- `supported` — `boolean`，可选。 若 agent 参与任何形式的多智能体协作，则置为 true。
- `delegation` — `boolean`，可选。 若 agent 能将子任务委托给其他 agent 同时保留控制权，则置为 true。
- `handoffs` — `boolean`，可选。 若 agent 能将整个会话完全移交给另一个 agent，则置为 true。
- `subagents` — 由 [`SubagentInfo`](#subagentinfo) 组成的数组，可选。 该 agent 可调用的子智能体列表。有助于客户端构建 agent 选择界面。

封闭对象：schema 会拒绝此处未列出的成员。

### ReasoningCapabilities {#reasoningcapabilities}
推理与思考能力。当你的 agent 暴露其内部思考过程（例如思维链、扩展思考）时启用这些字段。

**字段：**

- `supported` — `boolean`，可选。 若 agent 会生成对客户端可见的推理/思考 token，则置为 true。
- `streaming` — `boolean`，可选。 若推理 token 以增量流式方式发出（而非一次性全部返回），则置为 true。
- `encrypted` — `boolean`，可选。 若推理内容被加密（零数据保留模式），则置为 true。客户端应预期的是不透明的 encryptedValue 字段而非可读内容。

封闭对象：schema 会拒绝此处未列出的成员。

### MultimodalInputCapabilities {#multimodalinputcapabilities}
agent 能接受的输入模态。客户端据此显示或隐藏文件上传按钮、录音器、图片选择器等。

**字段：**

- `image` — `boolean`，可选。 如果智能体能够处理图像输入（例如截图、照片），则设为 true。
- `audio` — `boolean`，可选。 如果智能体能够处理音频输入（语音、录音），则设为 true。
- `video` — `boolean`，可选。 如果智能体能够处理视频输入，则设为 true。
- `pdf` — `boolean`，可选。 如果智能体能够处理 PDF 文档，则设为 true。
- `file` — `boolean`，可选。 如果智能体能够处理任意文件上传，则设为 true，即图像、音频、视频和文档 parts 未涵盖种类的文件。此字段不说明文件如何到达；part 的 source（内联、URL 或 provider handle）是另一个问题。

封闭对象：schema 会拒绝此处未列出的成员。

### MultimodalOutputCapabilities {#multimodaloutputcapabilities}
智能体能够作为输出产生的模态。客户端使用它来预判智能体响应中可能出现丰富内容。

**字段：**

- `image` — `boolean`，可选。 如果智能体能够在其响应中生成图像，则设为 true。
- `audio` — `boolean`，可选。 如果智能体能够产生音频输出（文本转语音、音频文件），则设为 true。

封闭对象：schema 会拒绝此处未列出的成员。

### MultimodalCapabilities {#multimodalcapabilities}
多模态输入与输出支持。组织为 input 和 output 两个子对象，以便客户端可以独立查询智能体接受什么与产生什么。

**字段：**

- `input` — [`MultimodalInputCapabilities`](#multimodalinputcapabilities)，可选。 智能体能够作为输入接受的模态（图像、音频、视频、PDF、文件）。
- `output` — [`MultimodalOutputCapabilities`](#multimodaloutputcapabilities)，可选。 智能体能够作为输出产生的模态（图像、音频）。

封闭对象：schema 会拒绝此处未列出的成员。

### ExecutionCapabilities {#executioncapabilities}
执行控制与限制。声明这些内容，以便客户端能够就一次智能体运行可能持续多久或可能执行多少步骤设定预期。

**字段：**

- `codeExecution` — `boolean`，可选。 如果智能体能够在运行期间执行代码（例如 Python、JavaScript），则设为 true。
- `sandboxed` — `boolean`，可选。 如果代码执行发生在沙箱或隔离环境中，则设为 true。仅当 codeExecution 为 true 时有意义。
- `maxIterations` — `integer` （最小 0，最大 9007199254740991），可选。 智能体每次运行将执行的工具调用/推理迭代的最大次数。帮助客户端显示进度或设定超时预期。
- `maxExecutionTime` — `integer` （最小 0，最大 9007199254740991），可选。 智能体在超时之前运行的最大墙钟时间（以 milliseconds 计）。

封闭对象：schema 会拒绝此处未列出的成员。

### HumanInTheLoopCapabilities {#humanintheloopcapabilities}
人机交互（human-in-the-loop）支持。当你的智能体能够在继续之前暂停执行以请求人工输入、审批或反馈时，启用这些项。

**字段：**

- `supported` — `boolean`，可选。 如果智能体支持任何形式的人机交互（human-in-the-loop）交互，则设为 true。
- `approvals` — `boolean`，可选。 如果智能体能够在执行敏感操作（例如发送邮件、删除数据）之前暂停并请求显式审批，则设为 true。
- `interventions` — `boolean`，可选。 如果智能体允许人工在执行中途介入并修改其计划，则设为 true。
- `feedback` — `boolean`，可选。 如果智能体能够结合用户反馈（点赞/点踩、纠正）来改进其在当前会话内的行为，则设为 true。
- `interrupts` — `boolean`，可选。 如果智能体参与 AG-UI 中断（interrupt）协议，则设为 true：它以携带 interrupt 结果的 RUN_FINISHED 结束一次运行，并通过 RunAgentInput.resume 接受传回的答复。
- `approveWithEdits` — `boolean`，可选。 如果工具调用中断接受 resume 负载中的 editedArgs，则设为 true。仅当 interrupts 为 true 时有意义。

封闭对象：schema 会拒绝此处未列出的成员。

### AgentCapabilities {#agentcapabilities}
对智能体当前能力的带类型的、分类的快照。所有字段均为可选（optional）——智能体只声明它所支持的能力。省略的字段表示该能力未被声明（未知），而不是表示其不受支持。custom 字段是一个逃生通道，用于容纳不属于标准类别的集成特定能力。

**字段：**

- `identity` — [`IdentityCapabilities`](#identitycapabilities)，可选。 智能体身份与元数据。
- `transport` — [`TransportCapabilities`](#transportcapabilities)，可选。 支持的传输机制（SSE、WebSocket、二进制等）。
- `tools` — [`ToolsCapabilities`](#toolscapabilities)，可选。 智能体提供的工具以及工具调用配置。
- `output` — [`OutputCapabilities`](#outputcapabilities)，可选。 输出格式支持（结构化输出、MIME 类型）。
- `state` — [`StateCapabilities`](#statecapabilities)，可选。 状态与内存管理（快照、增量、持久化）。
- `multiAgent` — [`MultiAgentCapabilities`](#multiagentcapabilities)，可选。 多智能体协同（委派、移交、子智能体）。
- `reasoning` — [`ReasoningCapabilities`](#reasoningcapabilities)，可选。 推理与思考支持（思维链、加密思考）。
- `multimodal` — [`MultimodalCapabilities`](#multimodalcapabilities)，可选。 多模态输入/输出支持（图像、音频、视频、文件）。
- `execution` — [`ExecutionCapabilities`](#executioncapabilities)，可选。 执行控制与限制（代码执行、超时、迭代上限）。
- `humanInTheLoop` — [`HumanInTheLoopCapabilities`](#humanintheloopcapabilities)，可选。 人机交互（human-in-the-loop）支持（审批、介入、反馈）。
- `custom` — `object`, 按 key 开放，可选。 标准类别未涵盖的集成特定能力。按 key 开放：key 之下允许任意 JSON 值，因为上述类别无法预见一个集成会声明什么。

封闭对象：schema 会拒绝此处未列出的成员。

## 混入 {#mixins}
共享的字段集合，被展平进每一个组合它们的定义。它们在 schema 中作为具名定义存在，以便文档只写一次；线上对象永远不会只是一个混入。

### Attributable {#attributable}
被组合进一切可能归属于子智能体工作的部分：描述内容或进度的事件、各消息类型，以及每个中断。运行作用域的事件省略它——RUN_STARTED、RUN_FINISHED 与 RUN_ERROR 描述的是运行本身，MESSAGES_SNAPSHOT 则是会话范围的，因此它们都不能归属于某一个子智能体。工具调用也省略它，并继承其所属消息的归属。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。


### BaseEvent {#baseevent}
每个事件无论其类型为何都携带的字段。这些字段被组合（composed）进每个事件的定义，而非逐一重复，因此此处一处修改即可一次触达所有事件。

**字段：**

- `type` — [`EventType`](#eventtype), **必填**。 这是哪种事件。每个事件定义都将其收窄为单一取值。
- `timestamp` — `integer` （最小 -9007199254740991，最大 9007199254740991），可选。 事件创建的时间。取值范围限定在 JSON 数字可无损往返的区间内，因此消费方读取到的值就是生产方写入的值。有意不采用浮点数。此处不约束单位，因为该单位从未被规范性地规定；实践中每个设置该值的 SDK 都使用 Unix epoch 起的毫秒数，生产方若选择其他单位，即使通过校验也会被消费方误读。协议中没有任何部分对该值做计算。
- `rawEvent` — 任意 JSON 值（`null` 除外），可选。 本事件所由之翻译而来的供应商原生事件，原样携带，供调试使用，也供需要协议未建模细节的消费方使用。任意 JSON 值。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该事件的额外信息。


### BaseMessage {#basemessage}
developer、system、assistant 和 user 消息共有的字段。有意排除了 content，因为 user 消息的 content 可以是数组，而其他消息的 content 是字符串；且此处的组合是求交而非覆盖：如果基类把 content 约束为字符串，数组形式的 content 就会变为无效。tool、activity 和 reasoning 消息不组合本混入，因为它们不携带 name。

**字段：**

- `subagentRunId` — [`SubagentRunId`](#subagentrunid)，可选。 该条目所属的子智能体调用。缺省表示由父智能体直接产生。
- `id` — `string`, **必填**。 在会话内标识该消息。
- `role` — `string`, **必填**。 消息的发送者。每个消息定义都将其收窄为单个取值。
- `name` — `string`，可选。 作者可选的显示名称。
- `encryptedValue` — `string`，可选。 属于该消息的提供商不透明制品，由消费方存储并在后续轮次中返回。
- `metadata` — [`Metadata`](#metadata)，可选。 附加到该消息的额外信息。

