---
title: "事件"
description: "AGUI.Abstractions 中流式事件类型的文档"
---
<em class="lead">AGUI.Abstractions 中流式事件类型的文档</em>

# 事件 {#events}

AG-UI 采用基于流式事件的架构。事件是智能体后端与前端 UI 之间通信的单元。在 .NET 中，每个协议事件都派生自 `BaseEvent`，并带有 `type` 判别字段。

## 事件类型常量 {#event-type-constants}

`AGUIEventTypes` 定义了 SCREAMING_SNAKE_CASE 形式的线上判别值：

```csharp
AGUIEventTypes.RunStarted; // "RUN_STARTED"
AGUIEventTypes.RunFinished; // "RUN_FINISHED"
AGUIEventTypes.RunError; // "RUN_ERROR"
AGUIEventTypes.StepStarted; // "STEP_STARTED"
AGUIEventTypes.StepFinished; // "STEP_FINISHED"
AGUIEventTypes.TextMessageStart; // "TEXT_MESSAGE_START"
AGUIEventTypes.TextMessageContent; // "TEXT_MESSAGE_CONTENT"
AGUIEventTypes.TextMessageEnd; // "TEXT_MESSAGE_END"
AGUIEventTypes.ToolCallStart; // "TOOL_CALL_START"
AGUIEventTypes.ToolCallArgs; // "TOOL_CALL_ARGS"
AGUIEventTypes.ToolCallEnd; // "TOOL_CALL_END"
AGUIEventTypes.ToolCallResult; // "TOOL_CALL_RESULT"
AGUIEventTypes.StateSnapshot; // "STATE_SNAPSHOT"
AGUIEventTypes.StateDelta; // "STATE_DELTA"
AGUIEventTypes.MessagesSnapshot; // "MESSAGES_SNAPSHOT"
AGUIEventTypes.ActivitySnapshot; // "ACTIVITY_SNAPSHOT"
AGUIEventTypes.ActivityDelta; // "ACTIVITY_DELTA"
AGUIEventTypes.ReasoningStart; // "REASONING_START"
AGUIEventTypes.ReasoningMessageStart; // "REASONING_MESSAGE_START"
AGUIEventTypes.ReasoningMessageContent; // "REASONING_MESSAGE_CONTENT"
AGUIEventTypes.ReasoningMessageEnd; // "REASONING_MESSAGE_END"
AGUIEventTypes.ReasoningMessageChunk; // "REASONING_MESSAGE_CHUNK"
AGUIEventTypes.ReasoningEnd; // "REASONING_END"
AGUIEventTypes.ReasoningEncryptedValue; // "REASONING_ENCRYPTED_VALUE"
AGUIEventTypes.Raw; // "RAW"
AGUIEventTypes.Custom; // "CUSTOM"
```

## BaseEvent {#baseevent}

所有事件都继承自 `BaseEvent`。

