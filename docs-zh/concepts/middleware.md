---
title: "中间件"
description: "在 AG-UI 智能体中变换和拦截事件"
---
<em class="lead">在 AG-UI 智能体中变换和拦截事件</em>

# 中间件 {#middleware}

AG-UI 中的中间件提供了一种强大的方式，用来变换、过滤和增强流经智能体的事件流。它让你能够添加日志、认证、速率限制和事件过滤等横切关注点，而无需修改智能体的核心逻辑。

下方示例假定相关的 RxJS 操作符/工具（`map`、`tap`、`catchError`、`switchMap`、`timer` 等）已经导入。

## 什么是中间件？ {#what-is-middleware}

中间件位于智能体执行与事件消费方之间，让你能够：

1. **变换事件** – 在事件流经流水线时修改或增强它们
2. **过滤事件** – 有选择地放行或阻止某些事件
3. **添加元数据** – 注入额外的上下文或追踪信息
4. **处理错误** – 实现自定义的错误恢复策略
5. **监控执行** – 添加日志、指标或调试能力

## 中间件如何工作 {#how-middleware-works}

中间件构成一条链，每个中间件包裹下一个，形成一层层的功能。当智能体运行时，事件流会依次流经每个中间件。

```typescript
import { AbstractAgent } from "@ag-ui/client"

const agent = new MyAgent()

// Middleware chain: logging -> auth -> filter -> agent
agent.use(loggingMiddleware, authMiddleware, filterMiddleware)

// When agent runs, events flow through all middleware
await agent.runAgent()
```

通过 `agent.use(...)` 添加的中间件会在 `runAgent()` 中应用。`connectAgent()` 目前直接调用 `connect()`，不会运行中间件。

## 基于函数的中间件 {#functionbased-middleware}

对于简单的变换，你可以使用基于函数的中间件。这是添加中间件最简洁的方式：

```typescript
import { MiddlewareFunction } from "@ag-ui/client"
import { EventType } from "@ag-ui/core"

const prefixMiddleware: MiddlewareFunction = (input, next) => {
  return next.run(input).pipe(
    map(event => {
      if (
        event.type === EventType.TEXT_MESSAGE_CHUNK ||
        event.type === EventType.TEXT_MESSAGE_CONTENT
      ) {
        return {
          ...event,
          delta: `[AI]: ${event.delta}`
        }
      }
      return event
    })
  )
}

agent.use(prefixMiddleware)
```

## 基于类的中间件 {#classbased-middleware}

对于需要状态或配置的更复杂场景，请使用基于类的中间件：

```typescript
import { Middleware } from "@ag-ui/client"
import { Observable } from "rxjs"
import { tap } from "rxjs/operators"

class MetricsMiddleware extends Middleware {
  private eventCount = 0

  constructor(private metricsService: MetricsService) {
    super()
  }

  run(input: RunAgentInput, next: AbstractAgent): Observable<BaseEvent> {
    const startTime = Date.now()

    return this.runNext(input, next).pipe(
      tap(event => {
        this.eventCount++
        this.metricsService.recordEvent(event.type)
      }),
      finalize(() => {
        const duration = Date.now() - startTime
        this.metricsService.recordDuration(duration)
        this.metricsService.recordEventCount(this.eventCount)
      })
    )
  }
}

agent.use(new MetricsMiddleware(metricsService))
```

如果你在编写类中间件，请优先使用这些辅助方法：
- `runNext(input, next)` 把块事件规范化为完整的 `TEXT_MESSAGE_*`/`TOOL_CALL_*` 序列。
- `runNextWithState(input, next)` 还提供每个事件之后累积的 `messages` 与 `state`。

## 内置中间件 {#builtin-middleware}

AG-UI 为常见用例提供了若干内置中间件组件：

### FilterToolCallsMiddleware {#filtertoolcallsmiddleware}

根据允许列表或禁止列表过滤工具调用：

```typescript
import { FilterToolCallsMiddleware } from "@ag-ui/client"

// Only allow specific tools
const allowedFilter = new FilterToolCallsMiddleware({
  allowedToolCalls: ["search", "calculate"]
})

// Or block specific tools
const blockedFilter = new FilterToolCallsMiddleware({
  disallowedToolCalls: ["delete", "modify"]
})

agent.use(allowedFilter)
```

