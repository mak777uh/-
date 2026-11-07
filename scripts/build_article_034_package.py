"""build_article_034_package.py — assemble the deposit package for article 034.

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
STEM = "034-what-a-signal-should-change"
ART = ROOT / "articles" / f"{STEM}.md"
PDF = ROOT / "articles" / f"{STEM}.pdf"
VERIFIER = ROOT / "scripts" / "check_article_034_numbers.py"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
SCRIPT = ROOT / "morphogenesis" / "scripts" / "s87_e14_what_signal_changes.py"
OUT = ROOT / "_exports" / f"{STEM}-v1.0.zip"
VERSION = "v1.0"
DOI_PREVIOUS = "10.5281/zenodo.24035630"

LICENSE = """CC BY 4.0

Copyright (c) 2026 Ilya Vladimirov

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

ZENODO = {
    "title": "What a signal should change: the place, the time, or the rules",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-07",
    "version": VERSION,
    "creators": [{"name": "Vladimirov, Ilya"}],
    "license": "cc-by-4.0",
    "access_right": "open",
    "language": "eng",
    "keywords": ["pond", "signal", "environment", "agent-based model", "rules versus map"],
    "notes": "Made by an AI agent working in the project's repository, with periodic feedback from the human operator; every printed number is re-derived from the deposited artifacts by a machine check.",
    "description": (
        "The earlier articles tested only one way a signal can act - it tells the cell where the food is - and it paid "
        "only when it predicted the food early enough, and then only weakly (+0.012). This article asks which way pays: "
        "the place (where the food is), the time (how much food, everywhere), or the rules (what the cell itself pays). "
        "Every arm adds the same total resource per step, so the arms differ only in how the signal distributes or "
        "modulates it, and each arm runs on twenty seeds. The signal that changes the rules is four times stronger than "
        "the signal that says where (+0.0512 against +0.0117, with 18 of 20 seeds positive against 14 of 20); the signal "
        "that says when is indistinguishable from noise (+0.0080, 11 of 20). The reason is structural: the cells are "
        "immobile, planted in the poor centre of the grid, so a map is worth nothing to them, while a change in their own "
        "terms applies wherever they stand. Every printed number is re-derived from the deposited artifact by a machine "
        "check (20 checks, 0 failures)."),
    "related_identifiers": [{
        "relation": "references",
        "identifier": DOI_PREVIOUS,
        "scheme": "doi",
        "resource_type": "publication-preprint",
    }],
}

INSTRUCTION = f"""# Publishing instruction - article 034

**Title:** {ZENODO['title']}
**Version:** {VERSION}
**Author:** Ilya Vladimirov
**Licence:** CC BY 4.0

## What to deposit

1. `{STEM}.md` - the article (Markdown source)
2. `{STEM}.pdf` - the rendered article
3. `artifacts/s89_e14b_20seeds.json` - the 100 runs the article's table and figure come from
4. `figures/fig1-where-the-signal-acts.png` and `.pdf` - the figure, reading and typesetting versions
4. `scripts/s41_e1_phase_diagram.py` - the script that produced them
5. `check_article_034_numbers.py` - the machine check of every printed number (run it inside the unpacked archive:
   `python check_article_035_numbers.py` -> 0 failures out of 20 checks)
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
    missing = [p for p in (ART, PDF, VERIFIER, SCRIPT, ROOT / "scripts" / "make_article_034_figures.py")
               if not p.exists()]
    if missing:
        raise SystemExit(f"[034-package] missing: {[str(p) for p in missing]}\n"
                         "Run scripts/make_article_034_pdf.py first.")
    artifact = POND / "s89_e14b_20seeds.json"
    if not artifact.exists():
        raise SystemExit(f"[034-package] missing artifact {artifact}")

    # Forward-slash keys only: on Windows `zf.write(path, "a/b")` stores backslashes and the archive then fails to
    # open on Linux and on Zenodo.
    figdir = ROOT / "articles" / "034-figures"
    figures = [(f"figures/{p.name}", p.read_bytes()) for p in sorted(figdir.iterdir())
               if p.suffix.lower() in (".png", ".pdf")]
    article = (ART.read_text(encoding="utf-8")
               .replace("](034-figures/", "](figures/")
               .replace("](033-selection-exists-but-a-heritable-trait-does-not-ride-it.md)",
                        "](https://github.com/mak777uh/-/blob/main/articles/033-selection-exists-but-a-heritable-trait-does-not-ride-it.md)"))
    entries: list[tuple[str, bytes]] = [
        (ART.name, article.encode("utf-8")),
        (PDF.name, PDF.read_bytes()),
        *figures,
        (f"artifacts/{artifact.name}", artifact.read_bytes()),
        (f"scripts/{SCRIPT.name}", SCRIPT.read_bytes()),
        ("check_article_034_numbers.py", VERIFIER.read_bytes()),
        ("make_article_035_figures.py", (ROOT / "scripts" / "make_article_034_figures.py").read_bytes()),
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
    print(f"[034-package] {OUT} - {OUT.stat().st_size} bytes, {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
