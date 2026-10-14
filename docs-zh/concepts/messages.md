---
title: "消息"
description: "理解 AG-UI 中的消息结构与通信"
---
<em class="lead">理解 AG-UI 中的消息结构与通信</em>

# 消息 {#messages}

消息构成 AG-UI 协议中通信的骨干。它们表示用户与 AI 智能体之间的会话历史，
并提供一种标准化方式来交换信息，而无需关心所使用的底层 AI 服务。

## 消息结构 {#message-structure}

AG-UI 消息遵循厂商中立的格式，在保持结构一致的同时确保不同 AI 提供方之间的兼容性。
这使应用可以在不同 AI 服务（如 OpenAI、Anthropic 或自定义模型）之间切换，
而无需修改客户端实现。

基本消息结构包含：

```typescript
interface BaseMessage {
  id: string // Unique identifier for the message
  role: string // The role of the sender (user, assistant, system, tool, reasoning)
  content?: string // Optional text content of the message
  name?: string // Optional name of the sender
  encryptedContent?: string // Optional encrypted content for privacy-preserving state continuity
  metadata?: Record<string, any> // Optional extra information attached to the message
}
```

`role` 判别字段可以是 `"user"`、`"assistant"`、`"system"`、`"tool"`、
`"developer"`、`"activity"` 或 `"reasoning"`。具体消息类型在此形状之上
扩展它们所需的字段。

每种消息类型都携带 `metadata`，这是一个按 key 开放的可选对象，会随着消息由其事件
构建而不断累积。工具调用各自携带自己的 `metadata`。相关规则见 [元数据](./metadata.md)。

> `encryptedContent` 字段支持隐私保护的工作流，其中敏感内容（例如推理链）
> 可以在多轮之间传递，而不暴露原始内容。这对零数据保留（ZDR）合规和
> `store:false` 场景尤其有用。

## 消息类型 {#message-types}

AG-UI 支持多种消息类型，以适配会话中的不同参与者：

### 用户消息 {#user-messages}

从最终用户发送给智能体的消息：

```typescript
interface UserMessage {
  id: string
  role: "user"
  content: string | ContentPart[] // Text or multimodal input from the user
  name?: string // Optional user identifier
}

type ContentPart =
  | TextPart
  | ImagePart
  | AudioPart
  | VideoPart
  | DocumentPart

interface DataSource {
  type: "data"
  value: string
  mimeType: string
}

interface UrlSource {
  type: "url"
  value: string
  mimeType?: string
}

interface FileSource {
  type: "file"
  value: string // a handle the provider issued; opaque, never fetched
  provider?: string // who issued it, e.g. "openai"
  mimeType?: string
}

type PartSource = DataSource | UrlSource | FileSource

interface TextPart {
  type: "text"
  text: string
}

interface ImagePart {
  type: "image"
  source: PartSource
  metadata?: Record<string, unknown>
}

interface AudioPart {
  type: "audio"
  source: PartSource
  metadata?: Record<string, unknown>
}

interface VideoPart {
  type: "video"
  source: PartSource
  metadata?: Record<string, unknown>
}

interface DocumentPart {
  type: "document"
  source: PartSource
  metadata?: Record<string, unknown>
}
```

> 在 Python 中，此前的 `BinaryInputContent` 模型已废弃，但作为兼容路径
> 暂时仍然可用。

这一结构在保持传统纯文本输入可用的同时，也支持在同一条消息中承载更丰富的载荷，
例如图像、音频片段或上传的文件。

### 助手消息 {#assistant-messages}

从 AI 助手发送给用户的消息：

```typescript
interface AssistantMessage {
  id: string
  role: "assistant"
  content?: string // Text response from the assistant (optional if using tool calls)
  name?: string // Optional assistant identifier
  toolCalls?: ToolCall[] // Optional tool calls made by the assistant
  encryptedContent?: string // Optional encrypted content for state continuity
}
```

### 系统消息 {#system-messages}

提供给智能体的指令或上下文：

```typescript
interface SystemMessage {
  id: string
  role: "system"
  content: string // Instructions or context for the agent
  name?: string // Optional identifier
}
```

### 工具消息 {#tool-messages}

工具执行的结果：

