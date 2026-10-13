---
title: "原始与自定义事件"
description: "两个逃生舱口，以及使它们不至于沦为第二套协议的种种限制 — 1.0"
---
<em class="lead">两个逃生舱口，以及使它们不至于沦为第二套协议的种种限制</em>

两种事件类型承载协议未建模之物：`RAW`，
不翻译地透传的一个提供方原生事件；`CUSTOM`，
应用自己的事件。两者都是独立的——它们不开启、
不关闭任何属于它们自己的条目，MAY 出现在一个
开启中的运行内的任何位置；不过 `CUSTOM` 不同于
`RAW`，它在其所属的车道内会结束一条开启中的
[chunk 流](../basic/patterns/streaming.md#closing-a-chunk-stream)。
它们的限制正是重点：本页上的一切存在，都是
为了让逃生舱口不能悄无声息地变成第二套协议。

## `RAW` {#raw}

不翻译地透传一个提供方原生事件，供需要协议
未建模之细节的消费方使用。

```json
{
  "type": "RAW",
  "event": { "…the provider's own event…": true },
  "source": "openai"
}
```

- `event` 是 REQUIRED，且是任何 JSON 值；
  `source` 是 OPTIONAL，指名它来自哪个提供方
  或框架。
- 消费方 MUST NOT 从一个 `RAW` 事件推导协议
  行为：其中没有任何东西会开启、关闭或修正
  本规范所跟踪的任何事物。
- 生产方 SHOULD 与标准事件一同发出 `RAW`，
  绝不以其代替标准事件。只以 `RAW` *表达*
  某物的生产方并未把它放进协议。

同样的载荷也作为普通事件上的 `rawEvent` 字段
传输——那种写法把一个出处附着到一个已翻译的
事件上，而 `RAW` 承载的是不存在对应已翻译事件
的材料。

## `CUSTOM` {#custom}

协议为应用自己的事件提供的扩展点。

```json
{
  "type": "CUSTOM",
  "name": "com.example.cart-updated",
  "value": { "items": 3 }
}
```

- `name` 与 `value` 都是 REQUIRED——没有名字，
  消费方无法路由该值；而没有载荷的事件什么都
  没说。
- 无法识别某个 `name` 的消费方 MUST 忽略该
  事件。这是协议合法流量，而非
  [无法识别的内容](../basic/processing.md)：
  没有任何东西被剥离，也没有任何东西触发
  警告。
- 名字属于应用空间。生产方 SHOULD 给自己
  杜撰的名字加上厂商或应用标识作为前缀，
  以免两个扩展同一条流的一方发生冲突；
  无前缀的名字为协议自身的未来用途保留。
- 消费方对一个已识别的 `CUSTOM` 事件所做
  的任何事情都在协议之外。生产方 MUST NOT 依赖
  `CUSTOM` 事件承载本规范分配给标准事件的
  语义——一个被符合的消费方合法忽略的自定义
  “message”不是一条消息。

## 数据类型 {#data-types}

[`RawEvent`](../schema.md#rawevent) 与 [`CustomEvent`](../schema.md#customevent) 由
[schema 参考](../schema.md) 定义。

## 安全考量 {#security-considerations}

透传内容按定义不受校验：没有 schema 约束
`event` 或 `value`，且 `RAW` 载荷源自提供方
获取它们的任何地方。消费方 MUST 把两者都
当作不受信任的输入——绝不作为标记渲染、
执行、或授予权限——并 SHOULD 以与其所概括的
网络流量同等的怀疑态度对待一个 `RAW` 载荷。
