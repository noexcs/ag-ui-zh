# AG-UI 文档中文翻译 — 任务契约（所有翻译 agent 必读）

## 背景
你在把 AG-UI 官方文档站（英文）翻译成简体中文，部署到 GitHub Pages。
本轮范围：`/Users/noexcs/Projects/ag-ui-zh/docs-zh/` 下**除 `1.0/` 以外**的全部页面（文档 Tab + SDK Tab）。
`1.0/`（规范）已完成，禁止改动。
文件已预处理：内部链接已转相对路径、Card/Note 组件已转 Markdown、每个标题尾部已注入英文锚点 `{#slug}`、
callout 已转成 python-markdown admonition（`!!! 类型` + 正文缩进 4 格，无闭合行）。
**只翻译分配给你的文件，原地覆写，不要碰其他文件。**

## 硬性规则（违反任何一条即失败）
1. **逐文件翻译**：读取文件 → 翻译成简体中文 → 写回同一路径。保持 Markdown 结构完全一致：
   标题数量/层级、列表嵌套、表格行列、围栏代码块数量必须与原文一一对应。
2. **代码块内容一字不动**：``` 围栏内的所有文本（JSON、HTTP、SSE、mermaid、bash、TypeScript、Python、C#、
   XML、YAML）严禁翻译、严禁改动，包括注释、mermaid 图里的英文标签。
3. **链接目标一字不动**：`](` 与 `)` 之间的路径/URL/锚点严禁改动（相对路径形如 `./foo.md#bar`、
   `../concepts/x.md`）；只翻译链接文字。
4. **标题锚点**：每个标题行尾部的 `{#english-slug}` 必须原样保留（只翻译标题文字本身，锚点保持英文）。
   形如 ``### `onRunInitialized()` ``、``## `RunAgentInput` `` 的**代码标题**：反引号内的标识符不翻译，锚点保留。
   `# @ag-ui/core`、`# AGUI.Abstractions` 这类包名标题：包名保持英文。
5. **YAML frontmatter**：保留 `title:` 和 `description:` 两键，把它们的值翻译成中文
   （保留引号风格；空值保持空）。
6. **admonition 块**：`!!! note` / `!!! tip` / `!!! warning` / `!!! info` 行本身一字不动；
   其下缩进 4 格的正文行翻译后**必须仍保持 4 格缩进**，不得增删空行、不得添加闭合行 `!!!`。
7. **RFC 2119 关键字保持英文大写原样**：MUST / MUST NOT / REQUIRED / SHALL / SHOULD /
   SHOULD NOT / RECOMMENDED / MAY / OPTIONAL 等，嵌在中文句子里（如 "MUST 使用…"）。
8. **协议标识符保持英文**：事件类型（`RUN_STARTED`、`TEXT_MESSAGE_CONTENT`…）、
   字段名（`threadId`、`runId`、`messageId`、`toolCallId`…）、Schema 类型名（`BaseEvent`、
   `RunAgentInput`、`EventType`…）、SDK 符号（`AbstractAgent`、`HttpAgent`、`AgentSubscriber`、
   `AGUIChatClient`、`IAguiTransport`…）、包名（`@ag-ui/core`、`ag_ui.core`、`AGUI.Abstractions`…）、
   方法名（`run()`、`addSubscriber()`、`onRunStartedEvent()`…）、技术名词（JSON、SSE、HTTP、
   Protobuf、SDK、AG-UI、Mintlify、npm、pip…）一律保留英文。
9. **不增删内容**：不添加译者注、不删除任何信息、不合并/拆分段落。空正文的 stub 页
   （`sdk/js/encoder.md`、`sdk/js/proto.md`）不在翻译范围，不要碰。
10. 标点：中文句子用中文标点（，。：；（）""），英文标识符前后保持原文风格，
    破折号沿用原文的 `—`。
11. 翻译风格：技术规范文体，精确、克制、无营销语气。同一术语全篇一致（见术语表）。

## 术语表（必须一致）
| 英文 | 中文 |
|---|---|
| event | 事件 |
| event stream | 事件流 |
| run | 运行 |
| run input | 运行输入 |
| thread / conversation | 会话 |
| message | 消息 |
| tool call / tool result | 工具调用 / 工具结果 |
| reasoning | 推理 |
| state | 状态 |
| snapshot / delta | 快照 / 增量 |
| interrupt / resume | 中断 / 恢复 |
| producer | 生产方 |
| consumer | 消费方 |
| middleware | 中间件 |
| transport / binding | 传输 / 传输绑定 |
| processing model | 处理模型 |
| conformance | 符合性 |
| subagent | 子智能体 |
| metadata | 元数据 |
| raw event | 原始事件 |
| passthrough | 透传 |
| activity | 活动 |
| step | 步骤 |
| lifecycle | 生命周期 |
| envelope | 信封 |
| discriminator | 判别字段 |
| mixin | 混入 |
| capabilities | 能力 |
| chunk | 块 |
| closed object | 封闭对象 |
| wire format | 线上格式 |
| enforcement | 强制执行 |
| fatal / warning | 致命 / 警告 |
| tolerant reader, strict writer | 宽容的读取方，严格的写入方 |
| replayed history | 重放的会话历史 |
| trust boundary | 信任边界 |
| side-effectful | 有副作用的 |
| keep-alive | 保活 |
| subscriber | 订阅者 |
| handler | 处理器 |
| client | 客户端 |
| server / endpoint | 服务器 / 端点 |
| hosting | 托管 |
| extensibility | 可扩展性 |
| compaction | 流压缩 |
| multimodal input | 多模态输入 |
| integration | 集成 |
| framework | 框架 |
| draft / proposal | 提案 |
| roadmap | 路线图 |

## 验收（翻译完每个文件后自查）
- `grep -c '^#\{1,6\} ' 文件` 标题数与原文一致
- 所有 `{#...}` 锚点保留
- 代码块内容未变（diff 中代码块无中文）
- `!!! ` admonition 行保留、正文 4 格缩进未破坏
- 无残留英文整句（除上述保留词）
