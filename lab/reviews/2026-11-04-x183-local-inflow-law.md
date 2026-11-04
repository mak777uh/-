# Проверка: the seeded pair's fusion is governed by the local inflow at its site rather than by the nominal rate F (X180/X183), and the X181 gap-10 cell share reproduces

- **Раздел/строка CLAIMS:** no `CLAIMS.md` row yet. The claim lives in `morphogenesis/experiments/E09_pond/l1_field_x183_local_collapse.json` (`verdict`), `.../l1_field_x180_dispersion.json` (`verdict`), `reports/2026-11-04-x180-dispersion.md` §"What this does to the block's statements", and `reports/2026-11-04-x184-cold-body-plan.md` §1. The secondary claim is `.../l1_field_x181_worst_cell.json` (`verdict`) with `reports/2026-11-04-x181-worst-cell-plan.md`.
- **Вердикт:** держится с оговоркой
- **Что пересчитано:** all 1 005 `morphogenesis/experiments/L1_field/*.compact.json` read by an independent reader (`lab/reviews/_scratch_x183_check.py`, run from the repo root with `python lab/reviews/_scratch_x183_check.py`; nothing imported from `scripts/x18*.py`). Per artifact: first sample `series[0]==[step, comps]`, component tuple via `[uid,area,cx,cy]` or dict, toroidal 96×96 distance, `r0=sqrt(area/π)`, `G=(sin(2πy/12)cos(2πx/12)+1)/2` with `int(round(·))%96`, `fused = min(len(comps))==1`. A pair is in the ladder iff `round(dist−2r0)==10` and `2.7≤r0≤3.1`. Candidates re-derived as `F*(1+0.5*(2G−1))` for G at the midpoint, the body mean, the body min and the body max. AUC by direct pairwise counting (ties at ½), Wilson by the exact formula, deviance both by a from-scratch replica of the stated 81-point grid and by an unconstrained two-parameter logistic MLE. X181 read from the 30 raw `L1_field/x181_s1211..1240.json` and its six pre-existing families re-derived from the compacts, not from the X179 table. The X184 series, which completed at 19:20 while this review was being written, was evaluated separately by `lab/reviews/_scratch_x184_check.py` from the 30 raw `L1_field/x184_F0??_s????.json` (provisional: see below).
- **Расхождение:** every AUC, share, Wilson interval and the 109-run count reproduce exactly (table below). Three framing numbers do not mean what the text implies. (1) "measured r0 2.7-3.1": inside the ladder `r0` is a **single value 3.03825** (first-sample area 29, i.e. the seeded radius 3); the 2.7-3.1 band selects exactly that value. (2) "measured gap 10": `dist−2r0 = 9.92349` in all 109 runs (`dx=16`, `dy=0`), so 10 is `round(9.923)`, a design constant of `SEP=16, r=3`, not a measurement. (3) `G_min` deviance is 96.9 under the stated grid method (reproduced) but 96.2 under an unconstrained 2-parameter logistic — 0.7 apart, same ordering, not a substantive discrepancy.
- **Проверки на устойчивость:** see the five attacks. Headline: the *local-inflow family* (body mean or body min) is overwhelmingly better than the nominal rate (permutation p = 0.0005 for the best of the four local readings; LRT against the intercept-only null 52.1 for `G_min` vs 4.4 for nominal). The *specific* "colder body" choice is **not** separated from the body mean by the ladder (`AUC(G_min)−AUC(G_mean) = +0.0275`, paired-bootstrap 95 % CI `[−0.048, +0.106]`; the mean variant wins in 4 of the 6 families where the AUC is computable; dropping F = 0.036 reverses the winner) — but the X184 series, which manipulates the colder body's inflow prospectively, now confirms the direction (Cochran–Armitage one-sided p ≈ 1.8·10⁻⁶, AUC 0.982). The `min(components)==1` readout is a transient coalescence, not a terminal single body.
- **Что убьёт утверждение:** a completed X184 whose shares are flat or fall with the colder body's local inflow would kill the local-inflow reading and restore the nominal form — this did not happen (see the X184 appendix). What would still kill the *printed* forms: (i) if the official X184 aggregate, once written, disagrees with the raw runs read here; (ii) a second seed family in which the body mean clearly out-discriminates the colder body outside the F = 0.036 level; (iii) any evidence that `min(components)==1` is a threshold artefact of the component tracker rather than a real coalescence — that would void the outcome variable itself.
- **Что предложить ведущему:** keep the claim, but (1) commit an official X184 aggregate and cite it, since the raw runs are untracked and the numbers below cannot go into CLAIMS/manuscript until then; (2) quote the law as **the local inflow at the seeded site** with the colder body as the pre-registered reading that X184 confirmed, and state that the ladder alone cannot separate the colder body from the body mean; (3) replace "measured r0 2.7-3.1 / measured gap 10" with the constants 3.03825 and 9.923 (`SEP=16`, radius 3); (4) say `min == 1` is a coalescence event, not a merged final state.

