# X162 — Is the local scale of the pattern inherited? (pre-registration, 04.11)

**Status:** pre-registered, not run. Analysis only: the logs of the X156 series already in git carry every component's
uid, area and centre at every logged step, so the neighbour spacing can be reconstructed without a single new world.

**Question.** X156 measured a trait of the *body* (its shape) and found it inherited at about half. X155 measured a trait
the tracking rule *writes* (the composition scalar `s`) and found 0.98. Both are properties of the individual. The local
scale — how far the nearest neighbour is, i.e. the spacing of the pattern — is a property of the *medium* around the body,
and it is the one quantity whose inheritance would be a statement about the environment rather than about the object. If a
daughter inherits her mother's neighbourhood spacing, then what is transmitted in this medium is a place, not a form.

## 1. Manipulation is connected

No manipulation: this is a measurement on existing logs. The connection that must be shown instead is that the readout is
**computed from the same components that the parent–daughter reconstruction uses**, so the pairing and the spacing come
from one source and cannot disagree:

- parent–daughter pairs are the pairs X156 already used (the mother read at her last logged step before the daughter's uid
  first appears, the daughter at her first logged step, one logging quantum apart at most);
- the spacing is computed at those same two steps from the same component list: `g = |c_parent − c_neighbour| − r_parent −
  r_neighbour` with `r = sqrt(area / pi)`, the minimum over all other components, i.e. a surface-to-surface distance, the
  same convention as the fusion work;
- the daughter's spacing is the minimum over her neighbours at her first step, which by construction excludes her mother
  (the mother's uid is gone by then).

## 2. Positive control fires

The control is the pair of quantities already measured on the same pairs, recomputed by this script: the area slope must
land at **0.45 ± 0.10** and the shape slope (`log elongation`) at **0.61 ± 0.12** in the lattice habitat, matching X156's
0.4514 [0.4264, 0.4771] and 0.6074 [0.5399, 0.6785]. The control fires if the recomputed area slope falls inside that band;
if it does not, the reconstruction in this script differs from X156's and the spacing number is not reportable.

## 3. Readout exists and varies

The readout is the surface gap to the nearest neighbour, in cells. It must have a standard deviation of **at least 0.5
cells** across all pair measurements and a median between 1 and 20 cells: a world where every body is equally spaced, or
where neighbours are absent, carries no information and the item stops as "the readout does not exist".

## 4. Sensitivity arithmetic

The X156 pairs give 4 111 measurements over 20 runs. Spacing is noisier than shape (it depends on where the neighbour
happens to be), so the expected slope is estimated conservatively: with a per-pair scatter of about 2 cells and a between-
run spread of about 2 cells, the slope's standard error at 4 000 pairs is about 0.02 — an order of magnitude below any
slope worth reporting (0.3). Twenty runs also give a **between-run** estimate, which is the one that matters: the item is
decided on the run-level slope (one slope per run, 20 values), where the standard error is about 0.15 and a slope of 0.4 is
visible. Both are reported; the run-level one decides.

## 5. Refusal rule

If the run-level slope of the daughter's spacing on her mother's has a 95 % bootstrap interval that contains zero, **or** if
it lies inside the 95 % band of the shuffled-parent null, the item is recorded as **the local scale is not inherited** — the
medium's spacing is not transmitted across a division, and the third heredity channel of this line is closed with a number.
The slope is reported with the null band beside it either way. A slope that is positive but indistinguishable from the
shape ladder's 0.45-0.61 is reported as "spacing is inherited no better and no worse than shape".

## 6. What would kill it

A positive control that misses its band (the reconstruction differs); a readout with too little spread; a slope that
collapses when the pairing is broken (the pairing, not the medium, made it); or a slope that is entirely explained by the
body's own size (spacing correlates with radius), which is why the partial slope controlling for the parent's radius is
reported next to the raw one.

## 7. Implementation notes

Script `scripts/x162_local_scale.py`, reading `morphogenesis/experiments/L1_field/x156_shape_f030_s8*.compact.json`
(1.6-2.0 MB each, in git). Output `morphogenesis/experiments/E09_pond/l1_field_x162_local_scale.json`. The nearest-neighbour
distances use periodic boundaries, as everywhere in this line. Nothing is committed from the per-run logs; only the
aggregate and the report.
