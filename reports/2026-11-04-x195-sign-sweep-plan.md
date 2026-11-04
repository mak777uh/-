# X195 — where does the sign change? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X193 (radius 3 gap 10) and X192 (radius 6 gap 9) find the same mechanism — at a fixed local inflow the bridge decides the outcome —
and opposite signs of the inflow–outcome relation: the fusion share **rises** with the inflow at radius 3 (Spearman +0.413 over
classes, +0.515 over the nine value means) and **falls** at radius 6 (−0.378 and −0.833). The bridge account explains the reversal as
a size effect — a stronger inflow thins the bridge between large bodies and thickens it between small ones — and that account makes a
checkable prediction: the sign must move **monotonically somewhere between** the two, which is what this item measures. It runs the
same phase census at **radius 4 gap 12** and **radius 5 gap 10**, both with a centre separation of 20 cells against radius 6's 21 and
radius 3's 16, so the inflow band and the phase map stay as close to the measured arms as the geometry allows.

## 2. Positive control fires

The control fires if each arm realises all 144 phase classes with one representative world each (threshold 288 runs, 144 per arm),
if each arm's recomputed `F_local` matches its enumerated value to 0.0025, if the ring peak is at least 0.3 on the slices used, if at
least **12** worlds per arm reach the contact moment (bar 12), and if each arm realises at least **8** of its inflow values with at
least 4 classes each (bars 8 and 4). Any arm failing any of these is dropped and said so.

## 3. Readout exists and varies

The registered readout of X190–X193: the contact-moment bridge ratio (the field midway between the bodies over the maximum inside a
radius-10 disc around them, at the last saved slice on which the two pieces are still separate), with the outcome being one component
at some sample. The aggregate reports each arm's per-value table, its within-value spread and fusion share, and the sign of the
inflow–outcome relation both over classes and over the value means, on the same footing as X192 and X193 so the four radii can be
read in one row.

## 4. Sensitivity arithmetic, and the prediction

Radius 3 and radius 6 each delivered a clear sign with 144 worlds and a within-value spread of 0.40–0.45, so the same 144 worlds per
arm are enough to place an intermediate sign if the change is between them. Registered **before the run**:

- **the phase decides the bridge at fixed inflow at both radii**: the spread at the most crowded inflow value is at least **0.05** in
  each arm;
- **the outcome follows the bridge at fixed inflow at both radii**: at that value the worlds above its median ratio fuse at least
  **0.3 more often** than those below, in each arm;
- **the sign moves monotonically with size**: the four measured radii order as `r3` (positive), `r4`, `r5`, `r6` (negative) with the
  class-level Spearman **not increasing** from radius 3 to radius 6 (a sequence like +, +, −, −, or +, 0, −, −), so the change lies at
  or between radii 4 and 5.

## 5. Refusal rule

If the four radii order non-monotonically (for instance +, −, +, −), the item is recorded as **size does not order the sign** and the
two published censuses stand as two arms rather than as one trend — a substantive restriction, written as one. If an arm's spread is
below 0.05, that arm is recorded as **the phase does not decide the bridge at this size**, and the mechanism's range is restricted to
the sizes where it does. If an arm cannot realise its classes or fewer than 12 of its worlds reach the contact moment, that arm is
recorded as **not sensitive by construction** and the intermediate radii are widened or dropped rather than stretched.

## 6. What would kill it

The separation is held at 20 cells, but radius 4 and radius 5 bodies are neither radius 3 nor radius 6 bodies, so an intermediate sign
is evidence about the trend and not a claim that any one arm reproduces another. The class unit is again one representative world per
class, resting on X190/X191's zero within-site and within-phase spread and on X194's finding that the selected arms are where the
clone structure lives — which is exactly where these censuses are. X194 also showed that a phase alone over-counts worlds when
several arms pool, so every count here is per arm, never pooled. And the reversal is a property of this line's two geometries and one
nominal inflow; nothing here claims it for another band.

## 7. Implementation notes

Runner `scripts/x195_sign_sweep.py` (both arms in one script, per-arm class census, slices into `_hourly/x195_fields/<arm>/`),
analysis `scripts/x195_sign_sweep_analyse.py` (per-arm tables plus the four-radius sign row). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x195_sign_sweep.json`. Cost about twenty-five minutes of CPU for 288 runs.