---

## What was recomputed, exactly

Reader: 1 005 compact files → 742 have a two-component first sample → 157 have `round(gap)==10` → **109** in `r0 ∈ [2.7, 3.1]`. The 157 gap-10 runs split by `r0` as `{3.038: 109, 4.442: 24, 5.997: 24}` (radius 3 / 4.4 / 6 arms); only the radius-3 block is in the ladder.

| quantity | claimed | recomputed |
|---|---|---|
| ladder runs | 109 | **109** |
| F = 0.026 share | 0.30 | 6/20 = **0.3000** |
| F = 0.030 share | 0.408 | 20/49 = **0.4082** |
| F = 0.033 share | 0.40 | 8/20 = **0.4000** |
| F = 0.036 share | 0.65 | 13/20 = **0.6500** |
| AUC nominal F | 0.6055 | **0.6055** |
| AUC `F_local_mid` | 0.2129 | **0.2129** |
| AUC `F_local_mean` | 0.8504 | **0.8504** |
| AUC `F_local_min` (colder body) | 0.8778 | **0.8778** |
| AUC `F_local_max` | 0.6615 | **0.6615** |
| mean within-level AUC, `G_min` | 0.8984 | **0.8984** (0.9643 / 0.8707 / 0.7917 / 0.9670) |
| deviance 1-parameter logistic, nominal | 144.6 | **144.6** (stated grid, re-implemented) |
| deviance 1-parameter logistic, `G_min` | 96.9 | **96.9** (stated grid); 96.2 (2-param MLE) |
| X181 fused | 12/30 = 0.40 | **12/30 = 0.4000** |
| X181 Wilson | [0.2459, 0.5768] | **[0.2459, 0.5768]** |
| X181 pooled | 0.4051 over 79 | 20/49 + 12/30 = 32/79 = **0.4051** |
| pooled_before families | 4/5, 3/9, 2/5, 2/5, 7/15, 2/10 | **4/5, 3/9, 2/5, 2/5, 7/15, 2/10** |

Reference scale for the deviances: the intercept-only null is **149.0**; the nominal fit spends 4.4 of it (χ²₁, p = 0.035 — marginal), `G_mean` 46.6 (p = 8.6·10⁻¹²), `G_min` 52.1 (p = 5.2·10⁻¹³). So the nominal rate is barely distinguishable from "no information" on this ladder, and the local reading is not.

## The five attacks

