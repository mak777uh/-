"""Build the deposit package for article 034, to the publisher's checklist.

Same standard as 032/035: MANIFEST.sha256 one line per file, zenodo.json, LICENSE, INSTRUCTION.md, and every
zip entry written with a forward-slash key via writestr(ZipInfo(...)) so the archive opens on Linux and Zenodo.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "articles" / "034-what-a-signal-should-change.md"
PDF = ROOT / "articles" / "034-what-a-signal-should-change.pdf"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
SCRIPTS = ROOT / "morphogenesis" / "scripts"
OUT = ROOT / "_exports" / "034-what-a-signal-should-change-v1.0.zip"

ARTIFACTS = ["s89_e14b_20seeds.json"]
CODE = ["s87_e14_what_signal_changes.py"]

LICENSE = """CC BY 4.0

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

ZENODO = {
    "title": "What a signal should change: the place, the time, or the rules",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-07",
    "version": "v1.0",
    "language": "eng",
    "license": "cc-by-4.0",
    "access_right": "open",
    "creators": [{"name": "Vladimirov, Ilya", "affiliation": "independent researcher"}],
    "keywords": ["signal", "environment", "agent-based model", "immobile agents",
                 "rules versus map"],
    "description": (
        "Earlier articles of the series tested only one way a signal can act: it tells the cell where the "
        "food is, and it paid only when it predicted the food early enough, and then weakly (+0.012). This "
        "article asks which way a signal should act: the place, the time, or the rules. Cells are immobile "
        "and planted in the poor centre of the grid; every arm adds the same total resource per step, so the "
        "arms differ only in how the signal distributes or modulates it. Twenty seeds. A signal that changes "
        "the RULES (lowers the cell's upkeep) gives +0.0512 with 18 of 20 seeds positive, four times stronger "
        "than a signal saying WHERE (+0.0117, 14/20) and far above a signal saying WHEN (+0.0080, 11/20 = "
        "noise). An immobile cell cannot act on a map; it can only benefit from its own terms becoming "
        "cheaper. This agrees with the selection measurements of article 033: a cell's fate is set by energy "
        "and age, not by whether it stands in a rich zone."
    ),
    "notes": ("Part of a series. The previous article is 033. Corrections in this version: none "
              "(first version of this article)."),
    "related_identifiers": [
        {"identifier": "10.5281/zenodo.24035630", "relation": "continues", "scheme": "doi",
         "resource_type": "publication-preprint"}
    ],
}

INSTRUCTION = """# Publishing instruction - article 034

**Title:** What a signal should change: the place, the time, or the rules
**Version:** v1.0
**Author:** Ilya Vladimirov
**Licence:** CC BY 4.0
**Language:** English

## What to deposit

1. `034-what-a-signal-should-change.md` - the article
2. `034-what-a-signal-should-change.pdf` - the rendered article
3. `artifacts/s89_e14b_20seeds.json` - all 100 rows the article cites
4. `scripts/s87_e14_what_signal_changes.py` - the script that produced them
5. `MANIFEST.sha256` - sha256 of every file, one line per file
6. `zenodo.json` - the deposit metadata
7. `LICENSE` - CC BY 4.0

## Metadata

Everything is in `zenodo.json`. The related identifier points at 031
(`10.5281/zenodo.24035630`) so the series stays navigable.

## Corrections

A published record is corrected by a NEW VERSION of the same concept DOI, with the first line of the
description reading `Corrections in this version: <what changed and why>`. Drafts that were never
published may be deleted.

## What to send back

The DOI of the published record and the concept DOI.
"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    for p in (ART, PDF):
        if not p.exists():
            print(f"missing {p}")
            return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    entries: list[tuple[str, bytes]] = [
        (ART.name, ART.read_bytes()),
        (PDF.name, PDF.read_bytes()),
    ]
    for name in ARTIFACTS:
        p = POND / name
        if p.exists():
            entries.append((f"artifacts/{name}", p.read_bytes()))
    for name in CODE:
        p = SCRIPTS / name
        if p.exists():
            entries.append((f"scripts/{name}", p.read_bytes()))
    entries.append(("LICENSE", LICENSE.encode("utf-8")))
    entries.append(("INSTRUCTION.md", INSTRUCTION.encode("utf-8")))
    entries.append(("zenodo.json", (json.dumps(ZENODO, ensure_ascii=False, indent=2) + "\n").encode("utf-8")))
    manifest = "".join(f"{sha256_bytes(data)}  {key}\n" for key, data in entries)
    entries.append(("MANIFEST.sha256", manifest.encode("utf-8")))

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for key, data in entries:
            info = zipfile.ZipInfo(key.replace("\\", "/"))
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)
    with zipfile.ZipFile(OUT) as zf:
        names = zf.namelist()
        bad = [n for n in names if "\\" in n]
    print(f"[034-package] {OUT} - {OUT.stat().st_size} bytes, {len(entries)} entries, "
          f"backslash names {len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
