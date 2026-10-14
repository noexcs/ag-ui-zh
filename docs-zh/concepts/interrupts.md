---
title: "中断"
description: "Agent User Interaction Protocol 中的 human-in-the-loop 暂停与恢复"
---
<em class="lead">Agent User Interaction Protocol 中的 human-in-the-loop 暂停与恢复</em>

智能体有时需要暂停：在执行敏感操作前获得人工批准、请求结构化输入，或等待带外策略决策。
AG-UI 将其暴露为**可感知中断的运行生命周期** — 一种终结模型：运行以中断结果结束，
客户端随后发起一次新的运行，并携带针对各中断的响应。

## 生命周期 {#lifecycle}

```mermaid
sequenceDiagram
  participant Agent
  participant Client as Client App

  Note over Agent,Client: Run 1 begins
  Agent-->>Client: RunStarted (runId: r1)
  Agent-->>Client: ...ToolCall* / TextMessage* / StateSnapshot...
  Note over Agent,Client: Agent needs user input — emit snapshot, then interrupt
  Agent-->>Client: RunFinished { outcome: { type: "interrupt", interrupts: [...] } }

  Note over Agent,Client: User resolves interrupts
  Client-->>Agent: RunAgentInput { threadId, resume: [{interruptId, status, payload?}, ...] }

  Note over Agent,Client: Run 2 begins; resume[].interruptId links back to run 1's interrupts
  Agent-->>Client: RunStarted (runId: r2)
  Agent-->>Client: ...continue / ToolCallResult / ...
  Agent-->>Client: RunFinished { outcome: { type: "success" }, result }
```

## 运行结果 {#run-outcomes}

`RunFinished` 携带一个可选的 `outcome` 字段 — 一个判别联合，其变体特定数据嵌套在内部：

- **省略** — 旧版/向后兼容。按正常完成处理。尚不了解中断的既有
  AG-UI 客户端仍会发出这种形状，新的读取方也应接受它。
- `{ type: "success" }` — 运行正常完成。可选的 `result`
  出于向后兼容仍保留在事件的根上。
- `{ type: "interrupt", interrupts: [...] }` — 运行因等待用户输入而暂停。
  `interrupts` 是非空数组，且它位于 outcome 内部，因此随需要它的变体一起传递。

```typescript
type RunFinishedOutcome =
  | { type: "success" }
  | { type: "interrupt"; interrupts: Interrupt[] }

type RunFinishedEvent = {
  type: "RUN_FINISHED"
  threadId: string
  runId: string
  result?: unknown
  outcome?: RunFinishedOutcome
}
```

由于 `outcome` 是可选的，一个从未听说过中断的旧版生产方（没有 `outcome` 字段）
在新 schema 下仍可作为 `RunFinished` 事件通过校验 — 客户端只需在关心可感知中断
变体时才检查 `outcome`。

## Interrupt 类型 {#the-interrupt-type}

```typescript
type Interrupt = {
  id: string
  reason: string
  message?: string
  toolCallId?: string
  responseSchema?: JsonSchema
  expiresAt?: string
  metadata?: Record<string, any>
  subagentRunId?: string
}
```

