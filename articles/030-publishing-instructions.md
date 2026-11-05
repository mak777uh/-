# Publishing instructions — article 030 (for the person who performs the deposit)

This is the detailed map for whoever uploads the article. It says where everything lies on the machine that built it, what is
inside the data archive, how to check the archive before uploading, which fields are already filled in, and what must not be
changed. The short version of the same information travels inside the archive as `PUBLISHING.md`.

**Status: prepared, not submitted. Nothing has gone outward.** Do not upload until the author says so in writing.

- **Author (and the only person to ask):** Ilya Vladimirov.
- **Licence:** CC BY 4.0 (the standing default; if the author names another licence, change it in `zenodo.json` and `LICENSE`
  first).
- **Version of the article:** v2.1. **Version of the archive:** v2.1.

## 1. Where everything lies

Built on this machine, in the repository `C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo`:

| what | where |
|---|---|
| **the data archive to upload** | `_exports\030-gap-switches-fusion-v2.1.zip` (about 2.2 MB, 73 files inside) |
| the same archive, already unpacked for inspection | `_exports\030-gap-switches-fusion\` |
| the article (Markdown, the source of the PDF) | `articles\030-the-gap-between-surfaces-decides-fusion.md` |
| the article as PDF, nine figures embedded | `articles\030-the-gap-between-surfaces-decides-fusion.pdf` |
| the nine figures, PNG (reading) and PDF (typesetting) | `articles\030-figures\` |
| every number printed in the article, with its source | `articles\030-figures\tables.json` |
| the verified reference list (20 entries, one rejected) | `articles\030-references.md` |
| the aggregates the article cites (45 files) | `morphogenesis\experiments\E09_pond\l1_field_x15*.json` ... `l1_field_x19*.json` |
| the independent reviews of the article's numbers | `lab\reviews\2026-11-04-030-numbers.md` (the earlier, narrower edition) and `lab\reviews\2026-11-05-030-v20-numbers.md` (the blocks added in v2.0 and the gap curve added in v2.1) |
| the machine check that every printed number is real | `scripts\check_article_030_numbers.py` |
| the script that rebuilds the archive | `scripts\build_article_030_package.py` |
| the script that rebuilds the article PDF | `scripts\make_article_030_pdf.py` |

The zip is written outside version control on purpose (`_exports\` is not committed); the repository keeps the article, the
figures, the tables and the build scripts, so the archive can be rebuilt at any time with

```bash
python scripts/make_article_030_figures.py     # figures and tables.json, from committed artifacts only
python scripts/make_article_030_pdf.py         # the article PDF (needs the bundled LibreOffice kit)
python scripts/build_article_030_package.py    # _exports\030-gap-switches-fusion-v2.1.zip
python scripts/check_article_030_numbers.py    # re-derives all 164 printed numbers and compares them with the text
```

## 1b. Links (for the depositor)

| what | link |
|---|---|
| the repository (branch `main`, the article's home) | https://github.com/mak777uh/- |
| the article, Markdown source | https://github.com/mak777uh/-/blob/main/articles/030-the-gap-between-surfaces-decides-fusion.md |
| these instructions, in the repository | https://github.com/mak777uh/-/blob/main/articles/030-publishing-instructions.md |
| the verified reference list | https://github.com/mak777uh/-/blob/main/articles/030-references.md |
| the article's figures and `tables.json` | https://github.com/mak777uh/-/tree/main/articles/030-figures |
| the independent review of the added numbers | https://github.com/mak777uh/-/blob/main/lab/reviews/2026-11-05-030-v20-numbers.md |
| the review of the earlier edition | https://github.com/mak777uh/-/blob/main/lab/reviews/2026-11-04-030-numbers.md |
| the previous article of the series (published, cited by DOI) | https://doi.org/10.5281/zenodo.23933440 |
| the project's sequence map (which article is which step) | https://github.com/mak777uh/-/blob/main/docs/series.md |
| Zenodo: start a new upload | https://zenodo.org/uploads/new |
| Zenodo: the API documentation (the commands in section 4) | https://developers.zenodo.org/ |
| arXiv: submit (only if the author asks, only after Zenodo) | https://arxiv.org/submit |

The data archive itself is **not** in the repository (it is rebuilt by `scripts/build_article_030_package.py`); it is the file
named in section 1 and it is what you upload.

## 2. What is inside the archive (73 files)

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
figures/fig1..fig9 .png and .pdf                   the nine figures in both formats (18 files)
data/derived/tables.json                           every number plotted in the article
data/aggregates/*.json                             the 45 aggregates the article cites (original files, unchanged)
```