```typescript
interface ToolMessage {
  id: string
  role: "tool"
  content: string // Result from the tool execution
  toolCallId: string // ID of the tool call this message responds to
  error?: string // Optional error message if the tool execution failed
  encryptedValue?: string // Optional encrypted reasoning for state continuity
}
```

要点：

- `toolCallId` 将结果链接回原始工具调用
- 使用 `error` 表示工具执行失败
- 使用 `encryptedValue` 附加加密的思维链，说明智能体如何解释或处理该工具结果

### 活动消息 {#activity-messages}

仅存在于前端的结构化 UI 消息。用于进度、状态或任何不应发送给模型的自定义视觉元素：

```typescript
interface ActivityMessage {
  id: string
  role: "activity"
  activityType: string // e.g. "PLAN", "SEARCH", "SCRAPE"
  content: Record<string, any> // Structured payload rendered by the frontend
}
```

要点

- 通过 `ACTIVITY_SNAPSHOT` 和 `ACTIVITY_DELTA` 发出，以支持实时、
  可更新的 UI（清单、步骤、进行中的搜索等）。
- **仅限前端：** 永远不会转发给智能体，因此无需过滤，也不会造成 LLM 混淆。
- **可自定义：** 定义你自己的 `activityType` 与 `content`，并渲染与之匹配的 UI 组件。
- **可流式传输：** 可以随时间更新，以支持长时间运行的操作。
- 通过把自定义事件转换为持久化的消息对象，帮助持久化/恢复这些事件。

### 开发者消息 {#developer-messages}

用于开发或调试的内部消息：

```typescript
interface DeveloperMessage {
  id: string
  role: "developer"
  content: string
  name?: string
}
```

### 推理消息 {#reasoning-messages}

表示智能体内部推理或思维链过程的消息：

```typescript
interface ReasoningMessage {
  id: string
  role: "reasoning"
  content: string // Reasoning content (visible to client)
  encryptedValue?: string // Optional encrypted reasoning for state continuity
}
```

!!! tip
    与 Activity 消息不同，Reasoning 消息用于表示
      智能体的内部思考过程，出于隐私考虑可能被加密，并且
      需要在后续轮次中回传给智能体以进一步处理。

要点：

- 通过 `REASONING_MESSAGE_START`、`REASONING_MESSAGE_CONTENT` 和
  `REASONING_MESSAGE_END` 事件发出。
- **可见性控制：** 内容可以对用户可见（作为摘要），也可以完全加密。
- **加密值：** 使用 `REASONING_ENCRYPTED_VALUE` 事件将加密的思维链附加到
  消息或工具调用，而不暴露内容。
- **状态连续性：** 加密的推理项可以在多轮对话之间传递，而不暴露原始思维链。
- **隐私优先：** 在保留推理能力的同时支持 `store:false` 与零数据保留（ZDR）策略。
- **与助手消息分离：** 推理与最终响应保持区分，以避免污染会话历史。

