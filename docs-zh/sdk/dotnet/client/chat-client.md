---
title: "AGUIChatClient"
description: "用于消费 AG-UI 端点的 IChatClient 实现"
---
<em class="lead">用于消费 AG-UI 端点的 IChatClient 实现</em>

# AGUIChatClient {#aguichatclient}

`AGUIChatClient` 是面向 AG-UI 的 `IChatClient` 实现。它把
`ChatMessage` 值与 `ChatOptions` 转换为 `RunAgentInput`，将该输入发送到 AG-UI 端点，
并把返回的事件流转换为 `ChatResponseUpdate` 值。

```csharp
using AGUI.Client;
using Microsoft.Extensions.AI;
```

!!! note
    .NET 客户端并未定义与 `AbstractAgent` 等价的东西。集成点是
      `Microsoft.Extensions.AI.IChatClient`。

## 构造 {#construction}

从 `AGUIChatClientOptions` 创建客户端。最简单的形式是用 `HttpClient` 和 AG-UI 端点
URL 构建内置的 HTTP 传输：

```csharp
using AGUI.Client;
using Microsoft.Extensions.AI;

HttpClient httpClient = new();
IChatClient client = new AGUIChatClient(new(httpClient, "https://api.example.com/agent"));
```

`AGUIChatClient` 只有一个构造函数，接受 `AGUIChatClientOptions`：

```csharp
new AGUIChatClient(AGUIChatClientOptions options);
```

`AGUIChatClientOptions` 携带传输以及可选的序列化器设置：

```csharp
public sealed class AGUIChatClientOptions
{
    public AGUIChatClientOptions();
    public AGUIChatClientOptions(HttpClient httpClient, string endpoint); // builds the HTTP transport
    public required IAGUITransport Transport { get; init; }
    public JsonSerializerOptions? JsonSerializerOptions { get; init; }
}
```

当你需要为测试或替代的线上协议使用自定义传输时，请直接设置 `Transport`。参见
[传输](./transport.md)。
配置的 `JsonSerializerOptions` 也会在转换 MEAI 消息内容时使用，包括
`AIContent.AdditionalProperties` 中的自定义 CLR 值。

## 流式响应 {#streaming-responses}

`GetStreamingResponseAsync` 以 MEAI `ChatResponseUpdate` 对象的形式流式输出 AG-UI
结果：

```csharp
using AGUI.Client;
using Microsoft.Extensions.AI;

using HttpClient httpClient = new();
IChatClient client = new AGUIChatClient(new(httpClient, "https://api.example.com/agent"));

List<ChatMessage> messages =
[
    new(ChatRole.User, "Explain AG-UI in one paragraph"),
];

await foreach (ChatResponseUpdate update in client.GetStreamingResponseAsync(
    messages,
    options: null,
    cancellationToken: CancellationToken.None))
{
    if (!string.IsNullOrEmpty(update.Text))
    {
        Console.Write(update.Text);
    }
}
```

在内部，客户端会把 AG-UI 事件流转换回 `ChatResponseUpdate` 对象。文本事件变为文本增量，
工具调用事件变为 MEAI 工具调用内容，生命周期事件仍可通过 `RawRepresentation` 获取。

## 非流式响应 {#nonstreaming-responses}

`GetResponseAsync` 也已实现。它消费流式响应并返回最终的 `ChatResponse`：

```csharp
ChatResponse response = await client.GetResponseAsync(
    messages,
    cancellationToken: CancellationToken.None);

Console.WriteLine(response.Text);
```

## 无状态性与 ConversationId {#statelessness-and-conversationid}

`AGUIChatClient` 是无状态的。它在每一轮都发送完整的消息历史，并且从不在返回的更新上暴露
`ConversationId`。

这是有意为之。在 `Microsoft.Extensions.AI` 中，非 null 的 `ConversationId` 表示由服务
管理的会话。智能体包装器随后可能只在下一轮发送新增的消息增量。这在与会话无状态的 AG-UI
服务器通信时会截断历史。

请改用这些标识符：

- `ChatResponseUpdate.ResponseId` 是 AG-UI 运行 id。
- `update.RawRepresentation as RunStartedEvent` 暴露 `RUN_STARTED` 事件中的 AG-UI
  `ThreadId` 与 `RunId`。
- `update.AdditionalProperties["agui_thread_id"]` 在 `RUN_STARTED` 更新上也包含解析出的
  AG-UI 会话 id。

```csharp
using AGUI.Abstractions;
using Microsoft.Extensions.AI;

static (string? ThreadId, string? RunId) GetAGUIIds(
    IEnumerable<ChatResponseUpdate> updates)
{
    RunStartedEvent? started = updates
        .Select(update => update.RawRepresentation)
        .OfType<RunStartedEvent>()
        .FirstOrDefault();

    return (started?.ThreadId, started?.RunId);
}
```

