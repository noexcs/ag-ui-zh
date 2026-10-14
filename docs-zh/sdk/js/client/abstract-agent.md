---
title: "AbstractAgent"
description: "带核心事件处理的基础智能体实现"
---
<em class="lead">带核心事件处理的基础智能体实现</em>

# AbstractAgent {#abstractagent}

`AbstractAgent` 类为 Agent User Interaction Protocol 中的所有智能体实现提供基础。它处理核心的事件流处理、状态管理与消息历史。

```typescript
import { AbstractAgent } from "@ag-ui/client"
```

## 配置 {#configuration}

默认情况下，所有智能体都通过向构造函数提供一个可选的 `AgentConfig` 对象来配置。

```typescript
interface AgentConfig {
  agentId?: string // The identifier of the agent
  description?: string // A description of the agent, used by the LLM
  threadId?: string // The conversation thread identifier
  initialMessages?: Message[] // An array of initial messages
  initialState?: State // The initial state of the agent
}
```

### 在你的子类中添加配置项 {#adding-configuration-options-in-your-subclass}

要添加额外的配置项，建议扩展 `AgentConfig` 接口，并在子类中用扩展后的配置调用 super 构造函数，如下所示：

```typescript
interface MyAgentConfig extends AgentConfig {
  myConfigOption: string
}

class MyAgent extends AbstractAgent {
  private myConfigOption: string

  constructor(config: MyAgentConfig) {
    super(config)
    this.myConfigOption = config.myConfigOption
  }
}
```

## 核心方法 {#core-methods}

### runAgent() {#runagent}

执行智能体并处理结果的主要方法。

```typescript
runAgent(parameters?: RunAgentParameters, subscriber?: AgentSubscriber): Promise<RunAgentResult>
```

#### 参数 {#parameters}

```typescript
interface RunAgentParameters {
  runId?: string // Unique ID for this execution run
  tools?: Tool[] // Available tools for the agent
  context?: Context[] // Contextual information
  forwardedProps?: Record<string, any> // Additional properties to forward
}
```

可选的 `subscriber` 参数允许你提供一个 [AgentSubscriber](./subscriber.md)，用于在本次特定运行期间处理事件。

#### 返回值 {#return-value}

```typescript
interface RunAgentResult {
  result: any // The final result returned by the agent
  newMessages: Message[] // New messages added during this run
}
```

### subscribe() {#subscribe}

添加一个 [AgentSubscriber](./subscriber.md)，用于跨多次智能体运行处理事件。

```typescript
subscribe(subscriber: AgentSubscriber): { unsubscribe: () => void }
```

返回一个带有 `unsubscribe()` 方法的对象，可在不再需要时移除该订阅者。

### use() {#use}

向智能体的事件处理管线中添加中间件。

```typescript
use(...middlewares: (Middleware | MiddlewareFunction)[]): this
```

中间件可以是：
- **函数中间件**：转换事件流的简单函数
- **类中间件**：用于有状态操作的 `Middleware` 类实例

```typescript
// Function middleware
agent.use((input, next) => {
  console.log("Processing:", input.runId);
  return next.run(input);
});

// Class middleware
agent.use(new FilterToolCallsMiddleware({
  allowedToolCalls: ["search"]
}));

// Chain multiple middleware
agent.use(loggingMiddleware, authMiddleware, filterMiddleware);
```

中间件按添加顺序执行，每个都包裹下一个。中间件在 `runAgent()` 中生效；`connectAgent()` 目前直接调用 `connect()`。更多细节参见[中间件文档](./middleware.md)。

### getCapabilities() {#getcapabilities}

返回智能体当前的能力。可选 — 子类实现该方法以声明其支持的内容。未实现时返回 `undefined`。

```typescript
getCapabilities?(): Promise<AgentCapabilities>
```

完整的 `AgentCapabilities` 类型定义与使用模式参见[能力](../../../concepts/capabilities.md)。

### abortRun() {#abortrun}

取消当前智能体执行。

```typescript
abortRun(): void
```

### clone() {#clone}

创建智能体实例的深拷贝。

```typescript
clone(): AbstractAgent
```

### connectAgent() {#connectagent}

与实现了 `connect()` 方法的智能体建立持久连接。

```typescript
connectAgent(parameters?: RunAgentParameters, subscriber?: AgentSubscriber): Promise<RunAgentResult>
```

与 `runAgent()` 类似，但内部使用 `connect()` 方法。该智能体必须实现 `connect()`，或者此功能必须由诸如 [CopilotKit](https://copilotkit.ai) 之类的框架提供。

## 可观察属性 {#observable-properties}

### events$ {#events}

智能体执行期间发出的所有事件的可观察流。

```typescript
events$: Observable<BaseEvent>
```

该属性提供对智能体事件流的直接访问。事件使用 `ReplaySubject` 存储，因此迟到的订阅者将收到全部历史事件。

## 属性 {#properties}

- `agentId`：智能体实例的唯一标识符
- `description`：人类可读的描述
- `threadId`：会话线程标识符
- `messages`：会话消息数组
- `state`：当前智能体状态对象
- `events$`：智能体执行期间发出的所有 `BaseEvent` 对象的可观察流（会为迟到的订阅者重放）

## 受保护方法 {#protected-methods}

这些方法旨在由子类实现或扩展：

### run() {#run}

执行智能体并返回可观察的事件流。

```typescript
protected abstract run(input: RunAgentInput): RunAgent
```

### connect() {#connect}

建立持久连接并返回可观察的事件流。

```typescript
protected connect(input: RunAgentInput): RunAgent
```

重写该方法以实现持久连接。默认实现会抛出 `ConnectNotImplementedError`。

### apply() {#apply}

处理来自运行的事件并更新智能体状态。

```typescript
protected apply(input: RunAgentInput): ApplyEvents
```

### prepareRunAgentInput() {#preparerunagentinput}

准备智能体执行的输入参数。

```typescript
protected prepareRunAgentInput(parameters?: RunAgentParameters): RunAgentInput
```

### onError() 与 onFinalize() {#onerror-and-onfinalize}

用于错误处理与清理操作的生命周期钩子。

```typescript
protected onError(error: Error): void
protected onFinalize(): void
```
