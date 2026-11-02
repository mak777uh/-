# X112b — the ladder and the specificity at cuts 0.15 and 0.25, on the same worlds as the 0.20 reference

**Why.** X112 tried to get a cut sweep cheaply by re-measuring areas off saved fields and voided on its own control: identity is the
logger's labeling of the field at the cut under test, and no anchoring scheme reproduced the 0.20 numbers. X99's route is the one that
works — new runs at each threshold.

**And it is a paired design, not a new sample.** `--threshold` belongs to the observer, not to the physics: it decides which pixels count
as a structure, not how the field evolves. So running seeds 301–310 at `--threshold 0.15` and `0.25` reproduces the **same twenty
worlds** X108 measured at 0.20, with a different observer — the same trick X99 used on the sparse series. The comparison at 0.20 is
therefore X108's own number, not a borrow from another sample.

## 1. Manipulation is connected

Twenty runs at `F = 0.030` (seeds 301–310, X100's flags otherwise), ten with `--threshold 0.15` and ten with `--threshold 0.25`. The
0.20 reference is X108's `x101b` aggregate: `ρ₁ = 0.548`, specificity gap 0.302, basin coverage 0.979.

Connectedness: every run must keep **≥ 10 components** at step 6000 under its own threshold, and each cut must give at least **300
ancestor–daughter pairs**. A cut that dissolves the population (0.25 was the harshest in X99) is reported as unreadable rather than as a
null.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The world is unchanged:** each run's field must be independent of the threshold — checked by comparing `uid_pairs` structure and the
   series' component counts against X108's runs at the same seeds; the control **fires if** the number of logged steps and the field's
   peak amplitude at step 6000 agree run-by-run within 0.01 (the ODE does not see the threshold).
2. **The 0.20 reference is the published one:** 0.548 at `F = 0.030`, quoted from `l1_field_x101b_dense.json`, not recomputed.

## 3. Readout exists and varies

Per cut: `ρ₁` (parent–daughter area), the specificity gap (parent minus nearest non-ancestor, X102's rule), the median area, the pair
count and the coverage. Variation exists by construction: X99 measured a factor of three in the half-life between 0.15 and 0.25, and the
median excursion area at 0.20 is 83 cells in this cell.

## 4. Sensitivity arithmetic

Ten worlds per cut, 300–2 200 pairs, so the standard error of a coefficient is 0.021–0.058. The declared resolution is **0.10** for the
level and **0.15** for the gap, as in X112 and X102. Because the worlds are shared with the 0.20 reference, the comparison is paired and
the world-to-world variation cancels.

## 5. Refusal rule (fixed before the run)

**Void** if a cut keeps fewer than 10 components in any run, gives fewer than 300 pairs, or if the world-unchanged control fails.

**The level is cut-bound** if `|ρ₁(cut) − 0.548| ≥ 0.10` for at least one cut; **cut-stable** if both are `≤ 0.05`.
**The gap is cut-bound** if `|gap(cut) − 0.302| ≥ 0.15` for at least one cut; **cut-stable** if both are `≤ 0.10`.
**Mixed** otherwise, per cut — the two statements are reported separately because this block's finding is that they can move
independently.

The direction X112's four anchoring schemes suggested (higher at 0.15, lower at 0.25) is on record before the runs; it is a prediction to
check, not a result.

## Design summary

| factor | value |
|---|---|
| runs | 20 (seeds 301–310 × thresholds 0.15 and 0.25), `F = 0.030`, ~105 s each |
| reference | X108 at 0.20: `ρ₁ = 0.548`, gap 0.302 |
| readouts | `ρ₁`, the specificity gap, median area, pairs, coverage at each cut |
| controls | world-unchanged check against X108's runs; the 0.20 reference is quoted, not recomputed |
| artifact | `E09_pond/l1_field_x112b_cuts.json` |

## Checklist

- [x] connected (≥ 10 components, ≥ 300 pairs, world-unchanged check)
- [x] positive control numeric (ODE independent of the threshold, run-by-run within 0.01)
- [x] readout exists and varies (X99's factor of three; median area 83 cells at 0.20)
- [x] sensitivity computed (§4: SE 0.021–0.058, resolution 0.10 / 0.15, paired across cuts)
- [x] refusal rule written, with cut-stable as a real outcome
- [x] stated: the same worlds as the reference, because the threshold is an observer parameter

## Status

Registered 2026-11-02 21:44 MSK, before the runs.

доска: принято 0, отклонено 0, отложено 0.
