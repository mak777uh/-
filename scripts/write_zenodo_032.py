"""Write the zenodo.json metadata file for article 032 (and, generically, for others).

Zenodo accepts a `zenodo.json` inside the deposit; it fills the record form. The file carries the title,
author, licence, keywords, the relation to the previous article of the series, and the description that
the depositor will see.
"""
from __future__ import annotations
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "_exports" / "032-what-decides-whether-behaviour-pays-v1.0.zenodo.json"

META = {
    "title": "What decides whether behaviour pays: movement, not the signal it follows",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-07",
    "version": "v1.1",
    "language": "eng",
    "license": "cc-by-4.0",
    "access_right": "open",
    "creators": [
        {"name": "Vladimirov, Ilya", "affiliation": "independent researcher"}
    ],
    "keywords": [
        "agent-based model", "foraging", "habituation", "mobility",
        "signal field", "boundary of the setup", "artificial life"
    ],
    "description": (
        "Two negative results that reorder the previous article of the series, plus one refuted mechanism. "
        "(1) The sign of the greedy-movement advantage depends on the resource recovery rate: with slow "
        "recovery the greedy rule loses to a non-moving control (gap -0.174), with fast recovery it wins "
        "(+0.036). (2) The cause is a trap of inaction - the adaptive prediction tracks the falling "
        "resource, so cells stop qualifying to move. (3) Removing the adaptation flips the sign (+0.338), "
        "but with a near-equal absolute mobility budget the two references are indistinguishable (0.238 vs "
        "0.246, both below the 0.340 control), so what matters is how much the cell moves, not what it "
        "compares with. (4) A continuous diffusing signal field was tested in four designs: the "
        "cells-built field and an external rhythm are inert, the memory field works (+0.038..+0.045), but "
        "plain smoothing of the resource matches it (0.299 vs 0.297) - because a cell moves only 0.14 cells "
        "from its birth cell in a lifetime. Every printed number is machine-checked against the deposited "
        "artifacts."
    ),
    "notes": (
        "Part of a series. The previous article is 031, DOI 10.5281/zenodo.24012536. "
        "Corrections in this version: none (first version of this article)."
    ),
    "related_identifiers": [
        {
            "identifier": "10.5281/zenodo.24012536",
            "relation": "continues",
            "scheme": "doi",
            "resource_type": "publication-preprint",
        }
    ],
}


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(META, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[032-zenodo] {OUT} - {OUT.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
