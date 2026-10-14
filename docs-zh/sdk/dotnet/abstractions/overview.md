---
title: "概览"
description: "AG-UI .NET SDK 中的协议类型"
---
<em class="lead">AG-UI .NET SDK 中的协议类型</em>

# AGUI.Abstractions {#aguiabstractions}

`AGUI.Abstractions` 是 AG-UI .NET SDK 的协议类型包。它定义了 AG-UI 客户端与服务器
共用的、共享的事件、消息、工具、上下文、能力、中断与序列化类型。

```bash
dotnet add package AGUI.Abstractions
```

该包对 HTTP、ASP.NET Core 或特定智能体运行时不持任何主张。它是 `@ag-ui/core` 的 .NET
对应物：用于事件流与请求负载的稳定线上类型。

!!! note
    `AGUI.Abstractions` 面向 `net10.0`、`net9.0`、`net8.0`、
      `netstandard2.0` 和 `net472`。它兼容 AOT：可序列化的协议类型注册在源生成的
      `AGUIJsonSerializerContext` 中。

## SDK 包 {#sdk-packages}

.NET SDK 被拆分为多个小包，因此协议类型、线上格式、客户端代码与服务器代码可以独立采用。

| 包 | 适用场景 |
| --- | --- |
| `AGUI.Abstractions` | 协议事件、消息、工具、能力、中断与 JSON 序列化。 |
| `AGUI.Formatting` | 事件流格式化器抽象与 Server-Sent Events 支持。 |
| `AGUI.Protobuf` | Protobuf 事件流格式化与二进制协议支持。 |
| `AGUI.Client` | 用于消费 AG-UI 端点的 HTTP 客户端与 `IChatClient` 实现。 |
| `AGUI.Server` | 从 `ChatResponseUpdate` 流到 AG-UI 事件的框架无关适配器。 |

## 线上格式与对齐 {#wire-formats-and-parity}

基于 Server-Sent Events 的 JSON 是全保真的事件流。
`AGUI.Formatting` 定义事件流格式化器契约与 SSE 支持。
`AGUI.Protobuf` 为共享 proto schema 所支持的协议子集添加二进制事件流格式化。

协议对齐始于 `AGUI.Abstractions`。当 TypeScript 参考 SDK 新增或修改某个线上类型时，
对应的 .NET 事件、消息、工具或能力类型应随 `AGUIJsonSerializerContext` 与兼容性测试
夹具一同更新。每当协议变更新增或修改 .NET 类型时，都应更新公共 API 跟踪文件。

```bash
cd sdks/dotnet
dotnet test tests/AGUI.Abstractions.UnitTests/
dotnet test tests/AGUI.Formatting.UnitTests/
dotnet test tests/AGUI.Protobuf.UnitTests/
```

## 类型 {#types}

表示协议基本构建块的核心数据结构：

- [RunAgentInput](./types.md#runagentinput) - 运行智能体的输入负载
- [Message types](./types.md#message-types) - 会话、工具、活动与推理消息
- [AGUIContext](./types.md#context) - 提供给智能体的上下文信息
- [AGUITool](./types.md#tool) - 带 JSON Schema 参数的工具定义
- [AgentCapabilities](./types.md#agentcapabilities) - 结构化的能力声明

- [类型参考](./types.md) — `AGUI.Abstractions` 中协议类型的完整文档

  - [多模态输入](./multimodal-inputs.md) — 用于文本、图像、音频、视频、文档与二进制输入的用户消息内容部分

## 事件 {#events}

事件驱动智能体与前端之间的通信：

- [Lifecycle events](./events.md#lifecycle-events) - 运行与步骤跟踪
- [Text message events](./events.md#text-message-events) - 助手消息流式输出
- [Tool call events](./events.md#tool-call-events) - 函数调用生命周期
- [State management events](./events.md#state-management-events) - 智能体状态与消息快照
- [Reasoning events](./events.md#reasoning-events) - 推理流支持
- [Activity events](./events.md#activity-events) - 结构化进度与瞬态 UI 状态
- [Special events](./events.md#special-events) - 原始事件与自定义事件

- [事件参考](./events.md) — `AGUI.Abstractions` 中所有事件类型的完整文档
