---
title: "类型"
description:
  "Agent User Interaction Protocol Python SDK 中使用的核心类型文档"
---
<em class="lead">Agent User Interaction Protocol Python SDK 中使用的核心类型文档</em>

# 核心类型 {#core-types}

Agent User Interaction Protocol Python SDK 建立在一组核心类型之上，
这些类型表示整个系统中使用的基础结构。本页记录这些类型及其属性。

## RunAgentInput {#runagentinput}

`from ag_ui.core import RunAgentInput`

运行智能体的输入参数。在 HTTP API 中，它是 `POST` 请求的请求体。

`tools` 包含客户端为本次运行提供的工具。后端定义的工具应保留在后端智能体或
框架配置中，并且可以通过智能体能力单独公布。

```python
class RunAgentInput(ConfiguredBaseModel):
    thread_id: str
    run_id: str
    parent_run_id: Optional[str] = None
    state: Any = None  # optional: absent means "no state"; a bare null reads as absent
    messages: List[Message]
    tools: List[Tool]
    context: List[Context]
    forwarded_props: Any
    resume: Optional[List[ResumeEntry]] = None
```

| 属性              | 类型                          | 说明                                                                                                |
| ----------------- | ----------------------------- | --------------------------------------------------------------------------------------------------- |
| `thread_id`       | `str`                         | 会话线程的 ID                                                                       |
| `run_id`          | `str`                         | 当前运行的 ID                                                                               |
| `parent_run_id`   | `Optional[str]`               | （可选）生成此运行的那次运行的 ID                                                      |
| `state`           | `Any`                         | （可选）智能体的当前状态；缺失表示“无状态”，裸 `null` 也会被读作缺失 |
| `messages`        | `List[Message]`               | 会话中的消息列表                                                                |
| `tools`           | `List[Tool]`                  | 客户端提供的、本次运行可用的工具                                                        |
| `context`         | `List[Context]`               | 提供给智能体的上下文对象列表                                                       |
| `forwarded_props` | `Any`                         | 转发给智能体的附加属性                                                        |
| `resume`          | `Optional[List[ResumeEntry]]` | 针对每个中断的响应，用于恢复以中断结果结束的运行                      |

## ResumeEntry {#resumeentry}

`from ag_ui.core import ResumeEntry`

