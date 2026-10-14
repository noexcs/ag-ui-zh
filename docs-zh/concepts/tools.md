---
title: "工具"
description:
  "理解工具，以及它们如何支撑 human-in-the-loop AI 工作流"
---
<em class="lead">理解工具，以及它们如何支撑 human-in-the-loop AI 工作流</em>

# 工具 {#tools}

工具是 AG-UI 协议中的基础概念，使 AI 智能体能够与外部系统交互，并把人的判断纳入其工作流。

AG-UI 区分由智能体后端定义的工具，以及由客户端在运行时提供的工具。后端定义的工具保留在后端智能体或框架配置中。客户端定义的工具通过 `RunAgentInput.tools` 传入，使智能体能够回调到应用特定的前端行为，例如 UI 操作、审批或由用户介入的工作流。

## 什么是工具？ {#what-are-tools}

在 AG-UI 中，工具是智能体可以调用的函数，用于：

1. 请求特定信息
2. 在外部系统中执行操作
3. 请求人的输入或确认
4. 访问专门的能力

工具弥合了 AI 推理与现实世界操作之间的差距，使智能体能够完成仅靠对话无法完成的任务。

## 工具结构 {#tool-structure}

工具遵循一致的结构，用以定义其名称、用途和预期参数：

```typescript
interface Tool {
  name: string // Unique identifier for the tool
  description: string // Human-readable explanation of what the tool does
  parameters: {
    // JSON Schema defining the tool's parameters
    type: "object"
    properties: {
      // Tool-specific parameters
    }
    required: string[] // Array of required parameter names
  }
}
```

