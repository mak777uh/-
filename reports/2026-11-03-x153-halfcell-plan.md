# X153 — is the boundary a whole-cell step, or does it creep within a cell?

**Why.** The block now has two facts that are clean and one that is not. The **time** of mutual coalescence is the surface
gap's: 29, 39, 49 logged steps at gaps 6, 7, 8, exact per seed while coalescence is universal (twenty seed-runs across
four radii). The **boundary** — the largest gap at which every seed coalesces — is 8 cells at radius 3 (28 cells of disc
area) and 7 at radius 4.5, 5.25 and 6 (64, 87 and 113). What is not known is whether that boundary is a **whole-cell
step** — the last integer gap at which coalescence is universal, with nothing in between — or a **continuous** line that
the one-cell sweep has been sampling coarsely.

A half-integer separation separates the two readings. Radius 6 holds 5/5 at a gap of 7 cells (separation 19) and 3/5 at 8
(separation 20). At separation **19.5** the surface gap is **7.5** cells, halfway between the last universal gap and the
first broken one.

## 1. Manipulation is connected

Same probe (`--init-spots R:SEP`, float separations already used by X151), same inflow `F = 0.030`, same 6 000 steps,
dense logging every 10 steps, the same tolerance-free readout. Only the separation moves, by half a cell, so the
manipulation is exactly the quantity the boundary is defined on.

| arm | radius | gap | separation | runs |
|---|---|---|---|---|
| `x153_g75_r60` | 6.0 | 7.5 | 19.5 | 10 new (seeds 601–610) |

Ten seeds, not five: with five, a 4/5 result is one seed away from 5/5 and the arm would not be able to tell
"step" from "creep" — the declared minimal effect needs a denominator that can distinguish them.

## 2. Positive control fires (numeric)

Four controls. **The control fires if** all four hold:

1. **The readout is on the same scale as its neighbours**: with radius 6 and separation 19.5 the probe must place two
   discs whose first logged frame has two components of area ≥ 20 cells, and the surface gap computed from the artifact
   (`separation − 2R`) must be **7.5**, not rounded to 7 or 8.
2. **The timing stays inside the bracket the two neighbouring arms set**: in the seeds that coalesce, the median time to
   mutual coalescence must lie in **[39, 49]** logged steps — 39 is gap 7's median, 49 is gap 8's. A median outside that
   bracket means the half-cell separation changed something other than the gap, and the arm is void.
3. **Seeds 601–605 must be directly comparable with the neighbouring arms**, so they are reported separately from 606–610.
4. **No arm ends empty** (occupancy ≥ 5 % of the grid at the last step), and every median is printed with its n.

## 3. Readout exists and varies

The class spans M, A and P across the neighbouring arms of this radius, and the two nearest arms differ (5/5 at gap 7,
3/5 at gap 8), so the readout has room to vary at the half-cell this arm adds.

## 4. Sensitivity arithmetic

Ten seeds at one arm. The declared minimal effect is a **half** of the seeds: the arm is decisive for "step" if it
coalesces in at least **9 of 10** (then the boundary is above 7.5 and the step at 8 stands), and decisive for "creep" if
it coalesces in at most **6 of 10** (then 7.5 is measurably worse than 7 and the boundary is interior to the cell). Seven
or eight of ten is declared **indeterminate** in advance, not after the numbers.

## 5. Refusal rule (fixed before the run)

**Void** if control 1 fails (the arm is not on the same scale), if control 2 fails (the timing leaves [39, 49]), or if
any run ends empty or fails to start as two components.

The registered outcomes:

- **Whole-cell step**: at least 9 of 10 seeds coalesce at a gap of 7.5. Then the boundary is the last integer gap at which
  coalescence is universal, the half-cell changes nothing, and the block's picture is closed at this resolution: a step at
  8 cells for the small disc and at 7 for the larger ones.
- **The boundary creeps within the cell**: at most 6 of 10 coalesce. Then 7.5 is already worse than 7, the boundary is a
  line rather than a step, and the reported "gap of 7" is a sampling of it — the next run is a half-cell ladder at radius
  6 (7.0, 7.5, 8.0 with ten seeds each) to measure the line rather than its endpoints.
- **Indeterminate**: 7 or 8 of 10. Then the half-cell is inside the noise of ten seeds and the next run doubles the seeds
  at 7.5 alone, because adding radii would not help.
- **Contradiction**: at most 3 of 10 coalesce. Then 7.5 is worse than 8, which contradicts the monotonicity the whole
  block rests on; the run is reported as a contradiction and no further radius is measured until it is explained.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots 6.0:19.5` (float separation, as X151) |
| runs | 10 new at `F = 0.030`, seeds 601–610 |
| readouts | class per seed (M / A / P), time to mutual coalescence, surface gap recomputed from the artifact |
| controls | surface gap 7.5 exactly; median time inside [39, 49]; 601–605 reported separately; nothing empty |
| artifact | `E09_pond/l1_field_x153_halfcell.json` |

## Checklist

- [x] connected (the separation moves by half a cell, which is the quantity the boundary is defined on)
- [x] positive control numeric (surface gap 7.5 exactly, median time inside 39–49)
- [x] readout exists and varies (5/5 against 3/5 in the two neighbouring arms)
- [x] sensitivity computed (§4: ≥9/10 = step, ≤6/10 = creep, 7–8/10 = indeterminate, declared in advance)
- [x] refusal rule written, with step / creep / indeterminate / contradiction as separate outcomes

## Status

Registered 2026-11-03 19:58 MSK, before the run. Light field runs, no training.
