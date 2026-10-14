---
title: "概览"
description: "服务器适配器包概览"
---
<em class="lead">服务器适配器包概览</em>

# AGUI.Server {#aguiserver}

`AGUI.Server` 是 AG-UI 的 .NET 服务器端适配器。它把
`Microsoft.Extensions.AI.IChatClient` 流转换为 AG-UI 协议事件，因此你可以把任何聊天
客户端暴露为接受 `RunAgentInput` 并向 Web 前端流式发送 AG-UI 事件的 AG-UI 端点。

```bash
dotnet add package AGUI.Server
```

## 核心理念 {#the-core-idea}

你不需要学习新的智能体编程模型。你托管的是一个 `IChatClient`。

该包把 AG-UI 请求体适配为 `Microsoft.Extensions.AI` 消息与选项，调用你的聊天客户端，
然后把流式的 `ChatResponseUpdate` 值转换回 AG-UI 协议事件。

## 它依赖什么 {#what-it-depends-on}

`AGUI.Server` 有意保持小巧：

- 来自 `AGUI.Abstractions` 的 [AG-UI 协议类型](../abstractions/events.md)
- `Microsoft.Extensions.AI.Abstractions`

它与框架无关：不依赖 ASP.NET Core 或任何 Web 框架。你把该适配器托管在你选择的 Web 框架中
（示例与文档使用 ASP.NET Core）。它也不依赖 .NET AG-UI 客户端包。服务器包与客户端包共享
协议类型，但彼此独立。

!!! note
    服务器包面向 `net10.0`、`net9.0` 和 `net8.0`。

## 托管层处理的内容 {#what-the-hosting-layer-handles}

托管层为你处理协议细节：

- 把 `RunAgentInput.Messages` 转换为 `ChatMessage` 值
- 把 `RunAgentInput.Resume` 转换为 MEAI 审批与中断响应内容，将负载 — 以及对于
  非工具类中断还有元数据 — 携带到 `InterruptResponseContent` 上
- 把客户端声明的工具安装到 `ChatOptions` 上
- 将原始输入存储在 `ChatOptions.AdditionalProperties[AGUIConstants.RunAgentInputKey]` 下
- 发出 `RUN_STARTED` 与终结性的 `RUN_FINISHED` 结果
- 把文本、推理、工具调用、工具结果、状态、原始事件与中断映射为 AG-UI 事件
- 将结果以 Server-Sent Events 流式发送

## 验证与框架归属 {#verification-and-framework-ownership}

服务器测试验证 `RunAgentInput` 变为 `ChatMessage` 与 `ChatOptions`、恢复负载变为标准
MEAI 响应内容、生命周期事件被发出，以及流式的 `ChatResponseUpdate` 值变为预期的文本、
推理、工具、状态、原始、自定义与中断事件。原始 AG-UI 事件（包括 `RUN_ERROR`）在通过
`ChatResponseUpdate.RawRepresentation` 提供时透传。

```bash
cd sdks/dotnet
dotnet test tests/AGUI.Server.UnitTests/
dotnet test tests/AGUI.Hosting.AspNetCore.IntegrationTests/
```

SDK 拥有共享的 AG-UI 与 `Microsoft.Extensions.AI` 桥接。框架特定的映射归属于消费方框架。
例如，Microsoft Agent Framework 可以使用 `AGUI.Server` 作为通用桥接，然后用
`AGUIStreamOptions` 或原始 AG-UI 事件映射其自身的工作流、步骤与智能体事件。

## 服务器与客户端协同 {#server-and-client-together}

在构建 AG-UI 服务器时使用 `AGUI.Server`。当 .NET 代码需要把 AG-UI 端点作为
`IChatClient` 消费时，使用 [AGUI.Client](../client/overview.md)。

- [端点](./endpoints.md) — 构建规范的 ASP.NET Core AG-UI 端点

  - [可扩展性](./extensibility.md) — 使用 AGUIStreamOptions 自定义流转换
