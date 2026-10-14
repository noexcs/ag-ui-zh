---
title: "生成式 UI"
description: "理解 AG-UI 与生成式 UI 规范之间的关系"
---
<em class="lead">理解 AG-UI 与生成式 UI 规范之间的关系</em>

## **AG-UI 与生成式 UI 规范** {#agui-and-generative-ui-specs}

最近发布的若干规范使智能体能够返回生成式 UI，从而提升了 Agent&lt;-&gt;User 对话的能力与灵活性。

A2UI、MCP-UI 和 Open-JSON-UI 都是**生成式 UI 规范。** 生成式 UI 让智能体不仅可以用文本、还可以用动态 UI 组件回应用户。

| **规范** | **来源 / 维护方** | **用途** |
| --- | --- | --- |
| **A2UI** | Google | 声明式、对 LLM 友好的生成式 UI 规范。基于 JSONL 并支持流式传输，面向平台无关的渲染而设计。 |
| **Open-JSON-UI** | OpenAI | 对 OpenAI 内部声明式生成式 UI schema 的开放标准化。 |
| **MCP-UI** | Microsoft + Shopify | 完全开放的、基于 iframe 的生成式 UI 标准，扩展 MCP 以支持面向用户的体验。 |

尽管命名相似，**AG-UI 并不是生成式 UI 规范**——它是一个**用户交互协议**，提供智能体与应用之间的**双向运行时连接**。

AG-UI 原生支持上述所有生成式 UI 规范，也允许开发者定义**自己的自定义生成式 UI 标准**。
