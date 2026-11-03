"""make_article_029_pdf.py — render article 029 as a self-contained PDF for the deposit.

The deposit ships the article both as Markdown and as a PDF, so that the reader does not have to
convert anything. There is no pandoc or TeX on the publication machine, so the Markdown is rendered
into a `.docx` with python-docx and converted with the bundled LibreOffice Kit:

    python scripts/make_article_029_pdf.py
    python scripts/make_article_029_pdf.py --node <node.exe> --lo-cli <libreoffice-kit/cli.js>

Output: `articles/029-figures/029-lineages-in-a-pattern-forming-field.pdf` (committed, and picked up
by `scripts/build_article_029_package.py`), intermediate `.docx` under `_exports/029-pdf/` (ignored).

The renderer understands only the subset of Markdown the article uses: headings, paragraphs, pipe
tables, fenced code, block quotes (the definition box), bullet and numbered items, images and the
inline `**bold**` / `*italic*` / `` `code` `` / `[label](link)` forms. Anything else is emitted as
literal text rather than silently dropped.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "029-lineages-in-a-pattern-forming-field.md"
FIGS = ROOT / "articles" / "029-figures"
PDF = ROOT / "articles" / "029-lineages-in-a-pattern-forming-field.pdf"
WORK = ROOT / "_exports" / "029-pdf"
DOCX = WORK / "029-lineages-in-a-pattern-forming-field.docx"

BODY_FONT = "Georgia"
HEAD_FONT = "Cambria"
MONO_FONT = "Consolas"
BODY_SIZE = 10.5
CONTENT_WIDTH_IN = 6.3

DEFAULT_NODE = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources\runtime"
                r"\primary-runtime\dependencies\node\bin\node.exe")
DEFAULT_LO_CLI = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources"
                  r"\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js")

INLINE = re.compile(
    r"(\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`|\[[^\]]+\]\([^)]*\))"
)
TABLE_SEP = re.compile(r"^:?-{2,}:?$")


# --------------------------------------------------------------------------- document skeleton

def new_document() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)
    section.top_margin = Cm(2.3)
    section.bottom_margin = Cm(2.3)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_SIZE)
    normal.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.12
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), BODY_FONT)
    return doc


def style_heading(paragraph, size: float, *, space_before: float, bold: bool = True,
                  color=(0x11, 0x11, 0x11), keep_with_next: bool = True) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(space_before)
    fmt.space_after = Pt(6)
    fmt.keep_with_next = keep_with_next
    for run in paragraph.runs:
        run.font.name = HEAD_FONT
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = RGBColor(*color)


# --------------------------------------------------------------------------- inline markup

def add_rich(paragraph, text: str, *, size: float | None = None, bold: bool = False,
             italic: bool = False, font: str | None = None) -> None:
    """Split inline markup into runs, keeping bold/italic/code/link labels."""
    for piece in INLINE.split(text):
        if not piece:
            continue
        run = paragraph.add_run()
        run.bold = bold
        run.italic = italic
        if size:
            run.font.size = Pt(size)
        if font:
            run.font.name = font
        if piece.startswith("**") and piece.endswith("**") and len(piece) > 4:
            run.text = piece[2:-2]
            run.bold = True
        elif piece.startswith("`") and piece.endswith("`") and len(piece) > 2:
            run.text = piece[1:-1]
            run.font.name = MONO_FONT
            run.font.size = Pt((size or BODY_SIZE) - 1.2)
            run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            run.text = piece[1:-1]
            run.italic = not italic
        elif piece.startswith("["):
            label, _, target = piece[1:-1].partition("](")
            label = label.strip("`")
            run.text = label
            if target and not target.endswith((".png", ".pdf")):
                run.font.color.rgb = RGBColor(0x2B, 0x4C, 0x7E)
                run.underline = True
        else:
            run.text = piece


def shade(paragraph_or_cell, hex_fill: str) -> None:
    element = paragraph_or_cell._p if hasattr(paragraph_or_cell, "_p") else paragraph_or_cell._tc
    pr = element.get_or_add_pPr() if hasattr(element, "get_or_add_pPr") else element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    pr.append(shd)


def border(cell, color: str = "BFBFBF") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tc_pr.append(borders)


# --------------------------------------------------------------------------- block writers

def add_body_paragraph(doc, text: str, *, first: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_rich(p, text)
    if first:
        p.paragraph_format.space_before = Pt(2)


def add_bullet(doc, text: str, marker: str = "•", indent_cm: float = 0.55) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(indent_cm)
    p.paragraph_format.first_line_indent = Cm(-0.45)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(marker + "\t")
    add_rich(p, text)


def add_table(doc, rows: list[list[str]]) -> None:
    header, body = rows[0], rows[1:]
    table = doc.add_table(rows=1 + len(body), cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for column, text in enumerate(header):
        cell = table.rows[0].cells[column]
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        add_rich(p, text, size=9, bold=True)
        shade(cell, "EDEDED")
    for r, row in enumerate(body, start=1):
        for column in range(len(header)):
            text = row[column] if column < len(row) else ""
            cell = table.rows[r].cells[column]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            add_rich(p, text, size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_code(doc, lines: list[str]) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    for index, line in enumerate(lines):
        run = p.add_run(line)
        run.font.name = MONO_FONT
        run.font.size = Pt(9)
        if index < len(lines) - 1:
            run.add_break()
    shade(p, "F4F4F4")


def add_box(doc, lines: list[str]) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    border(cell)
    shade(cell, "F7F7F2")
    cell.text = ""
    first = True
    for line in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.15)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_rich(p, line, size=9.3)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_image(doc, alt: str, target: str) -> None:
    path = (ARTICLE.parent / target).resolve()
    if not path.exists():
        raise FileNotFoundError(f"figure not found: {path}")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(CONTENT_WIDTH_IN))


# --------------------------------------------------------------------------- markdown driver

def document_properties(doc: Document) -> None:
    """Fill the metadata a reader sees in a PDF viewer (python-docx defaults to its own name)."""
    props = doc.core_properties
    props.author = "Ilya Vladimirov"
    props.last_modified_by = "Ilya Vladimirov"
    props.title = "How lineages begin and end in a pattern-forming chemical medium"
    props.subject = "Lineages in a pattern-forming chemical medium (Gray-Scott), v2.0"
    props.keywords = "reaction-diffusion; lineage tracking; heredity; merger; Gray-Scott"
    props.comments = ("Data and figures: CC BY 4.0. Every printed number is checked against the aggregates by "
                      "scripts/check_article_029_numbers.py.")


def render(markdown: str) -> Document:
    doc = new_document()
    document_properties(doc)
    lines = markdown.split("\n")
    i = 0
    first_paragraph = True
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            block: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i].rstrip())
                i += 1
            i += 1
            add_code(doc, block)
            first_paragraph = False
            continue

        if stripped.startswith("|"):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(TABLE_SEP.match(c) for c in cells):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            first_paragraph = False
            continue

        if stripped.startswith("![") and "](" in stripped:
            match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
            if match:
                add_image(doc, match.group(1), match.group(2))
                first_paragraph = False
                i += 1
                continue

        if stripped.startswith(">"):
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip().lstrip(">").strip())
                i += 1
            add_box(doc, block)
            first_paragraph = False
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading:
            level, text = len(heading.group(1)), heading.group(2)
            if level == 1:
                p = doc.add_paragraph(text)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                style_heading(p, 19, space_before=0)
                p.paragraph_format.space_after = Pt(10)
            elif level == 2:
                p = doc.add_paragraph(text)
                style_heading(p, 14, space_before=14)
            else:
                p = doc.add_paragraph(text)
                style_heading(p, 11.5, space_before=10, color=(0x22, 0x22, 0x22))
            first_paragraph = True
            i += 1
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            add_bullet(doc, numbered.group(2), marker=numbered.group(1) + ".", indent_cm=0.75)
            first_paragraph = False
            i += 1
            continue

        if stripped.startswith("- "):
            add_bullet(doc, stripped[2:])
            first_paragraph = False
            i += 1
            continue

        paragraph: list[str] = []
        while i < len(lines):
            current = lines[i].strip()
            if (not current or current.startswith(("#", "|", ">", "```", "- ", "!["))
                    or re.match(r"^\d+\.\s", current)):
                break
            paragraph.append(current)
            i += 1
        add_body_paragraph(doc, " ".join(paragraph), first=first_paragraph)
        first_paragraph = False
    return doc


# --------------------------------------------------------------------------- conversion

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
        raise SystemExit(f"[029-pdf] conversion failed: {payload.strip()}")
    if result.returncode != 0 or not pdf.exists() or pdf.stat().st_size == 0:
        raise SystemExit(f"[029-pdf] conversion produced no PDF: {payload.strip()}")
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise SystemExit("[029-pdf] output does not start with %PDF-")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="render article 029 to PDF")
    ap.add_argument("--article", type=Path, default=ARTICLE)
    ap.add_argument("--out", type=Path, default=PDF)
    ap.add_argument("--node", default=DEFAULT_NODE)
    ap.add_argument("--lo-cli", default=DEFAULT_LO_CLI)
    args = ap.parse_args(argv)

    WORK.mkdir(parents=True, exist_ok=True)
    doc = render(args.article.read_text(encoding="utf-8"))
    doc.save(DOCX)
    convert(DOCX, args.out, args.node, args.lo_cli)
    print(f"[029-pdf] {args.out.relative_to(ROOT)} — {args.out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
