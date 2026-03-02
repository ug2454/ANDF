"""
ANDFDocument model and fluent builder API.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


# ─────────────────────────────────────────────
# Theme presets
# ─────────────────────────────────────────────

THEMES: dict[str, dict] = {
    "default": {
        "name": "default",
        "font_body": "Inter, sans-serif",
        "font_heading": "Inter, sans-serif",
        "font_mono": "JetBrains Mono, monospace",
        "font_size": 11,
        "line_height": 1.6,
        "colors": {
            "text": "#1a1a1a",
            "heading": "#111111",
            "link": "#1a73e8",
            "muted": "#6b7280",
            "border": "#e5e7eb",
            "callout_info": "#eff6ff",
            "callout_warning": "#fffbeb",
            "callout_error": "#fef2f2",
            "callout_success": "#f0fdf4",
            "callout_tip": "#f5f3ff",
            "code_bg": "#f8f8f8",
            "code_border": "#e1e4e8",
        },
    },
    "academic": {
        "name": "academic",
        "font_body": "Georgia, serif",
        "font_heading": "Georgia, serif",
        "font_mono": "Courier New, monospace",
        "font_size": 11,
        "line_height": 1.7,
        "colors": {
            "text": "#1a1a1a",
            "heading": "#000000",
            "link": "#0000EE",
            "muted": "#555555",
            "border": "#cccccc",
            "callout_info": "#e8f0fe",
            "callout_warning": "#fef3c7",
            "callout_error": "#fee2e2",
            "callout_success": "#dcfce7",
            "callout_tip": "#ede9fe",
            "code_bg": "#f6f8fa",
            "code_border": "#d0d7de",
        },
    },
    "corporate": {
        "name": "corporate",
        "font_body": "Arial, sans-serif",
        "font_heading": "Arial, sans-serif",
        "font_mono": "Consolas, monospace",
        "font_size": 10,
        "line_height": 1.5,
        "colors": {
            "text": "#212121",
            "heading": "#1565c0",
            "link": "#1565c0",
            "muted": "#757575",
            "border": "#e0e0e0",
            "callout_info": "#e3f2fd",
            "callout_warning": "#fff8e1",
            "callout_error": "#ffebee",
            "callout_success": "#e8f5e9",
            "callout_tip": "#f3e5f5",
            "code_bg": "#f5f5f5",
            "code_border": "#bdbdbd",
        },
    },
    "minimal": {
        "name": "minimal",
        "font_body": "system-ui, sans-serif",
        "font_heading": "system-ui, sans-serif",
        "font_mono": "ui-monospace, monospace",
        "font_size": 11,
        "line_height": 1.6,
        "colors": {
            "text": "#374151",
            "heading": "#111827",
            "link": "#2563eb",
            "muted": "#9ca3af",
            "border": "#f3f4f6",
            "callout_info": "#f0f9ff",
            "callout_warning": "#fffbeb",
            "callout_error": "#fff1f2",
            "callout_success": "#f0fdf4",
            "callout_tip": "#faf5ff",
            "code_bg": "#f9fafb",
            "code_border": "#e5e7eb",
        },
    },
}

DEFAULT_LAYOUT: dict = {
    "page_size": "A4",
    "orientation": "portrait",
    "margins": {"top": 25, "bottom": 25, "left": 25, "right": 25},
    "columns": 1,
    "header": None,
    "footer": "page_number",
}


# ─────────────────────────────────────────────
# Section builder
# ─────────────────────────────────────────────

class Section:
    def __init__(self, doc: "ANDFDocument", section_id: str, title: str, role: str):
        self._doc = doc
        self.id = section_id
        self.title = title
        self.role = role
        self.block_ids: list[str] = []
        self.subsections: list["Section"] = []

    # ── block helpers ──

    def _add_block(self, block_type: str, **fields) -> "Section":
        block_id = f"blk_{uuid.uuid4().hex[:8]}"
        block = {"type": block_type, **fields}
        self._doc._blocks[block_id] = block
        self.block_ids.append(block_id)
        return self

    def heading(self, text: str, level: int = 2, **semantic) -> "Section":
        return self._add_block("heading", level=level, text=text,
                               semantic=_sem(semantic))

    def paragraph(self, text: str, **semantic) -> "Section":
        return self._add_block("paragraph", text=text, semantic=_sem(semantic))

    def image(self, asset_id: str, alt: str = "", caption: str = "",
              width: str = "100%", align: str = "center", **semantic) -> "Section":
        return self._add_block("image", asset_id=asset_id, alt=alt,
                               caption=caption, width=width, align=align,
                               semantic=_sem(semantic))

    def table(self, headers: list[str], rows: list[list[str]],
              caption: str = "", align: Optional[list[str]] = None,
              **semantic) -> "Section":
        return self._add_block("table", caption=caption, headers=headers,
                               rows=rows, align=align or ["left"] * len(headers),
                               semantic=_sem(semantic))

    def list(self, items: list, ordered: bool = False, **semantic) -> "Section":
        normalized = []
        for item in items:
            if isinstance(item, str):
                normalized.append({"text": item, "level": 0})
            else:
                normalized.append(item)
        return self._add_block("list", ordered=ordered, items=normalized,
                               semantic=_sem(semantic))

    def code(self, code: str, language: str = "text", caption: str = "",
             line_numbers: bool = False, **semantic) -> "Section":
        return self._add_block("code", language=language, code=code,
                               caption=caption, line_numbers=line_numbers,
                               semantic=_sem(semantic))

    def quote(self, text: str, attribution: str = "",
              style: str = "blockquote", **semantic) -> "Section":
        return self._add_block("quote", text=text, attribution=attribution,
                               style=style, semantic=_sem(semantic))

    def callout(self, text: str, variant: str = "info", title: str = "",
                **semantic) -> "Section":
        return self._add_block("callout", variant=variant, title=title,
                               text=text, semantic=_sem(semantic))

    def separator(self) -> "Section":
        return self._add_block("separator")

    def pagebreak(self) -> "Section":
        return self._add_block("pagebreak")

    def add_subsection(self, section_id: str, title: str,
                       role: str = "body") -> "Section":
        sub = Section(self._doc, section_id, title, role)
        self.subsections.append(sub)
        self._doc._section_map[section_id] = sub
        return sub

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "role": self.role,
            "blocks": self.block_ids,
            "subsections": [s.to_dict() for s in self.subsections],
        }


def _sem(kwargs: dict) -> dict:
    """Build a semantic annotation dict from keyword arguments."""
    sem: dict = {}
    for key in ("role", "context", "importance", "entities", "summary"):
        if key in kwargs:
            sem[key] = kwargs[key]
    return sem


# ─────────────────────────────────────────────
# Main document
# ─────────────────────────────────────────────

class ANDFDocument:
    """
    Fluent builder for ANDF documents.

    Usage::

        doc = ANDFDocument()
        doc.set_metadata(title="My Doc", authors=["Alice"])
        sec = doc.add_section("intro", "Introduction")
        sec.paragraph("Hello world")
        doc.save("output.andf")
    """

    FORMAT_VERSION = "1.0"

    def __init__(self):
        self._id = str(uuid.uuid4())
        self._metadata: dict = {
            "title": "Untitled Document",
            "subtitle": "",
            "authors": [],
            "created": _now(),
            "modified": _now(),
            "keywords": [],
            "language": "en",
            "category": "",
            "status": "draft",
            "version": "1.0",
            "license": "",
        }
        self._layout: dict = dict(DEFAULT_LAYOUT)
        self._theme: dict = dict(THEMES["default"])
        self._sections: list[Section] = []
        self._section_map: dict[str, Section] = {}
        self._blocks: dict[str, dict] = {}
        self._assets: dict[str, dict] = {}
        self._references: list[dict] = []
        self._ai: dict = {
            "summary": "",
            "key_points": [],
            "topics": [],
            "reading_time_minutes": 1,
            "complexity": "medium",
            "questions_answered": [],
            "entities": {
                "people": [],
                "organizations": [],
                "technologies": [],
                "concepts": [],
            },
        }

    # ── metadata ──

    def set_metadata(self, title: str = "", subtitle: str = "",
                     authors: Optional[list[str]] = None,
                     keywords: Optional[list[str]] = None,
                     language: str = "en", category: str = "",
                     status: str = "draft", version: str = "1.0",
                     license: str = "", **extra) -> "ANDFDocument":
        if title:
            self._metadata["title"] = title
        if subtitle:
            self._metadata["subtitle"] = subtitle
        if authors is not None:
            self._metadata["authors"] = authors
        if keywords is not None:
            self._metadata["keywords"] = keywords
        self._metadata["language"] = language
        self._metadata["category"] = category
        self._metadata["status"] = status
        self._metadata["version"] = version
        self._metadata["license"] = license
        self._metadata["modified"] = _now()
        self._metadata.update(extra)
        return self

    # ── layout ──

    def set_layout(self, page_size: str = "A4", orientation: str = "portrait",
                   margins: Optional[dict] = None, columns: int = 1,
                   header: Optional[str] = None,
                   footer: str = "page_number") -> "ANDFDocument":
        self._layout["page_size"] = page_size
        self._layout["orientation"] = orientation
        if margins:
            self._layout["margins"] = margins
        self._layout["columns"] = columns
        self._layout["header"] = header
        self._layout["footer"] = footer
        return self

    # ── theme ──

    def set_theme(self, name: str = "default",
                  **overrides) -> "ANDFDocument":
        base = THEMES.get(name, THEMES["default"])
        self._theme = dict(base)
        self._theme.update(overrides)
        return self

    # ── sections ──

    def add_section(self, section_id: str, title: str,
                    role: str = "body") -> Section:
        sec = Section(self, section_id, title, role)
        self._sections.append(sec)
        self._section_map[section_id] = sec
        return sec

    def get_section(self, section_id: str) -> Optional[Section]:
        return self._section_map.get(section_id)

    # ── assets ──

    def add_asset_file(self, path: str,
                       name: Optional[str] = None) -> str:
        import base64
        import mimetypes
        import os
        asset_id = f"asset_{uuid.uuid4().hex[:8]}"
        mime, _ = mimetypes.guess_type(path)
        mime = mime or "application/octet-stream"
        file_name = name or os.path.basename(path)
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        self._assets[asset_id] = {
            "type": mime.split("/")[0],
            "name": file_name,
            "mime_type": mime,
            "encoding": "base64",
            "data": data,
        }
        return asset_id

    def add_asset_base64(self, data: str, mime_type: str,
                         name: str = "asset") -> str:
        asset_id = f"asset_{uuid.uuid4().hex[:8]}"
        self._assets[asset_id] = {
            "type": mime_type.split("/")[0],
            "name": name,
            "mime_type": mime_type,
            "encoding": "base64",
            "data": data,
        }
        return asset_id

    # ── references ──

    def add_reference(self, ref_type: str = "article", label: str = "",
                      title: str = "", authors: Optional[list[str]] = None,
                      year: Optional[int] = None, doi: str = "",
                      url: str = "", **extra) -> str:
        ref_id = f"ref_{uuid.uuid4().hex[:8]}"
        self._references.append({
            "id": ref_id,
            "type": ref_type,
            "label": label,
            "title": title,
            "authors": authors or [],
            "year": year,
            "doi": doi,
            "url": url,
            **extra,
        })
        return ref_id

    # ── AI layer ──

    def set_ai(self, summary: str = "", key_points: Optional[list] = None,
               topics: Optional[list] = None,
               reading_time_minutes: int = 1,
               complexity: str = "medium",
               questions_answered: Optional[list] = None,
               entities: Optional[dict] = None) -> "ANDFDocument":
        self._ai["summary"] = summary
        if key_points is not None:
            self._ai["key_points"] = key_points
        if topics is not None:
            self._ai["topics"] = topics
        self._ai["reading_time_minutes"] = reading_time_minutes
        self._ai["complexity"] = complexity
        if questions_answered is not None:
            self._ai["questions_answered"] = questions_answered
        if entities is not None:
            self._ai["entities"] = entities
        return self

    # ── serialization ──

    def to_dict(self) -> dict:
        return {
            "andf_version": self.FORMAT_VERSION,
            "document_id": self._id,
            "metadata": self._metadata,
            "layout": self._layout,
            "theme": self._theme,
            "sections": [s.to_dict() for s in self._sections],
            "blocks": self._blocks,
            "assets": self._assets,
            "references": self._references,
            "ai": self._ai,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ANDFDocument":
        doc = cls()
        doc._id = data.get("document_id", doc._id)
        doc._metadata = data.get("metadata", doc._metadata)
        doc._layout = data.get("layout", doc._layout)
        doc._theme = data.get("theme", doc._theme)
        doc._blocks = data.get("blocks", {})
        doc._assets = data.get("assets", {})
        doc._references = data.get("references", [])
        doc._ai = data.get("ai", doc._ai)
        # Rebuild sections
        for s_data in data.get("sections", []):
            sec = _section_from_dict(doc, s_data)
            doc._sections.append(sec)
            doc._section_map[sec.id] = sec
        return doc

    @classmethod
    def from_file(cls, path: str) -> "ANDFDocument":
        from .parser import ANDFParser
        return ANDFParser.parse(path)

    def save(self, path: str) -> None:
        from .renderer import ANDFRenderer
        html = ANDFRenderer(self).render()
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def open_in_browser(self, path: Optional[str] = None) -> None:
        import tempfile
        from .cli import _open_in_browser
        if path is None:
            fd, path = tempfile.mkstemp(suffix=".andf", prefix="andf_")
            os.close(fd)
        self.save(path)
        _open_in_browser(path)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _section_from_dict(doc: ANDFDocument, data: dict) -> Section:
    sec = Section(doc, data["id"], data.get("title", ""), data.get("role", "body"))
    sec.block_ids = data.get("blocks", [])
    for sub_data in data.get("subsections", []):
        sub = _section_from_dict(doc, sub_data)
        sec.subsections.append(sub)
        doc._section_map[sub.id] = sub
    return sec
