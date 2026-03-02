"""
Tests for the ANDF library.
Run with: python -m pytest tests/
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from andf import ANDFDocument, ANDFParser, ANDFAILayer


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def simple_doc():
    doc = ANDFDocument()
    doc.set_metadata(
        title="Test Document",
        authors=["Alice", "Bob"],
        keywords=["test", "andf"],
        category="Testing",
        status="draft",
    )
    sec = doc.add_section("intro", "Introduction", role="introduction")
    sec.heading("Welcome", level=2)
    sec.paragraph("Hello **world**! This is a *test* document.")
    sec.list(["Item one", "Item two", {"text": "Sub-item", "level": 1}])
    sec.code("print('hello')", language="python", caption="Example")
    sec.callout("This is a callout.", variant="info", title="Note")
    sec.separator()
    return doc


@pytest.fixture
def rich_doc(simple_doc):
    simple_doc.add_reference(
        ref_type="article",
        label="Test2024",
        title="Test Paper",
        authors=["Test Author"],
        year=2024,
    )
    simple_doc.set_ai(
        summary="A test document.",
        key_points=["Point one", "Point two"],
        topics=[{"label": "Testing", "confidence": 0.9}],
        reading_time_minutes=2,
        complexity="low",
    )
    return simple_doc


# ─────────────────────────────────────────────
# Document model tests
# ─────────────────────────────────────────────

class TestANDFDocument:
    def test_default_metadata(self):
        doc = ANDFDocument()
        assert doc._metadata["title"] == "Untitled Document"
        assert doc._metadata["language"] == "en"
        assert doc._metadata["status"] == "draft"

    def test_set_metadata(self, simple_doc):
        assert simple_doc._metadata["title"] == "Test Document"
        assert simple_doc._metadata["authors"] == ["Alice", "Bob"]
        assert "test" in simple_doc._metadata["keywords"]

    def test_add_section(self, simple_doc):
        assert len(simple_doc._sections) == 1
        sec = simple_doc._sections[0]
        assert sec.id == "intro"
        assert sec.title == "Introduction"
        assert sec.role == "introduction"

    def test_blocks_created(self, simple_doc):
        # heading + paragraph + list + code + callout + separator = 6 blocks
        assert len(simple_doc._blocks) == 6

    def test_section_block_ids(self, simple_doc):
        sec = simple_doc._sections[0]
        assert len(sec.block_ids) == 6
        for bid in sec.block_ids:
            assert bid in simple_doc._blocks

    def test_block_types(self, simple_doc):
        types = [b["type"] for b in simple_doc._blocks.values()]
        assert "heading" in types
        assert "paragraph" in types
        assert "list" in types
        assert "code" in types
        assert "callout" in types
        assert "separator" in types

    def test_themes(self):
        for name in ("default", "academic", "corporate", "minimal"):
            doc = ANDFDocument()
            doc.set_theme(name)
            assert doc._theme["name"] == name

    def test_set_layout(self):
        doc = ANDFDocument()
        doc.set_layout(page_size="Letter", orientation="landscape", columns=2)
        assert doc._layout["page_size"] == "Letter"
        assert doc._layout["orientation"] == "landscape"
        assert doc._layout["columns"] == 2

    def test_add_reference(self, rich_doc):
        assert len(rich_doc._references) == 1
        ref = rich_doc._references[0]
        assert ref["label"] == "Test2024"
        assert ref["year"] == 2024

    def test_subsections(self):
        doc = ANDFDocument()
        sec = doc.add_section("main", "Main")
        sub = sec.add_subsection("sub1", "Sub Section")
        sub.paragraph("Sub content")
        assert len(sec.subsections) == 1
        assert "sub1" in doc._section_map

    def test_all_block_types(self):
        doc = ANDFDocument()
        sec = doc.add_section("s1", "Test")
        sec.heading("H1", level=1)
        sec.heading("H2", level=2)
        sec.paragraph("Para")
        sec.list(["a", "b"])
        sec.list(["x", "y"], ordered=True)
        sec.code("x = 1", language="python")
        sec.quote("A quote", attribution="Someone")
        sec.callout("Info", variant="info")
        sec.callout("Warning", variant="warning")
        sec.callout("Error", variant="error")
        sec.callout("Success", variant="success")
        sec.callout("Tip", variant="tip")
        sec.table(["A", "B"], [["1", "2"]])
        sec.separator()
        sec.pagebreak()
        assert len(doc._blocks) == 15

    def test_to_dict_structure(self, simple_doc):
        d = simple_doc.to_dict()
        assert d["andf_version"] == "1.0"
        assert "document_id" in d
        assert "metadata" in d
        assert "layout" in d
        assert "theme" in d
        assert "sections" in d
        assert "blocks" in d
        assert "assets" in d
        assert "references" in d
        assert "ai" in d

    def test_to_json_valid(self, simple_doc):
        j = simple_doc.to_json()
        data = json.loads(j)
        assert data["andf_version"] == "1.0"

    def test_from_dict_roundtrip(self, rich_doc):
        d = rich_doc.to_dict()
        doc2 = ANDFDocument.from_dict(d)
        assert doc2._metadata["title"] == "Test Document"
        assert len(doc2._sections) == 1
        assert len(doc2._blocks) == len(rich_doc._blocks)
        assert len(doc2._references) == 1


# ─────────────────────────────────────────────
# Renderer tests
# ─────────────────────────────────────────────

class TestRenderer:
    def test_render_produces_html(self, simple_doc):
        from andf.renderer import ANDFRenderer
        html = ANDFRenderer(simple_doc).render()
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "andf-toolbar" in html
        assert "andf-viewer" in html
        assert "andf-page" in html

    def test_json_embedded(self, simple_doc):
        from andf.renderer import ANDFRenderer
        html = ANDFRenderer(simple_doc).render()
        assert 'type="application/andf+json"' in html
        assert "Test Document" in html

    def test_meta_tag(self, simple_doc):
        from andf.renderer import ANDFRenderer
        html = ANDFRenderer(simple_doc).render()
        assert 'name="andf-version" content="1.0"' in html

    def test_save_and_load(self, simple_doc):
        with tempfile.NamedTemporaryFile(suffix=".andf", delete=False) as f:
            path = f.name
        try:
            simple_doc.save(path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 1000
            doc2 = ANDFDocument.from_file(path)
            assert doc2._metadata["title"] == "Test Document"
        finally:
            os.unlink(path)

    def test_all_block_types_render(self):
        from andf.renderer import ANDFRenderer
        doc = ANDFDocument()
        doc.set_metadata(title="Render Test")
        sec = doc.add_section("s", "Section")
        sec.heading("H", level=1)
        sec.paragraph("Para with **bold** and *italic*.")
        sec.list(["a", "b", "c"])
        sec.list(["x", "y"], ordered=True)
        sec.code("print(1)", language="python")
        sec.quote("Quote text", attribution="Author")
        sec.callout("Info text", variant="info", title="Note")
        sec.callout("Warning text", variant="warning")
        sec.callout("Error text", variant="error")
        sec.callout("Success text", variant="success")
        sec.callout("Tip text", variant="tip")
        sec.table(["A", "B", "C"], [["1", "2", "3"], ["4", "5", "6"]])
        sec.separator()
        sec.pagebreak()
        sec.paragraph("After page break")
        html = ANDFRenderer(doc).render()
        assert "andf-h1" in html
        assert "andf-p" in html
        assert "andf-list" in html
        assert "andf-pre" in html
        assert "andf-quote" in html
        assert "andf-callout-info" in html
        assert "andf-callout-warning" in html
        assert "andf-callout-error" in html
        assert "andf-callout-success" in html
        assert "andf-callout-tip" in html
        assert "andf-table" in html
        assert "andf-hr" in html

    def test_multiple_pages(self):
        """Document with many blocks should span multiple pages."""
        from andf.renderer import ANDFRenderer
        doc = ANDFDocument()
        doc.set_metadata(title="Long Doc")
        sec = doc.add_section("s", "Section")
        for i in range(60):
            sec.paragraph(f"Paragraph {i}: " + "Lorem ipsum dolor sit amet. " * 5)
        html = ANDFRenderer(doc).render()
        page_count = html.count('class="andf-page"')
        assert page_count > 1

    def test_explicit_pagebreak(self):
        from andf.renderer import ANDFRenderer
        doc = ANDFDocument()
        doc.set_metadata(title="PB Test")
        sec = doc.add_section("s", "Section")
        sec.paragraph("Page 1")
        sec.pagebreak()
        sec.paragraph("Page 2")
        html = ANDFRenderer(doc).render()
        page_count = html.count('class="andf-page"')
        assert page_count >= 2


# ─────────────────────────────────────────────
# Parser tests
# ─────────────────────────────────────────────

class TestParser:
    def test_extract_json_from_html(self, simple_doc):
        from andf.renderer import ANDFRenderer
        html = ANDFRenderer(simple_doc).render()
        data = ANDFParser.extract_json(html)
        assert data["metadata"]["title"] == "Test Document"
        assert data["andf_version"] == "1.0"

    def test_parse_file(self, simple_doc):
        with tempfile.NamedTemporaryFile(suffix=".andf", delete=False) as f:
            path = f.name
        try:
            simple_doc.save(path)
            doc2 = ANDFParser.parse(path)
            assert doc2._metadata["title"] == "Test Document"
        finally:
            os.unlink(path)

    def test_validate_valid(self, simple_doc):
        d = simple_doc.to_dict()
        ok, errors = ANDFParser.validate(d)
        assert ok
        assert errors == []

    def test_validate_missing_version(self):
        d = {"document_id": "abc", "metadata": {"title": "T"}, "andf_version": "2.0"}
        ok, errors = ANDFParser.validate(d)
        assert not ok
        assert any("andf_version" in e for e in errors)

    def test_validate_missing_title(self):
        d = {"andf_version": "1.0", "document_id": "abc", "metadata": {}}
        ok, errors = ANDFParser.validate(d)
        assert not ok
        assert any("title" in e for e in errors)

    def test_validate_unknown_block_type(self):
        d = {
            "andf_version": "1.0",
            "document_id": "abc",
            "metadata": {"title": "T"},
            "blocks": {"blk_1": {"type": "unknown_type"}},
        }
        ok, errors = ANDFParser.validate(d)
        assert not ok
        assert any("unknown" in e for e in errors)

    def test_parse_raw_json(self, simple_doc):
        raw = simple_doc.to_json()
        data = ANDFParser.extract_json(raw)
        assert data["metadata"]["title"] == "Test Document"


# ─────────────────────────────────────────────
# AI Layer tests
# ─────────────────────────────────────────────

class TestAILayer:
    def test_full_text_contains_title(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        text = layer.full_text()
        assert "Test Document" in text

    def test_full_text_contains_content(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        text = layer.full_text()
        assert "Hello world" in text
        assert "Item one" in text

    def test_full_text_no_markdown_markup(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        text = layer.full_text()
        assert "**" not in text
        assert "*world*" not in text

    def test_to_markdown_heading(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        md = layer.to_markdown()
        assert "# Test Document" in md
        assert "## Introduction" in md

    def test_to_markdown_code_fence(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        md = layer.to_markdown()
        assert "```python" in md

    def test_to_markdown_references(self, rich_doc):
        layer = ANDFAILayer(rich_doc)
        md = layer.to_markdown()
        assert "References" in md
        assert "Test2024" in md

    def test_structured_context(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        ctx = layer.structured_context()
        assert ctx["document"]["title"] == "Test Document"
        assert len(ctx["sections"]) == 1
        assert ctx["sections"][0]["id"] == "intro"

    def test_context_chunks(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        chunks = layer.context_chunks(max_chars=200)
        assert len(chunks) > 0
        for chunk in chunks:
            assert "text" in chunk
            assert "section" in chunk
            assert "index" in chunk

    def test_context_chunks_max_size(self, simple_doc):
        layer = ANDFAILayer(simple_doc)
        max_chars = 150
        chunks = layer.context_chunks(max_chars=max_chars)
        for chunk in chunks:
            assert chunk["char_count"] <= max_chars + 200  # some tolerance

    def test_document_summary(self, rich_doc):
        layer = ANDFAILayer(rich_doc)
        summary = layer.document_summary()
        assert summary["title"] == "Test Document"
        assert summary["complexity"] == "low"
        assert summary["reading_time_minutes"] == 2
        assert "Point one" in summary["key_points"]
        assert summary["reference_count"] == 1
        assert summary["block_count"] == 6

    def test_blocks_by_importance(self):
        doc = ANDFDocument()
        sec = doc.add_section("s", "S")
        sec.paragraph("Important", importance=5)
        sec.paragraph("Normal", importance=2)
        sec.paragraph("Also important", importance=4)
        layer = ANDFAILayer(doc)
        high = layer.blocks_by_importance(min_importance=4)
        assert len(high) == 2

    def test_get_entities(self, rich_doc):
        entities = ANDFAILayer(rich_doc).get_entities()
        assert isinstance(entities, dict)


# ─────────────────────────────────────────────
# Inline markup tests
# ─────────────────────────────────────────────

class TestInlineMarkup:
    def test_bold(self):
        from andf.renderer import inline
        assert "<strong>bold</strong>" in inline("**bold** text")

    def test_italic(self):
        from andf.renderer import inline
        assert "<em>italic</em>" in inline("*italic* text")

    def test_code(self):
        from andf.renderer import inline
        assert "<code>x</code>" in inline("`x`")

    def test_ref(self):
        from andf.renderer import inline
        assert 'class="ref"' in inline("[Smith2024]")

    def test_html_escape(self):
        from andf.renderer import inline
        result = inline("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


# ─────────────────────────────────────────────
# Asset tests
# ─────────────────────────────────────────────

class TestAssets:
    def test_add_asset_base64(self, simple_doc):
        asset_id = simple_doc.add_asset_base64("aGVsbG8=", "image/png", "test.png")
        assert asset_id in simple_doc._assets
        asset = simple_doc._assets[asset_id]
        assert asset["mime_type"] == "image/png"
        assert asset["data"] == "aGVsbG8="

    def test_asset_in_rendered_output(self, simple_doc):
        from andf.renderer import ANDFRenderer
        asset_id = simple_doc.add_asset_base64("aGVsbG8=", "image/png", "img.png")
        sec = simple_doc._sections[0]
        sec.image(asset_id, alt="Test image", caption="A test image")
        html = ANDFRenderer(simple_doc).render()
        assert "data:image/png;base64,aGVsbG8=" in html
        assert "Test image" in html

    def test_missing_asset_placeholder(self):
        from andf.renderer import ANDFRenderer
        doc = ANDFDocument()
        doc.set_metadata(title="T")
        sec = doc.add_section("s", "S")
        sec.image("nonexistent_asset_id", alt="Missing image")
        html = ANDFRenderer(doc).render()
        assert "Missing image" in html


# ─────────────────────────────────────────────
# End-to-end
# ─────────────────────────────────────────────

class TestEndToEnd:
    def test_full_roundtrip(self):
        """Create → save → parse → AI extract → verify."""
        doc = ANDFDocument()
        doc.set_metadata(
            title="E2E Test",
            authors=["Tester"],
            keywords=["e2e"],
        )
        doc.set_theme("corporate")
        doc.set_ai(
            summary="End-to-end test document.",
            key_points=["It works"],
            complexity="low",
        )
        ref_id = doc.add_reference(label="Ref1", title="A Reference", year=2025)
        sec = doc.add_section("main", "Main Section")
        sec.heading("Overview", level=2)
        sec.paragraph(f"Document with a reference [Ref1].")
        sec.table(["X", "Y"], [["1", "2"], ["3", "4"]], caption="Data")
        sub = sec.add_subsection("sub", "Sub Section")
        sub.paragraph("Sub content here.")

        with tempfile.NamedTemporaryFile(suffix=".andf", delete=False) as f:
            path = f.name
        try:
            doc.save(path)

            # Parse back
            doc2 = ANDFDocument.from_file(path)
            assert doc2._metadata["title"] == "E2E Test"
            assert len(doc2._sections) == 1
            assert len(doc2._references) == 1

            # AI layer
            layer = ANDFAILayer(doc2)
            text = layer.full_text()
            assert "E2E Test" in text
            assert "Overview" in text

            md = layer.to_markdown()
            assert "## Overview" in md

            summary = layer.document_summary()
            assert summary["complexity"] == "low"
            assert "It works" in summary["key_points"]

            # Validate
            with open(path) as f:
                content = f.read()
            data = ANDFParser.extract_json(content)
            ok, errors = ANDFParser.validate(data)
            assert ok, f"Validation errors: {errors}"

        finally:
            os.unlink(path)
