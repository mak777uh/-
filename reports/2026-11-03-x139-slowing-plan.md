# X139 — the slowing curve: does the merge time saturate well inside the mixing length, or keep rising?

**Why.** X136 and X140 found a second signature of the mixing length beyond the mere fact of merging: the median time to absorption **rises towards the crossing** — 19, 39, 49, 79 steps at 12, 14, 15, 16
cells (radius 3), and 9 → 59 at radius 4.5. Two questions remain, and both are cheap:

1. does it **saturate** well inside the length (a floor of a few steps because the structures touch), or does it keep rising as the gap shrinks?
2. is the rise **monotone** at one-cell spacing, or does it step?

The existing points are sparse below 12: nothing at 7, 8, 10 or 11 — the region where the gap is 1–5 cells and the two discs are almost touching.

## 1. Manipulation is connected

Same probe (`--init-spots R:SEP`, seed-dependent placement, anchored), same inflow `F = 0.030`, same radius 3, same seeds 601–605, same 6 000 steps, dense logging.

| separation | gap (`SEP − 6`) | runs | source |
|---|---|---|---|
| **7, 8, 10, 11** | **1, 2, 4, 5** | **20 new** | this run |
| 12 | 6 | 5 | reused from X136 |
| 14, 15 | 8, 9 | 10 | reused from X136 |
| 16 | 10 | 5 | reused from X136 (the crossing, a coin) |

Forty runs in the analysis, twenty of them new. The readout is the same: the median and per-seed steps from seeding to the moment one seeded subtree ends into the other's reach.

## 2. Positive control fires (numeric)

Four controls. **The control fires if** all four hold:

1. **The reused arms reproduce their source**: 12 → median 19, 14 → 39, 15 → 49, 16 → 79 and the same per-seed values. A change means the analysis moved, not the world.
2. **Every new arm starts as two components** of area ≥ 20 cells at the first logged step. A radius-3 pair at separation 7 has a one-cell gap; if it starts as one component the arm is degenerate and is dropped, not smoothed.
3. **Every run is alive** under the structural rule.
4. **The curve is monotone within the seeds' resolution**: a median at a larger gap must not be lower than at a smaller gap by more than two seeds' worth of spread; a genuine inversion is printed, not fitted away.

## 3. Readout exists and varies

Per separation: the median and the five per-seed times. The existing points already span 19 → 79 steps across 12 → 16 cells, so variation at the top of the range is established; the new points fill 7 → 11.

## 4. Sensitivity arithmetic

Five seeds per point; times are quantised at the 10-step logging interval, so a median is resolved to one quantum. The declared resolution is **10 steps** at each point and **one cell** on the gap. A saturation floor is declared if the three smallest gaps (1, 2, 4) give medians within one quantum of each other.

## 5. Refusal rule (fixed before the run)

**Void** if a reused arm misses its source, or a new arm does not start as two components (the one-cell gap arm is the likely candidate), or more than one run is dead.

**Saturation** is published if the medians at gaps 1, 2 and 4 agree within 10 steps — the merge then has a floor set by contact, and the rising part of the curve belongs to the range 5–10 cells.
**A continuous rise** is published if the medians keep increasing with the gap across the whole new range; the report then quotes the curve as a table and says the time is a function of the gap rather than a floor plus a rise.
**An inversion** (a smaller gap taking longer) is reported as is.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots R:SEP` (unchanged, anchored) |
| runs | 20 new at `F = 0.030` (separations 7, 8, 10, 11 × seeds 601–605), plus 20 reused from X136 |
| readouts | median and per-seed steps to absorption at nine separations |
| controls | the reused arms reproduce X136; two components; liveness; monotonicity printed |
| artifact | `E09_pond/l1_field_x139_slowing.json` |

## Checklist

- [x] connected (the manipulation is the gap, in cells; twenty new points below the old range)
- [x] positive control numeric (four reused arms must reproduce X136's medians exactly)
- [x] readout exists and varies (19 → 79 steps across 12 → 16 cells already)
- [x] sensitivity computed (§4: 10-step resolution, one-cell spacing, a declared floor test)
- [x] refusal rule written, with saturation, continuous rise and inversion as separate outcomes

## Status

Registered 2026-11-03 13:56 MSK, before the sweep. Light CPU run, no training.