The raw field arrays (96 × 96 float32 per world) are **not** in the archive: they are regenerable from the committed scripts
and they are tens of megabytes. The 45 aggregates carry one row per world, which is what the outcomes and the tables are built
from.

## 3. Check the archive before uploading (about 5 minutes)

1. **Integrity.** Unpack the zip and check every file against its checksum:
   `sha256sum -c MANIFEST.sha256` (Linux/macOS) or, on Windows, `Get-FileHash -Algorithm SHA256` for each line of the
   manifest. Every line must report OK.
2. **Nothing missing.** Count the files: 73 in the archive; nine figures × two formats = 18; 45 aggregates; `tables.json`;
   and the 9 top-level files listed above.
3. **Spot-check one number end to end.** In `data/derived/tables.json` open `fig5.by_gap[1]`: it reads
   `{"radius": 4.0, "gap": 10.0, "fused": 34, "share": 0.1883, ...}`. The same 34 must appear in the article's table in
   section 5.5 (row "radius 4, gap 10", column "fused") and in the aggregate
   `data/aggregates/l1_field_x196_gap_or_size.json` at `gap_table.r4_g10.fused_worlds`. If the three disagree, stop and tell
   the author — do not "fix" anything.
4. **Spot-check the newest block as well.** In `data/derived/tables.json` open `fig6.gap_table.r4_g8`: it reads
   `{"radius": 4.0, "gap": 8.0, "sep": 16.0, "share": 0.9607, "fused_worlds": 138, "worlds": 144}`. The same 138
   and 0.9607 must appear in the article's section 5.5 table (row "radius 4, gap 8") and in the aggregate
   `data/aggregates/l1_field_x198_gap_curve.json` at `gap_table.r4_g8`.

The author's own checks, already run and not to be repeated (they need the repository): 164 printed numbers are compared with
the aggregates by `scripts/check_article_030_numbers.py`, the earlier edition's six result groups were recomputed over 1008
per-world rows (`lab/reviews/2026-11-04-030-numbers.md`), and the blocks added in v2.0 were recomputed independently in
`lab/reviews/2026-11-05-030-v20-numbers.md`. Your job is to confirm that the
archive you received is the checked one.

Every field of `zenodo.json` is already filled in: title, description, keywords, licence `CC-BY-4.0`, version `v2.1`,
language, and one creator, `Vladimirov, Ilya`. The single related identifier points at the previous article of the series (DOI 10.5281/zenodo.23933440) with the
relation `references`, and the article itself opens by summarising that previous step. **Do not add an author, an affiliation, an ORCID or a
link that the author did not give.**

## 4. Deposit on Zenodo (enough on its own)

The archive has **folders** — `figures/`, `data/aggregates/`, `data/derived/`. Zenodo's *legacy* deposition API cannot store a
file name that contains a slash: `PUT <bucket>/data/aggregates/x.json` answers **404**, and a client that loops over
`find . -type f` therefore fails at the first data file. Flattening the names instead would break `MANIFEST.sha256` and every
path the README gives. The **records API keeps the tree**, so deposit with it.

**The script (in the repository, not in the archive).** It reads `zenodo.json` from the unpacked archive, translates the fields
to the records API, uploads all 73 entries, and checks every uploaded file against the local copy before it will publish:

```bash
export ZENODO_TOKEN=<personal access token with deposit:write>

# 1. create the draft, upload, and verify — prints the record id, the reserved DOI and a per-file check
python scripts/zenodo_deposit_030.py --archive _exports/030-gap-switches-fusion

# 2. re-check what the server holds at any time (size and md5 of every file)
python scripts/zenodo_deposit_030.py --archive _exports/030-gap-switches-fusion --verify

# 3. publish — irreversible, only after the author confirms the file list in writing
python scripts/zenodo_deposit_030.py --archive _exports/030-gap-switches-fusion --publish
```

**By hand, in the same order:** `POST /api/records` with the metadata; `POST /api/records/<id>/draft/files` with the list of
keys (`[{"key": "figures/fig1-what-we-measure.png"}, ...]`); `PUT` each file's bytes to the `links.content` URL the response
gives; `POST /api/records/<id>/draft/files/<url-encoded key>/commit` for each file; then
`POST /api/records/<id>/draft/actions/publish`. Leave the legacy `/api/deposit/depositions` endpoint alone for this archive.

