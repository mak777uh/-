# X198 — the fusion share as a function of the surface-to-surface gap (pre-registration, 05.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X196 established the either-or with three arms: the surface-to-surface gap switches fusion and the body size shifts it. Two of
the five rows of its table, however, came from different radii, so the shape of the switch between a 9-cell and an 8-cell gap is
still interpolated across two bodies, and the "shift of about a tenth" rests on a single matched pair (radius 4 and radius 6 at a
gap of 8). This item runs the switch itself at a fixed size — **radius 4 at gaps 8, 9, 10, 11 and 12** — and repeats the three
largest gaps at **radius 6** (gaps 8, 9, 10). The centre separation follows from the geometry, `separation = 2 r + gap`, and is
reported with the measured radii and gaps rather than the nominal ones.

Two of the eight arms are deliberate replications of already committed measurements: radius 4 gap 12 and radius 6 gap 9 were run
in X195/X196/X192, and radius 4 gap 8 in X196. They are re-run inside one process so that the curve is internally consistent, and
their agreement with the committed values is itself a registered check (§4.5).

## 2. Positive control fires

The control fires if each arm realises all 144 phase classes with one representative world each (threshold 1152 runs, 144 per
arm), if each arm's recomputed `F_local` matches its enumerated value to 0.0025, if the ring peak is at least 0.3 on the slices
used, and if at least **12** worlds per arm reach the contact moment (bar 12). An arm failing any of these is dropped and said so.

## 3. Readout exists and varies

The registered readout is unchanged: the contact-moment bridge ratio, and the outcome as one component at some sample. The
aggregate reports, per arm, the fusion share over its phase classes, the per-value table, the phase spread at the most crowded
value, and the bridge's association with the inflow; plus, for the outcome, the share itself, since the whole point of this item
is a share that varies between the arms.

## 4. Sensitivity arithmetic, and the prediction

At 144 worlds per arm the binomial sd of a share near 0.5 is `sqrt(0.25/144) ≈ 0.042`, so a step of 0.2 between neighbouring gaps
is close to five of those; near 0 and near 1 the sd is smaller still (`sqrt(0.04/144) ≈ 0.017`). The five radius-4 arms give five
successive shares; under the null of exchangeable arms the chance that they come out in one prescribed order is `1/5! = 0.008`.
Registered **before the run**:

- **the share is monotone in the gap at radius 4**: `share(12) ≤ share(11) ≤ share(10) ≤ share(9) ≤ share(8)` over the nine
  supply values, with `share(12) = 0` and `share(8) ≥ 0.9`;
- **the switch is localised to a single cell**: at least one neighbouring pair of gaps differs by at least **0.4** in share,
  which places the transition between two adjacent gap values rather than across the two-cell spacing X196 could resolve;
- **the size shift survives the finer grid**: at matched gaps 8, 9 and 10 the radius-6 share is not below the radius-4 share by
  more than 0.05, and at least at one of those gaps the radius-6 share is higher by at least **0.10**;
- **the phase still decides the bridge in every arm**: the spread at the most crowded supply value is at least **0.05** in each
  arm, and at least 12 worlds reach contact in each arm;
- **the line reproduces itself**: the re-run arms match their committed values — radius 4 gap 12 at 0.00, radius 6 gap 9 at 0.40,
  radius 4 gap 8 at 0.96 — within ±0.05 in share.

## 5. Refusal rule

If the radius-4 shares are **not** monotone, the item is recorded as **the gap is not the only variable in this band**, and the
supply distribution of the offending arm is reported with it. If the radius-6 curve lies **to the right** of the radius-4 curve at
matched gaps (lower share), the item is recorded as **the size shift is opposite in sign to X196**, which corrects X196 rather
than extending it. If **no** arm has a share strictly between 0.05 and 0.95, the item is recorded as **the switch is binary on this
grid**, which is a result about the rasterisation as much as about the medium. If an arm fails the positive control it is dropped
from the curve and the curve is reported with the gap it is missing.

## 6. What would kill it

The share is a mean over nine supply values, and the nine values are not evenly populated by the 144 phase classes, so a curve
built on means can move because the weighting moves and not because the gap does; the per-value table is therefore reported and
the class-level association is given alongside. Every arm is again one representative world per phase class, resting on
X190/X191's zero within-site and within-phase spread, and X194 showed the clone structure lives exactly in these selected arms —
so 1152 worlds are not 1152 independent observations, and the stated sd is a plotting aid, not an interval. Finally, this
geometry band is narrow by construction: a curve over gaps 8–12 cells says nothing about a 30-cell gap.

## 7. Implementation notes

Runner `scripts/x198_gap_curve.py` (eight arms, per-arm class census, slices into `_hourly/x198_fields/<arm>/`), analysis
`scripts/x198_gap_curve_analyse.py`. Aggregate `morphogenesis/experiments/E09_pond/l1_field_x198_gap_curve.json`. Cost about one
hundred minutes of CPU for 1152 runs. The result card is `docs/world-design.md` §10jg plus that aggregate (the pond-line
exception, AGENTS.md §6.5).
