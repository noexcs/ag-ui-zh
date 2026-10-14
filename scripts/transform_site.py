#!/usr/bin/env python3
"""Convert upstream Mintlify .mdx sources (docs tab + SDKs tab, 60 pages)
into mkdocs-ready Markdown under docs-zh/ with full-site relative links.

Reuses transform.py's slug/anchor/Note machinery. Additional handlers:
order-independent Card/CardGroup, img/video/Steps/Callout/span-badge/
a-in-div JSX degradation, the introduction.md accordion-grid prepass, and
full-site link resolution (local .md/.json when translated, live-site
fallback otherwise).

Run:  python scripts/transform_site.py
"""
import os
import posixpath
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transform as T  # noqa: E402  (slugify / rewrite_headings / convert_notes)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, ".git-upstream", "docs")
OUT = os.path.join(ROOT, "docs-zh")
LIVE = "https://docs.ag-ui.com"

PAGES = [
    "introduction",
    "agentic-protocols",
    "quickstart/applications",
    "quickstart/introduction",
    "quickstart/server",
    "quickstart/middleware",
    "quickstart/clients",
    "migrating-to-1-0",
    "talk-to-us",
    "concepts/architecture",
    "concepts/events",
    "concepts/agents",
    "concepts/middleware",
    "concepts/messages",
    "concepts/metadata",
    "concepts/reasoning",
    "concepts/state",
    "concepts/interrupts",
    "concepts/serialization",
    "concepts/tools",
    "concepts/subagents",
    "concepts/capabilities",
    "concepts/generative-ui-specs",
    "integrations",
    "integrations/google-adk-js",
    "drafts/overview",
    "drafts/generative-ui",
    "drafts/meta-events",
    "tutorials/cursor",
    "tutorials/debugging",
    "development/updates",
    "development/roadmap",
    "development/contributing",
    "support",
    "sdk/js/core/overview",
    "sdk/js/core/types",
    "sdk/js/core/multimodal-inputs",
    "sdk/js/core/events",
    "sdk/js/client/overview",
    "sdk/js/client/abstract-agent",
    "sdk/js/client/http-agent",
    "sdk/js/client/middleware",
    "sdk/js/client/subscriber",
    "sdk/js/client/compaction",
    "sdk/js/encoder",
    "sdk/js/proto",
    "sdk/python/core/overview",
    "sdk/python/core/types",
    "sdk/python/core/multimodal-inputs",
    "sdk/python/core/events",
    "sdk/python/encoder/overview",
    "sdk/dotnet/abstractions/overview",
    "sdk/dotnet/abstractions/types",
    "sdk/dotnet/abstractions/events",
    "sdk/dotnet/abstractions/multimodal-inputs",
    "sdk/dotnet/client/overview",
    "sdk/dotnet/client/chat-client",
    "sdk/dotnet/client/transport",
    "sdk/dotnet/hosting/overview",
    "sdk/dotnet/hosting/endpoints",
    "sdk/dotnet/hosting/extensibility",
]


def attr(tag, name):
    m = re.search(name + r'="([^"]*)"', tag)
    return m.group(1) if m else None


def convert_cards(md):
    """Order-independent Card/CardGroup -> markdown bullets (site-wide)."""

    def card_repl(m):
        tag, desc = m.group(1), m.group(2)
        title = attr(tag, "title") or "(untitled)"
        href = attr(tag, "href") or "#"
        link = f"[{title}](#CARDHREF#{href})" if href.startswith("/") else f"[{title}]({href})"
        return f"- {link} — {' '.join(desc.split())}\n"

    if "<CardGroup" in md:
        md = re.sub(
            r"<CardGroup\b[^>]*>(.*?)</CardGroup>",
            lambda m: re.sub(
                r"<Card\s+(.*?)>(.*?)</Card>", card_repl, m.group(1), flags=re.DOTALL
            ).strip(),
            md,
            flags=re.DOTALL,
        )
    md = re.sub(r"<Card\s+(.*?)>(.*?)</Card>", card_repl, md, flags=re.DOTALL)
    return md


def convert_img(md):
    def repl(m):
        tag = m.group(0)
        return f"![{attr(tag, 'alt') or ''}]({attr(tag, 'src') or ''})"

    return re.sub(r"<img\b[^>]*?/?>", repl, md, flags=re.DOTALL)


