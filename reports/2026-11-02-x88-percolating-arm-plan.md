# X88 — the high-inflow arm at twenty worlds: is the memory shorter or longer where the pattern percolates?

**Why.** X87 measured the memory with twenty worlds per inflow and per-world half-lives for the first time, and the U of §10fa did
not appear: **1.82 / 1.16 / 1.07** at `F` = 0.025 / 0.030 / 0.035 — a monotone decline, where the five-world pooled numbers had given
1.47 / 0.73 / 1.61. The only arm where a U could still live is the one never measured at this power: `F ≥ 0.040`, where the morphology
changes character (component count collapses to 1–4 and β₁ rises to 11–87, i.e. the pattern percolates and the lattice becomes a
maze). Either memory turns back up there, which restores a two-armed shape, or it keeps falling and the description of this medium
becomes simple: memory shortens monotonically as inflow rises.

This is the last cheap question in the memory line, and it decides how the whole curve is written.

## 1. Manipulation is connected

Three inflows (`F = 0.040`, `0.045`, `0.050`), twenty jittered worlds each (seeds 241–260), flags identical to X87 (split on,
`--sample-every 50`, single scale 12.0, `--hetero-amp 0.5`, 6000 steps, field at 6000). Parity with X87's flags is checked and
reported.

Connectedness here is a **regime check**, not a component count: this arm is *supposed* to have few components. **The check fires if**
the median component count per cell is below 15 and β₁ > 0 in at least 15 of the 20 worlds, i.e. the worlds are the percolating ones
and not accidentally lattice-like.

## 2. Positive control fires (numeric)

The `F = 0.040` cell must reproduce what X74 measured there with the same convention. **The control fires if** its pooled `rho1` lies
in **[0.42, 0.55]** (X74: 0.486 with five worlds) and its per-world median half-life lies in **[1.2, 2.3]** divisions (X74's pooled
value was 1.61 and X87 showed pooled and per-world medians differ by up to 0.2 at five worlds, so the band is wide deliberately).

## 3. Readout exists and varies

Per world: `rho1..3` from `uid_pairs`, per-world `lambda` and half-life, components and β₁, `s` and `q'` from the saved field. The
primary readout is the **per-world median half-life** per cell with its range and its fittable count; `rho1` is reported beside it as
the level, per §10ff.

## 4. Sensitivity arithmetic

Per-world half-lives within a cell span ~0.4–2.5 in X87 (sd ≈ 0.6). With twenty worlds the standard error of a cell median is ≈0.13, so
a difference of **0.4 divisions** between cells is 3σ and is the declared resolution. That is enough to separate 1.07 (X87's 0.035)
from 1.61 (X74's pooled 0.040) if the rise is real, and to detect a return to ≥1.5. Cost: 60 runs at ~90 s ≈ **90 minutes**.

## 5. Refusal rule (registered before the run)

**Void** if a cell has <400 lag-1 pairs, a dead field (std < 0.01), or if the §2 control misses its band.

**Rise (the U survives)** if the per-world median half-life at 0.045 or 0.050 exceeds the 1.07 measured at 0.035 by at least **0.40**.
**Decline (no U)** if the medians are non-increasing across 0.035 → 0.040 → 0.045 → 0.050, allowing each step to be flat within 0.40.
**Inconclusive** otherwise, printed in full.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.040`, `0.045`, `0.050` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5`, `const_ones` signal |
| worlds | 20 per cell, seeds 241–260, `--init-jitter` |
| identity | `--split-new-uid` on (heredity convention, as X87) |
| logging | `--sample-every 50` (as X85/X87) |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| field | saved at 6000, `_x88_fields/` |
| artifact | `morphogenesis/experiments/L1_field/x88_f{040,045,050}_s241-260.json`, aggregate `l1_field_x88_percolating_arm.json` |

## Checklist before the series

- [x] connected (regime check: few components, β₁ > 0 — the opposite of the lattice cells)
- [x] positive control fires (numeric bands, §2)
- [x] readout exists and varies (198 of 203 worlds fittable across X74/X87)
- [x] sensitivity computed (§4: SE 0.13, resolution 0.40)
- [x] refusal rule written, with "flat within 0.40" as an allowed outcome
- [x] both conventions named (identity, logging)

## Status

Registered 2026-11-02 08:00 MSK, before the series. Sixty runs, ~90 minutes.

доска: принято 0, отклонено 0, отложено 0.