推理的流式事件生命周期见[推理事件](./events.md#reasoning-events)。

## 厂商中立性 {#vendor-neutrality}

AG-UI 消息设计为厂商中立，这意味着它们可以轻松地与各种 AI 提供方使用的专有格式
相互映射：

```typescript
// Example: Converting AG-UI messages to OpenAI format
const openaiMessages = agUiMessages
  .filter((msg) => ["user", "system", "assistant"].includes(msg.role))
  .map((msg) => ({
    role: msg.role as "user" | "system" | "assistant",
    content: msg.content || "",
    // Map tool calls if present
    ...(msg.role === "assistant" && msg.toolCalls
      ? {
          tool_calls: msg.toolCalls.map((tc) => ({
            id: tc.id,
            type: tc.type,
            function: {
              name: tc.function.name,
              arguments: tc.function.arguments,
            },
          })),
        }
      : {}),
  }))
```

这一抽象使 AG-UI 可以充当通用接口，而无需关心底层 AI 服务。

## 消息同步 {#message-synchronization}

消息可以通过两种主要机制在客户端与服务器之间同步：

### 完整快照 {#complete-snapshots}

`MESSAGES_SNAPSHOT` 事件提供会话中所有消息的完整视图：

```typescript
interface MessagesSnapshotEvent {
  type: EventType.MESSAGES_SNAPSHOT
  messages: Message[] // Complete array of all messages
}
```

这通常用于：

- 初始化会话时
- 连接中断之后
- 发生重大状态变化时
- 确保客户端与服务器同步

### 流式消息 {#streaming-messages}

对于实时交互，新消息可以在生成时流式传输：

1. **开始一条消息**：表示正在创建一条新消息

   ```typescript
   interface TextMessageStartEvent {
     type: EventType.TEXT_MESSAGE_START
     messageId: string
     role: string
   }
   ```

2. **流式传输内容**：在内容块可用时发送它们

   ```typescript
   interface TextMessageContentEvent {
     type: EventType.TEXT_MESSAGE_CONTENT
     messageId: string
     delta: string // Text chunk to append
   }
   ```

3. **结束一条消息**：表明消息已完成
   ```typescript
   interface TextMessageEndEvent {
     type: EventType.TEXT_MESSAGE_END
     messageId: string
   }
   ```

这种流式方式通过即时反馈提供响应迅速的用户体验。

## 消息中的工具集成 {#tool-integration-in-messages}

AG-UI 消息优雅地集成了工具使用，使智能体可以执行操作并处理其结果：

### 工具调用 {#tool-calls}

工具调用内嵌在助手消息中：

```typescript
interface ToolCall {
  id: string // Unique ID for this tool call
  type: "function" // Type of tool call
  function: {
    name: string // Name of the function to call
    arguments: string // JSON-encoded string of arguments
  }
}
```

带工具调用的助手消息示例：

```typescript
{
  id: "msg_123",
  role: "assistant",
  content: "I'll help you with that calculation.",
  toolCalls: [
    {
      id: "call_456",
      type: "function",
      function: {
        name: "calculate",
        arguments: '{"expression": "24 * 7"}'
      }
    }
  ]
}
```

### 工具结果 {#tool-results}

工具执行的结果表示为工具消息：

```typescript
{
  id: "result_789",
  role: "tool",
  content: "168",
  toolCallId: "call_456" // References the original tool call
}
```

这形成了清晰的工具使用链条：

1. 助手请求一次工具调用
2. 工具执行并返回结果
3. 助手可以引用该结果并作出响应

## 流式工具调用 {#streaming-tool-calls}

与文本消息类似，工具调用也可以流式传输，以实时展示智能体的操作：

1. **开始一次工具调用**：

   ```typescript
   interface ToolCallStartEvent {
     type: EventType.TOOL_CALL_START
     toolCallId: string
     toolCallName: string
     parentMessageId?: string // Optional link to parent message
   }
   ```

2. **流式传输参数**：

   ```typescript
   interface ToolCallArgsEvent {
     type: EventType.TOOL_CALL_ARGS
     toolCallId: string
     delta: string // JSON fragment to append to arguments
   }
   ```

3. **结束一次工具调用**：
   ```typescript
   interface ToolCallEndEvent {
     type: EventType.TOOL_CALL_END
     toolCallId: string
   }
   ```

这使前端可以在智能体构建其推理的过程中逐步展示被调用的工具。

## 实践示例 {#practical-example}

下面是一个带工具使用的完整会话示例：

```typescript
// Conversation history
;[
  // User query
  {
    id: "msg_1",
    role: "user",
    content: "What's the weather in New York?",
  },

  // Assistant response with tool call
  {
    id: "msg_2",
    role: "assistant",
    content: "Let me check the weather for you.",
    toolCalls: [
      {
        id: "call_1",
        type: "function",
        function: {
          name: "get_weather",
          arguments: '{"location": "New York", "unit": "celsius"}',
        },
      },
    ],
  },

  // Tool result
  {
    id: "result_1",
    role: "tool",
    content:
      '{"temperature": 22, "condition": "Partly Cloudy", "humidity": 65}',
    toolCallId: "call_1",
  },

  // Assistant's final response using tool results
  {
    id: "msg_3",
    role: "assistant",
    content:
      "The weather in New York is partly cloudy with a temperature of 22°C and 65% humidity.",
  },
]
```

## 结语 {#conclusion}

AG-UI 中的消息结构在保持厂商中立的同时，支持复杂的会话式 AI 体验。
通过标准化消息的表示、同步与流式传输方式，AG-UI 提供了一致的方式来
实现人机交互式通信，而无需关心底层 AI 服务。

该系统支持从简单文本交换到复杂工具驱动工作流的一切场景，
同时兼顾实时响应性与高效的数据传输。
