# X135 — the mixing length in the percolating cell, and the single-disc control

**Why.** X134 placed two discs at a chosen separation in the lattice (`F = 0.030`) and found a **wall** between 12 and 18 cells: 10 of 10 seeds merge inside one pattern
wavelength (12 cells), 20 of 20 keep both lineages beyond it. The block's reading is that the habitat's effect on a lineage reduces to **a length**. That reading
makes a prediction which is cheap to test and easy to fail: the percolating cell has a longer wavelength (`q' = 7`, ≈13.7 cells) and a body that percolates, so its
mixing length should be **larger** — and if the body mixes everything regardless of distance, the sweep will show merging at **every** separation, which is a
different and equally important answer.

The single-disc arm is the control that separates "two lineages merged" from "the world filled and everything became one body": with `SEP = 0` both offsets coincide,
so the same flag seeds **one** disc, and the arm says whether a single seeded structure survives at this inflow at all.

## 1. Manipulation is connected

The probe is unchanged from X134 (`--init-spots R:SEP`, additive, anchored bit-for-bit when absent — the anchor comparison is re-used and re-checked, not re-run, since
the probe has not changed since). Only the inflow changes: `F = 0.040`, the cell whose body percolates (largest component 935 cells at the last step, X126).

| arm | separation | seeds |
|---|---|---|
| control | **0** (one disc) | 601–605 |
| mixing | 8, 12, 18, 24, 30, 36 | 601–605 each |

Thirty-five runs, radius 3 cells (29 cells of area), 6 000 steps, dense logging every 10 steps, `--split-new-uid`, no field saving. The readout is X134's,
unchanged: with `--split-new-uid` each seeded disc is a uid and a lineage is a subtree, so the question is whether one seeded subtree disappears into the other, when,
and whether both are present at the last step. The `SEP = 0` arm has only one seeded uid, so its readout is survival and size, not absorption.

## 2. Positive control fires (numeric)

Five controls. **The control fires if** all five hold:

1. **The anchor still matches**: the anchor run X134 produced (its own scratch copy) against the committed projection `morphogenesis/experiments/L1_field/x108_f030_s301.compact.json`, key by key, `uid_pairs` identical.
2. **The two-disc arms start as two components** of area ≥ 20 cells at the first logged step (and the `SEP = 0` arm as one).
3. **Every run is alive** under the structural rule (occupancy ≥ 0.05, largest ≥ 50 cells).
4. **The single-disc control survives**: in at least 4 of 5 control seeds the seeded uid (or its subtree) is present at the last logged step. If a lone disc does not
   survive at this inflow, the two-disc arms cannot be read as merging rather than dying and the run is void.
5. **The sweep spans both outcomes or spans none**: absorption in ≥ 3 of 5 seeds at some separation **and** ≤ 2 of 5 at another gives a threshold; absorption in
   ≥ 3 of 5 at **every** separation is the "the body mixes everything" outcome, which is reported as such rather than as a void.

## 3. Readout exists and varies

Per separation: the five seeds' absorption outcomes, the median time to absorption, and both-lineages-alive counts. The control arm reports the single disc's subtree
size and survival. Variation is the question: in the lattice it ran 5/5 → 0/5 across six cells of separation; here it may run 5/5 at every separation.

## 4. Sensitivity arithmetic

Five seeds per separation, resolution two seeds in five, and the same 6-cell spacing as X134 so the two sweeps are directly comparable. The lattice's threshold is
bracketed at 12–18 cells; if the maze's is bracketed at 24–30 or higher, the two lengths differ by more than the spacing and the difference is real at this
resolution. If the maze merges at every separation up to 36, the declared reading is **"mixing length at least three wavelengths"**, not "no mixing length".

## 5. Refusal rule (fixed before the run)

**Void** if the anchor no longer matches, or any two-disc arm does not start as two components, or more than two runs are dead, or the single-disc control fails.

**A threshold** is published as the interval between the largest merging separation and the smallest separating one, with seed counts on both sides.
**"The body mixes everything"** is published if absorption occurs in ≥ 3 of 5 seeds at every separation including 36, with the control arm showing that a single disc
does survive — that would say the percolating cell has no segregation length at this scale, which is the direct counterpart of the lattice's 12–18 cells.
**Non-monotone** is reported as is.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots R:SEP` (unchanged from X134, anchored) |
| runs | 35 at `F = 0.040`: the `SEP = 0` control plus six separations, five seeds each |
| readouts | absorption by the other lineage, both alive at the end, time to absorption; control: single-disc survival and subtree size |
| controls | anchor; two components at the first step; liveness; single-disc survival; the sweep spanning an outcome |
| artifact | `E09_pond/l1_field_x135_maze_mixing.json` |

## Checklist

- [x] connected (the manipulation is the initial separation, in cells, at a different inflow)
- [x] positive control numeric (anchor re-checked; two components; single-disc survival as the control that separates merging from dying)
- [x] readout exists and varies (the lattice ran 5/5 → 0/5; the maze may not)
- [x] sensitivity computed (§4: same 6-cell spacing as X134 so the lengths are comparable)
- [x] refusal rule written, with "the body mixes everything" as a named outcome

## Status

Registered 2026-11-03 08:55 MSK, before the sweep. Light CPU run, no training.
