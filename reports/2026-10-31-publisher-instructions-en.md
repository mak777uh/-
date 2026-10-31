# Publisher instructions: version 1.5 (English edition)

A short instruction for whoever uploads. The laboratory-side review is in `reports/2026-10-31-publication-package.md`
(not needed for uploading).

---

## 0. Why a new version

Record `10.5281/zenodo.23838564` (v1.4) was published correctly, but the uploaded article is **one edit behind** the
repository: it lacks the lifetime-share sentence (22 % / 71 %, 75 % / 24 %), the DOI line, and it states the median
cell count as 2131 instead of **2131.5**. The uploaded archive also differs from the current build.

Version 1.5.1 fixes both and adds the **English edition**, and it carries one substantive strengthening: the claim that
an organism builds a model of its own trace (rather than of the world) is now supported by an **intervention**, not by
correlation alone. With consumption severed (`ghost_no_consumption`) the predictive dependence collapses from
**+0.0362 in 10 of 10 runs** to **0.0000 in none of 8**. The Russian v1.4 does not contain this control.

---

## 1. What to upload — three files

| file | what it is |
|---|---|
| `articles/028-field-without-stipulated-objects.md` | **English edition, v1.5** — the primary text |
| `articles/028-pole-bez-zadannyh-obektov.md` | Russian original, v1.4 (kept for the record) |
| `_exports/logs-2026-10-31.zip` | data and code; `README-BUNDLE.md`, `LICENSE`, `MANIFEST.json` inside |

**Archive checksum (must match):**
`da7c65dc7d84303b…` — full value in the build output, and it is stable because the instructions are not inside the
archive. Verify with:

```
python scripts/make_logs_bundle.py --verify logs-2026-10-31.zip
# expected: files 1656, broken 0, missing 0, content hash matches: True
```

---

## 2. How: new version of the existing record

1. Open `https://zenodo.org/records/23838564`.
2. Press **New version** (not "New upload") — this keeps the concept DOI `10.5281/zenodo.23838563` and the link to
   `10.5281/zenodo.23669737`.
3. Remove the two old files, upload the three files from §1.
4. **Version:** `1.5.1`. **Publication date:** `2026-10-31`.
5. Type: **Preprint**. Language: **English** (the Russian edition is an attachment; if Zenodo allows only one language,
   set English and say in the description that the Russian original is included).
6. License: **CC0 1.0** (unchanged).
7. Related identifier `10.5281/zenodo.23669737` — keep `isSupplementTo`.
8. Preview, then **save as draft** and show the owner.
9. Publish only after the owner's explicit "ok".

---

## 3. Metadata (copy as is)

**Title:**
`A field without stipulated objects: how a component counter passed itself off as diversity`

**Author:** Vladimirov, Ilia Sergeevich (Владимиров Илья Сергеевич)

**Description:**

> Organisation in a digital medium, and its boundaries. In a continuous medium with no stipulated objects (the
> Gray–Scott model) organisation arises, inheritance and selection are measurable, but the number of "structures" turns
> out to measure the fraying of a single percolation cluster rather than a number of bodies: durable structures are the
> same in heterogeneous and homogeneous worlds (1.3 versus 1.2), form does not transfer between environments (8–11 %
> keep their class, 50–67 % die), and no measured property predicts survival. The earlier null results are explained by
> the world being uninhabitable by a constant: income was capped at 0.008 per step against a cost of 0.03; with the
> coefficient corrected the world becomes habitable (10 of 10 runs, median 2131.5 cells, range/median 3.54 %), and in
> it a self-model evolves but not a world-model: the organism's state predicts the resource it consumes itself
> (+0.0386 at high cost) and carries exactly zero information about resource in cells it does not touch (0.0000).
> Seven of our own conclusions are retracted, two weakened and two rewritten after a code check; every number is
> recomputed from its aggregate by a script in the attached archive. English edition of v1.4; the Russian original is
> included.

**Keywords:**
`artificial life; reaction-diffusion; Gray-Scott; percolation; individuality; selection; habitability; mutual information; reproducibility; negative results`

---

## 4. Do not

- do not create a new record — it must be a **new version** of the existing one;
- do not change the license: **CC0 1.0** is the owner's decision;
- do not modify the archive after upload;
- do not add model weights (`.pt`) — they are absent by design;
- do not list agents' service labels (`lead`) as authors.

---

## 5. Send back

1. The **version DOI** (a new number under the same concept DOI).
2. The link.
3. Confirmation that **three** files are present and the license is CC0.

We will then write the DOI into `CITATION.cff`, the article and the reports, and close the publication item.
