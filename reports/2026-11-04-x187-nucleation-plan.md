# X187 — does a warm medium nucleate its own bodies at the largest size? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X186 re-read the 57-cell table in the local inflow and found the per-cell association positive in 9 of 11 cells with spread, as
the law of X183/X184 predicts — with the exceptions both at the largest measured radius: r_eff 5.86 at gap 7 (slope −0.132) and
at gap 9 (−0.478, 54 runs, share 0.37). There the warmer the pair's surroundings, the *less* it ends as one component.

The candidate mechanism is the one that made the pair's midpoint anti-predictive in X180 and X182: in this world a warmer medium
is a medium that **nucleates**. A pair of large bodies sits in a warm site, the surrounding field buds bodies of its own, and the
component count never reaches one even when the fronts meet. This item manipulates the pair's local inflow at two levels and
counts the bodies that appear besides the two seeded ones — which the component log records with positions at every sample, so
the readout needs no field dumps.

## 2. Positive control fires

The control fires if (a) each run's recomputed local inflow at the colder body lands inside its level (tolerance 0.0025), (b) the
two levels' means are at least **0.008 apart** in `F_local` (a factor of 1.4 at `F` = 0.030), (c) at least three runs per group
reach a minimum component count of 2 or less, so "how many bodies are around the pair" is measurable rather than vacuous, and
(d) the peak stays inside [0.05, 2.0] at every read. Thresholds: 0.0025, 0.008, three runs, [0.05, 2.0]. A run whose level
misses is excluded and counted.

## 3. Readout exists and varies

Primary: the number of components **other than the two seeded ones** whose centres lie within 8 cells of the pair's midpoint at
the sample where the total component count is smallest — a nucleation count. Secondary: the share, and the final component count.
The secondary must vary (the same readout varies within each arm already, X179).

## 4. Sensitivity arithmetic, and the prediction

Two arms (radius 6 gap 9; radius 3 gap 10), two levels of the colder body's inflow (0.019 cold, 0.030 warm), six seeds per cell =
24 runs, 3 000 steps and samples every 10 steps, so about 300 samples per run. Radius 6 costs about 40 s a run and radius 3 about
30 s, i.e. about fifteen minutes total. Registered **before the run**:

- **radius 6 gap 9:** the warm level coalesces **less** than the cold one and shows **more** extra bodies around the pair
  (median extra ≥ 1 at the sample of minimum count against 0 for the cold level);
- **radius 3 gap 10:** the warm level coalesces **more** than the cold one, and the difference in extra bodies is **≤ 1** in the
  same direction — no nucleation signature.

The design's power is thin by construction: six seeds per group put the share's standard error near 0.2, so the *count* is the
registered primary and the share a description; a difference in median extra bodies of one body is what the item can see.

## 5. Refusal rule

If the radius-6 warm level shows more extra bodies *and* the cold level coalesces more, the item is recorded as **a warm medium
nucleates bodies of its own at the largest size, and that is why the local-inflow law flips sign there**, with the consequence
stated: the law's sign is size-dependent, and the crossing table's radius-5.9 cells must be read with the nucleation count beside
the share. If the extra-body count does not differ between levels, the item is recorded as **the flip is not nucleation** and the
flipped cells stand unexplained, to be attacked by holding the site fixed and varying the gap instead. If the warm level shows
more extra bodies at radius 3 as well, the item is recorded as **nucleation is general and the law's sign at small radius must be
re-derived**, which weakens X183/X184's reading.

## 6. What would kill it

The extra-body count is a proxy for nucleation and is computed from centres, so a body that buds and merges within one sample
interval is invisible; a null result therefore does not prove the absence of nucleation, only its absence at this sampling. Both
arms use the same site arithmetic, so a mistake there moves both levels together — the audit recomputes every run's level from
its logged centres and reports the misses rather than dropping them silently. And 3 000 steps at radius 6 is long enough for the
pair to be buried by the field (X173 saw that at about 150 of 3 000 steps), so the minimum-count sample is used rather than the
final state, and the final count is reported beside it.

## 7. Implementation notes

Runner `scripts/x187_large_radius.py` selects seeds by the colder body's pattern value for each arm's own separation and runs the
four groups. Analysis `scripts/x187_nucleation_analyse.py` recomputes the levels from the logged centres, counts extra bodies
around the pair at the minimum-count sample, and reports the two arms' levels side by side. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x187_nucleation.json`. Cost about fifteen minutes of CPU.
