---
title: "端点"
description: "将 IChatClient 托管为 AG-UI 端点"
---
<em class="lead">将 IChatClient 托管为 AG-UI 端点</em>

# 端点 {#endpoints}

AG-UI 端点就是普通的 ASP.NET Core POST 端点。它接收 `RunAgentInput`，调用
`IChatClient`，把流式响应转换为 AG-UI 事件，并返回 Server-Sent Events。

## 注册 AG-UI 服务 {#register-agui-services}

在启动期间调用 `AddAGUI()`。它使用 AG-UI 源生成序列化器上下文配置 ASP.NET Core JSON
选项，并注册 `IChatClient` 流水线使用的中断内容类型。

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddAGUI();
// Register your Microsoft.Extensions.AI IChatClient here.

var app = builder.Build();

app.MapAGUI("/");

app.Run();
```

## 端点模式 {#endpoint-pattern}

每个 AG-UI 端点都遵循同样的五个步骤。

1. **接收 RunAgentInput**

   映射一个接收 `[FromBody] RunAgentInput` 的 POST 端点。

2. **创建 ChatRequestContext**

   调用 `input.ToChatRequestContext(jsonSerializerOptions, streamOptions?)`。返回的上下文暴露 `ctx.Messages` 与 `ctx.ChatOptions`。

3. **调用 IChatClient**

   把 `ctx.Messages` 与 `ctx.ChatOptions` 传给 `chatClient.GetStreamingResponseAsync(...)`。

4. **转换为 AG-UI 事件**

   让 `ChatResponseUpdate` 流经过 `.AsAGUIEventStreamAsync(ctx, cancellationToken)`。

5. **返回 Server-Sent Events**

   返回 `TypedResults.ServerSentEvents(WrapAsSseItems(events, ct))`。

## 最小端点 {#minimal-endpoint}

这是 .NET 示例使用的规范端点形态。

```csharp
using System.Net.ServerSentEvents;
using System.Runtime.CompilerServices;
using AGUI.Abstractions;
using AGUI.Server;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Options;

using JsonOptions = Microsoft.AspNetCore.Http.Json.JsonOptions;

namespace MyAgent.Server;

internal static class AGUIEndpoint
{
    internal static IEndpointConventionBuilder MapAGUI(
        this IEndpointRouteBuilder endpoints,
        string pattern)
    {
        return endpoints.MapPost(pattern, (
            [FromBody] RunAgentInput input,
            [FromServices] IChatClient chatClient,
            [FromServices] IOptions<JsonOptions> jsonOptions,
            CancellationToken cancellationToken) =>
        {
            var jsonSerializerOptions = jsonOptions.Value.SerializerOptions;

            var ctx = input.ToChatRequestContext(jsonSerializerOptions);

            var updates = chatClient.GetStreamingResponseAsync(
                ctx.Messages,
                ctx.ChatOptions,
                cancellationToken);

            var events = updates.AsAGUIEventStreamAsync(ctx, cancellationToken);

            return TypedResults.ServerSentEvents(
                WrapAsSseItems(events, cancellationToken));
        });
    }

    private static async IAsyncEnumerable<SseItem<BaseEvent>> WrapAsSseItems(
        IAsyncEnumerable<BaseEvent> events,
        [EnumeratorCancellation] CancellationToken cancellationToken)
    {
        await foreach (var evt in events
            .WithCancellation(cancellationToken)
            .ConfigureAwait(false))
        {
            yield return new SseItem<BaseEvent>(evt);
        }
    }
}
```

## 关键 API {#key-apis}

### ToChatRequestContext {#tochatrequestcontext}

`ToChatRequestContext` 把 AG-UI 请求适配为 `Microsoft.Extensions.AI` 的请求形态。

```csharp
var ctx = input.ToChatRequestContext(jsonSerializerOptions);
```

`ChatRequestContext` 包含：

- `ctx.Input` - 原始的 `RunAgentInput`
- `ctx.Messages` - 转换后的 `List<ChatMessage>`
- `ctx.ChatOptions` - 已配置的 `ChatOptions`

原始输入也可在下游聊天客户端和工具处通过
`ctx.ChatOptions.AdditionalProperties[AGUIConstants.RunAgentInputKey]` 获取。

!!! tip
    客户端工具与审批流的路由会自动进行。来自 `RunAgentInput.Tools` 的客户端声明工具会被
      安装到 `ctx.ChatOptions.Tools` 上，并通过审批流水线路由。

### AsAGUIEventStreamAsync {#asaguieventstreamasync}

`AsAGUIEventStreamAsync` 把流式的 `ChatResponseUpdate` 值转换为 AG-UI `BaseEvent`
值。

```csharp
var events = updates.AsAGUIEventStreamAsync(ctx, cancellationToken);
```

它发出运行生命周期事件，把文本内容映射为 `TEXT_MESSAGE_*` 事件，把
`FunctionCallContent` 与 `FunctionResultContent` 映射为工具事件，把
`TextReasoningContent` 映射为推理事件，并透传存储在
`ChatResponseUpdate.RawRepresentation` 中的任何 `BaseEvent`。

### WrapAsSseItems {#wrapassseitems}

ASP.NET Core 的 `TypedResults.ServerSentEvents` 写出 `SseItem<T>` 值。这个小的辅助方法
把每个 AG-UI 事件包装进 `SseItem<BaseEvent>`。

```csharp
return TypedResults.ServerSentEvents(
    WrapAsSseItems(events, cancellationToken));
```

## 添加流选项 {#adding-stream-options}

当端点需要自定义流转换时，传入 `AGUIStreamOptions`。

```csharp
var streamOptions = new AGUIStreamOptions()
    .MapResultAsStateSnapshot("write_document");

var ctx = input.ToChatRequestContext(jsonSerializerOptions, streamOptions);
```

可用的映射钩子参见[可扩展性](./extensibility.md)。
