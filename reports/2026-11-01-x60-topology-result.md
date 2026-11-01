# X60 result: heterogeneity does not add spots, it removes the wavelength

1 November 2026, 04:45. Twenty runs, 0 failed, 24 minutes of GPU. This is the first time the line has kept the field
instead of only its component count, and the field says something the count could not.

## What was run

`scripts/x60_series.py` — two arms, paired by seed, exactly the `x18` design, plus `--save-fields`: `v` saved at
t = 2000, 4000, 6000 as `float32`, 37 KB each, six files per seed pair. Preregistration and its five checks:
[`2026-11-01-x60-fields-and-masks-plan.md`](2026-11-01-x60-fields-and-masks-plan.md).

| | |
|---|---|
| runs | 20 (10 seeds × 2 arms), 0 failed |
| wall time | 57–85 s per run, 24 min total |
| anchor | passed before the series: the flag is inert, `series` bit-for-bit identical with and without it |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_betti.json` (60 rows, three blocks) |

**One transient failure, recorded rather than hidden:** the first attempt stalled on one homogeneous run (CUDA, no output
for 10 minutes, one array written). The series now has a per-run 900 s timeout and one retry; the rerun finished all
twenty. The stall never reproduced, which is why it is written down as an unresolved intermittent rather than as a fix.

**The saved fields reproduce the runner's own observable exactly.** After applying the runner's `min_cells = 5` filter,
β₀ computed from the arrays equals `components` in the JSON in **60 of 60** rows. That is the licence to trust the
topological quantities below.

## What the topology says

β₀ and β₁ are computed with 4-connectivity and periodic wrap; χ by the bit-quad formula, β₁ = β₀ − χ.

| t | β₀ het / hom | β₁ het / hom | Δβ₀ (seeds) | Δβ₁ (seeds) |
|---|---|---|---|---|
| 2000 | 11.5 / 6.5 | **10.0 / 1.0** | +6.5 (6/10) | **+9.0 (10/10)** |
| 4000 | 3.0 / 2.5 | 17.5 / 11.5 | −0.5 (3/10) | +8.5 (7/10) |
| 6000 | 2.5 / 2.0 | 21.5 / 11.0 | +1.0 (5/10) | +4.5 (6/10) |

**At mid-run the heterogeneous field is not a scatter of spots — it is a perforated web.** It has more components and
*ten times* as many holes, in 10 of 10 seeds. The homogeneous field at the same moment has 6.5 blobs and one hole.

**The temptation to explain it by "more material" is removed.** Occupancy differs between arms, so a secondary control
(recomputed after the data, and labelled as such) lowers the heterogeneous threshold until its occupied area equals the
homogeneous run's, then recomputes both: **Δβ₁ = +5.5 at t=2000, 10/10 seeds** (+8.5 at 4000, 9/10; +6.0 at 6000, 8/10).
The excess of holes is not an excess of area.

**The count contrast does not appear at any single snapshot.** Δβ₀ is 6/10, 3/10, 5/10 — below the pre-declared 8/10 bar
at all three times. The published +3.57 is a property of the *time average over an early transient*, not of any
instantaneous field. That is the strongest confirmation so far of the v1.6 correction, and it comes from independent data.

## How far the web claim survives, measured rather than assumed

Two controls decide whether "more holes" is a property of the field or of the ruler. Both were run on the same arrays.

**Threshold.** The pre-registered threshold 0.2 is one slice. At four thresholds:

| threshold | t = 2000 | t = 4000 | t = 6000 |
|---|---|---|---|
| 0.15 | +14.5 (10/10) | +11.5 (8/10) | 0.0 (5/10) |
| 0.20 | +9.0 (10/10) | +8.5 (7/10) | +4.5 (6/10) |
| 0.25 | +7.5 (10/10) | +6.5 (6/10) | 0.0 (5/10) |
| 0.30 | +5.0 (8/10) | +3.0 (8/10) | +2.5 (7/10) |

The excess is **a transient phenomenon and nothing more**: it is robust at t = 2000 (8–10 of 10 seeds at every threshold)
and gone by t = 6000 at a fixed threshold, where the two arms overlap seed by seed even though their medians differ
(21.5 against 11.0). Reporting the late-time medians as a difference would be exactly the error this line keeps finding.

**One honest asymmetry.** At t = 2000 the homogeneous world has not yet reached its pattern (its own spectrum still peaks
at q = 1), so that comparison is *web against pre-pattern*, not *web against pattern*. The claim that survives is
therefore about **what heterogeneity does during the transient**, not about a permanent difference in hole count.

## What the spectrum says, and what it refuses to say

Seed-averaged radial power spectrum of `v`, q a mode index, λ = 96/q cells:

| t | heterogeneous | homogeneous |
|---|---|---|
| 2000 | q = 1, λ = 96 cells | q = 1, λ = 96 cells |
| 4000 | q = 1, λ = 96 cells | **q = 8, λ = 12 cells** |
| 6000 | q = 1, λ = 96 cells | **q = 8, λ = 12 cells** |

The homogeneous world settles into a **12-cell pattern wavelength** — the value the parameters imply. The heterogeneous
world never does: its variance stays at the largest available scale, one structure wrapping the domain.

**The wavelength normalisation of the preregistration is therefore refused, not performed.** `N·λ²/A` is only meaningful
when λ is a pattern scale; for the heterogeneous arm λ is the box, and the expression degenerates to `N`. This is refusal
rule item 4 doing its job, and it is more informative than the number would have been.

## What changes in the claim

Old: *"heterogeneous inflow roughly doubles the number of components."* True as a time average, and now visibly an
average over a transient.

New, and deliberately in two parts because the evidence supports two different strengths:

1. **Robust, across all three snapshots and both controls.** *Heterogeneous inflow costs the medium its pattern
   wavelength.* The homogeneous world converges to a periodic pattern of about twelve cells; the heterogeneous world
   never leaves the scale of the domain, at any snapshot, in the seed-averaged spectrum.
2. **Transient only.** *While that happens, the heterogeneous field passes through a perforated web* — ten times the
   holes of the homogeneous field at the same moment, 10/10 seeds, robust to threshold and to matched occupancy. By
   t = 6000 the two arms overlap seed by seed, and no permanent difference in hole count is claimed.

The count doubles early because a web has more struts than a set of spots, not because there are more objects — and the
honest sentence is that heterogeneity changes **the scale at which the field organises**, not the number of things in it.

## What is still open, and what is next

| question | status | next |
|---|---|---|
| Is the domain-scale mode a finite-size effect of the 96 grid? | open, and now the most important open question | `X58`: grid 192 with `Du, Dv → D/Δx²`, same three snapshots |
| Does the web support selection, or only copying? | open | `X61`: `eps = 0` control, `S1` drift + `I_null` |
| Are the holes stable objects or artefacts of the threshold? | partially: matched-occupancy control holds at 2000 | threshold sweep on saved fields, same arrays |
| Why did one run stall? | unresolved, intermittent | watch for recurrence; the timeout now bounds the cost |

## Status of the preregistration

Five checks passed before the run; the anchor passed; the run happened; **one of the four planned readouts (λ
normalisation) is refused by its own rule and the other three are reported**. That is the preregistration working, not
failing.
