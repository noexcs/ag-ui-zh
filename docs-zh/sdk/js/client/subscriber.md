---
title: "AgentSubscriber"
description:
  "用于智能体生命周期与事件处理的事件驱动订阅者系统"
---
<em class="lead">用于智能体生命周期与事件处理的事件驱动订阅者系统</em>

# AgentSubscriber {#agentsubscriber}

`AgentSubscriber` 接口提供了一套完备的事件驱动系统，用于在智能体执行期间处理
智能体生命周期事件、消息更新与状态变更。它让你可以挂接到智能体运行的各个阶段，
并修改其行为。

```typescript
import { AgentSubscriber } from "@ag-ui/client"
```

## 概述 {#overview}

`AgentSubscriber` 定义了一组可选的事件处理器与生命周期钩子，用于响应智能体执行的
不同阶段。该接口中的所有方法都是可选的，因此你可以只实现需要处理的事件。

所有订阅者方法都可以是同步或异步的 — 如果它们返回 Promise，智能体会等待其完成
再继续。

## 向智能体添加订阅者 {#adding-subscribers-to-agents}

订阅者可以通过两种方式添加到智能体：

### 永久订阅 {#permanent-subscription}

使用 `subscribe()` 方法添加一个会在多次智能体运行之间持续存在的订阅者：

```typescript
const agent = new HttpAgent({ url: "https://api.example.com/agent" })

const subscriber: AgentSubscriber = {
  onTextMessageContentEvent: ({ textMessageBuffer }) => {
    console.log("Streaming text:", textMessageBuffer)
  },
}

// Add permanent subscriber
const subscription = agent.subscribe(subscriber)

// Later, remove the subscriber if needed
subscription.unsubscribe()
```

### 临时订阅 {#temporary-subscription}

把订阅者直接传给 `runAgent()` 以一次性使用：

```typescript
const temporarySubscriber: AgentSubscriber = {
  onRunFinishedEvent: ({ result }) => {
    console.log("Run completed with result:", result)
  },
}

// Use subscriber for this run only
await agent.runAgent({ tools: [myTool] }, temporarySubscriber)
```

## 核心接口 {#core-interfaces}

### AgentSubscriber {#agentsubscriber}

定义所有可用事件处理器与生命周期钩子的主接口。该接口中的所有方法都是可选的，
因此你可以只实现需要处理的事件。

### AgentStateMutation {#agentstatemutation}

事件处理器可以返回 `AgentStateMutation` 对象，以修改智能体状态并控制事件处理：

```typescript
interface AgentStateMutation {
  messages?: Message[] // Update the message history
  state?: State // Update the agent state
  stopPropagation?: boolean // Prevent further subscribers from processing this event
}
```

当订阅者返回一个变更时：

- **messages**：替换当前消息历史
- **state**：替换当前智能体状态
- **stopPropagation**：若为 `true`，阻止后续订阅者处理该事件
  （用于覆盖默认行为）

### AgentSubscriberParams {#agentsubscriberparams}

传给大多数订阅者方法的通用参数：

```typescript
interface AgentSubscriberParams {
  messages: Message[] // Current message history
  state: State // Current agent state
  agent: AbstractAgent // The agent instance
  input: RunAgentInput // The original input parameters
}
```

## 事件处理器 {#event-handlers}

### 生命周期事件 {#lifecycle-events}

#### onRunInitialized() {#onruninitialized}

在智能体运行首次初始化、任何处理开始之前调用。

```typescript
onRunInitialized?(params: AgentSubscriberParams): MaybePromise<Omit<AgentStateMutation, "stopPropagation"> | void>
```

#### onRunFailed() {#onrunfailed}

在智能体运行遇到错误时调用。

```typescript
onRunFailed?(params: { error: Error } & AgentSubscriberParams): MaybePromise<Omit<AgentStateMutation, "stopPropagation"> | void>
```

#### onRunFinalized() {#onrunfinalized}

在智能体运行完成时调用，无论成功还是失败。

```typescript
onRunFinalized?(params: AgentSubscriberParams): MaybePromise<Omit<AgentStateMutation, "stopPropagation"> | void>
```

### 事件处理器 {#event-handlers}

#### onEvent() {#onevent}

通用事件处理器，接收智能体执行期间的所有事件。

