# Publishing instructions — article 031 (for the person who performs the deposit)

This is the map for whoever uploads the article. It says what exists, where it lies, how to check everything before
uploading, and what must not be changed. The same information, shorter, travels inside the archive as `PUBLISHING.md`.

**Status: ready to deposit once the author says so.** The article text, its three figures, its PDF, the data archive and
the machine check of every printed number all exist and pass. **Do not upload anything until the author says so in
writing.**

- **Author (and the only person to ask):** Ilya Vladimirov.
- **Licence:** CC BY 4.0 (the standing default; if the author names another licence, change it in `zenodo.json` and
  `LICENSE` first).
- **Version of the article:** v2.0. **Version of the archive:** v2.0.

## 1. What this article is

A research article with one negative and one positive result, both about the same pond world. Its published title is
**"Directionality works but does not scale, and inherited adaptation does not appear, in a resource-limited pond
world"** (the file name keeps the `031-` prefix for navigation; the number is not part of the title):

- **Positive, with a measured limit:** local resource-greedy movement does help (0.475 against 0.357 baseline on a patchy
  environment), but the gain decays as the rich zone fills (advantage vs rich-zone occupancy, r = −0.57 over 18 points).
  The reason is measured, not assumed: cells compete for space, not for food.
- **Negative:** four tests of inherited adaptation all give null (S6 double flip, S7 flip to a new environment, S9
  heritable mobility, S10 heritable directionality), and the null survives the removal of the lineage-monopoly confound
  (S18). Recovery after an environment change is dispersal and survival, not selection on a trait.
- **Two refuted variants:** smoothing the signal does not help; refreshing the rich zones does not restore the advantage.
- **Three withdrawn experiments**, named in the article as invalid by construction rather than as negative results.

The article follows the sequence's own shape: last time we found this and decided to check that; here are the results; here
is where we move next.

## 2. Where everything lies

Repository: `C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo`

