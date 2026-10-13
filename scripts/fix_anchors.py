#!/usr/bin/env python3
"""Align every zh heading anchor with the live upstream site's anchor ids.

The upstream Mintlify site auto-generates heading ids (e.g. `Data types` ->
`data_types`); the translation kept the prose 1:1 but the agents' explicit
anchors drift (hyphens, missing), breaking cross-page links that were
verbatim-copied from upstream. Fetch each upstream page's HTML, take the
heading ids in document order, and rewrite the zh page's heading anchors in
the same order (counts must match).
"""
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = "https://docs.ag-ui.com"

# zh path -> upstream url
PAGES = {
    "1.0/index.md": "/spec/1.0",
    "1.0/changelog.md": "/spec/1.0/changelog",
    "1.0/architecture.md": "/spec/1.0/architecture",
    "1.0/basic/index.md": "/spec/1.0/basic",
    "1.0/basic/run-input.md": "/spec/1.0/basic/run-input",
    "1.0/basic/metadata.md": "/spec/1.0/basic/metadata",
    "1.0/basic/capabilities.md": "/spec/1.0/basic/capabilities",
    "1.0/basic/patterns/index.md": "/spec/1.0/basic/patterns",
    "1.0/basic/patterns/streaming.md": "/spec/1.0/basic/patterns/streaming",
    "1.0/basic/patterns/snapshots.md": "/spec/1.0/basic/patterns/snapshots",
    "1.0/basic/patterns/interrupt-resume.md": "/spec/1.0/basic/patterns/interrupt-resume",
    "1.0/basic/transports/index.md": "/spec/1.0/basic/transports",
    "1.0/basic/transports/http-sse.md": "/spec/1.0/basic/transports/http-sse",
    "1.0/basic/transports/http-protobuf.md": "/spec/1.0/basic/transports/http-protobuf",
    "1.0/basic/processing.md": "/spec/1.0/basic/processing",
    "1.0/basic/versioning.md": "/spec/1.0/basic/versioning",
    "1.0/events/index.md": "/spec/1.0/events",
    "1.0/events/lifecycle.md": "/spec/1.0/events/lifecycle",
    "1.0/events/text-messages.md": "/spec/1.0/events/text-messages",
    "1.0/events/tool-calls.md": "/spec/1.0/events/tool-calls",
    "1.0/events/reasoning.md": "/spec/1.0/events/reasoning",
    "1.0/events/state.md": "/spec/1.0/events/state",
    "1.0/events/activity.md": "/spec/1.0/events/activity",
    "1.0/events/subagents.md": "/spec/1.0/events/subagents",
    "1.0/events/passthrough.md": "/spec/1.0/events/passthrough",
    "1.0/schema-files.md": "/spec/1.0/schema-files",
}

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE = re.compile(r"^(```|~~~)")


def zh_headings(text):
    """[(line_no, hashes, title_line)] outside code fences, frontmatter-safe."""
    out, infence, infront = [], False, 0
    for i, ln in enumerate(text.splitlines()):
        s = ln.strip()
        if infront:
            if s == "---":
                infront = 0
            continue
        if i < 2 and s == "---":
            infront = 1
            continue
        if FENCE.match(s):
            infence = not infence
            continue
        m = HEADING.match(ln)
        if m:
            out.append((i, m.group(1), m.group(2)))
    return out


def upstream_ids(url):
    req = urllib.request.Request(UP + url, headers={"User-Agent": "Mozilla/5.0 (anchor-alignment)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL)
    body = m.group(1) if m else html
    return [i for i in re.findall(r"<h[1-6][^>]*?\bid=\"([^\"]+)\"", body)
            if i != "page-title" and not i.startswith("_R_")]


def main():
    total = changed = 0
    for rel, url in PAGES.items():
        path = os.path.join(BASE, "docs-zh", rel)
        text = open(path, encoding="utf-8").read()
        lines = text.splitlines(keepends=True)
        heads = zh_headings(text)
        try:
            ids = upstream_ids(url)
        except Exception as e:
            print(f"FETCH FAIL {rel}: {e}", file=sys.stderr)
            sys.exit(1)
        # the live page may carry extra headings (e.g. none expected); align on counts
        if len(heads) != len(ids):
            print(f"COUNT MISMATCH {rel}: zh={len(heads)} upstream={len(ids)}")
            for h in heads:
                print("   zh:", h[2])
            sys.exit(1)
        new_lines = list(lines)
        page_changed = 0
        for (ln, hashes, title), uid in zip(heads, ids):
            line = lines[ln].rstrip("\n")
            stripped = re.sub(r"\s*\{#[a-z0-9_-]+\}\s*$", "", line)
            want = f"{stripped} {{#{uid}}}"
            if want != line:
                new_lines[ln] = want + "\n"
                page_changed += 1
        if page_changed:
            open(path, "w", encoding="utf-8").write("".join(new_lines))
        total += len(heads)
        changed += page_changed
        print(f"{rel}: {len(heads)} headings, {page_changed} anchors fixed")
    print(f"done: {total} headings checked, {changed} anchors updated")


if __name__ == "__main__":
    main()
