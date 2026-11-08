"""build_article_036_package.py — assemble the deposit package for article 036.

Same shape as the 031-035 packages: the article (Markdown + PDF), its figures, the scripts that produce and
check every number, the formal files the article describes, the licence, the Zenodo metadata, a sha256 manifest
and the publishing instruction.

Article 036 is unusual: it is about the bench, so the package carries the bench's own instruments rather than an
experiment artifact. That is deliberate — a reader must be able to run the checks the article claims.

    python scripts/build_article_036_package.py

Output: `_exports/036-a-research-bench-v1.0.zip` (ignored by git). Nothing is uploaded by this script.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
STEM = "036-a-research-bench-where-the-instrument-reports-on-itself"
ART = ROOT / "articles" / f"{STEM}.md"
PDF = ROOT / "articles" / f"{STEM}.pdf"
FIGDIR = ROOT / "articles" / "036-figures"
VERIFIER = ROOT / "scripts" / "check_article_036_numbers.py"
CLAIMS = ROOT / "lab" / "article-036-claims.json"
OUT = ROOT / "_exports" / "036-a-research-bench-v1.0.zip"
VERSION = "v1.0"
DOI_PREVIOUS = "10.5281/zenodo.24044032"

# the instruments the article describes; a reader must be able to run them
INSTRUMENTS = [
    ROOT / "scripts" / "closure_probe.py",
    ROOT / "scripts" / "policy_bridge.py",
    ROOT / "scripts" / "policy_diff.py",
    ROOT / "scripts" / "policy_mediator.py",
    ROOT / "scripts" / "check_run_manifest_gate.py",
    ROOT / "scripts" / "check_weights_ignored.py",
    ROOT / "scripts" / "check_protected_staged.py",
    ROOT / "scripts" / "check_single_running.py",
    ROOT / "scripts" / "check_experiment_manifest.py",
    ROOT / "scripts" / "check_report_style.py",
    ROOT / "scripts" / "lean_check.py",
    ROOT / "scripts" / "make_article_036_figures.py",
    ROOT / "formal" / "Policy.lean",
    ROOT / "mediator" / "src" / "lib.rs",
    ROOT / "mediator" / "Cargo.toml",
    ROOT / "lab" / "autonomy-rules.json",
    ROOT / "lab" / "experiments" / "E18.json",
    ROOT / "docs" / "report-template.md",
]

LICENSE = """CC BY 4.0

Copyright (c) 2026 Ilya Vladimirov

This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit https://creativecommons.org/licenses/by/4.0/
"""

ZENODO = {
    "title": "A research bench where the instrument reports on itself",
    "upload_type": "publication",
    "publication_type": "preprint",
    "publication_date": "2026-11-08",
    "version": VERSION,
    "creators": [{"name": "Vladimirov, Ilya"}],
    "license": "cc-by-4.0",
    "access_right": "open",
    "language": "eng",
    "keywords": ["reproducibility", "formal verification", "Lean 4", "mutation testing",
                 "agent governance", "research infrastructure"],
    "notes": ("Made by AI agents working in the project's repository, with periodic feedback from the human "
              "operator. Every printed number is produced by a command shipped in this package; "
              "check_article_036_numbers.py runs them and fails on a mismatch."),
    "related_identifiers": [
        {"identifier": DOI_PREVIOUS, "relation": "continues", "scheme": "doi"},
    ],
    "description": (
        "We describe the engineering and methodological apparatus of a long-running study of a minimal "
        "artificial world. Three claims are made and each is checkable by a command: reproducibility is "
        "enforced rather than promised (wrapper, manifest, bit-exact anchor); refutation is structural (every "
        "gate must fail on a planted defect); and the policy that governs the agents is proved (nine theorems "
        "in Lean, a bridge from the JSON file to the model, and three implementations required to agree before "
        "the harness acts). We report the failures, because they are the argument: six defects were found in a "
        "single day of formal work and five of them were the authors'."
    ),
}

INSTRUCTION = """# How to check this package

