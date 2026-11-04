# X183 — which local reading organises the rate ladder (04.11)

**Question.** X180 showed the seeded site's phase matters and that the naive phase (the midpoint) gives the wrong sign. That is
not a mechanism. This item asks the question that settles the choice of phase from the block's own data: which reading of "the
rate a run had" organises the rate ladder that X170 measured? No new series; the ladder is 139 runs at radius 3
(constructed: r = 3.03825, surface gap 9.923), `F` in {0.026, 0.030, 0.033, 0.036}.

| nominal rate | runs | share |
|---|---:|---:|
| 0.026 | 20 | 0.30 |
| 0.03 | 79 | 0.41 |
| 0.033 | 20 | 0.40 |
| 0.036 | 20 | 0.65 |

| candidate reading | AUC over the ladder | mean AUC inside a level | deviance |
|---|---:|---:|---:|
| `F_nominal` | 0.5874 | 0.5 | 185.0 |
| `F_local_mid` | 0.2149 | 0.1549 | 160.7 |
| `F_local_mean` | 0.8396 | 0.8569 | 135.5 |
| `F_local_min` | 0.8656 | 0.8951 | 129.3 |
| `F_local_max` | 0.6359 | 0.5739 | 181.0 |

**Result.** The nominal rate discriminates across levels (AUC 0.5874) and, being constant inside a
level, not at all within one — by construction 0.5. The local inflow at the pair's two seeded sites does discriminate within
levels: colder body 0.8656 (mean within 0.8951),
body mean 0.8396 (within 0.8569), midpoint
0.2149 — anti-predictive. A one-parameter logistic fit costs
185.0 for the nominal rate against 129.3 for the colder body.
**The nominal rate is a site average, and the local inflow at the seeded sites is the run-level rate.**

**Limits, stated plainly.** The ladder cannot separate the colder body from the body mean: their AUCs differ by
0.026, the independent review's paired
bootstrap interval for that difference crosses zero, and dropping the `F` = 0.036 level flips which of the two wins. The supported
claim is therefore the local inflow *at the seeded sites*, with the colder body as the reading this item chose and X184 tested.
Runs whose seeds were chosen by phase or by the local inflow itself (X182, X184, X187, 84 runs) are excluded from this pool. And the outcome is a transient
coalescence: every run flagged as coalesced rebounds above one component, none ends on one.

**Independent review.** `lab/reviews/2026-11-04-x183-local-inflow-law.md` — verdict **держится с оговоркой**; it reproduced the
109-run version of every number with its own reader, found that r0 = 3.03825 and the surface gap 9.923 are design constants rather
than measurements, and established the two limits above (min-versus-mean, and coalescence rather than terminal fusion).

**Next hypotheses.** Control the colder body's inflow prospectively (X184), and re-read the radius-6 cliff in the local inflow.
Artifact: `morphogenesis/experiments/E09_pond/l1_field_x183_local_collapse.json`.
