---
title: "能力"
description: "AG-UI 协议中智能体的动态能力发现"
---
<em class="lead">AG-UI 协议中智能体的动态能力发现</em>

# 能力 {#capabilities}

AG-UI 协议中的智能体可以通过**能力发现**在运行时声明它们支持什么。这使客户端
可以查询智能体，并根据可用特性调整自身行为 — 无需猜测或硬编码假设。

## 工作原理 {#how-it-works}

`AbstractAgent` 声明了一个可选的 `getCapabilities()` 方法，返回智能体当前支持的
全部内容的类型化快照。该方法由了解自身能力的智能体子类实现 — LangGraph 与 ADK
集成，或你自己的集成 — 而不是由裸的 `HttpAgent` 实现，因为后者是一种传输，
没有可查询的发现端点。对于未实现该方法的智能体，下面这个可选调用会返回 `undefined`：

```typescript
// Any AbstractAgent subclass that implements getCapabilities(); a plain
// HttpAgent does not, and would yield undefined here.
const agent = new LangGraphAgent({ url: "https://my-agent.example.com/api" })

const capabilities = await agent.getCapabilities?.()

if (capabilities?.tools?.supported) {
  console.log(`Agent provides ${capabilities.tools.items?.length} tools`)
}

if (capabilities?.reasoning?.supported) {
  // Show reasoning UI toggle
}
```

### 关键原则 {#key-principles}

- **仅发现** — 智能体声明它能做什么，不存在协商
- **动态** — 返回调用时刻的当前状态（例如，如果新增了工具，下一次调用会反映出来）
- **可选** — 未实现该方法的智能体返回 `undefined`
- **缺失即未知** — 只声明你支持的内容，省略的字段意味着该能力未被声明

## AgentCapabilities 接口 {#the-agentcapabilities-interface}

能力被组织为多个类型化类别，每个类别代表智能体功能的一个不同方面：

```typescript
interface AgentCapabilities {
  /** Agent identity and metadata. */
  identity?: IdentityCapabilities
  /** Supported transport mechanisms (SSE, WebSocket, binary, etc.). */
  transport?: TransportCapabilities
  /** Tools the agent provides and tool calling configuration. */
  tools?: ToolsCapabilities
  /** Output format support (structured output, MIME types). */
  output?: OutputCapabilities
  /** State and memory management (snapshots, deltas, persistence). */
  state?: StateCapabilities
  /** Multi-agent coordination (delegation, handoffs, sub-agents). */
  multiAgent?: MultiAgentCapabilities
  /** Reasoning and thinking support (chain-of-thought, encrypted thinking). */
  reasoning?: ReasoningCapabilities
  /** Multimodal input/output support organized by direction (input vs output). */
  multimodal?: MultimodalCapabilities
  /** Execution control and limits (code execution, timeouts, iteration caps). */
  execution?: ExecutionCapabilities
  /** Human-in-the-loop support (approvals, interventions, feedback). */
  humanInTheLoop?: HumanInTheLoopCapabilities
  /** Integration-specific capabilities not covered by the standard categories. */
  custom?: Record<string, unknown>
}
```

`custom` 字段是集成特定能力的逃生通道，这些能力不属于标准类别。

## 能力类别 {#capability-categories}

### 身份 {#identity}

关于智能体的基本元数据。适用于发现类 UI、智能体市场与调试。当你希望客户端展示
智能体信息，或存在多个智能体而用户需要选择其中之一时，请设置这些字段。

```typescript
interface IdentityCapabilities {
  /** Human-readable name shown in UIs and agent selectors. */
  name?: string
  /** The framework or platform powering this agent (e.g., "langgraph", "mastra", "crewai"). */
  type?: string
  /** What this agent does — helps users and routing logic decide when to use it. */
  description?: string
  /** Semantic version of the agent (e.g., "1.2.0"). Useful for compatibility checks. */
  version?: string
  /** Organization or team that maintains this agent. */
  provider?: string
  /** URL to the agent's documentation or homepage. */
  documentationUrl?: string
  /** Arbitrary key-value pairs for integration-specific identity info. */
  metadata?: Record<string, unknown>
}
```

### 传输 {#transport}

声明智能体支持哪些传输机制。客户端据此选择最佳连接策略。只把智能体实际处理的
传输对应的标志设为 `true` — 不支持的应省略或设为 `false`。

```typescript
interface TransportCapabilities {
  /** Set `true` if the agent streams responses via SSE. Most agents enable this. */
  streaming?: boolean
  /** Set `true` if the agent accepts persistent WebSocket connections. */
  websocket?: boolean
  /** Set `true` if the agent supports the AG-UI binary protocol (protobuf over HTTP). */
  httpBinary?: boolean
  /** Set `true` if the agent can send async updates via webhooks after a run finishes. */
  pushNotifications?: boolean
  /** Set `true` if the agent supports resuming interrupted streams via sequence numbers. */
  resumable?: boolean
}
```

