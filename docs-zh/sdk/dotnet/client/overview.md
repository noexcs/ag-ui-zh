---
title: "概览"
description: "客户端包概览"
---
<em class="lead">客户端包概览</em>

# AGUI.Client {#aguiclient}

AG-UI .NET 客户端 SDK 把 AG-UI 端点适配到标准的
`Microsoft.Extensions.AI.IChatClient` 抽象。`AGUI.Client` 不引入新的智能体基类，而是
让 .NET 应用以消费任何其他聊天模型的方式消费 AG-UI 服务器。

```bash
dotnet add package AGUI.Client
```

!!! note
    如果你已经在使用 `Microsoft.Extensions.AI`，那么 AG-UI 服务器只是另一个
      `IChatClient`。

## AGUIChatClient {#aguichatclient}

`AGUIChatClient` 是该包中的主要类型。它包装 AG-UI HTTP+SSE 端点，并从 `IChatClient`
暴露 `GetStreamingResponseAsync` 与 `GetResponseAsync`。

- [构造](./chat-client.md#construction) - 从 `HttpClient` 和端点创建客户端，或从自定义传输创建
- [流式输出](./chat-client.md#streaming-responses) - 将 AG-UI 事件作为 `ChatResponseUpdate` 值消费
- [无状态行为](./chat-client.md#statelessness-and-conversationid) - 每一轮都发送完整的消息历史
- [会话连续性](./chat-client.md#thread-continuity) - 保持稳定的会话，或从先前的运行分支
- [中断与审批](./chat-client.md#interrupts-and-approvals) - 使用标准 MEAI 内容类型处理服务器暂停

- [AGUIChatClient 参考](./chat-client.md) — 通过 Microsoft.Extensions.AI IChatClient API 消费 AG-UI 端点

## 传输 {#transport}

客户端包包含一个小的传输抽象，用于发送 `RunAgentInput` 请求并接收 AG-UI 事件流。默认路径
使用 HTTP POST 与 Server-Sent Events；自定义传输适用于测试或非 HTTP 环境。

- [IAGUITransport](./transport.md#iaguitransport) - `AGUIChatClient` 使用的传输接口
- [HTTP 传输](./transport.md#http-transport) - 内置的 HTTP+SSE 行为
- [自定义传输](./transport.md#custom-transports) - 接入内存传输或替代的线上协议

- [传输参考](./transport.md) — 了解 AG-UI 客户端传输契约与 HTTP 事件流

## 设计上无状态 {#stateless-by-design}

从 .NET 客户端的视角看，AG-UI 端点是无状态的。每个请求都发送完整的消息历史，返回的
`ChatResponseUpdate` 对象不暴露 `ConversationId`。更新通过 `ResponseId` 关联，它映射到
AG-UI 运行 id。AG-UI 会话 id 可从 `RUN_STARTED` 事件以及
`AdditionalProperties["agui_thread_id"]` 获取。

关于线上传输的协议类型，参见 [.NET 事件参考](../abstractions/events.md)。

## 客户端验证 {#client-verification}

客户端测试保护 `Microsoft.Extensions.AI` 与 AG-UI 之间的转换。它们验证 `ChatMessage`
历史变为 AG-UI 消息、`ChatOptions.Tools` 变为 AG-UI 工具、调用方提供的 AG-UI 上下文、
转发属性与恢复负载都得到保留，以及 `RUN_ERROR` 事件变为 MEAI `ErrorContent` 更新。

它们还保护无状态会话契约：会话与运行标识符通过 AG-UI 字段保留，返回的更新清空
`ConversationId`，服务器端的工具调用被标记为信息性，使 .NET 客户端不会在本地执行它们。

```bash
cd sdks/dotnet
dotnet test tests/AGUI.Client.UnitTests/
dotnet test tests/AGUI.CrossLanguage.IntegrationTests/
```
