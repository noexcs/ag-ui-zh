# AG-UI Protocol 中文文档

[AG-UI Protocol](https://github.com/ag-ui-protocol/ag-ui) 1.0 官方规范（spec/1.0）的简体中文翻译。

AG-UI 是标准化智能体与面向用户应用之间通信的开放协议：一个请求进入，一条有序的类型化事件流输出，承载用户可见的全部智能体行为——文本、工具调用、推理、共享状态与进度。

## 在线阅读

<https://noexcs.github.io/ag-ui-zh/>

## 内容

- **规范**：规范总览、1.0 相对 0.x 的主要变更、架构
- **基础协议**：事件模型、运行输入、元数据、能力、事件模式（流式 / 快照–增量 / 中断–恢复）、传输（HTTP+SSE、HTTP+Protobuf）、处理模型、版本与兼容性
- **事件流**：运行与步骤、文本消息、工具调用、推理、状态、活动、子智能体、原始与自定义事件
- **参考**：Schema 文件、Schema 参考（由 `schema.json` 描述逐条翻译的完整字段参考）

翻译范围与上游 <https://docs.ag-ui.com/spec/1.0> 的 26 个文档页一一对应；代码块、锚点、链接结构与上游逐字一致，因此跨页锚点链接与上游可互换。

## 本地构建

```sh
pip install -r requirements.txt
PYTHONPATH=. python -m mkdocs build -f mkdocs.zh.yml
PYTHONPATH=. python -m mkdocs serve -f mkdocs.zh.yml
```

产物在 `site-zh/`（不入库）。

## 机器可读产物

- `docs-zh/1.0/schema.json` —— 官方 schema 原样拷贝
- 各页 frontmatter 含中文 `title` / `description`，可直接作为 LLM 上下文引用

## 许可证与署名

- 原文（英文规范与 schema.json）：MIT，© 2025 Tawkit Inc.、Markus Ecker（见上游 `docs/LICENSE`）
- 本翻译为社区翻译，采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 noexcs
- 构建工具：[MkDocs](https://www.mkdocs.org/) + [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
