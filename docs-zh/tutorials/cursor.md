---
title: "使用 Cursor 进行开发"
description: "使用 Cursor 更快地构建 AG-UI 实现"
---
<em class="lead">使用 Cursor 更快地构建 AG-UI 实现</em>

本指南将帮助你配置 Cursor，以便更快地构建自定义的 Agent User
Interaction Protocol（AG-UI）服务器与客户端。同样的原则
也适用于 Windsurf、VSCode 等其他 IDE。

## 将文档添加到 Cursor {#adding-the-documentation-to-cursor}

1. 打开 Cursor 设置
2. 进入 Features > Docs，点击“+ Add new Doc”
3. 粘贴以下 URL：https://docs.ag-ui.com/llms-full.txt
4. 点击“Add”

## 使用文档 {#using-the-documentation}

现在你可以使用这些文档来帮助构建 AG-UI 项目。输入
`@` 符号，选择“Docs”，然后从列表中选择
“Agent User Interaction Protocol”，即可将文档加载到当前提示中。编码愉快！

## 最佳实践 {#best-practices}

使用 Cursor 构建 AG-UI 服务器时：

- 将复杂问题拆解为更小的步骤
- 通过查看智能体编辑了哪些文件来了解它此前的操作
  （位于聊天输入框上方）
- 让智能体编写单元测试以验证你的实现
- 仔细遵循 AG-UI 协议规范
