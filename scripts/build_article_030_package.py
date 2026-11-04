"""build_article_030_package.py — assemble the deposit package for article 030.

The repository keeps the article, the figures, the derived tables and this script; the package puts them into one archive
with everything a depositor needs and no more: the article, the five figures (PNG for reading, PDF for typesetting), the
derived table behind every number, the committed aggregates the article cites, the verified reference list, a dataset
README, the licence, a Zenodo metadata record, a sha256 manifest and the publication brief.

    python scripts/build_article_030_package.py
    python scripts/build_article_030_package.py --no-zip     # leave the directory for inspection

Output: `_exports/030-gap-switches-fusion/` and `_exports/030-gap-switches-fusion-v1.1.zip` (both ignored by git).

One author is set (Vladimirov, Ilya — given by the owner on 05.11; no ORCID, no related identifiers); the licence is CC BY
4.0, the standing default, and the brief says where to change it. Nothing is uploaded by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "articles" / "030-the-gap-between-surfaces-decides-fusion.md"
FIGDIR = ROOT / "articles" / "030-figures"
REFS = ROOT / "articles" / "030-references.md"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "_exports" / "030-gap-switches-fusion"
ZIP = ROOT / "_exports" / "030-gap-switches-fusion-v1.1.zip"
STEM = "030-the-gap-between-surfaces-decides-fusion"

AGGREGATES = [
    "l1_field_x184_cold_body.json",
    "l1_field_x185_one_law.json",
    "l1_field_x186_table_local.json",
    "l1_field_x187_nucleation.json",
    "l1_field_x189_bridge.json",
    "l1_field_x190_bridge_sites.json",
    "l1_field_x191_site_sweep.json",
    "l1_field_x192_phase_census.json",
    "l1_field_x193_phase_census_r3.json",
    "l1_field_x194_phase_clusters.json",
    "l1_field_x195_sign_sweep.json",
    "l1_field_x196_gap_or_size.json",
    "l1_field_x197_deviance_worlds.json",
]

LICENSE = """Creative Commons Attribution 4.0 International Public License

By exercising the Licensed Rights (defined below), You accept and agree to be bound by the terms and conditions of this
Creative Commons Attribution 4.0 International Public License ("Public License"). To the extent this Public License may be
interpreted as a contract, You are granted the Licensed Rights in consideration of Your acceptance of these terms and
conditions, and the Licensor grants You such rights in consideration of benefits the Licensor receives from making the
Licensed Material available under these terms and conditions.

Full text: https://creativecommons.org/licenses/by/4.0/legalcode
"""

README = """# Dataset — the gap between surfaces switches fusion (article 030)

This archive accompanies the article `{stem}.md` and holds every number printed in it, the aggregates those numbers were
computed from, and the verified reference list.

## Layout

| path | what it is |
|---|---|
| `{stem}.md` | the article (Markdown, English) |
| `{stem}.pdf` | the article as a PDF (if the build machine had a PDF renderer; see PUBLISHING.md) |
| `figures/` | Figures 1-5 as PNG (reading) and PDF (typesetting) |
| `data/derived/tables.json` | every number plotted in the article, with the artifact it came from |
| `data/aggregates/` | the aggregates the article cites, verbatim from the repository |
| `references.md` | the verified reference list, with the verification command or manifest key per entry |
| `LICENSE` | CC BY 4.0 |
| `zenodo.json` | deposit metadata (Zenodo legacy API format) |
| `MANIFEST.sha256` | checksums of every file above |
| `PUBLISHING.md` | the brief for whoever performs the deposit |

## What the data are

Runs of a two-species reaction-diffusion medium on a 96x96 grid with a striped supply of period 12 cells. Each world places
two ring-shaped bodies of pattern at chosen positions and is followed for 400 steps. The outcome is whether the two bodies
become one connected component. "Bridge ratio" is the field value at the midpoint between the two bodies divided by the
strongest field value within 10 cells of that midpoint, read at the contact step.

The aggregates are summaries over the worlds of each arm, one row per world: the phase (a pair of positions modulo the
stripe period), the local supply at those positions, the outcome, and the bridge ratio at contact. The compact per-world
component lists are in the repository under `morphogenesis/experiments/L1_field/x19*.compact.json`; the raw 96x96 field
arrays are not part of the deposit (they are regenerable with the committed scripts).

## Provenance

Every number is computed from the aggregates by `scripts/make_article_030_figures.py` in the repository, written into
`data/derived/tables.json`, and checked against the article text by `scripts/check_article_030_numbers.py --ci`. The
aggregates carry their own command lines and pre-registrations. The independent recomputation of the headline numbers is
`lab/reviews/2026-11-04-030-numbers.md` in the repository.
"""

BRIEF = """# Publishing brief — article 030 "{title}"

You are receiving this brief together with one archive, `030-gap-switches-fusion-v1.1.zip`. The article and its data are
final: the numbers have been checked mechanically against the data and independently recomputed by a reviewer. Your job is
to deposit them, not to improve them. Where this brief says "ask the author", stop and ask; do not decide on your own.

## 1. What is in the archive

| file | what it is |
|---|---|
| `{stem}.md` | the article (Markdown, English) |
| `figures/fig1..fig5.png` and `.pdf` | the five figures, reading and typesetting versions |
| `data/derived/tables.json` | every number plotted in the article |
| `data/aggregates/*.json` | the aggregates the article cites |
| `references.md` | the verified reference list (20 entries, one rejected and not cited) |
| `LICENSE` | CC BY 4.0 |
| `zenodo.json` | deposit metadata |
| `MANIFEST.sha256` | sha256 of every file above |
| `PUBLISHING.md` | this brief, verbatim |

