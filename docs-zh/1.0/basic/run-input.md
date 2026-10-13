---
title: "运行输入"
description: "唯一一条从应用流向智能体的消息，以及它的每个字段各自要求什么 — 1.0"
---
<em class="lead">唯一一条从应用流向智能体的消息，以及它的每个字段各自要求什么</em>

事件从生产方流向消费方。反方向恰好只有一条消息：`RunAgentInput`，在每次交换开启时发送一次。生产方关于会话所知的一切，都经由它到达。它所请求的运行是该次交换的最后一次运行；重放某个会话历史的事件流在携带较早的运行时会[不再附带输入](../basic/transports/index.md#the-binding-contract)。

[模式](../schema.md#runagentinput)定义了它的形状；本页说明每个字段的要求。生产方 MAY 在 `RUN_STARTED.input` 上把输入回显回去，这样没有发起请求的消费方也能看到智能体被要求执行什么。

## 标识 {#identity}

`threadId` 命名会话，`runId` 命名本输入所请求的运行；两者均为 REQUIRED。流上的每一次运行都在其边界事件上携带输入的 `threadId`——携带身份的两个事件即 `RUN_STARTED` 和 `RUN_FINISHED`——且每次运行的两个边界事件 MUST 在 `runId` 上一致。被请求的运行回显本输入的 `runId`；被重放的运行携带它自己的。`parentRunId` 为 OPTIONAL，当智能体以独立运行启动另一个智能体时，它命名生成本次运行的那次运行。

## `protocolVersion` {#protocolversion}

在模式中为 OPTIONAL，因为缺失本身即标识出一个早于协议携带版本时期的对端——但实现此版本的消费方 MUST 在此声明它所使用的版本，除非它知道对端早于该字段，从而省略该成员，以免旧解析器拒绝它。生产方在 `RUN_STARTED` 上以自己的声明作答；规则见[版本与兼容性](../basic/versioning.md#version-negotiation)。

## `messages` {#messages}

REQUIRED。迄今为止的会话，按顺序。生产方 MUST 将其视为自己所被展示的完整历史——协议没有让较早轮次到达的旁路。

消息类型及其内容形状——包括多模态 [`ContentPart`](../schema.md#contentpart)，它以 URL、内联数据或[提供方文件句柄](#provider-file-handles)承载文本、图像、音频、视频和文档，既出现在用户消息上，也出现在回答[前端工具调用](../events/tool-calls.md#frontend-tools)的工具消息上——是模式的事。两条行为规则附于其上：

- 无法使用某个内容部分的生产方——一个没有视觉能力的模型被递上一张图像——MUST NOT 因此让运行失败。跳过无法使用的部分并继续才是符合性的行为；在降级后的*出站*路径上丢失内容则不同，它要求发出警告（[版本与兼容性](../basic/versioning.md)）。
- 活动消息永远不会传回生产方：消费方 MUST 在发送前将它们从 `messages` 中剥离。它们是消费方的渲染材料，而非智能体恢复所依据的会话。

### 提供方文件句柄 {#provider-file-handles}

媒体部分的 `source` 说明它的字节在哪里：内联携带（`data`）、可通过 URL 获取（`url`），或已位于模型提供方处、由一个提供方签发的句柄标识（`file`）——一个 OpenAI 或 Anthropic 的文件 id、一个 Gemini 文件 URI、一个只有该提供方能读的存储 URL。[`file` source](../schema.md#filesource) 之所以存在，是因为句柄既不是前两者中的任何一种：它不承载字节，也只有签发它的那个提供方能获取它，所以把它放进 `url` 只会招来其他所有对端的尝试。

- 一个 `file` 类型 `source` 的 `value` 是不透明的。对端 MUST NOT 去获取它、解析它，或从中读出一个 scheme；它要么把句柄交给提供方，要么不使用该部分。
- `provider` 在已知时命名签发该句柄的一方。它是 OPTIONAL——智能体本来就清楚自己与哪个提供方通信——当它存在时 SHOULD 是 [`TokenUsage.provider`](../schema.md#tokenusage) 所用的那种小写厂商 id，这样对端在发送前就能判断一个句柄是否是自己能用的。
- 一个被递上无法解析的句柄的生产方——别的提供方的、未知提供方的、已过期的——所处的正是上面第一条规则已涵盖的情形：它 MUST NOT 让运行失败，而是跳过该部分并继续，且 SHOULD 如此告知。句柄的有效期是提供方的事；想要携带过期时间的生产方将其放进该部分的 `metadata` 里。
- `source` 的分支是封闭集合：对端不认识其 `type` 的 `source` 会验证失败，而不是被透传下去。这正是该分支在 1.0 中而不是更晚次版本中的原因——按 1.0 构建的消费方从未可能把它传递下去。

## `tools` {#tools}

OPTIONAL。应用自己的工具——*前端工具*——为本次运行提供给智能体：名称、描述，以及（当工具带参数时）参数模式。执行它们的是应用，不是智能体；调用其中一个会把控制权交还到运行边界之外，其往返过程由[工具调用](../events/tool-calls.md#frontend-tools)规定。

缺失的列表与空列表含义相同：没有工具。生产方 MUST 把缺失的 `tools` 与空列表作完全相同的处理，消费方 MAY 省略空列表而不发送 `[]`。

## `context` {#context}

OPTIONAL。应用希望进入智能体上下文中的信息，以描述–值对的形式。它的存在就是为了被*注入*：生产方 SHOULD 让每一条条目都能被模型使用，作为本次运行依据的一部分。怎么做——系统提示词、前言、框架对上下文所做的任何处理——是生产方的事；协议只说 context 是给模型看的，而不是传输的簿记。

缺失与 `tools` 完全一样，意味着与空相同。

## `state` {#state}

OPTIONAL。运行所起始的状态——消费方最后同意的值，通常是上一次运行的[状态事件](../events/state.md)留下的东西。缺失的 `state` 意味着空对象：还没有任何同意的内容，而 `{}` 就是无。发出状态增量的生产方 MUST 以该值为基准计算增量，直到它自己的第一个快照将其替换。

## `forwardedProps` {#forwardedprops}

OPTIONAL。一个应用专属的通道，原封不动地透传给智能体。可以是任何 JSON 值，但整体 `null` 除外——整体为 `null` 意味着该字段被省略。载荷内部的 null 值会被保留。协议不对载荷附加任何含义，中间方 MUST NOT 更改它。

## `resume` {#resume}

OPTIONAL。当本次运行从某次运行继续时，对结束上一次运行的那些中断的回答。各条目及其义务在[中断与恢复](../basic/patterns/interrupt-resume.md)中规定。

## 错误处理 {#error-handling}

生产方无法解析的输入，或畸形的输入——某个已知字段携带了模式所拒绝的值——会在 `RUN_STARTED` 之前、经由传输的错误路径被拒绝：运行根本不会开始，也不存在可供 `RUN_ERROR` 传递的流。拒绝如何送达，是各[传输绑定](../basic/transports/index.md)的事。

输入中不可识别的成员不属于畸形。[处理模型](../basic/processing.md)的不对称性同样约束这个方向：生产方遇到不认识的输入材料时，会带警告地剥离它并继续运行，于是较新消费方的输入不会在较旧的生产方处被弹回。
