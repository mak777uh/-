# X168b — Removing the confound and locating the new crossings (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X168 found that a pair at a surface gap of 11 fuses in 5/5 runs at `F` = 0.026 and at `F` = 0.036, against 2/15 at
`F` = 0.030. Two things prevent that from being a result: the baseline came from a different seed set and a different run
length (X158: 6 000 steps, seeds 701-715, against 2 000 steps here), and both new arms fused at the only test gap, so their
crossings were never located. This item fixes both by running the matrix on one seed set, one run length and one script:

- **`F` = 0.030** at surface gaps 8, 10, 11 and 12 — the matched baseline, seeds 961-965, 2 000 steps;
- **`F` = 0.026 and 0.036** at surface gaps 12 and 14 — the brackets, same seeds, same length.

40 runs of 2 000 steps. Only the inflow rate and the seeded gap differ between arms.

## 2. Positive control fires

At gap 8 the pair must fuse in at least 4 of 5 runs **at every inflow rate tested** (0.026, 0.030, 0.036). The control fires
if each rate's gap-8 share is ≥ 0.8. If a rate fails, its arms are dropped from the comparison and the report says why, rather
than silently averaging over a broken world.

## 3. Readout exists and varies

The readout is the fusion share per (rate, gap) cell; it must vary across gaps within the `F` = 0.030 row (otherwise the row
cannot find a crossing) and the gap at the last two-body step must vary (standard deviation ≥ 0.2 cells overall).

## 4. Sensitivity arithmetic

At `F` = 0.030, gap 10 fuses 7/15 (0.47) and gap 11 fuses 2/15 (0.13), so the crossing sits between them and a five-seed
estimate is enough to place it in a two-cell window. At the new rates, gap 11 already fused 5/5, so the bracket at 12 decides
between "just past 11" (12 fuses partly, 14 not) and "far past 11" (12 fuses 5/5). Five seeds distinguish 5/5 from ≤ 2/5, i.e.
a share difference of 0.6 — the same resolution as X168, which is why the item adds gaps rather than seeds.

## 5. Refusal rule

If the matched `F` = 0.030 row places the crossing at 10-11 (i.e. 2/5 or fewer at gap 11 and 4/5 or more at gap 10), the X168
difference stands and is not a seed or length artefact, and the report states the crossings at the three rates. If the matched
baseline instead fuses at gap 11 in 3/5 or more, X168's contrast is an artefact of seeds or run length and the report says so
plainly and withdraws the non-monotone reading. If the gap-8 control fails at a rate, that rate's arms are not compared.

## 6. What would kill it

A matched baseline that reproduces 2/15-ish at gap 11 would confirm the dependence; a matched baseline that fuses at gap 11
would kill it. Brackets at 12 and 14 that fuse 5/5 at every rate would say the crossing depends on `F` far more strongly than
X168 could see, and that "about two cells" is a value at one rate by a wide margin — also a result, in the opposite direction
from a null.

## 7. Implementation notes

Runner `scripts/x168b_series.py` (matrix of rate × gap, seeds 961-965, 2 000 steps), analysis
`scripts/x168b_analyse.py` (fusion share per cell, crossing per rate as the highest gap with share ≥ 0.6, matched-baseline
comparison). Aggregate `morphogenesis/experiments/E09_pond/l1_field_x168b_inflow_matrix.json`. Cost about 25 minutes.
