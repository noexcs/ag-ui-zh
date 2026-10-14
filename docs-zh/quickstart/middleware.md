---
title: "中间件"
description:
  "通过 AG-UI 连接现有协议、进程内智能体或自定义方案"
---
<em class="lead">通过 AG-UI 连接现有协议、进程内智能体或自定义方案</em>

# 简介 {#introduction}

中间件实现让你能够**把现有协议与应用转换为 AG-UI 事件**。这种方式在现有系统与
AG-UI 之间建立桥梁，非常适合为当前应用添加智能体能力。

## 何时使用中间件实现 {#when-to-use-a-middleware-implementation}

中间件是灵活的选择。它让你把现有协议与应用转换为 AG-UI 事件，
从而在现有系统与 AG-UI 之间建立桥梁。

中间件非常适合：

- 把你的**现有协议或 API** **通用地转换**
- 在**现有系统或框架**的限制内工作
- **当你无法直接控制**智能体框架或系统时

## 你将构建什么 {#what-youll-build}

在本指南中，我们将创建一个中间件智能体，它：

1. 扩展 `AbstractAgent` 类
2. 连接到 OpenAI 的 GPT-4o 模型
3. 把 OpenAI 响应转换为 AG-UI 事件
4. 与你的应用在同一进程内运行

这种方式让你在保持 AG-UI 协议全部能力的同时，拥有与现有代码库集成的最大灵活性。

让我们开始吧！

## 前置条件 {#prerequisites}

开始之前，请确保你已具备：