**Web interface.** The fields map one-to-one onto the form: upload type **publication**, publication type **preprint**, access
**open**, version **v2.1**. Drag in the whole unpacked folder and then check the record page: `figures/` and `data/` must still
be folders, not names like `data_aggregates_...`. Keep `MANIFEST.sha256`, `README.md` and `LICENSE` in the deposit.

## 5. arXiv (optional, only after Zenodo, only if the author asks)

- **Category:** `q-bio.PE` (populations and evolution); `nlin.PS` (pattern formation) as a cross-list if the author agrees.
- **Files:** the PDF in the archive already has all nine figures embedded and can be uploaded as the main file. arXiv also
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
3. Nothing in the repository changes by itself at this point: the article stays at v2.1 with its status line "deposited, DOI
   …", which the author updates.

## 9. Questions

Every question goes to the author, **Ilya Vladimirov**. The three things only the author can answer are: the licence, the
author list, and whether the paper goes to Zenodo only (recommended, one step) or also to arXiv (a second step, after the
deposit).

## 10. The article's own version history and verification notes

Both sections used to close the article. They are provenance, not results, so they travel here instead of into the deposited
text; the version history is in chronological order and the counts are the final ones.

### Version history

- **v1.0** (2026-11-04): first edition. Consolidates the phase-census line X184–X197 for an outside reader, including the
  correction of the "size window" reading (X195) to a **gap** reading (X196) and the unit-of-observation result (X194, X197),
  with the published deviance drop falling from 20.7 to 14.3 when the world replaces the run.
- **v1.1** (2026-11-05): a glossary of the article's own terms in §3; an explicit next-step section (§8); the author line set
  from the owner's answer (Ilya Vladimirov); a repeated word fixed. No number changed.
- **v1.2** (2026-11-05): the article opens with the shape the owner asked for — last time we found this, so we checked that,
  here are the results, here is where we move next. A new opening section states what the previous article found and the two
  questions it left open; the published previous step is cited by DOI; the sequence is mapped in `docs/series.md`; §8 is
  retitled. No number changed.
- **v2.0** (2026-11-05): one article for the whole path after the published previous step, rather than four. Adds §5.1 (the
  crossing and its geometry), §5.2 (what a daughter keeps), §5.6 (the corridor, its failed sharp prediction, the edge and the
  cliff, the rate ladder), §5.7 (the full crossing table and the between-family dispersion) and §5.8 (the bridge against the
  local inflow); the abstract and §1, §2, §6–§9 are rewritten to match; §9 lists the six places where a report's prose
  disagrees with the stored field. After the independent review of the added blocks, six sentences were corrected (X168c's seed
  count, X173's followable window, the two-habitat trade behind X156's mean slopes, X183's five candidate readings, X188's
  sensitivity end, X167's area ratio), and the gate then held **145** needles.
- **v2.1** (2026-11-05, the version deposited): the curve the v2.0 edition could only announce. X198 finished after v2.0 was
  written, so §5.5 gains the eight-arm curve (1152 worlds) with the crossing of one half between gaps 9 and 10, the two empty
  cells that were previously inferred, four arms that reproduce an earlier cell exactly, and the observation that the bridge
  keeps varying where nothing fuses (gaps 11 and 12); §8 records the answer instead of the running question; the artifact is
  [A27], the result card is §10jg of the field plan. The final build also renumbers the nine figures in reading order (they had
  been numbered in the order the analyses were done) and gives each one a caption, moves this history and the verification
  notes out of the article, fixes the two links that pointed at `figures/tables.json` (the table lives in `data/derived/`), and
  cites [20] in §9. No number changed: the build that leaves this machine passes **164 of 164**.

### Verification

- **Numbers.** Every number quoted in the article is re-derived from the committed artifacts by
  `python scripts/check_article_030_numbers.py --ci` — **164** needles, each of which must also appear verbatim in the text.
  The table behind them is `030-figures/tables.json` in the repository, `data/derived/tables.json` in the archive.
- **References.** Existence of every reference is checked in `030-references.md` (in the archive: `references.md`) via the
  corpus manifest or Crossref/DataCite; the one entry that could not be verified is marked there and is not cited.
- **Independent review.** `lab/reviews/2026-11-04-030-numbers.md` — the headline numbers of the earlier edition, including the
  two statistics whose interval depends on the unit of observation; `lab/reviews/2026-11-05-030-v20-numbers.md` — the blocks
  added in v2.0, whose six corrections are all applied.
- **Not published.** Nothing has been submitted, deposited or posted anywhere. The deposit is the publication and needs the
  author's written go-ahead. The author is fixed — one author, Ilya Vladimirov, no affiliation and no ORCID — and so is the
  licence (CC BY 4.0).