`FilterToolCallsMiddleware` 过滤已发出的 `TOOL_CALL_*` 事件。它不会阻止上游模型/运行时中的工具执行。

## 中间件模式 {#middleware-patterns}

常见模式包括日志、通过 `forwardedProps` 进行认证，以及速率限制。具体实现参见 [JS 中间件参考](../sdk/js/client/middleware.md)。

## 组合中间件 {#combining-middleware}

你可以组合多个中间件来构建复杂的处理流水线：

```typescript
const logMiddleware: MiddlewareFunction = (input, next) => next.run(input)
const metricsMiddleware = new MetricsMiddleware(metricsService)
const filterMiddleware = new FilterToolCallsMiddleware({ allowedToolCalls: ["search"] })

agent.use(logMiddleware, metricsMiddleware, filterMiddleware)
```

## 执行顺序 {#execution-order}

中间件按其被添加的顺序执行，每个中间件包裹下一个：

1. 第一个中间件接收原始输入
2. 它可以在把输入传给下一个中间件之前修改输入
3. 每个中间件处理来自链中下一个中间件的事件
4. 最后一个中间件调用实际的智能体

```typescript
agent.use(middleware1, middleware2, middleware3)

// Execution flow:
// → middleware1
//   → middleware2
//     → middleware3
//       → agent.run()
//     ← events flow back through middleware3
//   ← events flow back through middleware2
// ← events flow back through middleware1
```

## `RUN_STARTED` 上的协议版本 {#protocol-version-on-runstarted}

每次运行的 `RUN_STARTED.protocolVersion` 指明该运行的流所使用的版本，而不是由谁转发它（[版本管理](../1.0/basic/versioning.md#version-negotiation)）。对中间件而言，这意味着一条规则，由谁产出该运行来决定：

- **转发运行。** 当 `RUN_STARTED` 来自链中的下一个智能体时，原样透传它，其 `protocolVersion` 保持不变。不要添加、覆盖或移除它。如果下游智能体早于该字段出现，那么缺失的声明就是真实情况。
- **合成运行。** 当中间件自行应答请求并发出自己的 `RUN_STARTED`（没有下游智能体运行）时，中间件就是该运行的生产方。用 SDK 的 `PROTOCOL_VERSION` 常量声明它所依据的版本。不要照搬客户端的 `RunAgentInput.protocolVersion`，也不要省略该字段。
- **转换运行。** 把该流改写为另一种协议版本的中间件，声明它所发出的版本。

合成的运行与任何其他生产方一样，使用输入的 `threadId` 和 `runId`：

```typescript
import { EventType, PROTOCOL_VERSION, type RunStartedEvent } from "@ag-ui/client"

const runStarted: RunStartedEvent = {
  type: EventType.RUN_STARTED,
  threadId: input.threadId,
  runId: input.runId,
  protocolVersion: PROTOCOL_VERSION,
}
```

## 最佳实践 {#best-practices}

1. **保持中间件专注** – 每个中间件应只有单一职责
2. **优雅地处理错误** – 使用 RxJS 的错误处理操作符
3. **避免阻塞操作** – I/O 操作使用异步模式
4. **记录副作用** – 清楚标明中间件是否会修改状态
5. **独立测试中间件** – 为每个中间件编写单元测试
6. **考虑性能** – 注意事件流中的处理开销

## 进阶用例 {#advanced-use-cases}

### 条件中间件 {#conditional-middleware}

根据运行时条件应用中间件：

```typescript
const conditionalMiddleware: MiddlewareFunction = (input, next) => {
  if (input.forwardedProps?.debug === true) {
    // Apply debug logging
    return next.run(input).pipe(
      tap(event => console.debug(event))
    )
  }
  return next.run(input)
}
```

关于事件变换和流控制的变体，参见 [JS 中间件参考](../sdk/js/client/middleware.md)。

## 结语 {#conclusion}

中间件提供了一种灵活而强大的方式，让你在不修改核心逻辑的前提下扩展 AG-UI 智能体。无论你需要简单的事件变换，还是复杂的有状态处理，中间件系统都提供了构建健壮、可维护的智能体应用所需的工具。
