"""build_article_029_package.py — assemble the deposit package for article 029.

The package is written outside the repository (`_exports/029-lineages/`), because an external deposit is not a
repository artefact; the repository keeps the article, the figures, the derived tables and this script, so the package
is reproducible from a clean checkout.

Contents: the article, the five figures (PNG for reading, PDF for typesetting), the aggregates the article cites, the
derived tables, a dataset README, the licence, a Zenodo metadata record, a sha256 manifest, and the publication
instructions for the agent that will upload it. The whole directory is also written as a single zip next to it.

Run:
    python scripts/build_article_029_package.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FIGS = ROOT / "articles" / "029-figures"
ARTICLE = ROOT / "articles" / "029-lineages-in-a-pattern-forming-field.md"
INSTRUCTIONS = ROOT / "articles" / "029-publication-instructions.md"
OUT = ROOT / "_exports" / "029-lineages"
ZIP = ROOT / "_exports" / "029-lineages-v2.0.zip"

# Every aggregate a number in the article comes from.
AGGREGATES = [
    "l1_field_x113_depth.json",
    "l1_field_x113c_depth_rate.json",
    "l1_field_x114_window.json",
    "l1_field_x115_persistence.json",
    "l1_field_x116_matched.json",
    "l1_field_x119_model.json",
    "l1_field_x125c_ties.json",
    "l1_field_x126_third_cell.json",
    "l1_field_x128b_local.json",
    "l1_field_x130_remerge.json",
    "l1_field_x131_worlds.json",
    "l1_field_x132_power.json",
    "l1_field_x134_mixing.json",
    "l1_field_x136_wall.json",
    "l1_field_x138_scale.json",
    "l1_field_x140_gap_rule.json",
    "l1_field_x142_coalescence.json",
    "l1_field_x145_lone_disc.json",
    "l1_field_x147_radius45.json",
    "l1_field_x150_radius6.json",
    "l1_field_x151_radius525.json",
    "l1_field_x153_halfcell.json",
    "l1_field_x154_mixing.json",
    "l1_field_x155_heredity.json",
    "l1_field_x96c_pilot.json",
    "l1_field_x96d_orientation.json",
    "l1_field_x110b_gamma_cell.json",
]

README = """# Dataset — How lineages begin and end in a pattern-forming chemical medium

This directory is the deposit for article 029 (`029-lineages-in-a-pattern-forming-field.md`). It contains
aggregates, not raw fields: the run-level JSON artifacts of the field line are several megabytes each and live in the
public repository, where they are addressable by name.

## What is here

| path | what it is |
|---|---|
| `029-lineages-in-a-pattern-forming-field.md` | the article (Markdown, English) |
| `029-lineages-in-a-pattern-forming-field.pdf` | the same article as a PDF, with all five figures embedded |
| `figures/` | Figures 1-5 as PNG (reading) and PDF (typesetting) |
| `data/aggregates/` | the twenty-seven `l1_field_*.json` aggregates the article cites; each carries its own `command`, `prereg` and `verdict` fields |
| `data/derived/tables.json` | every number printed in the article, with the aggregate it came from |
| `data/derived/*.csv` | the same values as flat tables (the edge curve, the three habitats, the heredity readouts) |
| `zenodo.json` | metadata record for the deposit |
| `MANIFEST.sha256` | checksums of every file above |
| `PUBLISHING.md` | step-by-step instructions for the publishing agent |

## Provenance

All numbers are computed from the aggregates by `scripts/make_article_029_figures.py` in the repository, and every one
of them is checked against the article text by `scripts/check_article_029_numbers.py --ci`. The aggregates in turn are
built from per-run artifacts whose command lines are recorded in their own `command` field, and the seeds are listed in
each aggregate's `runs` or `seeds` block.

## Units and conventions

Lengths are lattice cells (one cell = 1/96 of the domain side); time is steps of the explicit integrator at `dt` = 1.0;
`F` is the inflow of the Gray-Scott kinetics; `s` is a dimensionless composition in the neighbourhood of 1.0; the
"surface gap" between two bodies is `centre separation - 2 * sqrt(area / pi)`, which is the quantity the mixing-length
claim is stated in.

## Licence

Data, figures and article text: CC BY 4.0.
"""

LICENSE = """Creative Commons Attribution 4.0 International Public License

Copyright (c) 2026 Morphogenesis laboratory

You are free to share (copy and redistribute the material in any medium or format) and to adapt (remix, transform, and
build upon the material for any purpose, even commercially), under the following terms: Attribution — you must give
appropriate credit, provide a link to the licence, and indicate if changes were made. No additional restrictions — you
may not apply legal terms or technological measures that legally restrict others from doing anything the licence
permits.

