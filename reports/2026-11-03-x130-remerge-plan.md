# X130 — do siblings merge back, and how long does it take?

**Why.** X128b found that in the lattice **54.6 %** of absorptions take a dying structure's cells into a **sibling**, and X129 found that this is not a distance effect
(at identical contact geometry a body's neighbour is a stranger 62 % of the time). The remaining question about the lattice's "family world" is dynamic: **a split
produces two daughters that stand next to each other — do they merge back, and after how long?** If they usually do, and quickly, then the lattice's kinship
absorption is a **re-merging of sisters**, not a slow demographic process, and the number to quote is a time.

This is measurable from the genealogy and the centroids alone: for every division, the distance between the daughters at birth, and the first step at which one
daughter's own uid ends by absorption into the other's subtree.

## 1. Manipulation is connected

No new worlds: the thirty dense logs of X108 and X126. Every division with at least two daughters that both have a peak is a start event; the clock runs until one
daughter's uid disappears into the other's subtree or the run ends.

| quantity | definition |
|---|---|
| **birth separation** `d0` | centroid distance between the two daughters at their first logged step |
| **re-merge event** | the first step at which daughter A's uid ends (no daughters of its own) while daughter B's uid is present and within reach of A's last centroid (`r_A + r_B + 2` cells) |
| **time to re-merge** | steps from the daughters' birth to that event, or censored at the run's end |
| **re-merge share** | the fraction of sister pairs with a re-merge inside the run, reported with the censoring share |

The reach rule is the same `+2` cells as X127b/X128b, so the census is comparable to those runs.

## 2. Positive control fires (numeric)

Four controls. **The control fires if** all four hold:

1. **The sibling-absorption count reproduces X128b**: 248 pairs in the lattice (smaller absorbed) and 187 in the maze, with the same partner rule.
2. **End-survival reproduces X126** (+0.2496 / +0.2984 / +0.1372) and the pair counts are 1 142 / 1 106 / 1 195.
3. **Heredity** `ρ₁ ≥ 0.35`.
4. **The clock is populated**: at least 300 sister pairs with a usable birth separation in every cell. Below that the median time describes a minority and the run is
   void.

## 3. Readout exists and varies

Per cell: the number of sister pairs, the median birth separation `d0`, the re-merge share with a bootstrap interval, the median time to re-merge, the censoring
share, and the relation between `d0` and the merge probability (median `d0` among merged against not). Variation is expected: daughters born 3 cells apart and
daughters born inside a body that grows between them are different populations.

## 4. Sensitivity arithmetic

Sister pairs 1 142 / 1 106 / 1 195 (X126), of which the ones with two measurable daughters are ~80 % (X97's census). Over ~900 pairs a share has SE 0.017, so the
declared resolution is **0.05** on the re-merge share. Times are quantised at the 10-step logging interval; a median over hundreds of events is resolved to one
quantum, and the declared resolution on the median time is **100 steps**.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 usable sister pairs, or the sibling-absorption count misses X128b's by more than 5 %, or heredity or end-survival misses its
source.

**Sisters merge back** if the re-merge share exceeds **0.50** in the lattice: then the family world is a re-merging world and the median time is the number to quote.
**Sisters separate** if it is below 0.25. **Partial** otherwise, with the share and the time printed — and in every case the censoring share is printed next to the
merge share, because a run that ends before the clock does cannot distinguish "never merged" from "not yet".

## Design summary

| factor | value |
|---|---|
| artifacts | the thirty dense logs of X108 and X126 |
| readouts | birth separation, re-merge share with censoring, median time to re-merge |
| controls | sibling-absorption count reproduces X128b; end-survival reproduces X126; heredity; ≥ 300 usable pairs |
| artifact | `E09_pond/l1_field_x130_remberge.json` |

## Checklist

- [x] connected (every division with two measurable daughters starts a clock; censoring reported)
- [x] positive control numeric (two published counts reproduced, one of them a census of the same events)
- [x] readout exists and varies (daughter separation against a growing body)
- [x] sensitivity computed (§4: SE 0.017 on the share, resolution 0.05 and 100 steps)
- [x] refusal rule written, with "partial" and a censoring share as real outcomes

## Status

Registered 2026-11-03 05:35 MSK, before the run. No new worlds, no GPU.
