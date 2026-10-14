---
title: "HttpAgent"
description: "用于连接远程 AI 智能体的基于 HTTP 的智能体"
---
<em class="lead">用于连接远程 AI 智能体的基于 HTTP 的智能体</em>

# HttpAgent {#httpagent}

`HttpAgent` 扩展了 `AbstractAgent`，以提供到远程 AI 智能体的基于 HTTP 的连接。它处理请求/响应周期，并把 HTTP 事件流转换为标准的 Agent User Interaction Protocol 事件。

```typescript
import { HttpAgent } from "@ag-ui/client"
```

## 配置 {#configuration}

创建 HTTP 智能体时，你需要提供一个 `HttpAgentConfig` 对象：

```typescript
interface HttpAgentConfig extends AgentConfig {
  url: string // Endpoint URL for the agent service
  headers?: Record<string, string> // Optional HTTP headers
}
```

## 创建 HttpAgent {#creating-an-httpagent}

```typescript
const agent = new HttpAgent({
  url: "https://api.example.com/v1/agent",
  headers: {
    Authorization: "Bearer your-api-key",
  },
})
```

## 方法 {#methods}

### runAgent() {#runagent}

通过向配置的端点发起 HTTP 请求来执行智能体。

```typescript
runAgent(parameters?: RunAgentParameters, subscriber?: AgentSubscriber): Promise<RunAgentResult>
```

#### 参数 {#parameters}

`parameters` 参数遵循标准的 `RunAgentParameters` 接口。可选的 `subscriber` 参数允许你提供一个 [AgentSubscriber](./subscriber.md)，用于在本次特定运行期间处理事件。

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

### abortRun() {#abortrun}

使用 AbortController 取消当前的 HTTP 请求。

```typescript
abortRun(): void
```

## 受保护方法 {#protected-methods}

### requestInit() {#requestinit}

配置 HTTP 请求。重写该方法以自定义请求的发起方式。

```typescript
protected requestInit(input: RunAgentInput): RequestInit
```

默认实现：

```typescript
{
  method: "POST",
  headers: {
    ...this.headers,
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  },
  body: JSON.stringify(input),
  signal: this.abortController.signal,
}
```

### run() {#run}

使用 HTTP 请求实现 `AbstractAgent` 中的抽象 `run()` 方法。

```typescript
run(input: RunAgentInput): RunAgent
```

## 属性 {#properties}

- `url`：智能体服务的端点 URL
- `headers`：随请求发送的 HTTP 请求头
- `abortController`：用于取消请求的 AbortController 实例
