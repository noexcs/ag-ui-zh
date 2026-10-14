---
title: "概览"
description: "用于编码 Agent User Interaction Protocol 事件的文档"
---
<em class="lead">用于编码 Agent User Interaction Protocol 事件的文档</em>

```bash
pip install ag-ui-protocol
```

# 事件编码器 {#event-encoder}

Agent User Interaction Protocol 使用流式方式把事件从智能体发送到客户端。`EventEncoder`
类提供将事件编码为可通过 HTTP 发送的格式的功能。

## EventEncoder {#eventencoder}

`from ag_ui.encoder import EventEncoder`

`EventEncoder` 类负责把 `BaseEvent` 对象编码为可传输给客户端的字符串表示。

```python
from ag_ui.core import BaseEvent
from ag_ui.encoder import EventEncoder

# Initialize the encoder {#initialize-the-encoder}
encoder = EventEncoder()

# Encode an event {#encode-an-event}
encoded_event = encoder.encode(event)
```

### 用法 {#usage}

`EventEncoder` 通常用在 HTTP 处理器中，把事件对象转换为数据流。当前实现把事件编码为
Server-Sent Events (SSE)，客户端可以使用 EventSource API 消费。

### 方法 {#methods}

#### `__init__(accept: str = None)` {#initaccept-str--none}

创建一个新的编码器实例。

| 参数 | 类型 | 说明 |
| --------- | ---------------- | ----------------------------------- |
| `accept`  | `str`（可选） | 客户端接受的内容类型 |

#### `encode(event: BaseEvent) -> str` {#encodeevent-baseevent--str}

把事件编码为字符串表示。

| 参数 | 类型 | 说明 |
| --------- | ----------- | ------------------- |
| `event`   | `BaseEvent` | 要编码的事件 |

**返回**：该事件以 SSE 格式表示的字符串。

### 示例 {#example}

```python
from ag_ui.core import TextMessageContentEvent, EventType
from ag_ui.encoder import EventEncoder

# Create an event {#create-an-event}
event = TextMessageContentEvent(
    type=EventType.TEXT_MESSAGE_CONTENT,
    message_id="msg_123",
    delta="Hello, world!"
)

# Initialize the encoder {#initialize-the-encoder}
encoder = EventEncoder()

# Encode the event {#encode-the-event}
encoded_event = encoder.encode(event)
print(encoded_event)
# Output: data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg_123","delta":"Hello, world!"}\n\n {#output-data-typetextmessagecontentmessageidmsg123deltahello-worldnn}
```

### 实现细节 {#implementation-details}

在内部，编码器把事件转换为 JSON，并将其格式化为具有以下结构的 Server-Sent Events：

```
data: {json-serialized event}\n\n
```

这种格式让客户端能够接收连续的事件流，并在事件到达时进行处理。
