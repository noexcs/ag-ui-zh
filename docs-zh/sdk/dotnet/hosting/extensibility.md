---
title: "可扩展性"
description: "使用 AGUIStreamOptions 自定义 AG-UI 流转换"
---
<em class="lead">使用 AGUIStreamOptions 自定义 AG-UI 流转换</em>

# 可扩展性 {#extensibility}

`AGUIStreamOptions` 用于自定义 `ChatResponseUpdate` 流转换为 AG-UI 事件的方式。它支持链式调用且只提供方法：创建一个实例，注册
`Map*` 钩子，然后将其传给 `ToChatRequestContext`。

```csharp
var streamOptions = new AGUIStreamOptions()
    .MapResultAsStateSnapshot("create_plan");

var ctx = input.ToChatRequestContext(jsonSerializerOptions, streamOptions);
```

当你的服务器需要暴露框架特定的内容类型、自定义中断、状态更新或流式工具参数预览时，请使用流选项。

## 内置转换 {#builtin-conversion}

常见路径无需使用流选项。托管层已经映射：

- `TextContent` 到 `TEXT_MESSAGE_*`
- `TextReasoningContent` 到 `REASONING_*`
- `FunctionCallContent` 到 `TOOL_CALL_*`
- `FunctionResultContent` 到 `TOOL_CALL_RESULT`
- `ToolApprovalRequestContent` 与 `InterruptRequestContent` 到中断结果
- 包含 `BaseEvent` 的 `ChatResponseUpdate.RawRepresentation` 直接到该事件

!!! note
    如果 `ChatResponseUpdate.RawRepresentation` 是 `BaseEvent`，托管层会原样发出它。
      这通常是自定义 `IChatClient` 包装器注入 `StateSnapshotEvent`、`CustomEvent` 或
      `RawEvent` 值的最简单方式。

## MapContent {#mapcontent}

`MapContent(Func<AIContent, IEnumerable<BaseEvent>?> mapper)` 接收一个尚未被映射的
`AIContent`，并返回要发出的 AG-UI 事件。返回 `null` 则让下一个映射器尝试处理该内容。

```csharp
using AGUI.Abstractions;
using AGUI.Server;
using Microsoft.Extensions.AI;

public sealed class WorkflowStepContent : AIContent
{
    public string StepName { get; set; } = string.Empty;
}

var streamOptions = new AGUIStreamOptions()
    .MapContent(content =>
        content is WorkflowStepContent step
            ? [new StepStartedEvent { StepName = step.StepName }]
            : null);
```

用于框架特定的内容类型，例如工作流标记、进度通知或领域事件。

!!! tip
    `TextReasoningContent` 已由原生逻辑处理。Step 07 示例会发出
      `TextReasoningContent`，托管层会将其转换为推理事件，无需自定义 `MapContent`
      配置。

## MapInterrupt {#mapinterrupt}

`MapInterrupt(Func<AIContent, AGUIInterrupt?> mapper)` 接收一个尚未被映射的
`AIContent`，并在运行需要用户输入时返回 `AGUIInterrupt`。托管层会发出带中断结果的
`RunFinishedEvent` 并停止该运行。返回 `null` 则继续尝试下一个映射器或
`MapContent`。

```csharp
using AGUI.Abstractions;
using AGUI.Server;
using Microsoft.Extensions.AI;

public sealed class ConfirmationRequiredContent : AIContent
{
    public string RequestId { get; set; } = string.Empty;

    public string Message { get; set; } = string.Empty;
}

var streamOptions = new AGUIStreamOptions()
    .MapInterrupt(content =>
        content is ConfirmationRequiredContent confirmation
            ? new AGUIInterrupt
            {
                Id = confirmation.RequestId,
                Reason = InterruptReasons.Confirmation,
                Message = confirmation.Message,
            }
            : null);
```

用于无法由内置 `InterruptRequestContent` 或工具审批内容表示的自定义人工介入内容。

