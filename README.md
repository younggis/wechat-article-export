# wechat-article-export

把 Markdown 草稿或 Codex 生成的文章内容，转换成适合微信公众号后台复制粘贴的富文本 HTML 文件。

这个 Skill 面向 Codex 使用：当你希望 Codex 将回答、技术文章、教程、项目复盘、公众号草稿等内容整理成微信公众号可用格式时，可以启用它。它会先保留 Markdown 源稿，再通过内置脚本生成带内联样式的 `.wechat.html` 文件。

## 适用场景

- 将 Codex 回复整理为微信公众号文章
- 将 Markdown 技术文档转换为公众号富文本
- 输出可在浏览器打开并复制到公众号编辑器的 HTML
- 为技术文章、产品说明、教程、复盘、周报等生成排版更稳定的公众号版本
- 同时保留 `.md` 源稿和 `.wechat.html` 发布稿

## 核心能力

- **Markdown 源稿优先**：先沉淀可维护的 `.md` 文件，再生成发布用 HTML。
- **公众号友好 HTML**：生成带内联样式的 HTML，便于复制到微信公众号编辑器。
- **基础排版支持**：支持标题、段落、加粗、斜体、链接、图片、列表、引用、代码块、分割线和简单表格。
- **主题选择**：内置 `clean` 和 `tech` 两种克制风格。
- **可复用脚本**：通过 `scripts/markdown_to_wechat.py` 稳定转换，避免每次手写 HTML。

## 安装方式

将本仓库放到 Codex 的 skills 目录下：

```powershell
cd C:\Users\young\.codex\skills
git clone https://github.com/younggis/wechat-article-export.git
```

目录名需要保持为：

```text
wechat-article-export
```

安装后，Codex 会通过 `SKILL.md` 的 frontmatter 描述自动识别触发场景。

## 使用方式

在 Codex 中直接描述导出目标，例如：

```text
使用 wechat-article-export，把上面的回答整理成一篇微信公众号文章，并导出可复制到公众号编辑器的 HTML。
```

也可以指定已有 Markdown 文件：

```text
把 G:\knowledge\agent-workflow.md 转成微信公众号富文本 HTML，风格用 tech。
```

Codex 通常会输出两个文件：

```text
article.md
article.wechat.html
```

其中 `.md` 是可继续编辑的源稿，`.wechat.html` 是打开后复制到公众号后台的发布稿。

## 脚本用法

你也可以直接运行内置转换脚本：

```powershell
python C:\Users\young\.codex\skills\wechat-article-export\scripts\markdown_to_wechat.py article.md -o article.wechat.html
```

常用参数：

| 参数 | 说明 |
| --- | --- |
| `input` | 输入 Markdown 文件 |
| `-o, --output` | 输出 HTML 文件，默认 `<input>.wechat.html` |
| `--title` | 设置 HTML 页面标题，默认取第一个 H1 或文件名 |
| `--theme clean|tech` | 选择主题，默认 `clean` |
| `--body-only` | 只输出正文 HTML 片段，不输出完整 HTML 文档 |
| `--no-copy-hint` | 去掉页面顶部的复制提示 |

示例：

```powershell
python C:\Users\young\.codex\skills\wechat-article-export\scripts\markdown_to_wechat.py `
  .\draft.md `
  -o .\draft.wechat.html `
  --title "AI Agent 工作流实践" `
  --theme tech
```

## 支持的 Markdown

当前转换器支持常见公众号文章结构：

- H1-H4 标题
- 普通段落
- 加粗、斜体、行内代码
- 链接和图片
- 无序列表和有序列表
- 引用块
- fenced code block 代码块
- 分割线
- 简单 pipe table 表格
- YAML frontmatter 自动跳过

## 推荐写作规范

- 使用清晰的 Markdown 标题组织结构。
- 段落尽量短，便于移动端阅读。
- 技术文章保留代码块语言标记，例如 ` ```python `。
- 表格保持简单，避免过宽。
- 图片使用可访问的 URL 或相对路径，发布前在浏览器中检查是否能正常显示。
- 不要在 Markdown 中混入复杂 HTML，除非确实需要且已验证公众号后台兼容。

## 推荐工作流

1. 先把文章内容写入或整理为 `.md`。
2. 检查标题层级、段落、代码块和图片链接。
3. 运行脚本生成 `.wechat.html`。
4. 在浏览器中打开 `.wechat.html`。
5. 选中文章正文区域并复制。
6. 粘贴到微信公众号后台编辑器中进行最终预览。

## 目录结构

```text
wechat-article-export/
  SKILL.md
  README.md
  scripts/
    markdown_to_wechat.py
```

## 注意事项

- 微信公众号后台会二次处理部分 HTML 和 CSS，最终效果应以后台预览为准。
- 该工具主要服务文章富文本转换，不负责自动登录、自动发布或后台接口操作。
- 复杂交互、脚本、外链样式表通常不适合公众号富文本环境。
- 发布前请检查图片授权、外链可访问性和代码片段长度。

## License

如需开源发布，请在仓库中补充明确的许可证文件。
