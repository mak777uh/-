"""build_article_031_package.py — assemble the deposit package for article 031.

The repository keeps the article, the figures, the verifier and this script; the package puts them into one archive
with everything a depositor needs and no more: the article (Markdown + PDF), the three figures (PNG for reading, PDF
for typesetting), the committed artifacts the article cites, the machine check of every printed number, a dataset
README, the licence, a Zenodo metadata record, a sha256 manifest and the publication brief.

    python scripts/build_article_031_package.py
    python scripts/build_article_031_package.py --no-zip     # leave the directory for inspection

Output: `_exports/031-directionality-and-inheritance/` and `_exports/031-directionality-and-inheritance-v2.0.zip`
(both ignored by git).

One author is set (Vladimirov, Ilya); the licence is CC BY 4.0, the standing default. Nothing is uploaded by this
script, and the package must not be uploaded until the author says so in writing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.md"
PDF = ROOT / "articles" / "031-directionality-and-inheritance-in-the-pond.pdf"
FIGDIR = ROOT / "articles" / "031-figures"
VERIFIER = ROOT / "scripts" / "check_article_031_numbers.py"
BRIEF = ROOT / "articles" / "031-publishing-instructions.md"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "_exports" / "031-directionality-and-inheritance"
ZIP = ROOT / "_exports" / "031-directionality-and-inheritance-v2.0.zip"
STEM = "031-directionality-and-inheritance-in-the-pond"
VERSION = "v2.0"
DOI_PREVIOUS = "10.5281/zenodo.23970711"

# Every artifact the article's numbers come from (checked by check_article_031_numbers.py).
AGGREGATES = [
    "s1_a2_ci_baseline.json",
    "s1_a2_ci_predgrad.json",
    "s1_a2_ci_predrand.json",
    "s2_b1_gradpos_flip200.json",
    "s2_b2_tumble_p06_flip200.json",
    "s4_baseline_flip200_current.json",
    "s4_localres_flip200_current.json",
    "s4_randdir_flip200_current.json",
    "s4_gradpos_sanity_flip200.json",
    "s6_c3_double_baseline.json",
    "s6_c3_double_localres.json",
    "s6_c3_double_randdir.json",
    "s7_c3b_baseline_ABC.json",
    "s7_c3b_localres_ABC.json",
    "s9_c2_full.json",
    "s10_c2b_full.json",
    "s11_patches_cheap.json",
    "s12_d2_full.json",
    "s13_d3_full.json",
    "s14_d4_full.json",
    "s15_e1_full.json",
    "s16_e1b_full.json",
    "s18_c4_full.json",
]

LICENCE = """CC BY 4.0

Copyright (c) 2026 Ilya Vladimirov

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

