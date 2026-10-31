# Corpus and literature search

Introduced 31.10.2026, after two hard lessons in one evening: a catalogue of 19 "documented cases" contained six
references that do not exist, and two of the real ones described something else; and I reported "read the literature"
when I had only confirmed that the papers exist.

This page is the full rule. The contract keeps the short version and a link.

---

## The rule

**A claim that "the literature says X" is made after searching the corpus, not from memory.**

```
python scripts/lit_index.py --search "<query>"          # search all full texts, with context
python scripts/lit_index.py --search "<query>" --doc davis
python scripts/lit_index.py --stats                     # what is in the corpus
python scripts/corpus_manifest.py --write               # rebuild the manifest
```

## What the corpus is

| part | where |
|---|---|
| full texts (extracted from PDF or fetched as XML) | `library/corpus/texts/*.txt` |
| manifest: DOI, year, why it is here, read status | `library/corpus/manifest.json` |
| inverted index over stemmed words | `library/corpus/index.json` |

The manifest is maintained by hand in `scripts/corpus_manifest.py` (`KNOWN` dict) — a paper enters the corpus only with
a DOI, a year, a reason and a read status.

## Read status is not the same as having the file

| status | meaning | may be cited? |
|---|---|---|
| `read` | full text read end to end | yes |
| `partial` | abstract plus the sections that matter | yes, with the limitation stated |
| `unread` | downloaded, not read | **no** |

Conflating "the file is there" with "the work has been read" is exactly the failure this page exists to prevent. On
31.10 the corpus held nine texts: five read, two partial, two unread — and that distinction was reported as it was.

## What is not in the corpus goes to the librarian's queue

`lab/lit-queue.json`, status `new`, with fields:

- `question` — what we need to know, phrased so that a search can answer it;
- `why` — which of our results or claims depends on the answer;
- `target` — the experiment or section that needs it;
- `deliverable` — the full text in `library/corpus/texts/` plus an entry in `KNOWN`.

`python scripts/lit_check.py --list` shows the queue; `--done` closes an item.

## Existence is checked separately from content

```
python scripts/verify_references.py --query "<title>"
python scripts/verify_references.py --file refs.json --write out.json
```

Crossref for journals and conferences, DataCite for repositories (Zenodo, Dryad). This catches invented references —
six of twelve in one run on 31.10, every one of them dated 2026. It does **not** catch a real paper described wrongly;
only reading does.

## What good search looks like

The extractor joins PDF text into long paragraphs, so the searcher splits documents into overlapping windows and ranks
them by how many query terms they contain. It prints three windows per document.

Example that paid for the tool on its first day:

```
python scripts/lit_index.py --search "spatial resolution diffusion confound" --doc davis_2023
```

returned the U-Skate equations showing that "spatial resolution" there is a `1/Δx²` coefficient on the diffusion terms —
which revealed that our own "grid 96 versus 128" comparison changes the physics rather than the accuracy (see
§10dx of the plan).
