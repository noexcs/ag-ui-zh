---
title: "构建应用"
description:
  "利用兼容的事件 AG-UI 事件流构建智能体应用"
---
<em class="lead">利用兼容的事件 AG-UI 事件流构建智能体应用</em>

# 简介 {#introduction}

AG-UI 提供了一个简洁、事件驱动的协议，让任何智能体都能将丰富、
结构化的输出流式传输到任何客户端。它可用于将任何智能体系统连接到
任何客户端。

客户端定义为任何能够接收、显示并响应
AG-UI 事件的系统。有关现有客户端与集成的更多信息，请参阅
[集成](../integrations.md)页面。

# 自动设置 {#automatic-setup}
AG-UI 提供了一个 CLI 工具，可为任意客户端与服务器自动创建或脚手架生成新应用。

```sh
npx create-ag-ui-app@latest
```

![](https://copilotkit-public-assets.s3.us-east-1.amazonaws.com/docs/ag-ui/quickstart.gif)

设置完成后，使用以下命令启动服务器

```sh
npm run dev
```

对于 CopilotKit 示例，打开 [http://localhost:3000](http://localhost:3000) 即可查看应用运行效果。
