# X196 — is the fusion window set by the body size or by the gap? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X195 measured **zero** fusion events in 288 worlds at radius 4 gap 12 and radius 5 gap 10, both with a centre separation of 20 cells,
while all 288 kept a measurable bridge whose association with the inflow ran in the radius-6 direction. The window can be set by the
**body size** (bodies too large for the dynamics to close the gap) or by the **separation** (a 20-cell gap is simply too far), and the
two are separable by changing one at a time:

- **radius 4, gap 10** (separation 18) and **radius 4, gap 8** (separation 16): the size is held and the bodies are brought together;
  radius 4 gap 12 (separation 20, no fusion) is the reference and radius 3 gap 10 (separation 16, fuses) is the small-body end;
- **radius 6, gap 8** (separation 20): the separation matches the radius-4 reference and the body is the one that partly fuses at gap
  9 (separation 21). If separation were the barrier, this arm would not fuse either.

## 2. Positive control fires

The control fires if each arm realises all 144 phase classes with one representative world each (threshold 432 runs, 144 per arm), if
each arm's recomputed `F_local` matches its enumerated value to 0.0025, if the ring peak is at least 0.3 on the slices used, and if at
least **12** worlds per arm reach the contact moment (bar 12). An arm failing any of these is dropped and said so. The reference arms
enter only from their committed aggregates, never pooled with these.

## 3. Readout exists and varies

The registered readout of X190–X195: the contact-moment bridge ratio, with the outcome being one component at some sample. The
aggregate reports per arm the fusion share over its phase classes, the per-value table, the phase spread at the most crowded value,
and the bridge's association with the inflow — plus, for the outcome, whether it varies at all in that arm, because X195 showed that
an arm can be informative about the bridge and silent about the outcome.

## 4. Sensitivity arithmetic, and the prediction

The reference arms give the scale: radius 3 gap 10 fuses at 0.0 to 1.0 across its inflow values, radius 4 gap 12 fuses never, radius 6
gap 9 fuses in 0.5 of its worlds on average. Bringing radius 4 from a 12-cell gap to 10 and 8 changes the separation by 2 and 4 cells
against a sampling of 144 worlds, and the negative control (radius 4 gap 12) is an absolute zero, so any fusion at all is a signal.
Registered **before the run**:

- **radius 4 fuses more as the gap closes**: the fusion share at radius 4 is **0** at gap 12 (reference), and at least one of gap 10
  and gap 8 shows a share **above 0.1**, with the share at gap 8 not below the share at gap 10;
- **the separation is not the barrier**: radius 6 gap 8 (separation 20) fuses, with a share **at least as large as** the average
  radius-6 gap-9 share over the same inflow values;
- **the phase still decides the bridge at every arm**: the spread at the most crowded value is at least **0.05** in each arm.

The registered positive control for the outcome is therefore radius 4 gap 8: if bringing the small body's partner two cells closer does
not produce a single fusion in 144 worlds, the barrier is the size at that separation and not the gap.

## 5. Refusal rule

If radius 4 gap 8 stays at zero fusion while radius 6 gap 8 fuses, the item is recorded as **the window is set by the size at a fixed
separation**, and X195's window is a size window. If both stay at zero, the item is recorded as **the separation is the barrier over
this whole range**, which changes the mechanism's variable from size to separation and is written as such. If radius 4 gap 8 fuses but
radius 4 gap 10 does not, the item is recorded as **the window closes sharply between separations 20 and 18** and the intermediate gap
is the place to look next. If the outcome varies in no arm, the item is recorded as **not sensitive by construction** and the
separations are widened further.

## 6. What would kill it

Holding the size and moving the gap also changes which cells the bodies occupy, so "the gap closes the window" is a statement about
this geometry band and not a continuous law of separation. Every arm is again one representative world per phase class, resting on
X190/X191's zero within-site and within-phase spread, and X194 showed the clone structure lives exactly in these selected arms. And
the radius-6 gap-8 arm differs from X192's gap-9 arm by one cell, which is the resolution of the rasterised discs — so its comparison
with radius 6 gap 9 is reported with the measured gaps and radii, not the nominal ones.

## 7. Implementation notes

Runner `scripts/x196_gap_or_size.py` (three arms, per-arm class census, slices into `_hourly/x196_fields/<arm>/`), analysis
`scripts/x196_gap_or_size_analyse.py`. Aggregate `morphogenesis/experiments/E09_pond/l1_field_x196_gap_or_size.json`. Cost about
thirty-six minutes of CPU for 432 runs.
