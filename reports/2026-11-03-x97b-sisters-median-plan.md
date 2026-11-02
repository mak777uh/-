# X97b — is the second-generation sister advantage branching arithmetic or a lineage effect?

**Why.** X97 showed the larger sister's granddaughters are larger on average (+12.90 cells in the lattice, CI 10.11–15.80). A mean is sensitive
to how many grandchildren a branch produces: a larger structure has more cells that can divide, so her line may simply branch more, and the
mean is pulled up by the number of branches rather than by their individual size. Two readouts separate the explanations:

- **the median** granddaughter per branch is insensitive to the number of branches;
- **the count** of grandchildren per branch measures the branching directly.

## 1. Manipulation is connected

The same sister pairs as X97 (X108's dense logs, 282 in the lattice and 186 in the maze), with at least one granddaughter on each branch.

## 2. Positive control fires (numeric)

Heredity on the same worlds `≥ 0.35` in both cells, and the **mean** difference must reproduce X97's value within **5 %** (12.90 and
170.91 cells) — the control fires if both hold. This is a re-read of the same artifacts under a new readout, so any drift means the pairing
changed.

## 3. Readout exists and varies

Per cell: the mean difference (X97's number, recomputed), the **median** difference (per pair, median of each branch, then paired), the
mean number of grandchildren per branch for the larger and the smaller sister, and the mean granddaughter area **per grandchild** (the
unweighted mean, which removes branch-count weighting entirely). Variation exists: X97's means are 12.90 and 170.91 and the branch counts
per sister range from 1 to several.

## 4. Sensitivity arithmetic

~280 and ~190 pairs; the standard error of a paired median difference is larger than of a mean, roughly 1.25×, so the resolution is
**0.15 × mean** rather than 0.05 cells — for the lattice about 2 cells. A median difference below half the mean difference is treated as
evidence that the mean is carried by branch counts.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 100 pairs or if the mean does not reproduce X97 within 5 %.

**Branching arithmetic dominates** if the median difference is `≤ 0.5 ×` the mean difference **and** the larger sister has at least 10 %
more grandchildren per branch.
**A lineage effect is needed** if the median difference is `≥ 0.5 ×` the mean difference.
**Mixed** otherwise — for instance a median holding while the branch counts do not differ, which would point at a third explanation (the
granddaughters' *sizes* differ without their number differing).

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs, the same pairs as X97 |
| readouts | mean, median, per-grandchild mean, grandchildren per branch |
| controls | heredity ≥ 0.35; the mean reproduces X97 within 5 % |
| artifact | `E09_pond/l1_field_x97b_sisters_median.json` |

## Checklist

- [x] connected (the same pairs as X97, 282 / 186)
- [x] positive control numeric (heredity ≥ 0.35; the mean within 5 % of X97)
- [x] readout exists and varies (means 12.90 / 170.91; branch counts 1–several)
- [x] sensitivity computed (§4: median SE ≈ 1.25× the mean's, resolution 0.15 × mean)
- [x] refusal rule written, with "a lineage effect is needed" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-03 00:02 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
