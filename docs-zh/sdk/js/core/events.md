---
title: "事件"
description:
  "Agent User Interaction Protocol SDK 中所用事件的文档"
---
<em class="lead">Agent User Interaction Protocol SDK 中所用事件的文档</em>

# 事件 {#events}

Agent User Interaction Protocol SDK 采用基于流式事件的架构。事件是智能体与前端之间通信的基本单元。本节记录事件类型及其属性。

## EventType 枚举 {#eventtype-enum}

`EventType` 枚举定义了系统中所有可能的事件类型：

```typescript
enum EventType {
  TEXT_MESSAGE_START = "TEXT_MESSAGE_START",
  TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT",
  TEXT_MESSAGE_END = "TEXT_MESSAGE_END",
  TOOL_CALL_START = "TOOL_CALL_START",
  TOOL_CALL_ARGS = "TOOL_CALL_ARGS",
  TOOL_CALL_END = "TOOL_CALL_END",
  TOOL_CALL_RESULT = "TOOL_CALL_RESULT",
  STATE_SNAPSHOT = "STATE_SNAPSHOT",
  STATE_DELTA = "STATE_DELTA",
  MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT",
  ACTIVITY_SNAPSHOT = "ACTIVITY_SNAPSHOT",
  ACTIVITY_DELTA = "ACTIVITY_DELTA",
  RAW = "RAW",
  CUSTOM = "CUSTOM",
  RUN_STARTED = "RUN_STARTED",
  RUN_FINISHED = "RUN_FINISHED",
  RUN_ERROR = "RUN_ERROR",
  STEP_STARTED = "STEP_STARTED",
  STEP_FINISHED = "STEP_FINISHED",
  REASONING_START = "REASONING_START",
  REASONING_MESSAGE_START = "REASONING_MESSAGE_START",
  REASONING_MESSAGE_CONTENT = "REASONING_MESSAGE_CONTENT",
  REASONING_MESSAGE_END = "REASONING_MESSAGE_END",
  REASONING_MESSAGE_CHUNK = "REASONING_MESSAGE_CHUNK",
  REASONING_END = "REASONING_END",
  REASONING_ENCRYPTED_VALUE = "REASONING_ENCRYPTED_VALUE",
  SUBAGENT_STARTED = "SUBAGENT_STARTED",
  SUBAGENT_FINISHED = "SUBAGENT_FINISHED",
  SUBAGENT_ERROR = "SUBAGENT_ERROR",
}
```

## BaseEvent {#baseevent}

所有事件都继承自 `BaseEvent` 类型，它提供所有事件类型共享的公共属性。

```typescript
type BaseEvent = {
  type: EventType // Discriminator field
  timestamp?: number
  rawEvent?: any
  metadata?: Record<string, any>
}
```

| 属性        | 类型                             | 描述                                     |
| ----------- | -------------------------------- | ---------------------------------------- |
| `type`      | `EventType`                      | 事件类型（联合类型的判别字段）           |
| `timestamp` | `number`（可选）                 | 事件创建时的时间戳                       |
| `rawEvent`  | `any`（可选）                    | 该事件被转换前的原始事件数据             |
| `metadata`  | `Record<string, any>`（可选）    | 附加到事件上的额外信息                   |

`metadata` 按 key 开放：一个 key 下允许任何 JSON 值，包括 `null`。该对象可以缺失，但存在时绝不为 `null`——显式的 `null` 会解析为缺失。`ag-ui` key 保留给 AG-UI 自用。使用 `@ag-ui/core` 的 `mergeMetadata` 将事件元数据合并进消息；参见[元数据](../../../concepts/metadata.md)。

## 生命周期事件 {#lifecycle-events}

这些事件表示一次智能体运行的生命周期。

### RunStartedEvent {#runstartedevent}

表示一次智能体运行的开始。

```typescript
type RunStartedEvent = BaseEvent & {
  type: EventType.RUN_STARTED
  threadId: string
  runId: string
  parentRunId?: string
  input?: RunAgentInput
}
```

