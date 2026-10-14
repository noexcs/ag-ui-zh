---
title: 元事件
description: 独立于智能体运行的注解与信号
---
<em class="lead">独立于智能体运行的注解与信号</em>

# 元事件提案 {#meta-events-proposal}

## 摘要 {#summary}

### 问题陈述 {#problem-statement}

目前，AG-UI 事件与智能体运行紧密耦合。对于独立于智能体执行生命周期、附加到事件流上的用户反馈、注解或外部信号，尚无标准化的方式。

### 动机 {#motivation}

AG-UI 通过 **MetaEvents** 得到扩展，这是一类新的事件，可以出现在事件流中的任意位置，独立于智能体运行。MetaEvents 提供了一种把注解、信号或反馈附加到序列化事件流上的方式。它们可能来自用户、客户端或外部系统，而非来自智能体。示例包括对某条消息的点赞/点踩等反应。

## 状态 {#status}

- **状态**：草案
- **作者**：Markus Ecker (mail@mme.xyz)

## 详细规范 {#detailed-specification}

### 概述 {#overview}

本提案引入：

- 一种新的 **MetaEvent** 类型，用于带外注解
- 可以出现在事件流中任意位置的事件
- 对用户反馈、标签与外部注解的支持
- 可扩展的载荷结构，用于应用特定的数据

## 新类型：MetaEvent {#new-type-metaevent}

```typescript
type MetaEvent = BaseEvent & {
  type: EventType.META
  /**
   * Application-defined type of the meta event.
   * Examples: "thumbs_up", "thumbs_down", "tag", "note"
   */
  metaType: string

  /**
   * Application-defined payload.
   * May reference other entities (e.g., messageId) or contain freeform data.
   */
  payload: Record<string, unknown>
}
```

### 关键特征 {#key-characteristics}

- **独立于运行**：MetaEvents 不绑定到任何特定的运行生命周期
- **位置灵活**：可以出现在运行之前、运行之间或运行之后
- **来源多样**：可能来自用户、客户端或外部系统
- **可扩展**：应用自行定义其 metaType 取值与载荷 schema

## 实现示例 {#implementation-examples}

### 用户反馈 {#user-feedback}

**点赞：**

```json
{
  "id": "evt_123",
  "ts": 1714063982000,
  "type": "META",
  "metaType": "thumbs_up",
  "payload": {
    "messageId": "msg_456",
    "userId": "user_789"
  }
}
```

**带原因的点踩：**

```json
{
  "id": "evt_124",
  "ts": 1714063985000,
  "type": "META",
  "metaType": "thumbs_down",
  "payload": {
    "messageId": "msg_456",
    "userId": "user_789",
    "reason": "inaccurate",
    "comment": "The calculation seems incorrect"
  }
}
```

### 注解 {#annotations}

**用户笔记：**

```json
{
  "id": "evt_789",
  "ts": 1714064001000,
  "type": "META",
  "metaType": "note",
  "payload": {
    "text": "Important question to revisit",
    "relatedRunId": "run_001",
    "author": "user_123"
  }
}
```

**标签赋值：**

```json
{
  "id": "evt_890",
  "ts": 1714064100000,
  "type": "META",
  "metaType": "tag",
  "payload": {
    "tags": ["important", "follow-up"],
    "threadId": "thread_001"
  }
}
```

### 外部系统事件 {#external-system-events}

**分析事件：**

```json
{
  "id": "evt_901",
  "ts": 1714064200000,
  "type": "META",
  "metaType": "analytics",
  "payload": {
    "event": "conversation_shared",
    "properties": {
      "shareMethod": "link",
      "recipientCount": 3
    }
  }
}
```

**审核标记：**

```json
{
  "id": "evt_902",
  "ts": 1714064300000,
  "type": "META",
  "metaType": "moderation",
  "payload": {
    "action": "flag",
    "messageId": "msg_999",
    "category": "inappropriate_content",
    "confidence": 0.95
  }
}
```

## 常见的元事件类型 {#common-meta-event-types}

尽管应用可以自行定义类型，以下这些是常用的：

| MetaType      | 描述       | 典型载荷                    |
| ------------- | ----------------- | ---------------------------------- |
| `thumbs_up`   | 正向反馈 | `{ messageId, userId }`            |
| `thumbs_down` | 负向反馈 | `{ messageId, userId, reason? }`   |
| `note`        | 用户注解   | `{ text, relatedId?, author }`     |
| `tag`         | 分类    | `{ tags[], targetId }`             |
| `bookmark`    | 稍后保存    | `{ messageId, userId }`            |
| `copy`        | 内容已复制    | `{ messageId, content }`           |
| `share`       | 内容已分享    | `{ messageId, method }`            |
| `rating`      | 数值评分    | `{ messageId, rating, maxRating }` |

## 用例 {#use-cases}

### 用户反馈收集 {#user-feedback-collection}

捕获用户对智能体回复的反应，以改进质量。

### 会话注解 {#conversation-annotation}

允许用户为会话中的重要部分添加笔记、标签或书签。

### 分析与跟踪 {#analytics-and-tracking}

记录用户交互与行为，而不影响智能体执行。

### 内容审核 {#content-moderation}

标记内容以供外部审核系统审查。

### 协作功能 {#collaborative-features}

让多个用户能够对共享会话进行注解或评论。

### 审计追踪 {#audit-trail}

创建所有交互的完整记录，而不只是智能体的回复。

## 实现考量 {#implementation-considerations}

### 客户端 SDK 变更 {#client-sdk-changes}

TypeScript SDK：

- 在 `@ag-ui/core` 中新增 `MetaEvent` 类型
- 用于常见元事件类型的辅助函数
- MetaEvent 过滤与查询工具

Python SDK：

- `MetaEvent` 类实现
- 用于常见类型的元事件构建器
- 事件流过滤能力

## 测试策略 {#testing-strategy}

- MetaEvent 创建与校验的单元测试
- 混合事件流的集成测试
- 高吞吐元事件的性能测试
- 载荷校验的安全测试

## 参考资料 {#references}

- [AG-UI 事件文档](../concepts/events.md)
- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
