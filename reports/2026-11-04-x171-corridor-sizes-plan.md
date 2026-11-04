# X171 — Is the corridor at contact a size-independent criterion? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X170 found that the field between two bodies at the moment they become one reads **0.516 / 0.479 / 0.392** of the body peak
at `F` = 0.026 / 0.030 / 0.036, and that the fusion share at a fixed gap rises with the source. That turns the crossing from a
measured length into a candidate rule: **two bodies become one when the bridge between them reaches some fraction of the body
peak, and the crossing in cells is wherever that fraction is reached.** If the rule is real, the fraction at contact must be the
same at every body size — otherwise the "criterion" is just a description of one arm.

This item measures the corridor at contact at two other sizes, at the crossing gap for each: radius 4.5 at surface gap 10 and
radius 6 at surface gap 9, fifteen seeds each, at the reference rate `F` = 0.030. The radius-3 arm of X170 is the reference
value, and it was measured with the same definition.

## 2. Positive control fires

The control is internal and unchanged from X170: the body peak must stay inside [0.05, 2.0] at every read, and the corridor
must read below the peak in at least 80 % of the contact runs. In addition, each arm's **fusion share at its own crossing gap**
must lie between 0.2 and 0.8 — an arm that fuses in none or in all of its runs is not sitting at the crossing and its contact
value would describe a different point. If an arm fails either, that arm is dropped and the report says why.

## 3. Readout exists and varies

The readout is the same normalised corridor: the minimum of the field over the middle third of the segment joining the two
bodies' centres, at the last sampled step with two bodies, divided by the peak field at that step. It must vary across runs
(standard deviation at least 0.02 overall) and it must not be at 0 or 1 in every run.

## 4. Sensitivity arithmetic

The comparison is between the medians of three sizes at the reference rate, with 15 seeds of radius 3 already measured
(X170: 0.479, within-group spread 0.036) and 15 seeds each for the two new arms. With roughly ten contact events per arm the
standard error of a median is about 0.015, so a difference of 0.05 between sizes is about three standard errors and the design
can see it; a difference of 0.02 is not resolvable and will not be claimed. The item states the contact count per arm so the
reader can adjust that arithmetic themselves.

## 5. Refusal rule

If the three sizes' medians agree to within the pooled within-group spread, the item is recorded as **the corridor is a
size-independent criterion** and the grid of crossing gaps becomes predictable from it. If they differ by more than the pooled
spread, the item is recorded as **the corridor is not a criterion but a per-arm description**, X170's mechanism does not
generalise, and the crossing's dependence on the source stays a fact without a model.

## 6. What would kill it

The likeliest failure is not a difference between sizes but a difference between *gaps*: each arm sits at its own crossing gap,
so a size effect and a gap effect are confounded unless the corridor turns out to be flat, which is the hypothesis. The design
cannot separate them, and the report will say so; separating them needs a fourth arm at a non-crossing gap, which this item
does not run.

## 7. Implementation notes

Runner `scripts/x171_corridor_sizes.py` (two sizes × fifteen seeds at `F` = 0.030, 2 000 steps, field dumps every ten steps into
a gitignored directory), analysis `scripts/x171_corridor_sizes_analyse.py` (same readout as X170, plus the radius-3 reference
read from X170's aggregate, per-arm contact counts and fusion shares). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x171_corridor_sizes.json`. Cost about 25 minutes of CPU.