DATASET_README = """# Dataset for article 031 — directionality works but does not scale, and inherited adaptation does not appear, in a resource-limited pond world

This package contains the article, its figures, and the machine-readable artifacts behind every number in it.

## What is here

| path | what it is |
|---|---|
| `{stem}.md` | the article (Markdown, English) |
| `{stem}.pdf` | the article as a PDF, three figures embedded |
| `figures/` | the three figures, PNG (reading) and PDF (typesetting) |
| `artifacts/` | the JSON aggregates the article's numbers come from, verbatim from the repository |
| `check_article_031_numbers.py` | the machine check: re-derives 50 printed numbers and compares them with the text |
| `references.md` | the three context references, with the identifier each was checked against |
| `LICENSE` | CC BY 4.0 |
| `zenodo.json` | deposit metadata |
| `MANIFEST.sha256` | sha256 of every file above |
| `PUBLISHING.md` | the brief for whoever performs the deposit |

## What the artifacts are

Each `*.json` under `artifacts/` is one experiment series: a list of runs (`rows`), one row per seed and arm, each with
per-window measurements (100 steps per window, 600 steps per run, 3 seeds). The article's numbers are means over seeds
and windows. Two families:

- `s1_*.json`, `s2_*.json`, `s4_*.json` — the directionality mechanism on a gradient environment;
- `s6_*.json` … `s18_*.json` — the inheritance tests (S6, S7, S9, S10, S18) and the patchy-environment transfer
  (S11–S16), including the runs the article names as invalid by construction.

## How to check the numbers

```bash
python check_article_031_numbers.py --ci     # 0 failures out of 50 checks
```

The script resolves the artifacts next to itself (`artifacts/`), so it runs unchanged inside this package. It checks
both directions: every value it recomputes must appear verbatim in the article, and the article may not state a value
the artifacts do not produce.

## What is NOT here

- The world engine itself (`morphogenesis/world/`) — it lives in the repository; the artifacts are its output.
- Raw per-cell fields: the aggregates keep per-window summaries, not the 32x32 grids.
- Checkpoints (`.pt` files) — the project does not publish weights in the deposit.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build the deposit package for article 031")
    ap.add_argument("--no-zip", action="store_true", help="leave the directory, do not zip")
    args = ap.parse_args(argv)

    missing = [p for p in (ART, PDF, BRIEF, VERIFIER) if not p.exists()]
    if missing:
        raise SystemExit(f"[031-package] missing required files: {[str(p) for p in missing]}\n"
                         "Run scripts/make_article_031_pdf.py first.")
    if not FIGDIR.exists():
        raise SystemExit("[031-package] figures directory missing — run scripts/make_article_031_figures.py")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "figures").mkdir(parents=True)
    (OUT / "artifacts").mkdir(parents=True)

    # The package has its own layout: figures live at figures/, the verifier sits beside the article at the root.
    article = ART.read_text(encoding="utf-8")
    article = article.replace("](031-figures/", "](figures/")
    article = article.replace("](../scripts/check_article_031_numbers.py)", "](check_article_031_numbers.py)")
    (OUT / f"{STEM}.md").write_text(article, encoding="utf-8", newline="\n")
    shutil.copy2(PDF, OUT / f"{STEM}.pdf")
    shutil.copy2(BRIEF, OUT / "PUBLISHING.md")
    shutil.copy2(VERIFIER, OUT / "check_article_031_numbers.py")
    for fig in sorted(FIGDIR.iterdir()):
        if fig.suffix.lower() in (".png", ".pdf"):
            shutil.copy2(fig, OUT / "figures" / fig.name)

    copied, absent = 0, []
    for name in AGGREGATES:
        src = POND / name
        if src.exists():
            shutil.copy2(src, OUT / "artifacts" / name)
            copied += 1
        else:
            absent.append(name)

    (OUT / "README.md").write_text(DATASET_README.format(stem=STEM), encoding="utf-8")
    (OUT / "LICENSE").write_text(LICENCE, encoding="utf-8")

    references = """# References cited in article 031

Eight works are cited. Each line gives the identifier its existence was checked against and the reading status in the
project's corpus (`read` = read end to end, `partial` = abstract or bibliographic record only).

1. Mathew A.M., Sasidevan V. *Modelling competition for space: Emergent inefficiency and inequality due to spatial
   self-organization among a group of crowd-avoiding agents.* arXiv:2407.21537 (2024). Verified: arXiv identifier.
   Status: partial. Preprint; the journal overview below supports the frame it introduces.
2. *Food Income and the Evolution of Forager Mobility.* Scientific Reports 9 (2019), s41598-019-42006-2.
   Verified: DOI 10.1038/s41598-019-42006-2. Status: partial.
3. Rowell J.T. *The limitation of species range: a consequence of searching along resource gradients.*
   PMC2760341 (2009). Verified: PubMed Central identifier. Status: partial.
4. Zhang B., DeAngelis D.L. *An overview of agent-based models in plant biology and ecology.* Annals of Botany 126 (2020).
   Verified: DOI 10.1093/aob/mcaa043. Status: read.
