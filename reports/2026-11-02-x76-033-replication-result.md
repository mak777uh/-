# X76: the 0.033 cell is ordinary after all — and the five cells now order by mixedness, not by inflow

**Date:** 2026-11-02, 02:55 MSK. **Experiment:** X76 (replication of the `0.033` cell with ten worlds).
**Preregistration:** `reports/2026-11-02-x76-033-replication-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x76_f033_pattern_s171-180.json`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x76_033.json`.

## Result

| statistic | X75 (5 worlds) | **X76 (10 worlds)** |
|---|---|---|
| lag-1 pairs | 917 | **2 059** |
| ρ₁ | 0.377 (below the band) | **0.447** (inside `[0.40, 0.60]`) |
| ρ₂ | 0.038 | 0.098 |
| ρ₃ | 0.053 | 0.040 |
| shuffle p95 | 0.045 | 0.034 |
| half-life | (0.71) | **0.57** |

Registered verdict: **ordinary cell** — with ten worlds the pooled ρ₁ sits inside the band, so X75's void was sampling, not a
property of the cell. Doubling the sample moved ρ₁ by 0.07 and halved its Fisher band, which is what a sampling accident should
look like.

The per-world table is the part worth reading: ρ₁ ranges **0.224–0.561** across the ten worlds and only 4 of 10 reach 0.45. The
pooled number is an average over quite different worlds — the same heterogeneity that made five worlds insufficient.

## The five cells, now ordered by mixedness

| cell | mixed (X71c, cut 0.2) | half-life |
|---|---|---|
| 0.030 | no | **1.47** |
| **0.033** | 3/5 | **0.57** |
| **0.035** | 5/5 | **0.73** |
| **0.037** | 4/5 | **0.56** |
| 0.040 | no | **1.61** |

The pattern is no longer a U with a suspicious minimum: it is **two levels**. Cells outside the band remember for 1.5–1.6
divisions; cells inside or at the edge of the band remember for 0.56–0.73. The factor between the levels is about **2.5**, and it
is the same at three different inflows inside the band — which is what "the rate depends on whether the medium has one preferred
scale or two" predicts, and what X74 could not show with one measurement inside the band.

This is the confirmation the previous three experiments were circling: X74 established that the rate varies with the inflow but
left three monotone covariates unable to explain a U; X75 produced one shallow edge and one void; X76 fills the void and the U
collapses into a step.

## What this changes

- The statement becomes two-valued and testable: **inside the multistable band the memory half-life is ≈ 0.6–0.7 divisions,
  outside it ≈ 1.5–1.6**, with the transition located to ±0.002 (the X71c resolution).
- It ties the line's two halves together: the parameter region where the medium can hold two forms (§10eq–§10ev) is exactly the
  region where it forgets fastest (§10ex–§10fa). Form diversity and memory depth trade off in this world.
- The mechanism question narrows further: it is not split rate, not size dispersion (both monotone in `F`, X74), and not the
  number of worlds. It is the presence of two scales.

## What this does not say

- It does not identify the mechanism — "two scales" is the surviving description, not a demonstrated cause. A world with two
  competing scales would need an independent handle (e.g. an imposed second scale via the hetero pattern) to test causally.
- The transition width is the sweep's: between 0.030 and 0.033 the half-life jumps from 1.47 to 0.57, and nothing was measured
  between them.
- Five cells, one box, one `k`. The per-world spread (0.22–0.56 at 0.033) is large enough that each cell's pooled value carries a
  real uncertainty that the Fisher band does not express.