| 属性          | 类型                       | 描述                                                                                                    |
| ------------- | -------------------------- | ------------------------------------------------------------------------------------------------------- |
| `threadId`    | `string`                   | 会话线程的 ID                                                                                           |
| `runId`       | `string`                   | 智能体运行的 ID                                                                                         |
| `parentRunId` | `string`（可选）           | （可选）用于分支/时间旅行的谱系指针。若存在，指向同一会话中先前的一次运行                                |
| `input`       | `RunAgentInput`（可选）    | （可选）为本次运行发送给智能体的确切输入载荷。可以省略已在历史中的消息                                  |

### TokenUsage {#tokenusage}

一种可复用的、仅含数值的 token 用量摘要，由终结性运行事件携带。它有意**只**包含提供方/模型标签与 token 计数——不含提示、补全、消息或标识符。这些计数遵循协议的[计量规则](../../../1.0/events/lifecycle.md#token-usage)：输入与输出计数是总量，缓存与推理计数是其中的部分，而绝不是额外的追加量。

```typescript
type TokenUsage = {
  provider?: string
  model?: string
  inputTokens?: number
  outputTokens?: number
  totalTokens?: number
  reasoningTokens?: number
  cachedInputTokens?: number
  cacheWriteInputTokens?: number
}
```

| 属性                    | 类型                | 描述                                                          |
| ----------------------- | ------------------- | ------------------------------------------------------------- |
| `provider`              | `string`（可选）    | 报告该用量的提供方（例如 `openai`）                           |
| `model`                 | `string`（可选）    | 产生该用量的模型                                              |
| `inputTokens`           | `number`（可选）    | 全部输入 token，含缓存读取与写入                              |
| `outputTokens`          | `number`（可选）    | 全部输出 token，含推理                                        |
| `totalTokens`           | `number`（可选）    | `inputTokens` 加上 `outputTokens`                             |
| `reasoningTokens`       | `number`（可选）    | 用于推理的输出 token；属于 `outputTokens` 的一部分            |
| `cachedInputTokens`     | `number`（可选）    | 从提示缓存读取的输入 token；属于 `inputTokens` 的一部分       |
| `cacheWriteInputTokens` | `number`（可选）    | 写入提示缓存的输入 token；属于 `inputTokens` 的一部分         |

### RunFinishedEvent {#runfinishedevent}

表示一次智能体运行成功完成。

```typescript
type RunFinishedEvent = BaseEvent & {
  type: EventType.RUN_FINISHED
  threadId: string
  runId: string
  result?: any
  usage?: TokenUsage[]
}
```

| 属性       | 类型                       | 描述                                                     |
| ---------- | -------------------------- | -------------------------------------------------------- |
| `threadId` | `string`                   | 会话线程的 ID                                            |
| `runId`    | `string`                   | 智能体运行的 ID                                          |
| `result`   | `any`（可选）              | 智能体运行的结果数据                                     |
| `usage`    | `TokenUsage[]`（可选）     | 该运行按 (provider, model) 划分的 token 用量（若报告）   |

### RunErrorEvent {#runerrorevent}

表示智能体运行期间发生错误。

```typescript
type RunErrorEvent = BaseEvent & {
  type: EventType.RUN_ERROR
  message: string
  code?: string
  usage?: TokenUsage[]
}
```

| 属性      | 类型                      | 描述                                             |
| --------- | ------------------------- | ------------------------------------------------ |
| `message` | `string`                  | 错误消息                                         |
| `code`    | `string`（可选）          | 错误码                                           |
| `usage`   | `TokenUsage[]`（可选）    | 已完成模型调用产生的部分 token 用量              |

### StepStartedEvent {#stepstartedevent}

表示智能体运行中某个步骤的开始。

```typescript
type StepStartedEvent = BaseEvent & {
  type: EventType.STEP_STARTED
  stepName: string
}
```

| 属性       | 类型     | 描述     |
| ---------- | -------- | -------- |
| `stepName` | `string` | 步骤名称 |

### StepFinishedEvent {#stepfinishedevent}

表示智能体运行中某个步骤的完成。

```typescript
type StepFinishedEvent = BaseEvent & {
  type: EventType.STEP_FINISHED
  stepName: string
}
```

| 属性       | 类型     | 描述     |
| ---------- | -------- | -------- |
| `stepName` | `string` | 步骤名称 |

## 文本消息事件 {#text-message-events}

这些事件表示会话中文本消息的生命周期。

### TextMessageStartEvent {#textmessagestartevent}

表示一条文本消息的开始。

```typescript
type TextMessageStartEvent = BaseEvent & {
  type: EventType.TEXT_MESSAGE_START
  messageId: string
  role: "assistant"
}
```

| 属性        | 类型          | 描述                   |
| ----------- | ------------- | ---------------------- |
| `messageId` | `string`      | 消息的唯一标识符       |
| `role`      | `"assistant"` | role 始终为 "assistant" |

### TextMessageContentEvent {#textmessagecontentevent}

表示流式文本消息中的一块内容。

```typescript
type TextMessageContentEvent = BaseEvent & {
  type: EventType.TEXT_MESSAGE_CONTENT
  messageId: string
  delta: string // Non-empty string
}
```

| 属性        | 类型     | 描述                                   |
| ----------- | -------- | -------------------------------------- |
| `messageId` | `string` | 与 TextMessageStartEvent 中的 ID 一致  |
| `delta`     | `string` | 文本内容块（非空）                     |

### TextMessageEndEvent {#textmessageendevent}

表示一条文本消息的结束。

```typescript
type TextMessageEndEvent = BaseEvent & {
  type: EventType.TEXT_MESSAGE_END
  messageId: string
}
```

| 属性        | 类型     | 描述                                   |
| ----------- | -------- | -------------------------------------- |
| `messageId` | `string` | 与 TextMessageStartEvent 中的 ID 一致  |

### TextMessageChunkEvent {#textmessagechunkevent}

便捷事件，在 JS/TS 客户端中会自动展开为 `TextMessageStart` → `TextMessageContent` → `TextMessageEnd`。

```typescript
type TextMessageChunkEvent = BaseEvent & {
  type: EventType.TEXT_MESSAGE_CHUNK
  messageId?: string // required on the first chunk for a message
  role?: "developer" | "system" | "assistant" | "user"
  delta?: string
}
```

行为

- 省略 start/end：客户端会把块序列转换为标准的 start/content/end 三元组，因此你无需手动发出它们。
- 首块要求：一条消息的第一个块必须包含 `messageId`。省略 `role` 时，它默认为 `assistant`。
- 流式传输：具有相同 `messageId` 的后续块会发出 `TextMessageContent` 事件。当另一条消息开始或事件流完成时，会自动发出 `TextMessageEnd`。

## 工具调用事件 {#tool-call-events}

这些事件表示智能体发起的工具调用的生命周期。

### ToolCallStartEvent {#toolcallstartevent}

表示一次工具调用的开始。

```typescript
type ToolCallStartEvent = BaseEvent & {
  type: EventType.TOOL_CALL_START
  toolCallId: string
  toolCallName: string
  parentMessageId?: string
}
```

| 属性              | 类型                | 描述                     |
| ----------------- | ------------------- | ------------------------ |
| `toolCallId`      | `string`            | 工具调用的唯一标识符     |
| `toolCallName`    | `string`            | 被调用工具的名称         |
| `parentMessageId` | `string`（可选）    | 父消息的 ID              |

### ToolCallArgsEvent {#toolcallargsevent}

表示一次工具调用的参数数据块。

```typescript
type ToolCallArgsEvent = BaseEvent & {
  type: EventType.TOOL_CALL_ARGS
  toolCallId: string
  delta: string
}
```

| 属性         | 类型     | 描述                                |
| ------------ | -------- | ----------------------------------- |
| `toolCallId` | `string` | 与 ToolCallStartEvent 中的 ID 一致  |
| `delta`      | `string` | 参数数据块                          |

### ToolCallEndEvent {#toolcallendevent}

表示一次工具调用的结束。

```typescript
type ToolCallEndEvent = BaseEvent & {
  type: EventType.TOOL_CALL_END
  toolCallId: string
}
```

| 属性         | 类型     | 描述                                |
| ------------ | -------- | ----------------------------------- |
| `toolCallId` | `string` | 与 ToolCallStartEvent 中的 ID 一致  |

### ToolCallResultEvent {#toolcallresultevent}

提供一次工具调用执行的结果。

```typescript
type ToolCallResultEvent = BaseEvent & {
  type: EventType.TOOL_CALL_RESULT
  messageId: string
  toolCallId: string
  content: string
  role?: "tool"
}
```

| 属性         | 类型                | 描述                                                    |
| ------------ | ------------------- | ------------------------------------------------------- |
| `messageId`  | `string`            | 该结果所属会话消息的 ID                                 |
| `toolCallId` | `string`            | 与对应 ToolCallStartEvent 中的 ID 一致                  |
| `content`    | `string`            | 工具执行产生的实际结果/输出内容                         |
| `role`       | `"tool"`（可选）    | 可选的 role 标识符，工具结果通常为 "tool"               |

## 状态管理事件 {#state-management-events}

这些事件用于管理智能体状态。

### StateSnapshotEvent {#statesnapshotevent}

提供智能体状态的完整快照。

```typescript
type StateSnapshotEvent = BaseEvent & {
  type: EventType.STATE_SNAPSHOT
  snapshot: any // StateSchema
}
```

| 属性       | 类型  | 描述         |
| ---------- | ----- | ------------ |
| `snapshot` | `any` | 完整状态快照 |

### StateDeltaEvent {#statedeltaevent}

使用 JSON Patch 提供对智能体状态的部分更新。

```typescript
type StateDeltaEvent = BaseEvent & {
  type: EventType.STATE_DELTA
  delta: any[] // JSON Patch operations (RFC 6902)
}
```

| 属性    | 类型    | 描述                     |
| ------- | ------- | ------------------------ |
| `delta` | `any[]` | JSON Patch 操作数组      |

### MessagesSnapshotEvent {#messagessnapshotevent}

提供会话中所有消息的快照。

```typescript
type MessagesSnapshotEvent = BaseEvent & {
  type: EventType.MESSAGES_SNAPSHOT
  messages: Message[]
}
```

| 属性       | 类型        | 描述             |
| ---------- | ----------- | ---------------- |
| `messages` | `Message[]` | 消息对象数组     |

### ActivitySnapshotEvent {#activitysnapshotevent}

投递某条活动消息的完整快照。

```typescript
type ActivitySnapshotEvent = BaseEvent & {
  type: EventType.ACTIVITY_SNAPSHOT
  messageId: string
  activityType: string
  content: Record<string, any>
  replace?: boolean
}
```

| 属性           | 类型                  | 描述                                                                                                   |
| -------------- | --------------------- | ------------------------------------------------------------------------------------------------------ |
| `messageId`    | `string`              | 目标 `ActivityMessage` 的标识符                                                                        |
| `activityType` | `string`              | 活动判别字段，例如 `"PLAN"` 或 `"SEARCH"`                                                              |
| `content`      | `Record<string, any>` | 描述完整活动状态的结构化载荷                                                                           |
| `replace`      | `boolean`（可选）     | 默认为 `true`；为 `false` 时，若已存在具有相同 ID 的消息，则忽略该快照                                  |

### ActivityDeltaEvent {#activitydeltaevent}

使用 JSON Patch 提供对活动快照的增量更新。

```typescript
type ActivityDeltaEvent = BaseEvent & {
  type: EventType.ACTIVITY_DELTA
  messageId: string
  activityType: string
  patch: any[] // RFC 6902 JSON Patch operations
}
```

| 属性           | 类型     | 描述                                                     |
| -------------- | -------- | -------------------------------------------------------- |
| `messageId`    | `string` | 目标 `ActivityMessage` 的标识符                          |
| `activityType` | `string` | 与最近一次快照一致的活动判别字段                         |
| `patch`        | `any[]`  | 应用于结构化活动载荷的 JSON Patch 操作                   |

## 推理事件 {#reasoning-events}

这些事件表示智能体内推理/思考过程的生命周期。推理事件使智能体能够将其内部思考过程暴露给前端，创建 role 为 `"reasoning"`、持久保存在消息历史中的 `ReasoningMessage` 对象。

### ReasoningStartEvent {#reasoningstartevent}

表示一个推理阶段的开始。这是一个透传事件，会通知订阅者但不会创建消息。

```typescript
type ReasoningStartEvent = BaseEvent & {
  type: EventType.REASONING_START
  messageId: string
}
```

| 属性        | 类型     | 描述                   |
| ----------- | -------- | ---------------------- |
| `messageId` | `string` | 推理阶段的标识符       |

### ReasoningMessageStartEvent {#reasoningmessagestartevent}

表示一条推理消息的开始。会在消息历史中创建新的 `ReasoningMessage`。

```typescript
type ReasoningMessageStartEvent = BaseEvent & {
  type: EventType.REASONING_MESSAGE_START
  messageId: string
  role: "reasoning"
}
```

| 属性        | 类型          | 描述                    |
| ----------- | ------------- | ----------------------- |
| `messageId` | `string`      | 消息的唯一标识符        |
| `role`      | `"reasoning"` | role 始终为 "reasoning" |

### ReasoningMessageContentEvent {#reasoningmessagecontentevent}

表示流式推理消息中的一块内容。

```typescript
type ReasoningMessageContentEvent = BaseEvent & {
  type: EventType.REASONING_MESSAGE_CONTENT
  messageId: string
  delta: string
}
```

| 属性        | 类型     | 描述                                           |
| ----------- | -------- | ---------------------------------------------- |
| `messageId` | `string` | 与 ReasoningMessageStartEvent 中的 ID 一致     |
| `delta`     | `string` | 推理内容块                                     |

### ReasoningMessageEndEvent {#reasoningmessageendevent}

表示一条推理消息的结束。

```typescript
type ReasoningMessageEndEvent = BaseEvent & {
  type: EventType.REASONING_MESSAGE_END
  messageId: string
}
```

| 属性        | 类型     | 描述                                           |
| ----------- | -------- | ---------------------------------------------- |
| `messageId` | `string` | 与 ReasoningMessageStartEvent 中的 ID 一致     |

### ReasoningMessageChunkEvent {#reasoningmessagechunkevent}

便捷事件，在 JS/TS 客户端中会自动展开为 `ReasoningMessageStart` → `ReasoningMessageContent` → `ReasoningMessageEnd`。

```typescript
type ReasoningMessageChunkEvent = BaseEvent & {
  type: EventType.REASONING_MESSAGE_CHUNK
  messageId?: string // required on the first chunk for a message
  delta?: string
}
```

行为

- 省略 start/end：客户端会把块序列转换为标准的 start/content/end 三元组。
- 首块要求：一条消息的第一个块必须包含 `messageId`。
- 流式传输：具有相同 `messageId` 的后续块会发出 `ReasoningMessageContent` 事件。当另一条消息开始或事件流完成时，会自动发出 `ReasoningMessageEnd`。

### ReasoningEndEvent {#reasoningendevent}

表示一个推理阶段的结束。这是一个透传事件，会通知订阅者但不会修改消息。

```typescript
type ReasoningEndEvent = BaseEvent & {
  type: EventType.REASONING_END
  messageId: string
}
```

| 属性        | 类型     | 描述                   |
| ----------- | -------- | ---------------------- |
| `messageId` | `string` | 推理阶段的标识符       |

### ReasoningEncryptedValueEvent {#reasoningencryptedvalueevent}

将加密值附加到消息或工具调用。发出该事件时，它会按 `entityId` 找到引用的实体，并设置其 `encryptedValue` 字段。

```typescript
type ReasoningEncryptedValueEvent = BaseEvent & {
  type: EventType.REASONING_ENCRYPTED_VALUE
  subtype: "tool-call" | "message"
  entityId: string
  encryptedValue: string
}
```

| 属性             | 类型                       | 描述                                       |
| ---------------- | -------------------------- | ------------------------------------------ |
| `subtype`        | `"tool-call" \| "message"` | 该值所属实体的类型                         |
| `entityId`       | `string`                   | 要附加该值的工具调用或消息的 ID            |
| `encryptedValue` | `string`                   | 要附加到该实体的加密值                     |

## 子智能体事件 {#subagent-events}

这些事件报告智能体将工作委派给了子智能体，使前端可以将输出归属于产生它的子智能体。归属信息本身以可选的 `subagentRunId` 出现在大多数其他事件类型上。

`subagentRunId` 标识**一次调用**，而非可复用的子智能体定义——同一个子智能体运行两次会产生两个不同的值。完整模型见[子智能体](../../../concepts/subagents.md)。

### SubagentStartedEvent {#subagentstartedevent}

宣告一次新的子智能体调用，并为其命名以供展示。

```typescript
type SubagentStartedEvent = BaseEvent & {
  type: EventType.SUBAGENT_STARTED
  subagentRunId: string
  name: string
  description?: string
  parentSubagentRunId?: string
  parentToolCallId?: string
  parentMessageId?: string
}
```

| 属性                  | 类型     | 描述                                      |
| --------------------- | -------- | ----------------------------------------- |
| `subagentRunId`       | `string` | 该次调用的不透明标识符                    |
| `name`                | `string` | 声明的子智能体名称或类型，用于展示        |
| `description`         | `string` | 可选的描述                                |
| `parentSubagentRunId` | `string` | 嵌套时表示可选的外层子智能体              |
| `parentToolCallId`    | `string` | 生成该子智能体的可选工具调用              |
| `parentMessageId`     | `string` | 持有该工具调用的可选消息                  |

### SubagentFinishedEvent {#subagentfinishedevent}

将一次子智能体调用标记为完成。

```typescript
type SubagentFinishedEvent = BaseEvent & {
  type: EventType.SUBAGENT_FINISHED
  subagentRunId: string
  result?: any
  outcome?: { type: "success" } | { type: "suspended"; interruptIds?: string[] }
}
```

| 属性            | 类型     | 描述                                                    |
| --------------- | -------- | ------------------------------------------------------- |
| `subagentRunId` | `string` | 与 `SubagentStartedEvent` 中的 id 一致                  |
| `result`        | `any`    | 可选载荷，对应 `RunFinishedEvent.result`                |
| `outcome`       | `SubagentFinishedOutcome` | 可选的可判别联合；省略表示成功（旧有读法）。`{ type: "suspended", interruptIds?: string[] }` 表示该子智能体已做检查点，正等待外部输入；`interruptIds` 指明哪些运行级中断的应答可以恢复它。 |

### SubagentErrorEvent {#subagenterrorevent}

将一次子智能体调用标记为失败。

```typescript
type SubagentErrorEvent = BaseEvent & {
  type: EventType.SUBAGENT_ERROR
  subagentRunId: string
  message: string
  code?: string
}
```

| 属性            | 类型     | 描述                                      |
| --------------- | -------- | ----------------------------------------- |
| `subagentRunId` | `string` | 与 `SubagentStartedEvent` 中的 id 一致    |
| `message`       | `string` | 人类可读的错误消息                        |
| `code`          | `string` | 可选的错误码                              |

### 其他事件上的归属 {#attribution-on-other-events}

大多数事件类型接受一个可选的 `subagentRunId`。不带它的事件属于父智能体，因此从不设置该字段的事件流与子智能体出现之前的行为完全一致。

`RunStartedEvent`、`RunFinishedEvent` 和 `RunErrorEvent` 不可归属——它们描述的是整个运行。`MessagesSnapshotEvent` 则按消息分别携带归属信息，因为一次快照会混合来自多个生产方的消息。

`StateSnapshotEvent` 和 `StateDeltaEvent` 可归属，但其上的归属是来源标记而非所有权——它记录的是哪个子智能体产生了该更新。状态始终以运行为范围，因此带归属的快照或增量与不带归属的一样，都会应用到该运行唯一的状态文档上。不存在按子智能体划分的状态。

订阅者可以通过 `onSubagentStartedEvent`、`onSubagentFinishedEvent` 和 `onSubagentErrorEvent` 直接对生命周期做出反应。

## 特殊事件 {#special-events}

### RawEvent {#rawevent}

用于透传来自外部系统的事件。

```typescript
type RawEvent = BaseEvent & {
  type: EventType.RAW
  event: any
  source?: string
}
```

| 属性     | 类型                | 描述             |
| -------- | ------------------- | ---------------- |
| `event`  | `any`               | 原始事件数据     |
| `source` | `string`（可选）    | 事件的来源       |

### CustomEvent {#customevent}

用于应用特定的自定义事件。

```typescript
type CustomEvent = BaseEvent & {
  type: EventType.CUSTOM
  name: string
  value: any
}
```

| 属性    | 类型     | 描述                     |
| ------- | -------- | ------------------------ |
| `name`  | `string` | 自定义事件的名称         |
| `value` | `any`    | 与该事件关联的值         |

## 已弃用的事件 {#deprecated-events}

!!! warning
    `THINKING_*` 事件已弃用，将在 1.0.0 版本中移除。
      新实现应改用 `REASONING_*` 事件。

### Thinking 事件（已弃用） {#thinking-events-deprecated}

以下事件类型已弃用：

| 已弃用的事件                    | 替代方案                    |
| ------------------------------- | --------------------------- |
| `THINKING_START`                | `REASONING_START`           |
| `THINKING_END`                  | `REASONING_END`             |
| `THINKING_TEXT_MESSAGE_START`   | `REASONING_MESSAGE_START`   |
| `THINKING_TEXT_MESSAGE_CONTENT` | `REASONING_MESSAGE_CONTENT` |
| `THINKING_TEXT_MESSAGE_END`     | `REASONING_MESSAGE_END`     |

详细的迁移指引见[推理迁移](../../../concepts/reasoning.md#migration-from-thinking-events)。

## 事件 Schema {#event-schemas}

SDK 使用 Zod schema 校验事件：

```typescript
const EventSchemas = z.discriminatedUnion("type", [
  TextMessageStartEventSchema,
  TextMessageContentEventSchema,
  TextMessageEndEventSchema,
  ToolCallStartEventSchema,
  ToolCallArgsEventSchema,
  ToolCallEndEventSchema,
  ToolCallResultEventSchema,
  StateSnapshotEventSchema,
  StateDeltaEventSchema,
  MessagesSnapshotEventSchema,
  ActivitySnapshotEventSchema,
  ActivityDeltaEventSchema,
  RawEventSchema,
  CustomEventSchema,
  RunStartedEventSchema,
  RunFinishedEventSchema,
  RunErrorEventSchema,
  StepStartedEventSchema,
  StepFinishedEventSchema,
  ReasoningStartEventSchema,
  ReasoningMessageStartEventSchema,
  ReasoningMessageContentEventSchema,
  ReasoningMessageEndEventSchema,
  ReasoningMessageChunkEventSchema,
  ReasoningEndEventSchema,
  ReasoningEncryptedValueEventSchema,
])
```

这支持在运行时校验事件，并提供 TypeScript 类型推断。

### ToolCallChunkEvent {#toolcallchunkevent}

便捷事件，在 JS/TS 客户端中会自动展开为 `ToolCallStart` → `ToolCallArgs` → `ToolCallEnd`。

```typescript
type ToolCallChunkEvent = BaseEvent & {
  type: EventType.TOOL_CALL_CHUNK
  toolCallId?: string // required on the first chunk for a tool call
  toolCallName?: string // required on the first chunk for a tool call
  parentMessageId?: string
  delta?: string
}
```

行为

- 省略 start/end：客户端会把块序列转换为标准的 start/args/end 三元组。
- 首块要求：第一个块必须同时包含 `toolCallId` 和 `toolCallName`；若给出 `parentMessageId`，它会传播到 `ToolCallStart`。
- 流式传输：具有相同 `toolCallId` 的后续块会发出 `ToolCallArgs`。当工具调用改变或事件流完成时，会自动发出 `ToolCallEnd`。
