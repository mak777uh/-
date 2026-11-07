"""Build the deposit package for article 032.

Same shape as the 031 package: the article, its PDF, the artifacts it cites, a manifest with sha256, and
a short instruction for the depositor. The package is written to `_exports/032-...-v1.2.zip`, which by
contract is never committed; the repository keeps the trace (this script and the manifest inside the zip).
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "articles" / "032-what-decides-whether-behaviour-pays.md"
PDF = ROOT / "articles" / "032-what-decides-whether-behaviour-pays.pdf"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "_exports" / "032-what-decides-whether-behaviour-pays-v1.2.zip"

# the artifacts the article cites
ARTIFACTS = [
    "s19_g1_full.json", "s22_g3_full.json", "s23_g4_fast_recovery.json", "s24_g6_full.json",
    "s25_g7_full.json", "s26_h2_full.json", "s27_h4_full.json", "s28_h5_full.json",
    "s29_h6_full.json", "s30_h7_full.json", "s31_h8_full.json", "s32_h9_full.json",
    "s33_h10_full.json", "s34_h11_full.json", "s35_g7b_budget5.json", "s36_g7c_budget2.json",
    "s37_g8_full.json", "s38_h12_full.json", "s39_h13_full.json", "s40_h14_full.json",
]
SCRIPTS = [
    "s19_g1_recovery_rate.py", "s22_g3_adaptation_trap.py", "s24_g6_mobility_control.py",
    "s26_h2_signal_field.py", "s27_h4_external_rhythm.py", "s28_h5_memory_field.py",
    "s29_h6_memory_curve.py", "s30_h7_lifetime_curve.py", "s31_h8_mobility_curve.py",
    "s32_h9_distance_curve.py", "s33_h10_displacement.py", "s34_h11_field_vs_smoothing.py",
    "s37_g8_budget_sweep.py", "s38_h12_wave_predicts_food.py", "s39_h13_prediction_mobile.py",
]

INSTRUCTION = """# Publishing instruction - article 032

**Title:** What decides whether behaviour pays: movement, not the signal it follows
**Version:** v1.2
**Author:** Ilya Vladimirov
**Licence:** CC BY 4.0
**Language:** English

## What to deposit

1. `032-what-decides-whether-behaviour-pays.md` - the article (Markdown source)
2. `032-what-decides-whether-behaviour-pays.pdf` - the rendered article
3. `artifacts/` - the result files the article cites
4. `scripts/` - the experiment scripts that produced them
5. `MANIFEST.sha256` - sha256 of every file in this package, one line per file
6. `check_article_032_numbers.py` - the machine check of every printed number; run it inside the unpacked
   archive (`python check_article_032_numbers.py`) to confirm the text and the artifacts agree
7. `zenodo.json` - the deposit metadata, ready to upload as it stands
8. `LICENSE` - CC BY 4.0

## Metadata

Everything is already in `zenodo.json`: title, description, keywords, licence CC BY 4.0, version v1.2, one
author (Vladimirov, Ilya), and the related identifier `references -> 10.5281/zenodo.24012536`, which is the
previous article of the series. Do not add an author, an affiliation or a link the author did not give.

## What to do if a corrected version is needed

A published record is never deleted and never rewritten. If the author asks for a correction:
1. upload it as a **new version of the same record** (not a new record), so the concept DOI stays stable;
2. keep the version number in the version field (`v1.2`, `v1.3`, ...);
3. put the correction first in the description, in this exact form:
   `Corrections in this version: <what was fixed, why, and which check caught it>`.
Deleting is for drafts only.

## What NOT to do

- Do not change the title, the author line or the licence.
- Do not split the package: the article, the PDF and the artifacts belong to one record.
"""

LICENSE = """CC BY 4.0

Copyright (c) 2026 Ilya Vladimirov

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