!!! warning
    不要将 `ConversationId` 用作 AG-UI 会话状态。每一轮都传入完整的消息历史，并使用
      AG-UI 会话/运行 id 进行线上层面的关联。

## 会话连续性 {#thread-continuity}

要保持稳定的 AG-UI 会话，请在多轮之间复用同一个 `ChatOptions` 实例。客户端会把解析出的
会话 id 固定到该选项实例上，而不设置 `ConversationId`。

若要显式继续或分支，请通过 `ChatOptions.RawRepresentationFactory` 设置
`RunAgentInput.ThreadId` 与
`RunAgentInput.ParentRunId`。这是控制线上层面字段的 AG-UI 原生方式：

```csharp
using AGUI.Abstractions;
using Microsoft.Extensions.AI;

List<ChatResponseUpdate> firstTurn = [];
await foreach (ChatResponseUpdate update in client.GetStreamingResponseAsync(
    [new ChatMessage(ChatRole.User, "Hello, tell me about serialization")],
    cancellationToken: CancellationToken.None))
{
    firstTurn.Add(update);
    Console.Write(update.Text);
}

RunStartedEvent? runStarted = firstTurn
    .Select(update => update.RawRepresentation)
    .OfType<RunStartedEvent>()
    .FirstOrDefault();

ChatOptions followUpOptions = new()
{
    RawRepresentationFactory = _ => new RunAgentInput
    {
        ThreadId = runStarted?.ThreadId ?? string.Empty,
        ParentRunId = runStarted?.RunId,
    },
};

await foreach (ChatResponseUpdate update in client.GetStreamingResponseAsync(
    [new ChatMessage(ChatRole.User, "Tell me more about event compaction")],
    followUpOptions,
    CancellationToken.None))
{
    Console.Write(update.Text);
}
```

!!! tip
    当你希望下一个请求从先前的运行分支时，请使用 `ParentRunId`。当你只需要在同一会话上
      继续时，省略它。

## 中断与审批 {#interrupts-and-approvals}

当 AG-UI 服务器以中断结果结束运行时，客户端会将该暂停暴露为 MEAI 内容：

- 工具调用审批变为 `ToolApprovalRequestContent`。
- 其他中断变为 `InterruptRequestContent`。

调用方追加一条响应消息并发送下一个请求。客户端从最新消息中提取
`ToolApprovalResponseContent` 与 `InterruptResponseContent`，并将其作为
`RunAgentInput.Resume` 发送。

```csharp
using AGUI.Abstractions;
using Microsoft.Extensions.AI;

List<ChatMessage> messages =
[
    new(ChatRole.User, "Delete the generated files"),
];

ChatResponse firstResponse = await client.GetResponseAsync(
    messages,
    cancellationToken: CancellationToken.None);

ToolApprovalRequestContent? approval = firstResponse.Messages
    .SelectMany(message => message.Contents)
    .OfType<ToolApprovalRequestContent>()
    .FirstOrDefault();

if (approval?.ToolCall is FunctionCallContent toolCall)
{
    messages.AddRange(firstResponse.Messages);
    messages.Add(new ChatMessage(ChatRole.User,
    [
        new ToolApprovalResponseContent(approval.RequestId, approved: true, toolCall),
    ]));

    ChatResponse resumed = await client.GetResponseAsync(
        messages,
        cancellationToken: CancellationToken.None);

    Console.WriteLine(resumed.Text);
}
```

对于非工具类中断，请使用 `InterruptResponseContent` 响应：

```csharp
using System.Text.Json;
using AGUI.Abstractions;
using Microsoft.Extensions.AI;

static ChatMessage CreateInterruptResponse(InterruptRequestContent request)
{
    using JsonDocument payload = JsonDocument.Parse("""{"approved":true}""");

    return new ChatMessage(ChatRole.User,
    [
        new InterruptResponseContent(request.RequestId)
        {
            Payload = payload.RootElement.Clone(),
        },
    ]);
}
```

`InterruptResponseContent.Metadata` 可选地携带关于该响应的信封数据 — 证明决策未被篡改的
签名、路由键 — 与 `Payload` 相对，后者是智能体所请求的答案。客户端会把它复制到恢复条目
的 `metadata` 上，托管层则在 `InterruptResponseContent` 上把它交还给服务器流水线；参见
[元数据](../../../concepts/metadata.md#resume-entries)。

```csharp
new InterruptResponseContent(request.RequestId)
{
    Payload = payload.RootElement.Clone(),
    Metadata = JsonDocument.Parse(
        """{"definitionId":"review-plan","key":"afterModel-review"}""")
        .RootElement.Clone(),
}
```

## 相关参考 {#related-references}

- [传输](./transport.md)
- [事件](../abstractions/events.md)
- [核心协议类型](../abstractions/types.md)
