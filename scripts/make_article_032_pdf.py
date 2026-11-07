"""Build the PDF for article 032 by reusing the article-031 renderer.

The 031 renderer hard-codes its input path; rather than duplicate 400 lines, this script imports it,
points it at 032 and writes the PDF next to the article. Everything else (Markdown -> docx -> PDF via
the bundled LibreOffice Kit) is the same pipeline that produced the published 031 PDF.
"""
from __future__ import annotations
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "make_article_031_pdf.py"


def main(argv=None) -> int:
    spec = importlib.util.spec_from_file_location("pdf031", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    art = ROOT / "articles" / "032-what-decides-whether-behaviour-pays.md"
    out = ROOT / "articles" / "032-what-decides-whether-behaviour-pays.pdf"
    if not art.exists():
        print(f"missing {art}", file=sys.stderr)
        return 1
    # the 031 module exposes ARTICLE / OUT paths as module-level constants; override them
    mod.ARTICLE = art
    mod.set_document_properties = lambda doc: _properties(doc)
    for name in ("OUT_PDF", "PDF", "OUT"):
        if hasattr(mod, name):
            setattr(mod, name, out)
    rc = mod.main(argv or [])
    print(f"[032-pdf] rc={rc} -> {out} exists={out.exists()}")
    if out.exists():
        print(f"[032-pdf] size {out.stat().st_size} bytes")
    return rc


def _properties(doc) -> None:
    """The 032 metadata: the shared renderer is 031's, so its title and subject would leak into this PDF."""
    p = doc.core_properties
    p.author = "Ilya Vladimirov"
    p.last_modified_by = "Ilya Vladimirov"
    p.title = "What decides whether behaviour pays: movement, not the signal it follows"
    p.subject = ("A pond world with resource, death and reproduction; the sign of the greedy advantage depends on the "
                 "resource recovery rate; the cause is a trap of inaction; a diffusing signal field is unnecessary; v1.2")
    p.keywords = "pond; directionality; habituation; mobility; memory; boundary-of-the-setup"
    p.comments = ("Data and figures: CC BY 4.0. Every printed number is checked against the artifacts by "
                  "scripts/check_article_032_numbers.py.")


if __name__ == "__main__":
    raise SystemExit(main())
