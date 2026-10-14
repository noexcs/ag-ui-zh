---
title: "简介"
description: "了解如何开始构建 AG-UI 集成"
---
<em class="lead">了解如何开始构建 AG-UI 集成</em>

<video controls preload="metadata">
<source src="https://copilotkit-public-assets.s3.us-east-1.amazonaws.com/docs/ag-ui/ag-ui-animation-simple.mp4" type="video/mp4">
</video>

# 什么是集成？ {#what-is-an-integration}

AG-UI 集成让你的智能体会说 AG-UI 协议。这意味着你的智能体可以与任何兼容 AG-UI 的客户端
应用协作 — 比如聊天界面、copilot 或自定义 AI 工具。

把它想象成为你的智能体添加一个通用翻译器。无需为每个客户端构建自定义 API，你只需实现一次
AG-UI，就能立即与任何兼容应用协作。

与 AG-UI 集成的智能体可以：
- **流式返回响应** - 生成过程中即时出现的实时文本
- **调用客户端侧工具** - 你的智能体可以使用客户端定义的函数与服务
- **共享状态** - 你的智能体状态是双向共享状态
- **通用执行** - 与任何兼容 AG-UI 的客户端应用集成
- **以及更多！** - 在[这里](../concepts/events.md)查看完整规范。

### 我应该在什么时候做集成？ {#when-should-i-make-any-integration}
如果你想找的集成没有列在我们的[集成页面](../integrations.md)上，你就需要自己做一个集成。
我们在下面准备了几篇指南！

不过，如果你想使用已有的集成（例如 LangGraph、CrewAI、Mastra 等），可以跳过这一步，
直接前往[构建应用](./applications.md)。

# 集成类型 {#types-of-integrations}
所以你已经决定需要一个集成了！很好，实现 AG-UI 集成有**两种主要方式**：

- [服务器实现](./server.md) — **直接从你的智能体**或服务器发出 AG-UI 事件。

  - [中间件实现](./middleware.md) — 把**已有协议**和应用**转换**为 AG-UI 事件。

### 何时使用服务器实现 {#when-to-use-a-server-implementation}
服务器实现让你直接从智能体或服务器发出 AG-UI 事件。如果你没有使用智能体框架，或者还没有
为你的智能体框架创建协议，这是最好的入门方式。

服务器实现也非常适合：
- 从零构建**新的智能体框架**
- 对事件如何发出以及发出什么拥有**最大控制权**
- 把智能体暴露为**独立 API**

### 何时使用中间件实现 {#when-to-use-a-middleware-implementation}
中间件是灵活的选择。它允许你把已有的协议和应用转换为 AG-UI 事件，在你的现有系统与 AG-UI
之间搭建桥梁。

中间件非常适合：
- 把**现有协议或 API**拿来并**通用地转换**
- 在**现有系统或框架**的约束内工作
- **当你无法直接控制**智能体框架或系统时
