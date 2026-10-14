"""Post-build: inject Mintlify-style header (brand + 1.0 版本徽章 + 三 Tab 行)
and the sidebar SDK quick-links into the built site.

Run after `mkdocs build` (CI / 本地). Idempotent via a marker comment.
"""
import os
import re
import sys

SITE = os.path.join(os.path.dirname(__file__), "..", "site-zh")
MARKER = "<!-- ag-ui-zh:header-injected -->"

SDK = [
    ("TypeScript SDK", "https://docs.ag-ui.com/sdk/js/core/overview",
     '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 3h18v18H3V3zm10.76 16.89c.5 0 .91-.08 1.25-.25.34-.16.6-.38.8-.65.18-.27.28-.58.31-.93h-2.1c0 .2.06.36.17.48.11.12.3.18.55.18.2 0 .38-.04.54-.13.16-.09.3-.22.41-.38.11-.17.19-.36.24-.58.06-.21.08-.44.08-.7v-.76c0-.38-.05-.71-.16-.99a1.8 1.8 0 0 0-.47-.7 1.87 1.87 0 0 0-.73-.4c-.31-.1-.66-.15-1.05-.15-.4 0-.76.05-1.08.16a1.8 1.8 0 0 0-.73.44 1.72 1.72 0 0 0-.42.68c-.09.26-.13.55-.13.86h1.87c0-.14.02-.27.06-.38.04-.11.11-.2.2-.28a.6.6 0 0 1 .28-.15c.11-.04.24-.05.38-.05.2 0 .37.04.5.11.13.07.22.16.29.28.06.12.1.25.11.39h-2.45v4.93zm6.24 0c.5 0 .92-.08 1.26-.25.33-.16.6-.38.79-.65.18-.27.28-.58.3-.93h-2.09c0 .2.06.36.17.48.11.12.29.18.54.18.2 0 .38-.04.54-.13.16-.09.3-.22.41-.38.11-.17.19-.36.24-.58.06-.21.08-.44.08-.7v-.76c0-.38-.05-.71-.16-.99a1.8 1.8 0 0 0-.47-.7 1.87 1.87 0 0 0-.73-.4c-.31-.1-.66-.15-1.05-.15-.4 0-.76.05-1.08.16a1.8 1.8 0 0 0-.73.44 1.72 1.72 0 0 0-.42.68c-.09.26-.13.55-.13.86h1.87c0-.14.02-.27.06-.38.04-.11.11-.2.2-.28a.6.6 0 0 1 .28-.15c.11-.04.24-.05.38-.05.2 0 .37.04.5.11.13.07.22.16.29.28.06.12.1.25.11.39h-2.45v4.93z" opacity=".9"/></svg>'),
    ("Python SDK", "https://docs.ag-ui.com/sdk/python/core/overview",
     '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2c-2.1 0-3.6.9-3.6 2.5v2.1c0 .9.6 1.5 1.5 1.5h3.7c2.5 0 4.4.9 4.4 3.4 0 1.9-1.1 3-2.9 3h-1.3v-2.1c0-2-1.7-3.7-4.4-3.7H9.6c-2 0-3.4 1-3.4 2.8v6c0 2 1.3 3 3.3 3h1.4v-2c0-1.3 1-2.2 2.5-2.2h2.4c2.6 0 4.2-1.8 4.2-4.7 0-2.9-2.1-4.2-4.9-4.2h-3V4.5c0-.8.6-1.2 1.9-1.2 1.5 0 2.1.6 2.1 1.2h2.3c0-2-1.7-3-4.4-3z"/></svg>'),
    (".NET SDK", "https://docs.ag-ui.com/sdk/dotnet/abstractions/overview",
     '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 3h18v18H3V3zm4.5 5.2v7.6H9.7v-3h1.2v-1.6H9.7V8.2h1.4v-1.6H4.8v1.6h2.7zm12.3 0h-3.4c-1.5 0-2.5 1-2.5 2.8v2c0 1.8 1 2.8 2.5 2.8h1v1.6h1.9v-9.2zm-1.9 6.2h-1.2c-.7 0-1.1-.4-1.1-1.2v-1.9c0-.8.4-1.2 1.1-1.2h1.2v4.3z" opacity=".9"/></svg>'),
]

