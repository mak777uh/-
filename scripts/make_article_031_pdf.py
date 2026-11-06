"""make_article_031_pdf.py — render article 031 as a self-contained PDF for the deposit.

Same pipeline as the 029 and 030 editions (no pandoc or TeX on the publication machine): the Markdown goes into a
`.docx` with python-docx and is converted with the bundled LibreOffice Kit.

    python scripts/make_article_031_pdf.py
    python scripts/make_article_031_pdf.py --node <node.exe> --lo-cli <libreoffice-kit/cli.js>

Output: `articles/031-directionality-and-inheritance-in-the-pond.pdf` (committed, and picked up by
`scripts/build_article_031_package.py`), intermediate `.docx` under `_exports/031-pdf/` (ignored).

Typesetting, chosen for reading on screen and on paper rather than for a web page:

- serif body (Georgia) at 10.5 pt with 1.25 line spacing, justified, hyphenated, widows and orphans kept together;
- headings in a distinct serif (Cambria) with space above, never orphaned at the foot of a page;
- a figure and its caption are one block: the image keeps with its caption paragraph, the caption is set 8.5 pt italic
  in a narrower measure and never starts a page on its own;
- tables are compact (8.5 pt), header row shaded and repeated when a table breaks across pages;
- running head with the short title on the left and the section on the right, page numbers at the foot;
- the title block is set apart: title, author line, DOI and licence, then the abstract in a narrower measure.

The renderer understands only the subset of Markdown this article uses: headings, paragraphs, pipe tables, fenced code,
block quotes, bullet and numbered items, images and the inline `**bold**` / `*italic*` / `` `code` `` / `[label](link)`
forms. Anything else is emitted as literal text rather than silently dropped.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.md"
PDF = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.pdf"
WORK = ROOT / "_exports" / "031-pdf"
DOCX = WORK / "031-directionality-and-inheritance-in-the-pond.docx"

BODY_FONT = "Georgia"
HEAD_FONT = "Cambria"
MONO_FONT = "Consolas"
BODY_SIZE = 10.5
CONTENT_WIDTH_IN = 6.3
INK = RGBColor(0x1B, 0x1B, 0x1B)
LINK = RGBColor(0x1F, 0x4E, 0x79)
RULE = RGBColor(0x8A, 0x8A, 0x8A)

DEFAULT_NODE = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources\runtime"
                r"\primary-runtime\dependencies\node\bin\node.exe")
DEFAULT_LO_CLI = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources"
                  r"\.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js")
DEFAULT_LO_CLI = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources"
                  r"\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js")


def set_document_properties(doc: Document) -> None:
    """Fill the metadata a reader sees in a PDF viewer (python-docx otherwise signs the file with its own name)."""
    p = doc.core_properties
    p.author = "Ilya Vladimirov"
    p.last_modified_by = "Ilya Vladimirov"
    p.title = "Directionality and inheritance in the pond: what works, where the boundary is"
    p.subject = ("A pond world with resource, death and reproduction; directionality transfers to patchy "
                 "environments but decays with crowding; four tests of inherited adaptation give null; v2.0")
    p.keywords = "pond; directionality; taxis; inheritance; lineage-selection; crowding; boundary-of-the-setup"
    p.comments = ("Data and figures: CC BY 4.0. Every printed number is checked against the artifacts by "
                  "scripts/check_article_031_numbers.py.")


def _shade(cell, colour: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), colour)
    tc_pr.append(shd)


def _repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def _field(par, instruction: str, placeholder: str = "") -> None:
    """A Word field (page number, section title) that LibreOffice resolves when it converts."""
    run = par.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    for node in (fld_begin, instr, fld_sep, text, fld_end):
        run._r.append(node)


def add_runs(par, text: str, base_size: float = BODY_SIZE) -> None:
    """Inline **bold**, *italic*, `code` and [label](target)."""
    # bold may span a line break or a sentence, so it is matched non-greedily across the whole paragraph;
    # italic and code stay single-line to keep "2*3" and "a*b" out of the emphasis path.
    tokens = re.split(r"(\*\*.+?\*\*|(?<!\*)\*[^*\n]+?\*(?!\*)|`[^`]+?`|\[[^\]]+\]\([^)]+\))", text, flags=re.S)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            r = par.add_run(tok[2:-2])
            r.bold = True
        elif tok.startswith("`") and tok.endswith("`"):
            r = par.add_run(tok[1:-1])
            r.font.name = MONO_FONT
            r.font.size = Pt(base_size - 0.5)
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r = par.add_run(tok[1:-1])
            r.italic = True
        elif tok.startswith("[") and "](" in tok:
            label, target = tok[1:-1].split("](", 1)
            r = par.add_run(label)
            r.font.color.rgb = LINK
            r.underline = True
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
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(CONTENT_WIDTH_IN))


def add_caption(doc, text: str) -> None:
    """A figure caption: 8.5 pt italic, narrower measure, starts on the same page as the image."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.right_indent = Cm(0.8)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.1
    add_runs(p, text, base_size=8.5)
    for r in p.runs:
        r.italic = True


