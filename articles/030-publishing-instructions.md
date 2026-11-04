# Publishing instructions — article 030 (for the person who performs the deposit)

This is the detailed map for whoever uploads the article. It says where everything lies on the machine that built it, what is
inside the data archive, how to check the archive before uploading, which fields are already filled in, and what must not be
changed. The short version of the same information travels inside the archive as `PUBLISHING.md`.

**Status: prepared, not submitted. Nothing has gone outward.** Do not upload until the author says so in writing.

- **Author (and the only person to ask):** Ilya Vladimirov.
- **Licence:** CC BY 4.0 (the standing default; if the author names another licence, change it in `zenodo.json` and `LICENSE`
  first).
- **Version of the article:** v2.0. **Version of the archive:** v2.0.

## 1. Where everything lies

Built on this machine, in the repository `C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo`:

| what | where |
|---|---|
| **the data archive to upload** | `_exports\030-gap-switches-fusion-v2.0.zip` (1.87 MB, 70 files inside) |
| the same archive, already unpacked for inspection | `_exports\030-gap-switches-fusion\` |
| the article (Markdown, the source of the PDF) | `articles\030-the-gap-between-surfaces-decides-fusion.md` |
| the article as PDF, eight figures embedded | `articles\030-the-gap-between-surfaces-decides-fusion.pdf` |
| the eight figures, PNG (reading) and PDF (typesetting) | `articles\030-figures\` |
| every number printed in the article, with its source | `articles\030-figures\tables.json` |
| the verified reference list (20 entries, one rejected) | `articles\030-references.md` |
| the aggregates the article cites (44 files) | `morphogenesis\experiments\E09_pond\l1_field_x15*.json` ... `l1_field_x19*.json` |
| the independent reviews of the article's numbers | `lab\reviews\2026-11-04-030-numbers.md` (the earlier, narrower edition) and `lab\reviews\2026-11-05-030-v20-numbers.md` (the blocks added in v2.0) |
| the machine check that every printed number is real | `scripts\check_article_030_numbers.py` |
| the script that rebuilds the archive | `scripts\build_article_030_package.py` |
| the script that rebuilds the article PDF | `scripts\make_article_030_pdf.py` |

The zip is written outside version control on purpose (`_exports\` is not committed); the repository keeps the article, the
figures, the tables and the build scripts, so the archive can be rebuilt at any time with

```bash
python scripts/make_article_030_figures.py     # figures and tables.json, from committed artifacts only
python scripts/make_article_030_pdf.py         # the article PDF (needs the bundled LibreOffice kit)
python scripts/build_article_030_package.py    # _exports\030-gap-switches-fusion-v2.0.zip
python scripts/check_article_030_numbers.py    # re-derives all 138 printed numbers and compares them with the text
```

## 2. What is inside the archive (70 files)

```text
030-the-gap-between-surfaces-decides-fusion.md     the article, Markdown
030-the-gap-between-surfaces-decides-fusion.pdf    the article, PDF with the figures embedded
references.md                                      the verified reference list (also a separate document in the repository)
README.md                                          what the dataset is, its units and its provenance
LICENSE                                            CC BY 4.0
zenodo.json                                        deposit metadata, ready to upload
PUBLISHING.md                                      the short publication brief
INSTRUCTIONS.md                                    this document, so the archive carries its own instructions
MANIFEST.sha256                                    sha256 of every file above
figures/fig1..fig8 .png and .pdf                   the eight figures in both formats (16 files)
data/derived/tables.json                           every number plotted in the article
data/aggregates/*.json                             the 44 aggregates the article cites (original files, unchanged)
```

The raw field arrays (96 × 96 float32 per world) are **not** in the archive: they are regenerable from the committed scripts
and they are tens of megabytes. The 44 aggregates carry one row per world, which is what the outcomes and the tables are built
from.

## 3. Check the archive before uploading (about 5 minutes)

1. **Integrity.** Unpack the zip and check every file against its checksum:
   `sha256sum -c MANIFEST.sha256` (Linux/macOS) or, on Windows, `Get-FileHash -Algorithm SHA256` for each line of the
   manifest. Every line must report OK.
2. **Nothing missing.** Count the files: 70 in the archive; eight figures × two formats = 16; 44 aggregates; `tables.json`;
   and the 9 top-level files listed above.
3. **Spot-check one number end to end.** In `data/derived/tables.json` open `fig4.by_gap[1]`: it reads
   `{"radius": 4.0, "gap": 10.0, "fused": 34, "share": 0.1883, ...}`. The same 34 must appear in the article's table in
   section 5.3 (row "radius 4, gap 10", column "fused") and in the aggregate
   `data/aggregates/l1_field_x196_gap_or_size.json` at `gap_table.r4_g10.fused_worlds`. If the three disagree, stop and tell
   the author — do not "fix" anything.

The author's own checks, already run and not to be repeated (they need the repository): 138 printed numbers are compared with
the aggregates by `scripts/check_article_030_numbers.py`, the earlier edition's six result groups were recomputed over 1008
per-world rows (`lab/reviews/2026-11-04-030-numbers.md`), and the blocks added in v2.0 were recomputed independently in
`lab/reviews/2026-11-05-030-v20-numbers.md`. Your job is to confirm that the
archive you received is the checked one.

Every field of `zenodo.json` is already filled in: title, description, keywords, licence `CC-BY-4.0`, version `v2.0`,
language, and one creator, `Vladimirov, Ilya`. The single related identifier points at the previous article of the series (DOI 10.5281/zenodo.23933440) with the
relation `references`, and the article itself opens by summarising that previous step. **Do not add an author, an affiliation, an ORCID or a
link that the author did not give.**

## 4. Deposit on Zenodo (enough on its own)

`zenodo.json` is in Zenodo's legacy API format. With a personal access token in `$ZENODO_TOKEN`:

```bash
# 1. create the deposition (the response gives links.bucket and the deposition id)
curl -sS -H "Authorization: Bearer $ZENODO_TOKEN" -H "Content-Type: application/json" \
     -X POST https://zenodo.org/api/deposit/depositions --data-binary @zenodo.json

# 2. upload every file except zenodo.json itself
for f in $(find . -type f ! -name zenodo.json); do
  curl -sS -H "Authorization: Bearer $ZENODO_TOKEN" -X PUT --data-binary @"$f" "<links.bucket>/${f#./}"
done

# 3. publish — irreversible, only after the author confirms the file list
curl -sS -H "Authorization: Bearer $ZENODO_TOKEN" \
     -X POST https://zenodo.org/api/deposit/depositions/<id>/actions/publish
```

The web interface works equally well: the fields map one-to-one onto the form, and the file list above is the list to drag in.
Settings: upload type **publication**, publication type **preprint**, access **open**, version **v2.0**. Keep
`MANIFEST.sha256`, `README.md` and `LICENSE` in the deposit.

## 5. arXiv (optional, only after Zenodo, only if the author asks)

- **Category:** `q-bio.PE` (populations and evolution); `nlin.PS` (pattern formation) as a cross-list if the author agrees.
- **Files:** the PDF in the archive already has all eight figures embedded and can be uploaded as the main file. arXiv also
  wants the source: if the author wants a LaTeX source, it has to be converted from the Markdown first — say so and ask,
  rather than uploading a half-converted package.
- **Abstract and title:** copy verbatim from the article and from `zenodo.json`.
- **Ancillary files:** upload the archive (or at least `MANIFEST.sha256`, `README.md` and `LICENSE`) as one ancillary `.zip`.
- **DOI:** cite the Zenodo DOI in the comments/DOI field. Reserve the Zenodo DOI before the arXiv upload if the author wants
  the DOI inside the arXiv record.
- arXiv's non-exclusive licence is fine; the CC BY 4.0 terms stay with the Zenodo record.

## 6. Journal (only if the author asks)

This package is not a journal submission. If the author asks, the realistic shortlist is *Artificial Life* (MIT Press),
*PLOS ONE*, or the ALIFE conference proceedings; each needs reformatting to its template and figures re-rendered at its column
width. Ask the author before reformatting, and never submit the same text to two venues at once.

## 7. What you must not do

1. **Do not edit the article's numbers, its claims or the wording of its conclusions, and do not touch the tables or the
   aggregates.** Every printed number is machine-checked against the aggregates; a "fix" breaks that chain.
2. **Do not add the raw 96 × 96 field arrays** to the deposit, and do not silently drop files: the file list in section 2 is
   the list that was checked.
3. **Do not rename** the article, the figures or the tables; the text refers to them by these names.
4. **Do not publish anything until the author says so in writing.** Until then this archive is a draft even though it is
   assembled.
5. **Do not decide the licence, the author list or the version yourself.** If something is unclear, stop and ask the author.

## 8. After the deposit

1. Record the DOI in the repository's `lab/notices.md` (one line: date, DOI, what was deposited) so the project can cite its
   own deposit; and, if the author wants the DOI in the metadata, add it to `zenodo.json -> related_identifiers` (the field is
   empty on purpose today).
2. If a journal or arXiv version follows, the Zenodo DOI belongs in its data-availability statement.
3. Nothing in the repository changes by itself at this point: the article stays at v1.1 with its status line "deposited, DOI
   …", which the author updates.

## 9. Questions

Every question goes to the author, **Ilya Vladimirov**. The three things only the author can answer are: the licence, the
author list, and whether the paper goes to Zenodo only (recommended, one step) or also to arXiv (a second step, after the
deposit).