SDK_ITEMS = "\n".join(
    f'<a class="agui-sdk__link" href="{u}" rel="noopener">'
    f'<span class="agui-sdk__icon">{i}</span><span>{n}</span></a>'
    for n, u, i in SDK
)

SDK_BLOCK = (
    '<ul class="agui-sdk" aria-label="SDK 快捷链接">' + SDK_ITEMS + "</ul>\n"
)

CSS = """
/* ===== Mintlify 风格复刻：页头 Tab 行 / 版本徽章 / 侧栏 SDK 快捷链 / TOC ===== */
.agui-version-chip {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--agui-text-muted);
  border: 1px solid var(--agui-border);
  border-radius: 0.5rem;
  padding: 0.2rem 0.55rem;
  margin-left: 0.9rem;
  white-space: nowrap;
  align-self: center;
}
/* 页头只留品牌名 + 徽章，隐藏 Material 的页内标题第二行 */
.md-header__title .md-header__topic + .md-header__topic {
  display: none;
}
/* 侧栏顶部站点名（与页头重复，原站侧栏无此项） */
.md-sidebar--primary .md-nav__title {
  display: none;
}
.agui-tabs-row {
  position: sticky;
  top: 4rem;
  z-index: 3;
  background-color: var(--agui-bg);
  border-bottom: 1px solid var(--agui-border-soft);
}
.agui-tabs-row .md-grid {
  padding: 0 1rem;
  display: flex;
  align-items: stretch;
  height: 48px;
  gap: 1.8rem;
}
.agui-tabs-row ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: stretch;
}
.agui-tabs-row a {
  display: inline-flex;
  align-items: center;
  height: 48px;
  padding: 0 0.1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--agui-text-muted);
  border-bottom: 2px solid transparent;
  text-decoration: none;
  font-family: var(--font-body);
}
.agui-tabs-row a:hover {
  color: var(--agui-text);
}
.agui-tabs-row a.agui-tab--active {
  color: var(--agui-text);
  border-bottom-color: var(--agui-text);
}
.agui-sdk {
  list-style: none;
  margin: 0;
  padding: 0.4rem 0 0.8rem;
}
.agui-sdk__link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.42rem 0.9rem;
  font-size: 0.87rem;
  font-weight: 450;
  color: var(--agui-text-muted);
  text-decoration: none;
}
.agui-sdk__link:hover {
  color: var(--agui-text);
  background-color: var(--agui-bg-inset);
}
.agui-sdk__icon {
  display: inline-flex;
  width: 1.35rem;
  height: 1.35rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.4rem;
  background: var(--agui-bg-inset);
  color: var(--agui-text);
  flex: 0 0 auto;
}
/* 侧栏分组：标签 + 组间分隔线（结构: nav > ul.md-nav__list > li.section） */
.md-sidebar--primary .md-nav--primary > .md-nav__list > .md-nav__item--section {
  border-top: 1px solid var(--agui-border-soft);
  margin-top: 0.9rem;
  padding-top: 0.8rem;
}
.md-sidebar--primary .md-nav--primary > .md-nav__list > .md-nav__item--section:first-child {
  border-top: none;
  margin-top: 0;
  padding-top: 0.2rem;
}
.md-sidebar--primary .md-nav--primary > .md-nav__list > .md-nav__item--section > .md-nav__link,
.md-sidebar--primary .md-nav--primary > .md-nav__list > .md-nav__item--section > label > .md-nav__link {
  display: block;
  margin: 0 0 0.5rem;
  padding: 0 0.9rem;
  background: none;
  font-size: 0.8rem;
  font-weight: 650;
  color: var(--agui-text);
  border-radius: 0;
  text-transform: none;
  letter-spacing: 0.01em;
}
.md-sidebar--primary .md-nav--primary > .md-nav__list > .md-nav__item--section > .md-nav__link:hover {
  background: none;
  color: var(--agui-text);
}
/* 嵌套组（事件模式 / 传输）：组名弱化，子项再缩进 */
.md-sidebar--primary .md-nav--primary .md-nav .md-nav__item--section > .md-nav__link,
.md-sidebar--primary .md-nav--primary .md-nav .md-nav__item--section > label > .md-nav__link {
  font-weight: 550;
  font-size: 0.82rem;
  color: var(--agui-text-muted);
  margin: 0.7rem 0 0.35rem;
  padding: 0 0.9rem;
  background: none;
}
/* 右侧 On this page：隐藏原标题，用注入的带图标标题 */
.md-sidebar--secondary .md-nav__title {
  display: none !important;
}
.agui-toc-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 1rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--agui-text);
  font-family: var(--font-body);
}
.md-sidebar--secondary .md-nav__link {
  padding-left: 1rem;
  border-left: 2px solid transparent;
}
.md-sidebar--secondary .md-nav__link:hover {
  background: none;
  color: var(--agui-text);
}
.md-sidebar--secondary .md-nav__link--active {
  color: var(--agui-text);
  font-weight: 550;
  border-left-color: var(--agui-text);
  background: none;
  box-shadow: none;
}
"""