**(a) Is "the colder body" circular or post hoc?** It is post-hoc *selection*, not circular arithmetic — `G_min` is computed from the seeded positions before the outcome, so there is no leakage. The ladder cannot separate the selected candidate from its neighbours:
- `AUC(G_min) − AUC(G_mean) = +0.0275`, paired bootstrap 95 % CI **`[−0.048, +0.106]`** (4 000 resamples). For mean-within the difference is `+0.0305`, CI `[−0.067, +0.138]`. Neither excludes 0.
- Half/half selection (4 000 random splits): `min` is the better candidate on half A 2 989 times and `mean` 1 011 times; the **held-out** AUC on B averages **0.8587** against **0.8507** for always using the mean. Out-of-sample gain from choosing "the colder body": ≈ 0.008.
- Leave-one-family-out (11 folds): `min` stays above `mean` in every fold (min−mean from +0.006 to +0.048) — the pooled ordering is stable, but the margin is small.
- **Within-family AUC**: the mean beats the min in **4 of the 6** families where it is computable — x158_g10_r30 1.000 vs 0.833, x170_F30 0.893 vs 0.804, x172_gap10 0.833 vs 0.792, x173_g10 1.000 vs 0.875; min beats mean only in x170_F26 (0.955 vs 0.909) and x170_F36 (0.940 vs 0.820). Both variants stay > 0.79 in every family, so *some* local reading works inside families; which one is not resolvable from the ladder.
- Permutation null for "best of the four local readings" (labels shuffled within the nominal level, 2 000 draws): observed 0.8778, null median 0.6035, null 95 % 0.6658, **p = 0.0005**. The local-inflow *family* is real even after the multiple comparison; the single winner inside it is not.
- **Out of sample (X184, below):** a series that selects seeds by the colder body's inflow did confirm the direction prospectively (p ≈ 1.8·10⁻⁶), so the post-hoc concern about the colder body is substantially answered — but the design selects on `min` by construction, and the body-mean reading is also strong on the same runs (AUC 0.94), so it does not cleanly separate the two.

**(b) Confounded with initial area or the measured gap?** No — and for a trivial reason. Inside the ladder `r0 = 3.03825` and `dist−2r0 = 9.92349` are **exactly constant** (`area0 = area1 = 29`, `dx = 16`, `dy = 0`) in all 109 runs and in every family; the correlations with `G_min` are undefined (zero variance), and `AUC(r0→fused) = AUC(gap→fused) = 0.5`. There is nothing to confound. The cost is the framing point above: the "measured r0 / measured gap" language describes a design constant.
Two geometric facts fall out. `G_min` is the left body in 55/109 runs and the right body in 54/109 (no side bias), and it is component 0 in 55/109. `G_min` correlates `+0.66` with `G_mean`, `−0.66` with `G_mid` and only `−0.08` with `G_max`; `G_min == G_mean` in 23/109 runs. Because `SEP = 16` is 120° of the 12-cell pattern, the two bodies sit at near-anti-correlated phases, which is exactly why min and mean are hard to separate and why `G_max` carries so much less.