`parameters` 字段使用 [JSON Schema](https://json-schema.org/) 定义工具接受的参数结构。该 schema 同时被智能体（用于生成有效的工具调用）和前端（用于校验并解析工具参数）使用。

## 前端定义的工具 {#frontenddefined-tools}

AG-UI 工具系统的一个关键特点是：工具在前端定义，并在执行期间传给智能体：

```typescript
// Define tools in the frontend
const userConfirmationTool = {
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
    },
    required: ["action"],
  },
}

// Pass tools to the agent during execution
agent.runAgent({
  tools: [userConfirmationTool],
  // Other parameters...
})
```

这种做法有几个优点：

1. **前端控制**：前端决定智能体可以使用哪些能力
2. **动态能力**：可以根据用户权限、上下文或应用状态添加或移除工具
3. **关注点分离**：智能体专注于推理，而前端负责工具的实现
4. **安全性**：敏感操作由应用控制，而不是由智能体控制

`RunAgentInput.tools` 只用于这些由客户端提供的工具。它不用于容纳后端智能体可用的每一个工具。如果你的集成有后端工具，请在后端框架中定义它们，或通过智能体能力对外声明，而不是从客户端发送它们的 schema。

## 工具调用生命周期 {#tool-call-lifecycle}

当智能体需要使用工具时，它遵循一套标准化的事件序列：

1. **ToolCallStart**：表示工具调用的开始，带有唯一 ID 和工具名称

   ```typescript
   {
     type: EventType.TOOL_CALL_START,
     toolCallId: "tool-123",
     toolCallName: "confirmAction",
     parentMessageId: "msg-456" // Optional reference to a message
   }
   ```

2. **ToolCallArgs**：在工具参数生成过程中将其流式传输

   ```typescript
   {
     type: EventType.TOOL_CALL_ARGS,
     toolCallId: "tool-123",
     delta: '{"act' // Partial JSON being streamed
   }
   ```

   ```typescript
   {
     type: EventType.TOOL_CALL_ARGS,
     toolCallId: "tool-123",
     delta: 'ion":"Depl' // More JSON being streamed
   }
   ```

   ```typescript
   {
     type: EventType.TOOL_CALL_ARGS,
     toolCallId: "tool-123",
     delta: 'oy the application to production"}' // Final JSON fragment
   }
   ```

3. **ToolCallEnd**：标记工具调用的完成
   ```typescript
   {
     type: EventType.TOOL_CALL_END,
     toolCallId: "tool-123"
   }
   ```

前端累积这些增量以构造完整的工具调用参数。工具调用完成后，前端可以执行该工具，并把结果返回给智能体。

### 工具调用元数据 {#tool-call-metadata}

这三个事件都可以携带 `metadata` 对象，并且它累积到**工具调用本身**，而不是累积到拥有它的助手消息上：

```typescript
assistantMessage.toolCalls[0].metadata
// { provider: "anthropic", latencyMs: 84 }
```

这是有意为之。一条助手消息可以拥有多个工具调用，因此把它们的元数据合并进父级，会使结果取决于这些调用恰好交织出现的顺序。让每个工具调用各自拥有元数据，就能保持结果无歧义。

`ToolCallResult` 不同——它会创建一条工具消息，因此其元数据像任何其他构建消息的事件一样合并进该消息。参见[元数据](./metadata.md)。

## 工具结果 {#tool-results}

工具执行完成后，结果会作为一条“工具消息”发送回智能体：

```typescript
{
  id: "result-789",
  role: "tool",
  content: "true", // Tool result as a string
  toolCallId: "tool-123" // References the original tool call
}
```

这条消息成为会话历史的一部分，使智能体能够在后续回复中引用并纳入工具的结果。

如果工具未成功，请把 `error` 设为失败消息：

```typescript
{
  id: "result-789",
  role: "tool",
  content: "Deployment blocked: the production environment is locked",
  toolCallId: "tool-123",
  error: "the production environment is locked" // Marks this result as a failure
}
```

`error` 是协议表达客户端侧工具失败的方式。没有它，失败的工具与成功的工具就无法区分——前端恰好放进 `content` 的内容就是智能体所能依据的全部信息。完整的 `ToolMessage` 结构见[消息](./messages.md)。

## Human-in-the-Loop 工作流 {#humanintheloop-workflows}

AG-UI 工具系统在实现 human-in-the-loop 工作流时尤为强大。通过定义请求人的输入或确认的工具，开发者可以打造把自主运行与人的判断无缝融合的 AI 体验。

例如：

1. 智能体需要做出一个重要决定
2. 智能体调用 `confirmAction` 工具，并带上该决定的细节
3. 前端向用户显示确认对话框
4. 用户提供其输入
5. 前端把用户的决定发送回智能体
6. 智能体在知晓用户选择的情况下继续处理

这种模式支持如下用例：

- **审批工作流**：AI 建议需要人工批准的操作
- **数据核验**：由人核验或修正 AI 生成的数据
- **协同决策**：AI 与人共同解决复杂问题
- **监督式学习**：人的反馈改进 AI 未来的决策

## CopilotKit 集成 {#copilotkit-integration}

[CopilotKit](https://docs.copilotkit.ai/) 通过其 [`useCopilotAction`](https://docs.copilotkit.ai/guides/frontend-actions) hook，为在 React 应用中使用 AG-UI 工具提供了简化的方式：

```tsx
import { useCopilotAction } from "@copilotkit/react-core"

// Define a tool for user confirmation
useCopilotAction({
  name: "confirmAction",
  description: "Ask the user to confirm an action",
  parameters: {
    type: "object",
    properties: {
      action: {
        type: "string",
        description: "The action to confirm",
      },
    },
    required: ["action"],
  },
  handler: async ({ action }) => {
    // Show a confirmation dialog
    const confirmed = await showConfirmDialog(action)
    return confirmed ? "approved" : "rejected"
  },
})
```

这种方式让你可以轻松定义与 React 组件集成的工具，并以清晰、声明式的方式处理工具执行逻辑。

## 工具示例 {#tool-examples}

以下是 AG-UI 应用中常见的一些工具类型：

### 用户确认 {#user-confirmation}

```typescript
{
  name: "confirmAction",
  description: "Ask the user to confirm an action",
  parameters: {
    type: "object",
    properties: {
      action: {
        type: "string",
        description: "The action to confirm"
      },
      importance: {
        type: "string",
        enum: ["low", "medium", "high", "critical"],
        description: "The importance level"
      }
    },
    required: ["action"]
  }
}
```

### 数据检索 {#data-retrieval}

```typescript
{
  name: "fetchUserData",
  description: "Retrieve data about a specific user",
  parameters: {
    type: "object",
    properties: {
      userId: {
        type: "string",
        description: "ID of the user"
      },
      fields: {
        type: "array",
        items: {
          type: "string"
        },
        description: "Fields to retrieve"
      }
    },
    required: ["userId"]
  }
}
```

### 用户界面控制 {#user-interface-control}

```typescript
{
  name: "navigateTo",
  description: "Navigate to a different page or view",
  parameters: {
    type: "object",
    properties: {
      destination: {
        type: "string",
        description: "Destination page or view"
      },
      params: {
        type: "object",
        description: "Optional parameters for the navigation"
      }
    },
    required: ["destination"]
  }
}
```

### 内容生成 {#content-generation}

```typescript
{
  name: "generateImage",
  description: "Generate an image based on a description",
  parameters: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "Description of the image to generate"
      },
      style: {
        type: "string",
        description: "Visual style for the image"
      },
      dimensions: {
        type: "object",
        properties: {
          width: { type: "number" },
          height: { type: "number" }
        },
        description: "Dimensions of the image"
      }
    },
    required: ["prompt"]
  }
}
```

## 最佳实践 {#best-practices}

为 AG-UI 设计工具时：

1. **清晰命名**：使用描述性强、以动作导向的名称
2. **详尽描述**：包含完整的描述，帮助智能体理解何时以及如何使用该工具
3. **结构化参数**：定义精确的参数 schema，使用描述性的字段名和约束
4. **必填字段**：只有确实必要时才把参数标记为必填
5. **错误处理**：在工具执行代码中实现健壮的错误处理
6. **用户体验**：设计能为人的决策提供适当上下文的工具 UI

## 结语 {#conclusion}

AG-UI 中的工具弥合了 AI 推理与现实世界操作之间的差距，使融合 AI 与人类智能双方优势的复杂工作流成为可能。通过在前端定义工具并把它们传给智能体，开发者可以打造 AI 与人高效协作的交互式体验。

工具系统在实现 human-in-the-loop 工作流时尤为强大，其中 AI 可以建议操作，但把关键决定交由人来做。这在自动化与人的判断之间取得平衡，创造出既强大又可信的 AI 体验。
