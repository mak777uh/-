# X203 — larger-n clean clones on verified non-zero-baseline strata (05.11, pre-registration)

**Status:** pre-registration before any X203 run. CPU, `field_track.py` / X198 COMMON, F=0.030, 400 steps. No physics changes.

## Question

X202 showed (a) historical disagreeing pairs are fragile to reproduce (C1 fail) and (b) outcomes can disagree even when phase AND edge distance are held fixed (residual variance beyond edge). X203 estimates the **within-world disagreement rate at fixed (geometry, phase, edge)** on strata with a **verified non-zero baseline**, so the estimate is sensitive (not saturated at 0/1).

## 1. Manipulation is connected

For each stratum (cell, phase, edge bin/value) we hold geometry, parameters and phase fixed and vary only the seed, selecting seeds whose realized edge distance equals the target (±0). The comparison is within-(phase,edge) groups: any outcome spread is not explained by phase or by the edge metric. Uses deterministic census/jitter (X198).

## 2. Positive control fires

Positive control = **non-zero baseline** per stratum: before the main read, a stratum is included only if an initial screen (or historical/X202 evidence at the same position class) shows at least **1 fused and 1 unfused** outcome across >=4 pilot runs, i.e. baseline share in (0.1, 0.9). The control fires if >=3 strata meet the baseline criterion; otherwise the item reports "insensitive/no baseline strata found" (R2) rather than claiming zero variance.

## 3. Readout exists and varies

Readout: binary fusion (component count reaches 1 over 400 steps). Baseline-gated strata ensure variation (criterion 2). N per stratum = 8 seeds (target) at fixed (phase,edge).

## 4. Sensitivity arithmetic

Target: 4 strata × 8 seeds = **32 runs** (CPU). Per stratum, 8 Bernoulli trials: observing 0 disagreements is consistent with a true rate up to ~31% (rule-of-three upper bound ~3/8=0.375 naive; Wilson upper ~0.37 at 0/8) — so 0/8 does not prove zero variance, it bounds it; observing >=1 disagreement establishes nonzero variance. Report exact counts + Wilson intervals per stratum; do not claim "zero within-world variance" from 0/8.

## 5. Refusal rule

- **R1 (feasibility):** if a stratum yields <6 feasible fixed-(phase,edge) seeds, report actual n and mark under-powered.
- **R2 (baseline):** if <3 strata pass the non-zero-baseline screen, stop and report no sensitive strata (do not pool into a zero-variance claim).
- **R3 (phase/edge check):** exclude and report any run whose recomputed phase or edge != target.

## Criteria (registered)

- **C1 (baseline):** >=3 strata with baseline share in (0.1,0.9) over pilot/available runs.
- **C2 (residual variance):** in baseline strata, report per-stratum within-(phase,edge) disagreement/variance and pooled rate with Wilson interval. "Residual variance present" if >=1 stratum has >=1 disagreement among >=6 runs at fixed (phase,edge). (No claim of zero if 0.)
- **C3 (bound):** if all baseline strata show 0 disagreements, report the pooled upper bound (Wilson) and label "consistent with low but not proven zero within-world variance at this n".

## Artifacts

`scripts/x203_clean_clone.py --write` → `morphogenesis/experiments/E09_pond/l1_field_x203_clean_clone.json`; report `reports/2026-11-05-x203-clean-clone.md`; card §10jm.