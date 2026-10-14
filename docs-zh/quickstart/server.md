---
title: "服务器"
description: "实现兼容 AG-UI 的服务器"
---
<em class="lead">实现兼容 AG-UI 的服务器</em>

# 简介 {#introduction}

服务器实现让你能够**直接从智能体或服务器发出 AG-UI 事件**。这种方式非常适合从零
构建新的智能体，或为你的智能体能力提供专用服务。

## 何时使用服务器实现 {#when-to-use-a-server-implementation}

服务器实现让你能够直接从智能体或服务器发出 AG-UI 事件。如果你没有使用智能体
框架，或尚未为你的智能体框架创建协议，那么这是最好的入门方式。

服务器实现也非常适合：

- 从零**构建新的智能体框架**
- 对事件如何发出、发出什么拥有**最大控制权**
- 把智能体暴露为**独立 API**

## 你将构建什么 {#what-youll-build}

在本指南中，我们将创建一个独立的 HTTP 服务器，它：

1. 接受 AG-UI 协议请求
2. 连接到 OpenAI 的 GPT-4o 模型
3. 把响应作为 AG-UI 事件流式回传
4. 处理工具调用与状态管理

让我们开始吧！

## 前置条件 {#prerequisites}

开始之前，请确保你已具备：

- [Python](https://www.python.org/downloads/) **3.12 或更高版本**
- [Poetry](https://python-poetry.org/docs/#installation)，用于依赖管理
- 一个 **OpenAI API key**

### 1. 提供你的 OpenAI API key {#1-provide-your-openai-api-key}

首先，设置你的 API key：

```bash
# Set your OpenAI API key {#set-your-openai-api-key}
export OPENAI_API_KEY=your-api-key-here
```

### 2. 安装构建工具 {#2-install-build-utilities}

安装以下工具：

```bash
brew install protobuf
```

```bash
npm i nx
```

```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

## 步骤 1 – 搭建你的服务器骨架 {#step-1--scaffold-your-server}

首先克隆仓库：

```bash
git clone git@github.com:ag-ui-protocol/ag-ui.git
cd ag-ui
```

复制 server-starter 模板以创建你的 OpenAI 服务器：

```bash
cp -r integrations/server-starter integrations/openai-server
```

### 更新元数据 {#update-metadata}

打开 `integrations/openai-server/package.json` 并更新字段以匹配
你的新目录：

```json
{
  "name": "@ag-ui/openai-server",
  "author": "Your Name <your-email@example.com>",
  "version": "0.0.1",

  ... rest of package.json
}
```

接下来，更新 `integrations/openai-server/src/index.ts` 中的类名：

```ts
// Change the name to OpenAIServerAgent to add a minimal middleware for your integration.
// You can use this later on to add configuration etc.
export class OpenAIServerAgent extends HttpAgent {}
```

最后，通过把集成加入 `apps/dojo/src/menu.ts` 将其引入 dojo：

```ts
// ...
export const menuIntegrations: MenuIntegrationConfig[] = [
  // ...

  {
    id: "openai-server",
    name: "OpenAI Server",
    features: ["agentic_chat"],
  },
]
```

以及 `apps/dojo/src/agents.ts`：

```ts
// ...
import { OpenAIServerAgent } from "@ag-ui/openai-server"

export const agentsIntegrations: AgentIntegrationConfig[] = [
  // ...

  {
    id: "openai-server",
    agents: async () => {
      return {
        agentic_chat: new OpenAIServerAgent(),
      }
    },
  },
]
```

## 步骤 2 – 把包添加到 dojo 依赖 {#step-2--add-package-to-dojo-dependencies}

打开 `apps/dojo/package.json`，把 `"@ag-ui/openai-server": "workspace:*"` 添加到
`dependencies` 对象：

```json
{
  "name": "demo-viewer",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@ag-ui/agno": "workspace:*",
    "@ag-ui/langgraph": "workspace:*",
    "@ag-ui/mastra": "workspace:*",
    "@ag-ui/middleware-starter": "workspace:*",
    "@ag-ui/server-starter": "workspace:*",
    "@ag-ui/server-starter-all-features": "workspace:*",
    "@ag-ui/vercel-ai-sdk": "workspace:*",
    "@ag-ui/openai-server": "workspace:*"
  }
}
```

## 步骤 3 – 启动 dojo 与服务器 {#step-3--start-the-dojo-and-server}

现在看看你的成果。首先，启动你的 Python 服务器：

```bash
cd integrations/openai-server/server/python
poetry install && poetry run dev
```

在另一个终端中，启动 dojo：

```bash
# Install dependencies {#install-dependencies}
pnpm install

# Compile the project and run the dojo {#compile-the-project-and-run-the-dojo}
pnpm dev
```

访问 [http://localhost:3000](http://localhost:3000)，从下拉菜单中选择
**OpenAI**。目前你会看到 stub 服务器回复 **Hello world!**。

这个 stub 服务器的行为如下：

```python
# integrations/openai-server/server/python/example_server/__init__.py {#integrationsopenaiserverserverpythonexampleserverinitpy}
@app.post("/")
async def agentic_chat_endpoint(input_data: RunAgentInput, request: Request):
    """Agentic chat endpoint"""
    # Get the accept header from the request
    accept_header = request.headers.get("accept")

    # Create an event encoder to properly format SSE events
    encoder = EventEncoder(accept=accept_header)

    async def event_generator():

        # Send run started event
        yield encoder.encode(
          RunStartedEvent(
            type=EventType.RUN_STARTED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
          ),
        )

        message_id = str(uuid.uuid4())

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

很好！我们已经在发送 `RunStartedEvent`，这是迈向符合 AG-UI 的端点的第一步。
现在让它做些有用的事。

## 实现基础聊天 {#implementing-basic-chat}

让我们增强端点，调用 OpenAI 的 API 并把响应作为 AG-UI 事件流式回传：

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from ag_ui.core import (
    RunAgentInput,
    EventType,
    RunStartedEvent,
    RunFinishedEvent,
    TextMessageStartEvent,
    TextMessageContentEvent,
    TextMessageEndEvent
)
from ag_ui.encoder import EventEncoder
import uuid
from openai import OpenAI
import os

app = FastAPI(title="AG-UI Endpoint")

# Initialize OpenAI client {#initialize-openai-client}
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/")
async def agentic_chat_endpoint(input_data: RunAgentInput, request: Request):
    accept_header = request.headers.get("accept")
    encoder = EventEncoder(accept=accept_header)

    async def event_generator():
        # Send run started event
        yield encoder.encode(
            RunStartedEvent(
                type=EventType.RUN_STARTED,
                thread_id=input_data.thread_id,
                run_id=input_data.run_id
            )
        )

        # Convert AG-UI messages to OpenAI messages format
        openai_messages = []
        for msg in input_data.messages:
            if msg.role in ["user", "system", "assistant"]:
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content or ""
                })

        # Call OpenAI with streaming enabled
        stream = client.chat.completions.create(
            model="gpt-4o",
            stream=True,
            messages=openai_messages,
        )

        # Generate a message ID for the assistant's response
        message_id = str(uuid.uuid4())

        # Send text message start event
        yield encoder.encode(
            TextMessageStartEvent(
                type=EventType.TEXT_MESSAGE_START,
                message_id=message_id,
                role="assistant"
            )
        )

        # Process the streaming response and send content events
        for chunk in stream:
            if (chunk.choices and
                len(chunk.choices) > 0 and
                chunk.choices[0].delta and
                hasattr(chunk.choices[0].delta, 'content') and
                chunk.choices[0].delta.content):

                content = chunk.choices[0].delta.content
                yield encoder.encode(
                    TextMessageContentEvent(
                        type=EventType.TEXT_MESSAGE_CONTENT,
                        message_id=message_id,
                        delta=content
                    )
                )

        # Send text message end event
        yield encoder.encode(
            TextMessageEndEvent(
                type=EventType.TEXT_MESSAGE_END,
                message_id=message_id
            )
        )

        # Send run finished event
        yield encoder.encode(
            RunFinishedEvent(
                type=EventType.RUN_FINISHED,
                thread_id=input_data.thread_id,
                run_id=input_data.run_id
            )
        )

    return StreamingResponse(
        event_generator(),
        media_type=encoder.get_content_type()
    )
