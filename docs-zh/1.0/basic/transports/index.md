---
title: "传输"
description: "传输要承载 AG-UI 必须提供什么，以及标准绑定 — 1.0"
---
<em class="lead">传输要承载 AG-UI 必须提供什么，以及标准绑定</em>

协议语义在每种传输上都相同。一个传输是一个**绑定**：它定义[运行输入](../../basic/run-input.md)如何送达、事件如何成帧和编码、流如何终止或失败。它不定义事件意味着什么——[事件模式](../../basic/patterns/index.md)与[处理模型](../../basic/processing.md)在每种绑定上都相同。

## 绑定契约 {#the-binding-contract}

一个绑定 MUST 提供：

- **有序、完整的投递**：一次运行的事件按生产方发出的顺序投递。协议的顺序即到达顺序；一个会重排或丢弃事件的传输，若没有一层把两者都恢复回来，就无法承载 AG-UI。
- **开启交换的那条 `RunAgentInput` 的投递**，在任何事件之前。一条继续承载[更多运行](../../events/lifecycle.md#several-runs-on-one-stream)——一个被重放的会话——的流，不为它们再投递任何输入：那些运行是生产方在重述历史，每个 `RUN_STARTED` MAY 携带它自己的 `input` 回显。
- **一个终止信号**，消费方能把它与截断区分开：在终止事件之后干净结束的流是一次已闭合的运行；在没有终止信号的情况下死去的连接是一次被截断的运行。
- **一条用于拒绝输入的错误路径**——结构非法的 `RunAgentInput` 在 `RUN_STARTED` 之前、在流之外被拒收。

认证与授权是绑定和应用的属性，而不是协议的属性：AG-UI 不定义任何凭证，一个绑定携带其通道所使用的任何东西（HTTP 认证、环境进程身份，或什么都没有）。

## 标准绑定 {#standard-bindings}

1. [HTTP + Server-Sent Events](../../basic/transports/http-sse.md)：运行输入是一个 HTTP POST；事件以携带 JSON 的 SSE 帧流回。
2. [HTTP + Protobuf](../../basic/transports/http-protobuf.md)：同一个 POST，协商为长度前缀 protobuf 帧的二进制响应。

两种绑定共享请求半部；它们只在响应编码上不同，由内容协商选择。说 HTTP 的实现 MUST 支持 SSE 绑定；protobuf 绑定是 OPTIONAL。

## 截断 {#truncation}

一条流在没有终止事件的情况下结束的消费方遇到一次被截断的运行：生产方可能一直在继续，但这个消费方永远看不到剩下的部分。一次被截断的运行没有结果。消费方 MUST NOT 为它合成一个 `RUN_FINISHED`，也 MUST NOT 报告它已成功；运行在断裂之前已交付的一切都保持已交付。除此之外是否以及如何呈现这次截断——让运行保持未决，还是抛出一个合成的失败——是消费方的事；重新运行是一次新的运行，带有新的 `runId`。

## 自定义传输 {#custom-transports}

实现 MAY 通过其他通道承载 AG-UI——WebSockets、消息总线、进程内管道。一个自定义传输 MUST 保持事件模型、事件模式和处理规则，且 MUST 满足上述绑定契约。它 SHOULD 记录其成帧方式、输入投递、以及终止和错误信号，以助互操作。

承载 JSON 的自定义传输 SHOULD 恰好像 SSE 绑定那样给事件成帧——每个帧一个事件对象——而不是发明一种新信封：SSE 绑定的成帧就是协议的 JSON 成帧，只有其 HTTP 机制是 HTTP 特有的。
