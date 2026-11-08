"""Build the PDF for article 036 by reusing the article-031 renderer.

The 031 renderer hard-codes its input path; rather than duplicate 400 lines, this script imports it, points it
at 036 and writes the PDF next to the article. Everything else (Markdown -> docx -> PDF via the bundled
LibreOffice Kit) is the same pipeline that produced the published 031-035 PDFs.

Usage: python scripts/make_article_036_pdf.py
"""
from __future__ import annotations
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "make_article_031_pdf.py"

ARTICLE = ROOT / "articles" / "036-a-research-bench-where-the-instrument-reports-on-itself.md"
OUT = ROOT / "articles" / "036-a-research-bench-where-the-instrument-reports-on-itself.pdf"


def _properties(doc) -> None:
    """The shared renderer is 031's, so its title and subject would otherwise leak into this PDF."""
    p = doc.core_properties
    p.author = "AI agents of the pond bench, with periodic human-operator feedback"
    p.last_modified_by = "AI agents of the pond bench"
    p.title = "A research bench where the instrument reports on itself"
    p.subject = ("How a minimal artificial world was made reproducible, refutable and formally checkable, "
                 "and what it cost")
    p.keywords = "reproducibility; formal verification; Lean; mutation testing; agent governance"


def main(argv=None) -> int:
    spec = importlib.util.spec_from_file_location("pdf031", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if not ARTICLE.exists():
        print(f"missing {ARTICLE}", file=sys.stderr)
        return 1
    mod.ARTICLE = ARTICLE
    mod.set_document_properties = _properties
    for name in ("OUT_PDF", "PDF", "OUT"):
        if hasattr(mod, name):
            setattr(mod, name, OUT)
    rc = mod.main(argv or [])
    print(f"[036-pdf] rc={rc} -> {OUT} exists={OUT.exists()}")
    if OUT.exists():
        print(f"[036-pdf] size {OUT.stat().st_size} bytes")
    return rc


if __name__ == "__main__":
    sys.exit(main())
