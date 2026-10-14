---
title: "事件"
description:
  "Agent User Interaction Protocol Python SDK 中所用事件的文档"
---
<em class="lead">Agent User Interaction Protocol Python SDK 中所用事件的文档</em>

# 事件 {#events}

Agent User Interaction Protocol Python SDK 采用基于流式事件的
架构。事件是智能体与前端之间通信的基本单元。本节记录事件类型及其属性。

## EventType 枚举 {#eventtype-enum}

`from ag_ui.core import EventType`

`EventType` 枚举定义了系统中所有可能的事件类型：

```python
class EventType(str, Enum):
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    ACTIVITY_SNAPSHOT = "ACTIVITY_SNAPSHOT"
    ACTIVITY_DELTA = "ACTIVITY_DELTA"
    RAW = "RAW"
    CUSTOM = "CUSTOM"
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"
    REASONING_START = "REASONING_START"
    REASONING_MESSAGE_START = "REASONING_MESSAGE_START"
    REASONING_MESSAGE_CONTENT = "REASONING_MESSAGE_CONTENT"
    REASONING_MESSAGE_END = "REASONING_MESSAGE_END"
    REASONING_MESSAGE_CHUNK = "REASONING_MESSAGE_CHUNK"
    REASONING_END = "REASONING_END"
    REASONING_ENCRYPTED_VALUE = "REASONING_ENCRYPTED_VALUE"
    SUBAGENT_STARTED = "SUBAGENT_STARTED"
    SUBAGENT_FINISHED = "SUBAGENT_FINISHED"
    SUBAGENT_ERROR = "SUBAGENT_ERROR"
```

## BaseEvent {#baseevent}

`from ag_ui.core import BaseEvent`

所有事件都继承自 `BaseEvent` 类，它提供所有事件类型共享的公共属性。

```python
class BaseEvent(ConfiguredBaseModel):
    type: EventType
    timestamp: Optional[int] = None
    raw_event: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
```

| 属性        | 类型                       | 描述                                     |
| ----------- | -------------------------- | ---------------------------------------- |
| `type`      | `EventType`                | 事件类型（联合类型的判别字段）           |
| `timestamp` | `Optional[int]`            | 事件创建时的时间戳                       |
| `raw_event` | `Optional[Any]`            | 该事件被转换前的原始事件数据             |
| `metadata`  | `Optional[Dict[str, Any]]` | 附加到事件上的额外信息                   |

`metadata` 按 key 开放：一个 key 下允许任何 JSON 值，包括
`None`。该对象可以缺失，但存在时绝不为 `None` — 显式的 `null` 会解析回缺失，
因此普通的 `model_dump_json()` 可以往返。`EventEncoder` 使用
`exclude_none=True`，因此缺失的对象会从线上格式中省略，而不会以 `null`
发出。`ag-ui` key 保留给 AG-UI 自用。

## 生命周期事件 {#lifecycle-events}

这些事件表示一次智能体运行的生命周期。

### RunStartedEvent {#runstartedevent}

`from ag_ui.core import RunStartedEvent`

表示一次智能体运行的开始。

```python
class RunStartedEvent(BaseEvent):
    type: Literal[EventType.RUN_STARTED]
    thread_id: str
    run_id: str
    parent_run_id: Optional[str] = None
    input: Optional[RunAgentInput] = None
```

| 属性            | 类型                      | 描述                                                                                                           |
| --------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `thread_id`     | `str`                     | 会话线程的 ID                                                                                                  |
| `run_id`        | `str`                     | 智能体运行的 ID                                                                                                |
| `parent_run_id` | `Optional[str]`           | （可选）用于分支/时间旅行的谱系指针。若存在，指向同一会话中先前的一次运行                                        |
| `input`         | `Optional[RunAgentInput]` | （可选）为本次运行发送给智能体的确切输入载荷。可以省略已在历史中的消息                                          |

### TokenUsage {#tokenusage}

`from ag_ui.core import TokenUsage`

