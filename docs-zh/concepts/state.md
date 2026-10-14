---
title: "状态管理"
description:
  "理解 AG-UI 中智能体与前端之间的状态同步"
---
<em class="lead">理解 AG-UI 中智能体与前端之间的状态同步</em>

# 状态管理 {#state-management}

状态管理是 AG-UI 协议的核心特性，它使智能体与前端应用之间能够实时同步。通过提供高效的共享和更新状态的机制，AG-UI 为 AI 智能体与人类用户无缝协作的体验奠定了基础。

## 共享状态架构 {#shared-state-architecture}

在 AG-UI 中，状态是一个结构化数据对象，它：

1. 在与智能体交互的过程中持续存在
2. 可被智能体和前端双方访问
3. 随着交互推进实时更新
4. 为双方的决策提供上下文

这种共享状态架构创建了一个双向通信通道，其中：

- 智能体可以访问应用的当前状态，以做出明智的决定
- 前端可以观察并响应智能体内部状态的变化
- 双方都可以修改状态，形成协作式工作流

## 状态同步方法 {#state-synchronization-methods}

AG-UI 提供两种互补的状态同步方法：

### 状态快照 {#state-snapshots}

`STATE_SNAPSHOT` 事件传递智能体当前状态的完整表示：

```typescript
interface StateSnapshotEvent {
  type: EventType.STATE_SNAPSHOT
  snapshot: any // Complete state object
}
```

快照通常用于：

- 在交互开始时建立初始状态
- 在连接中断后确保同步
- 发生需要完整刷新的重大状态变化时
- 为未来的增量更新建立新的基线

当前端收到 `STATE_SNAPSHOT` 事件时，它应该用快照的内容整体替换其现有的状态模型。

### 状态增量 {#state-deltas}

`STATE_DELTA` 事件使用 JSON Patch 格式（RFC 6902）传递状态的增量更新：

```typescript
interface StateDeltaEvent {
  type: EventType.STATE_DELTA
  delta: JsonPatchOperation[] // Array of JSON Patch operations
}
```

增量在带宽上更高效，只发送发生变化的内容，而不是整个状态。这种方式对以下场景尤为有价值：

- 流式交互期间的频繁小更新
- 大部分属性保持不变的大型状态对象
- 以完整快照发送会很低效的高频更新

## JSON Patch 格式 {#json-patch-format}

AG-UI 使用 JSON Patch 格式（RFC 6902）表示状态增量，它定义了一种标准化的方式来表达对 JSON 文档的更改：

```typescript
interface JsonPatchOperation {
  op: "add" | "remove" | "replace" | "move" | "copy" | "test"
  path: string // JSON Pointer (RFC 6901) to the target location
  value?: any // The value to apply (for add, replace)
  from?: string // Source path (for move, copy)
}
```

常见操作包括：

1. **add**：向对象或数组添加一个值

   ```json
   { "op": "add", "path": "/user/preferences", "value": { "theme": "dark" } }
   ```

2. **replace**：替换一个值

   ```json
   { "op": "replace", "path": "/conversation_state", "value": "paused" }
   ```

3. **remove**：移除一个值

   ```json
   { "op": "remove", "path": "/temporary_data" }
   ```

4. **move**：把一个值从一个位置移动到另一个位置
   ```json
   { "op": "move", "path": "/completed_items", "from": "/pending_items/0" }
   ```

前端应按顺序应用这些 patch，以维持准确的状态表示。如果应用 patch 后检测到不一致，前端可以请求一份新的 `STATE_SNAPSHOT`。

## AG-UI 中的状态处理 {#state-processing-in-agui}

在 AG-UI 的实现中，状态增量使用 `fast-json-patch` 库来应用：

