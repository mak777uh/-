# X101 — basins by steepest ascent: a size with no level set at all

**Why.** X100 showed heredity lives in a structure's **skirt** (the extent at an absolute cut) rather than in its **core** (the basin at
half its own maximum): with the same pairs, ρ₁ fell from 0.531 / 0.384 to 0.176 / 0.058. But X100's boundary was still a definition —
relative to each structure instead of global. The only version that answers "what is the size of a structure when nothing is cut" is a
basin defined by the field's **own topology**: assign every cell to the local maximum reached by steepest ascent, and take the basin's
area. No threshold, no fraction, no free parameter.

This is an **analysis of stored snapshots** — the twenty X100 runs already saved a field at every logged step — so it needs no GPU.

## 1. Manipulation is connected

Two inflows (`F = 0.030`, `0.040`), ten worlds each, same artifacts as X100. For every uid the analysis takes the snapshot where its
logged area peaks, locates its centroid, and walks the steepest-ascent path from that cell to its local maximum; the basin is every cell
that reaches the same maximum. Connectedness: the basin must be found for at least **80 %** of uids and the cell must carry at least
**100** lag-1 pairs.

## 2. Positive control fires (numeric)

Two checks, both numeric and both computable before the comparison:

1. the threshold-based ρ₁ recomputed on the same pairs must reproduce X100's own value for that inflow within **0.02** (X100: 0.531 and
   0.384) — same code, same pairs, so this is an implementation check;
2. the basins must **partition the field**: the sum of basin areas must equal the number of cells above the numerical floor times the
   fraction of cells that have a basin, i.e. no cell may be in two basins and none may be lost. A partition failure voids the series.

**The control fires if** both hold.

## 3. Readout exists and varies

Per cell: ρ₁ with the threshold-0.20 area, ρ₁ with the basin area, and the paired difference on the same pairs. Medians of both size
measures are reported, so the geometry is visible: how large is a topological basin compared with the excursion component?

## 4. Sensitivity arithmetic

Same pairs as X100, so the paired difference has the same resolution as there: a difference of **0.10** is resolvable at ~2σ per cell,
0.07 pooled. Cost: **no runs**, ~1 minute of CPU per cell.

## 5. Refusal rule (registered before the run)

**Void** if the partition check fails, if basin coverage is below 80 %, if fewer than 100 pairs, or if the recomputed threshold ρ₁
differs from X100's by more than 0.02.

**Heredity is carried by extent** if the basin-area ρ₁ stays within **0.10** of the threshold-area ρ₁ in both cells.
**Heredity needs the cut** if it falls by **≥ 0.20** in at least one cell — then the honest statement is that the inherited quantity is
defined only relative to a chosen excursion threshold, and the line's claims must say so.
**Mixed** otherwise.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs (fields at every logged step) |
| basin definition | steepest ascent to a local maximum on `v`, 8-neighbourhood with wrap; basin = all cells reaching the same maximum |
| readout | ρ₁(ancestor, descendant) for basin area vs threshold area, on the same pairs |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x101_watershed.json` |

## Checklist before the series

- [x] connected (80 % basin coverage, 100 pairs)
- [x] positive control fires (numeric: reproduction within 0.02 and a partition check)
- [x] readout exists and varies (X100 gives 0.53/0.38 for the threshold measure)
- [x] sensitivity computed (§4: paired difference 0.10 at ~2σ)
- [x] refusal rule written, with "heredity needs the cut" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 19:40 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
