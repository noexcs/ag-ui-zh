---
title: "元数据"
description: "把额外信息附加到事件、消息和工具调用上"
---
<em class="lead">把额外信息附加到事件、消息和工具调用上</em>

元数据是为协议附加额外信息而受认可的方式——token 用量、追踪 id、结束原因，以及你的应用需要随会话一并携带的任何内容。

在它出现之前，生产方把未声明的属性挂在事件上，并指望消费方把它们透传过去。这就是为什么在 1.0 中会移除到达订阅者的未知属性：元数据用一个已声明且有类型的机制取而代之，且消费方必须携带它。

## 它存在于何处 {#where-it-lives}

四个位置，全部可选：

| 携带 `metadata` | 说明                                                                               |
| --------------- | ---------------------------------------------------------------------------------- |
| 每个事件        | 在基础事件上声明一次，因此所有事件类型都拥有它                                     |
| 每条消息        | 全部七种角色：developer、system、assistant、user、tool、activity、reasoning        |
| 每个工具调用    | 工具调用不是消息——参见[工具调用](#tool-calls)                                      |
| 每个恢复条目    | 一个请求字段，因此没有任何内容合并进它——参见[恢复条目](#resume-entries)            |

## 结构 {#shape}

该对象**按 key 开放**。一个 key 下允许任何 JSON 值，包括 `null`。你放入其中的内容没有 schema。

```typescript
{
  type: EventType.TEXT_MESSAGE_END,
  messageId: "msg_123",
  metadata: {
    "ag-ui": { usage: { input: 1200, output: 340 } },
    finishReason: "stop",
    traceId: "abc-123",
    retries: 0,
    labels: ["experimental"]
  }
}
```

该对象本身**要么不存在，要么是一个对象——绝不是 `null`**。空对象是合法的，表示“无话可说”，等同于省略它。

!!! note
    生产方绝不发出 `"metadata": null`：在每一个官方 SDK 中，没有值的可选字段
      都会从 JSON 中整体省略。TypeScript 客户端强制执行这一点，并拒绝 `null`
      元数据对象——与一些较早的可选字段不同，元数据没有需要容忍的遗留生产方。
      注意这种不对称性：**key 下的 `null` 值**是有意义的数据，始终会被保留。
      只有代替整个对象的 `null` 才是无效的。

## 保留 key {#the-reserved-key}

`ag-ui` key 保留给 AG-UI 自身使用。其他每一个 key 都归你。

运行时没有任何机制会拒绝写入 `ag-ui`——强制执行这一点会与按 key 开放的规则相矛盾——但请把它视为禁区，因为 AG-UI 可能在未来的版本中把自己的值放在那里。

## 合并进消息 {#merging-into-messages}

一条消息由一串事件组装而成，而其中有意思的值只有在最后才可知：生产方在生成结束之前并不知道自己的 token 用量。因此消费方**在序列到达时，把每个事件的元数据合并进该事件所构建的消息**。

这里描述的是从流中组装消息的客户端，例如 TypeScript 客户端。.NET 客户端不组装 AG-UI 消息——参见下方的 SDK 说明。

规则是逐 key 的“后写胜出”：

```typescript
// TEXT_MESSAGE_START    metadata: { source: "openai", stage: "start" }
// TEXT_MESSAGE_CONTENT  metadata: { stage: "content" }
// TEXT_MESSAGE_END      metadata: { stage: "end", usage: { output: 340 } }

message.metadata
// { source: "openai", stage: "end", usage: { output: 340 } }
```

`source` 之所以保留下来，是因为之后没有任何内容设置过它。`stage` 最终停留在最后写入的值上。`usage` 只在最后到达，而这正是关键所在。

### 值是替换，绝不混合 {#values-are-replaced-never-blended}

合并绝不递归。持有数组或对象的 key 会被整体替换：

```typescript
// earlier: { tags: ["a", "b", "c"] }
// later:   { tags: ["z"] }
// result:  { tags: ["z"] }        not ["a", "b", "c", "z"]
```

这在 `ag-ui` 之下同样成立。如果你需要向嵌套结构添加内容，请发送完整的新值。

### 哪些内容不合并 {#what-does-not-merge}

不构建消息的事件上的元数据会留在该事件上，绝不会到达任何消息：

- `RUN_STARTED`、`RUN_FINISHED`、`RUN_ERROR`
- `STEP_STARTED`、`STEP_FINISHED`
- `STATE_SNAPSHOT`、`STATE_DELTA`
- `RAW`、`CUSTOM`
- `REASONING_START`、`REASONING_END`、`REASONING_ENCRYPTED_VALUE`

`MESSAGES_SNAPSHOT` 是一个特例：其中的消息携带各自的元数据，并且在到达时就已经附带好，因此该事件自身的元数据不会合并进其中任何一条消息。

!!! tip
    把运行级别的总计放在 `RUN_FINISHED` 上没有问题，而且往往是对的——只是要
      从事件中读取它们，而不是指望它们在消息上。如果你想让它们出现在某条特定
      消息上，请在该消息的 `*_END` 事件上发送它们。

## 工具调用 {#tool-calls}

工具调用事件——`TOOL_CALL_START`、`TOOL_CALL_ARGS`、`TOOL_CALL_END`——合并进**工具调用**，而不是合并进拥有它的助手消息。

```typescript
assistantMessage.toolCalls[0].metadata
// { provider: "anthropic", latencyMs: 84 }
```

原因在于多个工具调用可以共享同一条父助手消息。把它们的元数据全部折叠进该父级，会使结果取决于这些调用恰好交织出现的顺序——而流变换被允许改变该顺序。让每个工具调用拥有自己的元数据，就消除了这个共享目标，因此无论流如何被处理，结果都相同。

`TOOL_CALL_RESULT` 不同：它会创建一条工具消息，因此其元数据像任何其他构建消息的事件一样合并进该消息。

## 恢复条目 {#resume-entries}

`RunAgentInput.resume` 中的每个条目——即在一次运行以中断结果结束后，客户端发回的逐个中断响应——携带自己的元数据。它保存关于该响应的信封数据，例如证明人的决定未被篡改的签名，或路由 key；智能体所请求的答案属于 `payload`。

恢复条目是一个请求字段，而不是从流中组装出来的东西，因此**没有合并语义**——没有任何内容累积进它。完整的恢复契约见[中断](./interrupts.md#resuming-a-run)。

## 传输 {#transports}

在 JSON 之上——也就是 SSE 所承载的、以及每个 SDK 所读写的格式——元数据是一个普通对象，每一种值的形状都能精确往返：null、数组、嵌套对象、字符串和数字。

二进制 protobuf 格式把它作为 `google.protobuf.Struct` 携带，其值类型有真正的 null 情况，因此 key 下的 `null` 会被保留而不是被近似处理，并且不存在的对象与空对象保持可区分。那里有两点注意事项，且都不是元数据特有的：

- **并非每个事件都有 protobuf 表示。** 线上格式覆盖事件类型的一个子集——工具结果、活动、推理以及已弃用的 thinking 事件没有 protobuf 消息，因此无论是否带元数据，它们都根本无法跨越该传输。.NET 编码器会直接拒绝它们；TypeScript 编码器会产出一个随后在解码时被拒绝的空载荷。无论哪种方式，事件都不会到达，所以不要为这些事件依赖二进制传输。
- **数字是 IEEE-754 double。** `google.protobuf.Value` 把每个数字都建模为 double，因此超过 2^53 的整数在往返中会丢失精度。这是该格式的属性，同样适用于 `state` 以及所有其他动态载荷。

不保证不同编码器之间的输出逐字节一致：`Struct` 是 `map<string, Value>`，而 protobuf 的 map 条目顺序不是规范化的。得到保证的是双方解码出的值相同。在实践中，TypeScript 与 .NET 编码器对跨语言测试套件中的每个 fixture 确实产出完全相同的字节，这一点在该套件中已断言，但不要依赖它。

## SDK 参考 {#sdk-reference}

!!! note
    在每个 SDK 中元数据都是按 key 开放的，因此其类型刻意设计得宽松。保持内容可 JSON 序列化是你的责任——一个函数或一个 `bigint` 会在类型层面被接受，然后在编码时失败。

**TypeScript** — 事件、消息、工具调用和恢复条目上的 `metadata?: Record<string, any>`。如果你自己组装消息，`mergeMetadata(existing, incoming)` 从 `@ag-ui/core` 导出，保留 key 则用 `AGUI_METADATA_KEY`。

**Python** — `metadata: Optional[Dict[str, Any]]`。基础模型在每条序列化路径上都会省略任何未设置的可选字段，因此不存在的对象会被省略而不是作为 `null` 发出——无需 `exclude_none=True`。`Metadata` 与 `AGUI_METADATA_KEY` 从 `ag_ui.core` 导出。

**.NET** — `BaseEvent`、`AGUIMessage`、`AGUIToolCall` 和 `AGUIResume` 上的 `JsonElement? Metadata`，保留 key 使用 `AGUIMetadata.ReservedKey`。

它是一个**线上格式字段**。它通过 JSON 和 protobuf 忠实地往返，因此读取 `RunAgentInput` 的服务器或解码该流的客户端都会看到它完好无损，并且 `AGUIMessage.Metadata` 会在 `MESSAGES_SNAPSHOT` 中的消息上携带它。它被刻意不暴露在 `Microsoft.Extensions.AI` 的 `ChatMessage` 上，这与 `encryptedValue` 和 `AGUIToolMessage.Error` 已有的行为一致。

如果你通过 `AGUIChatClient` 消费该流，请注意这在实践中意味着什么：`EventStreamConverter` 对 `TEXT_MESSAGE_START`、`TEXT_MESSAGE_END`、`TOOL_CALL_START` 或 `TOOL_CALL_ARGS` 不会发出任何 `ChatResponseUpdate`，因此这些事件上的元数据——包括按上文建议放在 `TEXT_MESSAGE_END` 上的用量——也不会到达 `RawRepresentation`。请从原始事件流中读取它，而不是从高层 chat 客户端读取。

## 流压缩 {#compaction}

TypeScript 客户端中的 `compactEvents` 会把一串流式事件压缩成更少的事件，以便存储或重放，并有意对它们重新排序，使每个流的事件保持在一起。

元数据本身不会引入新的顺序敏感性：每个合并目标都是唯一的——每条消息有各自的目标，每个工具调用携带自己的目标，而不是折叠进它可能共享的父级——因此合并到同一目标的两个事件之间绝不会被重新排序。

不过，流压缩的重新排序在一般情况下并不保持语义，而这早于元数据就已存在。打断某个流的事件会被放在它之后发出，因此中途到达的 `MESSAGES_SNAPSHOT` 会在该消息自身的事件之后被重放，并覆盖它们所产出的内容——被追加的内容和合并的元数据同样如此。如果你依赖精确的重放等价性，请避免把快照与一个尚未结束的流交织在一起。