ZENODO = {
    "title": "What decides whether behaviour pays: movement, not the signal it follows",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-07",
    "version": "v1.2",
    "creators": [{"name": "Vladimirov, Ilya"}],
    "license": "cc-by-4.0",
    "access_right": "open",
    "language": "eng",
    "keywords": ["pond", "directionality", "habituation", "mobility", "memory", "signal field",
                 "negative result"],
    "description": (
        "The previous article of the series reported that local resource-greedy movement helps in a patchy pond "
        "world but that its advantage shrinks as the rich zone fills. This article asks what decides whether a "
        "movement rule pays at all, and two of the three expected answers turn out to be wrong. The sign of the "
        "advantage depends on the resource recovery rate: with slow recovery the greedy rule loses to a "
        "non-moving control (gap -0.078 to -0.205, all three seeds negative), with fast recovery it wins (+0.036 "
        "to +0.101). The cause of the loss is a trap of inaction - the step rule fires only when the cell's "
        "prediction exceeds the actual resource, and the prediction tracks the falling resource, so the cell "
        "stops noticing that it is in a bad place. Removing the adaptation flips the sign sharply (+0.338 "
        "instead of -0.174), but with the number of moving cells held equal the two references are "
        "indistinguishable (0.238 against 0.246): what matters is how much a cell moves, not what it compares "
        "with. A continuous diffusing signal field was tested in four designs; only the memory variant gives a "
        "gain (+0.038 to +0.045), and plain smoothing of the resource matches it (0.299 against 0.297). A cell "
        "moves 0.14 cells from its birth cell in a whole lifetime, so long-range information cannot be used. "
        "Every printed number is re-derived from the deposited artifacts by a machine check (26 checks, 0 "
        "failures)."),
    "related_identifiers": [{
        "relation": "references",
        "identifier": "10.5281/zenodo.24012536",
        "scheme": "doi",
        "resource_type": "publication-preprint",
    }],
}


def _arcname(path: pathlib.Path) -> str:
    """The name the file has inside the archive (always forward slashes, whatever the platform)."""
    if path.parent.name == "E09_pond":
        return f"artifacts/{path.name}"
    if path.parent.name == "scripts":
        return f"scripts/{path.name}"
    return path.name


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not ART.exists():
        print(f"missing {ART}")
        return 1
    if not PDF.exists():
        print(f"missing {PDF} (run scripts/make_article_032_pdf.py)")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = []
    # Every entry is written with a forward-slash key: on Windows `zf.write(path, "a/b")` stores the
    # directory with backslashes, and the archive then fails to open on Linux and on Zenodo.
    entries: list[tuple[str, bytes]] = [
        (ART.name, ART.read_bytes()),
        (PDF.name, PDF.read_bytes()),
    ]
    for name in ARTIFACTS:
        p = POND / name
        if p.exists():
            entries.append((f"artifacts/{name}", p.read_bytes()))
    for name in SCRIPTS:
        p = ROOT / "morphogenesis" / "scripts" / name
        if p.exists():
            entries.append((f"scripts/{name}", p.read_bytes()))
    entries.append(("check_article_032_numbers.py", (ROOT / "scripts" / "check_article_032_numbers.py").read_bytes()))
    entries.append(("INSTRUCTION.md", INSTRUCTION.encode("utf-8")))
    entries.append(("LICENSE", LICENSE.encode("utf-8")))
    entries.append(("zenodo.json", (json.dumps(ZENODO, ensure_ascii=False, indent=1) + "\n").encode("utf-8")))
    manifest = "".join(f"{hashlib.sha256(data).hexdigest()}  {key}\n" for key, data in entries)
    entries.append(("MANIFEST.sha256", manifest.encode("utf-8")))

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for key, data in entries:
            zf.writestr(zipfile.ZipInfo(key), data, compress_type=zipfile.ZIP_DEFLATED)
    print(f"[032-package] {OUT} - {OUT.stat().st_size} bytes, {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
