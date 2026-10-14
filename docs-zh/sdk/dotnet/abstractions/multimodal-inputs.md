---
title: "多模态输入"
description: "在 AGUI.Abstractions 中使用带类型化数据和 URL 来源的、特定模态的用户输入部分"
---
<em class="lead">在 AGUI.Abstractions 中使用带类型化数据和 URL 来源的、特定模态的用户输入部分</em>

# 多模态输入 {#multimodal-inputs}

`AGUIUserMessage.Content` 通过 `AGUIContent` 联合类型，接受纯文本或有顺序的多模态内容部分数组。

```csharp
using System.Text.Json;
using AGUI.Abstractions;

var message = new AGUIUserMessage
{
    Id = "user-1",
    Content =
    [
        new AGUITextInputContent
        {
            Text = "Summarize this PDF and screenshot"
        },
        new AGUIImageInputContent
        {
            Source = new AGUIInputContentUrlSource
            {
                Value = "https://example.com/screen.png",
                MimeType = "image/png"
            }
        },
        new AGUIDocumentInputContent
        {
            Source = new AGUIInputContentUrlSource
            {
                Value = "https://example.com/report.pdf",
                MimeType = "application/pdf"
            }
        }
    ]
};
```

## 用户消息内容 {#user-message-content}

AG-UI 中用户消息的线上模型是 `content: string | InputContent[]`。在 .NET 中，这由 `AGUIContent` 表示。

```csharp
var plainText = new AGUIUserMessage
{
    Id = "user-1",
    Content = "Hello"
};

var parts = new AGUIUserMessage
{
    Id = "user-2",
    Content =
    [
        new AGUITextInputContent { Text = "Describe this image." },
        new AGUIImageInputContent
        {
            Source = new AGUIInputContentUrlSource
            {
                Value = "https://example.com/image.png",
                MimeType = "image/png"
            }
        }
    ]
};
```

`AGUIContent` 具备从 `string`、`List<AGUIInputContent>` 和 `AGUIInputContent[]` 的隐式转换，支持集合表达式，并实现 `IReadOnlyList<AGUIInputContent>` 以用于规范化读取。当存储的值是字符串时，这个只读列表外观会把它暴露为单个 `AGUITextInputContent`。

## 输入内容类型 {#input-content-types}

所有内容部分都派生自 `AGUIInputContent`，并使用 JSON 的 `type` 判别字段。

| C# 类型 | JSON `type` | 属性 |
| ------- | ----------- | ---------- |
| `AGUITextInputContent` | `text` | `text` |
| `AGUIImageInputContent` | `image` | `source`，可选 `metadata` |
| `AGUIAudioInputContent` | `audio` | `source`，可选 `metadata` |
| `AGUIVideoInputContent` | `video` | `source`，可选 `metadata` |
| `AGUIDocumentInputContent` | `document` | `source`，可选 `metadata` |
| `AGUIBinaryInputContent` | `binary` | `mimeType`，可选 `id`、`url`、`data`、`filename` |

### 文本 {#text}

```csharp
var text = new AGUITextInputContent
{
    Text = "What issue do you see in this UI?"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"text"` | 内容判别字段 |
| `Id` | `id` | `string?` | 可选的部分标识符 |
| `Text` | `text` | `string` | 文本内容 |
| `Metadata` | `metadata` | `JsonElement?` | 可选元数据，例如某个搜索命中的来源和标题 |

### 媒体部分 {#media-parts}

图像、音频、视频和文档都派生自 `AGUIMediaInputContent`。

```csharp
var image = new AGUIImageInputContent
{
    Source = new AGUIInputContentUrlSource
    {
        Value = "https://example.com/ui.png",
        MimeType = "image/png"
    },
    Metadata = JsonDocument.Parse("""{"detail":"high"}""").RootElement.Clone()
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"image"`、`"audio"`、`"video"` 或 `"document"` | 内容判别字段 |
| `Id` | `id` | `string?` | 可选的部分标识符 |
| `Source` | `source` | `AGUIInputContentSource` | 数据、URL 或提供商文件来源 |
| `Metadata` | `metadata` | `JsonElement?` | 可选的特定模态元数据 |

当服务器把 AG-UI 请求适配到 Microsoft.Extensions.AI 时，`AGUIChatMessageExtensions.AsChatMessages()` 会把数据来源映射为 `DataContent`、把 URL 来源映射为 `UriContent`、把文件来源映射为 `HostedFileContent`（句柄成为 `FileId`；`Provider` 在那里没有对应物，会在这一跳被丢弃，尽管它能通过 JSON 和 protobuf 往返）。来源的 MIME 类型会被保留；当 URL 来源省略 `mimeType` 时，`UriContent` 会从 URL 推断它。如果该 URL 没有可识别的扩展名，则规范化判别字段会提供 `image/*`、`audio/*` 或 `video/*`，以免模态信息丢失。

完整的 `metadata` 值会被保留在 MEAI 内容的 `AdditionalProperties["metadata"]` key 之下，包括对象形状的值。对于内联数据，字符串型的 `metadata.filename` 属性也会被赋给 `DataContent.Name`，以便支持文件的提供商能收到文件名。

