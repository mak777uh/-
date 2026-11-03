# X142 — the annihilation band: is the five-cell gap a hole of one cell or a band, and is it set by the gap or by the radius?

**Why.** X139 found that at a five-cell gap (radius 3, separation 11) the two seeded lineages **both end with no
descendants** in 5/5 seeds while the world stays alive — the pair is annihilated rather than merged or kept apart.
The point sits inside an otherwise smooth curve of merge times, and the curve is already measured on both sides of it:

| gap (cells) | 1 | 2 | 4 | **5** | 6 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|
| median steps | 1 | 1 | 10 | **annihilated** | 19 | 40 | 50 | 79 |
| source | X139 | X139 | X139 | X139 | X136 (SEP 12) | X136 | X136 | X136 |

Two cells are missing and they are the ones that decide what the thing is: **gap 3** (separation 9) and **gap 7**
(separation 13). If both merge the annihilation is a **one-cell hole in a smooth curve** and the description is the
curve plus one exception. If either annihilates it is a **band**, and its edges are the new content.

And there is a second question the same sweep can answer, because the gap rule (§10hd) says the mixing length is set
by the **absolute** gap between surfaces, not by the structure's size: does the annihilation also sit at an absolute
gap? At radius 4.5 (crossing at gap 9) the arms at gaps 4, 5 and 6 are new, and gap 7 (separation 16) is already
measured as **5/5 merged** by X140 — so the same window is bracketed at the second radius.

## 1. Manipulation is connected

Same probe (`--init-spots R:SEP`, seed-dependent placement, anchored by X139 and unmodified since — `git diff
scripts/field_track.py` is empty), same inflow `F = 0.030`, same seeds 601–605, same 6 000 steps, same dense logging
every 10 steps. The manipulation is the **gap in cells**, which is what the claim is about.

| radius | gap | separation | runs | source |
|---|---|---|---|---|
| 3 | **3** | **9** | **5 new** | this run |
| 3 | 5 | 11 | 5 | reused from X139 (the annihilation) |
| 3 | **7** | **13** | **5 new** | this run |
| 4.5 | **4, 5, 6** | **13, 14, 15** | **15 new** | this run |
| 3 | 1, 2, 4 | 7, 8, 10 | 15 | reused from X139 |
| 3 | 6, 8, 9, 10 | 12, 14, 15, 16 | 20 | reused from X136 |
| 4.5 | 7 | 16 | 5 | reused from X140 |

Twenty-five new runs, seventy in the analysis, and every point of the radius-3 curve from gap 1 to gap 10 is
present at one-cell spacing.

## 2. Positive control fires (numeric)

Five controls. **The control fires if** all five hold:

1. **The reused arms reproduce their source**: radius 3 gap 6 → 5/5 absorbed, median 19; gap 4 → median 10; gap 10 →
   2/5 absorbed; radius 4.5 gap 7 → 5/5 absorbed. Same per-seed values. A change means the analysis moved.
2. **Probe stability, one fresh run**: one repeat of X139's gap-5 arm (radius 3, separation 11, seed 601) into a
   separate file must produce an **identical** `series` and `uid_pairs` to `x139_sep11_s601.json` on disk. The probe
   path is therefore demonstrably unchanged, not merely assumed.
3. **Every new arm starts as two components** of area ≥ 20 cells at the first logged step. A degenerate arm is dropped
   and named, never smoothed.
4. **Every run is alive** under the structural rule — including the annihilation arms, whose world must be alive while
   both seeded lineages are not. A dead world would make "both lost" uninformative.
5. **The annihilation arm is read as annihilation, not as separation**: radius 3 gap 5 must still print
   `absorbed 0/5, both alive 0/5, unresolved 5/5`. This is the specific readout defect X139 found, and it is checked
   every time the class is used.

## 3. Readout exists and varies

The outcome classes are counts out of five at each gap and they already span the full range across one cell
(5/5 absorbed at gap 4, 0/5 absorbed with 5/5 `unresolved` at gap 5, 5/5 absorbed at gap 6), so variation at the
resolution used is established before the run. Secondary readouts, also already varying: the median steps to
absorption (1 → 79), the number of components at the last step, and the subtree sizes of the two seeded uids.

## 4. Sensitivity arithmetic

The primary readout is **discrete**: counts of five per arm. The switch actually observed between gap 4 and gap 5 was
5/5 → 0/5, i.e. a separation of five seeds, so five seeds per arm resolve it; the resolution is **one cell** on the
gap and **one seed** on the count. The declared minimal effect is the difference between "≥ 4/5 absorbed" and "≤ 1/5
absorbed"; an arm with 2–3/5 is by construction **indeterminate** and is reported as indeterminate rather than used
as an edge. No power calculation is needed for the primary readout because no continuous difference between arms is
claimed; the merge-time medians are quoted as secondary numbers with the 10-step logging quantum as their resolution.

