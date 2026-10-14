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
    ("TypeScript SDK", "sdk/js/core/overview.html",
     '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 3h18v18H3V3zm4.5 5.2v7.6H9.7v-3h1.2v-1.6H9.7V8.2h1.4v-1.6H4.8v1.6h2.7zm12.3 0h-3.4c-1.5 0-2.5 1-2.5 2.8v2c0 1.8 1 2.8 2.5 2.8h1v1.6h1.9v-9.2zm-1.9 6.2h-1.2c-.7 0-1.1-.4-1.1-1.2v-1.9c0-.8.4-1.2 1.1-1.2h1.2v4.3z" opacity=".9"/></svg>'),
    ("Python SDK", "sdk/python/core/overview.html",
     '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2c-2.1 0-3.6.9-3.6 2.5v2.1c0 .9.6 1.5 1.5 1.5h3.7c2.5 0 4.4.9 4.4 3.4 0 1.9-1.1 3-2.9 3h-1.3v-2.1c0-2-1.7-3.7-4.4-3.7H9.6c-2 0-3.4 1-3.4 2.8v6c0 2 1.3 3 3.3 3h1.4v-2c0-1.3 1-2.2 2.5-2.2h2.4c2.6 0 4.2-1.8 4.2-4.7 0-2.9-2.1-4.2-4.9-4.2h-3V4.5c0-.8.6-1.2 1.9-1.2 1.5 0 2.1.6 2.1 1.2h2.3c0-2-1.7-3-4.4-3z"/></svg>'),
    (".NET SDK", "sdk/dotnet/abstractions/overview.html",
     '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 3h18v18H3V3zm4.5 5.2v7.6H9.7v-3h1.2v-1.6H9.7V8.2h1.4v-1.6H4.8v1.6h2.7zm12.3 0h-3.4c-1.5 0-2.5 1-2.5 2.8v2c0 1.8 1 2.8 2.5 2.8h1v1.6h1.9v-9.2zm-1.9 6.2h-1.2c-.7 0-1.1-.4-1.1-1.2v-1.9c0-.8.4-1.2 1.1-1.2h1.2v4.3z" opacity=".9"/></svg>'),
]
def sdk_block(prefix):
    items = "\n".join(
        f'<a class="agui-sdk__link" href="{prefix}{u}">'
        f'<span class="agui-sdk__icon">{i}</span><span>{n}</span></a>'
        for n, u, i in SDK
    )
    return '<ul class="agui-sdk" aria-label="SDK 快捷链接">' + items + "</ul>\n"

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

    # 页内相对前缀（按页面目录深度）
    here = os.path.dirname(path).replace(SITE, "").strip("/").lower()
    prefix = "../" * (here.count("/") + 1) if here else ""

    # 1) 品牌名去掉“中文文档”；版本徽章仅规范页显示（对齐原站版本选择器）
    chip = '<span class="agui-version-chip">1.0（当前）</span>' if here.startswith("1.0") else ""
    html = html.replace(
        "<span class=\"md-ellipsis\">\n            AG-UI Protocol 中文文档\n          </span>",
        '<span class="md-ellipsis">\n            AG-UI Protocol\n          </span>' + chip,
        1,
    )

    # 2) 三 Tab 行（全部站内；active 按当前 Tab 判定）
    if here.startswith("1.0"):
        active_docs, active_spec, active_sdk = "", " agui-tab--active", ""
    elif here.startswith("sdk"):
        active_docs, active_spec, active_sdk = "", "", " agui-tab--active"
    else:
        active_docs, active_spec, active_sdk = " agui-tab--active", "", ""
    tabs = (
        '<nav class="agui-tabs-row" aria-label="主导航">'
        '<div class="md-grid"><ul>'
        f'<li><a href="{prefix}introduction.html" class="{active_docs}">文档</a></li>'
        f'<li><a href="{prefix}1.0/index.html" class="{active_spec}">规范</a></li>'
        f'<li><a href="{prefix}sdk/js/core/overview.html" class="{active_sdk}">SDK</a></li>'
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
        lambda m: m.group(1) + "\n" + sdk_block(prefix),
        html,
        count=1,
    )

    # 4) 右侧 TOC 标题：只认 .md-sidebar--secondary 容器内的 nav
    #    （主侧栏里也有一个 md-nav--secondary，是 Material 的 __toc 联动，不能锚它）
    sec = html.find('md-sidebar md-sidebar--secondary')
    if sec != -1:
        nav_pos = html.find('<nav class="md-nav md-nav--secondary"', sec)
        if nav_pos != -1:
            html = html[:nav_pos] + TOC_TITLE + html[nav_pos:]

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
