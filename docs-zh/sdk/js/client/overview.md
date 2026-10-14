---
title: "概述"
description: "客户端包概述"
---
<em class="lead">客户端包概述</em>

# @ag-ui/client {#aguiclient}

Agent User Interaction Protocol 客户端 SDK 为 AI 系统提供智能体连接选项。该包构建在核心类型与事件之上，为智能体实现提供灵活的连接方式。

```bash
npm install @ag-ui/client
```

## AbstractAgent {#abstractagent}

`AbstractAgent` 是用于实现自定义智能体连接的基类。扩展该类并实现 `run()`，即可把你自己的服务或智能体实现桥接到 AG-UI。

- [配置](./abstract-agent.md#configuration) - 使用
  agent ID、消息与状态进行设置
- [核心方法](./abstract-agent.md#core-methods) - 运行、中止与
  克隆功能
- [受保护方法](./abstract-agent.md#protected-methods) -
  供自定义实现使用的可扩展钩子
- [属性](./abstract-agent.md#properties) - 状态与消息
  跟踪

- [AbstractAgent 参考](./abstract-agent.md) — 用于创建自定义智能体连接的基类

## HttpAgent {#httpagent}

基于 HTTP 的智能体连接的具体实现：

- [配置](./http-agent.md#configuration) - URL 与请求头
  设置
- [方法](./http-agent.md#methods) - HTTP 专属的执行与
  取消
- [受保护方法](./http-agent.md#protected-methods) -
  可自定义的 HTTP 请求处理
- [属性](./http-agent.md#properties) - 连接管理

- [HttpAgent 参考](./http-agent.md) — 开箱即用的智能体连接 HTTP 实现，采用高效的事件编码格式

## 中间件 {#middleware}

通过灵活的中间件系统转换并拦截流经智能体的事件流：

- [函数中间件](./middleware.md#function-based-middleware) - 使用普通函数进行简单
  转换
- [类中间件](./middleware.md#class-based-middleware) - 带配置的
  有状态中间件
- [内置中间件](./middleware.md#built-in-middleware) -
  FilterToolCallsMiddleware 等
- [中间件模式](./middleware.md#middleware-patterns) - 常见
  用例与示例

- [中间件参考](./middleware.md) — 为 AG-UI 智能体提供强大的事件流转换与过滤能力

## AgentSubscriber {#agentsubscriber}

事件驱动的订阅者系统，用于在智能体执行期间处理智能体生命周期事件与状态变更：

- [事件处理器](./subscriber.md#event-handlers) - 生命周期、
  消息、工具调用与状态事件
- [状态管理](./subscriber.md#state-management) - 变更
  控制与传播处理
- [用法示例](./subscriber.md#usage-examples) - 日志记录、
  持久化与错误处理模式
- [集成](./subscriber.md#integration-with-agents) - 向智能体注册
  并使用订阅者

- [AgentSubscriber 参考](./subscriber.md) — 用于响应式智能体交互与中间件式功能的完整事件系统
