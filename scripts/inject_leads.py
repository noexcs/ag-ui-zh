#!/usr/bin/env python3
"""One-shot: insert a muted lead paragraph (the frontmatter description,
version marker stripped) right under the auto-rendered title of each page.
The original Mintlify site shows the description as a subtitle under the H1;
mkdocs-material only puts it in search/OG metadata, so we render it ourselves.

Idempotent: skips files that already have a <em class="lead"> line.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs-zh")


def main():
    count = 0
    for dirpath, _d, files in os.walk(DOCS):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dirpath, fn)
            with open(p, encoding="utf-8") as f:
                text = f.read()
            if '<em class="lead">' in text:
                continue
            m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            if not m:
                continue
            fm = m.group(1)
            dm = re.search(r'^description:\s*"?([^"\n]+?)"?\s*$', fm, re.MULTILINE)
            if not dm:
                continue
            desc = dm.group(1).strip()
            lead = re.sub(r"\s*[—–-]\s*1\.0\s*$", "", desc).strip()
            if not lead:
                continue
            insert_at = m.end()
            body = text[insert_at:]
            # lead sits before the first blank line of the body
            new_body = f'<em class="lead">{lead}</em>\n\n' + body.lstrip("\n")
            with open(p, "w", encoding="utf-8") as f:
                f.write(text[:insert_at] + new_body)
            count += 1
    print(f"lead inserted in {count} files")


if __name__ == "__main__":
    main()
