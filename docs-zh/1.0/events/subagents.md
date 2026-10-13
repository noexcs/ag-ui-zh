---
title: "子智能体"
description: "归属、所有权、嵌套、并行执行、状态与终结 — 1.0"
---
<em class="lead">归属、所有权、嵌套、并行执行、状态与终结</em>

一个智能体可以把运行的部分工作委派给另一个智能体。
被委派方生产的一切都在同一条流中传输，因此消费方
需要在不重放该运行的情况下知道哪些工作属于谁。

## 归属 {#attribution}

`subagentRunId` 标识子智能体的一次调用。
子智能体生产的事件携带它；父智能体生产的事件不携带。
`subagentRunId` 缺失意味着父智能体，且 MUST NOT 被
拼写为 `null`。

一个 id 标识的是一次*调用*，而非一个智能体。
生产方 MUST NOT 在同一个运行内把
`subagentRunId` 复用于第二次调用，即便是同一个子智能体
——第二次调用拥有自己的 id。当一次被暂停的调用
被继续时，一个 id MAY 在稍后的运行中再次出现。

哪些事件可以携带归属是一个结构性问题，
[schema](../schema.md#attributable) 给出了答案。把一个
标签读在一个独立事件上——`STEP_*`、`CUSTOM`、`RAW`、
状态事件——应读作出处：它记录的是
谁生产了该事件，而非生产方拥有该事件所触及之物的
私有副本。

## 生命周期 {#lifecycle}

`SUBAGENT_STARTED` 宣告一次调用，`SUBAGENT_FINISHED`
关闭它，`SUBAGENT_ERROR` 报告它已失败。三者都携带
其所涉的 `subagentRunId`，且生产方 MUST NOT 省略它。

- 宣告一次调用的生产方 MUST 在任何归属于它的
  事件之前宣告。
- 生产方 MUST NOT 宣告一个 id 已处于活跃状态的
  调用。
- 生产方 MUST NOT 复用本运行内已终结的调用的 id。
- 生产方宣告的每次调用 MUST 在本运行结束前被关闭，
  由 `SUBAGENT_FINISHED` 或 `SUBAGENT_ERROR` 关闭。

生产方 MAY 在什么也不宣告的情况下给事件加归属。
这样一条流告诉消费方哪些工作属于一组，却不告知
一次调用何时开始或结束，且消费方 MUST 接受它：
`subagentRunId` 本身就有意义，而要求生命周期事件
会把分组能力从那些无法报告它的生产方那里拿走。
能够报告生命周期的生产方 SHOULD 报告，因为消费方
届时可以把一次调用显示为运行中，而不是从碰巧
到达的事件去推断。

`SUBAGENT_ERROR` 结束的是该次调用，而非运行。
父智能体 MAY 处理一个失败的子智能体并继续；
这正是它不是 `RUN_ERROR` 的原因。

子智能体的模型调用就是这个运行的调用：没有
子智能体事件携带 token 用量，且运行的终态事件
[报告](../events/lifecycle.md#token-usage) 整个运行的
用量，包括子智能体在内。

`SUBAGENT_FINISHED` 报告该段为何结束。outcome 缺失
意味着成功。suspended outcome 意味着该次调用被
暂停，等待外部输入——对这条流而言是终态，对该次
调用而言不是，稍后的运行 MAY 以同一个 id 继续
它。生产方 MUST NOT 发送 schema 未描述的
outcome 值，且 MUST NOT 把中断 id 附着到
success outcome 上。

## 所有权 {#ownership}

归属不是建议性的。一旦某个实体在某所有者之下
开启，每一个延续它的事件 MUST 对该所有者
保持一致。

- 一条 `TEXT_MESSAGE_CONTENT` 或 `TEXT_MESSAGE_END`
  MUST NOT 携带一个与开启该消息的
  `TEXT_MESSAGE_START` 不一致的 `subagentRunId`。
  它 MAY 省略该标签：未加标签的延续继续的是
  开启者所拥有的一切，而只给开启者加标签的
  生产方仍然是符合的。
- 推理消息、工具调用相对于其 `TOOL_CALL_START`、
  活动消息相对于开启它们的快照，适用相同规则。
- 一条 `STEP_FINISHED` MUST 携带与其所关闭的
  `STEP_STARTED` 相同的归属。步骤是按所有者划分的：
  父智能体与子智能体 MAY 各自同时拥有一个同名
  步骤处于开启状态，且各自关闭自己的。

消费方 MUST 拒绝标签与其开启者不一致的延续。
接受它会把一个生产方的内容追加进另一个
生产方的消息，而这没有任何消费方能够事后检测。
不携带标签的延续不构成不一致，且 MUST 被接受。

工具调用继承承载它的消息的归属。生产方
MUST NOT 把一个工具调用归属于一个所有者，
同时承载它的消息却归属于另一个所有者。

## 嵌套与并行 {#nesting-and-parallelism}

子智能体 MAY 自己再委派。`SUBAGENT_STARTED` 上的
`parentSubagentRunId` 指名派生本次调用的那次调用；
缺失意味着父智能体直接派生了它。生产方
MUST NOT 指名一个未在本运行内宣告过的
父调用。

各调用 MAY 并行运行，其事件 MAY 任意交错。
每次调用的实体分别跟踪，因此两个子智能体
MAY 同时流式传输消息。消费方 MUST NOT 假定
一次调用的事件是连续的，也 MUST NOT 因为
另一次调用结束就关闭某次调用的实体。

## 状态 {#state}

状态是运行范围的。子智能体发送的
`STATE_SNAPSHOT` 或 `STATE_DELTA` 对运行状态的
更新与父智能体发送的完全相同，且消费方
MUST 如此应用。

状态事件上的 `subagentRunId` 是出处：它记录的是
哪个调用生产了该更新。它 MUST NOT 被读作子智能体
拥有一个私有状态，且消费方 MUST NOT 因为更新
是子智能体发送的就把它扣留于运行状态之外。
本协议没有按子智能体划分的状态。

## 终结 {#termination}

在仍有调用处于活跃状态时，运行 MUST NOT 结束。
一个在尚有调用开启时到达工作末尾的生产方
有 bug：要么该调用已结束而未被报告，要么它
未结束而运行并未结束。

`RUN_ERROR` 结束一切。运行出错时，消费方
MUST 把每个开启中的调用当作已放弃，且 MUST NOT
期望其中任何一个有关闭事件。

当一个运行以 interrupt outcome 结束时，其携带的
中断 MAY 带有归属。标签了 `subagentRunId` 的中断
是在该调用内部提出的；未加标签的中断属于父智能体。
一个因后代中断而被暂停的调用本身不拥有任何
中断，因此一个 suspended outcome MAY 完全不携带
中断 id。