## 2. Before uploading — confirm, do not decide

1. **Creators.** `zenodo.json -> creators` carries `Vladimirov, Ilya` — the author list the owner gave on 05.11 (one author,
   no ORCID, no other identifiers). Do not add names.
2. **Related identifiers.** The owner states there are none; `related_identifiers` is empty. If a DOI of its own or a
   companion deposit appears, the owner supplies it. *(OWNER)*
3. **Licence.** The archive carries CC BY 4.0, which is the standing default. If the owner names another licence it must be
   changed here first. *(OWNER)*
4. **The PDF.** If the article PDF is absent from the archive, the machine that built it had no PDF renderer: run
   `python scripts/make_article_030_pdf.py` (needs the bundled LibreOffice kit) before uploading, or deposit the Markdown
   alone and say so in the description.

## 3. Deposit settings

- **Upload type:** publication, **publication type:** preprint.
- **Title and description:** copy from `zenodo.json` verbatim.
- **Keywords:** from `zenodo.json` (`keywords`).
- **Access:** open.
- **Version:** v1.1.
- After the deposit, record the DOI back in the repository (`lab/notices.md`) so the line's own artifacts can cite it.

## 4. What this archive does NOT contain

The raw field arrays (96x96 float32 per world) are not deposited: they are regenerable from the committed scripts and
manifests, and they are several tens of megabytes. The component lists that the outcomes come from are in the repository.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rewrite_links(text: str) -> str:
    """The package has its own layout: point the article's links at it."""
    return (text
            .replace("](030-figures/", "](figures/")
            .replace("](030-references.md)", "](references.md)"))


def main() -> int:
    ap = argparse.ArgumentParser(description="build the article 030 deposit package")
    ap.add_argument("--no-zip", action="store_true")
    args = ap.parse_args()

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "figures").mkdir(parents=True)
    (OUT / "data" / "derived").mkdir(parents=True)
    (OUT / "data" / "aggregates").mkdir(parents=True)

    (OUT / f"{STEM}.md").write_text(rewrite_links(ART.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    pdf = ART.with_suffix(".pdf")
    if pdf.exists():
        shutil.copy2(pdf, OUT / f"{STEM}.pdf")
    else:
        print("[package-030] article PDF absent — run scripts/make_article_030_pdf.py before depositing")
    shutil.copy2(REFS, OUT / "references.md")
    for fig in sorted(FIGDIR.glob("fig*.png")) + sorted(FIGDIR.glob("fig*.pdf")):
        shutil.copy2(fig, OUT / "figures" / fig.name)
    shutil.copy2(FIGDIR / "tables.json", OUT / "data" / "derived" / "tables.json")
    missing = []
    for name in AGGREGATES:
        src = POND / name
        if not src.exists():
            missing.append(name)
            continue
        shutil.copy2(src, OUT / "data" / "aggregates" / name)
    if missing:
        print(f"[package-030] aggregates not found (skipped): {', '.join(missing)}")

    (OUT / "LICENSE").write_text(LICENSE, encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(README.format(stem=STEM), encoding="utf-8", newline="\n")
    (OUT / "PUBLISHING.md").write_text(
        BRIEF.format(stem=STEM, title="The gap between surfaces, not the body size, switches fusion in a "
                                       "pattern-forming chemical medium"),
        encoding="utf-8", newline="\n")

    zenodo = {
        "title": "The gap between surfaces, not the body size, switches fusion in a pattern-forming chemical medium",
        "upload_type": "publication",
        "publication_type": "preprint",
        "description": (
            "A reaction-diffusion medium with an uneven, striped supply is used to ask what decides whether two blobs of "
            "pattern fuse into one. Enumerating all positions modulo the stripe period gives 144 phase classes and nine "
            "distinct local supplies. At a fixed supply the bridge of chemical between the bodies decides the outcome "
            "(logistic slope 6.09, z 5.8 at radius 6; 4.85, z 2.7 at radius 3), with the supply-fusion association carrying "
            "the opposite sign at the smaller body. The surface-to-surface gap switches fusion (share 0.00 at a 12-cell gap, "
            "0.19 at 10, 0.40 at 9, 0.83 and 0.96 at 8) while the body size shifts it by about a tenth. Replacing runs by "
            "worlds leaves an AUC at 0.652 to 0.660 but moves a deviance drop from 20.7 to 14.3, inside that test's own bar "
            "of 20, so the unit of observation has to be checked per statistic."
        ),
        "creators": [{"name": "Vladimirov, Ilya"}],
        "license": "CC-BY-4.0",
        "access_right": "open",
        "version": "v1.1",
        "language": "eng",
        "keywords": ["reaction-diffusion", "pattern formation", "neural cellular automata", "coalescence", "bridge",
                     "pre-registration", "unit of observation"],
        "related_identifiers": [],
        "notes": ("author list as given by the owner on 2026-11-05: one author, no ORCID, no related identifiers. Nothing "
                  "has been uploaded by the build script."),
    }
    (OUT / "zenodo.json").write_text(json.dumps(zenodo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    lines = [f"{sha256(p)}  {p.relative_to(OUT).as_posix()}" for p in files]
    (OUT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    if not args.no_zip:
        if ZIP.exists():
            ZIP.unlink()
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(OUT.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(OUT).as_posix())
        print(f"[package-030] {ZIP.relative_to(ROOT)} — {ZIP.stat().st_size / 1024:.0f} KB, {len(files) + 1} files")
    else:
        print(f"[package-030] {OUT.relative_to(ROOT)} — {len(files) + 1} files (no zip)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