Full text: https://creativecommons.org/licenses/by/4.0/legalcode
"""


REPO_URL = "https://github.com/mak777uh/-/blob/main"

# The package has its own layout, so the article's repository-relative links are rewritten: figures and aggregates
# become local paths, everything that stays in the repository becomes an absolute URL.
LINK_REWRITES = [
    ("029-figures/tables.json", "data/derived/tables.json"),
    ("029-figures/tables.csv", "data/derived/tables.csv"),
    ("029-figures/table-", "data/derived/table-"),
    ("029-figures/", "figures/"),
    ("../morphogenesis/experiments/E09_pond/", "data/aggregates/"),
    ("../morphogenesis/experiments/L1_field/", f"{REPO_URL}/morphogenesis/experiments/L1_field/"),
    ("../reports/", f"{REPO_URL}/reports/"),
    ("../scripts/", f"{REPO_URL}/scripts/"),
    ("../manuscript/", f"{REPO_URL}/manuscript/"),
    ("../docs/", f"{REPO_URL}/docs/"),
    ("../README.md", f"{REPO_URL}/README.md"),
]


def rewrite_links(text: str) -> str:
    for old, new in LINK_REWRITES:
        text = text.replace(f"]({old}", f"]({new}")
    # The labels of the two front-matter links name a repository directory that does not exist in the
    # package; print the packaged path instead, so the PDF does not point the reader at `029-figures/`.
    text = text.replace("`029-figures/tables.json`", "`data/derived/tables.json`")
    text = text.replace("`029-figures/`", "`figures/`")
    return text


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "figures").mkdir(parents=True)
    (OUT / "data" / "aggregates").mkdir(parents=True)
    (OUT / "data" / "derived").mkdir()

    (OUT / ARTICLE.name).write_text(rewrite_links(ARTICLE.read_text(encoding="utf-8")),
                                    encoding="utf-8", newline="\n")
    for ext in ("png", "pdf"):
        for fig in sorted(FIGS.glob(f"*.{ext}")):
            shutil.copy2(fig, OUT / "figures" / fig.name)

    copied = 0
    for name in AGGREGATES:
        src = POND / name
        if not src.exists():
            print(f"[029-package] ВНИМАНИЕ: нет агрегата {name}")
            continue
        shutil.copy2(src, OUT / "data" / "aggregates" / name)
        copied += 1

    for name in ("tables.json", "tables.csv", "table-edge.csv", "table-habitats.csv", "table-heredity.csv"):
        shutil.copy2(FIGS / name, OUT / "data" / "derived" / name)

    pdf_src = ROOT / "articles" / "029-lineages-in-a-pattern-forming-field.pdf"
    pdf_present = pdf_src.exists()
    if pdf_present:
        shutil.copy2(pdf_src, OUT / pdf_src.name)
    else:
        print("[029-package] ВНИМАНИЕ: нет PDF статьи — депозит соберётся без него")

    zenodo = {
        "title": "How lineages begin and end in a pattern-forming chemical medium",
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": (
            "<p>Lineages in a pattern-forming medium without replicators: the Gray-Scott reaction-diffusion system in "
            "three habitats. Four measured results. (i) The medium has a mixing length: two lineages merge below a "
            "surface gap of 9 +/- 1 cells, independent of body size. (ii) A fusion is a merger, not a birth: both "
            "lineages end on the same step and one body appears under a new identifier. (iii) The outcome is a "
            "whole-cell step while the dissolution time spreads before it. (iv) A lineage's end is mostly the loss of "
            "its name rather than of its cells, and the habitat that maximises generations is not the one where a "
            "lineage survives. The heredity coefficient is measured rather than asserted: the daughter-on-parent slope "
            "is 0.9837 [0.9680, 1.0002] and 0.9931 [0.9756, 1.0103], the residual is the mutation rule's own sigma to "
            "one per cent, and with the mutation ablated the trait has no variance at all.</p>"
        ),
        "creators": [{"name": "Morphogenesis laboratory"}],
        "keywords": ["reaction-diffusion", "lineage tracking", "heredity", "merger", "identity",
                     "negative result", "Gray-Scott"],
        "license": "CC-BY-4.0",
        "access_right": "open",
        "language": "eng",
        "version": "2.0",
        "publication_date": "2026-11-04",
        "related_identifiers": [
            {"identifier": "https://github.com/mak777uh/-", "relation": "isSupplementTo", "scheme": "url"},
        ],
        "notes": "Derived tables: data/derived/tables.json lists every printed number with the aggregate it came from.",
    }
    (OUT / "zenodo.json").write_text(json.dumps(zenodo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
                                     newline="\n")
    readme = README
    if not pdf_present:
        readme = readme.replace("| `029-lineages-in-a-pattern-forming-field.pdf`"
                                " | the same article as a PDF, with all five figures embedded |\n", "")
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    (OUT / "LICENSE").write_text(LICENSE, encoding="utf-8", newline="\n")
    if INSTRUCTIONS.exists():
        shutil.copy2(INSTRUCTIONS, OUT / "PUBLISHING.md")
    else:
        print("[029-package] ВНИМАНИЕ: нет файла инструкций", INSTRUCTIONS)

    manifest_lines = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        manifest_lines.append(f"{sha256(path)}  {path.relative_to(OUT).as_posix()}")
    (OUT / "MANIFEST.sha256").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8", newline="\n")

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
            zf.write(path, arcname=f"029-lineages/{path.relative_to(OUT).as_posix()}")

    size_mb = ZIP.stat().st_size / (1024 * 1024)
    print(f"[029-package] агрегатов: {copied} из {len(AGGREGATES)}; файлов: {len(manifest_lines)}")
    print(f"[029-package] {OUT.relative_to(ROOT)} и {ZIP.relative_to(ROOT)} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
