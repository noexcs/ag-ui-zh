---
title: "Schema 文件"
description: "机器可读的 schema、其地址，以及如何使用它 — 1.0"
---
<em class="lead">机器可读的 schema、其地址，以及如何使用它</em>

schema 是结构方面的权威：哪些字段存在、哪些是必需的、
每个字段承载什么类型，以及判别字段可取哪些值。
本页说明到哪里获取它。

## 文件 {#the-file}

- [schema.json](schema.json) — 完整的 1.0 schema——所有事件、消息，以及运行输入。

```
https://ag-ui.com/spec/1.0/schema.json
```

该文件在其自身的 `$id` 中声明了那个地址，因此遵循
引用的校验器无需配置即可相对于它解析引用。
该地址直接提供该文件：工具与 schema 之间不存在
重定向，且响应携带一个跨域头，使基于浏览器的
工具能够读取它。

它是 [JSON Schema draft 2020-12](https://json-schema.org/draft/2020-12/release-notes)。
每个定义都可以按锚点寻址——`#TextMessageStartEvent`、
`#RunAgentInput`——因此工具可以指向某一个结构，
而无需对文件切片。

## 如何使用 {#using-it}

```bash
curl -sS https://ag-ui.com/spec/1.0/schema.json -o ag-ui-1.0.json
```

对照整个 schema 校验一个事件，让判别字段选出
成员；或者当你已知其结构时，对照单个锚点校验。

schema 在协议严格之处同样严格：它封闭了那些
结构被固定的对象，因此对它运行的校验器会拒绝
协议未描述的材料。按设计开放的对象保持开放——
其中包括 `metadata` 与 JSON Patch 操作——因为
协议承载消费方放入其中的任何东西。那种严格性
适用于创作与测试。*运行时*消费方做的恰好相反——
它接受无法识别的内容并将其剥离，正如
[处理模型](basic/processing.md) 所要求。不要
把严格的 schema 接进接收路径，然后把结果称为
符合性。

## schema 未说明的东西 {#what-the-schema-does-not-say}

排序、生命周期、归属、错误处理与兼容性都是
行为性的，没有任何 JSON Schema 能够表达它们。
它们在本文档的其他页面中规定，从[总览](index.md)开始。
