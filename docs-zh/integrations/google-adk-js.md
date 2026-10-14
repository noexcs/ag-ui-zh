---
title: Google ADK JavaScript 快速上手
description: 在 AG-UI 端点后面运行原生的 Google ADK JavaScript 智能体。
---
<em class="lead">在 AG-UI 端点后面运行原生的 Google ADK JavaScript 智能体。</em>

`@ag-ui/adk-js` 把服务器端的 Google ADK JavaScript `Runner` 适配为 AG-UI 的 `AbstractAgent`。当智能体与 Web 运行时都在 Node.js 中运行时使用它。现有的 `@ag-ui/adk` 包仍然是 Python ADK 中间件的 HTTP 客户端。

## 前置条件 {#prerequisites}

- Node.js 20.19 或更高版本
- `@ag-ui/client` 与 `@ag-ui/core` 1.x（使用能解析到 1.x 系列的 CopilotKit 版本）
- 来自 [Google AI Studio](https://aistudio.google.com/apikey) 的 Gemini API 密钥

## 将 ADK JavaScript 添加到应用 {#add-adk-javascript-to-an-application}

安装服务器依赖：

```bash
npm install @ag-ui/adk-js @google/adk @copilotkit/runtime hono
```

`@ag-ui/adk-js` 需要 `@google/adk` 2.x。

在服务器读取的环境中设置你的 Gemini 密钥：

```dotenv
GOOGLE_GENAI_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=0
```

创建 `app/api/copilotkit/route.ts`：

```typescript
import { ADKJSAgent } from "@ag-ui/adk-js"
import {
  CopilotRuntime,
  InMemoryAgentRunner,
  createCopilotEndpointSingleRoute,
} from "@copilotkit/runtime/v2"
import { Agent, InMemorySessionService } from "@google/adk"
import { handle } from "hono/vercel"

export const runtime = "nodejs"

const rootAgent = new Agent({
  name: "assistant",
  model: "gemini-2.5-flash",
  instruction: "Be concise and use frontend tools when appropriate.",
})

const copilotRuntime = new CopilotRuntime({
  agents: {
    assistant: new ADKJSAgent({
      appName: "assistant_app",
      sessionService: new InMemorySessionService(),
      agent: rootAgent,
      userId: "user-123", // resolve from server-side auth
    }),
  },
  runner: new InMemoryAgentRunner(),
})

const endpoint = createCopilotEndpointSingleRoute({
  runtime: copilotRuntime,
  basePath: "/api/copilotkit",
})

export const POST = handle(endpoint)
```

前端现在可以通过任意 AG-UI 客户端选择 `assistant` 智能体。CopilotKit React 应用在其 `CopilotKit` provider 上使用 `runtimeUrl="/api/copilotkit"` 与 `agent="assistant"`。

## 运行与并发 {#runs-and-concurrency}

不同的会话线程会在同一个共享的智能体实例上并发运行；对同一用户与同一线程的第二次运行会被以 `THREAD_BUSY` 拒绝。ADK 在每次运行后都会关闭每个 toolset，因此对于共享某个可关闭 toolset 的多个 root（或需要保持每次运行状态的 root），请通过工厂为每次运行提供实例（`agent: () => new Workflow(...)`），或者传入 `runner:` 以提供完全配置好的 Runner。客户端断开连接后发生的失败会写入 `logger`（默认 `console`）。

## 支持的集成行为 {#supported-integration-behavior}

- 流式输出助手消息与生命周期事件
- 后端与前端工具调用
- AG-UI 状态快照与 RFC 6902 状态增量
- ADK 的输入请求、确认请求与凭据请求，作为可恢复的中断。
  在运行时自行抛出确认请求的工具，还必须从 `checkRequireConfirmation` 返回 `true`（或在 `FunctionTool` 上声明 `requireConfirmation`），因为 ADK 2.x 会把批准绑定到它所指定的工具上。
- 恢复的消息历史，且消息 ID 稳定
- ADK 报告时的提供方/模型 token 用量
- 以裸 ADK `Workflow` 作为 `Runner` root（其工作流节点会作为子智能体上报，其前端工具会被发现）
- 用于 ADK 多智能体树的 AG-UI subagent 协议（见下文）

该集成仅限服务器端。切勿在浏览器组件中导入 `@ag-ui/adk-js` 或 `@google/adk`。关于工具、共享状态、生成式 UI 与中断，参见[在线 Dojo 示例](https://dojo.ag-ui.com/adk-js/feature/agentic_chat?openCopilot=true)。

## 子智能体 {#subagents}

`subagents: "steps"` 会在 ADK 子智能体工作前后发出 `STEP_STARTED` / `STEP_FINISHED`（`agent:<name>`）以及 `CUSTOM` 的 `MultiAgentHandoff` 事件 — 对所有客户端都安全，也是 Dojo 多智能体页面所读取的内容。`subagents: "attributed"` 会增加 AG-UI subagent 协议（`SUBAGENT_STARTED/FINISHED/ERROR`，事件、消息与中断上的 `subagentRunId`，在恢复时以同一 id 继续被挂起的子智能体）；消费方客户端需要 `@ag-ui/client` 1.x，因为较旧的客户端会在任何应用代码运行之前就拒绝这些事件类型。默认值为 `off`。