```

## 步骤 4 – 将 OpenAI 与 AG-UI 桥接 {#step-4--bridge-openai-with-agui}

让我们把 stub 转换成一个真实的服务器，从 OpenAI 流式获取补全结果。

### 安装 OpenAI SDK {#install-the-openai-sdk}

首先，我们需要 OpenAI SDK：

```bash
cd integrations/openai-server/server/python
poetry add openai
```

### AG-UI 回顾 {#agui-recap}

AG-UI 服务器实现该端点，并发出一个事件序列以表示：

- 生命周期事件（`RUN_STARTED`、`RUN_FINISHED`、`RUN_ERROR`）
- 内容事件（`TEXT_MESSAGE_*`、`TOOL_CALL_*` 等）

### 实现流式服务器 {#implement-the-streaming-server}

现在我们将把 stub 服务器转换为真实的 OpenAI 集成。关键区别在于，
我们不再发送硬编码的 "Hello world!" 消息，而是连接 OpenAI 的 API，
并通过 AG-UI 事件把响应流式回传。

该实现遵循与 stub 相同的事件流，但我们会在其中添加 OpenAI 客户端初始化，
并用真实的 API 调用替换模拟响应。如果响应中存在工具调用，我们也会处理它们，
从而使我们的服务器在需要时完全具备使用函数的能力。

```python
import os
import uuid
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from ag_ui.core import (
    RunAgentInput,
    EventType,
    RunStartedEvent,
    RunFinishedEvent,
    RunErrorEvent,
    TextMessageChunkEvent,
    ToolCallChunkEvent,
)
from ag_ui.encoder import EventEncoder
from openai import OpenAI

app = FastAPI(title="AG-UI OpenAI Server")

# Initialize OpenAI client - uses OPENAI_API_KEY from environment {#initialize-openai-client--uses-openaiapikey-from-environment}
client = OpenAI()

