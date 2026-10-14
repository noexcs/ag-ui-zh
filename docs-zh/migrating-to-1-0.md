---
title: "迁移到 1.0"
description: "应用或集成迁移到 AG-UI 1.0 时按 SDK 划分的变化——以及不变的部分"
---
<em class="lead">应用或集成迁移到 AG-UI 1.0 时按 SDK 划分的变化——以及不变的部分</em>

AG-UI 1.0 是第一个背后有规范支撑的版本：[schema](./1.0/schema.md) 是唯一事实来源，每个 SDK 的协议类型都由它生成，过去只存在于 TypeScript 客户端中的行为规则也已[记录成文](./1.0/index.md)。发生变化的大部分内容是增量的。本页讲的是非增量的那部分——每个 SDK 中你必须改动的地方，以及能自行继续工作的部分。

协议层面的变化列在规范的 [主要变更](./1.0/changelog.md) 中；本页不重复它们，只说明每项变化对你已有代码意味着什么。

## 继续可用的部分 {#what-keeps-working}

**0.x 的智能体可以继续对 1.0 客户端工作。** TypeScript 客户端带有一个始终开启的兼容边界，会翻译它在传入事件流中遇到的已弃用形态——五个 `THINKING_*` 事件转换为其 `REASONING_*` 对应事件，遗留的 `binary` 内容部分变为以其媒体类型命名的媒体部分，历史上被接受的整字段可选 `null` 在验证前变为字段缺失。每一次入站翻译都会发出警告。这些兼容垫片连同其替代方案与失效日期记录在 [`DEPRECATIONS.md`](https://github.com/ag-ui-protocol/ag-ui/blob/main/DEPRECATIONS.md) 中。其失效日期是临时的——自每个垫片编写起十二个月，若 1.0 发布推迟则在发布时重新计时——此后这些已弃用形态将彻底停止工作。

**1.0 的智能体可以继续对 0.x 客户端工作。** 1.0 新增的一切——`RUN_FINISHED.outcome`、子智能体事件、`protocolVersion`、活动事件——要么是可选的，要么是新的事件类型，而版本字段之前就存在的客户端会忽略它不认识的内容。

**线上格式相同。** 基于 SSE 的 JSON 与 protobuf 传输绑定在分帧上未变。你今天发送的字段名就是 1.0 读取的字段名，例外见本页。

---

## 生产方：声明你的版本 {#producers-declare-your-version}

1.0 生产方 MUST 在 `RUN_STARTED` 上声明其所使用的协议版本（[版本与兼容性](./1.0/basic/versioning.md)）。该字段在 schema 中是可选的，因为它的缺失正是识别 1.0 之前生产方的方式。这意味着当你自己构造事件时，没有任何 SDK 会替你添加它。使用 SDK 的常量，绝不要手写字符串，也绝不要回显 `RunAgentInput.protocolVersion` 中的版本：该声明陈述的是生产方自身的版本。

**Python：** 构造事件时传入 `protocol_version`。

```python
from ag_ui.core import PROTOCOL_VERSION, RunStartedEvent

RunStartedEvent(
    thread_id=input.thread_id,
    run_id=input.run_id,
    protocol_version=PROTOCOL_VERSION,
)
```

**TypeScript：** 在 `RUN_STARTED` 对象上设置 `protocolVersion`。

```ts
import { EventType, PROTOCOL_VERSION, type RunStartedEvent } from "@ag-ui/core";

const runStarted: RunStartedEvent = {
  type: EventType.RUN_STARTED,
  threadId: input.threadId,
  runId: input.runId,
  protocolVersion: PROTOCOL_VERSION,
};
```

**.NET：** `AGUI.Server` 在转换 `ChatResponseUpdate` 流时会为你构造 `RUN_STARTED`，该事件携带 `AGUIProtocol.Version`。无需额外添加。如果你自己发出 `RunStartedEvent`（作为 update 的 `RawRepresentation`），它会原样透传，因此需要自行设置该字段：

```csharp
new RunStartedEvent
{
    ThreadId = threadId,
    RunId = runId,
    ProtocolVersion = AGUIProtocol.Version,
};
```

**中间件与代理**在透传生产方的 `RUN_STARTED` 时 MUST 保持其 `protocolVersion` 不变。不要添加、覆写或移除它。该声明命名的是事件流所讲的内容，因此转发方报告的是原始生产方的版本。只有将事件流翻译为不同版本的层才声明它自己发出的版本。

---

## TypeScript {#typescript}

三个 SDK 中 TypeScript SDK 的改动最大，因为协议的行为此前正是在这里定义的。

### 省略整字段的可选 null {#omit-whole-optional-null-fields}

可选协议字段 MUST 缺失而不是为 `null`，包括 `rawEvent`、`RUN_FINISHED.result` 和 `forwardedProps`。`EventEncoder` 与出站 HTTP 输入会在传输前省略这些字段。内存中的智能体也要发出规范形态。

对于一组固定的整字段可选 `null`，较旧的生产方仍然兼容。在验证之前，客户端会将每个此类字段转换为字段缺失，并针对任意事件上的 `rawEvent` 和 `subagentRunId`、`RUN_STARTED.parentRunId`、`RUN_STARTED.input`、`RUN_FINISHED.result`、`RUN_FINISHED.outcome.pendingToolCallIds`、`RUN_FINISHED.usage[]` 中的 `provider`、`reasoningTokens`、`cachedInputTokens` 和 `cacheWriteInputTokens`、`RUN_ERROR.usage`、`SUBAGENT_FINISHED.result`、`TOOL_CALL_RESULT.role`、resume 条目的 `payload`、媒体部分的 `metadata`（`image`、`audio`、`video`、`document`）、工具的 `parameters` 以及 `RunAgentInput.forwardedProps`，每个字段每次运行警告一次。这适用于内存中的运行、重连、SSE 和 protobuf，包括事件中内嵌的消息与输入回显。订阅者收到的是规范化后的事件：例如旧的 `RUN_FINISHED.result: null` 会变为结果缺失。这是客户端的宽容，而非协议变更：生产方仍 MUST 省略这些字段。

直接 schema 验证仍然严格，且不会调用客户端的事件兼容边界。接受较旧 `RunAgentInput` 值的请求处理器 MUST 在调用 `RunAgentInputSchema.parse` 之前，在本地省略历史上被接受的可选 null：`forwardedProps`、`tools[].parameters`、`resume[].payload`，以及 `messages[].content[]` 中 image/audio/video/document 部分的 `metadata`。不要递归剥离应用数据中的 null，也不要移除已经拒绝过 null 的字段中的 null。CopilotKit 共享的 run/connect 请求解析器将其作为本地兼容例外处理；AG-UI 不暴露公开的请求规范化辅助函数。现有的 `RunAgentInput.state: null` 解析器宽容行为仍产生 `undefined`。

此兼容性仅限于上面列出的字段。事件或消息的 `metadata: null` 仍然无效，其他可选 null 如 `TEXT_MESSAGE_START.name`、`RUN_ERROR.code`、`usage[].model`、`RunAgentInput.parentRunId`，以及嵌套在消息中的 `subagentRunId: null` 也同样无效。必需的 JSON 载荷（如 `CUSTOM.value`）以及 state、metadata 或其他应用数据中的 null 值仍然有效并被保留。

### zod 是 `@ag-ui/core` 的可选对等依赖 {#zod-is-an-optional-peer-dependency-of-aguicore}

`@ag-ui/core` 的主入口只有类型与常量，从不加载 zod。验证器位于子路径上，导入它们需要 zod（`3.25.18` 或更新，或任意 `4.x`）：

```ts
// before
import { EventSchemas, UserMessageSchema, EventType } from "@ag-ui/core";

// after
import { EventType } from "@ag-ui/core";
import { EventSchemas, UserMessageSchema } from "@ag-ui/core/schemas";
```

```bash
npm install @ag-ui/core          # types only — nothing else to install
npm install @ag-ui/core zod      # if you use the validators
```

每个验证器都迁移了，包括历史别名（`EventSchemas`、`*InputPartSchema` 名称、`OptionalMetadataSchema`）以及能力 schema。`@ag-ui/client` 也不再重新导出它们——它重新导出 core 的主入口，而它们不在其中。`@ag-ui/client` 自身仍依赖 zod，因为其强制执行阶段用它做验证；客户端的安装方式没有变化。

### 未知内容不再进入你的代码 {#unknown-material-no-longer-reaches-your-code}

客户端在中间件之后、所有路径上都有一个强制执行阶段。类型不被任何东西识别的事件会被丢弃并给出警告。已知事件上的未知属性会被剥离，并给出指明其路径的警告。协议定义的字段上出现*格式错误*的值——字符串位置出现数字——会使运行失败，一如往常。

如果你以前在订阅者中从事件上读取非标准属性，它在订阅者看到之前就已被移除。额外数据的受认可通道是 `metadata`，它在每个事件和消息上按 key 开放，且从不被剥离。

你发送的内容同样如此：`RunAgentInput` 上的未知 key 会在传输前被剥离。为此目的而存在的字段是 `forwardedProps`，它将任意 JSON 原封不动地传给智能体。

### 1.0 中更严格的行为 {#behaviour-that-is-stricter-in-10}

客户端过去宽松执行、或仅在某一条路径上执行的两条规则，现在在所有地方都适用。每条规则都会把某种悄然成功的情况变成失败的运行。

**推理的开启/关闭纪律会被校验。** 指名一个无人开启的消息的 `REASONING_MESSAGE_CONTENT` 或 `REASONING_MESSAGE_END`、未开启就被关闭的推理跨度，以及运行结束时仍处于开启状态的跨度或消息，都会使运行失败。孤立的片段与重复开启在 1.0 之前对 `THINKING_*` 就已被拒绝；在 `RUN_FINISHED` 时因跨度或消息仍处于开启而使运行失败是新增的，与文本消息和工具调用此前的行为一致。跨度与推理消息是彼此独立的命名空间——与 `THINKING_*` 不同，推理消息不必位于某个跨度内，而 `REASONING_START` 的 id 也不会开启一条推理消息。

**强制执行保证在每条路径上都成立。** 未知内容被剥离*并*给出警告，格式错误的已知值则是致命的——现在在装有中间件时以及通过 protobuf 传输绑定时也成立，而不仅限于纯 SSE 路径。过去在这些路径上静默消失的内容——中间件链内展开的块上的无法识别属性、跨 protobuf 解码器的未知消息 role 或 patch 操作——现在会一路传递到强制执行阶段，并在被丢弃处被报告。

**`RUN_ERROR` 未变，这是有意为之。** 生产方发出的 `RUN_ERROR` 是一个格式良好的事件流——智能体如实报告其运行失败并不构成协议违规——因此客户端接受它：事件被投递给 `onRunErrorEvent`，事件流继续，`runAgent()` 正常 resolve，与 0.x 完全一致。`RUN_ERROR` 之后的 `RUN_STARTED` 会在同一事件流中开始新的运行，该运行产生的一切都会被应用。如果你在运行报告自身失败时需要被拒绝的 promise，请从你自己的 `onRunErrorEvent` 订阅者中抛出；客户端不会替你这么做。

### 从公开 API 中移除 {#retired-from-the-public-api}

- 五个 `THINKING_*` 事件——enum 成员、类型、schema、工厂。请发出 `REASONING_*`；传入的 `THINKING_*` 事件流仍由上述边界翻译。
- `BinaryInputContent`（`{ type: "binary" }`）。请使用带 `source` 的媒体部分——`image`、`audio`、`video`、`document`。传入的遗留部分仍会被翻译。
- `@ag-ui/client` 中的 `stripUnknown` 与 `StripResult`。它们是强制执行阶段的内部实现。

### 重命名与类型变更 {#renames-and-type-changes}

- `SubAgentInfo` → `SubagentInfo`，以及 `AgentCapabilities` 上的 `multiAgent.subAgents` → `subagents`。线上 key 随之改变，且没有别名：仍携带 `subAgents` 的声明会将该 key 视为未知。协议在所有地方都把这个词写成一个词（`subagentRunId`）。
- `RunAgentInput.tools` 和 `.context` 在 TypeScript 类型上非可选。线上缺失仍表示空；SDK 将其呈现为 `[]`，因此下游无需做收窄。
- `AbstractAgent.maxVersion` 已弃用，改用 `maxProtocolVersion`。覆写旧名称仍然可用，并在每个进程警告一次。
- 内容部分按其本身而非方向命名：`InputContent` → `ContentPart`、`TextInputContent` → `TextPart`、`ImageInputContent` → `ImagePart`（audio、video、document 同理）、`InputContentSource` → `PartSource`、`InputContentDataSource` → `DataSource`、`InputContentUrlSource` → `UrlSource`，以及与之对应的 `...Schema` 验证器。旧名称作为相同类型与验证器的已弃用别名导出，因此不会破坏任何东西；线上的 `type` 值未变。
- `PartSource` 增加了第三种分支 `FileSource`（`type: "file"`）：模型提供方为其已上传的字节签发的句柄。对 `source.type` 做穷尽 switch 的代码需要为它加一个分支。绝不要将其 `value` 当作 URL；如果你的智能体无法把该句柄交给其提供方，就像对待模型无法接受的其他部分一样，跳过该部分并给出警告。
- `ToolMessage.content` 和 `ToolCallResultEvent.content` 为 `string | ContentPart[]`，与 `UserMessage.content` 此前一致。将工具结果直接传入字符串位置的代码需要先做收窄；来自 `@ag-ui/core` 的 `contentToText()` 给出拼接后的文本部分，`contentHasMedia()` 说明该扁平化是否会丢失内容。遗留的 `ActionExecutionResult` 桥接以这种方式扁平化并给出警告。
- 每个内容部分都有可选的 `id`，`TextPart` 具有媒体部分早已具备的可选 `metadata`。
- capabilities 上的 `execution.maxIterations` 和 `maxExecutionTime` 校验为非负整数且位于 JavaScript 安全范围内。

### 新增，值得了解 {#new-and-worth-knowing}

客户端在每个 `RunAgentInput` 上声明 `protocolVersion: "1.0"`，并在 `RUN_STARTED` 上读取生产方的应答，当生产方使用更新或无法解释的版本时给出警告。将 `maxProtocolVersion` 固定为低于此客户端包自身版本会省略该字段，用于对端解析器会拒绝未知成员的情况。

Protobuf 解码会合并单值消息字段的重复出现，包括嵌套消息、metadata 和运行输入。后出现的标量值胜出，重复列表条目按顺序追加，被省略的字段保留其先前值。TypeScript 与 .NET 遵循相同的 protobuf 合并规则。

---

## Python {#python}

Python SDK 是生产方侧的：它定义智能体发出的形态。改动较小，其中一项会影响任何解析其输出的代码。

### 缺失字段被省略，绝不为 `null` {#absent-fields-are-omitted-never-null}

无值的字段会从 JSON 中省略，而不是写成 `null`。这在 1.0 之前就已发布，位于 `ag-ui-protocol` 0.1.20，因此只有从更早版本升级时它才是迁移步骤——但这是最可能影响任何解析智能体输出的代码的变更。执行 `if payload["parentMessageId"] is None` 或等价判断的读取方需要改为 `"parentMessageId" not in payload`。*作为值*的 `null`——metadata key 之下、状态快照之内、JSON Patch 的 `add` 为 `null`——会被精确保留；只有代表整个缺失字段的 `null` 才会消失。

### 生成的模型取代手写模型 {#generated-models-replace-the-handwritten-ones}

`ag_ui.core` 保留了它导出的每一个名称，除了下面被移除和重命名的那些，现在从生成的源码重新导出，构造方式未变：snake_case 关键字参数，线上使用别名。有三种行为不同：

- 单值字面量（`type`、固定的 `role`）默认取其唯一合法值；你不再需要写出它们。
- 带 schema 默认值的字段（文本消息上的 `role`、patch 上的 `replace`）在缺失时解析为 `None`，而不是实体化的默认值。
- JSON Patch 操作解析为带类型的操作模型。线上形式完全相同。

验证与以往一样宽容：未知 key 会被保留，pydantic 的默认强制转换仍然适用。严格契约是规范的 [fixture 语料库](./1.0/schema-files.md)，而不是 SDK 模型。

### 将 JSON Patch 条目作为对象读取 {#read-json-patch-entries-as-objects}

`StateDeltaEvent.delta` 和 `ActivityDeltaEvent.patch` 中的条目是带类型的操作模型，即使你用字典构造事件也是如此。将 `patch["path"]` 和 `patch.get("op")` 之类的字典读取替换为 `patch.path` 和 `patch.op`。线上发送的 JSON 未变。

如果某个 patch 库或其他现有代码需要字典，用 `model_dump(by_alias=True)` 转换每个操作。保持别名启用可保留 move 和 copy 操作上的 `from` 等线上 key。

```python
from ag_ui.core import StateDeltaEvent

event = StateDeltaEvent(delta=[{"op": "replace", "path": "/count", "value": 1}])
operation = event.delta[0]
assert operation.path == "/count"  # Previously: event.delta[0]["path"]
assert operation.op == "replace"  # Previously: event.delta[0].get("op")

patches = [operation.model_dump(by_alias=True) for operation in event.delta]
assert patches == [{"op": "replace", "path": "/count", "value": 1}]
```

同时支持较旧 SDK 字典与 1.0 模型的适配器可以原样保留字典条目，仅在条目为模型时调用 `model_dump(by_alias=True)`。

### 移除 {#retired}

- `MetadataMixin`，来自 `ag_ui.core`、`ag_ui.core.types` 和 `ag_ui.core.events`。生成的协议模型已携带其 metadata 字段，因此该独立辅助类不再导出。移除该 import；对于继承了它的自定义模型，改为从 `ag_ui.core.types` 继承 `ConfiguredBaseModel` 并声明 `metadata: Optional[Metadata] = None`，从 `typing` 导入 `Optional`，从 `ag_ui.core` 导入 `Metadata`。
- `THINKING_*` 事件。请发出 `REASONING_*`。生产方侧没有兼容垫片；TypeScript 客户端在其一侧翻译旧的事件流。
- 作为*部分*的 `BinaryInputContent`：`ContentPart` 没有 `binary` 成员，携带它的消息会在 `RunAgentInput` 验证时被拒绝。该类本身在 `ag_ui.core` 中仍可导入一个版本周期（见 `DEPRECATIONS.md`），因此针对 0.x 编写的适配器仍能导入，其遗留分支只是永远不会执行；SDK 从不构造它。请使用媒体部分。

### 重命名 {#renamed}

- `SubAgentInfo` → `SubagentInfo`；`MultiAgentCapabilities.sub_agents` → `subagents`（线上 key 为 `subagents`）。`SubAgentInfo` 作为同一类的别名再导出一个版本周期；旧字段与旧线上 key 则不会。
- `ExecutionCapabilities.max_iterations` 和 `max_execution_time` 现在拒绝负值。
- 内容部分按其本身而非方向命名：`InputContent` → `ContentPart`、`TextInputContent` → `TextPart`、`ImageInputContent` → `ImagePart`（audio、video、document 同理）、`InputContentSource` → `PartSource`、`InputContentDataSource` → `DataSource`、`InputContentUrlSource` → `UrlSource`。旧名称仍从 `ag_ui.core` 导出，作为相同类的别名。
- `PartSource` 有第三种分支 `FileSource`（`type="file"`）：模型提供方为其已上传的字节签发的句柄。按 source 类分支的代码需要为它加一个分支。绝不要将其 `value` 当作 URL；如果你的智能体无法把该句柄交给其提供方，就像对待模型无法接受的其他部分一样，跳过该部分并给出警告。
- `ToolMessage.content` 和 `ToolCallResultEvent.content` 为 `Union[str, List[ContentPart]]`，与 `UserMessage.content` 此前一致。把工具结果当作 `str` 处理的代码需要先做收窄。每个部分都有可选的 `id`，`TextPart` 具有媒体部分早已具备的可选 `metadata`。

---

## .NET {#net}

.NET SDK 跨度最大，因为它是最后一个仍在手写协议类型的 SDK，也因为它获得了另外两个早已具备的一项特性。

### 生成的模型取代约 60 个手写类 {#generated-models-replace-60-handwritten-classes}

消费方看到的接口与之前相同，减去 schema 移除的部分：相同的 sealed 类、相同的 `[JsonPropertyName]` 线上名称，写入时省略缺失成员。.NET 对无法识别内容的宽容度未变——未知属性会被跳过，正如 `System.Text.Json` 一贯所为——因此不应指望并不存在的严格性。

有一种行为比之前更宽容：SDK 没有对应模型的某事件*类型*现在会被两个流读取器跳过并给出 trace 警告，而不是终止事件流。单独解码一个未知事件仍会抛出 `AGUIUnknownEventTypeException`。

### 子智能体 {#subagents}

`SUBAGENT_STARTED`、`SUBAGENT_FINISHED` 和 `SUBAGENT_ERROR` 有模型、JSON 处理与 protobuf 映射器。`SubagentRunId` 是可以携带归属信息的事件上的属性——而非基础事件上的属性——因此按事件类型分支的消费方要从具体类型读取它。[子智能体规则](./1.0/events/subagents.md)说明了消费方必须如何处理它。

### 移除 {#retired}

- `AGUIBinaryInputContent`、其类型常量及其转换器分支。跨 Microsoft.Extensions.AI 边界的 `DataContent` 或 `UriContent` 会变为以其媒体类型命名的媒体部分，文件名放在该部分的 metadata 中。.NET 没有中间件层，也没有任何东西翻译传入的遗留部分：`{ "type": "binary" }` 部分是一个未知判别值，转换器会抛出 `JsonException`，导致整条消息的反序列化失败——以及承载它的快照或运行输入的反序列化失败。仍发出遗留部分的生产方 MUST 先升级，1.0 的 .NET 消费方才能读取它。

### 重命名与类型变更 {#renames-and-type-changes}

- `SubAgentInfo` → `SubagentInfo`；`MultiAgentCapabilities.SubAgents` → `Subagents`（线上 key 为 `subagents`）。没有别名；旧 key 会被跳过。
- `AgentCapabilities.Custom` 和 `IdentityCapabilities.Metadata` 为 `JsonElement?` 而非 `IDictionary<string, object?>?`。用 `JsonSerializer.SerializeToElement(...)` 构造它们。
- `ExecutionCapabilities.MaxIterations` 和 `MaxExecutionTime` 为 `long?` 而非 `int?`。
- `Tool.Parameters` 和 `RunAgentInput.ForwardedProperties`（线上 key 为 `forwardedProps`）是可为 null 的 `JsonElement?`，如 schema 所述；消息的 `Id` 是始终写入的非空字符串。
- `AGUIUserContent` → `AGUIContent`：字符串或部分的联合不再专属于用户消息。`AGUIToolMessage.Content` 和 `ToolCallResultEvent.Content` 为 `AGUIContent` 而非 `string`；字符串仍可隐式赋值，读回时使用 `Content.Value as string` 或遍历其各部分。尽管 schema 将部分类重命名为 `...Part`，这些部分类仍保留其 `AGUI...InputContent` 名称。每个部分都有可选的 `Id`，`AGUITextInputContent` 具有媒体部分早已具备的可选 `Metadata`。
- `AGUIInputContentSource` 有第三个子类 `AGUIInputContentFileSource`（`type: "file"`，常量 `AGUIInputContentSourceTypes.File`）：模型提供方为其已上传的字节签发的句柄，带可选的 `Provider` 与 `MimeType`。对 source 继承体系做 `switch` 需要为它加一个分支。绝不要将其 `Value` 当作 URL；如果你的智能体无法把该句柄交给其提供方，就像对待模型无法接受的其他部分一样，跳过该部分并给出警告。

### AOT {#aot}

源生成的序列化器上下文是提前编译下唯一的解析器。工具结果按其运行时类型序列化，类型未被该上下文注册的结果会抛出 `NotSupportedException`。`int` 在 1.0 中被显式注册——此前它只是偶然存在。

---

## 下一步阅读 {#where-to-look-next}

- [主要变更](./1.0/changelog.md) 页，了解协议层面的差异，并附有指向规范的链接。
- [能力](./1.0/basic/capabilities.md)，了解声明在被规范化后现在意味着哪些义务。
- [版本与兼容性](./1.0/basic/versioning.md)，了解 1.0 对端如何与更旧的对端通信。
