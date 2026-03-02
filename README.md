# ANDF — AI Native Document Format

**ANDF** (`.andf`) is a document format built for AI-native workflows. Every `.andf` file is a self-contained HTML file that:

- **Opens in any browser instantly** — looks and feels like a PDF (toolbar, dark background, white pages, page numbers)
- **Is trivially parseable by AI** — structured JSON is embedded in a `<script type="application/andf+json">` tag
- **Requires no install, no server, no extension**

---

## Quick Start

```python
from andf import ANDFDocument

doc = ANDFDocument()
doc.set_metadata(title="My Report", authors=["Alice"])

sec = doc.add_section("intro", "Introduction")
sec.heading("Welcome", level=2)
sec.paragraph("Hello from **ANDF**! This is *important*.")
sec.callout("Remember to save your work!", variant="tip", title="Tip")
sec.table(
    headers=["Name", "Score"],
    rows=[["Alice", "95"], ["Bob", "87"]],
    caption="Table 1: Results",
)
sec.code("print('hello world')", language="python")

doc.save("report.andf")
doc.open_in_browser("report.andf")  # opens in browser
```

---

## Installation

```bash
pip install andf
```

For development (after cloning the repo):

```bash
pip install -e .
```

---

## CLI

```bash
# Create a blank document
andf new output.andf

# Open in browser
andf open output.andf

# Extract embedded JSON
andf parse output.andf --pretty

# Validate format
andf validate output.andf

# Show metadata
andf info output.andf

# AI layer summary
andf ai output.andf
```

---

## File Format

An `.andf` file is an HTML file. The complete document data is embedded as JSON:

```html
<script type="application/andf+json">
{
  "andf_version": "1.0",
  "document_id": "...",
  "metadata": { "title": "...", "authors": [...] },
  "sections": [...],
  "blocks": { "blk_xxx": { "type": "paragraph", "text": "..." } },
  ...
}
</script>
```

AI tools extract it with a single regex:

```python
import re, json

pattern = re.compile(
    r'<script[^>]+type=["\']application/andf\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL
)
data = json.loads(pattern.search(open("file.andf").read()).group(1))
```

---

## Block Types

| Type | Description |
|------|-------------|
| `heading` | Section heading (levels 1–6) |
| `paragraph` | Body text with `**bold**`, `*italic*`, `` `code` ``, `[ref]` markup |
| `image` | Embedded image from assets |
| `table` | Data table with headers and rows |
| `list` | Ordered or unordered list with nesting |
| `code` | Syntax-highlighted code block |
| `quote` | Block quote with optional attribution |
| `callout` | Highlighted box: info / warning / error / success / tip |
| `separator` | Horizontal rule |
| `pagebreak` | Explicit page break |

---

## Themes

```python
doc.set_theme("default")    # Inter sans-serif, clean
doc.set_theme("academic")   # Georgia serif, formal
doc.set_theme("corporate")  # Arial, business blue headings
doc.set_theme("minimal")    # System UI, minimal color
```

---

## AI Layer

```python
from andf import ANDFDocument, ANDFAILayer

doc = ANDFDocument.from_file("report.andf")
layer = ANDFAILayer(doc)

# Plain text
text = layer.full_text()

# Markdown (best for LLM input)
md = layer.to_markdown()

# RAG chunks
chunks = layer.context_chunks(max_chars=4000)

# Document summary
summary = layer.document_summary()
print(summary["key_points"])

# High-importance blocks
important = layer.blocks_by_importance(min_importance=4)
```

---

## Project Structure

```
andf/
├── __init__.py     # Public API
├── document.py     # ANDFDocument model + fluent builder
├── renderer.py     # HTML renderer
├── parser.py       # Parser + validator
├── ai_layer.py     # AI extraction layer
└── cli.py          # Command-line interface

spec/
└── ANDF-1.0.md     # Format specification

examples/
├── create_examples.py
├── research_paper.andf
├── business_report.andf
├── legal_contract.andf
└── technical_manual.andf

tests/
└── test_andf.py
```

---

## Generate Examples

```bash
python examples/create_examples.py
```

Opens each `.andf` file in your browser to see the viewer.

---

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## Specification

See [`spec/ANDF-1.0.md`](spec/ANDF-1.0.md) for the complete format specification.

---

## License

Apache 2.0
