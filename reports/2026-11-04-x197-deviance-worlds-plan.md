# X197 — does X186's published deviance drop survive counting worlds? (pre-registration, 04.11)

**Status:** analysis of existing artifacts, no runs; registered before the numbers were computed.

## 1. Manipulation is connected

X186's headline was that the **local inflow** beats the **nominal F** in a binomial deviance over the mixed cells of the observational
pool: 464.5 → 436.5, a drop of 28.0, with 9 of 11 cells showing the expected sign. X194 then showed that this pool is nearly all
singleton worlds (757 runs, 633 arm-held worlds) and that its own AUC barely moves when worlds replace runs — but X194's statistic
was an AUC of its own, not X186's deviance. This item re-runs **X186's own deviance and slope** over the same pool, twice: one row per
run and one row per **world** (cell × phase), with a phase-clustered bootstrap beside a run bootstrap for the drop. The pool keeps
X186's guard (x182/x184/x187 excluded) and adds the later arms selected by the inflow or the phase (x18*/x19*), because those are
selected by the readout's driver and would bias the association.

## 2. Positive control fires

The control fires if the pool reproduces its expected size (at least **500** runs and at least **400** of them in mixed cells, bars
500 and 400), if at least **4** mixed cells are found (bar 4), if both deviance fits return a number for runs and for worlds (threshold:
non-null), and if each bootstrap produces at least **100** usable resamples out of 120 (bar 100).

## 3. Readout exists and varies

The readout is X186's own: the drop in binomial deviance between a model on the nominal `F` and a model on the local inflow, with the
per-cell slope's sign as the secondary readout. It is comparable to X186's published 28.0 exactly because the code is X186's. The
aggregate also reports how many cells still carry both outcomes when a cell's runs are collapsed into worlds, since a cell that loses
its mixed character under collapsing tells us where the arms and phases sat.

## 4. Sensitivity arithmetic, and the prediction

X186's pool has 5 to 30 runs per mixed cell, and X194 measured fewer than one repeat per world overall, so collapsing should change
the row count by only a few per cent and the drop by a fraction of its own size. Registered **before the numbers**:

- the mixed pool collapses to at most **0.9** worlds per run (i.e. at least 10 per cent of rows are repeats);
- the drop over worlds stays **within 20 per cent** of the drop over runs;
- the phase-clustered bootstrap puts the drop above its own bar of 20 at least as often as the run bootstrap does, so the interval
  does not widen materially.

## 5. Refusal rule

If the mixed pool collapses to nearly one world per run (≥ 0.95), the item is recorded as **X186 was not affected by pooling** and
X192's proposal is closed for this statistic as well, with X194's finding extended from an AUC to a deviance. If the drop over worlds
moves by more than 20 per cent, the item is recorded as **X186's number was carried by repeated runs** and the published claim needs a
correction in the manuscript rather than a footnote. If the collapse itself fails the control, the item is recorded as **not sensitive
by construction**.

## 6. What would kill it

X186 measured its deviance on the pool as it stood then; this re-runs it on the pool as it stands now minus the selected arms, so a
discrepancy against 464.5/436.5 is expected and is reported as a pool difference rather than as a correction of the published number.
The deviance fit is X186's grid search, retained literally so the two numbers are comparable, and its coarseness (slope in steps of
0.1, shifts in steps of 0.05) is the same in both readings. Collapsing a cell's runs to a world uses the mean outcome, which turns a
mixed cell into a fractional row: that is a quasi-binomial reading and it is labelled as such, with the count of worlds that are still
mixed reported beside it.

## 7. Implementation notes

Script `scripts/x197_deviance_worlds.py`, aggregate `morphogenesis/experiments/E09_pond/l1_field_x197_deviance_worlds.json`. Cost a
few minutes of CPU (two bootstraps of 120 resamples over about 700 rows).
