# X197 — does X186's published deviance drop survive counting worlds? (04.11)

**Question.** X186's headline was that the **local inflow** beats the **nominal F** in a binomial deviance over the mixed cells of the
observational pool: 464.5 → 436.5, a drop of 28.0. X194 then showed the pool is nearly all singleton worlds and that its **own** AUC
barely moves when worlds replace runs. This item re-runs X186's own deviance with a row per **world** (cell × phase) instead of per
run, with a phase-clustered bootstrap beside the run bootstrap. Preregistration
`reports/2026-11-04-x197-deviance-worlds-plan.md`.

**Result: the number does not survive counting worlds, and the effect lands inside its own bar.**

| quantity | over runs | over worlds |
|---|---:|---:|
| mixed rows | 311 | 258 |
| nominal-`F` deviance | 424.0 | 352.9 |
| local-inflow deviance | 403.3 | 338.6 |
| **drop** | **20.7** | **14.3** |
| share of resamples with drop > 20 | 0.517 | 0.208 |
| median resampled drop | 20.75 | 13.149999999999999 |

The pool holds 742 runs, 311 of them in 11 mixed cells, and those collapse to
**258 worlds** — 1.205 runs per world, so about a fifth of the mixed rows are repeats. The drop falls from
20.7 to 14.3 (30.9 per cent), and the phase-clustered bootstrap puts it
above X186's own bar of 20 in only **0.208** of resamples against **0.517** for runs, with a median
resampled drop of 13.149999999999999. With worlds as the unit the typical outcome of X186's own test is *below* the bar it used to
call the local inflow the better predictor.

Registered predictions: one of three passed. The collapse ratio did pass (1.205 runs per world, above the registered
1.11), the 20-per-cent stability bar failed outright (the drop moves 30.9 per cent), and the
interval claim failed in the direction that matters — the world bootstrap puts the drop above 20 far less often, not as often.

**Two honest qualifications.** First, this pool is not X186's own run: excluding the later selected arms and the arms selected by the
inflow gives 424.0 → 403.3 against the published 464.5 → 436.5, so the published absolute deviances are not
reproduced here by construction; the like-for-like comparison is this item's own pair, runs against worlds. Second, X194's finding that
the published intervals stand is **not contradicted**: X194 measured an AUC of the inflow–fusion association, which did not move
(0.652 → 0.660), while X186's deviance drop moves by a third. The lesson is that the world unit has to be checked **per statistic**,
not per paper.

**What this changes.** X186's conclusion — that the local inflow predicts the outcome better than the nominal `F` — must be stated with
the world as the unit of observation, where the evidence is a drop of 14.3 against a bar of 20, i.e. **inside the bar**.
The per-cell slope signs are unaffected (2 of 11 cells negative by runs, 2 by worlds). The
conclusion is not withdrawn — the local-inflow law itself rests on the construction of X184 (0.00 → 1.00 by design) and on X185's two
windows, not on this deviance — but this particular test's strength is reduced, and the manuscript now says so.

**Next hypotheses.** (1) Re-run X197 with **two seeds per world** to price the world unit directly rather than inferring it from
repeats. (2) The same runs-vs-worlds pair for X183's AUC and X186's per-cell slopes, so every published statistic of the line carries
its own unit check. (3) A deviance that treats the world as a random effect (mixed model over cells), which is the statistically
correct way to keep the repeated structure instead of averaging it away. Artifact:
`morphogenesis/experiments/E09_pond/l1_field_x197_deviance_worlds.json`.
