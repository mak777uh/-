# X186 — the crossing table re-read in the local inflow (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X183 established that the rate a run "had" is the local inflow at its seeded sites: over the 139-run ladder the nominal rate
discriminates with AUC 0.587 and 0.5 within a level by construction, while the inflow at the seeded sites reaches 0.866 (0.895
within levels) and costs 129.3 of deviance against 185.0. X184 then moved the colder body's inflow in advance and the share went
0.00 → 1.00; X185 showed X182's opposite-signed midpoint control is the same law.

The consequence has not been drawn yet: **every share in the 57-cell crossing table is an average over the local inflows its
seeds happened to draw**, so the table's own numbers — including the cliff at radius 6 that X178 reported as 0.33 → 0.00 in one
cell of gap — may be partly a site draw. This item re-reads the table that way. It runs nothing; the covariates are computed from
the seeded centres of the committed projections, and the phase-selected families (X182, X184) stay out of the pool exactly as
they do in X179 and X183.

## 2. Positive control fires

The control fires if (a) the pooled local-inflow model reproduces the four ladder shares within their Wilson intervals, (b) the
radius-6 arms' local-inflow distributions are reported as means with spreads so the cliff audit is on numbers rather than on a
claim, and (c) at least 8 of the 57 cells have both outcomes and ≥5 runs, which is what a per-cell slope needs to mean anything.
Thresholds: ladder shares reproduced within their intervals, at least 8 usable cells. If fewer than 8 cells qualify, the per-cell
part of the item is reported as underpowered and only the pooled models are read.

## 3. Readout exists and varies

Primary: the share per cell, and per cell the slope of the outcome on log local inflow. Secondary: the pooled deviance of
`outcome ~ log F + gap + radius` fitted twice, once with the nominal `F` and once with the local inflow at the seeded sites —
the same contrast X183 used on the ladder, now asked of the whole table.

## 4. Sensitivity arithmetic, and the prediction

The pool is expected to be the 742 two-body runs of X179 plus X181's 30, minus the 60 phase-selected ones, i.e. about 712 runs in
57 cells; the cells with ≥5 runs and both outcomes are expected to number 12-20, which is enough for group-level slopes but not
for per-cell significance. Registered **before the run**, from the local-inflow law:

- the pooled model using the local inflow at the seeded sites has a **lower deviance** than the same model on the nominal rate,
  and the registered bar is a drop of at least 20 deviance units on the pooled non-saturated runs;
- per-cell slopes are **negative in the nominal rate's own ordering only where a cell mixes rates**, so the per-cell part is a
  description rather than a prediction, and the item commits only to reporting them;
- the radius-6 cliff: the two arms' mean local inflow is expected to differ by less than 0.004 in `F_local` (both were run at
  `F` = 0.030 with random sites), and if it does, the cliff is **not** a site draw and X178's reading stands.

## 5. Refusal rule

If the local-inflow model does not beat the nominal one by the registered 20 deviance units on the pooled table, the item is
recorded as **X183's collapse is local to the ladder** and the table keeps the nominal form of its shares. If the radius-6 arms'
mean local inflows differ by more than 0.004 in `F_local`, the item is recorded as **the cliff is partly a site draw** and the
cliff's share must be quoted with the arms' site distributions, not as a property of the gap alone. If the directions differ
between cells with no pattern, the item is recorded as **the table's cells are not exchangeable beyond the local-inflow law** and
nothing else is claimed.

## 6. What would kill it

The nominal rate enters the table mainly through cells that differ in rate by design, so a pooled deviance win can be a restating
of X183 rather than new evidence about the table; the item therefore reports the per-cell slopes as well, and counts a pooled win
as supporting evidence only if the per-cell slopes are negative in the local variable in a majority of the cells where the local
variable has spread. And the cliff audit is a comparison of means over 10 and 25 runs, so a difference below 0.004 is inside its
own noise and is stated as such rather than as a null result.

## 7. Implementation notes

`scripts/x186_table_local.py` recomputes, for every two-body run in the committed projections, the nominal rate, the local inflow
at the colder body and at the body mean, the measured gap and radius, and the outcome; groups by cell; fits the two pooled
logistic models by grid search; and reports the radius-6 arms. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x186_table_local.json`. Cost under a minute of CPU.
