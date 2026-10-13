#!/usr/bin/env python3
"""Batch-translate the AG-UI schema descriptions (EN -> ZH) via completion().

Reads /tmp/schema_descs.json  (list of {id,text,count}), writes
/tmp/schema_desc_zh.json       ({id: translation}).

Robust: char-budget batching, retry with backoff, checkpointed per batch so a
crash resumes. Run from the eval kernel:  %load  (needs the `completion` global)
"""
import asyncio
import json
import time

SRC = "/tmp/schema_descs.json"
OUT = "/tmp/schema_desc_zh.json"

PREAMBLE = """You are translating the AG-UI protocol 1.0 JSON Schema reference from English to Simplified Chinese.
Translate each numbered description into Simplified Chinese. Technical-protocol register, precise, concise.
Rules:
- Keep ALL of these in English (do not translate): event type names (RUN_STARTED, TEXT_MESSAGE_CONTENT, ...), field names (threadId, runId, messageId, toolCallId, subagentRunId, metadata, rawEvent, timestamp, type, role, delta, value, name, content, op, from, path, snapshot, patch, messages, parts, ...), schema type names (BaseEvent, Attributable, RunAgentInput, EventType, State, Metadata, Tool, Interrupt, ...), and technical terms (JSON, JSON Schema, JSON Patch, RFC 6902, RFC 7386, SSE, HTTP, Protobuf, camelCase, base64, Unix epoch, milliseconds, null, boolean, integer, string, number, array, object, min, max, required, optional).
- RFC 2119 keywords stay uppercase English: MUST, MUST NOT, SHALL, SHOULD, RECOMMENDED, NOT RECOMMENDED, MAY, OPTIONAL.
- Terminology (must be consistent): event=事件, run=运行, message=消息, tool call=工具调用, tool result=工具结果, reasoning=推理, state=状态, snapshot=快照, delta=增量, interrupt=中断, resume=恢复, producer=生产方, consumer=消费方, subagent=子智能体, metadata=元数据, raw event=原始事件, discriminator=判别字段, mixin=混入, closed object=封闭对象, open by key=按 key 开放, wire format=线上格式, thread/conversation=会话, step=步骤, lifecycle=生命周期, envelope=信封, passthrough=透传, activity=活动, capabilities=能力.
- Output ONLY a JSON array of strings, in input order, one translation per input. No numbering, no keys, no markdown, no code fences.
"""
SCHEMA = {"type": "array", "items": {"type": "string"}}


def load_done():
    try:
        with open(OUT) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save(done):
    with open(OUT, "w") as f:
        json.dump(done, f, ensure_ascii=False, indent=0)


def make_batches(items, done, budget=2200):
    todo = [it for it in items if it["id"] not in done]
    batches, cur, chars = [], [], 0
    for it in todo:
        add = len(it["text"]) + 3
        if cur and chars + add > budget:
            batches.append(cur)
            cur, chars = [], 0
        cur.append(it)
        chars += add
    if cur:
        batches.append(cur)
    return batches


async def translate_batch(batch, attempt=1):
    lines = [f"{i}. {it['text']}" for i, it in enumerate(batch)]
    prompt = PREAMBLE + "Descriptions:\n" + "\n".join(lines)
    for a in range(1, attempt + 1):
        try:
            h = completion(prompt, schema=SCHEMA)
            res = await h.wait()
            if not isinstance(res, list):
                res = json.loads(res) if isinstance(res, str) else res
            if isinstance(res, list) and len(res) == len(batch) and all(
                isinstance(x, str) for x in res
            ):
                return res
            raise ValueError(f"bad shape: {type(res)} len={len(res) if isinstance(res,list) else 'n/a'}")
        except Exception as e:
            if a == attempt:
                raise
            wait = 3 * a
            print(f"  batch retry {a}/{attempt} after {wait}s: {e}")
            await asyncio.sleep(wait)


async def run():
    items = json.load(open(SRC))
    done = load_done()
    print(f"loaded {len(items)} descs, {len(done)} already done")
    batches = make_batches(items, done)
    print(f"{len(batches)} batches to run")
    for bi, batch in enumerate(batches):
        ids = [it["id"] for it in batch]
        if all(i in done for i in ids):
            continue
        try:
            trans = await translate_batch(batch, attempt=4)
        except Exception as e:
            print(f"  !! batch {bi} FAILED after retries: {e}")
            continue
        for it, tr in zip(batch, trans):
            done[it["id"]] = tr.strip()
        save(done)
        print(f"  batch {bi + 1}/{len(batches)} done ({len(batch)} items, total {len(done)})")
    print(f"DONE: {len(done)}/{len(items)} translated")


try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.run(run())
else:
    await run()
