---
title: "多模态输入"
description:
  "在 ag_ui.core 中使用带类型化 data/url 来源的、特定模态的用户输入部分"
---
<em class="lead">在 ag_ui.core 中使用带类型化 data/url 来源的、特定模态的用户输入部分</em>

# 多模态输入 {#multimodal-inputs}

`UserMessage.content` 既接受纯文本，也接受有序的多模态部分列表。

```python
from ag_ui.core import (
    UserMessage,
    TextPart,
    ImagePart,
    DocumentPart,
    UrlSource,
)

message = UserMessage(
    id="user-1",
    content=[
        TextPart(text="Summarize this PDF and screenshot"),
        ImagePart(
            source=UrlSource(
                value="https://example.com/screen.png",
                mime_type="image/png",
            )
        ),
        DocumentPart(
            source=UrlSource(
                value="https://example.com/report.pdf",
                mime_type="application/pdf",
            )
        ),
    ],
)
```

## 来源类型 {#source-types}

使用 `source.type` 描述负载的投递方式：

- `data`：内联 base64 负载，`mime_type` 为必需
- `url`：HTTP(S) 或 data URL，`mime_type` 可选

## 常见用例 {#common-use-cases}

### 视觉问答 {#visual-qa}

```python
from ag_ui.core import UserMessage, TextPart, ImagePart, UrlSource

message = UserMessage(
    id="q1",
    content=[
        TextPart(text="What issue do you see in this UI?"),
        ImagePart(
            source=UrlSource(
                value="https://example.com/ui.png",
                mime_type="image/png",
            ),
            metadata={"detail": "high"},
        ),
    ],
)
```

### 音频转录 {#audio-transcription}

```python
from ag_ui.core import UserMessage, TextPart, AudioPart, UrlSource

message = UserMessage(
    id="q2",
    content=[
        TextPart(text="Transcribe this recording."),
        AudioPart(
            source=UrlSource(
                value="https://example.com/meeting.wav",
                mime_type="audio/wav",
            )
        ),
    ],
)
```

### 已弃用的二进制模型 {#deprecated-binary-model}

`BinaryInputContent` 已弃用，并会发出 `DeprecationWarning`。在迁移到特定模态的部分期间，
它作为临时的兼容路径保留。