5. Tyler J.A., Hargrove W.W. *Predicting Spatial Distribution of Foragers over Large Resource Landscapes: A Modeling
   Analysis of the Ideal Free Distribution.* Oikos 80 (1997). Verified: DOI 10.2307/3546022. Status: partial.
6. Xu L., Vision T.J., Servedio M.R. *Evolutionary rescue under demographic and environmental stochasticity.*
   Journal of Evolutionary Biology 36 (2023). Verified: DOI 10.1111/jeb.14224. Status: read.
7. Vriend S.J.G., Engen S., Gustafsson L. *Quantitative analyses of stochastic influences on the response to phenotypic
   selection.* Evolution (2025). Verified: DOI 10.1093/evolut/qpaf108. Status: read.
8. Ponzi E., Keller L.F., Bonnet T. *Heritability, selection, and the response to selection in the presence of phenotypic
   measurement error.* Evolution 72 (2018). Verified: DOI 10.1111/evo.13573. Status: read.

The article also cites its own previous steps, *How lineages begin and end in a pattern-forming chemical medium*
(DOI 10.5281/zenodo.23933440) and *The gap between surfaces, not the body size, switches fusion*
(DOI 10.5281/zenodo.23970711).

These works are not our world: the agent-based review and the Ideal Free Distribution concern plants and foragers, and the
evolutionary literature concerns populations with sexual reproduction. What transfers is the language and the frame, not the
numbers.
"""
    (OUT / "references.md").write_text(references, encoding="utf-8")

    zenodo = {
        "title": "Directionality works but does not scale, and inherited adaptation does not appear, in a resource-limited pond world",
        "upload_type": "publication",
        "publication_type": "preprint",
        "publication_date": "2026-11-06",
        "version": VERSION,
        "creators": [{"name": "Vladimirov, Ilya"}],
        "license": "cc-by-4.0",
        "access_right": "open",
        "language": "eng",
        "keywords": ["pond", "directionality", "taxis", "inheritance", "lineage selection", "crowding",
                     "negative result"],
        "description": (
            "A pond world with a resource, death and reproduction is used to ask two questions. First, does a local "
            "behavioural rule help after the environment changes? Local resource-greedy movement does: it holds 0.475 "
            "of the favourable half against 0.357 for the control on a patchy environment. The advantage decays as the "
            "rich zone fills (correlation -0.57 with rich-zone occupancy over 18 points), because cells compete for "
            "space rather than for food: one organism per grid cell, and the patch's inflow exceeds one cell's "
            "consumption, so the resource barely falls while occupancy rises. Second, is such a skill inherited? Four "
            "tests -- a double flip back to the native environment, a flip to a new environment, a heritable mobility "
            "trait and a heritable directionality trait, each with a transplant control -- give a consistent null, and "
            "the null survives the removal of the lineage-monopoly confound. Three experiments are recorded as invalid "
            "by construction rather than as negative results. Every printed number is re-derived from the deposited "
            "artifacts by a machine check (49 checks, 0 failures)."),
        "related_identifiers": [{
            "relation": "references",
            "identifier": DOI_PREVIOUS,
            "scheme": "doi",
            "resource_type": "publication-preprint",
        }],
    }
    (OUT / "zenodo.json").write_text(json.dumps(zenodo, ensure_ascii=False, indent=1), encoding="utf-8")

    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256")
    lines = [f"{sha256(p)}  {p.relative_to(OUT).as_posix()}" for p in files]
    (OUT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(f"[031-package] directory: {OUT}")
    print(f"[031-package] files: {len(files) + 1} (including MANIFEST.sha256), artifacts copied: {copied}")
    if absent:
        print(f"[031-package] WARNING artifacts not found: {absent}")

    if not args.no_zip:
        if ZIP.exists():
            ZIP.unlink()
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(OUT.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(OUT).as_posix())
        print(f"[031-package] zip: {ZIP} ({ZIP.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