## 5. Refusal rule (fixed before the run)

**Void** if a reused arm misses its source (control 1), if the probe repeat differs from the committed X139 log
(control 2), if a new arm does not start as two components (control 3), or if more than one run is dead (control 4).

The registered outcomes, fixed before the data:

- **A one-cell hole.** Radius 3 gaps 3 and 7 both give ≥ 4/5 absorbed. The annihilation is confined to gap 5 and the
  result is the curve itself: 1, 1, 10, annihilated, 19, 40, 50, 79 steps. The report then says the five-cell gap is
  an isolated exception in a monotone curve, not a regime.
- **A band.** At least one of gaps 3 and 7 gives ≤ 1/5 absorbed with no surviving descendants. The annihilation covers
  at least two cells, and the report states both edges at one-cell resolution and whether the band has an interior.
- **Absolute gap.** Radius 4.5 gap 5 gives ≤ 1/5 absorbed with both lineages gone. The annihilation is then set by the
  absolute gap, as the mixing length is, and it is a property of the pattern wavelength rather than of the radius-3
  geometry.
- **Radius-set.** Radius 4.5 gaps 4, 5 and 6 all give ≥ 4/5 absorbed. The annihilation does not transfer to a second
  radius at the same gap, so it belongs to the radius-3 initial condition and the gap rule does not extend to the
  inner edge.
- **Neither.** Radius 4.5 has a hole, but not at gap 5. The report gives where the hole is and drops the absolute-gap
  reading for the inner edge.

An arm with 2–3/5 absorbed is reported as indeterminate; if both radius-3 new arms are indeterminate the sweep is
declared **unresolved at this resolution** and the next run doubles the seeds, not the gaps.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots R:SEP` (unchanged, anchored; re-verified by one fresh repeat) |
| runs | 25 new at `F = 0.030` (radius 3 gaps 3 and 7; radius 4.5 gaps 4, 5, 6; seeds 601–605), 45 reused |
| readouts | outcome class per arm (absorbed / both alive / unresolved), median steps, components at end, subtree sizes |
| controls | reuse reproduces; probe repeat identical; two components; liveness; the annihilation class still reads 0/5 + 5/5 |
| artifact | `E09_pond/l1_field_x142_annihilation.json` |

## Checklist

- [x] connected (the manipulation is the gap in cells; two arms bracket the hole at one-cell spacing on each side)
- [x] positive control numeric (four reused arms must reproduce their medians and counts; one fresh repeat must be identical)
- [x] readout exists and varies (5/5 absorbed vs 0/5 absorbed across one cell, already observed)
- [x] sensitivity computed (§4: discrete counts of five, one-cell resolution, an explicitly indeterminate middle)
- [x] refusal rule written, with one-cell hole, band, absolute gap, radius-set and neither as separate outcomes

## Status

Registered 2026-11-03 15:45 MSK, before the sweep. Light field run, no training.

## Amendment, 03.11 16:10 — two arms re-run, and what "alive" is a control for

Written after the probe control and while the first twenty-five arms were running, before any of them was read.

**1. Gaps 6 and 9 are re-run, not reused.** Checking the population before the analysis showed that X136's full
logs for separations 12 and 15 were retired before the compact projections existed — only 14, 16 and 17 were ever
compacted and committed. The gap-6 point is the merging neighbour on the other side of the hole and one of the two
decisive arms, so it cannot rest on a number in an aggregate whose raw artifact is gone. It is re-run here, and so is
gap 9, which the curve needs to be continuous. That makes **35 new runs** (25 registered plus 10), and it turns
control 1 into a stronger test than registered: the re-run arms must reproduce the numbers X136 published (5/5
absorbed, median 19 steps at gap 6; 5/5, median 49 at gap 9).

**2. "Alive" is a control for emptiness, not for fragmentation.** The registered control 4 said every run must be
alive under the structural rule (total area ≥ 5 % of the grid and a largest component ≥ 50 cells). X139's own
aggregate shows that rule failing in 2 of its 40 long runs — one seed of the annihilation arm and one at gap 8 —
where the field ends at a quarter of the grid in sixty-odd small patches. That is fragmentation, not death, and
requiring it of every arm would void the experiment for a reason unrelated to the claim. Control 4 therefore
becomes: **the field never empties** (occupancy ≥ 5 % of the grid at the last step), and **fragmentation is
reported per arm as a count** rather than used as a refusal. The refusal itself is unchanged in force: a world that
empties makes "both lineages lost" uninformative, and that is what still voids the arm.

The correction to X139's controls paragraph, made for the same reason, is appended there.
