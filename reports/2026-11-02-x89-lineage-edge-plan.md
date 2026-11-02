# X89 — where exactly do the lineages vanish? Four half-steps between 0.045 and 0.050

**Why.** X88 found the sharpest edge in the whole line without looking for it: at `F = 0.045` the worlds still hold **636**
ancestor-descendant pairs, at `F = 0.050` they hold **six**, and every one of those twenty worlds is a **single component** — nothing
divides, so there are no lineages at all. Between those two inflows the medium stops being a population and becomes one maze.

That is a boundary of the phenomenon, not a measurement problem, and it is worth locating because the whole heredity line is
meaningless on the far side of it. Four half-steps settle it.

## 1. Manipulation is connected

Four inflows (`F = 0.046`, `0.047`, `0.048`, `0.049`), eight jittered worlds each (seeds 261–268), flags identical to X88 (split on,
`--sample-every 50`, single scale, `--hetero-amp 0.5`, 6000 steps, field at 6000). The step from 0.045 (X88, 636 pairs) to 0.050
(X88, 6 pairs) is the gap to be resolved; both endpoints are already measured at twenty worlds.

Connectedness is the regime check: the fraction of worlds with a single component must rise monotonically from 0.045 to 0.050, and
β₁ must stay positive in every world (a maze has holes; a dead world does not).

## 2. Positive control fires (numeric)

The instrument must see the endpoints it is interpolating. **The control fires if** the lineage count per world falls monotonically
across the four new cells **and** the `F = 0.046` cell's median pairs per world is at least **10** (X88's 0.045 gives 636 pairs over
twenty worlds ≈ 32 per world; a first half-step that is already at 0 has missed the edge entirely and the series is void).

## 3. Readout exists and varies

Per world: ancestor-descendant pairs at lag 1, the number of components, β₁ from the field, and a half-life where it can be fitted. The
primary readout is **pairs per world**, because that is the quantity that goes to zero; components and β₁ describe the regime.

## 4. Sensitivity arithmetic

At 0.045 the worlds carry ~32 lag-1 pairs each (sd of the same order); at 0.050, 0. With eight worlds per cell the median is resolved
to a few pairs, so a **fivefold** drop between adjacent cells is unambiguous and is the declared resolution. Cost: 32 runs at ~120 s ≈
**65 minutes**.

## 5. Refusal rule (registered before the run)

**Void** if a cell's fields are dead (std < 0.01) or if the `F = 0.046` cell's median pairs per world is below 10 (§2).

**Sharp boundary** if a single half-step drops the median pairs per world by at least **10×**; the boundary is then quoted as lying
between those two inflows.
**Graded disappearance** if the fall is monotone but no single step reaches 10×.
**Inconclusive** otherwise, printed in full.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.046`, `0.047`, `0.048`, `0.049` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5`, `const_ones` signal |
| worlds | 8 per cell, seeds 261–268, `--init-jitter` |
| identity | `--split-new-uid` on (heredity convention) |
| logging | `--sample-every 50` |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| field | saved at 6000, `_x89_fields/` |
| artifact | `morphogenesis/experiments/L1_field/x89_f0{46,47,48,49}_s261-268.json`, aggregate `l1_field_x89_lineage_edge.json` |

## Checklist before the series

- [x] connected (regime check: single-component fraction rises, β₁ stays positive)
- [x] positive control fires (numeric, §2)
- [x] readout exists and varies (32 pairs per world at 0.045 against 0 at 0.050)
- [x] sensitivity computed (§4: fivefold resolution, 10× for "sharp")
- [x] refusal rule written, with "graded disappearance" as an allowed outcome
- [x] both conventions named (identity, logging)

## Status

Registered 2026-11-02 09:55 MSK, before the series. Thirty-two runs, ~65 minutes.

доска: принято 0, отклонено 0, отложено 0.
