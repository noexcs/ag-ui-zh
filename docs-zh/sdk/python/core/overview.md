---
title: "概述"
description: "Agent User Interaction Protocol SDK 的核心概念"
---
<em class="lead">Agent User Interaction Protocol SDK 的核心概念</em>

```bash
pip install ag-ui-protocol
```

# ag_ui.core {#aguicore}

Agent User Interaction Protocol SDK 采用基于事件的流式架构，
并配有强类型数据结构。此包提供了连接智能体系统的基础。

```python
from ag_ui.core import ...
```

## 类型 {#types}

表示系统构建模块的核心数据结构：

- [RunAgentInput](./types.md#runagentinput) - 运行智能体的输入参数
- [Message](./types.md#message-types) - 用户与助手的通信
  以及工具使用
- [Context](./types.md#context) - 提供给智能体的
  上下文信息
- [Tool](./types.md#tool) - 定义智能体可调用的函数
- [State](./types.md#state) - 智能体状态管理

- [类型参考](./types.md) — ag_ui.core 包中所有类型的完整文档

## 事件 {#events}

驱动智能体与前端之间通信的事件：

- [生命周期事件](./events.md#lifecycle-events) - 运行与步骤
  跟踪
- [文本消息事件](./events.md#text-message-events) - 助手
  消息流式传输
- [工具调用事件](./events.md#tool-call-events) - 函数调用
  生命周期
- [状态管理事件](./events.md#state-management-events) -
  智能体状态更新
- [特殊事件](./events.md#special-events) - 原始事件与自定义
  事件

- [事件参考](./events.md) — ag_ui.core 包中所有事件的完整文档
