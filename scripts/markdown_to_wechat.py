#!/usr/bin/env python3
"""Convert Markdown into WeChat Official Account friendly rich-text HTML."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


THEMES = {
    "clean": {
        "accent": "#1f6feb",
        "accent_soft": "#edf5ff",
        "text": "#2b2f36",
        "muted": "#6b7280",
        "border": "#e5e7eb",
        "code_bg": "#f6f8fa",
        "quote_bg": "#f8fafc",
    },
    "tech": {
        "accent": "#0f766e",
        "accent_soft": "#ecfdf5",
        "text": "#22272e",
        "muted": "#64748b",
        "border": "#dbe4ea",
        "code_bg": "#f4f7f7",
        "quote_bg": "#f0fdfa",
    },
}


def style(**items: str) -> str:
    return "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in items.items() if v)


def strip_frontmatter(markdown: str) -> str:
    if markdown.startswith("---\n"):
        end = markdown.find("\n---\n", 4)
        if end != -1:
            return markdown[end + 5 :].lstrip()
    return markdown


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^\s*#\s+(.+?)\s*$", line)
        if match:
            return re.sub(r"[*_`#]", "", match.group(1)).strip() or fallback
    return fallback


def parse_link_target(raw: str) -> Tuple[str, str]:
    raw = raw.strip()
    if not raw:
        return "", ""
    if raw[0] in ("'", '"') and raw[-1:] == raw[0]:
        return raw[1:-1], ""
    if " " not in raw:
        return raw, ""
    url, title = raw.split(" ", 1)
    return url.strip(), title.strip().strip("'\"")


def render_inline(text: str, palette: dict) -> str:
    placeholders: List[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\u0000{len(placeholders) - 1}\u0000"

    def image_repl(match: re.Match[str]) -> str:
        alt = html.escape(match.group(1), quote=True)
        src, title = parse_link_target(match.group(2))
        title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
        img_style = style(
            display="block",
            width="100%",
            max_width="100%",
            height="auto",
            margin="18px auto",
            border_radius="6px",
        )
        return stash(f'<img src="{html.escape(src, quote=True)}" alt="{alt}"{title_attr} style="{img_style}" />')

    def link_repl(match: re.Match[str]) -> str:
        label = render_inline(match.group(1), palette)
        href, title = parse_link_target(match.group(2))
        title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
        link_style = style(color=palette["accent"], text_decoration="none", border_bottom=f"1px solid {palette['accent']}")
        return stash(f'<a href="{html.escape(href, quote=True)}"{title_attr} style="{link_style}">{label}</a>')

    def code_repl(match: re.Match[str]) -> str:
        code_style = style(
            font_family="Consolas, Menlo, Monaco, monospace",
            font_size="0.92em",
            color="#d14",
            background=palette["code_bg"],
            padding="2px 5px",
            border_radius="4px",
        )
        return stash(f'<code style="{code_style}">{html.escape(match.group(1))}</code>')

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_repl, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"`([^`]+)`", code_repl, text)

    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"<em>\1</em>", escaped)

    def restore(match: re.Match[str]) -> str:
        return placeholders[int(match.group(1))]

    return re.sub("\u0000(\\d+)\u0000", restore, escaped)


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.match(r"^:?-{3,}:?$", cell or "") for cell in cells)


def split_table_row(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_code_block(code: str, language: str, palette: dict) -> str:
    wrapper_style = style(
        margin="16px 0",
        padding="0",
        border=f"1px solid {palette['border']}",
        border_radius="6px",
        overflow="hidden",
        background=palette["code_bg"],
    )
    lang_style = style(
        display="block",
        padding="8px 12px",
        font_size="12px",
        color=palette["muted"],
        background="#eef2f7",
        border_bottom=f"1px solid {palette['border']}",
        font_family="Consolas, Menlo, Monaco, monospace",
    )
    pre_style = style(
        margin="0",
        padding="13px 14px",
        overflow_x="auto",
        white_space="pre",
        line_height="1.65",
        font_size="13px",
        font_family="Consolas, Menlo, Monaco, monospace",
        color="#24292f",
    )
    lang = html.escape(language.strip() or "code")
    return (
        f'<section style="{wrapper_style}">'
        f'<span style="{lang_style}">{lang}</span>'
        f'<pre style="{pre_style}"><code>{html.escape(code.rstrip())}</code></pre>'
        "</section>"
    )


def render_heading(level: int, text: str, palette: dict) -> str:
    content = render_inline(text.strip(), palette)
    if level == 1:
        h_style = style(
            margin="8px 0 22px",
            padding="0 0 13px",
            font_size="24px",
            line_height="1.35",
            font_weight="700",
            color=palette["text"],
            border_bottom=f"2px solid {palette['accent']}",
        )
    elif level == 2:
        h_style = style(
            margin="28px 0 14px",
            padding="8px 12px",
            font_size="20px",
            line_height="1.45",
            font_weight="700",
            color=palette["text"],
            background=palette["accent_soft"],
            border_left=f"4px solid {palette['accent']}",
            border_radius="4px",
        )
    elif level == 3:
        h_style = style(
            margin="24px 0 10px",
            font_size="18px",
            line_height="1.5",
            font_weight="700",
            color=palette["text"],
        )
    else:
        h_style = style(
            margin="20px 0 8px",
            font_size="16px",
            line_height="1.55",
            font_weight="700",
            color=palette["text"],
        )
    return f'<h{level} style="{h_style}">{content}</h{level}>'


def render_paragraph(lines: Iterable[str], palette: dict) -> str:
    text = " ".join(line.strip() for line in lines).strip()
    p_style = style(
        margin="12px 0",
        font_size="16px",
        line_height="1.85",
        color=palette["text"],
        letter_spacing="0",
        text_align="left",
    )
    return f'<p style="{p_style}">{render_inline(text, palette)}</p>'


def render_list(items: List[str], ordered: bool, palette: dict) -> str:
    tag = "ol" if ordered else "ul"
    list_style = style(
        margin="12px 0",
        padding_left="1.35em",
        color=palette["text"],
        font_size="16px",
        line_height="1.85",
    )
    li_style = style(margin="4px 0", padding_left="2px")
    rendered = "".join(f'<li style="{li_style}">{render_inline(item, palette)}</li>' for item in items)
    return f'<{tag} style="{list_style}">{rendered}</{tag}>'


def render_blockquote(lines: List[str], palette: dict) -> str:
    text = "<br />".join(render_inline(line.strip(), palette) for line in lines if line.strip())
    quote_style = style(
        margin="16px 0",
        padding="12px 14px",
        color="#4b5563",
        background=palette["quote_bg"],
        border_left=f"4px solid {palette['accent']}",
        border_radius="4px",
        font_size="15px",
        line_height="1.8",
    )
    return f'<blockquote style="{quote_style}">{text}</blockquote>'


def render_table(rows: List[List[str]], palette: dict) -> str:
    table_style = style(
        width="100%",
        border_collapse="collapse",
        margin="16px 0",
        font_size="14px",
        line_height="1.65",
        color=palette["text"],
    )
    th_style = style(
        border=f"1px solid {palette['border']}",
        padding="9px 10px",
        background=palette["accent_soft"],
        font_weight="700",
        text_align="left",
    )
    td_style = style(border=f"1px solid {palette['border']}", padding="9px 10px", text_align="left")
    header = rows[0]
    body = rows[1:]
    html_rows = [
        "<tr>" + "".join(f'<th style="{th_style}">{render_inline(cell, palette)}</th>' for cell in header) + "</tr>"
    ]
    for row in body:
        html_rows.append(
            "<tr>" + "".join(f'<td style="{td_style}">{render_inline(cell, palette)}</td>' for cell in row) + "</tr>"
        )
    return f'<table style="{table_style}"><tbody>{"".join(html_rows)}</tbody></table>'


def render_markdown(markdown: str, theme: str) -> str:
    palette = THEMES[theme]
    lines = strip_frontmatter(markdown).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: List[str] = []
    paragraph: List[str] = []
    i = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(render_paragraph(paragraph, palette))
            paragraph = []

    while i < len(lines):
        line = lines[i]

        fence = re.match(r"^\s*```([\w.+-]*)\s*$", line)
        if fence:
            flush_paragraph()
            language = fence.group(1)
            i += 1
            code_lines = []
            while i < len(lines) and not re.match(r"^\s*```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            blocks.append(render_code_block("\n".join(code_lines), language, palette))
            i += 1
            continue

        if not line.strip():
            flush_paragraph()
            i += 1
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            blocks.append(render_heading(len(heading.group(1)), heading.group(2), palette))
            i += 1
            continue

        if re.match(r"^\s*[-*_]{3,}\s*$", line):
            flush_paragraph()
            hr_style = style(border="0", border_top=f"1px solid {palette['border']}", margin="24px 0")
            blocks.append(f'<hr style="{hr_style}" />')
            i += 1
            continue

        if line.lstrip().startswith(">"):
            flush_paragraph()
            quote_lines = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            blocks.append(render_blockquote(quote_lines, palette))
            continue

        list_match = re.match(r"^\s*(?:[-+*]\s+|\d+[.)]\s+)(.+)$", line)
        if list_match:
            flush_paragraph()
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            items = []
            while i < len(lines):
                marker = re.match(r"^\s*(?:([-+*])\s+|(\d+)[.)]\s+)(.+)$", lines[i])
                if not marker:
                    break
                current_ordered = marker.group(2) is not None
                if current_ordered != ordered:
                    break
                items.append(marker.group(3).strip())
                i += 1
            blocks.append(render_list(items, ordered, palette))
            continue

        if "|" in line and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            flush_paragraph()
            rows = [split_table_row(line)]
            i += 2
            while i < len(lines) and "|" in lines[i].strip():
                rows.append(split_table_row(lines[i]))
                i += 1
            blocks.append(render_table(rows, palette))
            continue

        paragraph.append(line)
        i += 1

    flush_paragraph()
    return "\n".join(blocks)


def wrap_document(body: str, title: str, theme: str, copy_hint: bool) -> str:
    palette = THEMES[theme]
    page_style = style(
        margin="0",
        padding="24px 12px",
        background="#ffffff",
        font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif",
    )
    article_style = style(
        max_width="720px",
        margin="0 auto",
        padding="0",
        color=palette["text"],
        font_size="16px",
        line_height="1.8",
    )
    hint_style = style(
        margin="0 0 18px",
        padding="10px 12px",
        color=palette["muted"],
        background="#f9fafb",
        border=f"1px dashed {palette['border']}",
        border_radius="6px",
        font_size="13px",
        line_height="1.6",
    )
    hint = ""
    if copy_hint:
        hint = f'<p style="{hint_style}">提示：在浏览器中打开本文件，选中文章正文区域后复制，可粘贴到微信公众号编辑器。</p>'
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
</head>
<body style="{page_style}">
  <article style="{article_style}">
    {hint}
    {body}
  </article>
</body>
</html>
"""