@app.post("/")
async def agentic_chat_endpoint(input_data: RunAgentInput, request: Request):
    """OpenAI agentic chat endpoint"""
    accept_header = request.headers.get("accept")
    encoder = EventEncoder(accept=accept_header)

    async def event_generator():
        try:
            yield encoder.encode(
                RunStartedEvent(
                    type=EventType.RUN_STARTED,
                    thread_id=input_data.thread_id,
                    run_id=input_data.run_id
                )
            )

            # Call OpenAI's API with streaming enabled
            stream = client.chat.completions.create(
                model="gpt-4o",
                stream=True,
                # Convert AG-UI tools format to OpenAI's expected format
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters,
                        }
                    }
                    for tool in input_data.tools
                ] if input_data.tools else None,
                # Transform AG-UI messages to OpenAI's message format
                messages=[
                    {
                        "role": message.role,
                        "content": message.content or "",
                        # Include tool calls if this is an assistant message with tools
                        **({"tool_calls": message.tool_calls} if message.role == "assistant" and hasattr(message, 'tool_calls') and message.tool_calls else {}),
                        # Include tool call ID if this is a tool result message
                        **({"tool_call_id": message.tool_call_id} if message.role == "tool" and hasattr(message, 'tool_call_id') else {}),
                    }
                    for message in input_data.messages
                ],
            )

            message_id = str(uuid.uuid4())

            # Stream each chunk from OpenAI's response
            for chunk in stream:
                # Handle text content chunks
                if chunk.choices[0].delta.content:
                    yield encoder.encode(
                        TextMessageChunkEvent(
                            type=EventType.TEXT_MESSAGE_CHUNK,
                            message_id=message_id,
                            delta=chunk.choices[0].delta.content,
                        )
                    )
                # Handle tool call chunks
                elif chunk.choices[0].delta.tool_calls:
                    tool_call = chunk.choices[0].delta.tool_calls[0]

                    yield encoder.encode(
                        ToolCallChunkEvent(
                            type=EventType.TOOL_CALL_CHUNK,
                            tool_call_id=tool_call.id,
                            tool_call_name=tool_call.function.name if tool_call.function else None,
                            parent_message_id=message_id,
                            delta=tool_call.function.arguments if tool_call.function else None,
                        )
                    )

            yield encoder.encode(
                RunFinishedEvent(
                    type=EventType.RUN_FINISHED,
                    thread_id=input_data.thread_id,
                    run_id=input_data.run_id
                )
            )

        except Exception as error:
            yield encoder.encode(
                RunErrorEvent(
                    type=EventType.RUN_ERROR,
                    message=str(error)
                )
            )

    return StreamingResponse(
        event_generator(),
        media_type=encoder.get_content_type()
    )

def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "example_server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main()
```

### 底层发生了什么？ {#what-happens-under-the-hood}

让我们拆解你的服务器在做什么：

1. **初始化** – 我们创建一个 OpenAI 客户端并发出 `RUN_STARTED`
2. **请求** – 我们以 `stream=True` 把用户消息发送给 `chat.completions`
3. **流式传输** – 我们把每个块作为 `TEXT_MESSAGE_CHUNK` 或 `TOOL_CALL_CHUNK` 转发
4. **结束** – 我们发出 `RUN_FINISHED`（如果出错则发出 `RUN_ERROR`）

用以下命令测试你的端点：

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "threadId": "thread_123",
    "runId": "run_456",
    "state": {},
    "messages": [
      {
        "id": "msg_1",
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
```

该实现创建了一个功能完备的 AG-UI 端点，它处理消息并实时把响应流式回传。

## 步骤 5 – 与你的服务器聊天 {#step-5--chat-with-your-server}

刷新 dojo 页面并开始输入。你会看到 GPT-4o 实时逐词流式输出其答案。

[CopilotKit](https://docs.copilotkit.ai) 之类的工具已经理解 AG-UI，
并提供即插即用的 React 组件。把它们指向你的服务器端点，
即可开箱获得功能完备的聊天 UI。

## 分享你的集成 {#share-your-integration}

你是否构建了他人可以复用的自定义服务器？我们欢迎社区贡献！

1. Fork [AG-UI 仓库](https://github.com/ag-ui-protocol/ag-ui)
2. 在 `integrations/` 下添加你的包。更多细节与命名
   约定见[贡献指南](../development/contributing.md)。
3. 提交一个 pull request，描述你的用例与设计决策

如果你有疑问、需要反馈，或想先验证一个想法，请在 GitHub Discussions 中发起讨论：
[AG-UI GitHub Discussions 讨论区](https://github.com/orgs/ag-ui-protocol/discussions)。

你的集成可能会随下一个版本发布，并帮助整个 AG-UI 生态成长。

## 结语 {#conclusion}

你现在拥有一个功能完备的 OpenAI AG-UI 服务器，以及一个用于测试它的本地 playground。
从这里你可以：

- 添加工具调用以增强你的服务器
- 把你的服务器部署到生产环境
- 将 AG-UI 引入任何其他模型或服务

祝你构建愉快！
