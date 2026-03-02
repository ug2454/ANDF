"""
ANDF — AI Native Document Format
=================================
A self-contained HTML file format that looks like a PDF in the browser
and is trivially parseable by AI tools.

Quick start::

    from andf import ANDFDocument

    doc = ANDFDocument()
    doc.set_metadata(title="My Document", authors=["Alice"])
    sec = doc.add_section("intro", "Introduction")
    sec.heading("Welcome", level=2)
    sec.paragraph("Hello from **ANDF**!")
    doc.save("output.andf")

    # Open in browser
    doc.open_in_browser("output.andf")

    # Parse an existing file
    doc2 = ANDFDocument.from_file("output.andf")

    # AI extraction
    from andf import ANDFAILayer
    layer = ANDFAILayer(doc2)
    print(layer.to_markdown())
"""

from .document import ANDFDocument
from .parser import ANDFParser
from .ai_layer import ANDFAILayer


def load(path: str) -> ANDFDocument:
    """Load an ANDF document from a file path."""
    return ANDFDocument.from_file(path)


def save(doc: ANDFDocument, path: str) -> None:
    """Save an ANDF document to a file path."""
    doc.save(path)


def open_in_browser(path: str) -> None:
    """Open an existing .andf file in the default browser."""
    from .cli import _open_in_browser
    _open_in_browser(path)


__version__ = "1.0.0"
__all__ = ["ANDFDocument", "ANDFParser", "ANDFAILayer", "load", "save", "open_in_browser"]
