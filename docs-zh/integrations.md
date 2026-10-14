---
title: 集成
description: "AG-UI 集成列表"
---
<em class="lead">AG-UI 集成列表</em>

本页展示各类 Agent User Interaction Protocol (AG-UI) 集成，它们体现了该协议的能力与通用性。

## 前端集成 {#frontend-integrations}

- **[CopilotKit](https://copilotkit.ai)** - 为你的产品提供 AI Copilots。

## 智能体框架 {#agent-frameworks}

- **[LangChain](https://www.langchain.com/langgraph)** - 在智能体的可控性与自主性之间取得平衡
- **[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)** - 用于构建、编排与部署 AI 智能体和多智能体工作流的框架，支持 Python 与 .NET。
- **[Google ADK](https://google.github.io/adk-docs/)** - Google 的 Agent Development Kit，用于基于 Gemini 模型构建 AI 智能体。AG-UI 同时支持 [Python 中间件](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/adk-middleware/python)与 [JavaScript 运行时集成](./integrations/google-adk-js.md)，并提供了一个[在线的 ADK JavaScript 演示](https://dojo.ag-ui.com/adk-js/feature/agentic_chat?openCopilot=true)。
- **[Google Antigravity](https://github.com/google-antigravity/antigravity-sdk-python)** - Google 的智能体运行框架 SDK，它在捆绑的本地进程中运行模型、其工具及其会话
- **[AWS Strands Agents](https://github.com/strands-agents/sdk-python)** - 一种模型驱动的方式来构建 AI 智能体
- **[Mastra](https://mastra.ai)** - TypeScript 智能体框架
- **[Pydantic AI](https://github.com/pydantic/pydantic-ai)** - Python 中生产就绪的 AI 智能体
- **[Agno](https://agno.com)** - 用于构建多智能体系统的全栈框架
- **[LlamaIndex](https://www.llamaindex.ai)** - 面向 LLM 应用的数据框架，具备 RAG 能力与工作流编排
- **[CrewAI](https://crewai.com)** - 借助强大的 AI 智能体，简化各行业的工作流。
- **[AG2](https://ag2.ai)** - 开源的 AgentOS
- **[Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)** - Anthropic 的托管智能体会话，通过 TypeScript、Python 与 .NET 桥接到 AG-UI
- **[Claude Agent SDK](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/claude-agent-sdk)** - Anthropic 的本地智能体 SDK，通过 AG-UI 提供服务
- **[Langroid](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/langroid)** - 用于构建多智能体 LLM 应用的轻量级 Python 框架
- **[Cloudflare Agents](https://github.com/ag-ui-protocol/ag-ui/tree/main/integrations/community/cloudflare-agents)** - 运行在 Cloudflare Workers 与 Durable Objects 上的智能体，通过 AG-UI 提供服务

## 基础设施 / 部署 {#infrastructure--deployment}

- **[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)** - 用于将 AG-UI 智能体部署到生产环境的全托管基础设施，具备原生协议支持、托管式认证、会话隔离与自动扩缩容。参见[部署指南](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-agui.html)与[发布公告](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-bedrock-agentcore-runtime-ag-ui-protocol/)。

## 规范（标准） {#specification-standard}
- **[Oracle Open Agent Spec](http://oracle.github.io/agent-spec/)** - 用于定义智能体系统的可移植语言
- **[A2A Middleware](https://a2a-protocol.org/)** - 为智能体互操作性提供权威的通用语言

## 生成式 UI {#generative-ui}
- **[A2UI](https://github.com/google/A2UI)** - 声明式生成式 UI，用于生成丰富、可交互的界面
- **[MCP Apps](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/)** - 直接在聊天界面中渲染来自 MCP 服务器的可交互 UI 组件

## SDK {#sdks}

| [Kotlin](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/kotlin/overview.mdx)
| [Golang](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/go/overview.mdx)
| [Dart](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/dart)
| [Java](https://github.com/ag-ui-protocol/ag-ui/blob/main/docs/sdk/java/overview.mdx)
| [Rust](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/rust/crates/ag-ui-client)
| [Ruby](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/ruby)
| [C++](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/c%2B%2B)
| [.NET](https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/dotnet/samples/GettingStarted)

#### （即将推出） {#coming-soon}
 | [Nim](https://github.com/ag-ui-protocol/ag-ui/pull/29)
 | [Flowise](https://github.com/ag-ui-protocol/ag-ui/issues/367)
 | [Langflow](https://github.com/ag-ui-protocol/ag-ui/issues/366)

### 客户端 {#clients}

| [CopilotKit](https://docs.copilotkit.ai/direct-to-llm/guides/quickstart)
| [终端 + Agent](./quickstart/clients.md)
| [聊天平台 — Slack、Microsoft Teams](https://github.com/CopilotKit/channels-sdk)
| [React Native](https://github.com/CopilotKit/CopilotKit/tree/main/examples/v2/react-native/demo)

加入 [Discord](https://discord.gg/Jd3FzfdJa8) 与 AG-UI 社区交流。