## MapCall {#mapcall}

`MapCall(string toolName, Func<FunctionCallContent, IEnumerable<BaseEvent>>
mapper)` 接收匹配的 `FunctionCallContent`，并在常规的工具调用开始、参数与结束事件之后
发出额外事件。

```csharp
using System.Text.Json;
using AGUI.Abstractions;
using AGUI.Server;

string? lastDocument = null;

var streamOptions = new AGUIStreamOptions()
    .MapCall("write_document", call =>
    {
        var document = call.Arguments?.TryGetValue("document", out var value) == true
            ? value?.ToString()
            : null;

        if (string.IsNullOrEmpty(document) || document == lastDocument)
        {
            return [];
        }

        lastDocument = document;

        var snapshot = JsonSerializer.SerializeToElement(new
        {
            document
        });

        return [new StateSnapshotEvent { Snapshot = snapshot }];
    });
```

用于流式工具参数预览。例如，当模型正在为 `write_document` 构建参数时，UI 可以在服务器端
工具完成之前更新实时的文档预览。

## MapResult {#mapresult}

`MapResult(string toolName, Func<FunctionResultContent,
IEnumerable<BaseEvent>> mapper)` 接收匹配的工具结果，并在常规的
`ToolCallResultEvent` 之后发出额外事件。

```csharp
using System.Text.Json;
using AGUI.Abstractions;
using AGUI.Server;

var streamOptions = new AGUIStreamOptions()
    .MapResult("save_recipe", result =>
    {
        var snapshot = JsonSerializer.SerializeToElement(new
        {
            saved = true,
            recipe = result.Result,
        });

        return
        [
            new StateSnapshotEvent { Snapshot = snapshot },
            new CustomEvent
            {
                Name = "recipe.saved",
                Value = snapshot,
            },
        ];
    });
```

当服务器端的工具结果还需要同时更新状态、活动或应用特定的 UI 时使用。

## 状态映射辅助方法 {#state-mapping-helpers}

两个便捷方法覆盖了常见的状态管理场景：

```csharp
var streamOptions = new AGUIStreamOptions()
    .MapResultAsStateSnapshot("create_plan")
    .MapResultAsStateDelta("update_plan_step");
```

- `MapResultAsStateSnapshot(toolName)` 发出 `StateSnapshotEvent`
- `MapResultAsStateDelta(toolName)` 发出 `StateDeltaEvent`

两个辅助方法都要求 `FunctionResultContent.Result` 是 `JsonElement`。如果你的工具返回
其他类型，请使用 `MapResult` 并自行序列化该值。

## RawRepresentation 透传 {#rawrepresentation-passthrough}

对于自定义的 `IChatClient` 包装器，将 `RawRepresentation` 设为某个 AG-UI 事件通常比
定义新的 `AIContent` 类型更简单。

```csharp
using System.Text.Json;
using AGUI.Abstractions;
using Microsoft.Extensions.AI;

var state = JsonSerializer.SerializeToElement(new
{
    status = "ready"
});

yield return new ChatResponseUpdate
{
    RawRepresentation = new StateSnapshotEvent
    {
        Snapshot = state,
    },
};
```

转换器会直接发出 `StateSnapshotEvent`。如果原始事件出现在运行开始之前，托管层会先发出
`RUN_STARTED`。

## 链式注册 {#chaining}

你可以注册多个 `MapContent` 或 `MapInterrupt` 回调。它们按注册顺序依次尝试，第一个
非 null 的结果生效。

```csharp
var streamOptions = new AGUIStreamOptions()
    .MapInterrupt(TryMapConfirmation)
    .MapInterrupt(TryMapInputRequest)
    .MapContent(TryMapWorkflowStep)
    .MapContent(TryMapProgress);
```

保持映射小而聚焦。标准文本、推理、工具和中断使用内置转换，仅为你的服务器特有的事件添加
流选项。
