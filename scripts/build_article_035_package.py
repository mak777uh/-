"""build_article_035_package.py — assemble the deposit package for article 035.

Same shape as the 031 and 032 packages: the article (Markdown + PDF), the artifact it cites, the script that produced
it, the machine check of every printed number, the licence, the Zenodo metadata, a sha256 manifest and the publishing
instruction.

    python scripts/build_article_035_package.py

Output: `_exports/035-where-movement-pays-v1.0.zip` (ignored by git). Nothing is uploaded by this script, and the
package must not be uploaded until the author says so in writing.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
STEM = "035-where-movement-pays-the-boundary-of-profitability"
ART = ROOT / "articles" / f"{STEM}.md"
PDF = ROOT / "articles" / f"{STEM}.pdf"
VERIFIER = ROOT / "scripts" / "check_article_035_numbers.py"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
SCRIPT = ROOT / "morphogenesis" / "scripts" / "s41_e1_phase_diagram.py"
OUT = ROOT / "_exports" / f"{STEM}-v1.0.zip"
VERSION = "v1.0"
DOI_PREVIOUS = "10.5281/zenodo.24012536"

LICENSE = """CC BY 4.0

Copyright (c) 2026 Ilya Vladimirov

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

ZENODO = {
    "title": "Where movement pays: the boundary of profitability in a resource-limited pond",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-07",
    "version": VERSION,
    "creators": [{"name": "Vladimirov, Ilya"}],
    "license": "cc-by-4.0",
    "access_right": "open",
    "language": "eng",
    "keywords": ["pond", "movement", "density dependence", "resource renewal", "boundary of profitability"],
    "notes": "Made by an AI agent working in the project's repository, with periodic feedback from the human operator; every printed number is re-derived from the deposited artifacts by a machine check.",
    "description": (
        "The earlier articles of the series measured whether a movement rule pays at single points: one density, one "
        "resource-recovery rate, one mobility. This one maps the surface. We ran 240 simulations across four colony "
        "densities and three recovery rates, ten seeds each, and measured the difference between a cell that steps "
        "towards the richest neighbour and a cell that does not move. The boundary exists and it runs along the "
        "recovery rate: with medium or fast recovery movement pays at every density tested (+0.028 to +0.076), while "
        "with slow recovery the sign flips at the two highest densities (-0.022 and -0.030). The optimum is at a "
        "density of 128 cells on 1024 (12.5 %), not at the lowest density tested (3.1 %): with too few cells nobody "
        "finds a patch, and at 53.7 % the competition eats the gain. This explains an earlier result of the series - "
        "the working density of 53.7 % sits beyond the boundary when recovery is slow, which is why greedy movement "
        "was found harmful there. Every printed number is re-derived from the deposited artifact by a machine check "
        "(27 checks, 0 failures)."),
    "related_identifiers": [{
        "relation": "references",
        "identifier": DOI_PREVIOUS,
        "scheme": "doi",
        "resource_type": "publication-preprint",
    }],
}

INSTRUCTION = f"""# Publishing instruction - article 035

**Title:** {ZENODO['title']}
**Version:** {VERSION}
**Author:** Ilya Vladimirov
**Licence:** CC BY 4.0

## What to deposit

1. `{STEM}.md` - the article (Markdown source)
2. `{STEM}.pdf` - the rendered article
3. `artifacts/s49_e1_density_axis.json` - the 240 runs the article's table comes from
4. `scripts/s41_e1_phase_diagram.py` - the script that produced them
5. `check_article_035_numbers.py` - the machine check of every printed number (run it inside the unpacked archive:
   `python check_article_035_numbers.py` -> 0 failures out of 27 checks)
6. `MANIFEST.sha256` - sha256 of every file in this package, one line per file
7. `zenodo.json` - the deposit metadata, ready to upload as it stands
8. `LICENSE` - CC BY 4.0

## Settings

Upload type **publication**, publication type **preprint**, access **open**, version **{VERSION}**, licence
**CC BY 4.0**, author **Vladimirov, Ilya**. Title and description: copy from `zenodo.json`. The single related
identifier points at the previous article of the series (DOI {DOI_PREVIOUS}, relation *references*).

## What to do if a corrected version is needed

A published record is never deleted and never rewritten. Upload the correction as a **new version of the same
record**, keep the version field, and put `Corrections in this version: <what was fixed, why, which check caught
it>` first in the description. Deleting is for drafts only.

## How the article was made

It was written by an AI agent working in the project's repository, from artifacts the agent also produced, with
periodic feedback from the human operator who owns the project. Keep this statement in the record: it is part of
the article, not a formality.

## What not to do

- Do not change the title, the author line, the licence or the numbers.
- Do not split the package: the article, its PDF and the artifact belong to one record.
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    missing = [p for p in (ART, PDF, VERIFIER, SCRIPT) if not p.exists()]
    if missing:
        raise SystemExit(f"[035-package] missing: {[str(p) for p in missing]}\n"
                         "Run scripts/make_article_035_pdf.py first.")
    artifact = POND / "s49_e1_density_axis.json"
    if not artifact.exists():
        raise SystemExit(f"[035-package] missing artifact {artifact}")

    # Forward-slash keys only: on Windows `zf.write(path, "a/b")` stores backslashes and the archive then fails to
    # open on Linux and on Zenodo.
    entries: list[tuple[str, bytes]] = [
        (ART.name, ART.read_bytes()),
        (PDF.name, PDF.read_bytes()),
        (f"artifacts/{artifact.name}", artifact.read_bytes()),
        (f"scripts/{SCRIPT.name}", SCRIPT.read_bytes()),
        ("check_article_035_numbers.py", VERIFIER.read_bytes()),
        ("LICENSE", LICENSE.encode("utf-8")),
        ("zenodo.json", (json.dumps(ZENODO, ensure_ascii=False, indent=1) + "\n").encode("utf-8")),
        ("INSTRUCTION.md", INSTRUCTION.encode("utf-8")),
    ]
    manifest = "".join(f"{sha256(data)}  {key}\n" for key, data in entries)
    entries.append(("MANIFEST.sha256", manifest.encode("utf-8")))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for key, data in entries:
            zf.writestr(zipfile.ZipInfo(key), data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"[035-package] {OUT} - {OUT.stat().st_size} bytes, {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
