---
title: "类型"
description:
  "Agent User Interaction Protocol SDK 中使用的核心类型文档"
---
<em class="lead">Agent User Interaction Protocol SDK 中使用的核心类型文档</em>

# 核心类型 {#core-types}

Agent User Interaction Protocol SDK 建立在一组核心类型之上，
这些类型表示整个系统中使用的基础结构。本页记录这些类型及其属性。

## RunAgentInput {#runagentinput}

运行智能体的输入参数。在 HTTP API 中，它是 `POST` 请求的请求体。

`tools` 包含客户端为本次运行提供的工具。后端定义的工具应保留在后端智能体或
框架配置中，并且可以通过智能体能力单独公布。

```typescript
type RunAgentInput = {
  threadId: string
  runId: string
  parentRunId?: string
  state?: any // absent means "no state"; a bare null is read as absent
  messages: Message[]
  tools: Tool[]
  context: Context[]
  forwardedProps: any
  resume?: ResumeEntry[]
}
```

| 属性             | 类型                       | 说明                                                                                     |
| ---------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| `threadId`       | `string`                   | 会话线程的 ID                                                            |
| `runId`          | `string`                   | 当前运行的 ID                                                                    |
| `parentRunId`    | `string (optional)`        | 生成此运行的那次运行的 ID                                                      |
| `state`          | `any (optional)`           | 智能体的当前状态；缺失表示“无状态”，裸 `null` 也会被读作缺失 |
| `messages`       | `Message[]`                | 会话中的消息数组                                                    |
| `tools`          | `Tool[]`                   | 客户端提供的、本次运行可用的工具                                             |
| `context`        | `Context[]`                | 提供给智能体的上下文对象数组                                           |
| `forwardedProps` | `any`                      | 转发给智能体的附加属性                                             |
| `resume`         | `ResumeEntry[] (optional)` | 针对每个中断的响应，用于恢复以中断结果结束的运行           |

## ResumeEntry {#resumeentry}