在客户端方向，`AsAGUIMessages(jsonSerializerOptions)` 会根据 MIME 类型把 `DataContent` 和 `UriContent` 映射为规范化媒体部分，并把它们的 `AdditionalProperties` 序列化为该部分的 `metadata`。当 `DataContent.Name` 对应的属性尚不存在时，它会被作为 `metadata.filename` 包含进来。

### 二进制 {#binary}

`AGUIBinaryInputContent` 表示任意二进制输入部分。

```csharp
var binary = new AGUIBinaryInputContent
{
    MimeType = "application/octet-stream",
    Data = "AAECAwQ=",
    Filename = "payload.bin"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"binary"` | 内容判别字段 |
| `MimeType` | `mimeType` | `string` | MIME 类型 |
| `Id` | `id` | `string?` | 可选的二进制标识符 |
| `Url` | `url` | `string?` | 可选的二进制 URL |
| `Data` | `data` | `string?` | 可选的内联 base64 数据 |
| `Filename` | `filename` | `string?` | 可选的文件名 |

## 来源类型 {#source-types}

媒体输入部分使用 `AGUIInputContentSource`，这是一个基于判别字段的层级结构，JSON 字段为 `type`。

### 数据来源 {#data-source}

对内联 base64 载荷使用 `AGUIInputContentDataSource`。`mimeType` 为必需。

```csharp
var source = new AGUIInputContentDataSource
{
    Value = "iVBORw0KGgo...",
    MimeType = "image/png"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"data"` | 来源判别字段 |
| `Value` | `value` | `string` | 内联 base64 载荷 |
| `MimeType` | `mimeType` | `string` | 载荷 MIME 类型 |

### URL 来源 {#url-source}

对 HTTP(S) URL 或 data URL 使用 `AGUIInputContentUrlSource`。`mimeType` 为可选。

```csharp
var source = new AGUIInputContentUrlSource
{
    Value = "https://example.com/meeting.wav",
    MimeType = "audio/wav"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"url"` | 来源判别字段 |
| `Value` | `value` | `string` | URL 或 data URL |
| `MimeType` | `mimeType` | `string?` | 可选 MIME 类型 |

### 文件来源 {#file-source}

对已经存在于模型提供商处的字节使用 `AGUIInputContentFileSource`——一个 OpenAI 或 Anthropic 文件 id、一个 Gemini 文件 URI。不会抓取任何内容，且 `Value` 是不透明的：把它交回发放它的那个提供商，或者丢弃该部分。`provider` 和 `mimeType` 为可选。

```csharp
var source = new AGUIInputContentFileSource
{
    Value = "file-abc123",
    Provider = "openai",
    MimeType = "application/pdf"
};
```

| C# 属性 | JSON 字段 | 类型 | 说明 |
| ----------- | ---------- | ---- | ----------- |
| `Type` | `type` | `"file"` | 来源判别字段 |
| `Value` | `value` | `string` | 提供商的句柄，与发放时完全一致 |
| `Provider` | `provider` | `string?` | 发放方，例如 `"openai"`、`"anthropic"`、`"google"` |
| `MimeType` | `mimeType` | `string?` | 可选 MIME 类型 |

## 常见用例 {#common-use-cases}

### 视觉问答 {#visual-qa}

```csharp
var message = new AGUIUserMessage
{
    Id = "q1",
    Content =
    [
        new AGUITextInputContent
        {
            Text = "What issue do you see in this UI?"
        },
        new AGUIImageInputContent
        {
            Source = new AGUIInputContentUrlSource
            {
                Value = "https://example.com/ui.png",
                MimeType = "image/png"
            },
            Metadata = JsonDocument.Parse("""{"detail":"high"}""").RootElement.Clone()
        }
    ]
};
```

### 音频转录 {#audio-transcription}

```csharp
var message = new AGUIUserMessage
{
    Id = "q2",
    Content =
    [
        new AGUITextInputContent
        {
            Text = "Transcribe this recording."
        },
        new AGUIAudioInputContent
        {
            Source = new AGUIInputContentUrlSource
            {
                Value = "https://example.com/meeting.wav",
                MimeType = "audio/wav"
            }
        }
    ]
};
```

### 混合媒体比较 {#mixed-media-comparison}

```csharp
var message = new AGUIUserMessage
{
    Id = "q3",
    Content =
    [
        new AGUITextInputContent
        {
            Text = "Compare the screenshot with the spec."
        },
        new AGUIImageInputContent
        {
            Source = new AGUIInputContentDataSource
            {
                Value = "iVBORw0KGgo...",
                MimeType = "image/png"
            }
        },
        new AGUIDocumentInputContent
        {
            Source = new AGUIInputContentUrlSource
            {
                Value = "https://example.com/spec.pdf",
                MimeType = "application/pdf"
            }
        }
    ]
};
```

!!! tip
    对仅含文本的简单轮次使用纯字符串 `Content`。当顺序重要，或用户消息
      在文本之外还包含媒体时，使用多模态部分。