```typescript
case EventType.STATE_DELTA: {
  const { delta } = event as StateDeltaEvent;

  try {
    // Apply the JSON Patch operations to the current state without mutating the original
    const result = applyPatch(state, delta, true, false);
    state = result.newDocument;
    return emitUpdate({ state });
  } catch (error: unknown) {
    console.warn(
      `Failed to apply state patch:\n` +
      `Current state: ${JSON.stringify(state, null, 2)}\n` +
      `Patch operations: ${JSON.stringify(delta, null, 2)}\n` +
      `Error: ${errorMessage}`
    );
    return emitNoUpdate();
  }
}
```

该实现确保：

- Patch 以原子方式应用（要么全部成功，要么全部不应用）
- 应用过程中不会改动原始状态
- 错误会被捕获并优雅处理

## Human-in-the-Loop 协作 {#humanintheloop-collaboration}

共享状态系统是 AG-UI 中 human-in-the-loop 工作流的基础。它使以下能力成为可能：

1. **实时可见性**：用户可以观察智能体的思考过程和当前状态
2. **上下文感知**：智能体可以访问用户操作、偏好和应用状态
3. **协同决策**：人和 AI 都可以对不断演进的状态做出贡献
4. **反馈回路**：人可以通过修改状态属性来纠正或引导智能体

例如，智能体可能会用一个拟议的操作来更新其状态：

```json
{
  "proposal": {
    "action": "send_email",
    "recipient": "client@example.com",
    "content": "Draft email content..."
  }
}
```

前端可以把这份提案展示给用户，用户随后可以在执行前批准、拒绝或修改它。

## CopilotKit 实现 {#copilotkit-implementation}

[CopilotKit](https://docs.copilotkit.ai) 是一个用于构建 AI 助手的流行框架，它通过其 “shared state” 特性利用 AG-UI 的状态管理系统。该实现使智能体（尤其是 LangGraph 智能体）与前端应用之间能够双向同步状态。

CopilotKit 的共享状态系统通过以下方式实现：

```jsx
// In the frontend React application
const { state: agentState, setState: setAgentState } = useCoAgent({
  name: "agent",
  initialState: { someProperty: "initialValue" },
})
```

这个 hook 建立了与智能体状态的实时连接，从而可以：

1. 在前端读取智能体的当前状态
2. 从前端更新智能体的状态
3. 基于智能体的状态渲染 UI 组件

在后端，LangGraph 智能体可以这样发出状态更新：

```python
# In the LangGraph agent {#in-the-langgraph-agent}
async def tool_node(self, state: ResearchState, config: RunnableConfig):
    # Update state with new information
    tool_state = {
        "title": new_state.get("title", ""),
        "outline": new_state.get("outline", {}),
        "sections": new_state.get("sections", []),
        # Other state properties...
    }

    # Emit updated state to frontend
    await copilotkit_emit_state(config, tool_state)

    return tool_state
```

这些状态更新使用 AG-UI 的状态快照和增量机制传输，在智能体与前端之间形成无缝的共享上下文。

## 最佳实践 {#best-practices}

在 AG-UI 中实现状态管理时：

1. **审慎使用快照**：只有在建立基线确有必要时才发送完整快照。
2. **增量变更优先使用增量**：小幅状态更新应使用增量，以尽量减少数据传输。
3. **审慎设计状态结构**：设计状态对象时考虑支持部分更新，并尽量减少 patch 的复杂度。
4. **处理状态冲突**：为来自智能体和前端的冲突更新实现解决策略。
5. **包含错误恢复**：提供在检测到不一致时重新同步状态的机制。
6. **考虑安全影响**：避免在共享状态中存储敏感信息。

## 结语 {#conclusion}

AG-UI 的状态管理系统为构建人与 AI 智能体协作的应用提供了强大的基础。通过在前后端之间借助快照和 JSON Patch 增量高效地同步状态，AG-UI 使融合人类直觉与 AI 能力双方优势的复杂 human-in-the-loop 工作流成为可能。

CopilotKit 等框架中的实现表明，这种共享状态方式可以创造出比完全自主的系统或传统用户界面都更有效的协作体验。
