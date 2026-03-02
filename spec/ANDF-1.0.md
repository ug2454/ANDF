# ANDF 1.0 — AI Native Document Format Specification

**Version:** 1.0
**Date:** 2026-03-02
**Status:** Draft

---

## 1. Overview

ANDF (AI Native Document Format) is a file format for structured documents that:

1. Opens directly in any web browser, rendering a PDF-like viewer — no installation required.
2. Embeds structured JSON data that AI tools can extract with zero preprocessing.
3. Is generated and consumed by a pure-Python library.

An `.andf` file is a **self-contained HTML file** with:
- An HTML shell rendering the PDF-like view (toolbar, white pages, dark background).
- Inline CSS and JavaScript.
- A `<script type="application/andf+json">` tag in `<head>` containing the complete document data as JSON.

---

## 2. File Format

### 2.1 MIME Type

```
application/andf+html
```

### 2.2 File Extension

`.andf`

### 2.3 Encoding

UTF-8 (required).

### 2.4 Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="andf-version" content="1.0">
  <script type="application/andf+json">
    { ...JSON document data... }
  </script>
  <!-- inline CSS, Google Fonts -->
</head>
<body>
  <!-- toolbar, TOC sidebar, rendered pages -->
  <!-- Prism.js for syntax highlighting -->
  <!-- inline viewer JS -->