### 工具 {#tools}

工具调用能力。区分智能体自身提供的工具（列在 `items` 中）与客户端在运行时通过
`RunAgentInput.tools` 传入的工具。当你的智能体可以调用函数、搜索网页、执行代码等
时，请启用此项。

```typescript
interface ToolsCapabilities {
  /** Set `true` if the agent can make tool calls at all. Set `false` to explicitly
   *  signal tool calling is disabled even if items are present. */
  supported?: boolean
  /** The tools this agent provides on its own (full JSON Schema definitions).
   *  These are distinct from client-provided tools passed in `RunAgentInput.tools`. */
  items?: Tool[]
  /** Set `true` if the agent can invoke multiple tools concurrently within a single step. */
  parallelCalls?: boolean
  /** Set `true` if the agent accepts and uses tools provided by the client at runtime. */
  clientProvided?: boolean
}
```

### 输出 {#output}

输出格式支持。当你的智能体可以返回符合 JSON schema 的响应时，请启用
`structuredOutput`，这对程序化消费很有用。

```typescript
interface OutputCapabilities {
  /** Set `true` if the agent can produce structured JSON output matching a provided schema. */
  structuredOutput?: boolean
  /** MIME types the agent can produce (e.g., `["text/plain", "application/json"]`).
   *  Omit if the agent only produces plain text. */
  supportedMimeTypes?: string[]
}
```

### 状态 {#state}

状态与记忆管理能力。这些字段告知客户端智能体如何处理共享状态，以及会话上下文
是否在多次运行之间持久保存。

```typescript
interface StateCapabilities {
  /** Set `true` if the agent emits `STATE_SNAPSHOT` events (full state replacement). */
  snapshots?: boolean
  /** Set `true` if the agent emits `STATE_DELTA` events (JSON Patch incremental updates). */
  deltas?: boolean
  /** Set `true` if the agent has long-term memory beyond the current thread
   *  (e.g., vector store, knowledge base, or cross-session recall). */
  memory?: boolean
  /** Set `true` if state is preserved across multiple runs within the same thread.
   *  When `false`, state resets on each run. */
  persistentState?: boolean
}
```

### 多智能体 {#multiagent}

多智能体协调能力。当你的智能体可以编排工作或把工作交接给其他智能体时，请启用这些。

```typescript
interface MultiAgentCapabilities {
  /** Set `true` if the agent participates in any form of multi-agent coordination. */
  supported?: boolean
  /** Set `true` if the agent can delegate subtasks to other agents while retaining control. */
  delegation?: boolean
  /** Set `true` if the agent can transfer the conversation entirely to another agent. */
  handoffs?: boolean
  /** List of sub-agents this agent can invoke. Helps clients build agent selection UIs. */
  subagents?: Array<{ name: string; description?: string }>
}
```

### 推理 {#reasoning}

推理与思考能力。当你的智能体暴露其内部思考过程（例如思维链、扩展思考）时，
请启用这些。

```typescript
interface ReasoningCapabilities {
  /** Set `true` if the agent produces reasoning/thinking tokens visible to the client. */
  supported?: boolean
  /** Set `true` if reasoning tokens are streamed incrementally (vs. returned all at once). */
  streaming?: boolean
  /** Set `true` if reasoning content is encrypted (zero-data-retention mode).
   *  Clients should expect opaque `encryptedValue` fields instead of readable content. */
  encrypted?: boolean
}
```

### 多模态 {#multimodal}

多模态输入与输出支持，组织为 `input` 与 `output` 两个子对象，以便客户端可以分别
查询智能体接受什么与产生什么。客户端据此显示/隐藏文件上传按钮、录音器、图像选择器等。

```typescript
interface MultimodalInputCapabilities {
  /** Set `true` if the agent can process image inputs (e.g., screenshots, photos). */
  image?: boolean
  /** Set `true` if the agent can process audio inputs (speech, recordings). */
  audio?: boolean
  /** Set `true` if the agent can process video inputs. */
  video?: boolean
  /** Set `true` if the agent can process PDF documents. */
  pdf?: boolean
  /** Set `true` if the agent can process arbitrary file uploads. */
  file?: boolean
}

interface MultimodalOutputCapabilities {
  /** Set `true` if the agent can generate images as part of its response. */
  image?: boolean
  /** Set `true` if the agent can produce audio output (text-to-speech, audio files). */
  audio?: boolean
}

interface MultimodalCapabilities {
  /** Modalities the agent can accept as input (images, audio, video, PDFs, files). */
  input?: MultimodalInputCapabilities
  /** Modalities the agent can produce as output (images, audio). */
  output?: MultimodalOutputCapabilities
}
```

