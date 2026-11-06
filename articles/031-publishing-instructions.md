# Publishing instructions — article 031 (for the person who performs the deposit)

This is the map for whoever uploads the article. It says what exists, where it lies, what is still missing, how to check
everything before uploading, and what must not be changed.

**Status: draft, ready to deposit once the author says so.** The article text, its figures, its PDF, the data archive
and the number check all exist and pass. The independent review exists but was written by the lead (self-review), not
by a second pair of eyes — see section 6. **Do not upload anything until the author says so in writing.**

- **Author (and the only person to ask):** Ilya Vladimirov.
- **Licence:** CC BY 4.0 (the standing default; if the author names another licence, change it in `zenodo.json` and `LICENSE`
  first — neither file exists for this article yet).
- **Version of the article:** v1.0.

## 1. What this article is

A research article with one negative and one positive result, both about the same pond world:

- **Negative:** four independent tests of inherited adaptation all give null (S6 double flip, S7 flip to a new environment,
  S9 heritable mobility, S10 heritable directionality). Recovery after an environment change is dispersal and survival, not
  selection on a trait.
- **Positive, with a measured limit:** local resource-greedy movement does help (0.475 against 0.357 baseline on a patchy
  environment), but the gain decays as the rich zone fills (advantage vs rich-zone occupancy, r = −0.57 over 18 points).
- **Two refuted variants:** smoothing the signal does not help; refreshing the rich zones does not restore the advantage.
- **Three withdrawn experiments**, named in the article as invalid by construction rather than as negative results.

The article follows the sequence's own shape: last time we found this and decided to check that; here are the results; here is
where we move next.

## 2. Where everything lies

Repository: `C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo`

| what | where | state |
|---|---|---|
| the article (Markdown) | `articles\031-directionality-and-inheritance-in-the-pond.md` | **ready** |
| the three figures, PNG (reading) and PDF (typesetting) | `articles\031-figures\` | **ready** |
| the machine check of every printed number (20 checks) | `scripts\check_article_031_numbers.py` | **ready** |
| the figure builder (reads artifacts only) | `scripts\make_article_031_figures.py` | **ready** |
| the artifacts the article cites | `morphogenesis\experiments\E09_pond\s{6,7,9,10,12,13,14,15,16}_*.json` | **ready** |
| the reports behind each section | `reports\2026-11-06-s{4,5,6,7,9,10,11,12,13,14,15,16,17}-*.md` | **ready** |
| the article as PDF | `articles\031-directionality-and-inheritance-in-the-pond.pdf` | **ready** |
| the data archive to upload | `_exports\031-directionality-and-inheritance-v1.0.zip` (about 0.9 MB, 32 files) | **ready** |
| the same archive, unpacked for inspection | `_exports\031-directionality-and-inheritance\` | **ready** |
| the review of the numbers | `lab\reviews\2026-11-06-031-numbers.md` (verdict: holds with caveats) | **ready, self-review** |
| the script that rebuilds the PDF | `scripts\make_article_031_pdf.py` | **ready** |
| the script that rebuilds the archive | `scripts\build_article_031_package.py` | **ready** |
| reference list file | — | **MISSING**; the three context references are cited inline in §2 |

## 3. How to check everything before uploading

Run from the repository root. All three must pass:

```bash
python scripts/check_article_031_numbers.py    # expect: 0 failures out of 20 checks
python scripts/make_article_031_figures.py     # rebuilds the three figures from artifacts
python scripts/check_links.py                  # expect: битых: 0
```

`check_article_031_numbers.py` re-reads the artifacts and compares them with the numbers the prose states. It is the reason
the text cannot drift from the data. If it reports a failure, **do not upload** — report it to the author instead.

## 4. What must not be changed

1. **No number may be edited by hand.** If a number looks wrong, the artifact is right and the article is fixed by rerunning
   the checker and correcting the prose — never the other way round.
2. **The withdrawn experiments stay withdrawn.** S5/C, S11/D and the first S6/C3 attempt are named in §4.3 as invalid by
   construction. Removing that section would turn an honest record into a misleading one.
3. **The three nulls stay nulls.** The article does not claim that inheritance is impossible in general — only that it does
   not appear in this setup. Do not strengthen the wording.
4. **No "life", "consciousness" or "intelligence" claims.** The project's own contract forbids them; the article speaks of an
   observed class of behaviour and its boundary.
5. **The article is not deposited until the author says so in writing.** Nothing has gone outward.

## 5. Depositing (only after section 6 is complete and the author agrees)

1. Create the archive (needs the script from section 6), unpack it once and verify the file count and that
   `check_article_031_numbers.py` passes inside the unpacked copy.
2. Zenodo: start a new upload — https://zenodo.org/uploads/new
3. Fill: title from the article's first line; authors "Ilya Vladimirov"; version "v1.0"; licence CC BY 4.0; description =
   the article's abstract verbatim.
4. Upload the PDF, the figures, and the data archive.
5. Reserve the DOI, put it into the article header and into `articles/README.md`, rebuild the PDF, re-upload.
6. Publish, then record the DOI in `lab/registry.json` and in the article's changelog.

Zenodo API documentation: https://developers.zenodo.org/

## 6. What is still missing (before a deposit)

| item | state |
|---|---|
| **PDF** | **done** — `scripts/make_article_031_pdf.py` (same LibreOffice renderer as 030) |
| **data archive** | **done** — `scripts/build_article_031_package.py`, 32 files, 19 artifacts, sha256 manifest verified |
| **review** | **done but not independent** — `lab/reviews/2026-11-06-031-numbers.md`, verdict "holds with caveats", written by the lead. The repository's contract wants a second pair of eyes; if one is available, a reviewer should re-check it before deposit. |
| **reference list** | **not produced** — the three context references are cited inline in §2. A standalone verified list (Crossref/DataCite check) would be needed if the depositor requires one. |

The review's caveats have already been written into the article: §4.1 now says the last-window gap (+0.036) is within
seed scatter and that the −0.57 correlation has no p-value because its points are serially dependent; §4.2 now says the
four tests are independent by mechanism, not by data.

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

The article is written and its numbers are verified by machine, but it is **not** ready to upload: the PDF, the data archive
and the independent review do not exist yet, and the author has not authorised a deposit. When those three exist, run the
three checks in section 3, then follow section 5. If anything in the article looks wrong, the artifacts are the truth — report
the discrepancy to the author rather than editing a number.
