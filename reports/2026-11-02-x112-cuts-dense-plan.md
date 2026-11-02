# X112 — the ladder and the specificity at three cuts, on the same genealogies and the same frames

**Why.** Two results in this block are stated at a single excursion cut (0.20): the definition ladder (X101, dense version X108) and the
specificity gap (X102, dense version X108). X99 showed the **half-life** is cut-bound by a factor of three and even reverses between
inflows, so "every heredity number in this line is a statement about excursion sets at 0.20" is already written down. What has never
been tested is whether *the ladder* and *the gap* move with the cut the same way the level does.

The dense series makes this analysis-only: `_x108_fields` holds a field at **every logged step**, so a structure's area at another cut
can be measured on the very frame where its genealogy was built. The uids are those of the 0.20 run — identity is fixed, only the size
definition changes, which is exactly the comparison the ladder makes.

## 1. Manipulation is connected

X108's twenty runs (seeds 301–310, two inflows), `uid_outcomes` for peak frame and centroid of every uid, `uid_pairs` for the
genealogy, `_x108_fields/<run>_t<step>.npy` for the frames. For every uid and every cut ∈ {**0.15, 0.20, 0.25**}: the area of the
4-connected component of `v > cut` that contains the uid's peak centroid at its peak frame. The nearest non-ancestor (X102's control) is
taken from the same frame.

Connectedness: at least **300 pairs** per cell and per cut. A uid whose peak pixel falls below the cut is **undefined at that cut** and is
dropped for that cut only — the count is reported, because that is the honest cost of a higher cut.

## 2. Positive control fires (numeric)

At `cut = 0.20` the recomputation must reproduce X108's excursion-set coefficient within **0.02**: 0.548 at 0.030 and 0.480 at 0.040, and
the control **fires if** both land inside that band. This is the check that measuring areas off saved fields reproduces the logger's own
areas; if it fails, the frame-to-centroid path is wrong and nothing below is comparable.

## 3. Readout exists and varies

Per cell and cut: `ρ₁(parent, child)`, the specificity gap (parent minus nearest non-ancestor), the median area, and the coverage
(pairs with both areas defined). Variation exists by construction — X99 measured a factor of three at half-life between 0.15 and 0.25, and
the median excursion area at 0.20 is 83 and 400 cells in the two cells.

## 4. Sensitivity arithmetic

1 900–2 200 pairs per cell, so the standard error of a coefficient is 0.021–0.023; the paired structure across cuts removes the
world-to-world variation, as in X102. The declared resolution is **0.10** for a level and **0.15** for a gap, matching the bars X101 and
X102 used.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 pairs at any cut or if the 0.20 control misses its ±0.02 band.

**The level is cut-bound** if `ρ₁` varies by ≥ 0.10 across cuts in at least one cell; **the level is cut-stable** if it varies by ≤ 0.05
everywhere.
**The gap is cut-bound** if the specificity gap varies by ≥ 0.15 in at least one cell; **the gap is cut-stable** if it varies by ≤ 0.10
everywhere.
**Mixed** otherwise, printed per cell and cut — and the two statements are reported separately, because the day's finding is precisely
that the level and the gap can move independently.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs and their saved fields (a field at every logged step) |
| readouts | component area at 0.15 / 0.20 / 0.25 on the uid's own frame; `ρ₁` and the specificity gap per cut |
| controls | 0.20 reproduction within ±0.02 of X108; ≥ 300 pairs per cell and cut |
| artifact | `E09_pond/l1_field_x112_cuts_dense.json` |

## Checklist

- [x] connected (300 pairs per cell and cut; undefined uids counted per cut)
- [x] positive control numeric (0.20 reproduces 0.548 / 0.480 within ±0.02)
- [x] readout exists and varies (X99's factor of three; medians 83 / 400 cells)
- [x] sensitivity computed (§4: SE 0.021–0.023, resolution 0.10 for a level and 0.15 for a gap)
- [x] refusal rule written, with cut-stable as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 21:36 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