```csharp
public abstract class BaseEvent
{
    public abstract string Type { get; } // "type"
    public long? Timestamp { get; set; } // "timestamp"
    public JsonElement? RawEvent { get; set; } // "rawEvent"
    public JsonElement? Metadata { get; set; } // "metadata"
}
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `string` | 事件判别字段 |
| `Timestamp` | `timestamp` | `long?` | 可选的事件时间戳 |
| `RawEvent` | `rawEvent` | `JsonElement?` | 可选的原始事件数据 |
| `Metadata`  | `metadata`  | `JsonElement?` | 可选的额外信息，按 key 开放 |

`Metadata` 按 key 开放：任何 JSON 值都允许出现在某个 key 之下，包括 `null`。该对象可以缺失，但存在时绝不为 `null`——显式的 `null` 会被读回为缺失，缺失的对象会从线上格式中省略，而不是序列化为 `null`。`AGUIMetadata.ReservedKey`（`"ag-ui"`）保留给 AG-UI 自用。

## 生命周期事件 {#lifecycle-events}

生命周期事件表示运行与步骤的生命周期。

### RunStartedEvent {#runstartedevent}

表示一次智能体运行的开始。

```csharp
var evt = new RunStartedEvent
{
    ThreadId = "thread-1",
    RunId = "run-1",
    ParentRunId = "run-0",
    Input = input,
    ProtocolVersion = AGUIProtocol.Version
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"RUN_STARTED"` | 事件判别字段 |
| `ThreadId` | `threadId` | `string` | 会话线程 ID |
| `RunId` | `runId` | `string` | 智能体运行 ID |
| `ParentRunId` | `parentRunId` | `string?` | 可选的父运行 ID |
| `Input` | `input` | `RunAgentInput?` | 该运行的可选输入载荷 |
| `ProtocolVersion` | `protocolVersion` | `string?` | 生产方使用的 AG-UI 协议版本。在每个手工构造的事件上将它设为 `AGUIProtocol.Version`（`"1.0"`）；缺少它的事件流会被读作 1.0 之前 |

### RunFinishedEvent {#runfinishedevent}

表示一次智能体运行的完成。

```csharp
var evt = new RunFinishedEvent
{
    ThreadId = "thread-1",
    RunId = "run-1",
    Outcome = new RunFinishedSuccessOutcome()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"RUN_FINISHED"` | 事件判别字段 |
| `ThreadId` | `threadId` | `string` | 会话线程 ID |
| `RunId` | `runId` | `string` | 智能体运行 ID |
| `Result` | `result` | `JsonElement?` | 可选的运行结果 |
| `Outcome` | `outcome` | `RunFinishedOutcome?` | 可选的带类型结果 |
| `Usage` | `usage` | `IList<TokenUsage>?` | 该运行的可选 token 用量 |

`RunFinishedOutcome` 是一个多态值，其 `type` 为 `"success"` 或 `"interrupt"`。`RunFinishedInterruptOutcome` 携带 `interrupts`，即 `IList<AGUIInterrupt>`。

`Usage` 在 [TokenUsage](#tokenusage) 中描述。

### RunErrorEvent {#runerrorevent}

表示智能体运行期间发生错误。

```csharp
var evt = new RunErrorEvent
{
    Message = "The model request failed.",
    Code = "model_error"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"RUN_ERROR"` | 事件判别字段 |
| `Message` | `message` | `string` | 错误消息 |
| `Code` | `code` | `string?` | 可选的错误码 |
| `Usage` | `usage` | `IList<TokenUsage>?` | 失败前累积的可选部分用量 |

### TokenUsage {#tokenusage}

提供方报告的 token 用量，由两个终结性运行事件携带。每个 `(provider, model)` 对一条记录，因此调用多个模型的运行会将其分别保留；只需要总计的消费方可以对各条记录求和。

```csharp
var evt = new RunFinishedEvent
{
    ThreadId = "thread-1",
    RunId = "run-1",
    Outcome = new RunFinishedSuccessOutcome(),
    Usage =
    [
        new TokenUsage
        {
            Provider = "openai",
            Model = "gpt-4o",
            InputTokens = 658,
            OutputTokens = 188,
            TotalTokens = 846
        }
    ]
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Provider` | `provider` | `string?` | 处理该请求的提供方 |
| `Model` | `model` | `string?` | 处理该请求的模型 |
| `InputTokens` | `inputTokens` | `long?` | 全部输入 token，含缓存读取与写入 |
| `OutputTokens` | `outputTokens` | `long?` | 全部输出 token，含推理 |
| `TotalTokens` | `totalTokens` | `long?` | `inputTokens` 加上 `outputTokens` |
| `ReasoningTokens` | `reasoningTokens` | `long?` | 用于推理的输出 token；属于 `outputTokens` 的一部分 |
| `CachedInputTokens` | `cachedInputTokens` | `long?` | 从提示缓存读取的输入 token；属于 `inputTokens` 的一部分 |
| `CacheWriteInputTokens` | `cacheWriteInputTokens` | `long?` | 写入提示缓存的输入 token；属于 `inputTokens` 的一部分。`Microsoft.Extensions.AI` 没有对应的一等属性，因此 `AGUI.Server` 从 `UsageDetails.AdditionalCounts["CacheWriteInputTokens"]` 读取它，`AGUI.Client` 则写入该处 |

每个字段都是可选的。计数为 null 表示提供方未报告该值，这与报告为零不同——因此 `usage` 绝不会凭空造出提供方未提供的计数。该类型按设计仅含数值：它不携带提示、补全、消息、工具参数或线程/运行/用户标识符。

使用 `AGUI.Server` 托管时，`Microsoft.Extensions.AI` 以 `UsageContent` 报告的用量会被自动累积并附加到终结事件上。`ModelId` 提供模型标签；用 `AGUIStreamOptions.WithUsageProvider("openai")` 设置提供方标签。

### StepStartedEvent {#stepstartedevent}

表示某个具名步骤的开始。

```csharp
var evt = new StepStartedEvent { StepName = "plan" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"STEP_STARTED"` | 事件判别字段 |
| `StepName` | `stepName` | `string` | 步骤名称 |

### StepFinishedEvent {#stepfinishedevent}

表示某个具名步骤的完成。

```csharp
var evt = new StepFinishedEvent { StepName = "plan" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"STEP_FINISHED"` | 事件判别字段 |
| `StepName` | `stepName` | `string` | 步骤名称 |

## 文本消息事件 {#text-message-events}

文本消息事件以 start/content/end 序列流式传输助手文本。

### TextMessageStartEvent {#textmessagestartevent}

```csharp
var evt = new TextMessageStartEvent
{
    MessageId = "msg-1",
    Role = AGUIRoles.Assistant,
    Name = "assistant"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TEXT_MESSAGE_START"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 消息 ID |
| `Role` | `role` | `string` | 消息 role，通常为 `"assistant"` |
| `Name` | `name` | `string?` | 可选的发送者名称 |

### TextMessageContentEvent {#textmessagecontentevent}

```csharp
var evt = new TextMessageContentEvent
{
    MessageId = "msg-1",
    Delta = "Hello"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TEXT_MESSAGE_CONTENT"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 来自 start 事件的消息 ID |
| `Delta` | `delta` | `string` | 文本增量 |

### TextMessageEndEvent {#textmessageendevent}

```csharp
var evt = new TextMessageEndEvent { MessageId = "msg-1" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TEXT_MESSAGE_END"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 来自 start 事件的消息 ID |

## 工具调用事件 {#tool-call-events}

工具调用事件流式传输工具调用的参数与可选的服务端结果。

### ToolCallStartEvent {#toolcallstartevent}

```csharp
var evt = new ToolCallStartEvent
{
    ParentMessageId = "msg-1",
    ToolCallId = "call-1",
    ToolCallName = "get_weather"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TOOL_CALL_START"` | 事件判别字段 |
| `ParentMessageId` | `parentMessageId` | `string?` | 可选的父助手消息 ID |
| `ToolCallId` | `toolCallId` | `string` | 工具调用 ID |
| `ToolCallName` | `toolCallName` | `string` | 工具名称 |

### ToolCallArgsEvent {#toolcallargsevent}

```csharp
var evt = new ToolCallArgsEvent
{
    ToolCallId = "call-1",
    Delta = """{"city":"Seattle"}"""
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TOOL_CALL_ARGS"` | 事件判别字段 |
| `ToolCallId` | `toolCallId` | `string` | 工具调用 ID |
| `Delta` | `delta` | `string` | 参数 JSON 块 |

### ToolCallEndEvent {#toolcallendevent}

```csharp
var evt = new ToolCallEndEvent { ToolCallId = "call-1" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TOOL_CALL_END"` | 事件判别字段 |
| `ToolCallId` | `toolCallId` | `string` | 工具调用 ID |

### ToolCallResultEvent {#toolcallresultevent}

```csharp
var evt = new ToolCallResultEvent
{
    MessageId = "tool-msg-1",
    ToolCallId = "call-1",
    Content = """{"temperature":72}""",
    Role = AGUIRoles.Tool
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"TOOL_CALL_RESULT"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 工具结果消息 ID |
| `ToolCallId` | `toolCallId` | `string` | 工具调用 ID |
| `Content` | `content` | `string` | 工具结果内容 |
| `Role` | `role` | `string?` | 可选的 role，通常为 `"tool"` |

## 状态管理事件 {#state-management-events}

状态事件同步前端状态与消息历史。

### StateSnapshotEvent {#statesnapshotevent}

提供完整的状态快照。

```csharp
var evt = new StateSnapshotEvent
{
    Snapshot = JsonDocument.Parse("""{"draft":"hello"}""").RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"STATE_SNAPSHOT"` | 事件判别字段 |
| `Snapshot` | `snapshot` | `JsonElement` | 完整状态值 |

### StateDeltaEvent {#statedeltaevent}

提供增量状态变更，通常为 JSON Patch 操作。

```csharp
var evt = new StateDeltaEvent
{
    Delta = JsonDocument.Parse("""
        [{ "op": "replace", "path": "/draft", "value": "hello world" }]
        """).RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"STATE_DELTA"` | 事件判别字段 |
| `Delta` | `delta` | `JsonElement` | 状态增量载荷 |

### MessagesSnapshotEvent {#messagessnapshotevent}

用服务器视图替换前端会话历史。

```csharp
var evt = new MessagesSnapshotEvent
{
    Messages =
    [
        new AGUIUserMessage { Id = "user-1", Content = "Hello" }
    ]
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"MESSAGES_SNAPSHOT"` | 事件判别字段 |
| `Messages` | `messages` | `IList<AGUIMessage>` | 完整消息列表 |

## 推理事件 {#reasoning-events}

推理事件暴露模型或智能体的推理流。它们可以创建并更新消息历史中的 `AGUIReasoningMessage` 条目。

### ReasoningStartEvent {#reasoningstartevent}

```csharp
var evt = new ReasoningStartEvent { MessageId = "reasoning-1" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_START"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 推理阶段 ID |

### ReasoningMessageStartEvent {#reasoningmessagestartevent}

```csharp
var evt = new ReasoningMessageStartEvent
{
    MessageId = "reasoning-1",
    Role = AGUIRoles.Reasoning
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_MESSAGE_START"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 推理消息 ID |
| `Role` | `role` | `string` | 默认为 `"reasoning"` |

### ReasoningMessageContentEvent {#reasoningmessagecontentevent}

```csharp
var evt = new ReasoningMessageContentEvent
{
    MessageId = "reasoning-1",
    Delta = "Checking constraints..."
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_MESSAGE_CONTENT"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 推理消息 ID |
| `Delta` | `delta` | `string` | 推理内容增量 |

### ReasoningMessageEndEvent {#reasoningmessageendevent}

```csharp
var evt = new ReasoningMessageEndEvent { MessageId = "reasoning-1" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_MESSAGE_END"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 推理消息 ID |

### ReasoningMessageChunkEvent {#reasoningmessagechunkevent}

带可选字段的紧凑推理消息块事件。

```csharp
var evt = new ReasoningMessageChunkEvent
{
    MessageId = "reasoning-1",
    Delta = "Partial reasoning..."
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_MESSAGE_CHUNK"` | 事件判别字段 |
| `MessageId` | `messageId` | `string?` | 可选的推理消息 ID |
| `Delta` | `delta` | `string?` | 可选的推理内容增量 |

### ReasoningEndEvent {#reasoningendevent}

```csharp
var evt = new ReasoningEndEvent { MessageId = "reasoning-1" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_END"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 推理阶段 ID |

### ReasoningEncryptedValueEvent {#reasoningencryptedvalueevent}

将加密值附加到消息或工具调用。

```csharp
var evt = new ReasoningEncryptedValueEvent
{
    Subtype = "message",
    EntityId = "reasoning-1",
    EncryptedValue = "opaque-token"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"REASONING_ENCRYPTED_VALUE"` | 事件判别字段 |
| `Subtype` | `subtype` | `string` | 实体子类型，如 `"message"` 或 `"tool-call"` |
| `EntityId` | `entityId` | `string` | 消息或工具调用 ID |
| `EncryptedValue` | `encryptedValue` | `string` | 不透明的加密值 |

## 活动事件 {#activity-events}

活动事件为 UI 渲染器携带结构化的进度状态。

### ActivitySnapshotEvent {#activitysnapshotevent}

```csharp
var evt = new ActivitySnapshotEvent
{
    MessageId = "activity-1",
    ActivityType = "PLAN",
    Content = JsonDocument.Parse("""{"status":"running"}""").RootElement.Clone(),
    Replace = true
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"ACTIVITY_SNAPSHOT"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 活动消息 ID |
| `ActivityType` | `activityType` | `string` | 活动判别字段 |
| `Content` | `content` | `JsonElement` | 结构化活动内容 |
| `Replace` | `replace` | `bool?` | 可选的替换/合并提示 |

### ActivityDeltaEvent {#activitydeltaevent}

```csharp
var evt = new ActivityDeltaEvent
{
    MessageId = "activity-1",
    ActivityType = "PLAN",
    Patch = JsonDocument.Parse("""
        [{ "op": "replace", "path": "/status", "value": "done" }]
        """).RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"ACTIVITY_DELTA"` | 事件判别字段 |
| `MessageId` | `messageId` | `string` | 活动消息 ID |
| `ActivityType` | `activityType` | `string` | 活动判别字段 |
| `Patch` | `patch` | `JsonElement` | 活动 JSON Patch 载荷 |

## 子智能体事件 {#subagent-events}

这些事件报告智能体将工作委派给了子智能体，使前端可以将输出归属于产生它的子智能体。归属信息本身以可选的 `SubagentRunId` 出现在大多数其他事件类型上。

`SubagentRunId` 标识**一次调用**，而非可复用的子智能体定义——同一个子智能体运行两次会产生两个不同的值。完整模型见[子智能体](../../../concepts/subagents.md)。

### SubagentStartedEvent {#subagentstartedevent}

宣告一次新的子智能体调用，并为其命名以供展示。

```csharp
var evt = new SubagentStartedEvent
{
    SubagentRunId = "sub-1",
    Name = "researcher",
    Description = "Searches for supporting sources"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"SUBAGENT_STARTED"` | 事件判别字段 |
| `SubagentRunId` | `subagentRunId` | `string` | 该次调用的不透明 id |
| `Name` | `name` | `string` | 声明的子智能体名称，用于展示 |
| `Description` | `description` | `string?` | 可选的描述 |
| `ParentSubagentRunId` | `parentSubagentRunId` | `string?` | 嵌套时表示外层子智能体 |
| `ParentToolCallId` | `parentToolCallId` | `string?` | 生成该子智能体的工具调用 |
| `ParentMessageId` | `parentMessageId` | `string?` | 持有该工具调用的消息 |

### SubagentFinishedEvent {#subagentfinishedevent}

将一次子智能体调用标记为完成。

```csharp
var evt = new SubagentFinishedEvent { SubagentRunId = "sub-1" };
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"SUBAGENT_FINISHED"` | 事件判别字段 |
| `SubagentRunId` | `subagentRunId` | `string` | 与 `SubagentStartedEvent` 中的 id 一致 |
| `Result` | `result` | `object?` | 可选载荷，对应 `RunFinishedEvent.Result` |
| `Outcome` | `outcome` | `SubagentFinishedOutcome?` | `SubagentFinishedSuccessOutcome` 或 `SubagentFinishedSuspendedOutcome`（带可选的 `InterruptIds`）；`null` 表示成功（旧有读法）。suspended 表示该子智能体已做检查点，正等待外部输入；`InterruptIds` 指明哪些运行级中断的应答可以恢复它。 |

### SubagentErrorEvent {#subagenterrorevent}

将一次子智能体调用标记为失败。

```csharp
var evt = new SubagentErrorEvent
{
    SubagentRunId = "sub-1",
    Message = "Search backend unavailable"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"SUBAGENT_ERROR"` | 事件判别字段 |
| `SubagentRunId` | `subagentRunId` | `string` | 与 `SubagentStartedEvent` 中的 id 一致 |
| `Message` | `message` | `string` | 人类可读的错误消息 |
| `Code` | `code` | `string?` | 可选的错误码 |

### 其他事件上的归属 {#attribution-on-other-events}

大多数事件类型都暴露一个可选的 `SubagentRunId`。不带它的事件属于父智能体，因此从不设置它的事件流与子智能体出现之前的行为完全一致。

`RunStartedEvent`、`RunFinishedEvent` 和 `RunErrorEvent` 不可归属——它们描述的是整个运行。`MessagesSnapshotEvent` 则按消息分别携带归属信息。

`StateSnapshotEvent` 和 `StateDeltaEvent` 可归属，但其上的归属是来源标记而非所有权——它记录的是哪个子智能体产生了该更新。状态始终以运行为范围，因此带归属的快照或增量与不带归属的一样，都会应用到该运行唯一的状态文档上。

当事件被转换为 `Microsoft.Extensions.AI` 类型时，归属信息保存在 `ChatMessage.AdditionalProperties` 的 `agui.subagentRunId` key 下，因为这些类型没有专门用于它的字段。

## 特殊事件 {#special-events}

### RawEvent {#rawevent}

透传未经处理的外部数据。

```csharp
var evt = new RawEvent
{
    Event = JsonDocument.Parse("""{"provider":"example","event":"token"}""").RootElement.Clone(),
    Source = "provider"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"RAW"` | 事件判别字段 |
| `Event` | `event` | `JsonElement` | 原始载荷 |
| `Source` | `source` | `string?` | 可选的来源标识符 |

### CustomEvent {#customevent}

携带应用特定的数据。

```csharp
var evt = new CustomEvent
{
    Name = "progress",
    Value = JsonDocument.Parse("""{"percent":50}""").RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"CUSTOM"` | 事件判别字段 |
| `Name` | `name` | `string` | 自定义事件名称 |
| `Value` | `value` | `JsonElement?` | 可选的自定义载荷 |

## 序列化 {#serialization}

`BaseEvent` 使用以 `type` 字段为 key 的基于判别字段的 JSON 转换器。所有具体事件类型都注册在 `AGUIJsonSerializerContext` 中。

```csharp
BaseEvent evt = new TextMessageContentEvent
{
    MessageId = "msg-1",
    Delta = "Hello"
};

var json = JsonSerializer.Serialize(
    evt,
    AGUIJsonSerializerContext.Default.BaseEvent);
```
