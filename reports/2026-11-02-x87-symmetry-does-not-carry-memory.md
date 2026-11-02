# X87 — symmetry does not carry the size memory (and the memory declines with inflow, not in a U)

**Date:** 2026-11-02, 07:45 MSK. **Experiment:** X87 (X85's cells brought to twenty worlds each, split convention on).
**Preregistration:** `reports/2026-11-02-x87-memory-symmetry-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x87_f0{25,30,35}_pattern_s221-232.json` (36 runs), fields `_x87_fields/`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x87_memory_vs_symmetry.json`.

## Registered verdict

**Symmetry does not carry the size memory.** The rule fired on its "flat" clause: all three within-cell coefficients lie inside
±0.3.

## Numbers

Twenty worlds per inflow (X85's eight, seeds 191–198, plus X87's twelve, seeds 221–232), flags verified identical across the two series
(parity check passes on all physical parameters), 4 115–4 901 lag-1 ancestor-descendant pairs per cell.

| `F` | `rho1` | pairs | within-cell ρ(`rho1`, `s`) | `s` median (IQR) | half-life, per-world median | fittable |
|---|---|---|---|---|---|---|
| 0.025 | 0.391 | 4 901 | **−0.05** | 0.385 (0.359–0.455) | 1.82 | 20/20 |
| 0.030 | 0.549 | 4 791 | **−0.26** | 0.679 (0.611–0.730) | 1.16 | 18/20 |
| 0.035 | 0.470 | 4 115 | **−0.21** | 0.837 (0.804–0.878) | 1.07 | 19/20 |

- The **positive control fired**: the 0.030 cell's pooled `rho1` is 0.549 against the band [0.45, 0.56] (X74's 0.507, same convention),
  and the 0.035 cell's symmetry is 0.837 against [0.78, 0.90] (X85's 0.870, X86's 0.848). The pooled worlds are the worlds the memory
  numbers come from.
- Pooled over all sixty: raw ρ(`rho1`, `s`) = **+0.16**, partial correlation controlling inflow = **−0.10**. The raw positive value is
  inflow confounding (`s` tracks `F` at 0.90); once inflow is held, nothing remains.
- The three coefficients are negative — the direction the earlier underpowered series hinted at — but at 20 worlds a coefficient of
  0.26 is ≈1.2σ. **The honest bound: a negative association stronger than ≈0.3 is excluded; nothing smaller is.**

So the answer to the question the two-scale programme started with: the one coordinate the environment can actually turn — how much of
the pattern locks to the imposed orientation — **does not carry the size memory**. Memory is a property of the medium's own state, not
of the symmetry it is displaying.

## The secondary readout, which contradicts a claim we wrote yesterday

Per-world median half-life: **1.82 / 1.16 / 1.07** divisions at `F` = 0.025 / 0.030 / 0.035. That is **monotone decreasing in inflow**,
whereas §10fa and claim 295 describe a **U**: long outside the band, short inside it, long again above it, measured as 1.47 / 0.73 /
1.61 with five worlds and pooled pairs.

Two things are different here: the worlds are split-convention (comparable with X74), but the 0.025 inflow — where the memory is
longest, 1.82 — was never measured in X74; and the 0.035 value has moved from 0.73 (pooled, five worlds) to 0.85 (X85's eight) to
**1.07** (twenty). With a fixed estimator across three inflows the shape is a decline, not a U.

What that means for the write-up: the "U" was an artefact of the estimator and the sample, in that order — the §10ff audit already
showed the pooled half-life is not aggregation-robust, and this series shows the same statistic moving by 45 % when the cell went from
five worlds to twenty. The claim's *direction* ("the band is the shallowest place") is not supported at the lower edge (0.025 is
shallower than the band at 0.035, but 0.035 is not the shallowest of the three either — it is 1.07 against 1.16 at 0.030). **Nothing in
this series supports a U.** The honest current statement is: within 0.025–0.035, memory declines as inflow rises, and the high-inflow
arm (0.040+, where the pattern percolates: β₁ 11–87) was never measured with twenty worlds and per-world half-lives.

## What to do next, and what not to

- **Not** more symmetry-versus-memory runs: the question is answered to the resolution that matters, and pushing to |ρ| = 0.2 would
  cost ~60 worlds per cell for a bound nobody needs.
- **Yes** to re-measuring the high-inflow arm (0.040, 0.045, 0.050) with twenty worlds and the same estimator, because that is where
  the U was claimed and where the morphology changes character (holes, percolation). ~60 runs, and it either restores the U or
  replaces it with a decline.

доска: принято 0, отклонено 0, отложено 0.
