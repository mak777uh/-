"""build_article_031_package.py — assemble the deposit package for article 031.

The repository keeps the article, the figures, the verifier and this script; the package puts them into one
archive with everything a depositor needs and no more: the article (Markdown + PDF), the three figures (PNG for
reading, PDF for typesetting), the committed artifacts the article cites, the machine check of every printed
number, a dataset README, the licence, a Zenodo metadata record, a sha256 manifest and the publication brief.

    python scripts/build_article_031_package.py
    python scripts/build_article_031_package.py --no-zip     # leave the directory for inspection

Output: `_exports/031-directionality-and-inheritance/` and `_exports/031-directionality-and-inheritance-v1.0.zip`
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
ZIP = ROOT / "_exports" / "031-directionality-and-inheritance-v1.0.zip"
STEM = "031-directionality-and-inheritance-in-the-pond"

# Every artifact the article's numbers come from (checked by check_article_031_numbers.py).
AGGREGATES = [
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
    "s4_baseline_flip200_current.json",
    "s4_localres_flip200_current.json",
    "s4_randdir_flip200_current.json",
    "s4_gradpos_sanity_flip200.json",
    "s2_b1_gradpos_flip200.json",
    "s2_b2_tumble_p06_flip200.json",
]

LICENCE = """CC BY 4.0

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

DATASET_README = """# Dataset for article 031 — directionality and inheritance in the pond

This package contains the article, its figures, and the machine-readable artifacts behind every number.

## What the artifacts are

Each `*.json` under `artifacts/` is one experiment series: a list of runs (`rows`), each with per-seed
windows of measurements. The article's numbers are means over seeds and windows; the file
`check_article_031_numbers.py` re-derives 20 of them and compares them with the text.

The two kinds of file:

- `s4_*.json`, `s2_*.json` — the baseline and mechanism runs on a gradient environment;
- `s6_*.json` … `s16_*.json` — the inheritance tests (S6, S7, S9, S10) and the patchy-environment
  transfer (S11–S16).

## How to reproduce

```bash
python check_article_031_numbers.py     # expects the artifacts at ../../morphogenesis/experiments/E09_pond/
```

Inside this package the artifacts sit in `artifacts/`, so the verifier needs its `POND` path pointed at that
directory (one-line change at the top of the script), or run it from the repository, where the paths match.

## What is NOT here

- The world engine itself (`morphogenesis/world/`) — it lives in the repository, not the package; the
  artifacts are its output.
- Checkpoints (`.pt` files) — the project does not publish weights in the deposit.
- The three withdrawn experiments' raw runs are included where they exist, because the article names them
  as invalid by construction; their numbers are not used.
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

    shutil.copy2(ART, OUT / f"{STEM}.md")
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

    (OUT / "README.md").write_text(DATASET_README, encoding="utf-8")
    (OUT / "LICENSE").write_text(LICENCE, encoding="utf-8")

    zenodo = {
        "title": "Directionality and inheritance in the pond: what works, where the boundary is",
        "upload_type": "publication",
        "publication_type": "article",
        "publication_date": "2026-11-06",
        "version": "v1.0",
        "creators": [{"name": "Vladimirov, Ilya"}],
        "license": "cc-by-4.0",
        "keywords": ["pond", "directionality", "taxis", "inheritance", "lineage selection"],
        "description": ("Four independent tests of inherited adaptation in a resource-limited pond world all "
                        "give null; separately, local resource-greedy movement transfers to a patchy "
                        "environment but its advantage decays as the rich zone fills (r = -0.57 with "
                        "rich-zone occupancy). Three experiments are named as invalid by construction."),
    }
    (OUT / "zenodo.json").write_text(json.dumps(zenodo, ensure_ascii=False, indent=1), encoding="utf-8")

    manifest = {"files": []}
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.json":
            manifest["files"].append({
                "path": path.relative_to(OUT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            })
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[031-package] directory: {OUT}")
    print(f"[031-package] files: {len(manifest['files'])}, artifacts copied: {copied}")
    if absent:
        print(f"[031-package] WARNING artifacts not found: {absent}")

    if not args.no_zip:
        if ZIP.exists():
            ZIP.unlink()
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(OUT.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(OUT).as_posix())
        print(f"[031-package] zip: {ZIP} ({ZIP.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
