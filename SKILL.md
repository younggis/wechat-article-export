---
name: wechat-article-export
description: Convert assistant responses or Markdown drafts into WeChat Official Account article files. Use when the user asks to output content as a 公众号文章, 微信公众号富文本, Markdown 转公众号格式, 保存为可复制到公众号编辑器的 HTML, or prepare a WeChat-ready article file.
---

# WeChat Article Export

## Overview

Create a polished Markdown draft first, then export it to a WeChat editor-friendly HTML file with inline styles. Use the bundled script for deterministic conversion and save the final file in the current workspace unless the user specifies another path.

## Workflow

1. Draft or refine the article in Markdown.
2. Save the Markdown source as a `.md` file in the workspace.
3. Run `scripts/markdown_to_wechat.py` to create a `.wechat.html` file.
4. Report both saved paths to the user.

## Script Usage

Run from any workspace:

```powershell
python C:\Users\young\.codex\skills\wechat-article-export\scripts\markdown_to_wechat.py article.md -o article.wechat.html
```

Optional flags:

- `--title "标题"`: set the HTML page title. Defaults to the first H1 or filename.
- `--theme clean|tech`: choose a restrained article style. Default is `clean`.
- `--body-only`: output only the article body fragment instead of a full HTML document.
- `--no-copy-hint`: omit the top copy instruction note.

The output is HTML with inline CSS intended to be opened in a browser and copied into the WeChat Official Account editor. Keep the generated `.md` file as the editable source of truth.

## Authoring Rules

- Preserve the user's technical meaning and code exactly when converting.
- Use Markdown headings for article structure; avoid manual HTML unless the user explicitly asks for it.
- Keep code blocks fenced with language hints when possible.
- For WeChat readability, prefer short paragraphs, explicit section headings, and compact code snippets.
- If the user asks for "公众号富文本", provide `.wechat.html`; if they ask for source too, also provide `.md`.

## Supported Markdown

The bundled converter supports common article Markdown: H1-H4, paragraphs, bold, italic, inline code, links, images, unordered lists, ordered lists, blockquotes, fenced code blocks, horizontal rules, and simple pipe tables.
