---
title: "智能体"
description: "了解 Agent User Interaction Protocol 中的智能体"
---
<em class="lead">了解 Agent User Interaction Protocol 中的智能体</em>

# 智能体 {#agents}

智能体是 AG-UI 协议中处理请求并生成响应的核心组件。它们建立了一种标准化方式，
让前端应用通过一致的接口与 AI 服务通信，而无需关心底层实现。

## 什么是智能体？ {#what-is-an-agent}

在 AG-UI 中，智能体是一个满足以下条件的类：

1. 管理会话状态与消息历史
2. 处理传入的消息与上下文
3. 通过事件驱动的流式接口生成响应
4. 遵循标准化的通信协议

智能体可以实现为连接任意 AI 服务，包括：

- 大型语言模型（LLM），如 GPT-4 或 Claude
- 自定义 AI 系统
- 检索增强生成（RAG）系统
- 多智能体系统

## 智能体架构 {#agent-architecture}

AG-UI 中的所有智能体都扩展 `AbstractAgent` 类，该类为以下能力提供基础：

- 状态管理
- 消息历史跟踪
- 事件流处理
- 工具使用

```typescript
import { AbstractAgent } from "@ag-ui/client"

class MyAgent extends AbstractAgent {
  run(input: RunAgentInput): RunAgent {
    // Implementation details
  }
}
```

### 核心组件 {#core-components}

AG-UI 智能体包含若干关键组件：

1. **配置**：智能体 ID、会话 ID 与初始状态
2. **消息**：包含用户消息与助手消息的会话历史
3. **状态**：在多次交互之间持久保存的结构化数据
4. **事件**：用于与客户端通信的标准化消息
5. **工具**：智能体可用于与外部系统交互的函数

## 智能体类型 {#agent-types}

AG-UI 提供不同的智能体实现以适应各种需求：

### AbstractAgent {#abstractagent}

所有智能体都扩展的基类。它处理核心事件处理、状态管理与消息历史。

### HttpAgent {#httpagent}

一个具体实现，通过 HTTP 连接远程 AI 服务：

```typescript
import { HttpAgent } from "@ag-ui/client"

const agent = new HttpAgent({
  url: "https://your-agent-endpoint.com/agent",
  headers: {
    Authorization: "Bearer your-api-key",
  },
})
```

### 自定义智能体 {#custom-agents}

你可以通过扩展 `AbstractAgent` 创建自定义智能体，以集成任意 AI 服务：

```typescript
class CustomAgent extends AbstractAgent {
  // Custom properties and methods

  run(input: RunAgentInput): RunAgent {
    // Implement the agent's logic
  }
}
```

## 实现智能体 {#implementing-agents}

### 基本实现 {#basic-implementation}

要创建自定义智能体，请扩展 `AbstractAgent` 类并实现必需的 `run` 方法：

```typescript
import {
  AbstractAgent,
  RunAgent,
  RunAgentInput,
  EventType,
  BaseEvent,
} from "@ag-ui/client"
import { Observable } from "rxjs"

class SimpleAgent extends AbstractAgent {
  run(input: RunAgentInput): RunAgent {
    const { threadId, runId } = input

    return () =>
      new Observable<BaseEvent>((observer) => {
        // Emit RUN_STARTED event
        observer.next({
          type: EventType.RUN_STARTED,
          threadId,
          runId,
        })

        // Send a message
        const messageId = Date.now().toString()

        // Message start
        observer.next({
          type: EventType.TEXT_MESSAGE_START,
          messageId,
          role: "assistant",
        })

        // Message content
        observer.next({
          type: EventType.TEXT_MESSAGE_CONTENT,
          messageId,
          delta: "Hello, world!",
        })

        // Message end
        observer.next({
          type: EventType.TEXT_MESSAGE_END,
          messageId,
        })

        // Emit RUN_FINISHED event
        observer.next({
          type: EventType.RUN_FINISHED,
          threadId,
          runId,
        })

        // Complete the observable
        observer.complete()
      })
  }
}
```

## 智能体能力 {#agent-capabilities}

AG-UI 协议中的智能体提供一组丰富的能力，支持复杂的 AI 交互：

### 交互式通信 {#interactive-communication}

智能体通过事件流与前端应用建立双向通信通道。这支持：

- 逐字符的实时流式响应
- 用户与 AI 之间的即时反馈循环
- 长时间运行操作的进度指示
- 双向的结构化数据交换

### 工具使用 {#tool-usage}

智能体可以使用工具来执行操作并访问外部资源。
重要的是，工具由前端应用定义并传入智能体，从而形成灵活且可扩展的系统：

```typescript
// Tool definition
const confirmAction = {
  name: "confirmAction",
  description: "Ask the user to confirm a specific action before proceeding",
  parameters: {
    type: "object",
    properties: {
      action: {
        type: "string",
        description: "The action that needs user confirmation",
      },
      importance: {
        type: "string",
        enum: ["low", "medium", "high", "critical"],
        description: "The importance level of the action",
      },
      details: {
        type: "string",
        description: "Additional details about the action",
      },
    },
    required: ["action"],
  },
}

// Running an agent with tools from the frontend
agent.runAgent({
  tools: [confirmAction], // Frontend-defined tools passed to the agent
  // other parameters
})
```

工具通过一系列事件被调用：

1. `TOOL_CALL_START`：表示工具调用的开始
2. `TOOL_CALL_ARGS`：流式传输工具调用的参数
3. `TOOL_CALL_END`：标记工具调用的完成

