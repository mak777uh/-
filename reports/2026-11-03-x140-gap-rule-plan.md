# X140 — the third radius: the gap rule predicts a crossing at 18 cells

**Why.** X138 replaced the centre-distance reading with a **gap** reading: at radius 3 (29 cells of area) the crossover sits at 16 cells, i.e. a gap of `16 − 2·3 = 10`; at radius 6 (113 cells) it sits at
20, a gap of `20 − 2·6 = 8`. So the invariant is a surface gap of about **9 ± 1 cells**. That is a rule with a **prediction**, and this run tests it on a radius that was not used to build it.

**R = 4.5** (64 cells of area, halfway between the two measured structures). The rule predicts a crossover at **2·4.5 + 9 = 18 cells**. A crossover at 16 or at 22 falsifies the rule; a
crossover at 18 with the same slowdown would make three radii agree on one number and turn the rule from a summary of two points into a measurement.

## 1. Manipulation is connected

Same probe (`--init-spots R:SEP`, seed-dependent placement, anchored), same inflow `F = 0.030`, same seeds 601–605, same 6 000 steps, dense logging. Only the radius changes: **4.5** instead of 3 or 6.
A radius-4.5 disc is 64 cells of area, so `sqrt(area/π) = 4.5` to the digit.

| arm | separation | seeds |
|---|---|---|
| control | 0 (one disc of radius 4.5) | 601–605 |
| sweep | **16, 18, 20, 22** | 601–605 |

Twenty-five runs. The four points straddle the prediction by one cell on each side and by three beyond it.

## 2. Positive control fires (numeric)

Five controls. **The control fires if** all five hold:

1. **The anchor still matches** (the probe is unchanged since X134b): the X134b anchor against the committed projection of `x108_f030_s301.json`, key by key.
2. **The radius-4.5 seed is one structure**: one component of area ≥ 20 at the first logged step and still one at step 100, in at least 4 of 5 control runs.
3. **Every two-disc arm starts as two components** at the first logged step.
4. **Every run is alive** under the structural rule.
5. **The sweep spans both outcomes** — absorption in ≥ 3 of 5 seeds at some separation and ≤ 2 at another. One outcome means the four points all sit on the same side and the prediction was not
   tested; that is a void, not a missing effect.

## 3. Readout exists and varies

Per separation: absorbed count, both-alive count, median and per-seed steps. The control reports whether one radius-4.5 disc survives as one structure.

## 4. Sensitivity arithmetic

Five seeds per point and a three-of-five rule; four separations at 2-cell spacing. The three candidate crossings (16, 18, 22) are separated by the spacing, so the design discriminates between them.
The declared resolution on the crossing is **± 1 cell**.

## 5. Refusal rule (fixed before the run)

**Void** if the anchor moves, or the control disc is not one structure, or a two-disc arm does not start as two components, or more than one run is dead, or the sweep spans one outcome.

**The gap rule holds** if the crossing is at **18 ± 1 cells**. **It fails** if the crossing is at 16 or below (the gap would be ≤ 7, outside the 9 ± 1 band) or at 22 and above (a gap ≥ 13). In the
failing case the three radii are reported as three independent numbers and the rule is withdrawn — the report says so rather than fitting a curve through three points.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots R:SEP` (unchanged, anchored) |
| runs | 25 at `F = 0.030`: the `SEP = 0` control plus separations 16, 18, 20, 22, all at **R = 4.5**, five seeds each |
| readouts | absorbed count, both alive, steps to absorption; control: one disc survives as one structure |
| controls | anchor; the radius-4.5 seed is one structure; two components; liveness; both outcomes present |
| artifact | `E09_pond/l1_field_x140_gap_rule.json` |

## Checklist

- [x] connected (the lever is the seeding radius at a value not used to build the rule)
- [x] positive control numeric (the seed must be one structure at step 1 *and* step 100)
- [x] readout exists and varies (R = 3 crosses at 16, R = 6 at 20; R = 4.5 must land at 18)
- [x] sensitivity computed (§4: 2-cell spacing against three candidate crossings, ±1 cell)
- [x] refusal rule written, with withdrawal of the rule as a real outcome

## Status

Registered 2026-11-03 12:52 MSK, before the sweep. Light CPU run, no training.