`RunAgentInput.resume` 内部针对单个中断的响应，回应上一次运行中的
一个中断。完整的恢复契约见
[中断](../../../concepts/interrupts.md#resuming-a-run)。

```typescript
type ResumeEntry = {
  interruptId: string
  status: "resolved" | "cancelled"
  payload?: any
  metadata?: Record<string, any>
}
```

| 属性          | 类型                             | 说明                                                                                  |
| ------------- | -------------------------------- | ------------------------------------------------------------------------------------- |
| `interruptId` | `string`                         | 此条目所回应的中断的 ID                                              |
| `status`      | `"resolved" \| "cancelled"`      | 用户是响应了该中断还是放弃了它                                 |
| `payload`     | `any (optional)`                 | 响应本身，会依据该中断的 `responseSchema` 进行校验               |
| `metadata`    | `Record<string, any> (optional)` | 关于该响应的信封数据 — 签名、路由键 — 绝非答案本身 |

`metadata` 遵循协议中其他各处元数据的同一约定：按 key 开放，一个 key 下允许
任意 JSON 值（包括 `null`），对象本身可以缺失或是一个对象，但绝不出现 `null`，
且 `ag-ui` key 为保留键。resume 条目是一个请求字段，因此不会有任何内容合并进
它；见[元数据](../../../concepts/metadata.md#resume-entries)。

## 消息类型 {#message-types}

SDK 包含若干消息类型，表示系统中不同类型的消息。

!!! note
    每种消息类型都携带一个可选的 `metadata` 对象
      （`Record<string, any>`），`ToolCall` 也是如此。为简洁起见，下文
      各类型的表格都省略了它们。
      它按 key 开放 — 一个 key 下允许任意 JSON 值，包括 `null` —
      且对象本身可以缺失，但绝不是 `null`。`ag-ui` key
      保留给 AG-UI 自身使用。元数据会在消息由其事件
      构建的过程中累积；合并规则见[元数据](../../../concepts/metadata.md)。

### Role {#role}

表示消息发送者可能具有的角色。

```typescript
type Role =
  | "developer"
  | "system"
  | "assistant"
  | "user"
  | "tool"
  | "activity"
  | "reasoning"
```

### DeveloperMessage {#developermessage}

表示来自开发者的消息。

```typescript
type DeveloperMessage = {
  id: string
  role: "developer"
  content: string
  name?: string
}
```

| 属性      | 类型          | 说明                                             |
| --------- | ------------- | ------------------------------------------------ |
| `id`      | `string`      | 消息的唯一标识符                |
| `role`    | `"developer"` | 消息发送者的角色，固定为 "developer" |
| `content` | `string`      | 消息的文本内容（必填）           |
| `name`    | `string`      | 发送者的可选名称                      |

### SystemMessage {#systemmessage}

表示系统消息。

```typescript
type SystemMessage = {
  id: string
  role: "system"
  content: string
  name?: string
}
```

| 属性      | 类型       | 说明                                          |
| --------- | ---------- | --------------------------------------------- |
| `id`      | `string`   | 消息的唯一标识符             |
| `role`    | `"system"` | 消息发送者的角色，固定为 "system" |
| `content` | `string`   | 消息的文本内容（必填）        |
| `name`    | `string`   | 发送者的可选名称                   |

### AssistantMessage {#assistantmessage}

表示来自助手的消息。

```typescript
type AssistantMessage = {
  id: string
  role: "assistant"
  content?: string
  name?: string
  toolCalls?: ToolCall[]
}
```

| 属性        | 类型                    | 说明                                             |
| ----------- | ----------------------- | ------------------------------------------------ |
| `id`        | `string`                | 消息的唯一标识符                |
| `role`      | `"assistant"`           | 消息发送者的角色，固定为 "assistant" |
| `content`   | `string` (optional)     | 消息的文本内容                      |
| `name`      | `string` (optional)     | 发送者的名称                               |
| `toolCalls` | `ToolCall[]` (optional) | 此消息中发起的工具调用                  |

### UserMessage {#usermessage}

表示来自用户的消息。

```typescript
type UserMessage = {
  id: string
  role: "user"
  content: string | ContentPart[]
  name?: string
}
```

| 属性      | 类型                      | 说明                                                                  |
| --------- | ------------------------- | --------------------------------------------------------------------- |
| `id`      | `string`                  | 消息的唯一标识符                                     |
| `role`    | `"user"`                  | 消息发送者的角色，固定为 "user"                           |
| `content` | `string \| ContentPart[]` | 纯文本，或由多模态内容片段构成的有序数组 |
| `name`    | `string`                  | 发送者的可选名称                                           |

### ContentPart {#contentpart}

受支持的内容部件的联合。同一批部件既出现在 `UserMessage` 上，
也出现在 `ToolMessage` 上：工具结果是一个字符串，或是它们的列表。每个部件
都可以携带一个可选的 `id`；`metadata` 不受约束，文本搜索命中就在其中
保存它的来源和标题。

```typescript
type ContentPart = TextPart | ImagePart | AudioPart | VideoPart | DocumentPart
```

### PartSource {#partsource}

```typescript
type PartSource = DataSource | UrlSource | FileSource

type DataSource = {
  type: "data"
  value: string
  mimeType: string
}

type UrlSource = {
  type: "url"
  value: string
  mimeType?: string
}

type FileSource = {
  type: "file"
  value: string // the handle, exactly as the provider issued it
  provider?: string // who issued it, e.g. "openai", "anthropic", "google"
  mimeType?: string
}
```

`FileSource` 指向已存在于模型提供方处的字节 — 一个 OpenAI 或 Anthropic
文件 id、一个 Gemini 文件 URI。不会去获取任何内容，且 `value` 是不透明的：
智能体要么把它交给自己的提供方，要么丢弃该部件，而绝不把它当作 URL。

### TextPart {#textpart}

```typescript
type TextPart = {
  type: "text"
  id?: string
  text: string
  metadata?: unknown
}
```

### ImagePart {#imagepart}

```typescript
type ImagePart = {
  type: "image"
  id?: string
  source: PartSource
  metadata?: unknown
}
```

### AudioPart {#audiopart}

```typescript
type AudioPart = {
  type: "audio"
  id?: string
  source: PartSource
  metadata?: unknown
}
```

### VideoPart {#videopart}

```typescript
type VideoPart = {
  type: "video"
  id?: string
  source: PartSource
  metadata?: unknown
}
```

### DocumentPart {#documentpart}

```typescript
type DocumentPart = {
  type: "document"
  id?: string
  source: PartSource
  metadata?: unknown
}
```

### ToolMessage {#toolmessage}

表示来自工具的消息。

```typescript
type ToolMessage = {
  id: string
  content: string | ContentPart[]
  role: "tool"
  toolCallId: string
  error?: string
  encryptedValue?: string
}
```

| 属性             | 类型                | 说明                                            |
| ---------------- | ------------------- | ----------------------------------------------- |
| `id`             | `string`            | 消息的唯一标识符               |
| `content`        | `string`            | 消息的文本内容                     |
| `role`           | `"tool"`            | 消息发送者的角色，固定为 "tool"     |
| `toolCallId`     | `string`            | 此消息所回应的工具调用的 ID    |
| `error`          | `string` (optional) | 工具调用失败时的错误消息           |
| `encryptedValue` | `string` (optional) | 通过签名附加的可选加密值 |

### ActivityMessage {#activitymessage}

表示在聊天消息之间发出的结构化活动进度。

```typescript
type ActivityMessage = {
  id: string
  role: "activity"
  activityType: string
  content: Record<string, any>
}
```

| 属性           | 类型                  | 说明                                                    |
| -------------- | --------------------- | ------------------------------------------------------- |
| `id`           | `string`              | 活动消息的唯一标识符              |
| `role`         | `"activity"`          | 固定判别字段，将消息标识为活动 |
| `activityType` | `string`              | 用于渲染器选择的活动判别字段      |
| `content`      | `Record<string, any>` | 表示活动状态的结构化载荷      |

### ReasoningMessage {#reasoningmessage}

表示来自智能体内部思考过程的推理/思维消息。

```typescript
type ReasoningMessage = {
  id: string
  role: "reasoning"
  content: string
  encryptedValue?: string
}
```

| 属性             | 类型                | 说明                                               |
| ---------------- | ------------------- | -------------------------------------------------- |
| `id`             | `string`            | 推理消息的唯一标识符        |
| `role`           | `"reasoning"`       | 固定判别字段，标识推理角色 |
| `content`        | `string`            | 推理/思维内容                     |
| `encryptedValue` | `string` (optional) | 通过签名附加的可选加密值    |

### Message {#message}

表示系统中任意类型消息的联合类型。

```typescript
type Message =
  | DeveloperMessage
  | SystemMessage
  | AssistantMessage
  | UserMessage
  | ToolMessage
  | ActivityMessage
  | ReasoningMessage
```

### ToolCall {#toolcall}

表示智能体发起的工具调用。

```typescript
type ToolCall = {
  id: string
  type: "function"
  function: FunctionCall
  encryptedValue?: string
}
```

| 属性             | 类型                | 说明                                            |
| ---------------- | ------------------- | ----------------------------------------------- |
| `id`             | `string`            | 工具调用的唯一标识符             |
| `type`           | `"function"`        | 工具调用的类型，始终为 "function"        |
| `function`       | `FunctionCall`      | 关于被调用函数的详细信息         |
| `encryptedValue` | `string` (optional) | 通过签名附加的可选加密值 |

#### FunctionCall {#functioncall}

表示工具调用中的函数名与参数。

```typescript
type FunctionCall = {
  name: string
  arguments: string
}
```

| 属性        | 类型     | 说明                                             |
| ----------- | -------- | ------------------------------------------------ |
| `name`      | `string` | 要调用的函数名                     |
| `arguments` | `string` | 传给函数的 JSON 编码参数字符串 |

## Context {#context}

表示提供给智能体的一条上下文信息。

```typescript
type Context = {
  description: string
  value: string
}
```

| 属性          | 类型     | 说明                                        |
| ------------- | -------- | ------------------------------------------- |
| `description` | `string` | 关于此上下文表示什么的描述 |
| `value`       | `string` | 实际的上下文值                    |

## Tool {#tool}

定义一个可由智能体调用的工具。

```typescript
type Tool = {
  name: string
  description: string
  parameters: any // JSON Schema
}
```

| 属性          | 类型     | 说明                                             |
| ------------- | -------- | ------------------------------------------------ |
| `name`        | `string` | 工具名称                                 |
| `description` | `string` | 工具功能的描述                |
| `parameters`  | `any`    | 定义工具参数的 JSON Schema |

## State {#state}

表示智能体在执行期间的状态。

```typescript
type State = any
```

状态类型是灵活的，可以保存智能体实现所需的任何数据结构。

## AgentCapabilities {#agentcapabilities}

由 `getCapabilities()` 返回的、带类型的能力声明。所有字段都是
可选的 — 智能体只声明它们支持的内容。

```typescript
interface AgentCapabilities {
  identity?: IdentityCapabilities
  transport?: TransportCapabilities
  tools?: ToolsCapabilities
  output?: OutputCapabilities
  state?: StateCapabilities
  multiAgent?: MultiAgentCapabilities
  reasoning?: ReasoningCapabilities
  multimodal?: MultimodalCapabilities
  execution?: ExecutionCapabilities
  humanInTheLoop?: HumanInTheLoopCapabilities
  custom?: Record<string, unknown>
}
```

| 属性             | 类型                         | 说明                                         |
| ---------------- | ---------------------------- | -------------------------------------------- |
| `identity`       | `IdentityCapabilities`       | 智能体身份与元数据                  |
| `transport`      | `TransportCapabilities`      | 受支持的传输机制               |
| `tools`          | `ToolsCapabilities`          | 智能体提供的工具与工具调用配置 |
| `output`         | `OutputCapabilities`         | 输出格式支持                        |
| `state`          | `StateCapabilities`          | 状态与记忆管理                  |
| `multiAgent`     | `MultiAgentCapabilities`     | 多智能体协调                     |
| `reasoning`      | `ReasoningCapabilities`      | 推理与思考支持               |
| `multimodal`     | `MultimodalCapabilities`     | 多模态输入/输出支持              |
| `execution`      | `ExecutionCapabilities`      | 执行控制与限制                 |
| `humanInTheLoop` | `HumanInTheLoopCapabilities` | Human-in-the-loop 支持                    |
| `custom`         | `Record<string, unknown>`    | 集成特定的能力            |

各类别的完整类型定义与使用模式见[能力](../../../concepts/capabilities.md)。