`RunAgentInput.resume` 内部针对单个中断的响应，回应上一次运行中的
一个中断。完整的恢复契约见
[中断](../../../concepts/interrupts.md#resuming-a-run)。

```python
class ResumeEntry(GeneratedBaseModel):
    interrupt_id: str
    status: ResumeStatus  # "resolved" | "cancelled"
    payload: Optional[Any] = None
    metadata: Optional[Metadata] = None
```

| 属性           | 类型                       | 说明                                                                                  |
| -------------- | -------------------------- | ------------------------------------------------------------------------------------- |
| `interrupt_id` | `str`                      | 此条目所回应的中断的 ID                                              |
| `status`       | `ResumeStatus`             | 若用户已响应则为 `"resolved"`，若用户放弃则为 `"cancelled"`                   |
| `payload`      | `Optional[Any]`            | 响应本身，会依据该中断的 `response_schema` 进行校验              |
| `metadata`     | `Optional[Dict[str, Any]]` | 关于该响应的信封数据 — 签名、路由键 — 绝非答案本身 |

`metadata` 遵循协议中其他各处元数据的同一约定：按 key 开放，一个 key 下允许
任意 JSON 值（包括 `None`），对象本身可以缺失或是一个映射，但在线上绝不出现
`null`，且 `ag-ui` key 为保留键。resume 条目是一个请求字段，因此不会有任何
内容合并进它；见[元数据](../../../concepts/metadata.md#resume-entries)。

## 消息类型 {#message-types}

SDK 包含若干消息类型，表示系统中不同类型的消息。

!!! note
    每种消息类型都携带一个可选的 `metadata` 对象（`Optional[Dict[str,
      Any]]`），`ToolCall` 也是如此。为简洁起见，下文各类型的表格
      都省略了它们。它按 key 开放 — 一个 key 下允许任意 JSON 值，
      包括 `None` — 且对象本身可以缺失，但绝不是 `None`。
      `ag-ui` key 保留给 AG-UI 自身使用。元数据会在消息由其事件
      构建的过程中累积，工具调用事件则累积到工具调用本身之上；
      合并规则见[元数据](../../../concepts/metadata.md)。

### Role {#role}

`from ag_ui.core import Role`

表示消息发送者可能具有的角色。

```python
Role = Literal["developer", "system", "assistant", "user", "tool", "activity", "reasoning"]
```

### DeveloperMessage {#developermessage}

`from ag_ui.core import DeveloperMessage`

表示来自开发者的消息。

```python
class DeveloperMessage(BaseMessage):
    role: Literal["developer"]
    content: str
```

| 属性      | 类型                   | 说明                                             |
| --------- | ---------------------- | ------------------------------------------------ |
| `id`      | `str`                  | 消息的唯一标识符                |
| `role`    | `Literal["developer"]` | 消息发送者的角色，固定为 "developer" |
| `content` | `str`                  | 消息的文本内容（必填）           |
| `name`    | `Optional[str]`        | 发送者的可选名称                      |

### SystemMessage {#systemmessage}

`from ag_ui.core import SystemMessage`

表示系统消息。

```python
class SystemMessage(BaseMessage):
    role: Literal["system"]
    content: str
```

| 属性      | 类型                | 说明                                          |
| --------- | ------------------- | --------------------------------------------- |
| `id`      | `str`               | 消息的唯一标识符             |
| `role`    | `Literal["system"]` | 消息发送者的角色，固定为 "system" |
| `content` | `str`               | 消息的文本内容（必填）        |
| `name`    | `Optional[str]`     | 发送者的可选名称                   |

### AssistantMessage {#assistantmessage}

`from ag_ui.core import AssistantMessage`

表示来自助手的消息。

```python
class AssistantMessage(BaseMessage):
    role: Literal["assistant"]
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
```

| 属性         | 类型                       | 说明                                             |
| ------------ | -------------------------- | ------------------------------------------------ |
| `id`         | `str`                      | 消息的唯一标识符                |
| `role`       | `Literal["assistant"]`     | 消息发送者的角色，固定为 "assistant" |
| `content`    | `Optional[str]`            | 消息的文本内容                      |
| `name`       | `Optional[str]`            | 发送者的名称                               |
| `tool_calls` | `Optional[List[ToolCall]]` | 此消息中发起的工具调用                  |

### UserMessage {#usermessage}

`from ag_ui.core import UserMessage`

表示来自用户的消息。

```python
class UserMessage(BaseMessage):
    role: Literal["user"]
    content: Union[str, List["ContentPart"]]
```

| 属性      | 类型                              | 说明                                                                  |
| --------- | --------------------------------- | --------------------------------------------------------------------- |
| `id`      | `str`                             | 消息的唯一标识符                                     |
| `role`    | `Literal["user"]`                 | 消息发送者的角色，固定为 "user"                           |
| `content` | `Union[str, List["ContentPart"]]` | 纯文本字符串，或由多模态片段构成的有序列表 |
| `name`    | `Optional[str]`                   | 发送者的可选名称                                           |

### PartSource {#partsource}

表示非文本部件如何提供。

```python
PartSource = Annotated[
    Union[DataSource, UrlSource, FileSource],
    Field(discriminator="type"),
]

class DataSource(ConfiguredBaseModel):
    type: Literal["data"]
    value: str
    mime_type: str

class UrlSource(ConfiguredBaseModel):
    type: Literal["url"]
    value: str
    mime_type: Optional[str] = None

class FileSource(ConfiguredBaseModel):
    type: Literal["file"]
    value: str  # the handle, exactly as the provider issued it
    provider: Optional[str] = None  # who issued it, e.g. "openai", "anthropic", "google"
    mime_type: Optional[str] = None
```

`FileSource` 指向已存在于模型提供方处的字节 — 一个 OpenAI 或 Anthropic
文件 id、一个 Gemini 文件 URI。不会去获取任何内容，且 `value` 是不透明的：
智能体要么把它交给自己的提供方，要么丢弃该部件，而绝不把它当作 URL。

### TextPart {#textpart}

表示用户消息或工具结果内部的文本部件。

```python
class TextPart(ConfiguredBaseModel):
    type: Literal["text"]
    id: Optional[str] = None
    text: str
    metadata: Optional[Any] = None
```

| 属性       | 类型              | 说明                                                                      |
| ---------- | ----------------- | ------------------------------------------------------------------------- |
| `type`     | `Literal["text"]` | 标识部件类型                                                  |
| `id`       | `Optional[str]`   | 在其消息内标识该部件                                    |
| `text`     | `str`             | 文本内容                                                              |
| `metadata` | `Optional[Any]`   | 关于该部件的额外信息，例如某个搜索命中的来源和标题 |

### BinaryInputContent {#binaryinputcontent}

表示图像、音频或文件等二进制数据。

```python
class BinaryInputContent(ConfiguredBaseModel):
    type: Literal["binary"]
    mime_type: str
    id: Optional[str] = None
    url: Optional[str] = None
    data: Optional[str] = None
    filename: Optional[str] = None
```

| 属性        | 类型                | 说明                                          |
| ----------- | ------------------- | --------------------------------------------- |
| `type`      | `Literal["binary"]` | 标识片段类型                  |
| `mime_type` | `str`               | MIME 类型，例如 `"image/png"`          |
| `id`        | `Optional[str]`     | 对先前上传内容的引用      |
| `url`       | `Optional[str]`     | 可获取该内容的远程 URL |
| `data`      | `Optional[str]`     | Base64 编码的内容                        |
| `filename`  | `Optional[str]`     | 可选的文件名提示                        |

> **校验：** `id`、`url` 或 `data` 中必须至少提供一个。
>
> **已弃用：** `BinaryInputContent` 仍作为临时的
> 兼容模型提供。优先使用下文中特定模态的部件。

### ImagePart / AudioPart / VideoPart / DocumentPart {#imagepart--audiopart--videopart--documentpart}

```python
class ImagePart(ConfiguredBaseModel):
    type: Literal["image"]
    id: Optional[str] = None
    source: PartSource
    metadata: Optional[Any] = None

class AudioPart(ConfiguredBaseModel):
    type: Literal["audio"]
    id: Optional[str] = None
    source: PartSource
    metadata: Optional[Any] = None

class VideoPart(ConfiguredBaseModel):
    type: Literal["video"]
    id: Optional[str] = None
    source: PartSource
    metadata: Optional[Any] = None

class DocumentPart(ConfiguredBaseModel):
    type: Literal["document"]
    id: Optional[str] = None
    source: PartSource
    metadata: Optional[Any] = None
```

### ToolMessage {#toolmessage}

`from ag_ui.core import ToolMessage`

表示来自工具的消息。

```python
class ToolMessage(ConfiguredBaseModel):
    id: str
    role: Literal["tool"]
    content: Union[str, List[ContentPart]]
    tool_call_id: str
    error: Optional[str] = None
    encrypted_value: Optional[str] = None
```

| 属性              | 类型              | 说明                                            |
| ----------------- | ----------------- | ----------------------------------------------- |
| `id`              | `str`             | 消息的唯一标识符               |
| `content`         | `str`             | 消息的文本内容                     |
| `role`            | `Literal["tool"]` | 消息发送者的角色，固定为 "tool"     |
| `tool_call_id`    | `str`             | 此消息所回应的工具调用的 ID    |
| `error`           | `Optional[str]`   | 工具调用失败时的错误消息           |
| `encrypted_value` | `Optional[str]`   | 通过签名附加的可选加密值 |

### ActivityMessage {#activitymessage}

`from ag_ui.core import ActivityMessage`

表示在聊天消息之间发出的结构化活动进度。

```python
class ActivityMessage(ConfiguredBaseModel):
    id: str
    role: Literal["activity"]
    activity_type: str
    content: Dict[str, Any]
```

| 属性            | 类型                  | 说明                                                    |
| --------------- | --------------------- | ------------------------------------------------------- |
| `id`            | `str`                 | 活动消息的唯一标识符              |
| `role`          | `Literal["activity"]` | 固定判别字段，将消息标识为活动 |
| `activity_type` | `str`                 | 用于渲染器选择的活动判别字段      |
| `content`       | `Dict[str, Any]`      | 表示活动状态的结构化载荷      |

### ReasoningMessage {#reasoningmessage}

`from ag_ui.core import ReasoningMessage`

表示来自智能体内部思考过程的推理/思维消息。

```python
class ReasoningMessage(ConfiguredBaseModel):
    id: str
    role: Literal["reasoning"]
    content: str
    encrypted_value: Optional[str] = None
```

| 属性              | 类型                   | 说明                                               |
| ----------------- | ---------------------- | -------------------------------------------------- |
| `id`              | `str`                  | 推理消息的唯一标识符        |
| `role`            | `Literal["reasoning"]` | 固定判别字段，标识推理角色 |
| `content`         | `str`                  | 推理/思维内容                     |
| `encrypted_value` | `Optional[str]`        | 通过签名附加的可选加密值    |

### Message {#message}

`from ag_ui.core import Message`

表示系统中任意类型消息的联合类型。

```python
Message = Annotated[
    Union[
        DeveloperMessage,
        SystemMessage,
        AssistantMessage,
        UserMessage,
        ToolMessage,
        ActivityMessage,
        ReasoningMessage,
    ],
    Field(discriminator="role")
]
```

### ToolCall {#toolcall}

`from ag_ui.core import ToolCall`

表示智能体发起的工具调用。

```python
class ToolCall(ConfiguredBaseModel):
    id: str
    type: Literal["function"]
    function: FunctionCall
    encrypted_value: Optional[str] = None
```

| 属性              | 类型                  | 说明                                            |
| ----------------- | --------------------- | ----------------------------------------------- |
| `id`              | `str`                 | 工具调用的唯一标识符             |
| `type`            | `Literal["function"]` | 工具调用的类型，始终为 "function"        |
| `function`        | `FunctionCall`        | 关于被调用函数的详细信息         |
| `encrypted_value` | `Optional[str]`       | 通过签名附加的可选加密值 |

#### FunctionCall {#functioncall}

`from ag_ui.core import FunctionCall`

表示工具调用中的函数名与参数。

```python
class FunctionCall(ConfiguredBaseModel):
    name: str
    arguments: str
```

| 属性        | 类型  | 说明                                             |
| ----------- | ----- | ------------------------------------------------ |
| `name`      | `str` | 要调用的函数名                     |
| `arguments` | `str` | 传给函数的 JSON 编码参数字符串 |

## Context {#context}

`from ag_ui.core import Context`

表示提供给智能体的一条上下文信息。

```python
class Context(ConfiguredBaseModel):
    description: str
    value: str
```

| 属性          | 类型  | 说明                                        |
| ------------- | ----- | ------------------------------------------- |
| `description` | `str` | 关于此上下文表示什么的描述 |
| `value`       | `str` | 实际的上下文值                    |

## Tool {#tool}

`from ag_ui.core import Tool`

定义一个可由智能体调用的工具。

```python
class Tool(ConfiguredBaseModel):
    name: str
    description: str
    parameters: Any  # JSON Schema
```

| 属性          | 类型  | 说明                                             |
| ------------- | ----- | ------------------------------------------------ |
| `name`        | `str` | 工具名称                                 |
| `description` | `str` | 工具功能的描述                |
| `parameters`  | `Any` | 定义工具参数的 JSON Schema |

## State {#state}

`from ag_ui.core import State`

表示智能体在执行期间的状态。

```python
State = Any
```

状态类型是灵活的，可以保存智能体实现所需的任何数据结构。