def add_table(doc, rows: list[list[str]]) -> None:
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    for j, row in enumerate(rows):
        cells = t.add_row().cells
        for k, text in enumerate(row):
            par = cells[k].paragraphs[0]
            par.paragraph_format.space_before = Pt(1)
            par.paragraph_format.space_after = Pt(1)
            add_runs(par, text, base_size=BODY_SIZE - 2)
            for r in par.runs:
                r.font.size = Pt(BODY_SIZE - 2)
                if j == 0:
                    r.bold = True
            if j == 0:
                _shade(cells[k], "EEF3F8")
    _repeat_header(t.rows[0])
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(6)
    spacer.paragraph_format.line_spacing = 0.6


def _style_document(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = Pt(BODY_SIZE)
    style.font.color.rgb = INK
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.25
    pf.space_after = Pt(6)
    pf.widow_control = True
    # LibreOffice honours the document default language for hyphenation; the text is English.
    lang = OxmlElement("w:lang")
    lang.set(qn("w:val"), "en-GB")
    style.element.get_or_add_rPr().append(lang)

    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.header_distance = Cm(1.1)
    sec.footer_distance = Cm(1.0)
    sec.different_first_page_header_footer = True

    header = sec.header.paragraphs[0]
    header.text = ""
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("Directionality and inheritance in the pond  ·  031")
    run.font.size = Pt(8)
    run.font.name = HEAD_FONT
    run.font.color.rgb = RULE

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _field(footer, "PAGE", "1")
    for r in footer.runs:
        r.font.size = Pt(8.5)
        r.font.name = HEAD_FONT
        r.font.color.rgb = RULE


def render(md: str) -> Document:
    doc = Document()
    set_document_properties(doc)
    _style_document(doc)

    lines = md.split("\n")
    i = 0
    in_abstract = False
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            r = p.add_run("\n".join(block))
            r.font.name = MONO_FONT
            r.font.size = Pt(8.5)
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2)
            in_abstract = text.strip().lower().startswith("abstract")
            p = doc.add_heading(level=min(level, 4))
            p.paragraph_format.keep_with_next = True
            add_runs(p, text, base_size=16 - 1.6 * level)
            for r in p.runs:
                r.font.name = HEAD_FONT
                r.font.size = Pt({1: 19, 2: 13.5, 3: 11.5, 4: 10.5}[min(level, 4)])
                r.font.color.rgb = INK
                r.bold = True
            p.paragraph_format.space_before = Pt({1: 0, 2: 16, 3: 12, 4: 10}[min(level, 4)])
            p.paragraph_format.space_after = Pt({1: 6, 2: 6, 3: 4, 4: 3}[min(level, 4)])
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
        # soft-wrapped Markdown lines are one paragraph: join them before inline parsing, so emphasis and links that
        # straddle a line break are still recognised (the article is hard-wrapped at 120 columns).
        block = [stripped]
        j = i + 1
        while j < len(lines):
            nxt = lines[j].strip()
            if not nxt or nxt.startswith(("#", "|", "![", "```", ">")) or re.match(r"^(\d+\.|-)\s", nxt):
                break
            block.append(nxt)
            j += 1
        stripped = " ".join(block)
        i = j - 1
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if stripped.startswith("**Figure "):
            add_caption(doc, stripped)
            i += 1
            continue
        if in_abstract:
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.right_indent = Cm(0.8)
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
        raise SystemExit(f"[031-pdf] conversion failed: {payload.strip()}")
    if result.returncode != 0 or not pdf.exists() or pdf.stat().st_size == 0:
        raise SystemExit(f"[031-pdf] conversion produced no PDF: {payload.strip()}")
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise SystemExit("[031-pdf] output does not start with %PDF-")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="render article 031 to PDF")
    ap.add_argument("--article", type=Path, default=ARTICLE)
    ap.add_argument("--out", type=Path, default=PDF)
    ap.add_argument("--node", default=DEFAULT_NODE)
    ap.add_argument("--lo-cli", default=DEFAULT_LO_CLI)
    args = ap.parse_args(argv)

    WORK.mkdir(parents=True, exist_ok=True)
    doc = render(args.article.read_text(encoding="utf-8"))
    doc.save(DOCX)
    convert(DOCX, args.out, args.node, args.lo_cli)
    print(f"[031-pdf] {args.out.relative_to(ROOT)} — {args.out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
