---
title: "流压缩"
description: "用于缩减冗长流式序列的 compactEvents 工具"
---
<em class="lead">用于缩减冗长流式序列的 compactEvents 工具</em>

# compactEvents {#compactevents}

`compactEvents` 在保留语义的前提下缩减事件数组中的冗长流式序列。可用于在持久化之前缩小日志，或简化对 Server‑Sent Events (SSE) 流的后处理。

```ts
import { compactEvents, EventType, type BaseEvent } from "@ag-ui/client"

const compacted: BaseEvent[] = compactEvents(events)
```

## API {#api}

```ts
function compactEvents(events: BaseEvent[]): BaseEvent[]
```

## 它的作用 {#what-it-does}

- 文本消息：把同一 `messageId` 的 `TEXT_MESSAGE_START` → `TEXT_MESSAGE_CONTENT*` →
  `TEXT_MESSAGE_END` 归组，将所有 `delta` 块拼接为单个 `TEXT_MESSAGE_CONTENT` 事件。
- 工具调用：把同一 `toolCallId` 的 `TOOL_CALL_START` → `TOOL_CALL_ARGS*` → `TOOL_CALL_END`
  归组，将所有 `delta` 块拼接为单个 `TOOL_CALL_ARGS` 事件。
- 交错事件：出现在某个 start/end 对之间的任何事件都会被移到该序列之后，以使流式块保持连续。
- 透传：所有其他事件（状态、自定义等）原样保留。

## 示例 {#example}

之前：

```ts
[
  { type: EventType.TEXT_MESSAGE_START, messageId: "m1", role: "assistant" },
  { type: EventType.TEXT_MESSAGE_CONTENT, messageId: "m1", delta: "Hello" },
  { type: EventType.TEXT_MESSAGE_CONTENT, messageId: "m1", delta: " " },
  { type: EventType.CUSTOM, name: "thinking" },
  { type: EventType.TEXT_MESSAGE_CONTENT, messageId: "m1", delta: "world" },
  { type: EventType.TEXT_MESSAGE_END, messageId: "m1" },
]
```

之后：

```ts
[
  { type: EventType.TEXT_MESSAGE_START, messageId: "m1", role: "assistant" },
  { type: EventType.TEXT_MESSAGE_CONTENT, messageId: "m1", delta: "Hello world" },
  { type: EventType.TEXT_MESSAGE_END, messageId: "m1" },
  { type: EventType.CUSTOM, name: "thinking" },
]
```

工具调用压缩对 `TOOL_CALL_ARGS` 块的处理方式与此类似。

## 何时使用 {#when-to-use}

- 持久化事件历史（用更少的帧存储相同的含义）
- 为分析或导出准备快照
- 减少测试或调试输出中的噪声

## 元数据 {#metadata}

折叠一连串增量事件时也会按 key 合并它们的[元数据](../../../concepts/metadata.md)，后写入者胜出，因此压缩后的事件流产生的元数据与原始事件流相同。在首个增量之后到达的元数据 — 无论是来自后续增量，还是来自被重放的 start — 都会按到达顺序附着在被折叠的事件上，因为流压缩会把 start 发出在该事件之前。

流压缩会重排事件，使每个流的事件保持在一起，而这种重排总体上并不保持语义。两个并行的工具调用，如果其结束事件的到达顺序与开始事件相反，在助手消息的 `toolCalls` 数组中会变成互换的位置，但各自仍携带自己的元数据。更重要的是，中断某个流的事件会被发出在该流之后，因此一条在消息中途到达的 `MESSAGES_SNAPSHOT` 会在这条消息自身的事件之后被重放，并覆盖它们所产生的结果 — 既包括追加的内容，也包括合并后的元数据。如果你依赖精确的重放等价性，请避免让快照与未关闭的流交错。

## 说明与限制 {#notes--limitations}

- 该工具聚焦于消息流与工具调用流。它不会修改状态事件（`STATE_SNAPSHOT`/`STATE_DELTA`），也不会生成消息快照。
- 关于背景与更广泛的模式（分支、归一化），参见[序列化](../../../concepts/serialization.md)。
