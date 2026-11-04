# X193 — the phase census at the smaller bodies (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X192 censused the 144 phase classes at radius 6 gap 9 and found the mechanism's sharpest form: at a single inflow value the bridge
ratio spans 0.006–0.454 and the worlds above that value's median ratio fuse 1.0 of the time against 0.111 below (Fisher p < 0.001),
with a logistic slope of fusion on the ratio of 6.094 (z 5.76) over all 144 worlds. The same census at **radius 3 gap 10** asks two
things at once: whether the phase decides the bridge there as well, and whether the **sign** of the inflow–outcome relation is
reversed, as X190 found at this arm (0 of 5 cold sites fused against 3 of 5 warm). If both hold, the line has one mechanism whose sign
depends on the size, not two unrelated laws.

## 2. Positive control fires

As X192, at the smaller arm: every phase class realised by one world whose recomputed `F_local` matches to 0.0025, ring peak at
least 0.3, at least 12 worlds reaching the contact moment, at least 8 of the 9 inflow values realised with at least 4 classes each.
Thresholds: 144, 0.0025, 0.3, 12, 8, 4.

## 3. Readout exists and varies

The registered readout of X190–X192: the contact-moment bridge ratio (field midway between the bodies over the maximum in a radius-10
disc, at the last saved slice on which the two pieces are separate), plus the run's outcome and, at the most crowded inflow value, the
within-value contrast between worlds above and below that value's median ratio.

## 4. Sensitivity arithmetic, and the prediction

144 runs, one per phase class, one seed each. At this arm X190's four measured levels spanned ratios 0.227 (cold) to 0.316 (warm) with
a spread inside the warm level of 0.000 among identical phases, and X193's classes are expected to span a comparable or wider range,
so the same 0.05 spread bar applies. Registered **before the run**:

- the ratio depends on the phase beyond the inflow: the spread at the most crowded inflow value is at least **0.05**;
- the outcome follows the bridge at fixed inflow: at that value the worlds above its median ratio fuse at least **0.3 more often**
  than those below;
- **the sign of the inflow–outcome relation is reversed relative to radius 6**: the top inflow value's fusion share **exceeds** the
  bottom value's (at radius 6 it was 1.0 against 0.0 the other way);
- the logistic slope of fusion on the bridge ratio over all classes is **positive** with |z| ≥ 2.

## 5. Refusal rule

If the top value does not fuse more often than the bottom, the size dependence is recorded as **not established at this arm** and the
radius-3 reversal rests on X190's two-population comparison alone. If the phase spread is below 0.05 here, the phase dependence is
recorded as **a property of the largest bodies only**, and the mechanism's generality is restricted accordingly — that is a
substantive restriction and is written as one. If fewer than 12 worlds reach the contact moment, the item is recorded as **not
sensitive by construction**.

## 6. What would kill it

The phase map at radius 3 gap 10 is a different map from radius 6's (the separation changes which two discs set `G`), so the two
censuses are not the same sample and their class counts can differ; the item reports its own class count and inflow values rather than
assuming nine. The class unit again rests on one representative world per class, with X190's and X191's zero within-site and
within-phase spreads as the evidence, and a two-seed census is the registered way to price it. And a reversal at radius 3 does not by
itself make one law: a common mechanism is the *interpretation* the next paragraph argues for, not an extra measurement.

## 7. Implementation notes

Runner `scripts/x193_phase_census_r3.py`, analysis `scripts/x193_phase_census_r3_analyse.py`, both generated from the X192 pair with
the arm changed (radius 3, gap 10, separation 16) so that the measurement code is literally the same. Slices into
`_hourly/x193_fields/`; aggregate `morphogenesis/experiments/E09_pond/l1_field_x193_phase_census_r3.json`. Cost about twelve minutes
of CPU.