### 执行 {#execution}

执行控制与限制。声明这些字段，以便客户端可以预期智能体运行可能持续多久或需要多少步骤。

```typescript
interface ExecutionCapabilities {
  /** Set `true` if the agent can execute code (e.g., Python, JavaScript) during a run. */
  codeExecution?: boolean
  /** Set `true` if code execution happens in a sandboxed/isolated environment.
   *  Only meaningful when `codeExecution` is `true`. */
  sandboxed?: boolean
  /** Maximum number of tool-call/reasoning iterations the agent will perform per run.
   *  Helps clients display progress or set timeout expectations. */
  maxIterations?: number
  /** Maximum wall-clock time (in milliseconds) the agent will run before timing out. */
  maxExecutionTime?: number
}
```

### Human-in-the-Loop {#humanintheloop}

Human-in-the-loop 交互支持。当你的智能体可以暂停执行以请求人类输入、批准或反馈后
再继续时，请启用这些。

```typescript
interface HumanInTheLoopCapabilities {
  /** Set `true` if the agent supports any form of human-in-the-loop interaction. */
  supported?: boolean
  /** Set `true` if the agent can pause and request explicit approval before
   *  performing sensitive actions (e.g., sending emails, deleting data). */
  approvals?: boolean
  /** Set `true` if the agent allows humans to intervene and modify its plan mid-execution. */
  interventions?: boolean
  /** Set `true` if the agent can incorporate user feedback (thumbs up/down, corrections)
   *  to improve its behavior within the current session. */
  feedback?: boolean
  /** Set `true` if the agent participates in the AG-UI interrupt protocol (emits
   *  `RunFinished` with `outcome: { type: "interrupt", interrupts: [...] }`,
   *  accepts `RunAgentInput.resume`). */
  interrupts?: boolean
  /** Set `true` if tool-call interrupts accept `editedArgs` in the resume payload.
   *  Only meaningful when `interrupts` is `true`. */
  approveWithEdits?: boolean
}
```

!!! note
    完整协议规范见[中断](./interrupts.md)。

## 实现 getCapabilities() {#implementing-getcapabilities}

### 自定义智能体 {#custom-agents}

在你的智能体子类上实现 `getCapabilities()`，只返回你实际支持的能力：

```typescript
import { AbstractAgent, AgentCapabilities } from "@ag-ui/client"

class MyAgent extends AbstractAgent {
  async getCapabilities(): Promise<AgentCapabilities> {
    return {
      identity: {
        name: "my-agent",
        description: "A custom agent with tool support",
        version: "1.0.0",
      },
      transport: {
        streaming: true,
      },
      tools: {
        supported: true,
        items: this.getRegisteredTools(),
        clientProvided: true,
      },
      state: {
        snapshots: true,
        deltas: true,
      },
    }
  }

  // ... run() implementation
}
```

### 动态能力 {#dynamic-capabilities}

由于 `getCapabilities()` 返回实时快照，它反映智能体的当前状态：

```typescript
const agent = new MyAgent(config)

let caps = await agent.getCapabilities()
console.log(caps.tools?.items?.length) // 5

// Register more tools at runtime
agent.registerTool(newTool)

caps = await agent.getCapabilities()
console.log(caps.tools?.items?.length) // 6
```

## 客户端使用模式 {#client-usage-patterns}

### 自适应 UI {#adaptive-ui}

根据智能体支持的内容渲染 UI 组件：

```typescript
const capabilities = await agent.getCapabilities?.()

// Only show reasoning panel if supported
if (capabilities?.reasoning?.supported) {
  showReasoningPanel()
}

// Only show sub-agent selector if available
if (capabilities?.multiAgent?.subagents?.length) {
  showSubAgentSelector(capabilities.multiAgent.subagents)
}

// Only show approval UI if HITL is supported
if (capabilities?.humanInTheLoop?.approvals) {
  enableApprovalWorkflow()
}
```

### 特性门控 {#feature-gating}

禁用智能体不支持的特性，而不是在运行时失败：

```typescript
const capabilities = await agent.getCapabilities?.()

// Gate on an explicit declaration: an omitted field means undeclared, not unsupported.
const canUseStructuredOutput = capabilities?.output?.structuredOutput === true
const canStream = capabilities?.transport?.streaming === true
```

### 自定义能力 {#custom-capabilities}

通过 `custom` 字段访问集成特定的能力：

```typescript
const capabilities = await agent.getCapabilities?.()

const rateLimit = capabilities?.custom?.rateLimit as
  | { maxRequestsPerMinute: number }
  | undefined

if (rateLimit) {
  configureThrottling(rateLimit.maxRequestsPerMinute)
}
```
