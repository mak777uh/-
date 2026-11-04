# X176 — Two factors, one prediction: radius 6 at gap 10 (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X175 refuted the single-curve reading of X174 by finding two arms with the same share (0.27) and different corridors (0.437 at
radius 4.5 gap 9, 0.492 at radius 4.5 gap 10), and it left a two-factor picture: the corridor at contact rises with the arm's
marginality and with the initial gap. This item tests that picture at a cell where the two factors point the **same** way and
where the crossing has clearly passed.

Radius 6 crosses at surface gap 9 (X158: 3/10 at 9, 0/10 at 10). At **gap 10** the arm is past its crossing, so its share should
be low — and its bridge must span a longer distance than at that size's own crossing gap. Both factors predict a **high**
corridor.

## 2. Positive control fires

The control fires if the peak stays inside [0.05, 2.0] at every read (thresholds 0.05 and 2.0), the corridor reads below the peak
in **every** contact run (share 1.0), and — because a share of zero would make the arm undecidable — the arm produces at least
**three** contact events out of fifteen. If fewer than three, the arm is past the crossing by more than the design can resolve and
the item is recorded as undecided rather than as a confirmation.

## 3. Readout exists and varies

X170's contact-time corridor, unchanged. It must vary across runs (sd ≥ 0.02) and must not be 0 or 1 in every run.

## 4. Sensitivity arithmetic, and the prediction

Fifteen seeds at radius 6, gap 10, `F` = 0.030. Registered **before the run**:

- **share: between 0.05 and 0.25** (1 to 4 of 15), from radius 6's own crossing at gap 9 (3/10) falling away one cell out;
- **corridor: 0.50 to 0.55**, from the two-factor picture — more marginal than any arm measured (X174's share-0.27 arms read
  0.49 and 0.52) and spanning the longest bridge of any arm in the (size, gap) plane.

With three to four contact events the median's standard error is about 0.02, so a systematic offset of 0.04 is visible; a miss
would have to be that large to count.

## 5. Refusal rule

If both intervals hold, the item is recorded as **the two-factor picture predicts a cell it was not fitted to**, and the band's
upper edge (0.52-0.55) is where the most marginal, longest-bridge merges sit. If the share holds but the corridor comes in
significantly lower (below 0.50), the gap factor is weaker than X175's single comparison suggested and the band's upper edge
belongs to the rate, not to the geometry. If the share misses (the arm fuses more than 4 of 15), radius 6's crossing is not where
X158 put it and the item says so.

## 6. What would kill it

Radius 6 is the size whose crossing is the outlier in X158 (9 rather than 10), so its "one cell past the crossing" arm may not be
one cell past at all. If the share comes out at 0.4-0.5, the arm is still at its crossing and the prediction's premise — that the
crossing has passed — is wrong, which the item will record as a failed premise rather than a failed prediction.

## 7. Implementation notes

Runner `scripts/x176_past_crossing.py` (radius 6, gap 10, `F` = 0.030, seeds 1081-1095, 2 000 steps, field dumps every ten steps
into a gitignored directory), analysis `scripts/x176_past_crossing_analyse.py` (contact-time corridor, the registered intervals,
and the arm's position relative to X175's two-factor reading). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x176_past_crossing.json`. Cost about fifteen minutes of CPU.