随后前端应用可以执行该工具，并将结果回传给智能体。这种双向流程支持复杂的
human-in-the-loop 工作流，其中：

- 智能体可以请求执行特定操作
- 人类可以凭借恰当的判断执行这些操作
- 结果被回传给智能体以继续推理
- 智能体始终知晓过程中做出的所有决定

这一机制在实现 AI 与人类协作的界面时尤为强大。例如，[CopilotKit](https://docs.copilotkit.ai/)
正是利用了这一模式，通过其
[`useCopilotAction`](https://docs.copilotkit.ai/guides/frontend-actions) hook
提供了一种在 React 应用中定义与处理工具的简化方式。

通过工具机制让 AI 知晓人类的决定，应用可以保持上下文，并在用户与 AI 助手之间
创造更自然的协作体验。

### 状态管理 {#state-management}

智能体维护一种在多次交互之间持久保存的结构化状态。该状态可以：

- 通过 `STATE_DELTA` 事件增量更新
- 通过 `STATE_SNAPSHOT` 事件完全刷新
- 被智能体与前端共同访问
- 用于存储用户偏好、会话上下文或应用状态

```typescript
// Accessing agent state
console.log(agent.state.preferences)

// State is automatically updated during agent runs
agent.runAgent().subscribe((event) => {
  if (event.type === EventType.STATE_DELTA) {
    // State has been updated
    console.log("New state:", agent.state)
  }
})
```

### 多智能体协作 {#multiagent-collaboration}

AG-UI 支持智能体之间的交接与协作：

- 智能体可以将任务委派给其他专门的智能体
- 多个智能体可以在协调一致的工作流中协同工作
- 状态与上下文可以在智能体之间传递
- 前端在智能体切换过程中保持一致体验

例如，当需要编程帮助时，通用助手智能体可以交接给专门的编码智能体，
并传递会话上下文与具体需求。

### Human-in-the-Loop 工作流 {#humanintheloop-workflows}

智能体支持人类干预与协助：

- 智能体可以就特定决策请求人类输入
- 前端可以暂停智能体执行，并在人类反馈后恢复
- 人类专家可以在智能体输出最终确定前审阅并修改它们
- 混合工作流将 AI 的效率与人类的判断结合起来

这使应用中的智能体成为协作伙伴，而非自主系统。

### 会话记忆 {#conversational-memory}

智能体维护完整的会话消息历史：

- 过去的交互会影响未来的响应
- 消息历史在客户端与服务器之间同步
- 消息可以包含丰富内容（文本、结构化数据、引用）
- 可以管理上下文窗口以聚焦相关信息

```typescript
// Accessing message history
console.log(agent.messages)

// Adding a new user message
agent.messages.push({
  id: "msg_123",
  role: "user",
  content: "Can you explain that in more detail?",
})
```

### 元数据与埋点 {#metadata-and-instrumentation}

智能体可以发出关于其内部过程的元数据：

- 通过自定义事件暴露推理步骤
- 性能指标与时序信息
- 来源引用与参考跟踪
- 不同响应选项的置信度分数

这使前端能够对智能体的决策过程提供透明度，并帮助用户理解结论是如何得出的。

## 使用智能体 {#using-agents}

实现或实例化智能体后，可以这样使用它：

```typescript
// Create an agent instance
const agent = new HttpAgent({
  url: "https://your-agent-endpoint.com/agent",
})

// Add initial messages if needed
agent.messages = [
  {
    id: "1",
    role: "user",
    content: "Hello, how can you help me today?",
  },
]

// Run the agent
agent
  .runAgent({
    runId: "run_123",
    tools: [], // Optional tools
    context: [], // Optional context
  })
  .subscribe({
    next: (event) => {
      // Handle different event types
      switch (event.type) {
        case EventType.TEXT_MESSAGE_CONTENT:
          console.log("Content:", event.delta)
          break
        // Handle other events
      }
    },
    error: (error) => console.error("Error:", error),
    complete: () => console.log("Run complete"),
  })
```

## 智能体配置 {#agent-configuration}

智能体通过构造函数接受配置：

```typescript
interface AgentConfig {
  agentId?: string // Unique identifier for the agent
  description?: string // Human-readable description
  threadId?: string // Conversation thread identifier
  initialMessages?: Message[] // Initial messages
  initialState?: State // Initial state object
}

// Using the configuration
const agent = new HttpAgent({
  agentId: "my-agent-123",
  description: "A helpful assistant",
  threadId: "thread-456",
  initialMessages: [
    { id: "1", role: "system", content: "You are a helpful assistant." },
  ],
  initialState: { preferredLanguage: "English" },
})
```

## 智能体状态管理 {#agent-state-management}

AG-UI 智能体在多次交互之间维护状态：

```typescript
// Access current state
console.log(agent.state)

// Access messages
console.log(agent.messages)

// Clone an agent with its state
const clonedAgent = agent.clone()
```

## 结语 {#conclusion}

智能体是 AG-UI 协议的基础，提供了一种标准化方式将前端应用与 AI 服务连接起来。
通过实现 `AbstractAgent` 类，你可以为任意 AI 服务创建自定义集成，
同时为应用保持一致的接口。

事件驱动架构实现了现代 AI 应用所必需的实时流式交互，
而标准化协议确保了不同实现之间的兼容性。
