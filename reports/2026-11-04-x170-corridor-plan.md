# X170 — Why the crossing ignores the source: the corridor at contact (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X168c and X168d showed that the ten-cell crossing does not depend on the inflow rate across `F` = 0.026 to 0.036, and that the
result is measured rather than power-limited. A number without a mechanism is a fact looking for a reason: if the crossing is
a property of the reaction-diffusion pair, then at the moment two bodies come into contact the *field between them* should be
in the same state at every rate — the source sets how much chemical there is, but the geometry of the merge should be set by
the ratio of the two diffusion lengths and not by the supply.

This item measures that state. Three inflow rates, five seeds each, surface gap 10 (separation 16, radius 3): the arm in which
the crossing is half-fused, so both outcomes are present and the field is neither trivially separating nor trivially merged.
The field is dumped every ten steps, and the corridor is read at the last logged step at which there are still two bodies.

## 2. Positive control fires

The measure has an internal control: the peak of the field over the bodies must fall inside a plausible band (above 0.05 and
below 2.0) at every dump, and the corridor value must be **below** the body peak in at least 80 % of the dumps that have two
bodies. If the corridor reads at or above the peak, the reading is not measuring a corridor; if the peak leaves the band, the
run is not in the regime the crossing was measured in. The control fires if both hold at every seed.

## 3. Readout exists and varies

The readout is the **normalised corridor concentration** at contact: the minimum of the field along the segment joining the two
components' centres at the last two-body step, divided by the larger of the two components' peak values at that step. It must
vary across runs (standard deviation at least 0.02) and must not sit at 0 or 1 in every run (that would be a degenerate read).

## 4. Sensitivity arithmetic

The comparison is between three group medians with five seeds each. If the source really does not reach the corridor, the group
medians should differ by less than the within-group spread; with five runs per group the standard error of a median is about
0.7 sd, so a difference of one sd between group medians is the smallest that five seeds can resolve, and the item states the
within-group sd so the reader can see what was resolvable. A difference of two power-of-two factors in `F` (0.026 to 0.036 is
1.4×) that leaves the corridor unchanged to within one sd is the claim.

## 5. Refusal rule

If the corridor medians differ by more than one pooled sd between the extreme rates, the item is recorded as **the corridor does
depend on the source, and the insensitivity of the crossing needs a different explanation** — that is a real result and it
gets reported as such, with the direction. If the positive control fails at a rate, that rate is dropped and the report says
so. If the readout is degenerate (0 or 1 everywhere), the item is not reportable and says why.

## 6. What would kill it

The most likely failure is that the corridor is contaminated by the bodies' own rims: the segment between two centres passes
through both bodies, so its minimum can be dominated by the interface rather than by the gap. The design guards against this by
taking the minimum only over the middle third of the segment, which at a gap of 10 cells and bodies of radius about 6 lies in
the space between them, and by reporting the peak as well.

## 7. Implementation notes

Runner `scripts/x170_corridor.py` (three rates × five seeds, gap 10, 2 000 steps, field dumps every 10 steps into a gitignored
directory), analysis `scripts/x170_corridor_analyse.py` (last two-body step per run, corridor minimum over the middle third,
normalisation by the body peak, group medians and spreads, control check). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x170_corridor.json`. Cost about 20 minutes of CPU.
