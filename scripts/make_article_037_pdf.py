"""Build the PDF for article 037 by reusing the article-031 renderer.

Same pipeline as 032-036: import the 031 renderer, point it at 037, override the document properties.

Usage: python scripts/make_article_037_pdf.py
"""
from __future__ import annotations
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "make_article_031_pdf.py"

ARTICLE = ROOT / "articles" / "037-what-our-errors-say-about-the-limits-of-the-method.md"
OUT = ROOT / "articles" / "037-what-our-errors-say-about-the-limits-of-the-method.pdf"


def _properties(doc) -> None:
    p = doc.core_properties
    p.author = "AI agents of the pond bench, with periodic human-operator feedback"
    p.last_modified_by = "AI agents of the pond bench"
    p.title = "What our own errors say about the limits of the method"
    p.subject = ("A manifesto: three claims about why the present designs cannot find the living, "
                 "corrected after two independent referees")
    p.keywords = ("research method; open-ended evolution; falsifiability; within-cell measurement; "
                  "select versus specify")


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
    print(f"[037-pdf] rc={rc} -> {OUT} exists={OUT.exists()}")
    if OUT.exists():
        print(f"[037-pdf] size {OUT.stat().st_size} bytes")
    return rc


if __name__ == "__main__":
    sys.exit(main())
