# Publishing brief — article 029 "How lineages begin and end in a pattern-forming chemical medium"

You are receiving this brief together with one archive, `029-lineages-v2.2.zip`. The article and its data are final: the
author has reviewed them and the numbers have been checked mechanically against the data. Your job is to deposit them,
not to improve them. Where this brief says "ask the author", stop and ask; do not decide on your own.

## 1. What is in the archive

| file | what it is |
|---|---|
| `029-lineages-in-a-pattern-forming-field.md` | the article (Markdown, English, ~5 000 words, 8 sections) |
| `figures/fig1-what-we-measure.{png,pdf}` | schematic of the measurement (geometry, three outcomes, bookkeeping) |
| `figures/fig2-mixing-length.{png,pdf}` | the mixing length in two quantities: outcome against the initial gap, and the surface gap at contact for three body sizes |
| `figures/fig3-the-edge.{png,pdf}` | the edge: a step in the outcome, a spread in the timing |
| `figures/fig4-endings.{png,pdf}` | how bodies end, and the survival reversal across three habitats |
| `figures/fig5-heredity.{png,pdf}` | transmission slope against a shuffled null; scatter against the noise parameter |
| `figures/fig6-shape-heredity.{png,pdf}` | what a daughter inherits: the slope ladder, and the shape slopes read at four daughter ages |
| `data/aggregates/*.json` | 31 aggregate files: the numbers behind every table and figure, each with the command line of its runs |
| `data/derived/tables.json` | every number printed in the article, each entry naming the aggregate it came from |
| `data/derived/*.csv` | the same values as flat tables (`table-edge`, `table-habitats`, `table-heredity`) |
| `README.md` | description of the dataset: conventions, units, provenance |
| `LICENSE` | CC BY 4.0 |
| `zenodo.json` | deposit metadata in Zenodo's legacy-API format |
| `MANIFEST.sha256` | sha256 of every file above |
| `PUBLISHING.md` | this brief, verbatim, so the archive can be handed over on its own |
| `029-lineages-in-a-pattern-forming-field.pdf` | the article as a PDF, with all six figures embedded |

PDF figures are the typesetting versions, PNG the reading versions; both are full page width. The archive holds 53
files: the 59 listed in `MANIFEST.sha256` (everything, including this brief and the article PDF) plus the manifest
itself, which cannot contain its own hash.

## 2. Check the archive before you upload anything (5 minutes)

1. **Integrity.** Unpack and compare every file against `MANIFEST.sha256`:
   `sha256sum -c MANIFEST.sha256` (Linux/macOS), or `Get-FileHash -Algorithm SHA256` in a loop on Windows. Every line
   must report OK.
2. **Nothing missing.** Six figures in two formats (12 files), 31 aggregates, 6 files under `data/derived/`, and the
   7 top-level files: the article in `.md` and `.pdf`, `README.md`, `LICENSE`, `zenodo.json`, `PUBLISHING.md` and
   `MANIFEST.sha256`, plus 4 files under `papers/` — 60 files in all.
3. **Spot-check one number.** In `data/derived/tables.json` take the entry `"h_slope"`; the same string
   (`0.9837 [0.9680, 1.0002]`) must appear in the article's §4.6 table and in
   `data/aggregates/l1_field_x155_heredity.json` under `cells[*].slope` / `slope_ci`. If the three disagree, do not
   upload — tell the author.

The author's own verification, already run (do not re-run, it needs their repository): a checker requires each of the 91
printed numbers to appear in the article and in the derived table, and the derived table is generated from the
aggregates. Your job is to confirm that the archive you received is the checked one.

## 3. Fill in the two fields only the author can supply

`zenodo.json` is ready except for two values:

1. `creators[].name` — currently the placeholder `"Morphogenesis laboratory"`. Replace it with the author name(s) and
   affiliation **exactly as the author gives them**, in the author's order. Do not invent a name, an affiliation, or an
   ORCID. If the author has an ORCID, add `"orcid"` to the same object. The same name goes into the copyright line of
   `LICENSE` (currently the same placeholder) — ask the author for the exact wording rather than shortening it.
2. `related_identifiers[0].identifier` — currently a repository URL. Confirm it with the author. If the data repository is
   private, remove the entry and put "Data available from the author on request" into `notes` instead.

Everything else in `zenodo.json` (title, abstract, keywords, licence, version `2.1`, date) matches the article. **Do not
change the title.**

## 4. Deposit on Zenodo (recommended, and enough on its own)

`zenodo.json` is in the legacy API format. With a personal access token in `$ZENODO_TOKEN`:

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

The web interface works equally well: the fields in `zenodo.json` map one-to-one onto the form, and the file list above is
the list to drag in. Keep `MANIFEST.sha256`, `README.md` and `LICENSE` in the deposit — they are part of it.

If the author wants the DOI inside the arXiv version, reserve it first: Zenodo issues a draft DOI at creation and the
final one at publication.

## 5. arXiv (optional, and only after Zenodo)

- Category `q-bio.PE` (populations and evolution); `nlin.PS` as a cross-list if the author agrees.
- Convert the Markdown to PDF **with the figures embedded**, using `figures/*.pdf`. The article references the figures by
  their `figures/fig1-what-we-measure.png` names — keep those paths or relabel consistently, and check that all six
  appear.
- Abstract: copy the article's Abstract verbatim. Title: as in `zenodo.json`.
- Upload `MANIFEST.sha256` as an ancillary file, and preferably `README.md` and `LICENSE` with it in a single
  `.zip` — one ancillary archive is accepted more reliably than loose files.
- Cite the Zenodo DOI in the arXiv comments/DOI field.
- arXiv's non-exclusive licence is fine; the CC BY 4.0 terms stay with the Zenodo record.

## 6. Journal (only if the author asks for it)

This brief is not a journal submission. If the author asks, the realistic shortlist for this paper is *Artificial Life*
(MIT Press), *PLOS ONE*, or the ALIFE conference proceedings; each needs reformatting to its template and figures
re-rendered at its column width. Ask the author before reformatting, and never submit the same text to two venues at once.

## 7. What you must not do

1. **Do not edit the article's numbers, claims, or wording of conclusions, and do not touch the figure data.** Every
   number is machine-checked against the aggregates; a "fix" breaks that chain and misrepresents the data. If something
   looks wrong, report it to the author.
2. **Do not publish anything beyond this archive** — no other reports, no raw simulation output, no unrelated files.
3. **Do not use words the article deliberately avoids**: "life", "consciousness", "intelligence", or "alive" as a claim
   about the medium. The article says "lineage", "body", "ending", "transmission" for a reason, and that vocabulary is part
   of the result.
4. **Do not change the licence** (CC BY 4.0) or the version number.
5. **Do not upload with the placeholder author name.** If the author has not supplied it, stop.
6. **Do not publish a repository tag or release** — this deposit is the publication; anything else needs the author's word.

## 8. After publishing, report exactly four things

1. the DOI and the Zenodo record URL;
2. the number of files uploaded and their total size;
3. the sha256 of the uploaded `MANIFEST.sha256`;
4. the Zenodo version string.

If the author later asks for the DOI in the paper, update the article's front matter and re-issue the archive as `v2.1`;
do not re-upload over a published version — Zenodo versions are additive.
