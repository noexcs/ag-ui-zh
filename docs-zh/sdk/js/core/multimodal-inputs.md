---
title: "多模态输入"
description:
  "在 @ag-ui/core 中使用带类型化 data/url 来源的、特定模态的用户输入部分"
---
<em class="lead">在 @ag-ui/core 中使用带类型化 data/url 来源的、特定模态的用户输入部分</em>

# 多模态输入 {#multimodal-inputs}

`UserMessage.content` 既接受纯文本，也接受有序的多模态内容部分数组。

```typescript
import { UserMessage } from "@ag-ui/core"

const message: UserMessage = {
  id: "user-1",
  role: "user",
  content: [
    { type: "text", text: "Summarize this PDF and screenshot" },
    {
      type: "image",
      source: {
        type: "url",
        value: "https://example.com/screen.png",
        mimeType: "image/png",
      },
    },
    {
      type: "document",
      source: {
        type: "url",
        value: "https://example.com/report.pdf",
        mimeType: "application/pdf",
      },
    },
  ],
}
```

## 来源类型 {#source-types}

使用 `source.type` 描述负载的投递方式：

- `data`：内联 base64 负载，`mimeType` 为必需
- `url`：HTTP(S) 或 data URL，`mimeType` 可选

## 常见用例 {#common-use-cases}

### 视觉问答 {#visual-qa}

```typescript
{
  id: "q1",
  role: "user",
  content: [
    { type: "text", text: "What issue do you see in this UI?" },
    {
      type: "image",
      source: { type: "url", value: "https://example.com/ui.png", mimeType: "image/png" },
      metadata: { detail: "high" },
    },
  ],
}
```

### 音频转录 {#audio-transcription}

```typescript
{
  id: "q2",
  role: "user",
  content: [
    { type: "text", text: "Transcribe this recording." },
    {
      type: "audio",
      source: { type: "url", value: "https://example.com/meeting.wav", mimeType: "audio/wav" },
    },
  ],
}
```

### 混合媒体比较 {#mixed-media-comparison}

```typescript
{
  id: "q3",
  role: "user",
  content: [
    { type: "text", text: "Compare the screenshot with the spec." },
    {
      type: "image",
      source: { type: "data", value: "iVBORw0KGgo...", mimeType: "image/png" },
    },
    {
      type: "document",
      source: { type: "url", value: "https://example.com/spec.pdf", mimeType: "application/pdf" },
    },
  ],
}
```
