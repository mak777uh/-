# X192 — the phase census at the largest size (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X191's five-level sweep passed one of three registered criteria at the margin, and the reason is now known to be structural rather
than statistical: the local inflow at a pair of sites is a function of the **phase** — the position modulo the pattern's 12-cell
period — and the phase map is finite. Enumerating it over the seeds gives **144 phase classes** whose `F_local` takes only **nine
distinct values** (0.0150 to 0.0375), with up to 26 classes sharing one value. So "five sites per level" was five draws from a
class of up to 26, and the sweep's bars were missed because steps in `F_local` are only nine wide and each step pools many phases.

The census replaces the sample with **the population**: one world per phase class, 144 runs at radius 6 gap 9, one seed each (X190
showed seeds on a site are the same world; X191 showed sites in one phase are the same world). This also makes possible the design
X191 could not build — a **within-`F_local` contrast**, because several phase classes share one inflow value and differ in what the
field does between the bodies.

## 2. Positive control fires

The control fires if (a) every one of the 144 classes is realised by exactly one world whose recomputed `F_local` matches the
enumerated value to 0.0025, (b) the ring peak is at least 0.3 on the slices used, (c) at least **12 of the 144** worlds reach a saved
slice with two components, and (d) the `F_local` values realise at least **8 of the 9** distinct values, each with at least 4 classes.
Thresholds: 144, 0.0025, 0.3, 12, 8, 4.

## 3. Readout exists and varies

The registered readout of X190/X191: the contact-moment bridge ratio — the field value midway between the two bodies over the maximum
of `v` inside a radius-10 disc around them, at the last saved slice on which the two bodies are still separate — plus the outcome
(one component at some sample). Slice schedule as before. The aggregate reports, per `F_local` value, the classes' ratios, their
spread, and the fusion share.

## 4. Sensitivity arithmetic, and the prediction

144 runs, one per phase class; the classes' ratios in the two measured levels of X190 were 0.138-0.399, so a within-level difference
of 0.05 is at the scale the phenomenon has already shown, and it is the bar. Registered **before the run**:

- **the ratio depends on the phase beyond the inflow**: at the `F_local` value with the most classes (0.0225, 26 classes) the spread
  of the ratios is at least **0.05** — i.e. the bridge is not a function of `F_local` alone;
- **the ratio falls with the inflow over the population**: Spearman over the 144 classes is at most **−0.5**;
- **the outcome follows the bridge within a fixed inflow**: at the `F_local` value with the most classes, the worlds whose ratio is
  above that value's median fuse **at least 0.3 more often** than those below it;
- and the outcome falls with the inflow over the nine values (the top value's share is at most the bottom value's).

## 5. Refusal rule

If the within-level spread is below 0.05, the item is recorded as **the bridge is a function of the inflow alone** and the phase
variation seen in X190/X191 is attributed to the readout's noise rather than to the world, which changes how the mechanism must be
stated. If the within-level outcome contrast is below 0.3, the item is recorded as **the bridge varies but the outcome does not
follow it** — the mechanism would then be a description of the field rather than of the fusion, and the law's boundary condition
would have to be written without it. If fewer than 12 worlds reach the contact moment, the item is recorded as **not sensitive by
construction** and the arm is widened.

## 6. What would kill it

The census is per phase *class*, and a class is one representative seed: if two seeds of one class differed, the class would not be
the right unit — X190's zero within-site spread and X191's zero within-phase spread are the evidence that it is, and both are
reported beside this census. Nine `F_local` values with unequal class counts make the Spearman over classes weight the crowded
values; the aggregate therefore reports the correlation both over classes and over the nine value means. The census is one arm
(radius 6 gap 9): nothing here says the same structure holds at the smaller bodies, where X190 found the opposite sign at radius 3.

## 7. Implementation notes

Runner `scripts/x192_phase_census.py` enumerates the 144 phase classes with one representative seed each and runs them with the
usual slice schedule into `_hourly/x192_fields/` (one world per class, no seeds repeated). Analysis
`scripts/x192_phase_census_analyse.py` reuses the contact-moment measurement and reports the per-value tables, the within-value
contrast at the most crowded value, and the correlations over classes and over value means. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x192_phase_census.json`. Cost about twelve minutes of CPU.
