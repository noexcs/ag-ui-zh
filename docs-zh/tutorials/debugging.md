---
title: 调试
description:
  Agent User Interaction Protocol (AG-UI) 集成的全面调试指南
---
<em class="lead">Agent User Interaction Protocol (AG-UI) 集成的全面调试指南</em>

# 调试 AG-UI 集成 {#debugging-agui-integrations}

调试基于智能体的应用可能颇具挑战，尤其是在处理像 AG-UI 这样实时、事件驱动的协议时。
本指南向你介绍 AG-UI Dojo，一个用于学习、测试和调试 AG-UI 实现的强大工具。

## AG-UI Dojo {#the-agui-dojo}

AG-UI Dojo 是把 AG-UI 引入新平台的最佳方式，也是学习该协议基础能力的绝佳资源。它提供
一个结构化环境，让你可以测试并验证 AG-UI 协议的每个组件。

### Dojo 是什么？ {#what-is-the-dojo}

Dojo 由一系列“hello world”规模的演示组成，覆盖 AG-UI 提供的不同构建块。每个演示：

1. 展示某项具体 AG-UI 能力的实际效果
2. 并排呈现用户可见的交互与底层代码
3. 让你测试并验证自己的实现

### 把 Dojo 用作实现清单 {#using-the-dojo-as-an-implementation-checklist}

在把 AG-UI 引入新平台或新环境时，你可以把 Dojo 当作一份全面的“待办清单”：

1. 逐个完成每个演示
2. 在你的环境中实现并测试每个 AG-UI 构建块
3. 当所有演示在你的实现中都正确运行时，你就可以确信：功能完备的 copilot 与智能体原生
   应用都能构建在你的新平台上

这种有条不紊的方法确保你已覆盖完整 AG-UI 实现所需的全部功能。

### 把 Dojo 用作学习资源 {#using-the-dojo-as-a-learning-resource}

对于刚接触 AG-UI 的开发者，Dojo 是一份交互式学习资源：

- 每个条目演示一项具体的 AG-UI 能力
- 你既能看到交互在用户视角下的样子
- 也能看到并排展示的底层代码，帮助你理解其工作原理
- 递增的复杂度有助于从基础到高级特性逐步建立理解

### 常见调试模式 {#common-debugging-patterns}

在使用 Dojo 调试你的 AG-UI 实现时，请记住以下模式：

1. **事件顺序问题**：验证事件是否按正确顺序、以正确的嵌套关系发出（例如
   `TEXT_MESSAGE_START` 先于
   `TEXT_MESSAGE_CONTENT`）

2. **数据格式问题**：确保你的事件负载符合每种事件类型预期的结构

3. **传输层调试**：检查你所选的传输机制（SSE、WebSockets 等）是否正确投递事件

4. **状态同步**：确认状态更新通过快照与增量被正确应用

5. **工具执行**：验证工具调用与响应是否被正确格式化并处理

## Dojo 入门 {#getting-started-with-the-dojo}

要开始使用 AG-UI Dojo：

1. 从
   [github.com/ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) 克隆仓库
2. 按照 README 中的安装说明操作
3. 按顺序逐个完成演示
4. 使用提供的测试用例验证你的实现

Dojo 的结构化方法使其成为学习 AG-UI 并确保你的实现满足全部要求的重要资源。
