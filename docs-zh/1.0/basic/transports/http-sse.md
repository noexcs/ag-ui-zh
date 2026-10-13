---
title: "HTTP + Server-Sent Events"
description: "默认绑定：承载运行输入的 POST，承载运行的 text/event-stream — 1.0"
---
<em class="lead">默认绑定：承载运行输入的 POST，承载运行的 text/event-stream</em>

默认绑定。应用向智能体端点 POST 运行输入；响应是一个承载运行的
[Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
流。

## 请求 {#request}

- 客户端向智能体端点发送 `POST`。请求体是
  [`RunAgentInput`](../../basic/run-input.md)，作为单个 JSON 对象，
  UTF-8 编码，带 `Content-Type: application/json`。
- 客户端发送 `Accept: text/event-stream`（如果它也能消费那种绑定，则加上
  [protobuf 媒体类型](../../basic/transports/http-protobuf.md)）。

## 响应 {#response}

- 运行启动即以 `200` 应答，`Content-Type: text/event-stream`。
- 每个 SSE 事件的 `data` 负载恰好是一个作为 JSON 对象的协议事件 —
  从不多于一个，也从不是一段碎片。多行的 `data:` 字段按 SSE 的规定拼接。
- 生产方 MUST 用 LF（`\n`）行尾为流封装帧。SSE 文法也接受 CR 和 CRLF，
  但该绑定固定为每个消费方已知能解析的那一种形式；消费方 MAY 额外接受
  完整文法。
- 消费方 MUST 忽略 `data` 以外的 SSE 字段（`event:`、`id:`、`retry:`），
  并且 MUST 容忍 SSE 保活注释行（`: keep-alive`），生产方 MAY 以任何频率
  发送它们。
- 生产方在最后运行的终结事件之后关闭响应体。一个 POST 承载一个请求；但当
  生产方在请求的运行之前重放会话历史时，响应 MAY 仍然承载
  [多个运行](../../events/lifecycle.md#several-runs-on-one-stream) —
  按[绑定契约](../../basic/transports/index.md#the-binding-contract)，
  这些运行不再有额外输入传输。

## 错误 {#errors}

- 在运行开始前被拒绝的输入 — 格式错误的 JSON、验证失败、认证被拒 —
  是没有事件流的 HTTP 错误状态。运行从未启动。
- 流开启之后的失败在流内传输，作为 `RUN_ERROR`。HTTP 状态已经发出且无法
  更改；消费方 MUST NOT 仅凭 `200` 推断成功。
- 在没有终结事件的情况下断开的连接是一个
  [截断的运行](../../basic/transports/index.md#truncation)。

## 无恢复 {#no-resumption}

该绑定没有流恢复：SSE 的 `Last-Event-ID` 机制不被使用，断开的流也无法
重新进入。重跑是一次带有新 `runId` 的新运行，其输入携带消费方所保留的
一切。

## 示例 {#example}

```
POST /agent HTTP/1.1
Content-Type: application/json
Accept: text/event-stream

{"threadId":"thr-1","runId":"run-1","messages":[…]}

HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"type":"RUN_STARTED","threadId":"thr-1","runId":"run-1"}

data: {"type":"TEXT_MESSAGE_START","messageId":"msg-1","role":"assistant"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-1","delta":"Hello."}

data: {"type":"TEXT_MESSAGE_END","messageId":"msg-1"}

data: {"type":"RUN_FINISHED","threadId":"thr-1","runId":"run-1"}
```
