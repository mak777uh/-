# X90 — does the trickle stop, or does it only slow down? Twelve thousand steps at the fading edge

**Why.** X89 showed the lineage count decaying geometrically with inflow: 31.8 → 13.0 → 6.0 → 2.0 → 1.0 → 0.3 pairs per world from
`F = 0.045` to `0.050`, a factor 2.4 per half-step. At 0.050 a world produces one division event per three or four worlds over 6000
steps, which is at our resolution limit. The question that decides how to write it: is that *slow*, or is it *stopped and merely
sampled by chance*?

One measurement separates them. If divisions continue at a low rate, doubling the horizon doubles the count. If reproduction has
actually ceased, the count stays where it is.

## 1. Manipulation is connected

Three inflows (`F = 0.048`, `0.049`, `0.050`), eight jittered worlds each (seeds 271–278), **12 000 steps** instead of 6000, flags
otherwise identical to X89 (split on, `--sample-every 50`, single scale, `--hetero-amp 0.5`). Connectedness: the fields must still be
alive (std ≥ 0.01) and single-component with β₁ > 0, i.e. the same regime at twice the horizon.

## 2. Positive control fires (numeric)

The 6000-step counts are known from X88 and X89 and must be reproduced by a 6000-step *prefix* — but the artifacts are written at the
end, so instead the control is a regression check: the 12 000-step count at 0.050 must be **at least** the 6000-step value (0.3 per
world) in median, since a longer horizon cannot produce fewer events in the same world. **The control fires if** the median pairs per
world at 0.050 is ≥ 1 (i.e. at least one event in most worlds) — meaning the horizon was long enough for the rare events to register at
all, so the comparison is meaningful.

## 3. Readout exists and varies

Pairs per world at lag 1 (primary), plus components and β₁, and the full depth readout where fit. The comparison is
`pairs(12 000) / pairs(6 000)` per cell, using X88/X89's 6000-step medians (2.0, 1.0, 0.3).

## 4. Sensitivity arithmetic

Counts are small integers per world (0–3), so a cell's median is resolved to one event. With eight worlds, a doubling of a 1-event median
to 2 is already at the edge of resolution; the rule therefore uses the **ratio of the cell sums** (24 worlds per cell combined over two
horizons is not available, but 8 worlds × 3 cells = 24 for the ratio), and the declared resolution is a factor **1.5** on the cell
median. Cost: 24 runs at 12 000 steps, ~150 s each ≈ **60 minutes**.

## 5. Refusal rule (registered before the run)

**Void** if a cell's fields are dead (std < 0.01) or if the §2 control misses (0.050 median below 1 event).

**The trickle continues** if the median pairs per world at 12 000 steps is at least **1.5×** the 6000-step value in at least two of the
three cells — reproduction is rare but real, and the count scales with time.
**Reproduction has stopped** if the ratio is at most **1.2×** in all three cells — the remaining events are transient and the medium
has ceased to divide.
**Inconclusive** otherwise, printed in full.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.048`, `0.049`, `0.050` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5`, `const_ones` signal |
| worlds | 8 per cell, seeds 271–278, `--init-jitter` |
| identity | `--split-new-uid` on |
| logging | `--sample-every 50`, horizon **12 000** |
| grid | 96, `dt = 1.0` |
| field | saved at 12 000, `_x90_fields/` |
| artifact | `morphogenesis/experiments/L1_field/x90_f0{48,49,50}_s271-278.json`, aggregate `l1_field_x90_trickle.json` |

## Checklist before the series

- [x] connected (same regime at twice the horizon: alive, single component, β₁ > 0)
- [x] positive control fires (numeric: 0.050 median ≥ 1 event, else the horizon is too short to compare)
- [x] readout exists and varies (0.3 / 1.0 / 2.0 events per world at 6000)
- [x] sensitivity computed (§4: ratio of medians, resolution 1.5×)
- [x] refusal rule written, with "stopped" as a real outcome rather than a failure
- [x] both conventions named (identity, logging)

## Status

Registered 2026-11-02 10:50 MSK, before the series. Twenty-four runs, ~60 minutes.

доска: принято 0, отклонено 0, отложено 0.
