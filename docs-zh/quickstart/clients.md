---
title: "构建客户端"
description:
  "示例展示：使用 AG-UI 与 Mastra 从零构建一个会话式 CLI 智能体"
---
<em class="lead">示例展示：使用 AG-UI 与 Mastra 从零构建一个会话式 CLI 智能体</em>

# 简介 {#introduction}

客户端实现让你能够**构建利用 AG-UI 事件驱动协议的会话式应用**。这种方式在用户与
AI 智能体之间建立直接接口，展示了对 AG-UI 协议的直接访问。

客户端不必是 Web 应用。AG-UI 描述的是事件流，而不是渲染目标，因此任何能够消费
这些事件并将其呈现给用户的东西都是客户端：Web 应用、下面构建的终端客户端、
移动应用，或 Slack、Microsoft Teams 之类的聊天平台。
[Channels SDK](https://github.com/CopilotKit/channels-sdk) 就是一种聊天平台实现，
[OpenTag](https://github.com/CopilotKit/OpenTag) 则是其完整示例。

## 何时使用客户端实现 {#when-to-use-a-client-implementation}

如果你想探索/改造 AG-UI 协议，构建自己的客户端会很有用。对于生产环境，
请使用功能完备的客户端，例如 [CopilotKit](https://copilotkit.ai)。

## 你将构建什么 {#what-youll-build}

在本指南中，我们将创建一个 CLI 客户端，它：

1. 使用来自 `@ag-ui/mastra` 的 `MastraAgent`
2. 连接到 OpenAI 的 GPT-4o 模型
3. 实现一个天气工具以提供实际功能
4. 在终端中提供交互式聊天界面

让我们开始吧！

## 前置条件 {#prerequisites}

开始之前，请确保你已具备：

- [Node.js](https://nodejs.org/) **22.13.0 或更高版本**
- 一个 **OpenAI API key**
- [pnpm](https://pnpm.io/) 包管理器

### 1. 提供你的 OpenAI API key {#1-provide-your-openai-api-key}

首先，设置你的 API key：

```bash
# Set your OpenAI API key {#set-your-openai-api-key}
export OPENAI_API_KEY=your-api-key-here
```

### 2. 安装 pnpm {#2-install-pnpm}

如果你尚未安装 pnpm：

```bash
# Install pnpm {#install-pnpm}
npm install -g pnpm
```

## 步骤 1 – 初始化项目 {#step-1--initialize-your-project}

为你的 AG-UI 客户端创建一个新目录：

```bash
mkdir my-ag-ui-client
cd my-ag-ui-client
```

初始化一个新的 Node.js 项目：

```bash
pnpm init
```

### 设置 TypeScript 与基本配置 {#set-up-typescript-and-basic-configuration}

安装 TypeScript 与必要的开发依赖：

```bash
pnpm add -D typescript @types/node tsx
```

创建 `tsconfig.json` 文件：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

更新你的 `package.json` scripts：

```json
{
  "scripts": {
    "start": "tsx src/index.ts",
    "dev": "tsx --watch src/index.ts",
    "build": "tsc",
    "clean": "rm -rf dist"
  }
}
```

## 步骤 2 – 安装 AG-UI 与依赖 {#step-2--install-agui-and-dependencies}

安装 AG-UI 核心包与依赖：

```bash
# Core AG-UI packages {#core-agui-packages}
pnpm add @ag-ui/client @ag-ui/core @ag-ui/mastra

# Mastra ecosystem packages {#mastra-ecosystem-packages}
pnpm add @mastra/core @mastra/client-js @mastra/memory @mastra/libsql

# Mastra peer dependencies {#mastra-peer-dependencies}
pnpm add zod
```

## 步骤 3 – 创建你的智能体 {#step-3--create-your-agent}

让我们创建一个基本的会话式智能体。创建 `src/agent.ts`：

```typescript
import { Agent } from "@mastra/core/agent"
import { MastraAgent } from "@ag-ui/mastra"
import { Memory } from "@mastra/memory"
import { LibSQLStore } from "@mastra/libsql"

export const agent = new MastraAgent({
  resourceId: "cliExample",
  agent: new Agent({
    id: "ag-ui-assistant",
    name: "AG-UI Assistant",
    instructions: `
      You are a helpful AI assistant. Be friendly, conversational, and helpful.
      Answer questions to the best of your ability and engage in natural conversation.
    `,
    model: "openai/gpt-4o",
    memory: new Memory({
      storage: new LibSQLStore({
        id: "storage-memory",
        url: "file:./assistant.db",
      }),
    }),
  }),
  threadId: "main-conversation",
})
```

### 智能体中发生了什么？ {#whats-happening-in-the-agent}

1. **MastraAgent** – 我们用 AG-UI 协议适配器包装一个 Mastra Agent
2. **模型配置** – 我们使用 OpenAI 的 GPT-4o 以获得高质量响应
3. **记忆设置** – 我们使用 LibSQL 配置持久化记忆，以保存
   会话上下文
4. **指令** – 我们为智能体提供进行有帮助对话的基本准则

## 步骤 4 – 创建 CLI 界面 {#step-4--create-the-cli-interface}

现在创建交互式聊天界面。创建 `src/index.ts`：

```typescript
import * as readline from "readline"
import { agent } from "./agent"
import { randomUUID } from "@ag-ui/client"

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
})

async function chatLoop() {
  console.log("🤖 AG-UI Assistant started!")
  console.log("Type your messages and press Enter. Press Ctrl+D to quit.\n")

  return new Promise<void>((resolve) => {
    const promptUser = () => {
      rl.question("> ", async (input) => {
        if (input.trim() === "") {
          promptUser()
          return
        }
        console.log("")

        // Pause input while processing
        rl.pause()

        // Add user message to conversation
        agent.messages.push({
          id: randomUUID(),
          role: "user",
          content: input.trim(),
        })

        try {
          // Run the agent with event handlers
          await agent.runAgent(
            {}, // No additional configuration needed
            {
              onTextMessageStartEvent() {
                process.stdout.write("🤖 Assistant: ")
              },
              onTextMessageContentEvent({ event }) {
                process.stdout.write(event.delta)
              },
              onTextMessageEndEvent() {
                console.log("\n")
              },
            }
          )
        } catch (error) {
          console.error("❌ Error:", error)
        }

        // Resume input
        rl.resume()
        promptUser()
      })
    }

    // Handle Ctrl+D to quit
    rl.on("close", () => {
      console.log("\n👋 Thanks for using AG-UI Assistant!")
      resolve()
    })

    promptUser()
  })
}

async function main() {
  await chatLoop()
}

main().catch(console.error)
```

### CLI 界面中发生了什么？ {#whats-happening-in-the-cli-interface}

1. **Readline 接口** – 我们创建一个用于用户输入的交互式提示
2. **消息管理** – 我们把每次用户输入加入智能体的会话历史
3. **事件处理** – 我们监听 AG-UI 事件以提供实时反馈
4. **流式显示** – 我们在智能体响应生成时即时展示它

## 步骤 5 – 测试你的助手 {#step-5--test-your-assistant}

运行你新建的 AG-UI 客户端：

```bash
pnpm dev
```

你应该会看到：

```
🤖 AG-UI Assistant started!
Type your messages and press Enter. Press Ctrl+D to quit.

>
```

尝试提出类似这样的问题：

- "你好！最近怎么样？"
- "你能帮我做什么？"
- "讲个笑话"
- "用简单的方式解释量子计算"

你会看到智能体实时以流式文本作出响应！

## 步骤 6 – 理解 AG-UI 事件流 {#step-6--understanding-the-agui-event-flow}

让我们拆解发送一条消息时发生的过程：

1. **用户输入** – 你输入一个问题并按 Enter
2. **消息已添加** – 你的输入被加入会话历史
3. **智能体处理** – 智能体分析你的请求并组织响应
4. **响应生成** – 智能体将响应流式回传
5. **流式输出** – 你看到响应逐词出现

### 你正在处理的事件类型： {#event-types-youre-handling}

- `onTextMessageStartEvent` – 智能体开始响应
- `onTextMessageContentEvent` – 响应的每个块
- `onTextMessageEndEvent` – 响应完成

## 步骤 7 – 添加工具功能 {#step-7--add-tool-functionality}

现在你有了可用的聊天界面，让我们通过创建工具来添加一些实际能力。
我们将从天气工具开始。

### 创建你的第一个工具 {#create-your-first-tool}

让我们创建一个智能体可以使用的天气工具。创建目录结构：

```bash
mkdir -p src/tools
```

创建 `src/tools/weather.tool.ts`：

```typescript
import { createTool } from "@mastra/core/tools"
import { z } from "zod"

interface GeocodingResponse {
  results: {
    latitude: number
    longitude: number
    name: string
  }[]
}

interface WeatherResponse {
  current: {
    time: string
    temperature_2m: number
    apparent_temperature: number
    relative_humidity_2m: number
    wind_speed_10m: number
    wind_gusts_10m: number
    weather_code: number
  }
}

export const weatherTool = createTool({
  id: "get-weather",
  description: "Get current weather for a location",
  inputSchema: z.object({
    location: z.string().describe("City name"),
  }),
  outputSchema: z.object({
    temperature: z.number(),
    feelsLike: z.number(),
    humidity: z.number(),
    windSpeed: z.number(),
    windGust: z.number(),
    conditions: z.string(),
    location: z.string(),
  }),
  execute: async (inputData) => {
    return await getWeather(inputData.location)
  },
})

const getWeather = async (location: string) => {
  const geocodingUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(
    location
  )}&count=1`
  const geocodingResponse = await fetch(geocodingUrl)
  const geocodingData = (await geocodingResponse.json()) as GeocodingResponse

  if (!geocodingData.results?.[0]) {
    throw new Error(`Location '${location}' not found`)
  }

  const { latitude, longitude, name } = geocodingData.results[0]

  const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,weather_code`

  const response = await fetch(weatherUrl)
  const data = (await response.json()) as WeatherResponse

  return {
    temperature: data.current.temperature_2m,
    feelsLike: data.current.apparent_temperature,
    humidity: data.current.relative_humidity_2m,
    windSpeed: data.current.wind_speed_10m,
    windGust: data.current.wind_gusts_10m,
    conditions: getWeatherCondition(data.current.weather_code),
    location: name,
  }
}

function getWeatherCondition(code: number): string {
  const conditions: Record<number, string> = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
  }
  return conditions[code] || "Unknown"
}
```

### 天气工具中发生了什么？ {#whats-happening-in-the-weather-tool}

1. **工具定义** – 我们使用 Mastra 的 `createTool` 定义工具的接口
2. **输入 Schema** – 我们指定该工具接受一个位置字符串
3. **输出 Schema** – 我们定义返回的天气数据的结构
4. **API 集成** – 我们从 Open-Meteo 的免费天气 API 获取数据
5. **数据处理** – 我们把天气代码转换为人类可读的天气状况

### 更新你的智能体 {#update-your-agent}

现在更新我们的智能体以使用天气工具。更新 `src/agent.ts`：

```typescript
import { weatherTool } from "./tools/weather.tool" // <--- Import the tool

export const agent = new MastraAgent({
  agent: new Agent({
    // ...

    tools: { weatherTool }, // <--- Add the tool to the agent

    // ...
  }),
  threadId: "main-conversation",
})
```

### 更新你的 CLI 以处理工具 {#update-your-cli-to-handle-tools}

更新 `src/index.ts` 中的 CLI 界面以处理工具事件：

```typescript
// Add these new event handlers to your agent.runAgent call:
await agent.runAgent(
  {}, // No additional configuration needed
  {
    // ... existing event handlers ...

    onToolCallStartEvent({ event }) {
      console.log("🔧 Tool call:", event.toolCallName)
    },
    onToolCallArgsEvent({ event }) {
      process.stdout.write(event.delta)
    },
    onToolCallEndEvent() {
      console.log("")
    },
    onToolCallResultEvent({ event }) {
      if (event.content) {
        console.log("🔍 Tool call result:", event.content)
      }
    },
  }
)
```

### 测试你的天气工具 {#test-your-weather-tool}

现在重启你的应用并尝试询问天气：

```bash
pnpm dev
```

尝试类似这样的问题：

- "伦敦的天气怎么样？"
- "东京今天天气如何？"
- "西雅图在下雨吗？"

你会看到智能体使用天气工具获取真实数据并提供详细响应！

## 步骤 8 – 添加更多功能 {#step-8--add-more-functionality}

### 创建浏览器工具 {#create-a-browser-tool}

让我们添加网页浏览能力。首先安装 `open` 包：

```bash
pnpm add open
```

创建 `src/tools/browser.tool.ts`：

```typescript
import { createTool } from "@mastra/core/tools"
import { z } from "zod"
import { open } from "open"

export const browserTool = createTool({
  id: "open-browser",
  description: "Open a URL in the default web browser",
  inputSchema: z.object({
    url: z.url().describe("The URL to open"),
  }),
  outputSchema: z.object({
    success: z.boolean(),
    message: z.string(),
  }),
  execute: async (inputData) => {
    try {
      await open(inputData.url)
      return {
        success: true,
        message: `Opened ${inputData.url} in your default browser`,
      }
    } catch (error) {
      return {
        success: false,
        message: `Failed to open browser: ${error}`,
      }
    }
  },
})
```

### 用两个工具更新你的智能体 {#update-your-agent-with-both-tools}

更新 `src/agent.ts` 以包含这两个工具：

```typescript
import { Agent } from "@mastra/core/agent"
import { MastraAgent } from "@ag-ui/mastra"
import { Memory } from "@mastra/memory"
import { LibSQLStore } from "@mastra/libsql"
import { weatherTool } from "./tools/weather.tool"
import { browserTool } from "./tools/browser.tool"

export const agent = new MastraAgent({
  resourceId: "cliExample",
  agent: new Agent({
    id: "ag-ui-assistant",
    name: "AG-UI Assistant",
    instructions: `
      You are a helpful assistant with weather and web browsing capabilities.

      For weather queries:
      - Always ask for a location if none is provided
      - Use the weatherTool to fetch current weather data

      For web browsing:
      - Always use full URLs (e.g., "https://www.google.com")
      - Use the browserTool to open web pages

      Be friendly and helpful in all interactions!
    `,
    model: "openai/gpt-4o",
    tools: { weatherTool, browserTool }, // Add both tools
    memory: new Memory({
      storage: new LibSQLStore({
        id: "storage-memory",
        url: "file:./assistant.db",
      }),
    }),
  }),
  threadId: "main-conversation",
})
```

现在你可以让助手打开网站："帮我打开 Google" 或 "给我看看天气网站"。

## 步骤 9 – 部署你的客户端 {#step-9--deploy-your-client}

### 构建你的客户端 {#building-your-client}

创建生产构建：

```bash
pnpm build
```

### 创建启动脚本 {#create-a-startup-script}

在你的 `package.json` 中添加：

```json
{
  "bin": {
    "weather-assistant": "./dist/index.js"
  }
}
```

为构建产物 `dist/index.js` 添加 shebang：

```javascript
#!/usr/bin/env node
// ... rest of your compiled code
```

使其可执行：

```bash
chmod +x dist/index.js
```

### 全局链接 {#link-globally}

全局安装你的 CLI：

```bash
pnpm link --global
```

现在你可以在任何位置运行 `weather-assistant`！

## 扩展你的客户端 {#extending-your-client}

你的 AG-UI 客户端现在已是一个坚实的基础。以下是一些增强思路：

### 添加更多工具 {#add-more-tools}

- **计算器工具** – 用于数学运算
- **文件系统工具** – 用于读写文件
- **API 工具** – 用于连接其他服务
- **数据库工具** – 用于查询数据

### 改进界面 {#improve-the-interface}

- **富文本格式化** – 使用 `chalk` 之类的库实现彩色输出
- **进度指示器** – 为长时间操作显示加载状态
- **配置文件** – 允许用户自定义设置
- **命令行参数** – 支持不同的模式与选项

### 添加持久化 {#add-persistence}

- **会话历史** – 保存与恢复聊天会话
- **用户偏好** – 记住用户设置
- **工具结果缓存** – 缓存开销较大的 API 调用

## 分享你的客户端 {#share-your-client}

构建了有用的东西？考虑与社区分享：

1. **开源它** – 在 GitHub 上发布你的代码
2. **发布到 npm** – 让它可以通过 `npm install` 安装
3. **编写文档** – 帮助他人理解并扩展你的工作
4. **参与讨论** – 在
   [AG-UI GitHub Discussions](https://github.com/orgs/ag-ui-protocol/discussions) 分享你的经验

## 结语 {#conclusion}

你已从零构建了一个完整的 AG-UI 客户端！你的天气助手展示了这些核心概念：

- 具备实时流式传输的**事件驱动架构**
- 用于实际功能的**工具集成**
- 用于保留上下文的**会话记忆**
- 用于提升用户参与度的**交互式 CLI 界面**

从这里出发，你可以扩展客户端以支持任何用例 – 从简单的 CLI 工具到复杂的会话式应用。
AG-UI 协议提供基础，而你的创造力提供可能性。

祝你构建愉快！🚀
