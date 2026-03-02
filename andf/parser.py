"""
ANDFParser — reads a .andf file and returns an ANDFDocument.
"""
from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .document import ANDFDocument


class ANDFParser:
    # Matches <script type="application/andf+json">...</script>
    _SCRIPT_RE = re.compile(
        r'<script[^>]+type=["\']application/andf\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )

    @classmethod
    def parse(cls, path: str) -> "ANDFDocument":
        from .document import ANDFDocument
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        data = cls.extract_json(content)
        return ANDFDocument.from_dict(data)

    @classmethod
    def extract_json(cls, html_str: str) -> dict:
        match = cls._SCRIPT_RE.search(html_str)
        if not match:
            # Try parsing as raw JSON
            try:
                return json.loads(html_str.strip())
            except json.JSONDecodeError:
                raise ValueError("No ANDF JSON data found in file.")
        raw = match.group(1).strip()
        # Undo the </script> escaping done by the renderer
        raw = raw.replace("<\\/script>", "</script>")
        return json.loads(raw)

    @classmethod
    def validate(cls, data: dict) -> tuple[bool, list[str]]:
        errors: list[str] = []

        if data.get("andf_version") != "1.0":
            errors.append(f"Unsupported or missing andf_version: {data.get('andf_version')!r}")

        if "document_id" not in data:
            errors.append("Missing document_id")

        meta = data.get("metadata", {})
        if not meta.get("title"):
            errors.append("metadata.title is required")

        for i, sec in enumerate(data.get("sections", [])):
            if "id" not in sec:
                errors.append(f"Section {i} missing 'id'")
            if "title" not in sec:
                errors.append(f"Section {i} missing 'title'")

        blocks = data.get("blocks", {})
        valid_types = {
            "heading", "paragraph", "image", "table", "list",
            "code", "quote", "callout", "separator", "pagebreak", "equation",
        }
        for bid, block in blocks.items():
            btype = block.get("type")
            if btype not in valid_types:
                errors.append(f"Block {bid!r} has unknown type {btype!r}")

        return len(errors) == 0, errors
