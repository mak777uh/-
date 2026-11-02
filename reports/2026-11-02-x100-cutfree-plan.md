# X100 — does the heredity result survive a size that needs no excursion cut?

**Why.** X99 showed the memory map is definition-bound: moving the excursion cut from 0.20 to 0.15 or 0.25 moves the half-life by a
factor of three and reverses the ordering between inflows, because "peak area" is defined by that cut. The honest next step is not
another cut but a **size that needs none**: for each structure, the integral of `v` over the basin it sits in, with the basin boundary
taken at **half of that structure's own maximum** rather than at a global threshold. That is the "area at half maximum" idea from
`reports/2026-11-02-x99-cut-dependent.md`, and the question is whether the heredity of size survives the change of definition.

This needs the field at the moment each structure peaks, which the runner can now do (`--save-fields-every`, added 02.13 and anchored).

## 1. Manipulation is connected

Two inflows — `F = 0.030` (lattice) and `0.040` (percolating) — ten worlds each, seeds 291–300, flags identical to X87/X88 (split
identity, 50-step logging) **plus** `--save-fields-every 50`, so every logged snapshot has a field. The reference values are the
committed threshold-0.20 readings of the same inflows: ρ₁ = 0.549 at 0.030 and 0.471 at 0.040 (twenty worlds each).

Connectedness: every world must yield at least 100 ancestor-descendant pairs, and the cut-free size must be computable (a basin found)
for at least 80 % of the uids involved. Otherwise the cell cannot answer.

## 2. Positive control fires (numeric)

The same code, applied to the **threshold-defined** area, must reproduce the committed ρ₁ of the same inflow within 0.05. **The control
fires if** the recomputed threshold-based ρ₁ at 0.030 lands in **[0.50, 0.60]** and at 0.040 in **[0.42, 0.52]** (committed 0.549 and
0.471, twenty worlds; these ten-world cells have a standard error of ≈0.10, hence the ±0.05 band on the difference). If the control
misses, the pairing or the field parsing differs from the committed analysis and the comparison is void.

## 3. Readout exists and varies

Per world, twice — once with the threshold-0.20 area (reference) and once with the cut-free size:

- `S_cf(uid)` = Σ `v` over the basin around the uid's centroid at its peak snapshot, the basin being the connected set where
  `v ≥ 0.5 · max(v in that region)`;
- `A_cf(uid)` = the number of cells in that basin (so the two candidate definitions can be compared separately);
- `ρ₁` = Spearman(ancestor, descendant) at lag 1 for each definition.

The readout of interest is the **difference between the two ρ₁ values within the same worlds**, which removes the world-to-world
variation that limits the comparison across series.

## 4. Sensitivity arithmetic

Within ten worlds, ρ₁ has a standard error of ≈0.10. The paired comparison (same worlds, two definitions) has a much smaller error —
the two ρ values share their pair sets — so a difference of **0.10** is resolvable at roughly 2σ per cell and 0.07 pooled over two
cells. Cost: 20 runs at ~120 s with per-step fields ≈ **45 minutes**, ~90 MB of fields.

## 5. Refusal rule (registered before the run)

**Void** (cell-level) if fewer than 100 pairs, if the basin is found for fewer than 80 % of uids, or if the §2 control misses.

**Heredity survives the change of definition** if the pooled ρ₁ under the cut-free size stays within **0.10** of the threshold-based ρ₁
in both cells.
**Heredity is definition-bound too** if it moves by **≥ 0.20** in at least one cell, in either direction.
**Mixed** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.030`, `0.040` |
| worlds | 10 per cell, seeds 291–300, `--init-jitter` |
| fields | `--save-fields-every 50` (every logged snapshot) |
| identity, logging | `--split-new-uid`, `--sample-every 50` (as X87/X88) |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| reference | ρ₁ = 0.549 (0.030) and 0.471 (0.040), threshold 0.20, twenty worlds |
| artifact | `morphogenesis/experiments/L1_field/x100_f{030,040}_s291-300.json`, aggregate `l1_field_x100_cutfree.json` |

## Checklist before the series

- [x] connected (100 pairs, 80 % basin coverage)
- [x] positive control fires (numeric bands from the committed ρ₁, §2)
- [x] readout exists and varies (ρ₁ 0.39–0.55 across the line)
- [x] sensitivity computed (§4: paired difference 0.10 at ~2σ)
- [x] refusal rule written, with "definition-bound" as a real outcome
- [x] both conventions named (identity, logging) and the new field flag anchored

## Status

Registered 2026-11-02 19:00 MSK, before the series. Twenty runs, ~45 minutes.

доска: принято 0, отклонено 0, отложено 0.
