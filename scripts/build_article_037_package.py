"""build_article_037_package.py — assemble the deposit package for article 037.

Same shape as the 031-036 packages: the article (Markdown + PDF), its figures, the number gate and the claims it
checks, the referee reports that produced the corrections, the licence, the Zenodo metadata, a sha256 manifest and
the publishing instruction.

Article 037 is a manifesto, so its package carries its own review history: the two independent referee reports are
part of the evidence, because the document's value is that it was corrected by them.

    python scripts/build_article_037_package.py

Output: `_exports/037-what-our-errors-say-v1.0.zip` (ignored by git).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
STEM = "037-what-our-errors-say-about-the-limits-of-the-method"
ART = ROOT / "articles" / f"{STEM}.md"
PDF = ROOT / "articles" / f"{STEM}.pdf"
FIGDIR = ROOT / "articles" / "037-figures"
VERIFIER = ROOT / "scripts" / "check_article_037_numbers.py"
OUT = ROOT / "_exports" / "037-what-our-errors-say-v1.0.zip"
VERSION = "v1.0"
DOI_PREVIOUS = "10.5281/zenodo.24044880"

EVIDENCE = [
    ROOT / "lab" / "reviews" / "2026-11-08-037-rigour.md",
    ROOT / "lab" / "reviews" / "2026-11-08-037-literature.md",
    ROOT / "docs" / "eliminations.md",
    ROOT / "scripts" / "k_readouts.py",
    ROOT / "scripts" / "check_experiment_manifest.py",
    ROOT / "lab" / "experiments" / "E18.json",
    ROOT / "reports" / "2026-11-08-corpus-audit.md",
]

LICENSE = """CC BY 4.0

Copyright (c) 2026 Ilya Vladimirov

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

ZENODO = {
    "title": "What our own errors say about the limits of the method",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-08",
    "version": VERSION,
    "creators": [{"name": "Vladimirov, Ilya"}],
    "license": "cc-by-4.0",
    "access_right": "open",
    "language": "eng",
    "keywords": ["research method", "open-ended evolution", "falsifiability",
                 "within-cell measurement", "select versus specify", "agent governance"],
    "notes": ("Made by AI agents working in the project's repository, with periodic feedback from the human "
              "operator. The document was reviewed by two independent referees, both of whom found it wrong; "
              "their reports are shipped in this package and the corrections they forced are marked in the text."),
    "related_identifiers": [
        {"identifier": DOI_PREVIOUS, "relation": "continues", "scheme": "doi"},
    ],
    "description": (
        "We report the errors our own programme produced over 583 reports and 43 articles about a minimal "
        "artificial world, and draw a conclusion that is uncomfortable for us. Three claims: our errors have a "
        "common shape (restricted after review: two shapes, not one); the available designs can only imitate the "
        "living (restricted to what we ran, and to specification rather than selection); and the scientific graph "
        "that grows from below cannot reach a different ontology (withdrawn to a statement of ignorance, with an "
        "operational test added). We then propose four constraints on what we build, of which only one is a claim "
        "a single experiment can refute, and we state three stopping conditions with metrics, thresholds and "
        "seed counts - because a manifesto that cannot fail is a slogan, and the first version of ours was one."
    ),
}

INSTRUCTION = """# How to check this package

This is a manifesto, not an experiment. What can be checked is (a) that its numbers match the repository and
(b) that the corrections it claims were actually made.

## 1. What is in the archive

| path | what |
|---|---|
| `ARTICLE.md`, `ARTICLE.pdf` | the manifesto |
| `figures/` | the three claims and the four constraints |
| `check_article_037_numbers.py` | the number gate: 23 checks |
| `reviews/` | **the two independent referee reports that forced the corrections** |
| `evidence/` | the register of eliminated directions, the readouts, the manifest gate, E18, the corpus audit |
| `MANIFEST.sha256` | one line per file: `sha256  path` |

## 2. What you can check from the archive alone

1. **the manifest is intact** — `sha256sum -c MANIFEST.sha256`
2. **the corrections are real** — read `reviews/2026-11-08-037-rigour.md` and find, in `ARTICLE.md`, the
   paragraph that answers each finding. The reviewer's findings are numbered; the answers are marked
   "A referee of this document pointed out..." in the text.
3. **the readout is within-cell** — `evidence/k_readouts.py --self-test` must report 0 failures of 6, including
   the test that plants a cell-level bonus and requires the two readouts NOT to move.

## 3. What requires the repository

`check_article_037_numbers.py` reads the repository and compares counts. Run it from the repository root:

    python scripts/check_article_037_numbers.py

## 4. The claim this document does NOT make

It does not claim that the living has been found, that the current literature is wrong, or that working outside
the scientific graph is safe. It claims that a class of designs cannot reach a particular question, gives the
argument for the class, and states what would show the argument is empty.
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    missing = [p for p in (ART, PDF, VERIFIER, *EVIDENCE) if not p.exists()]
    if missing:
        raise SystemExit(f"[037-package] missing: {[str(p) for p in missing]}\n"
                         "Run scripts/make_article_037_figures.py and make_article_037_pdf.py first.")

    figures = [(f"figures/{p.name}", p.read_bytes()) for p in sorted(FIGDIR.iterdir())
               if p.suffix.lower() in (".png", ".pdf")]
    article = (ART.read_text(encoding="utf-8")
               .replace("](037-figures/", "](figures/"))

    entries: list[tuple[str, bytes]] = [
        ("ARTICLE.md", article.encode("utf-8")),
        ("ARTICLE.pdf", PDF.read_bytes()),
        *figures,
        ("check_article_037_numbers.py", VERIFIER.read_bytes()),
    ]
    for p in EVIDENCE:
        key = f"reviews/{p.name}" if "reviews" in p.parts else f"evidence/{p.name}"
        entries.append((key, p.read_bytes()))
    entries += [
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

    with zipfile.ZipFile(OUT) as zf:
        names = zf.namelist()
        bad = [n for n in names if "\\" in n]
        assert not bad, f"backslash names in the archive: {bad}"
        assert zf.testzip() is None, "the archive does not open"
        # every hash must match
        man = dict(reversed(l.split("  ", 1)) for l in zf.read("MANIFEST.sha256").decode().strip().splitlines())
        wrong = [k for k, h in man.items() if k in names and sha256(zf.read(k)) != h]
        assert not wrong, f"hash mismatch: {wrong}"
    print(f"[037-package] {OUT} - {OUT.stat().st_size} bytes, {len(entries)} entries, "
          f"backslash names 0, hashes verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
