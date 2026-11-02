# X99 — does the memory map belong to the world or to the excursion cut? Two inflows at two other thresholds

**Why.** X98 was registered to ask this and voided itself on a category error: the **angular** map (`q'`, `s`) is computed from the
continuous field and has no threshold at all, so masking it produced four different statistics rather than four cuts of one. What *is*
threshold-dependent is the **memory** map: peak area is defined on `v > threshold`, and every half-life in §10ff–§10fl is built from
those areas. The stored genealogies were made at 0.2 during the run, so no re-analysis can answer it — it needs runs at other cuts.

This is the reviewer's first question about the map, and it currently has no answer.

## 1. Manipulation is connected

Two inflows — `F = 0.030` (lattice, committed half-life 1.16) and `0.040` (percolating, 2.08) — each at **two thresholds**
(`--threshold 0.15` and `0.25`), ten worlds per cell, seeds 281–290, flags otherwise identical to X87/X88 (split identity, 50-step
logging, field at 6000). The 0.20 values are already measured and are the reference, not a cell to re-run.

Connectedness: every cell must still carry ≥400 lag-1 pairs and ≥10 mean components at its cut; otherwise the instrument does not work
at that threshold and the cell is void. The two thresholds are chosen so that the component count changes materially (a lower cut admits
more cells, a higher one fewer) — if the counts are identical at 0.15 and 0.25 the manipulation did not bite.

## 2. Positive control fires (numeric)

The reference cells are committed and fixed: **half-life 1.16 at `F = 0.030` and 2.08 at `F = 0.040`** (X87/X88, per-world medians, twenty
worlds). **The control fires if** both new cells at each threshold produce a half-life that can be fitted in at least 7 of 10 worlds —
i.e. the estimator survives the cut at all. A threshold at which the estimator cannot be fitted is not a test of robustness.

## 3. Readout exists and varies

Per world: `rho1..3`, per-world `lambda` and half-life, peak-area medians, component counts. Primary: the per-world median half-life per
cell, against the committed 0.20 reference of the same inflow.

## 4. Sensitivity arithmetic

Ten worlds per cell give a standard error of the median half-life of ≈0.2 divisions (per-world spread ~0.6 in X87/X88). The declared
resolution is therefore **0.4** divisions — the difference between "the map survives the cut" and "the map moves". Cost: 40 runs at
~90 s ≈ **60 minutes**.

## 5. Refusal rule (registered before the run)

**Void** (cell-level) if fewer than 400 pairs, fewer than 10 mean components, or fewer than 7 fittable worlds at that cut; and void if the
component counts at 0.15 and 0.25 are identical (the manipulation did not bite).

**Robust to the cut** if `|half(0.15) − half(0.20)| <= 0.4` **and** `|half(0.25) − half(0.20)| <= 0.4` **in both inflows**.
**Cut-dependent** if either threshold moves the half-life by **≥ 0.8** in either inflow.
**Mixed** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.030`, `0.040` |
| thresholds | `--threshold 0.15`, `0.25` (0.20 is the committed reference) |
| worlds | 10 per cell, seeds 281–290, `--init-jitter` |
| identity, logging | `--split-new-uid`, `--sample-every 50` (as X87/X88) |
| grid, step, horizon | 96, `dt = 1.0`, 6000; field saved at 6000 |
| artifact | `morphogenesis/experiments/L1_field/x99_f{030,040}_thr{015,025}_s281-290.json`, aggregate `l1_field_x99_threshold_memory.json` |

## Checklist before the series

- [x] connected (pairs, components, and a real difference in component counts between the two cuts)
- [x] positive control fires (numeric: fittable in ≥7 of 10 worlds at each cut)
- [x] readout exists and varies (half-life differs by ~0.9 between the two inflows at 0.20)
- [x] sensitivity computed (§4: SE 0.2, resolution 0.4)
- [x] refusal rule written, with "cut-dependent" as a real outcome
- [x] both conventions named (identity, logging)

## Status

Registered 2026-11-02 16:20 MSK, before the series. Forty runs, ~60 minutes.

доска: принято 0, отклонено 0, отложено 0.
