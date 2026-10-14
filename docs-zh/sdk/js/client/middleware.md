---
title: "中间件"
description: "面向 AG-UI 智能体的事件流变换与过滤"
---
<em class="lead">面向 AG-UI 智能体的事件流变换与过滤</em>

# 中间件 {#middleware}

`@ag-ui/client` 中的中间件系统提供了一种强大的方式，用来变换、过滤和增强流经智能体的事件流。中间件可以拦截并修改事件、添加日志、实现认证、过滤工具调用等等。

```typescript
import {
  AbstractAgent,
  BaseEvent,
  EventType,
  FilterToolCallsMiddleware,
  Message,
  Middleware,
  MiddlewareFunction,
  RunAgentInput
} from "@ag-ui/client"
import { Observable } from "rxjs"
```

下方示例假定相关的 RxJS 操作符/工具（`map`、`tap`、`filter`、`finalize`、`catchError`、`switchMap`、`timer`、`of` 等）已经导入。

## 类型 {#types}

### MiddlewareFunction {#middlewarefunction}

一个用于变换事件流的函数。

```typescript
type MiddlewareFunction = (
  input: RunAgentInput,
  next: AbstractAgent
) => Observable<BaseEvent>
```

函数式中间件接收的事件与下一个中间件或智能体所发出的完全一致。

### Middleware {#middleware}

用于创建中间件的抽象基类。

```typescript
interface EventWithState {
  event: BaseEvent
  messages: Message[]
  state: unknown
}

abstract class Middleware {
  abstract run(
    input: RunAgentInput,
    next: AbstractAgent
  ): Observable<BaseEvent>

  protected runNext(
    input: RunAgentInput,
    next: AbstractAgent
  ): Observable<BaseEvent>

  protected runNextWithState(
    input: RunAgentInput,
    next: AbstractAgent
  ): Observable<EventWithState>
}
```

- `runNext()` 运行 `next.run(...)`，并把块事件规范化为完整的 `TEXT_MESSAGE_*` / `TOOL_CALL_*` 序列。
- `runNextWithState()` 做同样的事，并且还提供每个事件被应用之后累积的 `messages` 与 `state`。

## 基于函数的中间件 {#functionbased-middleware}

创建中间件最简单的方式是使用函数。函数式中间件非常适合无状态的变换。

### 基本示例 {#basic-example}

```typescript
const loggingMiddleware: MiddlewareFunction = (input, next) => {
  console.log(`[${new Date().toISOString()}] Starting run ${input.runId}`)

  return next.run(input).pipe(
    tap(event => console.log(`Event: ${event.type}`)),
    finalize(() => console.log(`Run ${input.runId} completed`))
  )
}

agent.use(loggingMiddleware)
```

### 变换事件 {#transforming-events}

```typescript
const timestampMiddleware: MiddlewareFunction = (input, next) => {
  return next.run(input).pipe(
    map(event => {
      if (event.type === EventType.RUN_STARTED) {
        return {
          ...event,
          timestamp: Date.now()
        }
      }
      return event
    })
  )
}
```

### 错误处理 {#error-handling}

```typescript
const errorMiddleware: MiddlewareFunction = (input, next) => {
  return next.run(input).pipe(
    catchError(error => {
      console.error("Agent error:", error)

      // Return error event
      return of({
        type: EventType.RUN_ERROR,
        message: error.message
      } as BaseEvent)
    })
  )
}
```

## 基于类的中间件 {#classbased-middleware}

对于有状态的操作或复杂的逻辑，请继承 `Middleware` 类。

### 基本实现 {#basic-implementation}

```typescript
class CounterMiddleware extends Middleware {
  private totalEvents = 0

  run(input: RunAgentInput, next: AbstractAgent): Observable<BaseEvent> {
    let runEvents = 0

    return this.runNext(input, next).pipe(
      tap(() => {
        runEvents++
        this.totalEvents++
      }),
      finalize(() => {
        console.log(`Run events: ${runEvents}, Total: ${this.totalEvents}`)
      })
    )
  }
}

agent.use(new CounterMiddleware())
```

### 基于配置的中间件 {#configurationbased-middleware}

```typescript
class AuthMiddleware extends Middleware {
  constructor(
    private apiKey: string,
    private headerName: string = "Authorization"
  ) {
    super()
  }

  run(input: RunAgentInput, next: AbstractAgent): Observable<BaseEvent> {
    // Attach auth data in forwardedProps for downstream transport/agent logic
    const authenticatedInput: RunAgentInput = {
      ...input,
      forwardedProps: {
        ...input.forwardedProps,
        auth: {
          headerName: this.headerName,
          value: `Bearer ${this.apiKey}`
        }
      }
    }

    return this.runNext(authenticatedInput, next)
  }
}

const apiKey = process.env.API_KEY ?? ""
agent.use(new AuthMiddleware(apiKey))
```

## 累积器辅助方法（类中间件） {#accumulator-helpers-class-middleware}

类中间件可以使用 `Middleware` 的辅助方法，以处理规范化的事件和累积的状态。

### `runNext()` {#runnext}

`runNext()` 转发执行，并把块事件规范化为完整的 `TEXT_MESSAGE_*` 和 `TOOL_CALL_*` 事件。

### `runNextWithState()` {#runnextwithstate}