def convert_video(md):
    def repl(m):
        tag = m.group(0)
        src = re.search(r"src=\"([^\"]+)\"", tag)
        if not src:
            return ""
        return (
            '<video controls preload="metadata">\n'
            f'<source src="{src.group(1)}" type="video/mp4">\n'
            "</video>"
        )

    md = re.sub(r"<video\b[^>]*/\s*>", repl, md, flags=re.DOTALL)
    return re.sub(r"<video\b[^>]*>.*?</video>", repl, md, flags=re.DOTALL)


def convert_div_a(md):
    def repl(m):
        inner = m.group(1)
        am = re.search(r"<a\s+([^>]*)>(.*?)</a>", inner, re.DOTALL)
        if not am:
            kept = re.findall(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$", inner, re.M)
            return "\n".join(kept).strip() + "\n" if kept else "\n"
        href = attr(am.group(1), "href") or "#"
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", am.group(2))).strip()
        return f"[{text}]({href})\n"

    return re.sub(r"<div\b[^>]*>(.*?)</div>", repl, md, flags=re.DOTALL)


def convert_admonitions(md):
    """Note/Tip/Warning/Info/Check -> python-markdown admonitions (Callout -> info)。
    格式：!!! type + 正文缩进 4 格，无闭合行（::: 与闭合行均不被识别）。"""
    mapping = {"Note": "note", "Tip": "tip", "Warning": "warning", "Info": "info", "Check": "check"}

    def repl(kind):
        def _r(m):
            body = "\n".join("    " + ln for ln in m.group(1).strip().splitlines())
            return f"!!! {kind}\n" + body + "\n"

        return _r

    for comp, kind in mapping.items():
        md = re.sub(rf"<{comp}\b[^>]*>(.*?)</{comp}>", repl(kind), md, flags=re.DOTALL)
    return re.sub(r"<Callout\b[^>]*>(.*?)</Callout>", repl("info"), md, flags=re.DOTALL)

def convert_span_badge(md):
    def repl(m):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        return f"**{text}**"

    return re.sub(r"<span\b[^>]*>(.*?)</span>", repl, md, flags=re.DOTALL)


def convert_steps(md):
    def group_repl(m):
        steps = re.findall(
            r'<Step\s+title="([^"]*)"[^>]*>\s*(.*?)\s*</Step>', m.group(1), re.DOTALL
        )
        if not steps:
            return m.group(0)
        items = []
        for i, (t, d) in enumerate(steps, 1):
            body_txt = " ".join(" ".join(ln.split()) for ln in d.splitlines() if ln.strip())
            items.append(f"{i}. **{t}**\n\n   {body_txt}")
        return "\n\n".join(items) + "\n"

    return re.sub(r"<Steps>(.*?)</Steps>", group_repl, md, flags=re.DOTALL)
def localize_assets(md, rel_path):
    """/images/... /videos/... refs -> local assets/ copies (repo self-contained)."""
    up = "../" * rel_path.count("/")

    def repl(m):
        prefix, kind, name = m.group(1), m.group(2), m.group(3)
        src = os.path.join(SRC, kind, name)
        if not os.path.isfile(src):
            return m.group(0)
        dst = os.path.join(OUT, "assets", kind, name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
            shutil.copy2(src, dst)
        return f"{prefix}{up}assets/{kind}/{name}"

    return re.sub(r'(\(|src=")/(images|videos)/([A-Za-z0-9._-]+)', repl, md)


def strip_jsx_divs(md):
    prev = None
    while prev != md:
        prev = md
        md = re.sub(r"<div\b[^>]*>", "\n", md)
        md = md.replace("</div>", "\n")
    return md


def preprocess_introduction(text):
    """introduction.mdx only: accordion grid -> bullets, center divs -> img/video."""
    grid = re.search(
        r"<div style=\{\{display: 'grid'.*?>\s*(.*?)</div>\n*(?:\n\s*)*---",
        text,
        re.DOTALL,
    )
    if grid:
        cards = re.findall(r"py-4 bg-gray-50[^>]*>\s*\n(.*?)\s*\n</div>", grid.group(1), re.DOTALL)
        descs = re.findall(r"lineHeight: '1\.6'\}\}>\s*\n(.*?)\s*\n</div>", grid.group(1), re.DOTALL)
        bullets = [f"- **{' '.join(t.split())}**：{' '.join(d.split())}" for t, d in zip(cards, descs)]
        text = text[: grid.start()] + "\n".join(bullets) + "\n\n---" + text[grid.end():]

    def center_div(m):
        inner = m.group(1)
        if "<video" in inner:
            vm = re.search(r"<video\b[^>]*>.*?</video>", inner, re.DOTALL)
            return convert_video(vm.group(0)) if vm else "\n"
        srcs = re.findall(r'src="([^"]+)"', inner)
        if srcs:
            alt = re.search(r'alt="([^"]*)"', inner)
            pick = srcs[1] if len(srcs) > 1 else srcs[0]  # keep dark asset
            return f"![{alt.group(1) if alt else ''}]({pick})"
        return "\n"

    text = re.sub(
        r"<div style=\{\{textAlign: 'center'.*?\}\}>\s*(.*?)</div>",
        center_div,
        text,
        flags=re.DOTALL,
    )
    return text

LOCAL = None
def _local_candidates(root):
    """Site-root relative Mintlify path -> candidate local file paths."""
    if root.startswith("spec/1.0"):
        root = "1.0" + root[len("spec/1.0"):]
    if root.endswith(".json"):
        return [root]
    rel = root[:-3] if root.endswith(".md") else root
    if rel == "1.0":
        rel = "1.0/index"
    elif rel.endswith("/index"):
        rel = rel[:-6]
    out = [rel + ".md", rel + "/index.md"]
    if rel.endswith("/schema-files"):
        out.append("1.0/schema.json")
    return out


def build_local():
    """All local .md/.json: existing spec pages + this batch (not yet on disk)."""
    local = set()
    for base, _d, files in os.walk(OUT):
        for fn in files:
            if fn.endswith((".md", ".json")):
                local.add(os.path.relpath(os.path.join(base, fn), OUT).replace(os.sep, "/"))
    local.update(p + ".md" for p in PAGES)
    local.add("1.0/schema.json")
    return local


def resolve_link(target, rel_path):
    """Local relative .md/.json link when the page is local, else live site."""
    global LOCAL
    if LOCAL is None:
        LOCAL = build_local()
    if target.startswith("#CARDHREF#"):
        return resolve_link(target[len("#CARDHREF#"):], rel_path)
    if target.startswith(LIVE + "/"):
        target = "/" + target[len(LIVE) + 1 :]
    if target.startswith("//") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return f"]({target})"
    path, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    if target.startswith("#") or target.startswith("//") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path):
        return f"]({target})"
    if re.search(r"\.(png|jpe?g|gif|svg|webp|avif|mp4|css|js)$", path, re.I):
        return f"]({target})"
    if path.startswith("/"):
        root = path.lstrip("/")
    else:
        root = posixpath.normpath(
            posixpath.join(posixpath.dirname(rel_path), path)
        ).lstrip("./")
    if root in ("", "."):
        return f"]({LIVE}{target})"
    for cand in _local_candidates(root):
        if cand in LOCAL:
            rel = posixpath.relpath(cand, posixpath.dirname(rel_path))
            if not rel.startswith("."):
                rel = "./" + rel
            return f"]({rel}{anchor})"
    return f"]({LIVE}{target})"


def process(rel_path):
    src_path = os.path.join(SRC, rel_path + ".mdx")
    out_path = os.path.join(OUT, rel_path + ".md")
    with open(src_path, encoding="utf-8") as f:
        text = f.read()

    fm_m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    frontmatter = fm_m.group(0) if fm_m else ""
    body = text[fm_m.end():] if fm_m else text

    if rel_path == "introduction":
        body = preprocess_introduction(body)
    body = convert_cards(body)
    body = convert_admonitions(body)
    body = convert_img(body)
    body = convert_video(body)
    body = convert_div_a(body)
    body = convert_span_badge(body)
    body = convert_steps(body)
    body = strip_jsx_divs(body)
    body = localize_assets(body, rel_path)
    body = re.sub(
        r"\]\((?:#CARDHREF#)?([a-zA-Z./#][^)#]*)\)",
        lambda m: resolve_link(m.group(1), rel_path),
        body,
    )
    body = "\n".join(T.rewrite_headings(body.splitlines()))
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body)


def main():
    for rel in PAGES:
        process(rel)
    print(f"converted {len(PAGES)} pages -> docs-zh/")


if __name__ == "__main__":
    main()
