"""make_article_030_pdf.py — render article 030 as a self-contained PDF for the deposit.

Same renderer as the 029 edition (no pandoc or TeX on the publication machine): the Markdown goes into a
`.docx` with python-docx and is converted with the bundled LibreOffice Kit.

    python scripts/make_article_030_pdf.py
    python scripts/make_article_030_pdf.py --node <node.exe> --lo-cli <libreoffice-kit/cli.js>

Output: `articles/030-the-gap-between-surfaces-decides-fusion.pdf` (committed, and picked up by
`scripts/build_article_030_package.py`), intermediate `.docx` under `_exports/030-pdf/` (ignored).

The renderer understands only the subset of Markdown this article uses: headings, paragraphs, pipe tables,
fenced code, block quotes, bullet and numbered items, images and the inline `**bold**` / `*italic*` /
`` `code` `` / `[label](link)` forms. Anything else is emitted as literal text rather than silently dropped.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "030-the-gap-between-surfaces-decides-fusion.md"
FIGS = ROOT / "articles" / "030-figures"
PDF = ROOT / "articles" / "030-the-gap-between-surfaces-decides-fusion.pdf"
WORK = ROOT / "_exports" / "030-pdf"
DOCX = WORK / "030-the-gap-between-surfaces-decides-fusion.docx"

def set_document_properties(doc: Document) -> None:
    """Fill the metadata a reader sees in a PDF viewer (python-docx otherwise signs the file with its own name)."""
    p = doc.core_properties
    p.author = "Ilya Vladimirov"
    p.last_modified_by = "Ilya Vladimirov"
    p.title = ("The gap between surfaces, not the body size, switches fusion in a pattern-forming chemical medium")
    p.subject = "Reaction-diffusion medium with a striped supply; fusion as a function of the gap between surfaces; v2.1"
    p.keywords = "reaction-diffusion; pattern-formation; coalescence; pre-registration; unit-of-observation"
    p.comments = ("Data and figures: CC BY 4.0. Every printed number is checked against the aggregates by "
                  "scripts/check_article_030_numbers.py.")


BODY_FONT = "Georgia"
HEAD_FONT = "Cambria"
MONO_FONT = "Consolas"
BODY_SIZE = 10.5
CONTENT_WIDTH_IN = 6.3

DEFAULT_NODE = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources\runtime"
                r"\primary-runtime\dependencies\node\bin\node.exe")
DEFAULT_LO_CLI = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources"
                  r"\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js")


def _shade(cell, colour: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), colour)
    tc_pr.append(shd)


def add_runs(par, text: str, base_size: float = BODY_SIZE) -> None:
    """Inline **bold**, *italic*, `code` and [label](target)."""
    tokens = re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`|\[[^\]]+\]\([^)]+\))", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            r = par.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith("`") and tok.endswith("`"):
            r = par.add_run(tok[1:-1]); r.font.name = MONO_FONT; r.font.size = Pt(base_size - 0.5)
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r = par.add_run(tok[1:-1]); r.italic = True
        elif tok.startswith("[") and "](" in tok:
            label, target = tok[1:-1].split("](", 1)
            r = par.add_run(label); r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79); r.underline = True
        else:
            r = par.add_run(tok)
    for r in par.runs:
        r.font.size = r.font.size or Pt(base_size)


def add_image(doc, alt: str, target: str) -> None:
    path = (ARTICLE.parent / target).resolve()
    if not path.exists():
        raise FileNotFoundError(f"figure not found: {path}")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(CONTENT_WIDTH_IN))


def add_table(doc, rows: list[list[str]]) -> None:
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, row in enumerate(rows):
        cells = t.add_row().cells
        for k, text in enumerate(row):
            par = cells[k].paragraphs[0]
            add_runs(par, text, base_size=BODY_SIZE - 0.5)
            for r in par.runs:
                r.font.size = Pt(BODY_SIZE - 0.5)
                if j == 0:
                    r.bold = True
            if j == 0:
                _shade(cells[k], "EEF3F8")


def render(md: str) -> Document:
    doc = Document()
    set_document_properties(doc)
    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = Pt(BODY_SIZE)
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = sec.bottom_margin = Cm(2.0)

    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i]); i += 1
            i += 1
            p = doc.add_paragraph()
            r = p.add_run("\n".join(block)); r.font.name = MONO_FONT; r.font.size = Pt(8.5)
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2)
            p = doc.add_heading(level=min(level, 4))
            add_runs(p, text, base_size=16 - 1.6 * level)
            for r in p.runs:
                r.font.name = HEAD_FONT
                r.font.size = Pt(max(10.5, 17 - 1.7 * level))
                r.font.color.rgb = RGBColor(0x1B, 0x1B, 0x1B)
            i += 1
            continue
        if stripped.startswith("!["):
            mm = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)", stripped)
            if mm:
                add_image(doc, mm.group(1), mm.group(2))
                i += 1
                continue
        if stripped.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].strip()) <= set("|-: "):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not set("".join(cells)) <= set("-: "):
                    rows.append(cells)
                i += 1
            if rows:
                add_table(doc, rows)
            continue
        if stripped.startswith(">"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            add_runs(p, stripped.lstrip("> ").strip())
            for r in p.runs:
                r.italic = True
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            p = doc.add_paragraph(style="List Number")
            add_runs(p, m.group(2))
            i += 1
            continue
        if stripped.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, stripped[2:])
            i += 1
            continue
        p = doc.add_paragraph()
        add_runs(p, stripped)
        i += 1
    return doc


def convert(docx: Path, pdf: Path, node: str, lo_cli: str) -> None:
    if pdf.exists():
        pdf.unlink()
    result = subprocess.run([node, lo_cli, "convert", "--input", str(docx), "--output", str(pdf)],
                            capture_output=True, text=True)
    payload = (result.stdout or "") + (result.stderr or "")
    try:
        parsed = json.loads(result.stdout.strip().splitlines()[-1]) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        parsed = {}
    if parsed.get("code") not in (None, "ok", "success"):
        raise SystemExit(f"[030-pdf] conversion failed: {payload.strip()}")
    if result.returncode != 0 or not pdf.exists() or pdf.stat().st_size == 0:
        raise SystemExit(f"[030-pdf] conversion produced no PDF: {payload.strip()}")
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise SystemExit("[030-pdf] output does not start with %PDF-")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="render article 030 to PDF")
    ap.add_argument("--article", type=Path, default=ARTICLE)
    ap.add_argument("--out", type=Path, default=PDF)
    ap.add_argument("--node", default=DEFAULT_NODE)
    ap.add_argument("--lo-cli", default=DEFAULT_LO_CLI)
    args = ap.parse_args(argv)

    WORK.mkdir(parents=True, exist_ok=True)
    doc = render(args.article.read_text(encoding="utf-8"))
    doc.save(DOCX)
    convert(DOCX, args.out, args.node, args.lo_cli)
    print(f"[030-pdf] {args.out.relative_to(ROOT)} — {args.out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
