# X182 — the midpoint phase, chosen in advance (04.11)

**Question.** X180 found an observational, negative relation between the pattern value at the pair's **midpoint** and the
outcome. This item stops observing and controls it: seeds are selected by the pattern value at the pair's midpoint, five levels,
six seeds each, radius 3, gap 10, `F` = 0.030, 2 000 steps. Preregistration `reports/2026-11-04-x182-local-inflow-plan.md`
predicted a negative trend and registered the extreme levels.

| target midpoint G | recomputed G | F_local, midpoint | coalesced | share | Wilson |
|---|---:|---:|---:|---:|---|
| 0.08 | 0.0863 | 0.0052 | 6 of 6 | 1.00 | [0.6097, 1.0] |
| 0.28 | 0.2667 | 0.0160 | 6 of 6 | 1.00 | [0.6097, 1.0] |
| 0.50 | 0.5 | 0.0300 | 3 of 6 | 0.50 | [0.1876, 0.8124] |
| 0.70 | 0.7277 | 0.0437 | 1 of 6 | 0.17 | [0.0301, 0.5635] |
| 0.90 | 0.8943 | 0.0537 | 0 of 6 | 0.00 | [0.0, 0.3903] |

**Result.** The share falls as predicted: Cochran-Armitage z = -4.446, one-sided p for the negative direction
0.00e+00. The pre-registered prediction holds, so the midpoint phase is a real control and its
sign is negative: **a cold gap is what lets the pair become one component**.

**Controls.** Every level's recomputed value landed inside its band (recomputed for all 30 runs); the extremes are
0.81 apart in G, above the registered 0.5.

**Limits.** Six runs per level: the individual shares are coarse (their Wilson intervals span ≈0.4) and only the trend carries
weight. The design says nothing about the bodies' own sites — X183 and X184 do.

**Next hypotheses.** This negative midpoint effect and X184's positive colder-body effect have to be reconciled; X185 does it.
Artifact: `morphogenesis/experiments/E09_pond/l1_field_x182_local_inflow.json`.
