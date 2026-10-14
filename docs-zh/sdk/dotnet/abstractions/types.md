---
title: "类型"
description: "AGUI.Abstractions 中协议类型的文档"
---
<em class="lead">AGUI.Abstractions 中协议类型的文档</em>

# AGUI.Abstractions 类型 {#aguiabstractions-types}

`AGUI.Abstractions` 包含 AG-UI .NET 客户端与服务器共享的协议模型。
JSON 线上名称为 camelCase，并与 AG-UI 协议一致。

## RunAgentInput {#runagentinput}

`RunAgentInput` 是运行智能体的请求载荷。在 HTTP API 中，它是 `POST`
请求的请求体。

```csharp
using System.Text.Json;
using AGUI.Abstractions;

var input = new RunAgentInput
{
    ThreadId = "thread-1",
    RunId = "run-1",
    Messages =
    [
        new AGUIUserMessage
        {
            Id = "msg-1",
            Content = "Hello!"
        }
    ],
    Tools =
    [
        new AGUITool
        {
            Name = "get_weather",
            Description = "Get the weather for a city",
            Parameters = JsonDocument.Parse("""
                {
                  "type": "object",
                  "properties": {
                    "city": { "type": "string" }
                  },
                  "required": ["city"]
                }
                """).RootElement.Clone()
        }
    ]
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `ThreadId` | `threadId` | `string` | 会话线程的 ID |
| `RunId` | `runId` | `string` | 当前运行的 ID |
| `ParentRunId` | `parentRunId` | `string?` | 可选的血统指针，用于分支或时间旅行 |
| `Messages` | `messages` | `IList<AGUIMessage>` | 会话消息 |
| `Tools` | `tools` | `IList<AGUITool>?` | 智能体可用的工具 |
| `State` | `state` | `JsonElement?` | 当前前端或智能体状态 |
| `Resume` | `resume` | `IList<AGUIResume>?` | 用于被中断运行的恢复载荷 |
| `Context` | `context` | `IList<AGUIContext>?` | 提供给智能体的上下文对象 |
| `ForwardedProperties` | `forwardedProps` | `JsonElement` | 客户端转发的附加属性 |

## AGUIResume {#aguiresume}

`RunAgentInput.Resume` 内部针对单个中断的响应，回应上一次运行中的
一个中断。完整的恢复契约见
[中断](../../../concepts/interrupts.md#resuming-a-run)。

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `InterruptId` | `interruptId` | `string` | 此条目所回应的中断的 ID |
| `Status` | `status` | `string` | 若用户已响应则为 `ResumeStatus.Resolved`，若用户放弃则为 `ResumeStatus.Cancelled` |
| `Payload` | `payload` | `JsonElement?` | 响应本身，会依据该中断的 `responseSchema` 进行校验 |
| `Metadata` | `metadata` | `JsonElement?` | 关于该响应的信封数据 — 签名、路由键 — 绝非答案本身 |

`Metadata` 遵循协议中其他各处元数据的同一约定：按 key 开放，一个 key 下允许
任意 JSON 值（包括 `null`），对象本身可以缺失或是一个对象，但在线上绝不出现
`null`，且 `ag-ui` key（`AGUIMetadata.ReservedKey`）为保留键。resume 条目是
一个请求字段，因此不会有任何内容合并进它；见
[元数据](../../../concepts/metadata.md#resume-entries)。对于非工具中断，
托管层会把它带到 `InterruptResponseContent.Metadata` 上，而
`AGUIChatClient` 会把它从 `InterruptResponseContent` 复制到它发送的条目上。
工具审批条目会经由 MEAI 自身的审批内容类型转换，那些类型没有元数据表面 —
若在那里需要它，请通过 `RunAgentInput.Resume` 从原始条目读取。

## 消息类型 {#message-types}

消息构成一个以 `AGUIMessage` 为根的封闭层级。基类型只携带每种角色共享的
字段：`Id`、`Role` 和 `Metadata`。诸如 `content`、`name`、`encryptedValue`、
`toolCalls` 和 `toolCallId` 这类角色特有的属性，声明在密封的角色类上。

!!! note
    `Metadata`（`JsonElement?`，JSON 字段 `metadata`）由每种消息角色和
      `AGUIToolCall` 携带，为简洁起见在下文各表格中省略。
      它按 key 开放 — 一个 key 下允许任意 JSON 值，包括 `null` —
      且对象本身可以缺失，但绝不是 `null`。
      `AGUIMetadata.ReservedKey`（`"ag-ui"`）保留给 AG-UI 自身使用。
      元数据会在消息由其事件构建的过程中累积，工具调用事件则
      累积到工具调用本身之上；合并规则见
      [元数据](../../../concepts/metadata.md)。

```csharp
public abstract class AGUIMessage
{
    public string? Id { get; set; } // "id"
    public abstract string Role { get; } // "role"
    public JsonElement? Metadata { get; set; } // "metadata"
}
```

### 角色 {#roles}

`Role` 属性返回 `AGUIRoles` 中的一个小写常量：

| 常量 | JSON 值 |
| -------- | ---------- |
| `AGUIRoles.Developer` | `developer` |
| `AGUIRoles.System` | `system` |
| `AGUIRoles.Assistant` | `assistant` |
| `AGUIRoles.User` | `user` |
| `AGUIRoles.Tool` | `tool` |
| `AGUIRoles.Activity` | `activity` |
| `AGUIRoles.Reasoning` | `reasoning` |

### AGUIDeveloperMessage {#aguidevelopermessage}

```csharp
var message = new AGUIDeveloperMessage
{
    Id = "dev-1",
    Content = "Prefer concise answers.",
    Name = "policy"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"developer"` | 固定的角色判别字段 |
| `Content` | `content` | `string` | 开发者指令内容 |
| `Name` | `name` | `string?` | 可选的发送者名称 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |

### AGUISystemMessage {#aguisystemmessage}

```csharp
var message = new AGUISystemMessage
{
    Id = "sys-1",
    Content = "You are a helpful assistant.",
    Name = "system"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"system"` | 固定的角色判别字段 |
| `Content` | `content` | `string` | 系统指令内容 |
| `Name` | `name` | `string?` | 可选的发送者名称 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |

### AGUIAssistantMessage {#aguiassistantmessage}

```csharp
var message = new AGUIAssistantMessage
{
    Id = "asst-1",
    Content = "I can help with that.",
    ToolCalls =
    [
        new AGUIToolCall
        {
            Id = "call-1",
            Function = new AGUIToolCallFunction
            {
                Name = "get_weather",
                Arguments = """{"city":"Seattle"}"""
            }
        }
    ]
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"assistant"` | 固定的角色判别字段 |
| `Content` | `content` | `string?` | 可选的助手文本 |
| `Name` | `name` | `string?` | 可选的助手名称 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |
| `ToolCalls` | `toolCalls` | `IList<AGUIToolCall>?` | 该消息中发起的工具调用 |

### AGUIUserMessage {#aguiusermessage}

`AGUIUserMessage.Content` 是一个 `AGUIContent` 值。它建模 AG-UI
线上联合类型 `string | InputContent[]`。

```csharp
var textOnly = new AGUIUserMessage
{
    Id = "user-1",
    Content = "Summarize this image."
};

AGUIInputContent textPart = new AGUITextInputContent
{
    Text = "What is shown here?"
};

AGUIInputContent imagePart = new AGUIImageInputContent
{
    Source = new AGUIInputContentUrlSource
    {
        Value = "https://example.com/screen.png",
        MimeType = "image/png"
    }
};

var multimodal = new AGUIUserMessage
{
    Id = "user-2",
    Content = [textPart, imagePart]
};
```

`AGUIContent` 支持从 `string`、
`List<AGUIInputContent>` 和 `AGUIInputContent[]` 的隐式转换。它还有一个集合
构建器，因此 C# 集合表达式可用。在读取时，它实现
`IReadOnlyList<AGUIInputContent>`；纯字符串会被暴露为一个
`AGUITextInputContent` 部件。

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"user"` | 固定的角色判别字段 |
| `Content` | `content` | `AGUIContent` | 纯文本或有顺序的多模态部件 |
| `Name` | `name` | `string?` | 可选的用户名称 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |

`AGUIInputContent` 层级见[多模态输入](./multimodal-inputs.md)。

### AGUIToolMessage {#aguitoolmessage}

```csharp
var message = new AGUIToolMessage
{
    Id = "tool-msg-1",
    ToolCallId = "call-1",
    Content = """{"temperature":72}"""
};

// A result may also carry content parts — a document the tool returned, say.
var attachment = new AGUIToolMessage
{
    Id = "tool-msg-2",
    ToolCallId = "call-2",
    Content =
    [
        new AGUITextInputContent { Text = "Invoice attached." },
        new AGUIDocumentInputContent
        {
            Source = new AGUIInputContentUrlSource { Value = "https://example.com/INV-2291.pdf", MimeType = "application/pdf" },
        },
    ],
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"tool"` | 固定的角色判别字段 |
| `Content` | `content` | `AGUIContent` | 工具结果：纯文本或有顺序的内容部件，与用户消息上相同 |
| `ToolCallId` | `toolCallId` | `string` | 此消息所应答的工具调用的 ID |
| `Error` | `error` | `string?` | 可选的错误消息 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |

### AGUIActivityMessage {#aguiactivitymessage}

```csharp
var message = new AGUIActivityMessage
{
    Id = "activity-1",
    ActivityType = "PLAN",
    Content = JsonDocument.Parse("""{"status":"running"}""").RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"activity"` | 固定的角色判别字段 |
| `ActivityType` | `activityType` | `string` | 用于渲染器选择的活动判别字段 |
| `Content` | `content` | `JsonElement` | 结构化活动载荷 |

### AGUIReasoningMessage {#aguireasoningmessage}

```csharp
var message = new AGUIReasoningMessage
{
    Id = "reasoning-1",
    Content = "Thinking through the problem..."
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string?` | 消息 ID |
| `Role` | `role` | `"reasoning"` | 固定的角色判别字段 |
| `Content` | `content` | `string` | 推理文本 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |

### AGUIToolCall {#aguitoolcall}

```csharp
var call = new AGUIToolCall
{
    Id = "call-1",
    Type = "function",
    Function = new AGUIToolCallFunction
    {
        Name = "get_weather",
        Arguments = """{"city":"Seattle"}"""
    }
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Id` | `id` | `string` | 工具调用 ID |
| `Type` | `type` | `string` | 工具调用类型；默认为 `"function"` |
| `Function` | `function` | `AGUIToolCallFunction` | 函数名与 JSON 编码的参数 |
| `EncryptedValue` | `encryptedValue` | `string?` | 可选的不透明加密值 |

`AGUIToolCallFunction` 具有 `Name`（`name`）和 `Arguments`（`arguments`）。

## Context {#context}

`AGUIContext` 表示提供给智能体的一条上下文信息。

```csharp
var context = new AGUIContext
{
    Description = "Current customer tier",
    Value = "enterprise"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Description` | `description` | `string` | 关于该上下文表示什么的描述 |
| `Value` | `value` | `string` | 上下文值 |

## Tool {#tool}

`AGUITool` 定义一个智能体可以调用的工具。

```csharp
var tool = new AGUITool
{
    Name = "get_weather",
    Description = "Get the weather for a city",
    Parameters = JsonDocument.Parse("""
        {
          "type": "object",
          "properties": {
            "city": { "type": "string" }
          },
          "required": ["city"]
        }
        """).RootElement.Clone(),
    Metadata = JsonDocument.Parse("""{"ui":"compact"}""").RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Name` | `name` | `string` | 工具名称 |
| `Description` | `description` | `string?` | 可选的工具描述 |
| `Parameters` | `parameters` | `JsonElement` | 工具参数的 JSON Schema |
| `Metadata` | `metadata` | `JsonElement?` | 可选的任意工具元数据 |

## State {#state}

状态在 `RunAgentInput.State` 上表示为 `JsonElement?`，在
`StateSnapshotEvent` 与 `StateDeltaEvent` 中表示为 `JsonElement` 载荷。

```csharp
input.State = JsonDocument.Parse("""{"draft":"hello"}""").RootElement.Clone();
```

状态的 schema 由智能体定义。协议只负责承载它。

## AgentCapabilities {#agentcapabilities}

`AgentCapabilities` 是一种结构化声明，智能体可以公布它，以便客户端
发现它支持什么。所有字段都是可选的。

```csharp
var capabilities = new AgentCapabilities
{
    Identity = new IdentityCapabilities
    {
        Name = "Support Agent",
        Version = "1.0.0"
    },
    Transport = new TransportCapabilities
    {
        Streaming = true,
        Resumable = true
    },
    Tools = new ToolsCapabilities
    {
        Supported = true,
        ClientProvided = true
    },
    Multimodal = new MultimodalCapabilities
    {
        Input = new MultimodalInputCapabilities
        {
            Image = true,
            Audio = true,
            Pdf = true
        }
    }
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Identity` | `identity` | `IdentityCapabilities?` | 智能体身份与元数据 |
| `Transport` | `transport` | `TransportCapabilities?` | 流式传输、websocket、二进制、推送与可恢复性支持 |
| `Tools` | `tools` | `ToolsCapabilities?` | 工具支持与工具调用配置 |
| `Output` | `output` | `OutputCapabilities?` | 结构化输出与受支持的 MIME 类型 |
| `State` | `state` | `StateCapabilities?` | 快照、增量、记忆与持久化支持 |
| `MultiAgent` | `multiAgent` | `MultiAgentCapabilities?` | 委托、交接与子智能体信息 |
| `Reasoning` | `reasoning` | `ReasoningCapabilities?` | 推理、流式传输与加密推理支持 |
| `Multimodal` | `multimodal` | `MultimodalCapabilities?` | 多模态输入与输出支持 |
| `Execution` | `execution` | `ExecutionCapabilities?` | 代码执行与迭代/时间限制 |
| `HumanInTheLoop` | `humanInTheLoop` | `HumanInTheLoopCapabilities?` | 审批、干预、反馈、中断，以及带编辑的批准 |
| `Custom` | `custom` | `JsonElement?` | 集成特定的能力，按 key 开放；用 `JsonSerializer.SerializeToElement(...)` 构建它 |

协议层概念与使用模式见[能力](../../../concepts/capabilities.md)。

## 序列化 {#serialization}

所有协议类型都注册在 `AGUIJsonSerializerContext` 中，这是一个
源生成的 `JsonSerializerContext`。在 AOT 敏感代码中序列化协议
类型时使用它。

```csharp
var json = JsonSerializer.Serialize(
    input,
    AGUIJsonSerializerContext.Default.RunAgentInput);
```