`runNextWithState()` 返回 `{ event, messages, state }`，其中 `messages` 和 `state` 是每个事件被应用之后累积的值。

```typescript
class MetricsWithStateMiddleware extends Middleware {
  run(input: RunAgentInput, next: AbstractAgent): Observable<BaseEvent> {
    return this.runNextWithState(input, next).pipe(
      tap(({ event, messages, state }) => {
        if (event.type === EventType.RUN_FINISHED) {
          const stateKeyCount =
            state && typeof state === "object" ? Object.keys(state).length : 0

          console.log("Assistant messages:", messages.filter(m => m.role === "assistant").length)
          console.log("Final state keys:", stateKeyCount)
        }
      }),
      map(({ event }) => event)
    )
  }
}
```

## 内置中间件 {#builtin-middleware}

### FilterToolCallsMiddleware {#filtertoolcallsmiddleware}

根据允许列表或禁止列表过滤工具调用。

`FilterToolCallsMiddleware` 过滤已发出的 `TOOL_CALL_*` 事件（包括被阻止调用的参数/结果）。它不会阻止上游模型/运行时中的工具执行。

```typescript
import { FilterToolCallsMiddleware } from "@ag-ui/client"
```

#### 配置 {#configuration}

```typescript
type FilterToolCallsConfig =
  | { allowedToolCalls: string[]; disallowedToolCalls?: never }
  | { disallowedToolCalls: string[]; allowedToolCalls?: never }
```

#### 允许特定工具 {#allow-specific-tools}

```typescript
const allowFilter = new FilterToolCallsMiddleware({
  allowedToolCalls: ["search", "calculate", "summarize"]
})

agent.use(allowFilter)
```

#### 阻止特定工具 {#block-specific-tools}

```typescript
const blockFilter = new FilterToolCallsMiddleware({
  disallowedToolCalls: ["deleteFile", "sendEmail"]
})

agent.use(blockFilter)
```

你必须且只能指定 `allowedToolCalls` 或 `disallowedToolCalls` 之一。若两者都提供或都不提供，构造函数会抛出异常。

## 中间件模式 {#middleware-patterns}

### 计时中间件 {#timing-middleware}

```typescript
const timingMiddleware: MiddlewareFunction = (input, next) => {
  const startTime = performance.now()

  return next.run(input).pipe(
    finalize(() => {
      const duration = performance.now() - startTime
      console.log(`Execution time: ${duration.toFixed(2)}ms`)
    })
  )
}
```

### 速率限制 {#rate-limiting}

```typescript
class RateLimitMiddleware extends Middleware {
  private lastCall = 0

  constructor(private minInterval: number) {
    super()
  }

  run(input: RunAgentInput, next: AbstractAgent): Observable<BaseEvent> {
    const now = Date.now()
    const elapsed = now - this.lastCall

    if (elapsed < this.minInterval) {
      // Delay the execution
      return timer(this.minInterval - elapsed).pipe(
        switchMap(() => {
          this.lastCall = Date.now()
          return this.runNext(input, next)
        })
      )
    }

    this.lastCall = now
    return this.runNext(input, next)
  }
}

// Limit to one request per second
agent.use(new RateLimitMiddleware(1000))
```

其他常见模式包括重试逻辑和响应缓存。

## 串联中间件 {#chaining-middleware}

多个中间件可以组合起来，构建复杂的处理流水线。

```typescript
const logger = loggingMiddleware
const auth = new AuthMiddleware(apiKey)
const filter = new FilterToolCallsMiddleware({ allowedToolCalls: ["search"] })

agent.use(logger, auth, filter)

// Execution flow:
// logger → auth → filter → agent → filter → auth → logger
```

## 进阶用法 {#advanced-usage}

### 条件中间件 {#conditional-middleware}

```typescript
const debugMiddleware: MiddlewareFunction = (input, next) => {
  const isDebug = input.forwardedProps?.debug === true

  if (!isDebug) {
    return next.run(input)
  }

  return next.run(input).pipe(
    tap(event => {
      console.debug("[DEBUG]", JSON.stringify(event, null, 2))
    })
  )
}
```

## 生命周期说明 {#lifecycle-notes}

通过 `agent.use(...)` 添加的中间件会在 `runAgent()` 中运行（以及遗留的 bridge 路径）。`connectAgent()` 目前直接调用 `connect()`，不会运行中间件。

## 最佳实践 {#best-practices}

1. **单一职责**：每个中间件应专注于一个关注点
2. **错误处理**：始终优雅地处理错误，并考虑恢复策略
3. **性能**：在高吞吐场景中注意处理开销
4. **状态管理**：需要状态时使用基于类的中间件
5. **测试**：为每个中间件独立编写单元测试
6. **文档**：记录中间件的行为与副作用

## TypeScript 支持 {#typescript-support}

中间件系统具有完整的类型定义，可提供出色的 IDE 支持：

```typescript
import {
  AbstractAgent,
  BaseEvent,
  MiddlewareFunction,
  RunAgentInput
} from "@ag-ui/client"
import { Observable } from "rxjs"

// Type-safe middleware function
const typedMiddleware: MiddlewareFunction = (
  input: RunAgentInput,
  next: AbstractAgent
): Observable<BaseEvent> => {
  return next.run(input)
}
```