| what | where | state |
|---|---|---|
| the article (Markdown) | `articles\031-directionality-and-inheritance-in-the-pond.md` | **ready** |
| the article as PDF, eight pages, three figures embedded | `articles\031-directionality-and-inheritance-in-the-pond.pdf` | **ready** |
| the three figures, PNG (reading) and PDF (typesetting) | `articles\031-figures\` | **ready** |
| the machine check of every printed number (50 checks) | `scripts\check_article_031_numbers.py` | **ready** |
| the figure builder (reads artifacts only) | `scripts\make_article_031_figures.py` | **ready** |
| the artifacts the article cites (23 files) | `morphogenesis\experiments\E09_pond\s{1,2,4,6,7,9,10,11,12,13,14,15,16,18}_*.json` | **ready** |
| the reports behind each section | `reports\2026-11-0{5,6}-s*-*.md` | **ready** |
| the data archive to upload | `_exports\031-directionality-and-inheritance-v2.0.zip` (about 1.1 MB, 38 files: 37 hashed plus the manifest) | **ready** |
| the same archive, unpacked for inspection | `_exports\031-directionality-and-inheritance\` | **ready** |
| the reviews of the numbers | `lab\reviews\2026-11-06-031-numbers.md` and `lab\reviews\2026-11-06-031-independent.md` (verdict: holds with caveats) | **ready** |
| the script that rebuilds the PDF | `scripts\make_article_031_pdf.py` | **ready** |
| the script that rebuilds the archive | `scripts\build_article_031_package.py` | **ready** |

## 3. How to check everything before uploading

Run from the repository root. All three must pass:

```bash
python scripts/check_article_031_numbers.py --ci   # expect: 0 failures out of 50 checks
python scripts/make_article_031_figures.py         # rebuilds the three figures from artifacts
python scripts/build_article_031_package.py        # rebuilds the archive and its MANIFEST.sha256
```

Then check the archive itself: unpack it and compare every file with the manifest (`Get-FileHash -Algorithm SHA256` on
Windows, `sha256sum -c MANIFEST.sha256` on Linux/macOS) — 37 lines, all OK — and run the verifier inside the unpacked copy,
where it finds the artifacts next to itself:

```bash
cd _exports/031-directionality-and-inheritance
python check_article_031_numbers.py --ci           # expect: 0 failures out of 50 checks
```

`check_article_031_numbers.py` re-reads the artifacts and compares them with the numbers the prose states, in both
directions: a value it recomputes must appear verbatim in the article, and the article may not state a value the artifacts
do not produce. If it reports a failure, **do not upload** — report it to the author instead.

## 4. What must not be changed

1. **No number may be edited by hand.** If a number looks wrong, the artifact is right and the article is fixed by rerunning
   the checker and correcting the prose — never the other way round.
2. **The withdrawn experiments stay withdrawn.** S5/C, S11/D and the first S6/C3 attempt are named in §4.3 as invalid by
   construction. Removing that section would turn an honest record into a misleading one.
3. **The nulls stay nulls.** The article does not claim that inheritance is impossible in general — only that it does not
   appear in this setup, and it says where the test was underpowered. Do not strengthen the wording.
4. **No "life", "consciousness" or "intelligence" claims.** The project's own contract forbids them; the article speaks of
   an observed class of behaviour and its boundary.
5. **The author, the licence and the version are fixed** — one author, Ilya Vladimirov, no affiliation and no ORCID; CC BY
   4.0; v2.0. Do not add an author or a link the author did not give.
6. **Nothing is uploaded until the author says so in writing.**

## 5. Depositing on Zenodo (only after the author agrees)

The archive has folders — `figures/`, `artifacts/` — and Zenodo's *legacy* deposition API cannot store a file name that
contains a slash (`PUT <bucket>/artifacts/x.json` answers 404). Use the **records API**, which keeps the tree, or the web
form, and check afterwards that the folders survived.

1. Unpack the archive once and run the check from section 3 inside it.
2. Create the deposit and upload: either `python scripts/zenodo_deposit_030.py --archive <unpacked dir>` (the same script
   works for any article whose archive carries a `zenodo.json`; it verifies every uploaded file against the local copy and
   refuses to publish on a mismatch) or the web form at https://zenodo.org/uploads/new.
3. Settings: upload type **publication**, publication type **preprint**, access **open**, version **v2.0**, licence
   **CC BY 4.0**, author **Vladimirov, Ilya**. Title and description: copy from `zenodo.json`. The single related
   identifier points at the previous article of the series (DOI `10.5281/zenodo.23970711`, relation *references*).
4. Keep `MANIFEST.sha256`, `README.md`, `LICENSE` and `references.md` in the deposit.
5. Publish, then record the DOI in `lab/notices.md` so the line's own artifacts can cite it.

## 6. What is still open

| item | state |
|---|---|
| **independent review** | **done** — `lab/reviews/2026-11-06-031-independent.md`, verdict "holds with caveats"; its four corrections are applied in the article (S18 underpowered rather than null, the S13 ordering is a first-window effect, the shared runs behind "four tests", the S10 transplant is invalid) |
| **reference list** | **done** — `references.md` in the archive, three context references with the identifier each was checked against |
| **PDF** | **done** — 8 pages, three figures embedded, serif body, justified and hyphenated, running head and page numbers |
| **data archive** | **done** — 38 files, 23 artifacts, sha256 manifest verified, verifier runs inside it |

## 7. Links (for the depositor)

| what | link |
|---|---|
| the repository (branch `main`) | https://github.com/mak777uh/- |
| the article, Markdown source | https://github.com/mak777uh/-/blob/main/articles/031-directionality-and-inheritance-in-the-pond.md |
| these instructions, in the repository | https://github.com/mak777uh/-/blob/main/articles/031-publishing-instructions.md |
| the article's figures | https://github.com/mak777uh/-/tree/main/articles/031-figures |
| the machine check of the numbers | https://github.com/mak777uh/-/blob/main/scripts/check_article_031_numbers.py |
| the previous article of the series (published, cited by DOI) | https://doi.org/10.5281/zenodo.23970711 |
| Zenodo: start a new upload | https://zenodo.org/uploads/new |
| arXiv: submit (only if the author asks, only after Zenodo) | https://arxiv.org/submit |

## 8. One-paragraph summary for the depositor

The article is written, typeset and its numbers are verified by machine (50 checks, 0 failures); the archive is built and
its manifest covers 37 of 38 files, the 38th being the manifest itself. It is **not** uploaded: the author has not
authorised a deposit. When the author says so, run the three checks in section 3, then follow section 5. If anything in the
article looks wrong, the artifacts are the truth — report the discrepancy to the author rather than editing a number.
