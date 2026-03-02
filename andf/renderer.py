"""
ANDFRenderer — converts ANDFDocument to a self-contained .andf (HTML) file.
"""
from __future__ import annotations

import html
import json
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .document import ANDFDocument


# ─────────────────────────────────────────────
# Height estimations (px) for page layout
# ─────────────────────────────────────────────

PAGE_HEIGHT_PX = 900  # usable content height per A4 page

BLOCK_HEIGHTS = {
    "heading": lambda b: [80, 70, 60, 55, 50, 45][min(b.get("level", 1) - 1, 5)],
    "paragraph": lambda b: max(40, len(b.get("text", "")) // 80 * 20 + 20),
    "image": lambda b: 280,
    "table": lambda b: 40 + 28 * len(b.get("rows", [])),
    "list": lambda b: 20 + 22 * len(b.get("items", [])),
    "code": lambda b: 40 + 18 * max(1, b.get("code", "").count("\n") + 1),
    "quote": lambda b: max(60, len(b.get("text", "")) // 70 * 22 + 40),
    "callout": lambda b: max(70, len(b.get("text", "")) // 70 * 20 + 50),
    "separator": lambda b: 30,
    "pagebreak": lambda b: PAGE_HEIGHT_PX,  # forces new page
}


def estimate_height(block: dict) -> int:
    btype = block.get("type", "paragraph")
    fn = BLOCK_HEIGHTS.get(btype)
    return fn(block) if fn else 40


# ─────────────────────────────────────────────
# Inline markup → HTML
# ─────────────────────────────────────────────

def inline(text: str) -> str:
    """Convert simple markdown-like inline markup to HTML."""
    t = html.escape(text)
    # Bold
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    # Italic
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    # Inline code
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    # References [label]
    t = re.sub(r'\[([^\]]+)\]', r'<sup class="ref">[\1]</sup>', t)
    return t


# ─────────────────────────────────────────────
# Block renderers
# ─────────────────────────────────────────────

def render_heading(block: dict) -> str:
    level = block.get("level", 1)
    text = block.get("text", "")
    tag = f"h{min(max(level, 1), 6)}"
    return f'<{tag} class="andf-h andf-h{level}">{inline(text)}</{tag}>'


def render_paragraph(block: dict) -> str:
    text = block.get("text", "")
    return f'<p class="andf-p">{inline(text)}</p>'


def render_image(block: dict, assets: dict) -> str:
    asset_id = block.get("asset_id", "")
    alt = html.escape(block.get("alt", ""))
    caption = block.get("caption", "")
    width = block.get("width", "100%")
    align = block.get("align", "center")
    asset = assets.get(asset_id)
    parts = [f'<figure class="andf-figure andf-align-{align}">']
    if asset:
        mime = asset.get("mime_type", "image/png")
        data = asset.get("data", "")
        parts.append(f'<img src="data:{mime};base64,{data}" alt="{alt}" style="max-width:{width}">')
    else:
        parts.append(f'<div class="andf-image-placeholder">[Image: {alt}]</div>')
    if caption:
        parts.append(f'<figcaption>{inline(caption)}</figcaption>')
    parts.append('</figure>')
    return "\n".join(parts)


def render_table(block: dict) -> str:
    caption = block.get("caption", "")
    headers = block.get("headers", [])
    rows = block.get("rows", [])
    aligns = block.get("align", [])
    parts = ['<figure class="andf-table-wrap">']
    if caption:
        parts.append(f'<figcaption class="andf-table-caption">{inline(caption)}</figcaption>')
    parts.append('<table class="andf-table"><thead><tr>')
    for i, h in enumerate(headers):
        a = aligns[i] if i < len(aligns) else "left"
        parts.append(f'<th style="text-align:{a}">{inline(str(h))}</th>')
    parts.append('</tr></thead><tbody>')
    for row in rows:
        parts.append('<tr>')
        for i, cell in enumerate(row):
            a = aligns[i] if i < len(aligns) else "left"
            parts.append(f'<td style="text-align:{a}">{inline(str(cell))}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table></figure>')
    return "\n".join(parts)


def render_list(block: dict) -> str:
    ordered = block.get("ordered", False)
    items = block.get("items", [])
    tag = "ol" if ordered else "ul"
    parts = [f'<{tag} class="andf-list">']
    for item in items:
        level = item.get("level", 0)
        text = item.get("text", "")
        indent = level * 20
        parts.append(f'<li style="margin-left:{indent}px">{inline(text)}</li>')
    parts.append(f'</{tag}>')
    return "\n".join(parts)


def render_code(block: dict) -> str:
    language = block.get("language", "text")
    code = block.get("code", "")
    caption = block.get("caption", "")
    line_numbers = block.get("line_numbers", False)
    escaped = html.escape(code)
    ln_class = " line-numbers" if line_numbers else ""
    parts = ['<figure class="andf-code-wrap">']
    if caption:
        parts.append(f'<figcaption class="andf-code-caption">{html.escape(caption)}</figcaption>')
    parts.append(f'<pre class="andf-pre language-{language}{ln_class}"><code class="language-{language}">{escaped}</code></pre>')
    parts.append('</figure>')
    return "\n".join(parts)


def render_quote(block: dict) -> str:
    text = block.get("text", "")
    attribution = block.get("attribution", "")
    parts = ['<blockquote class="andf-quote">']
    parts.append(f'<p>{inline(text)}</p>')
    if attribution:
        parts.append(f'<cite>— {html.escape(attribution)}</cite>')
    parts.append('</blockquote>')
    return "\n".join(parts)


CALLOUT_ICONS = {
    "info": "ℹ",
    "warning": "⚠",
    "error": "✖",
    "success": "✔",
    "tip": "💡",
}


def render_callout(block: dict) -> str:
    variant = block.get("variant", "info")
    title = block.get("title", "")
    text = block.get("text", "")
    icon = CALLOUT_ICONS.get(variant, "ℹ")
    title_html = f'<div class="andf-callout-title">{icon} {html.escape(title)}</div>' if title else f'<div class="andf-callout-icon">{icon}</div>'
    return f'<div class="andf-callout andf-callout-{variant}">{title_html}<p>{inline(text)}</p></div>'


def render_separator(_block: dict) -> str:
    return '<hr class="andf-hr">'


def render_block(block: dict, assets: dict) -> str:
    btype = block.get("type", "paragraph")
    dispatch = {
        "heading": lambda: render_heading(block),
        "paragraph": lambda: render_paragraph(block),
        "image": lambda: render_image(block, assets),
        "table": lambda: render_table(block),
        "list": lambda: render_list(block),
        "code": lambda: render_code(block),
        "quote": lambda: render_quote(block),
        "callout": lambda: render_callout(block),
        "separator": lambda: render_separator(block),
        "pagebreak": lambda: "",  # handled at page level
    }
    fn = dispatch.get(btype, lambda: f'<p>[unknown block type: {btype}]</p>')
    return fn()


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

def build_css(theme: dict) -> str:
    c = theme.get("colors", {})
    font_body = theme.get("font_body", "Inter, sans-serif")
    font_heading = theme.get("font_heading", "Inter, sans-serif")
    font_mono = theme.get("font_mono", "JetBrains Mono, monospace")
    font_size = theme.get("font_size", 11)
    line_height = theme.get("line_height", 1.6)

    return f"""
/* ─── Reset ─── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: {font_body};
  font-size: {font_size}pt;
  line-height: {line_height};
  color: {c.get("text", "#1a1a1a")};
  background: #525659;
  min-height: 100vh;
}}

/* ─── Toolbar ─── */
#andf-toolbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 48px;
  background: #3c4043;
  color: #e0e0e0;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  z-index: 1000;
  box-shadow: 0 2px 6px rgba(0,0,0,.5);
  font-family: system-ui, sans-serif;
  font-size: 13px;
}}
#andf-toolbar button {{
  background: none;
  border: none;
  color: #e0e0e0;
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background .15s;
}}
#andf-toolbar button:hover {{ background: rgba(255,255,255,.1); }}
#andf-title {{ flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
#andf-page-info {{ white-space: nowrap; font-size: 13px; color: #bbb; }}
#andf-zoom-select {{
  background: #5a5f63;
  border: none;
  color: #e0e0e0;
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 12px;
  cursor: pointer;
}}
#andf-toc-btn {{ font-size: 18px !important; }}

/* ─── TOC sidebar ─── */
#andf-toc {{
  position: fixed;
  top: 48px; left: 0; bottom: 0;
  width: 260px;
  background: #2d2d2d;
  color: #ddd;
  overflow-y: auto;
  transform: translateX(-100%);
  transition: transform .25s;
  z-index: 900;
  padding: 16px;
  font-family: system-ui, sans-serif;
  font-size: 13px;
}}
#andf-toc.open {{ transform: translateX(0); }}
#andf-toc h3 {{ color: #fff; margin-bottom: 12px; font-size: 14px; }}
#andf-toc a {{
  display: block;
  color: #aaa;
  text-decoration: none;
  padding: 4px 0;
  border-left: 2px solid transparent;
  padding-left: 8px;
  margin-bottom: 2px;
}}
#andf-toc a:hover {{ color: #fff; border-left-color: #4a9eff; }}

/* ─── Viewer ─── */
#andf-viewer {{
  padding-top: 68px;
  padding-bottom: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}}

/* ─── Pages ─── */
.andf-page {{
  background: #fff;
  width: 210mm;
  min-height: 297mm;
  padding: 25mm;
  box-shadow: 0 4px 20px rgba(0,0,0,.4);
  position: relative;
  page-break-after: always;
}}

/* ─── Page number ─── */
.andf-page-num {{
  position: absolute;
  bottom: 12mm;
  left: 0; right: 0;
  text-align: center;
  font-size: 9pt;
  color: #999;
}}

/* ─── Content ─── */
.andf-h {{ font-family: {font_heading}; color: {c.get("heading", "#111")}; margin: .6em 0 .3em; }}
.andf-h1 {{ font-size: 2em; font-weight: 700; margin-top: 0; border-bottom: 2px solid {c.get("border", "#e5e7eb")}; padding-bottom: .3em; }}
.andf-h2 {{ font-size: 1.5em; font-weight: 700; }}
.andf-h3 {{ font-size: 1.2em; font-weight: 600; }}
.andf-h4 {{ font-size: 1.05em; font-weight: 600; }}
.andf-h5 {{ font-size: 1em; font-weight: 600; }}
.andf-h6 {{ font-size: .95em; font-weight: 600; color: {c.get("muted", "#6b7280")}; }}

.andf-p {{ margin: .5em 0; text-align: justify; }}

.andf-figure {{ margin: 1em 0; }}
.andf-align-center {{ text-align: center; }}
.andf-align-left {{ text-align: left; }}
.andf-align-right {{ text-align: right; }}
.andf-figure img {{ max-width: 100%; height: auto; border-radius: 4px; }}
.andf-image-placeholder {{
  background: {c.get("code_bg", "#f8f8f8")};
  border: 1px dashed {c.get("border", "#e5e7eb")};
  padding: 40px;
  text-align: center;
  color: {c.get("muted", "#6b7280")};
  border-radius: 4px;
}}
figcaption {{ font-size: .85em; color: {c.get("muted", "#6b7280")}; margin-top: .4em; text-align: center; }}

.andf-table-wrap {{ margin: 1em 0; overflow-x: auto; }}
.andf-table-caption {{ font-size: .9em; color: {c.get("muted", "#6b7280")}; margin-bottom: .4em; font-style: italic; }}
.andf-table {{ width: 100%; border-collapse: collapse; font-size: .9em; }}
.andf-table th {{
  background: {c.get("code_bg", "#f8f8f8")};
  font-weight: 600;
  padding: 8px 12px;
  border: 1px solid {c.get("border", "#e5e7eb")};
  text-align: left;
}}
.andf-table td {{
  padding: 7px 12px;
  border: 1px solid {c.get("border", "#e5e7eb")};
  vertical-align: top;
}}
.andf-table tr:nth-child(even) td {{ background: {c.get("code_bg", "#f8f8f8")}; }}

.andf-list {{ margin: .5em 0 .5em 1.5em; }}
.andf-list li {{ margin: .25em 0; }}

.andf-code-wrap {{ margin: 1em 0; }}
.andf-code-caption {{ font-size: .85em; color: {c.get("muted", "#6b7280")}; margin-bottom: .25em; font-family: {font_mono}; }}
.andf-pre {{
  background: {c.get("code_bg", "#f8f8f8")};
  border: 1px solid {c.get("code_border", "#e1e4e8")};
  border-radius: 6px;
  padding: 14px 16px;
  overflow-x: auto;
  font-family: {font_mono};
  font-size: 9pt;
  line-height: 1.5;
  white-space: pre;
}}
.andf-pre code {{ background: none; border: none; padding: 0; }}

.andf-quote {{
  border-left: 4px solid {c.get("link", "#1a73e8")};
  margin: 1em 0;
  padding: .5em 1em;
  color: {c.get("muted", "#6b7280")};
  font-style: italic;
}}
.andf-quote p {{ margin: 0 0 .3em; }}
.andf-quote cite {{ font-size: .9em; font-style: normal; }}

.andf-callout {{
  border-radius: 6px;
  padding: 12px 16px;
  margin: 1em 0;
  border-left: 4px solid;
}}
.andf-callout-info    {{ background: {c.get("callout_info",    "#eff6ff")}; border-color: #3b82f6; }}
.andf-callout-warning {{ background: {c.get("callout_warning", "#fffbeb")}; border-color: #f59e0b; }}
.andf-callout-error   {{ background: {c.get("callout_error",   "#fef2f2")}; border-color: #ef4444; }}
.andf-callout-success {{ background: {c.get("callout_success", "#f0fdf4")}; border-color: #22c55e; }}
.andf-callout-tip     {{ background: {c.get("callout_tip",     "#f5f3ff")}; border-color: #8b5cf6; }}
.andf-callout-title {{
  font-weight: 700;
  margin-bottom: .4em;
  font-size: 1em;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.andf-callout-icon {{ float: left; margin-right: 6px; }}
.andf-callout p {{ margin: 0; }}

.andf-hr {{ border: none; border-top: 1px solid {c.get("border", "#e5e7eb")}; margin: 1.2em 0; }}

code {{ font-family: {font_mono}; background: {c.get("code_bg", "#f8f8f8")}; padding: 1px 4px; border-radius: 3px; font-size: .9em; }}
sup.ref {{ font-size: .75em; color: {c.get("link", "#1a73e8")}; }}

/* ─── Cover page ─── */
.andf-cover {{ padding-top: 30mm; text-align: center; }}
.andf-cover .andf-h1 {{ font-size: 2.4em; border: none; margin-bottom: .2em; }}
.andf-cover-subtitle {{ font-size: 1.2em; color: {c.get("muted", "#6b7280")}; margin-bottom: 2em; }}
.andf-cover-authors {{ font-size: 1em; color: {c.get("text", "#1a1a1a")}; margin-bottom: .5em; }}
.andf-cover-date {{ font-size: .9em; color: {c.get("muted", "#6b7280")}; }}
.andf-cover-divider {{ margin: 2em auto; width: 80px; height: 3px; background: {c.get("link", "#1a73e8")}; border: none; }}

/* ─── Print ─── */
@media print {{
  #andf-toolbar, #andf-toc {{ display: none !important; }}
  #andf-viewer {{ padding-top: 0; background: white; }}
  .andf-page {{ box-shadow: none; margin: 0; }}
}}

/* ─── Responsive ─── */
@media (max-width: 800px) {{
  .andf-page {{ width: 100%; min-height: auto; padding: 15mm 8mm; }}
  #andf-viewer {{ padding-top: 58px; gap: 12px; }}
}}
""".strip()


# ─────────────────────────────────────────────
# JavaScript
# ─────────────────────────────────────────────

VIEWER_JS = r"""
(function() {
  var pages = document.querySelectorAll('.andf-page');
  var totalPages = pages.length;
  var currentPage = 1;
  var zoom = 100;

  var pageInfoEl = document.getElementById('andf-page-info');
  var zoomSelect = document.getElementById('andf-zoom-select');
  var viewer = document.getElementById('andf-viewer');

  function updatePageInfo() {
    if (pageInfoEl) pageInfoEl.textContent = 'Page ' + currentPage + ' / ' + totalPages;
  }

  function scrollToPage(n) {
    n = Math.max(1, Math.min(n, totalPages));
    currentPage = n;
    pages[n - 1].scrollIntoView({ behavior: 'smooth', block: 'start' });
    updatePageInfo();
  }

  function applyZoom(z) {
    zoom = Math.max(50, Math.min(200, z));
    viewer.style.transform = 'scale(' + zoom / 100 + ')';
    viewer.style.transformOrigin = 'top center';
    viewer.style.marginBottom = (zoom > 100 ? (zoom - 100) * 2.97 + 'mm' : '0');
    if (zoomSelect) zoomSelect.value = zoom;
  }

  // Intersection observer to track current page
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var idx = Array.prototype.indexOf.call(pages, entry.target);
        if (idx >= 0) { currentPage = idx + 1; updatePageInfo(); }
      }
    });
  }, { threshold: 0.3 });
  pages.forEach(function(p) { observer.observe(p); });

  // Toolbar button wiring
  var prevBtn = document.getElementById('andf-prev');
  var nextBtn = document.getElementById('andf-next');
  var zoomInBtn = document.getElementById('andf-zoom-in');
  var zoomOutBtn = document.getElementById('andf-zoom-out');
  var downloadBtn = document.getElementById('andf-download');
  var tocBtn = document.getElementById('andf-toc-btn');
  var toc = document.getElementById('andf-toc');

  if (prevBtn) prevBtn.onclick = function() { scrollToPage(currentPage - 1); };
  if (nextBtn) nextBtn.onclick = function() { scrollToPage(currentPage + 1); };
  if (zoomInBtn) zoomInBtn.onclick = function() { applyZoom(zoom + 10); };
  if (zoomOutBtn) zoomOutBtn.onclick = function() { applyZoom(zoom - 10); };
  if (zoomSelect) zoomSelect.onchange = function() { applyZoom(parseInt(this.value)); };

  if (downloadBtn) {
    downloadBtn.onclick = function() {
      var a = document.createElement('a');
      a.href = window.location.href;
      a.download = document.title + '.andf';
      a.click();
    };
  }

  if (tocBtn && toc) {
    tocBtn.onclick = function() { toc.classList.toggle('open'); };
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') scrollToPage(currentPage + 1);
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') scrollToPage(currentPage - 1);
    if (e.key === '+' || (e.key === '=' && e.ctrlKey)) { e.preventDefault(); applyZoom(zoom + 10); }
    if (e.key === '-' && e.ctrlKey) { e.preventDefault(); applyZoom(zoom - 10); }
    if (e.key === '0' && e.ctrlKey) { e.preventDefault(); applyZoom(100); }
  });

  updatePageInfo();
})();
"""


# ─────────────────────────────────────────────
# Main renderer
# ─────────────────────────────────────────────

class ANDFRenderer:
    def __init__(self, doc: "ANDFDocument"):
        self.doc = doc
        self.data = doc.to_dict()

    def render(self) -> str:
        data = self.data
        meta = data["metadata"]
        theme = data["theme"]
        assets = data.get("assets", {})

        title = html.escape(meta.get("title", "Untitled"))
        css = build_css(theme)
        json_data = json.dumps(data, ensure_ascii=False)
        # Escape </script> inside JSON
        json_data = json_data.replace("</script>", "<\\/script>")

        pages_html = self._build_pages(assets)
        toc_html = self._build_toc()

        authors_str = ", ".join(meta.get("authors", []))
        subtitle_str = html.escape(meta.get("subtitle", ""))
        created_str = meta.get("created", "")[:10]

        return f"""<!DOCTYPE html>
<html lang="{meta.get("language", "en")}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="andf-version" content="1.0">
<meta name="generator" content="ANDF Python Library">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet">
<script type="application/andf+json">{json_data}</script>
<style>
{css}
</style>
</head>
<body>

<!-- Toolbar -->
<div id="andf-toolbar">
  <button id="andf-toc-btn" title="Table of Contents">≡</button>
  <span id="andf-title">{title}</span>
  <button id="andf-prev" title="Previous page">&#8592;</button>
  <span id="andf-page-info">Page 1 / 1</span>
  <button id="andf-next" title="Next page">&#8594;</button>
  <button id="andf-zoom-out" title="Zoom out">&#8722;</button>
  <select id="andf-zoom-select" title="Zoom">
    <option value="50">50%</option>
    <option value="75">75%</option>
    <option value="100" selected>100%</option>
    <option value="125">125%</option>
    <option value="150">150%</option>
    <option value="175">175%</option>
    <option value="200">200%</option>
  </select>
  <button id="andf-zoom-in" title="Zoom in">&#43;</button>
  <button id="andf-download" title="Save file">&#8595;</button>
</div>

<!-- TOC Sidebar -->
<div id="andf-toc">
  <h3>Contents</h3>
{toc_html}
</div>

<!-- Viewer -->
<div id="andf-viewer">
{pages_html}
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
<script>
{VIEWER_JS}
</script>
</body>
</html>"""

    # ── Page layout ──

    def _build_pages(self, assets: dict) -> str:
        data = self.data
        meta = data["metadata"]
        blocks_dict = data.get("blocks", {})
        sections = data.get("sections", [])

        # Collect cover content
        cover_blocks = self._cover_html(meta)

        # Collect all block IDs in document order
        all_block_ids = self._collect_block_ids(sections)

        # Distribute blocks across pages
        pages: list[list] = []

        # Page 1: cover + first content blocks
        current_page: list = list(cover_blocks)  # list of raw HTML strings
        current_height = 200  # approximate cover height

        for block_id in all_block_ids:
            block = blocks_dict.get(block_id, {})
            btype = block.get("type", "paragraph")

            if btype == "pagebreak":
                pages.append(current_page)
                current_page = []
                current_height = 0
                continue

            h = estimate_height(block)
            if current_height + h > PAGE_HEIGHT_PX and current_height > 0:
                pages.append(current_page)
                current_page = []
                current_height = 0

            html_str = render_block(block, assets)
            current_page.append(html_str)
            current_height += h

        if current_page or not pages:
            pages.append(current_page)

        # Build page HTML
        total = len(pages)
        parts = []
        for i, page_blocks in enumerate(pages, 1):
            inner = "\n".join(page_blocks)
            parts.append(
                f'<div class="andf-page" id="page-{i}">\n{inner}\n'
                f'<div class="andf-page-num">{i}</div>\n</div>'
            )
        return "\n\n".join(parts)

    def _cover_html(self, meta: dict) -> list[str]:
        parts = ['<div class="andf-cover">']
        title = html.escape(meta.get("title", "Untitled"))
        parts.append(f'<h1 class="andf-h andf-h1">{title}</h1>')
        subtitle = meta.get("subtitle", "")
        if subtitle:
            parts.append(f'<p class="andf-cover-subtitle">{html.escape(subtitle)}</p>')
        authors = meta.get("authors", [])
        if authors:
            parts.append(f'<p class="andf-cover-authors">{html.escape(", ".join(authors))}</p>')
        created = meta.get("created", "")[:10]
        if created:
            parts.append(f'<p class="andf-cover-date">{html.escape(created)}</p>')
        parts.append('<hr class="andf-cover-divider">')
        parts.append('</div>')
        return parts

    def _collect_block_ids(self, sections: list[dict]) -> list[str]:
        ids = []
        for sec in sections:
            ids.extend(sec.get("blocks", []))
            ids.extend(self._collect_block_ids(sec.get("subsections", [])))
        return ids

    def _build_toc(self) -> str:
        sections = self.data.get("sections", [])
        lines = []
        for sec in sections:
            title = html.escape(sec.get("title", ""))
            sid = sec.get("id", "")
            lines.append(f'<a href="#sec-{sid}">{title}</a>')
            for sub in sec.get("subsections", []):
                st = html.escape(sub.get("title", ""))
                ssid = sub.get("id", "")
                lines.append(f'<a href="#sec-{ssid}" style="padding-left:20px;font-size:.9em">&nbsp;{st}</a>')
        return "\n".join(lines)
