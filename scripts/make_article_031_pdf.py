"""make_article_031_pdf.py — render article 031 as a self-contained PDF for the deposit.

Same renderer as the 030 edition (no pandoc or TeX on the publication machine): the Markdown goes into a
`.docx` with python-docx and is converted with the bundled LibreOffice Kit.

    python scripts/make_article_031_pdf.py
    python scripts/make_article_031_pdf.py --node <node.exe> --lo-cli <libreoffice-kit/cli.js>

Output: `articles/031-directionality-and-inheritance-in-the-pond.pdf` (committed, and picked up by
`scripts/build_article_031_package.py`), intermediate `.docx` under `_exports/031-pdf/` (ignored).

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
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.md"
FIGS = ROOT / "articles" / "031-figures"
PDF = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.pdf"
WORK = ROOT / "_exports" / "031-pdf"
DOCX = WORK / "031-directionality-and-inheritance-in-the-pond.docx"

BODY_FONT = "Georgia"
HEAD_FONT = "Georgia"
MONO_FONT = "Consolas"
BODY_SIZE = 10.5

DEFAULT_NODE = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources\runtime"
                r"\primary-runtime\dependencies\node\bin\node.exe")
DEFAULT_LO_CLI = (r"C:\Users\Admin\AppData\Local\Programs\DeepSeek Harness\resources"
                  r"\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js")


def set_document_properties(doc: Document) -> None:
    """Fill the metadata a reader sees in a PDF viewer."""
    p = doc.core_properties
    p.author = "Ilya Vladimirov"
    p.last_modified_by = "Ilya Vladimirov"
    p.title = "Directionality and inheritance in the pond: what works, where the boundary is"
    p.subject = ("A pond world with resource, death and reproduction; directionality transfers to patchy "
                 "environments but decays with crowding; four independent tests of inherited adaptation "
                 "give null; v1.0")
    p.keywords = ("pond; directionality; taxis; inheritance; lineage selection; boundary of the setup")


def add_runs(p, text: str, base_size: float | None = None) -> None:
    """Inline Markdown: **bold**, *italic*, `code`, [label](link)."""
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            r = p.add_run(text[pos:m.start()])
            if base_size:
                r.font.size = Pt(base_size)
        tok = m.group(0)
        if tok.startswith("**"):
            r = p.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith("`"):
            r = p.add_run(tok[1:-1]); r.font.name = MONO_FONT
        elif tok.startswith("["):
            label = tok[1:tok.index("]")]
            r = p.add_run(label); r.italic = True
        else:
            r = p.add_run(tok[1:-1]); r.italic = True
        if base_size:
            r.font.size = Pt(base_size)
        pos = m.end()
    if pos < len(text):
        r = p.add_run(text[pos:])
        if base_size:
            r.font.size = Pt(base_size)


def add_image(doc: Document, alt: str, rel: str) -> None:
    path = (ARTICLE.parent / rel).resolve()
    if not path.exists():
        p = doc.add_paragraph()
        add_runs(p, f"[missing figure: {rel}]")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(6.3))
    if alt:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(alt)
        r.italic = True
        r.font.size = Pt(8.5)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=ncol)
    table.style = "Light Grid Accent 1"
    for k, row in enumerate(rows):
        cells = table.add_row().cells
        for j in range(ncol):
            txt = row[j] if j < len(row) else ""
            para = cells[j].paragraphs[0]
            add_runs(para, txt, base_size=8.5)
            if k == 0:
                for r in para.runs:
                    r.bold = True


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
        stripped = lines[i].strip()
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
    size = args.out.stat().st_size
    print(f"[031-pdf] wrote {args.out} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
