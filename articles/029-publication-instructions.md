# Publishing instructions — article 029

Audience: the agent (human or AI) that will upload this package. You are publishing **on behalf of the owner**; the
owner has reviewed the article and given the go-ahead for the deposit. Nothing below requires you to make scientific
judgements: where a judgement is needed, the document says "ask the owner" and you must stop.

## What you are publishing

| item | file |
|---|---|
| the article (Markdown, English) | `029-lineages-in-a-pattern-forming-field.md` |
| figures 1-4 | `figures/fig1-mixing-length.{png,pdf}` … `fig4-heredity.{png,pdf}` |
| data: 28 aggregates | `data/aggregates/l1_field_*.json` |
| data: derived tables (every printed number + its source) | `data/derived/tables.json`, `data/derived/*.csv` |
| dataset description | `README.md` |
| licence | `LICENSE` (CC BY 4.0) |
| deposit metadata | `zenodo.json` (Zenodo legacy API format) |
| checksums | `MANIFEST.sha256` |

The whole set is also available as a single archive: `_exports/029-lineages-v1.0.zip` (repo root `_exports/`).

## Before you upload: verify, do not trust

Run these from the repository root. Each must succeed before you touch any external service.

```bash
python scripts/check_article_029_numbers.py --ci      # every printed number -> derived table -> aggregate
python scripts/verify.py                              # all repository gates, including that checker
sha256sum -c _exports/029-lineages/MANIFEST.sha256    # run inside _exports/029-lineages (Windows: use `Get-FileHash`)
```

`sha256sum -c` must print `OK` for every line. On Windows, compare `Get-FileHash -Algorithm SHA256` output against the
manifest with a script — do not eyeball 40 hashes.

## Metadata you must fill in, and may not invent

`zenodo.json` is a **template with two placeholders that only the owner can supply**:

1. `creators[].name` currently says `"Morphogenesis laboratory"`. Replace it with the author name(s) and affiliation the
   owner gives you, in the order the owner gives them. **Do not invent a name, an affiliation, or an ORCID.**
2. `related_identifiers[0].identifier` points at the public repository. Confirm the URL with the owner; if the repository
   is private, it must not be listed as a supplement and instead goes in `notes` as "data available on request".

Everything else (title, description, keywords, licence, version, date) is already correct and matches the article.
Do not change the title: it is the title the owner approved.

The two files that the article's own text calls "hosted in the repository" (the per-run artifacts) stay in the
repository. You are not uploading them, and you do not need to.

## Upload to Zenodo (the recommended first step)

Use the **legacy API** described in `zenodo.json`; the file is already in that format.

```bash
# 1. create the deposition (needs ZENODO_TOKEN in the environment; never commit or echo it)
curl -sS -H "Authorization: Bearer $ZENODO_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST https://zenodo.org/api/deposit/depositions \
     --data-binary @_exports/029-lineages/zenodo.json
```

The response contains `links.bucket` and the deposition id. Upload every file from `_exports/029-lineages/` (including
`MANIFEST.sha256` and `PUBLISHING.md`) to the bucket, then publish:

```bash
# 2. upload (repeat per file, or use the bucket API for a directory)
curl -sS -H "Authorization: Bearer $ZENODO_TOKEN" \
     -X PUT --data-binary @<file> "<links.bucket>/<basename>"
# 3. publish — this is irreversible; only after the owner confirms the file list
curl -sS -H "Authorization: Bearer $ZENODO_TOKEN" -X POST https://zenodo.org/api/deposit/depositions/<id>/actions/publish
```

If the API is unavailable, do it in the web interface with the same file list and the same metadata; the field names in
`zenodo.json` map one-to-one onto the form.

Record the resulting **DOI** in `lab/notices.md` and in `articles/029-…md` (a one-line "DOI:" note) — the deposit is only
finished when the repository knows its identifier.

## Upload to arXiv (optional, second step)

Category: `q-bio.PE` (populations and evolution), cross-list `nlin.PS` if the owner agrees. You need:

- `029-lineages-in-a-pattern-forming-field.md` converted to PDF **with the figures embedded** (`figures/*.pdf`
  are the typesetting versions; the PNGs are for reading). A plain Markdown-to-PDF tool with `figures/` on the path is
  enough; the article references the figures by their `figures/fig1-mixing-length.png` names, so keep those filenames.
- the abstract from the article's Abstract section, verbatim;
- `MANIFEST.sha256` uploaded as an ancillary file (arXiv accepts ancillary files on the upload form);
- licence: arXiv's non-exclusive licence (the CC BY 4.0 terms stay with the Zenodo record).

Do not submit to arXiv before the Zenodo DOI exists: the preprint should cite the dataset. If the owner prefers one
venue only, Zenodo alone is a complete deposit.

## Journal submission (only if the owner asks)

Nothing here is a submission. If the owner asks for a journal, the shortlist with the reason is in
`articles/029-publication-instructions.md` in the repository. In that case the article must be reformatted to the
journal's template and the figures re-rendered at the journal's width — ask the owner before reformatting anything.

## What you must not do

1. **Do not edit the article's numbers, claims or conclusions.** If something looks wrong, report it to the owner; the
   numbers are machine-checked against aggregates, and a "fix" breaks that chain.
2. **Do not publish anything but this package.** No other reports, no repository dumps, no raw fields, no seeds from
   other lines.
3. **Do not use words the line forbids**: "life", "consciousness", "intelligence", "alive" as a claim about the medium,
   "evolving" as a claim about populations. The article says "lineage", "endings", "transmission" for a reason.
4. **Do not change the licence.** CC BY 4.0 is what the package declares.
5. **Do not upload with a placeholder author.** If the owner has not supplied the author name, stop and ask.
6. **Do not mark the repository record as published before the DOI exists**; and do not tag a release without the
   owner's word (the repository's rule: tags only on a green CI and with the owner's decision).

## After publishing

Reply to the owner with exactly four things: the DOI (or the deposit URL), the number of files uploaded and their total
size, the sha256 of the uploaded `MANIFEST.sha256`, and the Zenodo version string. Then add the DOI to
`lab/notices.md`, `articles/029-…md` and the repository's `README.md` row, in one commit, and run
`python scripts/verify.py` once more.
