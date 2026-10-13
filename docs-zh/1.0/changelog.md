---
title: "主要变更"
description: "1.0 相对于 0.x 系列的变更 — 1.0"
---
<em class="lead">1.0 相对于 0.x 系列的变更</em>

本页列出 1.0 相对于协议 0.x 系列的行为变更，供熟悉 0.x、只想知道差异
而不想看整份文档的审阅者参考。本页是资料性的：被链接的页面才是规范。

## 主要变更 {#major-changes}

1. **规范存在了。** 0.x 只定义了形状；行为存在于 TypeScript 客户端中。
   这些页面上的规则——顺序、未知与畸形的区分、警告、归属——现在是
   规范性的，用 [BCP 14](https://datatracker.ietf.org/doc/html/bcp14)
   的语言书写，[模式](schema.md) 对结构具有权威，本文档对行为具有权威。

2. **运行报告其结束方式。** `RUN_FINISHED` 携带一个可选的 `outcome`：
   缺失或成功表示成功，中断结果（outcome）携带运行正在等待的内容，
   [取消结果](events/lifecycle.md#cancelled-runs) 标记在运行完成之前
   被有意停止的运行。随之而来的是 `Interrupt`、运行输入中的
   [恢复条目](basic/run-input.md)，以及[中断–恢复模式](basic/patterns/interrupt-resume.md)。
   在所有结果机制出现之前写好的每个生产方已经都是符合的。

3. **子智能体。** 被委派的工作通过可承载该字段的
   事件上的 `subagentRunId` 进行归属，可选地由 `SUBAGENT_STARTED` 宣布，
   由 `SUBAGENT_FINISHED` 或 `SUBAGENT_ERROR` 结束，并受
   [关于所有权、嵌套、并行与终止的规则](events/subagents.md) 约束。

4. **推理取代 thinking。** 0.x 的 `THINKING_*` 事件被弃用，
   取而代之的是[推理族](events/reasoning.md)：span、按 `messageId`
   匹配的流式推理消息，以及用于提供方产物的 `REASONING_ENCRYPTED_VALUE`——
   消费方存储并原样返回、而无需读取。被弃用的形状在
   [兼容性边界](basic/versioning.md#retired-shapes) 处被翻译，
   而非被丢弃。

5. **活动事件。** `ACTIVITY_SNAPSHOT` 和 `ACTIVITY_DELTA` 以消息的形式
   承载[结构化进度](events/activity.md)，其内容是一个对象，
   由 JSON Patch 修订。

6. **未知与畸形，成为规范性内容。** 未识别的事件、字段和联合体成员
   存活到强制执行阶段——该阶段丢弃未知事件、剥离未知成员，并边走边发出
   警告；畸形的已知值则是致命的。在翻译器有机会处理之前，什么都不被
   移除，且两种传输都汇入同一条[处理流水线](basic/processing.md)，
   该流水线还陈述了其对块字段唯一认可的收窄。

7. **分块形式有了规则。** 首个块 MUST 携带开启所必需的内容（文本的
   `messageId` 与角色语义，工具调用的 `toolCallId` 与 `toolCallName`）；
   后续块 MAY 省略它们；一个重复了开启字段但取值冲突的延续块是致命的
   （[流式模式](basic/patterns/streaming.md)）。

8. **二进制线上格式。** [HTTP + Protobuf 传输绑定](basic/transports/http-protobuf.md)
   被规定了——通过媒体类型协商，4 字节长度前缀帧，从同一个模式生成，
   并以共享字节语料固定跨实现的等价性。

9. **能力进入模式。** SDK 以三份手写副本承载的 `AgentCapabilities`
   声明现在只定义一次，就定义在模式中，并为每个 SDK 生成。其语义
   被明确陈述：省略表示未声明，声明是资料性的、而事件流具有权威，
   并且获取方式刻意留给实现决定（[能力](basic/capabilities.md)）。
   子智能体列表拼作 `subagents`，与 `subagentRunId` 一致；早前的
   `subAgents` 键不被读取。

10. **工具结果携带内容部分（parts）。** `TOOL_CALL_RESULT.content` 和它
    铸造的工具消息接受字符串，或接受与用户消息承载的相同部分的有序
    列表，于是工具可以返回一份文档、一张图片或一条搜索结果，而无须
    将其编码为字符串（[工具调用](events/tool-calls.md#result-content)）。
    各部分为此更名——`InputContent` → `ContentPart`、`TextInputContent` →
    `TextPart`、`ImageInputContent` → `ImagePart`，以此类推，
    `InputContentSource` → `PartSource`，含 `DataSource` 与 `UrlSource`——
    因为按方向命名的部分一旦流向另一边就是错名。线上格式不变：
    每个 `type` 取值都相同，只有定义名和锚点移动，且 SDK 保留旧名
    作为别名。每个部分都新增一个可选的 `id`，文本部分新增了媒体部分
    早已有的 `metadata`。`ReasoningPart`、`ToolCallPart` 和 `AssistantPart`
    为助手消息也承载部分的那个版本保留。

## 次要变更 {#minor-changes}

1. 运行输入上的 `tools` 和 `context` 是可选的：缺失与空表示同一件事
   （[运行输入](basic/run-input.md)）。
2. 元数据合并语义成为规范性内容：按键逐键进行，最后一次写入获胜，
   不递归，按事件族指定合并目标；`ag-ui` 键为保留键
   （[元数据](basic/metadata.md)）。
3. 缺失就是缺失：可选字段被省略，绝不发送 `null`
   （[事件模型](basic/index.md#absent-means-absent)）。
4. `RUN_FINISHED` 和 `RUN_ERROR` MAY 携带按提供方划分的 token 用量，
   采用单一核算口径：输入与输出计数是总量，缓存 token 与推理 token
   是其中的组成部分，缓存读取与缓存写入分开报告，且用量跟随运行边界——
   子智能体的调用计入，子运行与恢复运行的调用计出
   （[运行与步骤](events/lifecycle.md#token-usage)）。
5. 因前端工具调用而停止的运行为成功结束，绝不为中断，且成功结果
   MAY 在 `pendingToolCallIds` 中指明它留下的未应答调用
   （[工具调用](events/tool-calls.md#frontend-tools)）。
6. 输入消息 MAY 携带多模态内容部分（文本、图像、音频、视频、文档），
   以 URL、内联数据或提供方文件句柄的形式——`file` 源，1.0 新增，
   用于已上传至模型提供方的字节（[运行输入](basic/run-input.md#provider-file-handles)）。
7. `TOOL_CALL_RESULT` 本身就是一条消息，且不会重新打开它所应答的调用
   （[工具调用](events/tool-calls.md)）。
8. 允许在 `RUN_FINISHED` 之后出现迟到的 `RUN_ERROR`，报告在成功已
   被报告之后才浮现的失败（[运行与步骤](events/lifecycle.md)）。
9. 消费方将其拒绝的事件流与运行自行报告的失败区分开来，且
   “将该运行视为失败”被定义了：呈现它，绝不报告成功，API 形状
   留给实现（[运行与步骤](events/lifecycle.md#error-handling)）。
10. 协议版本带内传递：消费方在 `RunAgentInput.protocolVersion` 上声明
    自己的版本，生产方在 `RUN_STARTED.protocolVersion` 上以自己的版本
    回应，缺失则标识出未版本化的通信方
    （[版本化](basic/versioning.md#version-negotiation)）。