**(c) Does the AUC survive dropping F = 0.036?** The local reading survives; the *choice of `G_min`* does not.
- Nominal: AUC 0.6055 → **0.5369**; the three remaining shares (0.300 / 0.408 / 0.400) are nearly flat, so the level with share 0.65 was carrying almost all of the nominal discrimination. Good for the claim.
- `G_min`: 0.8778 → **0.8449**, mean-within 0.8984 → **0.8755**.
- `G_mean`: 0.8504 → **0.8572**, mean-within 0.8679 → **0.8788**.
- On the 89 runs that remain, **`F_local_mean` is the best local reading, not `F_local_min`**, in both metrics and in deviance (80.9 vs 85.7). The "colder body" result is carried by the F = 0.036 level (where `G_min` gives AUC 0.967 against `G_mean`'s 0.835).
Horizon control (only `steps == 2000`: 80 runs, 36 fused): nominal 0.6263, `G_mean` 0.8226, `G_min` 0.8857, `G_mid` 0.2614 — the same ordering as the full ladder, so the mixed horizons in the F = 0.030 bucket are not what produces the effect.

**(d) Is the fusion readout sound?** No run reaches one component at its first sample: **0/109** (the ladder filter requires `series[0]` to have exactly two components, so this is structural). But the readout means less than the word "fusion" suggests:
- Of the 47 runs flagged fused, **0 end on one component**, and **47/47 return to ≥ 2 components** afterwards. The single-component stretch is transient: median 4 samples with `count == 1` out of a median 201 samples per run (max 31); the first one appears at sample index 7–11 (≈ step 70–110).
- The 12 "fused" X181 runs behave the same (`12/12` rebound), and the 15 "fused" X184 runs too (`15/15`).
- The 62 unfused ladder runs never drop below 2, so the readout is a clean binary event. It is a *pairwise contact/coalescence* readout, which is what the ladder needs — but it is not "the pair ends as one body", and it must not be quoted as such.

**(e) Recount of the ladder set.** My reader finds exactly **109** runs under the stated filter. For transparency: 1 005 compacts scanned, 742 pass the "two components at the first sample" gate, 157 have `round(gap) == 10`, 109 of those have `r0 ∈ [2.7, 3.1]`. The F = 0.030 bucket is six families (x136 5, x158_g10_r30 9, x168c_F30_g10 5, x168c_F30_len 5, x170_F30 15, x173_g10 10) and mixes horizons 2 000 / 3 000 / 6 000; the other three buckets are single- or two-family and all 2 000-step.

**(X181, secondary).** From the 30 raw JSONs: 12/30 fused, Wilson [0.2459, 0.5768], inside the registered 0.23-0.59. The six pre-existing families recompute to 20/49 = 0.4082 from the raw compacts, so the pooled 32/79 = 0.4051 is a genuine pool and not a copied table entry.

## Appendix: the X184 out-of-sample test (provisional)

The X184 series (`scripts/x184_cold_body.py`) finished at 19:20:34 MSK while this review was being written: 30 raw runs, 5 levels × 6 seeds, radius 3, gap 10, F = 0.030, 2 000 steps, seeds chosen by `min(G)` of the pair **before** the run. **Status warning:** these files are untracked and `morphogenesis/experiments/E09_pond/l1_field_x184_cold_body.json` does not exist, so by the artifact contract these numbers are provisional and cannot be cited until the lead commits the official aggregate. I ran nothing; I only read the runs that had just been written.

Recomputed with my own reader (`_scratch_x184_check.py`), ordering the levels by the recomputed `F_local` at the colder body:

| registered level | n | fused | share | Wilson | mean F_local [range] |
|---|---|---|---|---|---|
| 0.0155 | 6 | 0 | **0.000** | [0.0000, 0.3903] | 0.01600 [0.01500, 0.01701] |
| 0.020 | 6 | 0 | **0.000** | [0.0000, 0.3903] | 0.01875 |
| 0.025 | 6 | 3 | **0.500** | [0.1876, 0.8124] | 0.02396 [0.02350, 0.02625] |
| 0.030 | 6 | 6 | **1.000** | [0.6097, 1.0000] | 0.03000 |
| 0.036 | 6 | 6 | **1.000** | [0.6097, 1.0000] | 0.03700 [0.03650, 0.03750] |

- **Registered directional criterion is met decisively:** Cochran–Armitage one-sided positive trend z = **+4.6386**, **p = 1.75·10⁻⁶** (run-level z = +4.5547, p = 2.62·10⁻⁶); `AUC(F_local_cold → fusion) = 0.9822`.
- **Positive controls pass:** max |recomputed `F_local` − registered label| = **0.00151** (tolerance 0.002); extreme-level separation **0.0225** ≥ registered 0.018.
- **The registered point intervals for the extremes are missed, in the strong direction:** coldest predicted 0.05-0.40, observed 0.000; warmest predicted 0.45-0.95, observed 1.000. These are not statistical contradictions — the observed Wilson intervals [0, 0.390] and [0.610, 1] still overlap the registered bands — but the effect is stronger than the plan predicted, not weaker.
- **The midpoint is confirmed as the wrong site:** on the same 30 runs `g_mid` gives AUC **0.0622** (anti-predictive), the body mean 0.9400, the warmer body 0.6489, the colder body 0.9822. Per-level means of `g_mid` fall monotonically (0.769 → 0.688 → 0.443 → 0.320 → 0.034) while the fusion share rises, whereas `g_cold` rises 0.034 → 0.125 → 0.299 → 0.500 → 0.733.
- **It does not fully resolve min vs mean:** X184 selects on `min` by construction, and the body-mean reading also performs well on the same runs (AUC 0.94 vs 0.98). A design selecting on the body mean would be needed to separate them.
- **Readout caveat applies here too:** 15/30 fused, and all 15 rebound above one component — the same transient coalescence.

## What this does and does not support

Supported, reproduced to the last digit of the aggregates: on this ladder the nominal rate is nearly uninformative (AUC 0.6055, LRT p = 0.035) while the local inflow at the seeded site organises the block (AUC 0.85-0.88, LRT p ≈ 10⁻¹²). The X181 cell's fresh-family share is reproducible. The X184 series prospectively confirms the direction of the law and confirms the midpoint as the wrong site.

Not established by the ladder alone: that the **colder body** specifically, rather than the body mean, is the causal site — the bootstrap CI on ΔAUC includes 0, the mean wins in 4 of 6 families, and dropping F = 0.036 reverses the pooled winner. X184 supports the colder-body reading prospectively but selects on it, so it is confirmation of the direction, not a separating experiment. `reports/2026-11-04-x180-dispersion.md` already says as much ("X183's empirical choice, not a derivation"); the numbers here quantify it.

Also worth fixing before this goes into the manuscript: the readout is a coalescence (`min == 1` is transient in 47/47 ladder, 12/12 X181 and 15/15 X184 cases), and "measured r0 2.7-3.1 / measured gap 10" should read as the constants 3.03825 and 9.923 (`SEP = 16`, radius 3).

## What could not be checked

- The official X184 aggregate does not exist; the runs above are untracked and were still being written when the review started, so their status is provisional until `l1_field_x184_cold_body.json` is committed. I did not run the analysis script.
- The `min == 1` frames come from the projections' component lists; the raw `.npy` fields are gitignored, so whether the single-component frame is a true saddle-bridging merge or a threshold artefact of the component tracker at `threshold = 0.2` cannot be settled from the committed artifacts.
- The between-family correlation of a family's mean `G_min` with its share is `+0.77` over 11 families, but those families differ in F and horizon, so this is descriptive only and I do not treat it as evidence of a within-cell effect.
- This review has been added to `lab/reviews/index.json` (only writable scope used), so `scripts/check_reviews.py` passes.

---

## Addendum — recheck of the committed 139-run ladder and X185 (2026-11-04 19:50, commits `1bdf78bc`/`6cfabfaf`)

Follow-up requested by the lead after the 139-run regeneration. Verdict above is unchanged (`держится с оговоркой`); this addendum only re-runs the numbers and records one new discrepancy. Independent reader: `lab/reviews/_scratch_x183_recheck.py`, plus `lab/reviews/_scratch_x180_exclusion_check.py` for the last item.

**139-run ladder reproduces, and the exclusion is complete there.** 1 095 compact artifacts; 832 runs pass the two-component-first-sample gate; excluding `x182_*`/`x184_*` leaves 772; **60 runs excluded** exactly, matching `excluded_phase_selected_runs: 60`. The ladder filter (`round(gap)==10`, `2.7 ≤ r0 ≤ 3.1`) then gives **139** runs, and **no x182/x184 file is inside it** (all 60 phase-selected runs *would* enter without the guard, so the guard is doing real work: 199 → 139). The 30 new `x181_*` compacts are inside, taking F = 0.030 from 49 to 79 runs.

| quantity | committed | my reader |
|---|---|---|
| ladder runs / excluded | 139 / 60 | **139 / 60** |
| F = 0.030 level | 79 runs, share 0.405 | **79 runs, 32 fused, 0.4051** |
| nominal AUC / deviance | 0.5874 / 185.0 | **0.5874 / 185.0** (2-param MLE 185.0) |
| colder body AUC / mean-within / dev | 0.8656 / 0.8951 / 129.3 | **0.8656 / 0.8951 / 129.3** (MLE 128.6) |
| body mean AUC / mean-within / dev | 0.8396 / 0.8569 / 135.5 | **0.8396 / 0.8569 / 135.5** (MLE 134.8) |
| midpoint AUC | 0.2149 | **0.2149** |

Within-level AUCs also match to the digit (colder body 0.9643 / 0.8574 / 0.7917 / 0.9670; body mean 0.8929 / 0.8664 / 0.8333 / 0.8352). As before, an unconstrained two-parameter logistic moves the two deviances by ≤ 0.7 without changing the ordering.

**X185 pooled bands reproduce exactly.** From the 60 `x182_*`/`x184_*` compacts: `[0,0.019)` **0/22**; `[0.019,0.024)` **5/11 = 0.4545**; `[0.024,0.028)` **1/2 = 0.500** (the thin band the message did not quote); `[0.028,0.032)` **15/15 = 1.0**; `[0.032,0.040)` **10/10 = 1.0**. A run-by-run cross-check of my recomputed `g_cold`, `F_local_cold` and `fused` against all **60** entries of `l1_field_x185_one_law.json → runs_detail` gives **0 mismatches**.

**The X184 caveat in the body is now closed.** `l1_field_x184_cold_body.json` is committed and I read it directly: levels 0/6, 0/6, 3/6, 6/6, 6/6 with Wilson `[0,0.3903]`, `[0,0.3903]`, `[0.1876,0.8124]`, `[0.6097,1.0]`, and `G_cold_mean` 0.0335 / 0.125 / 0.2988 / 0.5 / (0.7333) and `F_local_mean` 0.016 / 0.01875 / 0.02396 / 0.030 / (0.037) — every one identical to what I read off the raw runs before the aggregate existed, and `trend.z = 4.638` matches my 4.6386. So the X184 section above stands as committed, not provisional.

**The 109-run caveats all survive on 139.**
- *min vs mean still unresolved:* `ΔAUC = +0.0260`, paired-bootstrap 95 % CI **`[−0.047, +0.103]`** (was +0.0275, [−0.048, +0.106]); the body mean wins inside 4 of the 7 families where the AUC is computable, with the new `x181` family favouring the colder body (0.8495 vs 0.8102); leave-one-family-out stays positive in all 11 folds (+0.012 to +0.039); permutation null for the best of the four local readings gives **p = 0.0005**. So the added family nudges the point estimate but does not identify the colder body.
- *coalescence, not terminal fusion:* **59 fused runs, 0 end on one component, 59/59 rebound** above one (same as 47/47 before).
- *r0 / gap are design constants:* `r0 = 3.03825` and `dist − 2r0 = 9.92349` on all 139, with `dx = 16`, `dy = 0`.
- Horizon control (`steps == 2000`, n = 110): nominal 0.6025, body mean 0.8167, colder body 0.8656 — the ordering holds.

**New discrepancy — the x180 exclusion is NOT in the code.** The message says `x179_crossing_table.py`, `x180_dispersion.py` and `x183_local_collapse.py` now all exclude the 60 phase-selected runs. `x179` does (its radius-3/gap-10/F-0.030 cell reads 79 runs = 49 + 30 x181, `per_source` lists x181 and no x182/x184) and `x183` does (above; `x186` too). **`x180_dispersion.py` does not** — there is no `startswith(("x182_", "x184_"))` guard anywhere in the file, and the committed `l1_field_x180_dispersion.json` has `runs_scanned: 832`, i.e. my full-corpus count, not the 772 of the exclusion. The 60 phase-selected runs land in the cell `(radius 3.0, gap 10, F 0.03, steps 2000)`: committed **110 runs / 52 fused / share 0.473**, of which 60 are phase-selected; dropping them makes that cell **50 runs / 21 fused / 0.42**. Why it matters here and not elsewhere: X182 selects seeds *by the midpoint pattern value*, which is exactly the covariate X180 tests, so keeping it in X180's cells is circular for that item. Replicating X180's whole pipeline reproduces the committed top line exactly with all runs (`17` cells, mean point-biserial **−0.561**, `fused_higher_g 1`, `informative_runs 381`, pooled point-biserial **−0.578**) and gives `17` cells, **−0.552**, **321** informative runs, **−0.527** pooled without the phase-selected runs. The direction of X180's conclusion is unchanged, but its committed numbers still pool runs it was meant to drop. Fix in scope for the owner: add the same guard to `x180_dispersion.py` and regenerate `l1_field_x180_dispersion.json`.