| 字段 | 用途 |
| --- | --- |
| `id` | 跨越中断、恢复、幂等性与审计的关联键。 |
| `reason` | 分类路由提示 — 见[原因分类](#reason-taxonomy)。 |
| `message` | 人类可读的提示。通用的回退 UI 内容。 |
| `toolCallId` | 将该中断绑定到之前的 `ToolCall*` 序列。 |
| `responseSchema` | 期望的 `resume.payload` 的 JSON Schema。 |
| `expiresAt` | 可选的 ISO-8601 TTL。过期的恢复会产生 `RunError`。 |
| `metadata` | 自由形式的框架特定数据。 |
| `subagentRunId` | 其工作引发该中断的子智能体 — 若由根智能体引发则缺失。归属信息按中断记录，因为一次运行可以携带来自多个子智能体的中断。发出子智能体生命周期事件的生产方还会以 `outcome: { type: "suspended" }` 关闭该子智能体 — 生命周期事件仍是可选的，因此此处的归属信息本身即有效（见[子智能体](./subagents.md#suspension)）。 |

## 恢复一次运行 {#resuming-a-run}

同一会话上的下一个 `RunAgentInput` 携带一个 `resume` 数组：

```typescript
type RunAgentInput = {
  // ... existing fields
  resume?: Array<{
    interruptId: string
    status: "resolved" | "cancelled"
    payload?: any
    metadata?: Record<string, any>
  }>
}
```

- `resolved` — 用户已作出响应。`payload` 携带响应，并依据该中断的
  `responseSchema` 进行校验。拒绝在 payload 内部表达（例如 `{ approved: false }`），
  而不是作为单独的状态。
- `cancelled` — 用户放弃，未提供有意义的输入。
  应省略 `payload`。
- `metadata` — 关于该响应的可选信封数据（例如证明人类决定未被篡改的签名，
  或路由键），与之相对，`payload` 是智能体所请求并会据以行动的答案。
  按 key 开放；任一 key 下允许任意 JSON 值，包括 `null`。该对象本身要么缺失，
  要么是对象，绝不会是 `null`。`ag-ui` key 保留给 AG-UI 自身使用。
  两种状态均允许使用。

## 契约规则 {#contract-rules}

1. **同一会话。** 恢复请求必须使用与被中断运行相同的 `threadId`。
2. **恢复关联。** `resume[].interruptId` 必须引用被中断运行的 `interrupts[]`
   中的某个 `id`。`parentRunId` 与之正交 — 它保留其现有的
   AG-UI 分支/时间旅行语义。
3. **覆盖所有未决中断。** 单个 `resume` 数组必须处理被中断运行中的每一个
   未决中断。不支持部分恢复。
4. **未决中断会阻止新输入。** 如果某个会话存在未解决的中断，那么该会话上的任何
   `RunAgentInput` 都必须包含处理它们的 `resume`。接收到不符合规范输入的智能体
   必须发出 `RunError`。
5. **幂等性。** 具有相同 `(threadId, interruptId, status, payload)` 的恢复
   必须可以安全重放。
6. **载荷校验。** 如果某中断声明了 `responseSchema`，智能体可以校验对应的恢复
   `payload`，并在不匹配时发出 `RunError`。客户端应在提交前自行校验。
7. **过期强制执行。** 客户端不得在中断的 `expiresAt` 之后提交恢复。
   过期的恢复会产生 `RunError`。
8. **优雅处理。** 智能体应通过 `RunError` 处理缺失或无效的恢复载荷，
   而不是静默失败。

## 中断边界处的状态 {#state-at-the-interrupt-boundary}

在中断发生的那一刻，智能体必须在携带该中断的 `RunFinished` 事件**之前**，
通过 `StateSnapshot` 与 `MessagesSnapshot` 事件发出恢复所需的一切状态。

这条规则使协议与恢复模式无关：无论是重放式续接（从消息 + 状态重建上下文）
还是检查点式续接（恢复被挂起的协程），都必须在恢复时产生相同的可观察行为。
框架原生的检查点机制是一种实现优化，而非协议契约。

## 错误处理 {#error-handling}

`RunError` 是唯一的错误事件。`outcome` 枚举不携带 `"error"` 值。
会产生 `RunError` 的中断特定错误情况：

- 恢复在中断的 `expiresAt` 之后到达。
- 恢复载荷未能通过其 `responseSchema` 的校验。
- 恢复引用了智能体无法关联的 `interruptId`。
- 恢复未能处理每一个未决中断（违反规则 3）。
- 在存在未决中断的会话上，某个 `RunAgentInput` 省略了 `resume`
  （违反规则 4）。

## 原因分类 {#reason-taxonomy}

`reason` 是必需的字符串。一小组核心值由规范定义；任何其他字符串都是有效的扩展。

### 核心值 {#core-values}

| 值 | 语义 | 典型配套字段 |
| --- | --- | --- |
| `tool_call` | 绑定到某个等待决定的工具调用的中断。 | 必须设置 `toolCallId`。 |
| `input_required` | 智能体需要结构化输入才能继续。 | 应设置 `responseSchema`。 |
| `confirmation` | 未绑定到工具的独立是/否决定。 | `responseSchema` 可选；默认为布尔值。 |

### 自定义原因 {#custom-reasons}

任何其他字符串都是有效的。智能体应将自定义原因命名空间化为
`<framework>:<name>`（例如 `langgraph:database_modification`、
`mastra:workflow_suspend`）。`core:` 前缀保留给未来的规范新增内容。

### 客户端路由 {#client-routing}

- 客户端应针对已知的核心值进行分支，以提供专用 UI。
- 对于未知原因，客户端不得报错。应基于 `message`、
  `responseSchema` 与 `metadata` 进行渲染。

## 绑定工具的中断 {#toolbound-interrupts}

当中断携带 `reason: "tool_call"` 与 `toolCallId` 时，该工具调用及其解决过程跨越两次运行。
完整审计轨迹为：

1. 被中断运行的 `ToolCallArgs`（智能体的提议）。
2. 恢复运行的 `RunAgentInput.resume` 载荷（用户决定与修改）。
3. 恢复运行的 `ToolCallResult`（实际执行结果）。

智能体**不会**在恢复运行中重新发出 `ToolCallStart`/`ToolCallArgs`/`ToolCallEnd`
— 它针对原始 `toolCallId` 发出 `ToolCallResult`。

### 带修改批准 {#approve-with-edits}

对于支持带修改批准的绑定工具的中断，推荐的 `responseSchema` 模式：

```json
{
  "type": "object",
  "properties": {
    "approved": { "type": "boolean" },
    "editedArgs": {
      "type": "object",
      "description": "Full replacement of the tool args. Not merged."
    }
  },
  "required": ["approved"]
}
```

`editedArgs` 是完整替换，而不是部分合并。它在 schema 中的存在即是**能力信号**，
表明客户端可以提供编辑 UI。

## 示例 {#examples}

### 最小工具批准 {#minimal-tool-approval}

智能体在提议 `sendEmail` 之后中断：

```json
{
  "type": "RUN_FINISHED",
  "threadId": "thread-1",
  "runId": "run-1",
  "outcome": {
    "type": "interrupt",
    "interrupts": [
      {
        "id": "int-abc123",
        "reason": "tool_call",
        "message": "Send email to a@b.com with subject 'Hi'?",
        "toolCallId": "tc-001",
        "responseSchema": {
          "type": "object",
          "properties": { "approved": { "type": "boolean" } },
          "required": ["approved"]
        }
      }
    ]
  }
}
```

客户端提交恢复：

```json
{
  "threadId": "thread-1",
  "runId": "run-2",
  "resume": [
    { "interruptId": "int-abc123", "status": "resolved", "payload": { "approved": true } }
  ]
}
```

智能体在 `run-2` 中继续，针对 `tc-001` 发出 `ToolCallResult`，然后发出
`RunFinished { outcome: { type: "success" } }`。

### 带修改批准（完整审计） {#approve-with-edits-full-audit}

```json
{
  "type": "RUN_FINISHED",
  "threadId": "thread-2",
  "runId": "run-10",
  "outcome": {
    "type": "interrupt",
    "interrupts": [
      {
        "id": "int-email-edit",
        "reason": "tool_call",
        "message": "Send email to a@b.com? You can edit the body before approving.",
        "toolCallId": "tc-42",
        "responseSchema": {
          "type": "object",
          "properties": {
            "approved": { "type": "boolean" },
            "editedArgs": {
              "type": "object",
              "properties": {
                "to": { "type": "string", "format": "email" },
                "subject": { "type": "string" },
                "body": { "type": "string" }
              }
            }
          },
          "required": ["approved"]
        },
        "metadata": {
          "langgraph": {
            "checkpointId": "ckpt-xyz",
            "nodeId": "tool_executor"
          }
        }
      }
    ]
  }
}
```

客户端带修改的恢复：

```json
{
  "threadId": "thread-2",
  "runId": "run-11",
  "resume": [
    {
      "interruptId": "int-email-edit",
      "status": "resolved",
      "payload": {
        "approved": true,
        "editedArgs": {
          "to": "a@b.com",
          "subject": "Hi",
          "body": "Hi (revised per my note)"
        }
      }
    }
  ]
}
```

`tc-42` 的审计轨迹：

- `run-10` 的 `ToolCallArgs` — 原始提议。
- `run-11` 的 `RunAgentInput.resume[0].payload.editedArgs` — 用户修改。
- `run-11` 的 `ToolCallResult` — 实际结果。

### 并行中断 {#parallel-interrupts}

```json
{
  "type": "RUN_FINISHED",
  "threadId": "thread-3",
  "runId": "run-20",
  "outcome": {
    "type": "interrupt",
    "interrupts": [
      { "id": "i-1", "reason": "tool_call", "toolCallId": "tc-a", "message": "Approve sendEmail to x@y.com?" },
      { "id": "i-2", "reason": "tool_call", "toolCallId": "tc-b", "message": "Approve sendEmail to y@z.com?" },
      { "id": "i-3", "reason": "tool_call", "toolCallId": "tc-c", "message": "Approve sendEmail to z@w.com?" }
    ]
  }
}
```

客户端批准两个，取消一个：

```json
{
  "threadId": "thread-3",
  "runId": "run-21",
  "resume": [
    { "interruptId": "i-1", "status": "resolved", "payload": { "approved": true } },
    { "interruptId": "i-2", "status": "resolved", "payload": { "approved": true } },
    { "interruptId": "i-3", "status": "cancelled" }
  ]
}
```

在 `run-21` 中，智能体针对 `tc-a` 与 `tc-b` 发出 `ToolCallResult`，
并将 `tc-c` 视为未执行。

### 非工具输入请求 {#nontool-input-request}

```json
{
  "type": "RUN_FINISHED",
  "threadId": "thread-4",
  "runId": "run-30",
  "outcome": {
    "type": "interrupt",
    "interrupts": [
      {
        "id": "int-form",
        "reason": "input_required",
        "message": "Please provide the quarterly filing details.",
        "responseSchema": {
          "type": "object",
          "properties": {
            "quarter": { "type": "string", "enum": ["Q1", "Q2", "Q3", "Q4"] },
            "year": { "type": "integer", "minimum": 2000 },
            "revenue": { "type": "number" }
          },
          "required": ["quarter", "year", "revenue"]
        },
        "expiresAt": "2026-04-20T17:00:00Z"
      }
    ]
  }
}
```

客户端响应：

```json
{
  "threadId": "thread-4",
  "runId": "run-31",
  "resume": [
    {
      "interruptId": "int-form",
      "status": "resolved",
      "payload": { "quarter": "Q1", "year": 2026, "revenue": 4200000 }
    }
  ]
}
```

## 框架集成 {#framework-integrations}

| 框架 | 包 | 中断支持 |
| --- | --- | --- |
| LangGraph | `@ag-ui/langgraph` / `ag-ui-langgraph` | ✅ 接受 `RunAgentInput.resume[]`。可以发出 `RunFinishedEvent.outcome = {type:"interrupt"}` — 通过 `emitInterruptOutcome` / `emit_interrupt_outcome` 选择启用（默认关闭；通过 `command.resume` 恢复的旧版客户端一旦看到结构化 outcome 便不再恢复）。默认发出旧版 `CustomEvent(name="on_interrupt")`；可通过 `enableLegacyOnInterruptEvent: false` 禁用。提供子类钩子用于自定义 HITL 转换。 |
| AWS Strands | `@ag-ui/aws-strands` | ✅ 通过 `RunFinishedEvent.outcome` 转发原生 Strands 中断。 |

## 相关 {#related}

- [事件](./events.md) — `RunFinished` 如何融入更广泛的事件流。
- [能力](./capabilities.md) — 智能体声明的 `humanInTheLoop.interrupts` 与
  `humanInTheLoop.approveWithEdits` 标志。
