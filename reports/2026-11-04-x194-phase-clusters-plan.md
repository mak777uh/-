# X194 — how many worlds do the published pools contain? (pre-registration, 04.11)

**Status:** analysis of existing artifacts, no runs; registered before the numbers were computed.

## 1. Manipulation is connected

X192 established that the phase (bodies' positions modulo the pattern's 12-cell period) decides the bridge at fixed inflow; X190/X191
established that seeds within a site and sites within a phase are clones. Every pooled statistic of the line was computed over runs,
and a run count is an upper bound on the number of independent worlds. This item counts the worlds in the observational pool and
asks how much of each published association is carried by how few worlds.

## 2. Positive control fires

The control fires if 757 runs give exactly 633 worlds with no run in two worlds (threshold 633), if at least **20** worlds hold more
than one run (bar 20), if at least **500** runs and **100** worlds enter the pooled AUC (bars 500 and 100), and if each bootstrap runs
at least **1000** iterations (bar 1000) — any of these failing makes the pool unusable for an interval comparison.

A world is the **phase together with the arm** (initial radius bin, gap, `F`, steps): the phase fixes the positions only, so two runs
sharing a phase but differing in arm are different worlds, and a phase that shows both outcomes across arms is not evidence against
the class unit. For each world the item reports how many runs it holds and whether its runs agree in outcome; a world whose runs
disagree after the arm is held fixed is the direct price of the class unit and is reported, not hidden.

## 3. Readout exists and varies

The readout varies by construction: the pooled AUC must lie strictly between 0.5 and 1.0, otherwise no comparison of intervals is
made.

## 3a. What is a world

The line's own readout for this comparison: the association between the local inflow and the fusion outcome over the observational
pool (the ladder and its siblings), with every `x18*`/`x19*` pool excluded because those were selected **by** the inflow or by the
phase and would be circular. The pooled AUC is computed over runs and over worlds, and the same statistic is bootstrapped twice -
resampling runs and resampling worlds - so the two interval widths can be compared.

## 4. Sensitivity arithmetic, and the prediction

A 1.3x widening of the bootstrap standard deviation is the bar because with 633 worlds and a run count of 757 the clone structure can inflate at most that much if the repeats are few; the pool's own arithmetic - 757 runs against 633 worlds - is written here before the numbers, and the fourth prediction is stated as testable only against a like-for-like arm.

## 4a. Prediction registered before the numbers

- the observational pool holds substantially fewer worlds than runs: at most **a third** of the runs are distinct worlds;
- at least **20** worlds hold more than one run (the pool is not merely a set of singletons);
- resampling worlds gives an interval **at least 1.3 times wider** than resampling runs on the same statistic, i.e. the published
  intervals of the line are too narrow wherever their unit was a run;
- excluding the selected pools changes the pooled AUC by at least 0.05 against the earlier published pooled value, if that value was
  measured on them.

## 5. Refusal rule

If the pool turns out to be nearly all singletons (worlds ≈ runs), the item is recorded as **the published intervals do not need
widening** and the clone/phase findings remain local to the sweep-like designs. If a world containing several runs disagrees in
outcome, the item is recorded as **the world is not a sufficient unit** and the finding is stated as a bound on the line's
granularity rather than as a correction.

## 6. What would kill it

The pools differ in F, steps and geometry, so "world" pools runs that are not replications of one another; the item therefore
reports the world counts per cell as well as pooled, and the pooled figure is a statement about the pool, not about one experiment.
X187's own tests were computed with a readout of their own, so this item's re-expression of those groups is not a correction of them
and is labelled as such. And a run count remains a valid denominator for a *selected* pool by design: the finding concerns pooled
observational statistics, not the arms that were laid out on purpose.
