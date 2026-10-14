---
title: "传输"
description: "AG-UI 客户端传输抽象与 HTTP 事件流"
---
<em class="lead">AG-UI 客户端传输抽象与 HTTP 事件流</em>

# 传输 {#transport}

`AGUI.Client` 通过 `IAGUITransport` 把聊天客户端与线上协议分离。`AGUIChatClient`
构建一个 `RunAgentInput`，将其传给传输层，并消费由此产生的 AG-UI `BaseEvent` 流。

```csharp
using AGUI.Abstractions;
using AGUI.Client;
```

## IAGUITransport {#iaguitransport}

`IAGUITransport` 只有一个方法：

```csharp
public interface IAGUITransport
{
    IAsyncEnumerable<BaseEvent> SendAsync(
        RunAgentInput input,
        CancellationToken cancellationToken);
}
```

该输入包含 AG-UI 会话 id、运行 id、消息历史、工具、状态、上下文、转发属性，以及被中断运行
的恢复条目。输出是[事件参考](../abstractions/events.md)中所述的有序 AG-UI 事件流。

## HTTP 传输 {#http-transport}

`AGUIChatClientOptions(HttpClient, endpoint)` 构造函数在内部创建内置的 HTTP 传输：

```csharp
using AGUI.Client;
using Microsoft.Extensions.AI;

using HttpClient httpClient = new();
IChatClient client = new AGUIChatClient(new(httpClient, "https://api.example.com/agent"));
```

内置传输将请求作为 HTTP `POST` 发送，其请求体是序列化后的 `RunAgentInput`。响应按
Server-Sent Events 读取，每个 SSE 条目被反序列化为一个 `BaseEvent`。

!!! note
    `AGUIHttpTransport` 是 `AGUIChatClientOptions(HttpClient, endpoint)` 构造函数使用的
      内置 HTTP+SSE 实现。大多数应用无需直接实例化传输。

## 自定义传输 {#custom-transports}

当你希望在没有服务器的情况下测试或使用不同的传输时，实现 `IAGUITransport`。然后把该实现
传给 `AGUIChatClient`。

```csharp
using System.Runtime.CompilerServices;
using AGUI.Abstractions;
using AGUI.Client;
using Microsoft.Extensions.AI;

public sealed class InMemoryAGUITransport : IAGUITransport
{
    public List<RunAgentInput> Requests { get; } = [];

    public async IAsyncEnumerable<BaseEvent> SendAsync(
        RunAgentInput input,
        [EnumeratorCancellation] CancellationToken cancellationToken)
    {
        Requests.Add(input);
        await Task.Yield();

        string threadId = string.IsNullOrEmpty(input.ThreadId) ? "thread_1" : input.ThreadId;
        string runId = string.IsNullOrEmpty(input.RunId) ? "run_1" : input.RunId;

        yield return new RunStartedEvent { ThreadId = threadId, RunId = runId, ProtocolVersion = AGUIProtocol.Version };
        yield return new TextMessageStartEvent { MessageId = "msg_1", Role = AGUIRoles.Assistant };
        yield return new TextMessageContentEvent { MessageId = "msg_1", Delta = "Hello from AG-UI" };
        yield return new TextMessageEndEvent { MessageId = "msg_1" };
        yield return new RunFinishedEvent { ThreadId = threadId, RunId = runId };
    }
}

IAGUITransport transport = new InMemoryAGUITransport();
IChatClient client = new AGUIChatClient(new() { Transport = transport });
```

## 事件转换 {#event-conversion}

传输层返回 AG-UI 协议事件。`AGUIChatClient` 随后把它们转换为 `ChatResponseUpdate`
值：

- `RUN_STARTED` 确立 AG-UI 会话 id 与运行 id。
- 文本消息事件变为流式文本更新。
- 工具调用事件变为 MEAI 函数调用内容。
- 中断结果变为 `ToolApprovalRequestContent` 或 `InterruptRequestContent`。
- `RUN_ERROR` 变为 `ErrorContent` 更新。其 `message` 映射到
  `ErrorContent.Message`，其可选的 `code` 映射到
  `ErrorContent.ErrorCode`。当事件携带部分 `usage` 时，客户端还会发出 `UsageContent`
  更新，使 `ChatResponse.Usage` 包含失败前已消耗的 token。

每个更新上的 `ResponseId` 对应 AG-UI 运行 id。客户端在产出更新前会清空
`ConversationId`，以便调用方继续向无状态的 AG-UI 服务器发送完整的消息历史。

## 取消 {#cancellation}

`SendAsync` 接收调用方的 `CancellationToken`。自定义传输应在发送请求期间和产出事件期间
观察它：

```csharp
public async IAsyncEnumerable<BaseEvent> SendAsync(
    RunAgentInput input,
    [EnumeratorCancellation] CancellationToken cancellationToken)
{
    cancellationToken.ThrowIfCancellationRequested();

    await Task.Delay(TimeSpan.FromMilliseconds(10), cancellationToken);
    yield return new RunStartedEvent
    {
        ThreadId = input.ThreadId,
        RunId = input.RunId,
        ProtocolVersion = AGUIProtocol.Version,
    };

    cancellationToken.ThrowIfCancellationRequested();
    yield return new RunFinishedEvent { ThreadId = input.ThreadId, RunId = input.RunId };
}
```

## 相关参考 {#related-references}

- [AGUIChatClient](./chat-client.md)
- [事件](../abstractions/events.md)
- [核心协议类型](../abstractions/types.md)