TOC_TITLE = (
    '<div class="agui-toc-title" aria-hidden="true">'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18">'
    '<path fill="currentColor" d="M4 6h16v2H4zm0 5h10v2H4zm0 5h16v2H4z"/>'
    "</svg>"
    "<span>本页内容</span></div>"
)


def patch(path):
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8") as f:
        html = f.read()
    if MARKER in html:
        return False

    # 1) 品牌名去掉“中文文档” + 版本徽章（标题区之后，header flex 子项）
    html = html.replace(
        "<span class=\"md-ellipsis\">\n            AG-UI Protocol 中文文档\n          </span>",
        '<span class="md-ellipsis">\n            AG-UI Protocol\n          </span>'
        '<span class="agui-version-chip">1.0（当前）</span>',
        1,
    )

    # 2) 三 Tab 行（注入在 header 之后）
    here = os.path.dirname(path).replace(SITE, "").strip("/").lower()
    active = here.startswith("1.0")
    spec_href = "index.html" if here else "1.0/index.html"
    tabs = (
        '<nav class="agui-tabs-row" aria-label="主导航">'
        '<div class="md-grid"><ul>'
        '<li><a href="https://docs.ag-ui.com/introduction" rel="noopener">文档</a></li>'
        f'<li><a href="{spec_href}" class="{"agui-tab--active" if active else ""}">规范</a></li>'
        '<li><a href="https://docs.ag-ui.com/sdk/js/core/overview" rel="noopener">SDK</a></li>'
        "</ul></div></nav>"
    )
    html = re.sub(
        r"(</header>)",
        lambda m: m.group(1) + "\n  " + MARKER + "\n  " + tabs,
        html,
        count=1,
    )

    # 3) 侧栏 SDK 快捷链
    html = re.sub(
        r'(<nav class="md-nav md-nav--primary"[^>]*>)',
        r"\1\n" + SDK_BLOCK,
        html,
        count=1,
    )

    # 4) 右侧 TOC 标题（仅在有 TOC 的页面）
    if '<nav class="md-nav md-nav--secondary"' in html:
        html = html.replace(
            '<nav class="md-nav md-nav--secondary"',
            TOC_TITLE + '<nav class="md-nav md-nav--secondary"',
            1,
        )

    # 5) 样式
    html = html.replace("</body>", "<style>" + CSS + "</style>\n</body>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True


def main():
    n = 0
    for dp, _, fns in os.walk(SITE):
        for fn in fns:
            if fn.endswith(".html"):
                if patch(os.path.join(dp, fn)):
                    n += 1
    print(f"header injected: {n} pages")


if __name__ == "__main__":
    sys.exit(main())
