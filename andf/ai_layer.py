"""
ANDFAILayer — AI-friendly extraction from an ANDFDocument.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .document import ANDFDocument


def _strip_inline(text: str) -> str:
    """Remove simple markdown-like markup."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]', r'[\1]', text)
    return text


class ANDFAILayer:
    def __init__(self, doc: "ANDFDocument"):
        self.doc = doc
        self._data = doc.to_dict()
        self._blocks = self._data.get("blocks", {})

    # ── Text extraction ──

    def full_text(self) -> str:
        """Plain text concatenation of all blocks in document order."""
        parts = []
        meta = self._data.get("metadata", {})
        title = meta.get("title", "")
        if title:
            parts.append(title)
        subtitle = meta.get("subtitle", "")
        if subtitle:
            parts.append(subtitle)
        for block_id in self._all_block_ids():
            block = self._blocks.get(block_id, {})
            text = self._block_text(block)
            if text:
                parts.append(text)
        return "\n\n".join(parts)

    def to_markdown(self) -> str:
        """Markdown representation — best for LLM input."""
        lines: list[str] = []
        meta = self._data.get("metadata", {})

        # Front matter
        title = meta.get("title", "")
        if title:
            lines.append(f"# {title}")
        subtitle = meta.get("subtitle", "")
        if subtitle:
            lines.append(f"*{subtitle}*")
        authors = meta.get("authors", [])
        if authors:
            lines.append(f"**Authors:** {', '.join(authors)}")
        lines.append("")

        sections = self._data.get("sections", [])
        for sec in sections:
            lines.extend(self._section_markdown(sec, depth=0))

        # References
        refs = self._data.get("references", [])
        if refs:
            lines.append("\n---\n## References")
            for ref in refs:
                label = ref.get("label", ref.get("id", ""))
                title_r = ref.get("title", "")
                authors_r = ", ".join(ref.get("authors", []))
                year = ref.get("year", "")
                doi = ref.get("doi", "")
                line = f"[{label}] {title_r}"
                if authors_r:
                    line += f" — {authors_r}"
                if year:
                    line += f" ({year})"
                if doi:
                    line += f" DOI:{doi}"
                lines.append(line)

        return "\n".join(lines)

    def _section_markdown(self, sec: dict, depth: int) -> list[str]:
        lines: list[str] = []
        title = sec.get("title", "")
        if title:
            hashes = "#" * (depth + 2)
            lines.append(f"\n{hashes} {title}\n")
        for block_id in sec.get("blocks", []):
            block = self._blocks.get(block_id, {})
            md = self._block_markdown(block)
            if md:
                lines.append(md)
        for sub in sec.get("subsections", []):
            lines.extend(self._section_markdown(sub, depth + 1))
        return lines

    def _block_markdown(self, block: dict) -> str:
        btype = block.get("type", "paragraph")
        if btype == "heading":
            level = block.get("level", 2)
            text = _strip_inline(block.get("text", ""))
            return f"{'#' * level} {text}"
        if btype == "paragraph":
            return _strip_inline(block.get("text", ""))
        if btype == "list":
            items = block.get("items", [])
            ordered = block.get("ordered", False)
            lines = []
            for i, item in enumerate(items):
                prefix = f"{i+1}." if ordered else "-"
                indent = "  " * item.get("level", 0)
                lines.append(f"{indent}{prefix} {_strip_inline(item.get('text', ''))}")
            return "\n".join(lines)
        if btype == "code":
            lang = block.get("language", "")
            code = block.get("code", "")
            caption = block.get("caption", "")
            lines = []
            if caption:
                lines.append(f"*{caption}*")
            lines.append(f"```{lang}\n{code}\n```")
            return "\n".join(lines)
        if btype == "table":
            caption = block.get("caption", "")
            headers = block.get("headers", [])
            rows = block.get("rows", [])
            lines = []
            if caption:
                lines.append(f"*{caption}*")
            if headers:
                lines.append("| " + " | ".join(str(h) for h in headers) + " |")
                lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            return "\n".join(lines)
        if btype == "quote":
            text = _strip_inline(block.get("text", ""))
            attr = block.get("attribution", "")
            q = "\n".join(f"> {line}" for line in text.split("\n"))
            if attr:
                q += f"\n> — {attr}"
            return q
        if btype == "callout":
            variant = block.get("variant", "info").upper()
            title = block.get("title", "")
            text = _strip_inline(block.get("text", ""))
            header = f"**[{variant}]** {title}: " if title else f"**[{variant}]** "
            return f"> {header}{text}"
        if btype == "separator":
            return "---"
        if btype == "pagebreak":
            return "---"
        if btype == "image":
            alt = block.get("alt", "")
            caption = block.get("caption", "")
            return f"![{alt}]({caption or alt})"
        return ""

    def _block_text(self, block: dict) -> str:
        btype = block.get("type", "paragraph")
        if btype in ("heading", "paragraph"):
            return _strip_inline(block.get("text", ""))
        if btype == "list":
            return "\n".join(
                _strip_inline(item.get("text", ""))
                for item in block.get("items", [])
            )
        if btype == "code":
            return block.get("code", "")
        if btype == "table":
            lines = [" | ".join(block.get("headers", []))]
            for row in block.get("rows", []):
                lines.append(" | ".join(str(c) for c in row))
            return "\n".join(lines)
        if btype in ("quote", "callout"):
            return _strip_inline(block.get("text", ""))
        return ""

    # ── Structured context ──

    def structured_context(self) -> dict:
        """Returns a dict with hierarchy, semantic roles, and entities."""
        data = self._data
        ctx: dict[str, Any] = {
            "document": {
                "id": data.get("document_id"),
                "title": data["metadata"].get("title"),
                "authors": data["metadata"].get("authors", []),
                "language": data["metadata"].get("language", "en"),
            },
            "ai": data.get("ai", {}),
            "sections": [],
        }
        for sec in data.get("sections", []):
            ctx["sections"].append(self._section_context(sec))
        return ctx

    def _section_context(self, sec: dict) -> dict:
        block_contexts = []
        for bid in sec.get("blocks", []):
            block = self._blocks.get(bid, {})
            bc = {
                "id": bid,
                "type": block.get("type"),
                "text_preview": self._block_text(block)[:200],
                "semantic": block.get("semantic", {}),
            }
            block_contexts.append(bc)
        return {
            "id": sec.get("id"),
            "title": sec.get("title"),
            "role": sec.get("role"),
            "blocks": block_contexts,
            "subsections": [self._section_context(s) for s in sec.get("subsections", [])],
        }

    # ── Chunking ──

    def context_chunks(self, max_chars: int = 4000) -> list[dict]:
        """Splits document into chunks suitable for RAG / embedding."""
        chunks: list[dict] = []
        current_text = ""
        current_section = ""
        chunk_index = 0

        def flush():
            nonlocal current_text, chunk_index
            if current_text.strip():
                chunks.append({
                    "index": chunk_index,
                    "section": current_section,
                    "text": current_text.strip(),
                    "char_count": len(current_text.strip()),
                })
                chunk_index += 1
            current_text = ""

        for sec in self._data.get("sections", []):
            current_section = sec.get("title", "")
            for bid in sec.get("blocks", []):
                block = self._blocks.get(bid, {})
                text = self._block_text(block)
                if not text:
                    continue
                if len(current_text) + len(text) > max_chars:
                    flush()
                current_text += text + "\n\n"
            for sub in sec.get("subsections", []):
                current_section = f"{sec.get('title', '')} > {sub.get('title', '')}"
                for bid in sub.get("blocks", []):
                    block = self._blocks.get(bid, {})
                    text = self._block_text(block)
                    if not text:
                        continue
                    if len(current_text) + len(text) > max_chars:
                        flush()
                    current_text += text + "\n\n"

        flush()
        return chunks

    # ── Filtering ──

    def blocks_by_importance(self, min_importance: int = 3) -> list[dict]:
        """Returns blocks where semantic.importance >= min_importance."""
        result = []
        for bid in self._all_block_ids():
            block = self._blocks.get(bid, {})
            sem = block.get("semantic", {})
            importance = sem.get("importance", 0)
            if importance >= min_importance:
                result.append({"id": bid, **block})
        return result

    # ── Entities ──

    def get_entities(self) -> dict:
        """Returns merged entity list from the AI section."""
        ai = self._data.get("ai", {})
        return ai.get("entities", {
            "people": [], "organizations": [], "technologies": [], "concepts": []
        })

    # ── Summary ──

    def document_summary(self) -> dict:
        meta = self._data.get("metadata", {})
        ai = self._data.get("ai", {})
        return {
            "title": meta.get("title", ""),
            "subtitle": meta.get("subtitle", ""),
            "authors": meta.get("authors", []),
            "created": meta.get("created", "")[:10],
            "keywords": meta.get("keywords", []),
            "category": meta.get("category", ""),
            "status": meta.get("status", ""),
            "version": meta.get("version", ""),
            "summary": ai.get("summary", ""),
            "key_points": ai.get("key_points", []),
            "topics": ai.get("topics", []),
            "reading_time_minutes": ai.get("reading_time_minutes", 1),
            "complexity": ai.get("complexity", "medium"),
            "questions_answered": ai.get("questions_answered", []),
            "entities": ai.get("entities", {}),
            "section_count": len(self._data.get("sections", [])),
            "block_count": len(self._blocks),
            "reference_count": len(self._data.get("references", [])),
        }

    # ── Helpers ──

    def _all_block_ids(self) -> list[str]:
        ids = []
        for sec in self._data.get("sections", []):
            ids.extend(sec.get("blocks", []))
            for sub in sec.get("subsections", []):
                ids.extend(sub.get("blocks", []))
        return ids