Every number in the article is produced by a command shipped here. Nothing is asserted that cannot be run.

## 1. What is in the archive

| path | what |
|---|---|
| `ARTICLE.md` | the article, Markdown |
| `ARTICLE.pdf` | the article, PDF |
| `figures/` | the two figures, PNG and PDF |
| `check_article_036_numbers.py` | the number gate: runs the commands and compares with the claims |
| `article-036-claims.json` | the machine-readable list of claims |
| `instruments/` | the scripts the article describes (closure probes, policy bridge, mediator, gates) |
| `formal/Policy.lean` | the nine theorems |
| `mediator/src/lib.rs` | the Rust mediator, no dependencies |
| `lab/autonomy-rules.json` | the policy file the bridge reads |
| `MANIFEST.sha256` | one line per file: `sha256  path` |

## 2. What you can check without the full repository

The number gate needs the repository, because its claims are about repository counts. What you CAN check from
the archive alone:

1. **the proofs compile** — install Lean 4.35 (`elan default leanprover/lean4:stable`) and run
   `lean formal/Policy.lean`. It must exit 0 with no output.
2. **the Rust mediator compiles and its tests pass** — `cd mediator && cargo test`. Six tests must pass.
3. **the manifest is intact** — `sha256sum -c MANIFEST.sha256` (Linux/macOS) or
   `Get-FileHash` per line (Windows).

## 3. What requires the repository

`check_article_036_numbers.py` reads `lab/article-036-claims.json`, runs each command in the repository and
compares the parsed value with the expected one. It fails if a command exits non-zero, so a failing command is
never accepted as evidence. Run it from the repository root:

    python scripts/check_article_036_numbers.py
    python scripts/check_article_036_numbers.py --self-test   # plants a wrong number; must fail

## 4. The claim this package does NOT make

The article does not claim that the bench makes the science correct. It claims that part of the errors become
detectable, locatable and reproducible. The closure of the harness is measured on five probes, not proved, and
the article says so.
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    missing = [p for p in (ART, PDF, VERIFIER, CLAIMS, *INSTRUMENTS) if not p.exists()]
    if missing:
        raise SystemExit(f"[036-package] missing: {[str(p) for p in missing]}\n"
                         "Run scripts/make_article_036_figures.py and make_article_036_pdf.py first.")

    # Forward-slash keys only: on Windows `zf.write(path, "a/b")` stores backslashes and the archive then fails
    # to open on Linux and on Zenodo.
    figures = [(f"figures/{p.name}", p.read_bytes()) for p in sorted(FIGDIR.iterdir())
               if p.suffix.lower() in (".png", ".pdf")]
    article = (ART.read_text(encoding="utf-8")
               .replace("](036-figures/", "](figures/")
               .replace("](036-a-research-bench-where-the-instrument-reports-on-itself.md)", "](ARTICLE.md)"))

    entries: list[tuple[str, bytes]] = [
        ("ARTICLE.md", article.encode("utf-8")),
        ("ARTICLE.pdf", PDF.read_bytes()),
        *figures,
        ("check_article_036_numbers.py", VERIFIER.read_bytes()),
        ("article-036-claims.json", CLAIMS.read_bytes()),
    ]
    for p in INSTRUMENTS:
        rel = p.relative_to(ROOT).as_posix()
        key = rel if rel.startswith(("formal/", "mediator/", "lab/")) else f"instruments/{p.name}"
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

    # verify: no backslashes in names, and the archive opens
    with zipfile.ZipFile(OUT) as zf:
        names = zf.namelist()
        bad = [n for n in names if "\\" in n]
        assert not bad, f"backslash names in the archive: {bad}"
        assert zf.testzip() is None, "the archive does not open"
    print(f"[036-package] {OUT} - {OUT.stat().st_size} bytes, {len(entries)} entries, "
          f"backslash names 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
