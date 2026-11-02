# X85 — does the symmetry of the pattern carry the memory? (the knob the environment can actually turn)

**Why.** X84 showed that in this box the medium has one morphological period (~12 cells, the same with and without forcing) and that
what the environment changes is the **symmetry**: the fraction of power locked to the imposed checkerboard diagonals, `s`, runs from
0.38 at `F = 0.025` to a plateau of 0.92 at `F >= 0.040` (35 worlds, Spearman 0.687). Everything the two-scale series tried to do —
impose a second wavelength — turned out to move the forcing line while the morphology stayed put.

So the question that survives from that whole programme, stated in the units the medium actually has: **does the size memory depend on
`s`?** If a pattern locked to the forcing is rigid, its structures' sizes should follow the forcing rather than the lineage, and the
inherited component of size should shrink as `s` rises. That is a falsifiable prediction and it is the last piece the field line
needs before it can say what in this medium is inheritable at all.

## 1. Manipulation is connected

Three inflows where `s` is known to differ — `F = 0.025` (median 0.38), `0.030` (0.52), `0.035` (0.78) — eight jittered worlds each,
same flags as X71/X74 so the worlds are comparable. The manipulation is **not** a flag: `s` is measured per world from the saved field,
and the design relies on its **world-to-world spread inside a cell** (0.35–0.60 at 0.025, 0.64–0.81 at 0.035), which is what the
correlation uses. Connectedness is checked by that spread: if a cell's `s` range is narrower than 0.05, there is nothing to correlate
and the cell is void.

## 2. Positive control fires (numeric)

The `F = 0.030` cell must reproduce X74's single-scale reference and the `F = 0.035` cell must reproduce X71's symmetry.
**The control fires if** the 0.030 cell's pooled `rho1` lies in **[0.45, 0.56]** (X74: 0.507) and the 0.035 cell's median `s` lies in
**[0.64, 0.81]** (X71: 0.777). If either misses, the series is void: the worlds would not be comparable with the series the memory
numbers come from.

## 3. Readout exists and varies

Per world: symmetry `s` (`P_diag/(P_diag+P_axis)` at the prescribed diagonals), `rho1/rho2/rho3` from `uid_pairs` at 50-step logging,
per-world `lambda` and half-life (both ratios positive), components, and the median structure area. Memory is read with the estimator
fixed in §10ff: `rho1` is the **primary level**, half-life secondary with the per-world median and its range printed.

## 4. Sensitivity arithmetic

Within a cell, `sd(s)` ≈ 0.07–0.10 and `sd(rho1)` ≈ 0.06–0.10 (X71 and X76 spreads). With 8 worlds the standard error of a Spearman
coefficient is ~0.13, so a within-cell `|rho| = 0.7` is 2.6σ and is the declared within-cell resolution; pooled over 24 worlds the
resolution is `|rho| = 0.45`. Cost: 24 runs at ~110 s ≈ **45 minutes**.

## 5. Refusal rule (registered before the run)

**Void** if a cell has <10 components, <400 lag-1 pairs, a field that is dead (std < 0.01), or an `s` range narrower than 0.05, or if
the §2 control misses its bands.

**Symmetry carries memory** if, in at least **two of three** cells, Spearman(`rho1`, `s`) over the eight worlds is **<= −0.5** (memory
shorter where the pattern is more locked to the forcing), and the pooled partial correlation of `rho1` with `s` controlling `F` is
**<= −0.45**.

**Symmetry does not carry memory** if the within-cell coefficient is **>= +0.5** in at least two cells, or if **all** within-cell
coefficients lie in **[-0.3, +0.3]**.

**Inconclusive** otherwise, printed in full, with the per-cell coefficients and the partial correlation.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.025`, `0.030`, `0.035`, `k = 0.06` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5`, `const_ones` signal (as X71) |
| worlds | 8 per cell, `--init-jitter`, seeds 191–198 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every **50** steps; field at 6000 |
| artifact | `morphogenesis/experiments/L1_field/x85_f{025,030,035}_s191-198.json`, aggregate `l1_field_x85_symmetry_memory.json` |

## Checklist before the series

- [x] connected (`s` measured per world; the design uses its within-cell spread, and a narrow spread voids the cell)
- [x] positive control fires (numeric bands, §2)
- [x] readout exists and varies (`s` and `rho1` both vary; both were measured on stored fields already)
- [x] sensitivity computed (§4)
- [x] refusal rule written, including the case "no spread to correlate"

## Status

Registered 2026-11-02 04:45 MSK, before the series. Twenty-four runs, ~45 minutes. Runs after X82 frees the lane.

доска: принято 0, отклонено 0, отложено 0.
