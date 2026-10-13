"""MkDocs build helpers for the AG-UI Chinese docs.

mermaid_fence: render mermaid with a neutral, theme-following init so the
diagrams match the black/white site (light + dark) instead of Mermaid's
default pastel.
"""


def mermaid_fence(source, language, class_name, options, md, **kwargs):
    from pymdownx.superfences import fence_code_format

    init = (
        "%%{init: {'theme': 'base', 'themeVariables': "
        "{'primaryColor': '#ffffff', 'primaryBorderColor': '#9a9aa2', "
        "'primaryTextColor': '#09090b', 'lineColor': '#52525b', "
        "'edgeLabelBackground': '#ffffff', 'clusterBkg': '#fafafa', "
        "'clusterBorder': '#d4d4d8', "
        "'fontFamily': '-apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif', "
        "'fontSize': '14px'}, 'flowchart': {'nodeSpacing': 45, 'rankSpacing': 55, 'padding': 12, 'curve': 'basis'}}}%%\n"
    )
    return fence_code_format(
        init + source, language, class_name, options, md, **kwargs
    )
