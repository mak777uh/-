# X175 — Testing the share-corridor curve at an interior point (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X174 put the block's eight arm-cells on one line: the corridor at contact falls as the arm's fusion share rises (Pearson −0.95
over eight cells), and that ordering explains why X171's three sizes agreed — their shares agreed. A relation fitted to eight
non-independent cells needs a cell it was not fitted to, chosen inside the (size, gap) plane that neither family covered.

**Radius 4.5 at surface gap 9** is that cell: radius 4.5 has only been run at gap 10 (share 0.27, corridor 0.49) and radius 3 at
gap 9 (share 0.80, corridor 0.41). Interpolating both coordinates gives a predicted share near **0.6** and a predicted corridor
near **0.44**.

## 2. Positive control fires

The control fires if the arm's peak field stays inside [0.05, 2.0] at every read (a threshold of 0.05 on the low side and 2.0 on
the high side), if the corridor reads below the peak in **every** contact run (share 1.0), and if the arm produces **at least
three** contact events. Fewer than three contacts means the arm is too far past its crossing to describe a point on the curve,
and the item is reported as unplaced rather than as a miss.

## 3. Readout exists and varies

X170's contact-time corridor, unchanged: the minimum of the field over the middle third of the segment between the two bodies'
centres at the last sampled step with two bodies, divided by the peak at that step. It must vary across runs (standard deviation
≥ 0.02) and must not sit at 0 or 1 in every run.

## 4. Sensitivity arithmetic

Fifteen seeds at radius 4.5, gap 9, `F` = 0.030, with an expected eight to ten contact events; the within-arm spread of this
readout at radius 4.5 is 0.022 (X171). The prediction is stated as an interval, **0.42 to 0.46 for the corridor** and **0.45 to
0.72 for the share**, both wide enough to be reachable by an honest interpolation and narrow enough that a systematic offset of
0.08 would miss. With eight contacts the standard error of the median is about 0.01, so the corridor half of the prediction is
the sharp test and the share half is only a check that the arm is where it was placed.

## 5. Refusal rule

If the corridor lands inside 0.42-0.46 and the share inside 0.45-0.72, the item is recorded as **the curve is real at an
interior point**, and X174's eight-cell ordering survives an independent arm. If the corridor misses but the share lands, the
curve's shape is wrong even though the arm was placed correctly, and the relation is recorded as a two-family artefact. If both
miss, the arm was not placed where the interpolation said and the item says so without claiming anything about the curve.

## 6. What would kill it

One point cannot establish a curve; it can only fail to break one. A hit raises the relation from eight cells to nine and no
more. The real risk is that the interpolation is doing the work: radius 4.5 at gap 9 sits between two measured arms and any
smooth monotone relation would predict something in the middle, so a hit tests the *slope*, not the existence, of the relation.

## 7. Implementation notes

Runner `scripts/x175_interior.py` (radius 4.5, gap 9, `F` = 0.030, seeds 1061-1075, 2 000 steps, field dumps every ten steps into
a gitignored directory), analysis `scripts/x175_interior_analyse.py` (contact-time corridor, the two registered intervals, and the
arm's position on X174's curve). Aggregate `morphogenesis/experiments/E09_pond/l1_field_x175_interior.json`. Cost about ten
minutes of CPU.
