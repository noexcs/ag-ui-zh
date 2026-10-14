# AG-UI Protocol 中文文档

[AG-UI Protocol](https://github.com/ag-ui-protocol/ag-ui) 官方文档站的简体中文翻译，覆盖三个板块：**文档**（概念、入门、集成、教程）、**1.0 规范**全文、**SDK 参考**（TypeScript / Python / .NET）。

AG-UI 是标准化智能体与面向用户应用之间通信的开放协议：一个请求进入，一条有序的类型化事件流输出，承载用户可见的全部智能体行为——文本、工具调用、推理、共享状态与进度。

## 在线阅读

<https://noexcs.github.io/ag-ui-zh/>

## 内容

- **文档**：概述、与 MCP/A2A 的关系、入门（构建应用 / 构建集成 / 构建客户端）、迁移到 1.0、概念（事件、智能体、中间件、消息、元数据、推理、状态、中断、序列化、工具、子智能体、能力、生成式 UI 规范）、集成列表、提案、教程（Cursor、调试）、开发（贡献、路线图）
- **规范**：规范总览、1.0 相对 0.x 的主要变更、架构、基础协议（事件模型、运行输入、元数据、能力、事件模式、传输、处理模型、版本与兼容性）、事件流（八个事件族）、参考（Schema 文件、由 `schema.json` 逐条翻译的 Schema 参考）
- **SDK**：TypeScript（`@ag-ui/core`、`@ag-ui/client`、`@ag-ui/encoder`、`@ag-ui/proto`）、Python（`ag_ui.core`、`ag_ui.encoder`）、.NET（`AGUI.Abstractions`、`AGUI.Client`、`AGUI.Server`）

翻译范围与上游 <https://docs.ag-ui.com> 对应板块的页面一一对应；代码块、锚点、链接结构与上游逐字一致，因此跨页锚点链接与上游可互换。

## 本地构建

```sh
pip install -r requirements.txt
PYTHONPATH=. python -m mkdocs build -f mkdocs.zh.yml
python scripts/inject_header.py   # 注入原站页头（三 Tab 行、版本徽章、SDK 快捷链、TOC 标题）
PYTHONPATH=. python -m mkdocs serve -f mkdocs.zh.yml
```

产物在 `site-zh/`（不入库）。

## 机器可读产物

- `docs-zh/1.0/schema.json` —— 官方 schema 原样拷贝
- 各页 frontmatter 含中文 `title` / `description`，可直接作为 LLM 上下文引用

## 更新上游

上游 Mintlify 仓库快照在 `.git-upstream/docs/`（浅克隆）。规范页用 `scripts/transform.py`、文档/SDK 页用 `scripts/transform_site.py` 做 MDX→Markdown 预处理（链接相对化、Card/Note/Steps 组件转 Markdown、标题锚点注入、素材本地化），产物需人工翻译后入库。

## 许可证与署名

- 原文（英文文档、规范与 schema.json）：MIT，© 2025 Tawkit Inc.、Markus Ecker（见上游 `docs/LICENSE`）
- 本翻译为社区翻译，采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名 noexcs
- 构建工具：[MkDocs](https://www.mkdocs.org/) + [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