def convert(input_path: Path, output_path: Path, title: Optional[str], theme: str, body_only: bool, copy_hint: bool) -> None:
    markdown = input_path.read_text(encoding="utf-8-sig")
    markdown = strip_frontmatter(markdown)
    document_title = title or extract_title(markdown, input_path.stem)
    body = render_markdown(markdown, theme)
    output = body if body_only else wrap_document(body, document_title, theme, copy_hint)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Markdown to WeChat Official Account rich-text HTML.")
    parser.add_argument("input", type=Path, help="Input Markdown file.")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML file. Defaults to <input>.wechat.html.")
    parser.add_argument("--title", help="HTML page title. Defaults to first H1 or filename.")
    parser.add_argument("--theme", choices=sorted(THEMES), default="clean", help="Article style theme.")
    parser.add_argument("--body-only", action="store_true", help="Output only the article body HTML fragment.")
    parser.add_argument("--no-copy-hint", action="store_true", help="Omit the browser copy hint.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    input_path = args.input.resolve()
    if not input_path.exists():
        parser.error(f"Input file does not exist: {input_path}")
    output_path = (args.output or input_path.with_suffix(".wechat.html")).resolve()
    convert(
        input_path=input_path,
        output_path=output_path,
        title=args.title,
        theme=args.theme,
        body_only=args.body_only,
        copy_hint=not args.no_copy_hint,
    )
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
