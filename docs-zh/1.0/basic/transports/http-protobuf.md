---
title: "HTTP + Protobuf"
description: "二进制绑定：同一个 POST，流回的是长度前缀 protobuf 帧 — 1.0"
---
<em class="lead">二进制绑定：同一个 POST，流回的是长度前缀 protobuf 帧</em>

二进制绑定，供想要紧凑线上的消费方使用。它完全共享 [SSE 绑定](../../basic/transports/http-sse.md)的请求半部——运行输入是同一个 JSON POST——只有响应不同。

## 协商 {#negotiation}

- 想要此绑定的客户端在 `Accept` 头中包含
  `application/vnd.ag-ui.event+proto`，与 `text/event-stream` 并列。允许即选择加入——一个通配范围
  （`*/*`、`application/*`）也允许该媒体类型——所以不能消费 protobuf 的客户端 MUST 发送显式的 `Accept` 指明它能消费的，
  而不是通配或降权条目：两种媒体类型之间的相对质量值不会被参考。
- 支持该绑定的生产方 SHOULD 在客户端的 `Accept` 以正质量允许该媒体类型时总是以它作答，否则 MUST
  以 SSE 作答。不支持它的生产方忽略该媒体类型——这正是客户端 MUST 始终准备好接收 SSE 的原因。
- 响应的 `Content-Type` 恰好是 `application/vnd.ag-ui.event+proto`；
  消费方凭此头选择解析器。

## 成帧 {#framing}

响应体是一个帧序列，每帧一个协议事件：

- 一个帧是一个 4 字节长度头——一个无符号 32 位大端整数——
  后随恰好那么多字节的单个编码事件。
- 帧之间紧密相接，无分隔符。消费方 MUST 容忍跨传输块拆分的帧，以及一个块内的多个帧。
- 在帧中间结束的体是一次
  [被截断的运行](../../basic/transports/index.md#truncation)。

## 线上模式 {#the-wire-schema}

protobuf 消息定义与 SDK 由同一个 [JSON Schema](../../schema-files.md) 生成；线上模式不是第二个事实来源。跨实现的一致性属于符合性范围：一组规范事件的语料库固定了编码后的字节，每个第一方编码器 MUST 逐字节复现该语料库。（语料库就是保证——两个编码器拿到相同的*语义*值，仍可能以不同顺序排列一个开放 JSON 对象的条目，而 protobuf 的 map 编码会把这个差异显现出来。）

语义尽可能贴近 SSE 绑定，以二进制线所能达到的程度为限：

- 从一个帧解码出的事件进入与从 SSE 解析出的事件相同的
  [处理管道](../../basic/processing.md)——先中间件，后强制执行，完全一致。
- 线上模式作为开放载荷承载的材料——`RUN_FINISHED.outcome`、元数据、状态、`rawEvent`——存活过解码并到达该管道：一个经此绑定到达的不可识别结果由强制执行带警告地剥离，与 SSE 上完全相同，且绑定 MUST NOT 在解码时拒绝它。
- 对其余部分，二进制线天生更窄。一个*字段*早于本构建的线上模式而存在时，被 protobuf 解码本身跳过，悄无声息——带警告剥离的行为只有在 JSON 线上才完全可观察。同样的收窄也覆盖线上模式未建模的协议合法的开放成员：JSON Patch 操作的扩展成员在 JSON 线上 MUST 被保留，但过不了这一线。一个*事件*的信封分支早于本构建而存在时，没有类型字符串可向后传递，所以绑定带警告地丢弃该帧——强制执行给出的同样答案，只是说在了传输这一层。
- 一个字节无法解码为消息的帧是畸形的传输材料，对这条流是致命的。一个体单纯地在帧中间结束则不是：那是一次[被截断的运行](../../basic/transports/index.md#truncation)。

## 错误 {#errors}

与 [SSE 绑定](../../basic/transports/http-sse.md#errors)完全相同：流开始之前的拒绝是 HTTP 错误状态；流内部的失败是 `RUN_ERROR`，作为一个与其他帧无异的帧。