```typescript
onEvent?(params: { event: BaseEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onRunStartedEvent() {#onrunstartedevent}

在智能体运行开始执行时触发。

```typescript
onRunStartedEvent?(params: { event: RunStartedEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onRunFinishedEvent() {#onrunfinishedevent}

在智能体运行成功完成时调用。

```typescript
onRunFinishedEvent?(params: { event: RunFinishedEvent; result?: any } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onRunErrorEvent() {#onrunerrorevent}

在智能体运行遇到错误时触发。

```typescript
onRunErrorEvent?(params: { event: RunErrorEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onStepStartedEvent() {#onstepstartedevent}

在智能体运行中的一个步骤开始时调用。

```typescript
onStepStartedEvent?(params: { event: StepStartedEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onStepFinishedEvent() {#onstepfinishedevent}

在智能体运行中的一个步骤完成时触发。

```typescript
onStepFinishedEvent?(params: { event: StepFinishedEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

### 消息事件 {#message-events}

#### onTextMessageStartEvent() {#ontextmessagestartevent}

在文本消息开始生成时触发。

```typescript
onTextMessageStartEvent?(params: { event: TextMessageStartEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onTextMessageContentEvent() {#ontextmessagecontentevent}

在文本内容的每个块生成时调用。

```typescript
onTextMessageContentEvent?(params: { event: TextMessageContentEvent; textMessageBuffer: string } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onTextMessageEndEvent() {#ontextmessageendevent}

在文本消息生成完成时调用。

```typescript
onTextMessageEndEvent?(params: { event: TextMessageEndEvent; textMessageBuffer: string } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

### 工具调用事件 {#tool-call-events}

#### onToolCallStartEvent() {#ontoolcallstartevent}

在工具调用开始时触发。

```typescript
onToolCallStartEvent?(params: { event: ToolCallStartEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onToolCallArgsEvent() {#ontoolcallargsevent}

在工具调用参数被解析时调用，提供原始与已解析的参数数据。

```typescript
onToolCallArgsEvent?(params: { event: ToolCallArgsEvent; toolCallBuffer: string; toolCallName: string; partialToolCallArgs: Record<string, any> } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onToolCallEndEvent() {#ontoolcallendevent}

在工具调用完成并具备最终参数时调用。

```typescript
onToolCallEndEvent?(params: { event: ToolCallEndEvent; toolCallName: string; toolCallArgs: Record<string, any> } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onToolCallResultEvent() {#ontoolcallresultevent}

在收到工具调用结果时触发。

```typescript
onToolCallResultEvent?(params: { event: ToolCallResultEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

### 状态事件 {#state-events}

#### onStateSnapshotEvent() {#onstatesnapshotevent}

在提供完整状态快照时调用。

```typescript
onStateSnapshotEvent?(params: { event: StateSnapshotEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onStateDeltaEvent() {#onstatedeltaevent}

在应用部分状态变更时触发。

```typescript
onStateDeltaEvent?(params: { event: StateDeltaEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onMessagesSnapshotEvent() {#onmessagessnapshotevent}

在提供完整消息历史快照时调用。

```typescript
onMessagesSnapshotEvent?(params: { event: MessagesSnapshotEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onActivitySnapshotEvent() {#onactivitysnapshotevent}

在收到活动快照时调用。该处理器同时接收原始事件与任何既有的 `ActivityMessage`
（如果存在），以便你在默认客户端逻辑运行之前检查或替换它。

```typescript
onActivitySnapshotEvent?(params: {
  event: ActivitySnapshotEvent
  activityMessage?: ActivityMessage
  existingMessage?: Message
} & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onActivityDeltaEvent() {#onactivitydeltaevent}

对每个活动增量触发。使用此钩子可以在传入的 JSON Patch 操作更新会话记录之前
转换它们或对其去抖。

```typescript
onActivityDeltaEvent?(params: {
  event: ActivityDeltaEvent
  activityMessage?: ActivityMessage
} & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onRawEvent() {#onrawevent}

处理原始、未处理事件的处理器。

```typescript
onRawEvent?(params: { event: RawEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

#### onCustomEvent() {#oncustomevent}

处理自定义的应用程序特定事件的处理器。

```typescript
onCustomEvent?(params: { event: CustomEvent } & AgentSubscriberParams): MaybePromise<AgentStateMutation | void>
```

### 状态变更处理器 {#state-change-handlers}

#### onMessagesChanged() {#onmessageschanged}

在智能体的消息历史被更新时调用。

```typescript
onMessagesChanged?(params: Omit<AgentSubscriberParams, "input"> & { input?: RunAgentInput }): MaybePromise<void>
```

#### onStateChanged() {#onstatechanged}

在智能体的状态被修改时触发。

```typescript
onStateChanged?(params: Omit<AgentSubscriberParams, "input"> & { input?: RunAgentInput }): MaybePromise<void>
```

#### onNewMessage() {#onnewmessage}

在会话中新增一条消息时调用。

```typescript
onNewMessage?(params: { message: Message } & Omit<AgentSubscriberParams, "input"> & { input?: RunAgentInput }): MaybePromise<void>
```

#### onNewToolCall() {#onnewtoolcall}

在消息中新增一个工具调用时触发。

```typescript
onNewToolCall?(params: { toolCall: ToolCall } & Omit<AgentSubscriberParams, "input"> & { input?: RunAgentInput }): MaybePromise<void>
```

## 异步支持 {#async-support}

所有订阅者方法都支持同步与异步执行：

```typescript
const subscriber: AgentSubscriber = {
  // Synchronous handler
  onTextMessageContentEvent: ({ textMessageBuffer }) => {
    updateUI(textMessageBuffer)
  },

  // Asynchronous handler
  onStateChanged: async ({ state }) => {
    await saveStateToDatabase(state)
  },

  // Async handler with mutation
  onRunInitialized: async ({ messages, state }) => {
    const enrichedState = await loadUserPreferences()
    return {
      state: { ...state, ...enrichedState },
    }
  },
}
```

## 多个订阅者 {#multiple-subscribers}

智能体可以有多个订阅者，它们按添加顺序被处理：

```typescript
// First subscriber modifies state
const stateEnricher: AgentSubscriber = {
  onRunInitialized: ({ state }) => ({
    state: { ...state, timestamp: new Date().toISOString() },
  }),
}

// Second subscriber sees the modified state
const logger: AgentSubscriber = {
  onRunInitialized: ({ state }) => {
    console.log("State after enrichment:", state)
  },
}

agent.subscribe(stateEnricher)
agent.subscribe(logger)
```

## 与智能体集成 {#integration-with-agents}

基本用法模式：

```typescript
const agent = new HttpAgent({ url: "https://api.example.com/agent" })

// Add persistent subscriber
agent.subscribe({
  onTextMessageContentEvent: ({ textMessageBuffer }) => {
    updateStreamingUI(textMessageBuffer)
  },
  onRunFinishedEvent: ({ result }) => {
    displayFinalResult(result)
  },
})

// Run agent (subscriber will be called automatically)
const result = await agent.runAgent({
  tools: [myTool],
})
```