一种可复用的、仅含数值的 token 用量摘要，由终结性运行事件携带。
它有意**只**包含提供方/模型标签与 token 计数 — 不含
提示、补全、消息或标识符。这些计数遵循协议的[计量规则](../../../1.0/events/lifecycle.md#token-usage)：
输入与输出计数是总量，缓存与推理计数是其中的部分，而绝不是额外的追加量。

```python
class TokenUsage(ConfiguredBaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    cached_input_tokens: Optional[int] = None
    cache_write_input_tokens: Optional[int] = None
```

| 属性                       | 类型            | 描述                                                          |
| -------------------------- | --------------- | ------------------------------------------------------------- |
| `provider`                 | `Optional[str]` | 报告该用量的提供方（例如 `openai`）                           |
| `model`                    | `Optional[str]` | 产生该用量的模型                                              |
| `input_tokens`             | `Optional[int]` | 全部输入 token，含缓存读取与写入                              |
| `output_tokens`            | `Optional[int]` | 全部输出 token，含推理                                        |
| `total_tokens`             | `Optional[int]` | `input_tokens` 加上 `output_tokens`                           |
| `reasoning_tokens`         | `Optional[int]` | 用于推理的输出 token；属于 `output_tokens` 的一部分           |
| `cached_input_tokens`      | `Optional[int]` | 从提示缓存读取的输入 token；属于 `input_tokens` 的一部分      |
| `cache_write_input_tokens` | `Optional[int]` | 写入提示缓存的输入 token；属于 `input_tokens` 的一部分        |

### RunFinishedEvent {#runfinishedevent}

`from ag_ui.core import RunFinishedEvent`

表示一次智能体运行成功完成。

```python
class RunFinishedEvent(BaseEvent):
    type: Literal[EventType.RUN_FINISHED]
    thread_id: str
    run_id: str
    result: Optional[Any] = None
    usage: Optional[List[TokenUsage]] = None
```

| 属性        | 类型                         | 描述                                                     |
| ----------- | ---------------------------- | -------------------------------------------------------- |
| `thread_id` | `str`                        | 会话线程的 ID                                            |
| `run_id`    | `str`                        | 智能体运行的 ID                                          |
| `result`    | `Optional[Any]`              | 智能体运行的结果数据                                     |
| `usage`     | `Optional[List[TokenUsage]]` | 该运行按 (provider, model) 划分的 token 用量（若报告）   |

### RunErrorEvent {#runerrorevent}

`from ag_ui.core import RunErrorEvent`

表示智能体运行期间发生错误。

```python
class RunErrorEvent(BaseEvent):
    type: Literal[EventType.RUN_ERROR]
    message: str
    code: Optional[str] = None
    usage: Optional[List[TokenUsage]] = None
```

| 属性      | 类型                         | 描述                                    |
| --------- | ---------------------------- | --------------------------------------- |
| `message` | `str`                        | 错误消息                                |
| `code`    | `Optional[str]`              | 错误码                                  |
| `usage`   | `Optional[List[TokenUsage]]` | 已完成模型调用产生的部分 token 用量     |

### StepStartedEvent {#stepstartedevent}

`from ag_ui.core import StepStartedEvent`

表示智能体运行中某个步骤的开始。

```python
class StepStartedEvent(BaseEvent):
    type: Literal[EventType.STEP_STARTED]
    step_name: str
```

| 属性        | 类型  | 描述     |
| ----------- | ----- | -------- |
| `step_name` | `str` | 步骤名称 |

### StepFinishedEvent {#stepfinishedevent}

`from ag_ui.core import StepFinishedEvent`

表示智能体运行中某个步骤的完成。

```python
class StepFinishedEvent(BaseEvent):
    type: Literal[EventType.STEP_FINISHED]
    step_name: str
```

| 属性        | 类型  | 描述     |
| ----------- | ----- | -------- |
| `step_name` | `str` | 步骤名称 |

## 文本消息事件 {#text-message-events}

这些事件表示会话中文本消息的生命周期。

### TextMessageStartEvent {#textmessagestartevent}

`from ag_ui.core import TextMessageStartEvent`

表示一条文本消息的开始。

```python
class TextMessageStartEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_START]
    message_id: str
    role: Literal["assistant"]
```

| 属性         | 类型                   | 描述                 |
| ------------ | ---------------------- | -------------------- |
| `message_id` | `str`                  | 消息的唯一标识符     |
| `role`       | `Literal["assistant"]` | 角色始终为 "assistant" |

### TextMessageContentEvent {#textmessagecontentevent}

`from ag_ui.core import TextMessageContentEvent`

表示流式文本消息中的一块内容。

```python
class TextMessageContentEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_CONTENT]
    message_id: str
    delta: str  # Non-empty string

    def model_post_init(self, __context):
        if len(self.delta) == 0:
            raise ValueError("Delta must not be an empty string")
```

| 属性         | 类型  | 描述                                      |
| ------------ | ----- | ----------------------------------------- |
| `message_id` | `str` | 与 TextMessageStartEvent 中的 ID 匹配     |
| `delta`      | `str` | 文本内容块（非空）                        |

### TextMessageEndEvent {#textmessageendevent}

`from ag_ui.core import TextMessageEndEvent`

表示一条文本消息的结束。

```python
class TextMessageEndEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_END]
    message_id: str
```

| 属性         | 类型  | 描述                                      |
| ------------ | ----- | ----------------------------------------- |
| `message_id` | `str` | 与 TextMessageStartEvent 中的 ID 匹配     |

## 工具调用事件 {#tool-call-events}

这些事件表示智能体发起的工具调用的生命周期。

### ToolCallStartEvent {#toolcallstartevent}

`from ag_ui.core import ToolCallStartEvent`

表示一次工具调用的开始。

```python
class ToolCallStartEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_START]
    tool_call_id: str
    tool_call_name: str
    parent_message_id: Optional[str] = None
```

| 属性                | 类型            | 描述                    |
| ------------------- | --------------- | ----------------------- |
| `tool_call_id`      | `str`           | 工具调用的唯一标识符    |
| `tool_call_name`    | `str`           | 被调用工具的名称        |
| `parent_message_id` | `Optional[str]` | 父消息的 ID             |

### ToolCallArgsEvent {#toolcallargsevent}

`from ag_ui.core import ToolCallArgsEvent`

表示工具调用的一部分参数数据。

```python
class ToolCallArgsEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_ARGS]
    tool_call_id: str
    delta: str
```

| 属性           | 类型  | 描述                                   |
| -------------- | ----- | -------------------------------------- |
| `tool_call_id` | `str` | 与 ToolCallStartEvent 中的 ID 匹配     |
| `delta`        | `str` | 参数数据块                             |

### ToolCallEndEvent {#toolcallendevent}

`from ag_ui.core import ToolCallEndEvent`

表示一次工具调用的结束。

```python
class ToolCallEndEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_END]
    tool_call_id: str
```

| 属性           | 类型  | 描述                                   |
| -------------- | ----- | -------------------------------------- |
| `tool_call_id` | `str` | 与 ToolCallStartEvent 中的 ID 匹配     |

### ToolCallResultEvent {#toolcallresultevent}

`from ag_ui.core import ToolCallResultEvent`

提供工具调用执行的结果。

```python
class ToolCallResultEvent(BaseEvent):
    message_id: str
    type: Literal[EventType.TOOL_CALL_RESULT]
    tool_call_id: str
    content: str
    role: Optional[Literal["tool"]] = None
```

| 属性           | 类型                        | 描述                                                        |
| -------------- | --------------------------- | ----------------------------------------------------------- |
| `message_id`   | `str`                       | 该结果所属会话消息的 ID                                     |
| `tool_call_id` | `str`                       | 与对应 ToolCallStartEvent 中的 ID 匹配                      |
| `content`      | `str`                       | 工具执行产生的实际结果/输出内容                             |
| `role`         | `Optional[Literal["tool"]]` | 可选的角色标识符，工具结果通常为 "tool"                     |

## 状态管理事件 {#state-management-events}

这些事件用于管理智能体状态。

### StateSnapshotEvent {#statesnapshotevent}

`from ag_ui.core import StateSnapshotEvent`

提供智能体状态的完整快照。

```python
class StateSnapshotEvent(BaseEvent):
    type: Literal[EventType.STATE_SNAPSHOT]
    snapshot: State
```

| 属性       | 类型    | 描述                    |
| ---------- | ------- | ----------------------- |
| `snapshot` | `State` | 完整的状态快照          |

### StateDeltaEvent {#statedeltaevent}

`from ag_ui.core import StateDeltaEvent`

使用 JSON Patch 提供智能体状态的局部更新。

```python
class StateDeltaEvent(BaseEvent):
    type: Literal[EventType.STATE_DELTA]
    delta: List[Any]  # JSON Patch (RFC 6902)
```

| 属性    | 类型        | 描述                          |
| ------- | ----------- | ----------------------------- |
| `delta` | `List[Any]` | JSON Patch 操作数组           |

### MessagesSnapshotEvent {#messagessnapshotevent}

`from ag_ui.core import MessagesSnapshotEvent`

提供会话中所有消息的快照。

```python
class MessagesSnapshotEvent(BaseEvent):
    type: Literal[EventType.MESSAGES_SNAPSHOT]
    messages: List[Message]
```

| 属性       | 类型            | 描述                     |
| ---------- | --------------- | ------------------------ |
| `messages` | `List[Message]` | 消息对象数组             |

### ActivitySnapshotEvent {#activitysnapshotevent}

`from ag_ui.core import ActivitySnapshotEvent`

送达活动消息的完整快照。

```python
class ActivitySnapshotEvent(BaseEvent):
    type: Literal[EventType.ACTIVITY_SNAPSHOT]
    message_id: str
    activity_type: str
    content: Any
    replace: bool = True
```

| 属性            | 类型                    | 描述                                                                                 |
| --------------- | ----------------------- | ------------------------------------------------------------------------------------ |
| `message_id`    | `str`                   | 目标 `ActivityMessage` 的标识符                                                      |
| `activity_type` | `str`                   | 活动判别字段，例如 `"PLAN"` 或 `"SEARCH"`                                            |
| `content`       | `Any`                   | 描述完整活动状态的结构化载荷                                                         |
| `replace`       | `bool`（默认 `True`）   | 当为 `False` 时，若已存在相同 ID 的消息则忽略该快照                                  |

### ActivityDeltaEvent {#activitydeltaevent}

`from ag_ui.core import ActivityDeltaEvent`

使用 JSON Patch 对活动快照提供增量更新。

```python
class ActivityDeltaEvent(BaseEvent):
    type: Literal[EventType.ACTIVITY_DELTA]
    message_id: str
    activity_type: str
    patch: List[Any]
```

| 属性            | 类型        | 描述                                                            |
| --------------- | ----------- | --------------------------------------------------------------- |
| `message_id`    | `str`       | 目标 `ActivityMessage` 的标识符                                 |
| `activity_type` | `str`       | 与最近一次快照一致的活动判别字段                                |
| `patch`         | `List[Any]` | 应用到结构化活动内容上的 JSON Patch 操作                        |

## 特殊事件 {#special-events}

### RawEvent {#rawevent}

`from ag_ui.core import RawEvent`

用于透传来自外部系统的事件。

```python
class RawEvent(BaseEvent):
    type: Literal[EventType.RAW]
    event: Any
    source: Optional[str] = None
```

| 属性     | 类型            | 描述             |
| -------- | --------------- | ---------------- |
| `event`  | `Any`           | 原始事件数据     |
| `source` | `Optional[str]` | 事件的来源       |

### CustomEvent {#customevent}

`from ag_ui.core import CustomEvent`

用于应用特定的自定义事件。

```python
class CustomEvent(BaseEvent):
    type: Literal[EventType.CUSTOM]
    name: str
    value: Any
```

| 属性    | 类型  | 描述                     |
| ------- | ----- | ------------------------ |
| `name`  | `str` | 自定义事件的名称         |
| `value` | `Any` | 与该事件关联的值         |

## 推理事件 {#reasoning-events}

这些事件表示智能体内推理/思考过程的生命周期。推理事件使智能体
能够将其内部思考过程暴露给前端，创建以 `"reasoning"` 角色
持久保存在消息历史中的 `ReasoningMessage` 对象。

### ReasoningStartEvent {#reasoningstartevent}

`from ag_ui.core import ReasoningStartEvent`

表示一个推理阶段的开始。这是一个透传事件，会通知订阅者
但不会创建消息。

```python
class ReasoningStartEvent(BaseEvent):
    type: Literal[EventType.REASONING_START]
    message_id: str
```

| 属性         | 类型  | 描述                    |
| ------------ | ----- | ----------------------- |
| `message_id` | `str` | 推理阶段的标识符        |

### ReasoningMessageStartEvent {#reasoningmessagestartevent}

`from ag_ui.core import ReasoningMessageStartEvent`

表示一条推理消息的开始。会在消息历史中创建一条新的 `ReasoningMessage`。

```python
class ReasoningMessageStartEvent(BaseEvent):
    type: Literal[EventType.REASONING_MESSAGE_START]
    message_id: str
    role: Literal["reasoning"]
```

| 属性         | 类型                   | 描述                  |
| ------------ | ---------------------- | --------------------- |
| `message_id` | `str`                  | 消息的唯一标识符      |
| `role`       | `Literal["reasoning"]` | 角色始终为 "reasoning" |

### ReasoningMessageContentEvent {#reasoningmessagecontentevent}

`from ag_ui.core import ReasoningMessageContentEvent`

表示流式推理消息中的一块内容。

```python
class ReasoningMessageContentEvent(BaseEvent):
    type: Literal[EventType.REASONING_MESSAGE_CONTENT]
    message_id: str
    delta: str
```

| 属性         | 类型  | 描述                                           |
| ------------ | ----- | ---------------------------------------------- |
| `message_id` | `str` | 与 ReasoningMessageStartEvent 中的 ID 匹配     |
| `delta`      | `str` | 推理内容块                                     |

### ReasoningMessageEndEvent {#reasoningmessageendevent}

`from ag_ui.core import ReasoningMessageEndEvent`

表示一条推理消息的结束。

```python
class ReasoningMessageEndEvent(BaseEvent):
    type: Literal[EventType.REASONING_MESSAGE_END]
    message_id: str
```

| 属性         | 类型  | 描述                                           |
| ------------ | ----- | ---------------------------------------------- |
| `message_id` | `str` | 与 ReasoningMessageStartEvent 中的 ID 匹配     |

### ReasoningMessageChunkEvent {#reasoningmessagechunkevent}

`from ag_ui.core import ReasoningMessageChunkEvent`

便捷事件，用于在无需手动发出
`ReasoningMessageStart`/`ReasoningMessageEnd` 的情况下构建完整的推理消息。

```python
class ReasoningMessageChunkEvent(BaseEvent):
    type: Literal[EventType.REASONING_MESSAGE_CHUNK]
    message_id: Optional[str] = None  # required on first chunk for a message
    delta: Optional[str] = None
```

行为

- 便捷性：某些消费方（例如 JS/TS 客户端）会自动把块事件展开为
  标准的 start/content/end 序列。
- 首块要求：某条消息的第一个块必须包含
  `message_id`。
- 流式传输：具有相同 `message_id` 的后续块对应内容
  片段；在会执行展开的客户端中，完成会触发一个隐式的结束。

### ReasoningEndEvent {#reasoningendevent}

`from ag_ui.core import ReasoningEndEvent`

表示一个推理阶段的结束。这是一个透传事件，会通知
订阅者但不会修改消息。

```python
class ReasoningEndEvent(BaseEvent):
    type: Literal[EventType.REASONING_END]
    message_id: str
```

| 属性         | 类型  | 描述                    |
| ------------ | ----- | ----------------------- |
| `message_id` | `str` | 推理阶段的标识符        |

### ReasoningEncryptedValueEvent {#reasoningencryptedvalueevent}

`from ag_ui.core import ReasoningEncryptedValueEvent`

将加密值附加到消息或工具调用上。发出该事件时，
它会按 `entity_id` 找到所引用的实体，并设置其
`encrypted_value` 字段。

```python
ReasoningEncryptedValueSubtype = Literal["tool-call", "message"]

class ReasoningEncryptedValueEvent(BaseEvent):
    type: Literal[EventType.REASONING_ENCRYPTED_VALUE]
    subtype: ReasoningEncryptedValueSubtype
    entity_id: str
    encrypted_value: str
```

| 属性              | 类型                             | 描述                                       |
| ----------------- | -------------------------------- | ------------------------------------------ |
| `subtype`         | `ReasoningEncryptedValueSubtype` | 该值所属实体的类型                         |
| `entity_id`       | `str`                            | 要附加该值的工具调用或消息的 ID            |
| `encrypted_value` | `str`                            | 要附加到该实体上的加密值                   |

## 子智能体事件 {#subagent-events}

这些事件报告智能体已将工作委派给子智能体，从而使前端
能够把输出归属到产生它的子智能体。归属本身则以可选的
`subagent_run_id` 的形式出现在大多数其他事件类型上。

`subagent_run_id` 标识的是**一次调用**，而非可复用的子智能体
定义 — 同一个子智能体运行两次会得到两个不同的值。完整
模型参见[子智能体](../../../concepts/subagents.md)。

Python 中的字段名为 snake_case，在线性化到线上格式时转为 camelCase，
因此 `subagent_run_id` 在 JSON 中表现为 `subagentRunId`。

### SubagentStartedEvent {#subagentstartedevent}

`from ag_ui.core import SubagentStartedEvent`

宣告一次新的子智能体调用，并为其命名以供展示。

```python
class SubagentStartedEvent(BaseEvent):
    type: Literal[EventType.SUBAGENT_STARTED]
    subagent_run_id: str
    name: str
    description: Optional[str] = None
    parent_subagent_run_id: Optional[str] = None
    parent_tool_call_id: Optional[str] = None
    parent_message_id: Optional[str] = None
```

| 属性                     | 类型  | 描述                            |
| ------------------------ | ----- | ------------------------------- |
| `subagent_run_id`        | `str` | 该次调用的不透明标识符          |
| `name`                   | `str` | 声明的子智能体名称或类型，用于展示 |
| `description`            | `str` | 可选的描述                      |
| `parent_subagent_run_id` | `str` | 嵌套时表示可选的外层子智能体    |
| `parent_tool_call_id`    | `str` | 生成该子智能体的可选工具调用    |
| `parent_message_id`      | `str` | 持有该工具调用的可选消息        |

### SubagentFinishedEvent {#subagentfinishedevent}

`from ag_ui.core import SubagentFinishedEvent`

将一次子智能体调用标记为完成。

```python
class SubagentFinishedEvent(BaseEvent):
    type: Literal[EventType.SUBAGENT_FINISHED]
    subagent_run_id: str
    result: Optional[Any] = None
    outcome: Optional[SubagentFinishedOutcome] = None
```

| 属性              | 类型                                 | 描述                                                   |
| ----------------- | ------------------------------------ | ------------------------------------------------------ |
| `subagent_run_id` | `str`                                | 与 `SubagentStartedEvent` 中的 id 一致                 |
| `result`          | `Any`                                | 可选载荷，对应 `RunFinishedEvent.result`               |
| `outcome`         | `Optional[SubagentFinishedOutcome]`  | `SubagentFinishedSuccessOutcome` 与 `SubagentFinishedSuspendedOutcome`（带可选 `interrupt_ids`）的判别联合；`None` 表示成功（旧有读法）。suspended 表示该子智能体已做检查点，正等待外部输入；`interrupt_ids` 指明哪些运行级中断的应答可以恢复它。 |

### SubagentErrorEvent {#subagenterrorevent}

`from ag_ui.core import SubagentErrorEvent`

将一次子智能体调用标记为失败。

```python
class SubagentErrorEvent(BaseEvent):
    type: Literal[EventType.SUBAGENT_ERROR]
    subagent_run_id: str
    message: str
    code: Optional[str] = None
```

| 属性              | 类型  | 描述                                       |
| ----------------- | ----- | ------------------------------------------ |
| `subagent_run_id` | `str` | 与 `SubagentStartedEvent` 中的 id 一致     |
| `message`         | `str` | 人类可读的错误消息                         |
| `code`            | `str` | 可选的错误码                               |

### 其他事件上的归属 {#attribution-on-other-events}

大多数事件类型接受一个可选的 `subagent_run_id`。不带它的事件
属于父智能体，因此从不设置该字段的事件流与子智能体出现之前的行为
完全一致。

`RunStartedEvent`、`RunFinishedEvent` 和 `RunErrorEvent` 不可归属 —
它们描述的是整个运行。`MessagesSnapshotEvent` 则按消息分别携带归属
信息。

`StateSnapshotEvent` 和 `StateDeltaEvent` 可归属，但其上的归属是来源
标记而非所有权 — 它记录的是哪个子智能体产生了该更新。状态始终
以运行为范围，因此带归属的快照或增量与不带归属的一样，都会应用到
该运行唯一的状态文档上。

## 已弃用的事件 {#deprecated-events}

!!! warning
    `THINKING_*` 事件已弃用，将在 1.0.0 版本中移除。
      新实现应改用 `REASONING_*` 事件。

### Thinking 事件（已弃用） {#thinking-events-deprecated}

以下事件类型已弃用：

| 已弃用的事件                    | 替代方案                    |
| ------------------------------- | --------------------------- |
| `THINKING_START`                | `REASONING_START`           |
| `THINKING_END`                  | `REASONING_END`             |
| `THINKING_TEXT_MESSAGE_START`   | `REASONING_MESSAGE_START`   |
| `THINKING_TEXT_MESSAGE_CONTENT` | `REASONING_MESSAGE_CONTENT` |
| `THINKING_TEXT_MESSAGE_END`     | `REASONING_MESSAGE_END`     |

详细的迁移指引见[推理迁移](../../../concepts/reasoning.md#migration-from-thinking-events)。

## 事件判别 {#event-discrimination}

`from ag_ui.core import Event`

SDK 使用 Pydantic 的判别联合来校验事件：

```python
Event = Annotated[
    Union[
        TextMessageStartEvent,
        TextMessageContentEvent,
        TextMessageEndEvent,
        ToolCallStartEvent,
        ToolCallArgsEvent,
        ToolCallEndEvent,
        ToolCallResultEvent,
        StateSnapshotEvent,
        StateDeltaEvent,
        MessagesSnapshotEvent,
        ActivitySnapshotEvent,
        ActivityDeltaEvent,
        RawEvent,
        CustomEvent,
        RunStartedEvent,
        RunFinishedEvent,
        RunErrorEvent,
        StepStartedEvent,
        StepFinishedEvent,
        ReasoningStartEvent,
        ReasoningMessageStartEvent,
        ReasoningMessageContentEvent,
        ReasoningMessageEndEvent,
        ReasoningMessageChunkEvent,
        ReasoningEndEvent,
        ReasoningEncryptedValueEvent,
    ],
    Field(discriminator="type")
]
```

这支持在运行时校验事件，并在开发期进行类型检查。

### TextMessageChunkEvent {#textmessagechunkevent}

便捷事件，用于在无需手动发出
`TextMessageStart`/`TextMessageEnd` 的情况下构建完整的文本消息。

```python
from ag_ui.core import TextMessageChunkEvent

class TextMessageChunkEvent(BaseEvent):
    type: Literal[EventType.TEXT_MESSAGE_CHUNK]
    message_id: Optional[str] = None  # required on first chunk for a message
    role: Optional[TextMessageRole] = None  # defaults to "assistant" in JS client
    delta: Optional[str] = None
```

行为

- 便捷性：某些消费方（例如 JS/TS 客户端）会自动把块事件展开为
  标准的 start/content/end 序列，使生产方在使用块时可以省略显式的
  start/end 事件。
- 首块要求：某条消息的第一个块必须包含
  `message_id`。
- 流式传输：具有相同 `message_id` 的后续块对应内容
  片段；在会执行展开的客户端中，完成会触发一个隐式的结束。

### ToolCallChunkEvent {#toolcallchunkevent}

便捷事件，用于在无需手动发出
`ToolCallStart`/`ToolCallEnd` 的情况下发起工具调用。

```python
from ag_ui.core import ToolCallChunkEvent

class ToolCallChunkEvent(BaseEvent):
    type: Literal[EventType.TOOL_CALL_CHUNK]
    tool_call_id: Optional[str] = None      # required on first chunk
    tool_call_name: Optional[str] = None    # required on first chunk
    parent_message_id: Optional[str] = None
    delta: Optional[str] = None
```

行为

- 便捷性：消费方可以把块序列展开为标准的
  start/args/end 三元组（JS/TS 客户端会自动执行此操作）。
- 首块要求：在第一个块上同时包含 `tool_call_id` 和 `tool_call_name`。
- 流式传输：具有相同 `tool_call_id` 的后续块对应参数
  片段；在会执行展开的客户端中，完成会触发一个隐式的结束。