- [Node.js](https://nodejs.org/) **v16 或更高版本**
- 一个 **OpenAI API key**

### 1. 提供你的 OpenAI API key {#1-provide-your-openai-api-key}

首先，设置你的 API key：

```bash
# Set your OpenAI API key {#set-your-openai-api-key}
export OPENAI_API_KEY=your-api-key-here
```

### 2. 安装构建工具 {#2-install-build-utilities}

安装以下工具：

```bash
brew install protobuf
```

```bash
npm i nx
```

```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

## 步骤 1 – 搭建你的集成骨架 {#step-1--scaffold-your-integration}

首先克隆仓库

```bash
git clone git@github.com:ag-ui-protocol/ag-ui.git
cd ag-ui/
```

复制 middleware-starter 模板以创建你的 OpenAI 集成：

```bash
cp -r integrations/middleware-starter integrations/openai
```

### 更新元数据 {#update-metadata}

打开 `integrations/openai/package.json` 并更新字段以匹配你的新目录：

```json
{
  "name": "@ag-ui/openai",
  "author": "Your Name <your-email@example.com>",
  "version": "0.0.1",

  ... rest of package.json
}
```

接下来，更新 `integrations/openai/src/index.ts` 中的类名：

```ts
// change the name to OpenAIAgent
export class OpenAIAgent extends AbstractAgent {}
```

最后，通过把集成加入 `apps/dojo/src/menu.ts` 将其引入 dojo：

```ts
// ...
export const menuIntegrations: MenuIntegrationConfig[] = [
  // ...

  {
    id: "openai",
    name: "OpenAI",
    features: ["agentic_chat"],
  },
]
```

以及 `apps/dojo/src/agents.ts`：

```ts
// ...
import { OpenAIAgent } from "@ag-ui/openai"

export const agentsIntegrations: AgentIntegrationConfig[] = [
  // ...

  {
    id: "openai",
    agents: async () => {
      return {
        agentic_chat: new OpenAIAgent(),
      }
    },
  },
]
```

## 步骤 2 – 把包添加到 dojo 依赖 {#step-2--add-package-to-dojo-dependencies}

打开 `apps/dojo/package.json` 并添加包 `@ag-ui/openai`：

```json
{
  "name": "demo-viewer",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@ag-ui/agno": "workspace:*",
    "@ag-ui/langgraph": "workspace:*",
    "@ag-ui/mastra": "workspace:*",
    "@ag-ui/middleware-starter": "workspace:*",
    "@ag-ui/server-starter": "workspace:*",
    "@ag-ui/server-starter-all-features": "workspace:*",
    "@ag-ui/vercel-ai-sdk": "workspace:*",
    "@ag-ui/openai": "workspace:*", <- Add this line

  ... rest of package.json
}
```

## 步骤 3 – 启动 dojo {#step-3--start-the-dojo}

现在看看你的成果：

```bash
# Install dependencies {#install-dependencies}
pnpm install

# Compile the project and run the dojo {#compile-the-project-and-run-the-dojo}
pnpm dev
```

访问 [http://localhost:3000](http://localhost:3000)，从下拉菜单中选择
**OpenAI**。目前你会看到 stub 智能体回复 **Hello world!**。

这个 stub 智能体的行为如下：

```ts
// integrations/openai/src/index.ts
import {
  AbstractAgent,
  BaseEvent,
  EventType,
  RunAgentInput,
} from "@ag-ui/client"
import { Observable } from "rxjs"

export class OpenAIAgent extends AbstractAgent {
  run(input: RunAgentInput): Observable<BaseEvent> {
    const messageId = Date.now().toString()
    return new Observable<BaseEvent>((observer) => {
      observer.next({
        type: EventType.RUN_STARTED,
        threadId: input.threadId,
        runId: input.runId,
      } as any)

      observer.next({
        type: EventType.TEXT_MESSAGE_START,
        messageId,
      } as any)

      observer.next({
        type: EventType.TEXT_MESSAGE_CONTENT,
        messageId,
        delta: "Hello world!",
      } as any)

      observer.next({
        type: EventType.TEXT_MESSAGE_END,
        messageId,
      } as any)

      observer.next({
        type: EventType.RUN_FINISHED,
        threadId: input.threadId,
        runId: input.runId,
      } as any)

      observer.complete()
    })
  }
}
```

## 步骤 4 – 将 OpenAI 与 AG-UI 桥接 {#step-4--bridge-openai-with-agui}

让我们把 stub 转换成一个真实的智能体，从 OpenAI 流式获取补全结果。

### 安装 OpenAI SDK {#install-the-openai-sdk}

首先，我们需要 OpenAI SDK：

```bash
cd integrations/openai
pnpm install openai
```

### AG-UI 回顾 {#agui-recap}

AG-UI 智能体扩展 `AbstractAgent`，并发出一个事件序列以表示：

- 生命周期事件（`RUN_STARTED`、`RUN_FINISHED`、`RUN_ERROR`）
- 内容事件（`TEXT_MESSAGE_*`、`TOOL_CALL_*` 等）

### 实现流式智能体 {#implement-the-streaming-agent}

现在我们将把 stub 智能体转换为真实的 OpenAI 集成。关键区别在于，
我们不再发送硬编码的 "Hello world!" 消息，而是连接 OpenAI 的 API，
并通过 AG-UI 事件把响应流式回传。

该实现遵循与 stub 相同的事件流，但我们会在构造函数中添加 OpenAI 客户端初始化，
并用真实的 API 调用替换模拟响应。如果响应中存在工具调用，我们也会处理它们，
从而使我们的智能体在需要时完全具备使用函数的能力。

```typescript
// integrations/openai/src/index.ts
import {
  AbstractAgent,
  RunAgentInput,
  EventType,
  BaseEvent,
} from "@ag-ui/client"
import { Observable } from "rxjs"

import { OpenAI } from "openai"

export class OpenAIAgent extends AbstractAgent {
  private openai: OpenAI

  constructor(openai?: OpenAI) {
    super()
    // Initialize OpenAI client - uses OPENAI_API_KEY from environment if not provided
    this.openai = openai ?? new OpenAI()
  }

  run(input: RunAgentInput): Observable<BaseEvent> {
    return new Observable<BaseEvent>((observer) => {
      // Same as before - emit RUN_STARTED to begin
      observer.next({
        type: EventType.RUN_STARTED,
        threadId: input.threadId,
        runId: input.runId,
      } as any)

      // NEW: Instead of hardcoded response, call OpenAI's API
      this.openai.chat.completions
        .create({
          model: "gpt-4o",
          stream: true, // Enable streaming for real-time responses
          // Convert AG-UI tools format to OpenAI's expected format
          tools: input.tools.map((tool) => ({
            type: "function",
            function: {
              name: tool.name,
              description: tool.description,
              parameters: tool.parameters,
            },
          })),
          // Transform AG-UI messages to OpenAI's message format
          messages: input.messages.map((message) => ({
            role: message.role as any,
            content: message.content ?? "",
            // Include tool calls if this is an assistant message with tools
            ...(message.role === "assistant" && message.toolCalls
              ? {
                  tool_calls: message.toolCalls,
                }
              : {}),
            // Include tool call ID if this is a tool result message
            ...(message.role === "tool"
              ? { tool_call_id: message.toolCallId }
              : {}),
          })),
        })
        .then(async (response) => {
          const messageId = Date.now().toString()

          // NEW: Stream each chunk from OpenAI's response
          for await (const chunk of response) {
            // Handle text content chunks
            if (chunk.choices[0].delta.content) {
              observer.next({
                type: EventType.TEXT_MESSAGE_CHUNK, // Chunk events open and close messages automatically
                messageId,
                delta: chunk.choices[0].delta.content,
              } as any)
            }
            // Handle tool call chunks (when the model wants to use a function)
            else if (chunk.choices[0].delta.tool_calls) {
              let toolCall = chunk.choices[0].delta.tool_calls[0]

              observer.next({
                type: EventType.TOOL_CALL_CHUNK,
                toolCallId: toolCall.id,
                toolCallName: toolCall.function?.name,
                parentMessageId: messageId,
                delta: toolCall.function?.arguments,
              } as any)
            }
          }

          // Same as before - emit RUN_FINISHED when complete
          observer.next({
            type: EventType.RUN_FINISHED,
            threadId: input.threadId,
            runId: input.runId,
          } as any)

          observer.complete()
        })
        // NEW: Handle errors from the API
        .catch((error) => {
          observer.next({
            type: EventType.RUN_ERROR,
            message: error.message,
          } as any)

          observer.error(error)
        })
    })
  }
}
```

### 底层发生了什么？ {#what-happens-under-the-hood}

让我们拆解你的智能体在做什么：

1. **初始化** – 我们创建一个 OpenAI 客户端并发出 `RUN_STARTED`
2. **请求** – 我们以 `stream: true` 把用户消息发送给 `chat.completions`
3. **流式传输** – 我们把每个块作为 `TEXT_MESSAGE_CHUNK` 或 `TOOL_CALL_CHUNK` 转发
4. **结束** – 我们发出 `RUN_FINISHED`（如果出错则发出 `RUN_ERROR`）
   并完成 observable

## 步骤 5 – 与你的智能体聊天 {#step-5--chat-with-your-agent}

刷新 dojo 页面并开始输入。你会看到 GPT-4o 实时逐词流式输出其答案。

## 将 AG-UI 桥接到任意协议 {#bridging-agui-to-any-protocol}

你刚刚实现的模式 — 转换输入、转发流式块、发出 AG-UI 事件 — 几乎适用于任何后端：

- REST 或 GraphQL API
- WebSocket
- MQTT 之类的 IoT 协议

## 将你的智能体连接到前端 {#connect-your-agent-to-a-frontend}

[CopilotKit](https://docs.copilotkit.ai) 之类的工具已经理解 AG-UI，
并提供即插即用的 React 组件。把它们指向你的智能体端点，
即可开箱获得功能完备的聊天 UI。

## 分享你的集成 {#share-your-integration}

你是否构建了他人可以复用的自定义适配器？我们欢迎社区贡献！

1. Fork [AG-UI 仓库](https://github.com/ag-ui-protocol/ag-ui)
2. 在 `integrations` 下添加你的包。更多细节与命名
   约定见[贡献指南](../development/contributing.md)。
3. 提交一个 pull request，描述你的用例与设计决策

如果你有疑问、需要反馈，或想先验证一个想法，请在 GitHub Discussions 中发起讨论：
[AG-UI GitHub Discussions](https://github.com/orgs/ag-ui-protocol/discussions)。

你的集成可能会随下一个版本发布，并帮助整个 AG-UI 生态成长。

## 结语 {#conclusion}

你现在拥有一个功能完备的 OpenAI AG-UI 适配器，以及一个用于测试它的本地 playground。
从这里你可以：

- 添加工具调用以增强你的智能体
- 把你的集成发布到 npm
- 将 AG-UI 桥接到任何其他模型或服务

祝你构建愉快！