</body>
</html>
```

### 2.5 JSON Escaping

Inside the `<script>` tag the sequence `</script>` must be escaped as `<\/script>` to avoid premature script termination.

---

## 3. JSON Schema

### 3.1 Top-Level Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `andf_version` | string | Yes | Must be `"1.0"` |
| `document_id` | string (UUID) | Yes | Unique document identifier |
| `metadata` | object | Yes | Document metadata |
| `layout` | object | Yes | Page layout settings |
| `theme` | object | Yes | Visual theme |
| `sections` | array | Yes | Ordered list of top-level sections |
| `blocks` | object | Yes | Map of block_id → block object |
| `assets` | object | No | Map of asset_id → asset object |
| `references` | array | No | List of reference objects |
| `ai` | object | No | AI metadata |

### 3.2 Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title (required) |
| `subtitle` | string | Optional subtitle |
| `authors` | string[] | List of author names |
| `created` | string (ISO 8601) | Creation timestamp |
| `modified` | string (ISO 8601) | Last modified timestamp |
| `keywords` | string[] | Keyword tags |
| `language` | string (BCP 47) | Document language, e.g. `"en"` |
| `category` | string | Document category |
| `status` | string | `draft`, `review`, `final`, `published` |
| `version` | string | Document version string |
| `license` | string | License identifier (e.g. `"CC BY 4.0"`) |

### 3.3 Layout Object

| Field | Type | Description |
|-------|------|-------------|
| `page_size` | string | `"A4"`, `"Letter"`, `"A3"` |
| `orientation` | string | `"portrait"` or `"landscape"` |
| `margins` | object | `{ top, bottom, left, right }` in mm |
| `columns` | integer | Number of text columns (1 or 2) |
| `header` | string\|null | Header template or null |
| `footer` | string\|null | Footer template: `"page_number"` or null |

### 3.4 Theme Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Preset name: `default`, `academic`, `corporate`, `minimal` |
| `font_body` | string | CSS font-family for body text |
| `font_heading` | string | CSS font-family for headings |
| `font_mono` | string | CSS font-family for code |
| `font_size` | number | Base font size in pt |
| `line_height` | number | CSS line-height multiplier |
| `colors` | object | Color palette (see §3.4.1) |

#### 3.4.1 Colors Object

Keys: `text`, `heading`, `link`, `muted`, `border`, `callout_info`, `callout_warning`, `callout_error`, `callout_success`, `callout_tip`, `code_bg`, `code_border`.

### 3.5 Section Object

```json
{
  "id": "section-id",
  "title": "Section Title",
  "role": "body",
  "blocks": ["blk_abc123", "blk_def456"],
  "subsections": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique within document |
| `title` | string | Display title |
| `role` | string | `abstract`, `introduction`, `body`, `conclusion`, `appendix`, `references` |
| `blocks` | string[] | Ordered block IDs belonging to this section |
| `subsections` | Section[] | Nested sections |

### 3.6 Block Types

All blocks share:
- `type` (string, required)
- `semantic` (object, optional) — see §3.7

#### `heading`
```json
{ "type": "heading", "level": 2, "text": "Section Title" }
```

#### `paragraph`
```json
{ "type": "paragraph", "text": "Body text with **bold** and *italic*." }
```

Inline markup: `**bold**`, `*italic*`, `` `code` ``, `[ref-label]`.

#### `image`
```json
{
  "type": "image",
  "asset_id": "asset_abc123",
  "alt": "Description",
  "caption": "Figure 1: ...",
  "width": "80%",
  "align": "center"
}
```

#### `table`
```json
{
  "type": "table",
  "caption": "Table 1: ...",
  "headers": ["Col A", "Col B"],
  "rows": [["val1", "val2"]],
  "align": ["left", "right"]
}
```

#### `list`
```json
{
  "type": "list",
  "ordered": false,
  "items": [
    { "text": "First item", "level": 0 },
    { "text": "Sub-item", "level": 1 }
  ]
}
```

#### `code`
```json
{
  "type": "code",
  "language": "python",
  "code": "print('hello')",
  "caption": "Example",
  "line_numbers": false
}
```

#### `quote`
```json
{
  "type": "quote",
  "text": "To be or not to be.",
  "attribution": "Shakespeare",
  "style": "blockquote"
}
```

#### `callout`
```json
{
  "type": "callout",
  "variant": "info",
  "title": "Note",
  "text": "This is important."
}
```
Variants: `info`, `warning`, `error`, `success`, `tip`.

#### `separator`
```json
{ "type": "separator" }
```

#### `pagebreak`
```json
{ "type": "pagebreak" }
```

### 3.7 Semantic Annotation Object

Optional on any block:

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Semantic role: `definition`, `result`, `method`, `claim`, ... |
| `context` | string | Free-text context hint for AI |
| `importance` | integer (1–5) | Importance score for filtering |
| `entities` | string[] | Named entities in this block |
| `summary` | string | One-sentence summary of this block |

### 3.8 Asset Object

```json
{
  "type": "image",
  "name": "figure1.png",
  "mime_type": "image/png",
  "encoding": "base64",
  "data": "<base64-encoded data>"
}
```

### 3.9 Reference Object

```json
{
  "id": "ref_abc123",
  "type": "article",
  "label": "Smith2024",
  "title": "Paper Title",
  "authors": ["Smith, J.", "Doe, A."],
  "year": 2024,
  "doi": "10.1234/example",
  "url": "https://example.com"
}
```

Types: `article`, `book`, `conference`, `report`, `thesis`, `website`, `other`.

### 3.10 AI Object

```json
{
  "summary": "One-paragraph document summary.",
  "key_points": ["Point 1", "Point 2"],
  "topics": [{ "label": "Machine Learning", "confidence": 0.95 }],
  "reading_time_minutes": 5,
  "complexity": "medium",
  "questions_answered": ["What is X?"],
  "entities": {
    "people": [],
    "organizations": [],
    "technologies": [],
    "concepts": []
  }
}
```

Complexity: `low`, `medium`, `high`, `expert`.

---

## 4. AI Extraction

### 4.1 Locating the JSON

```python
import re, json
pattern = re.compile(
    r'<script[^>]+type=["\']application/andf\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE
)
match = pattern.search(html_content)
data = json.loads(match.group(1))
```

### 4.2 Recommended Extraction Flow

1. Extract JSON from `<script type="application/andf+json">`.
2. Read `data["ai"]["summary"]` for a quick overview.
3. Walk `data["sections"]` in order, following `blocks` IDs into `data["blocks"]`.
4. Use `data["blocks"][id]["semantic"]["importance"]` to filter high-value content.
5. Use `data["references"]` for citation data.

---

## 5. Browser Viewer Behaviour

| Feature | Behaviour |
|---------|-----------|
| Page layout | White `210mm × 297mm` pages with `box-shadow`, on `#525659` background |
| Toolbar | Fixed at top: TOC toggle, filename, page counter, zoom select, download |
| TOC sidebar | Slides in from left; lists all sections and subsections |
| Zoom | 50%–200% via dropdown or `+`/`-` buttons |
| Keyboard | `←`/`→` page navigation; `Ctrl +`/`-`/`0` zoom |
| Print | CSS `@media print` hides toolbar; prints clean pages |
| Fonts | Inter (body/headings) and JetBrains Mono (code) via Google Fonts CDN |
| Syntax highlight | Prism.js autoloader via CDN |

---

## 6. Versioning

The `andf_version` field in the JSON and the `<meta name="andf-version">` tag both identify the format version. Parsers MUST reject documents with unsupported versions or display a compatibility warning.

---

## 7. Security Considerations

- `.andf` files execute JavaScript in the browser — treat untrusted files with the same caution as arbitrary HTML.
- Base64-encoded assets are embedded inline; large assets may produce very large files.
- The JSON data is not signed or encrypted; do not rely on it for authenticity.

---

## 8. Example Minimal Document

```json
{
  "andf_version": "1.0",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata": {
    "title": "Hello ANDF",
    "authors": ["Alice"],
    "created": "2026-03-02T00:00:00Z",
    "modified": "2026-03-02T00:00:00Z",
    "language": "en",
    "status": "draft",
    "version": "1.0"
  },
  "layout": {
    "page_size": "A4",
    "orientation": "portrait",
    "margins": { "top": 25, "bottom": 25, "left": 25, "right": 25 },
    "columns": 1,
    "header": null,
    "footer": "page_number"
  },
  "theme": { "name": "default" },
  "sections": [
    {
      "id": "intro",
      "title": "Introduction",
      "role": "body",
      "blocks": ["blk_001"],
      "subsections": []
    }
  ],
  "blocks": {
    "blk_001": {
      "type": "paragraph",
      "text": "Hello from **ANDF**!"
    }
  },
  "assets": {},
  "references": [],
  "ai": {}
}
```
