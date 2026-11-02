# X85 — symmetry against memory: void by its own control, and the control's failure is the finding

**Date:** 2026-11-02, 10:35 MSK. **Experiment:** X85 (symmetry `s` against the size memory, three inflows x eight worlds).
**Preregistration:** `reports/2026-11-02-x85-symmetry-memory-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x85_f0{25,30,35}_pattern_s191-198.json` (24 runs), fields `_x85_fields/`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x85_symmetry_memory.json`.

## Registered verdict

**Void.** The positive control required the `F = 0.035` cell's median symmetry to land in **[0.64, 0.81]** (X71's 0.777 with five
worlds); the eight new worlds give **0.870** (range 0.778–0.901). The plan said "if either misses, the series is void", so it is a
void, and no claim is made in either direction.

## Why the control missed, and why that matters more than the test

The `F = 0.035` cell of X71 was run at `--sample-every 1000`; X85 runs at 50. That is not a logging choice: at every sampled step the
runner draws trait mutations (`rng.normal(args.s_ref, args.mutation)` for new components and `rng.normal(0, args.mutation)` for
daughters), the trait feeds back into the field, and so **the logging frequency is a physical parameter**. X71's worlds saw six
mutation events over 6000 steps, X85's saw a hundred and twenty.

Verified directly on 02.11: seed 191 at `F = 0.035`, identical flags except `--sample-every`, produces fields that differ by up to
**0.365** in v (not bit-identical). So the two series are not the same cell measured twice; they are two regimes.

That reframes the control failure. Within the 50-step regime the same inflow reads:

| series (regime) | worlds | `F = 0.030` s | `F = 0.035` s |
|---|---|---|---|
| X71 (1000-step) | 5 | 0.516 | 0.777 |
| X82 control cell (50-step) | 5 | 0.603 | — |
| X85 (50-step) | 8 | 0.671 (0.503–0.808) | **0.870** (0.778–0.901) |

- **The direction replicates across regimes**: every series rises with inflow, and within the 50-step regime X85 gives
  0.40 → 0.67 → 0.87 for 0.025 → 0.030 → 0.035.
- **The level does not**: at 0.030 the 50-step series give 0.603 and 0.671 (≈0.07 apart, seed scatter), while the 1000-step series
  gives 0.516; at 0.035 the two regimes give 0.777 and 0.870.
- The registered band [0.64, 0.81] was taken from a **different regime**, which is the design error this series caught. A control
  must be measured in the regime the experiment uses.

So the durable result of X85 is a **method** result: `--sample-every` is a physical parameter (when `--mutation > 0`), series at
different logging density are not comparable at the same seed, and every cross-series number in this line has to be checked for it.
In this line only X71/X71b/X71c used 1000; X73–X85 used 50.

## What the run measured, descriptively

| cell | `s` median (range) | `rho1` | half-life, per-world median | fittable | within-cell ρ(`rho1`, `s`) |
|---|---|---|---|---|---|
| 0.025 | 0.399 (0.357–0.474) | 0.376 | 1.85 | 8/8 | **−0.33** |
| 0.030 | 0.671 (0.503–0.808) | 0.543 | 1.15 | 7/8 | **−0.25** |
| 0.035 | 0.870 (0.778–0.901) | 0.463 | 0.85 | 8/8 | −0.02 |

- The **direction** of the registered prediction (memory shorter where the pattern is locked to the forcing) appears in two of three
  cells, but at −0.33 and −0.25 against a registered bar of −0.5, and in the third cell it is zero.
- The pooled rank correlation of `rho1` with `s` is **+0.26**, and the partial correlation controlling inflow is **0.00**: once the
  inflow is held, symmetry carries nothing here. The raw positive correlation is inflow confounding (`s` tracks `F` at 0.94).
- The half-life measured per world is **1.85 / 1.15 / 0.85** divisions — the same shape as X74's pooled 1.47 / 0.73 / 1.61? No:
  X74's `F = 0.025` was not measured, and the 0.035 value here (0.85) is in the same place as before (0.73–0.92), while the 0.030
  value (1.15) is lower than X74's 1.47. With eight worlds and per-world medians, the "two levels" contrast of §10fa is weaker than
  the pooled numbers said, which is consistent with the §10ff audit.
- `rho1` at 0.025 (0.376) is the lowest of the three, so the memory does not decline monotonically with inflow either.

## What this means for the question the series was built on

The hypothesis "symmetry carries the size memory" is **not supported** at this power: two coefficients in the predicted direction but
below the bar, one at zero, and a pooled partial correlation of 0.00. The hypothesis is also **not refuted** — the control failure
voids the series, so the honest state is "not tested with a valid instrument", and the instrument's own reproducibility is now the
binding constraint.

Before this question can be answered, `s` has to be measured with enough worlds to place a cell to ±0.03, which on the observed
spread (sd ≈ 0.10) means roughly **twenty worlds per cell**, not five to eight. That is a 60-run series, not a 24-run one, and it is
the number the next attempt should be costed at.

## Follow-ups that this run makes concrete

1. **Re-measure the `s(F)` curve with 20 worlds per inflow, all in one logging regime** at 0.025 / 0.030 / 0.035 (60 runs, ~2 h) —
   `s` is the x-axis of every memory claim in this line and its level is not yet placed.
2. **Then** the memory-versus-symmetry test, using the same worlds: it needs no new runs, only the `uid_pairs` already logged.
3. Note for the write-up: X85's `--split-new-uid` differs from X71's default, and the logging regime differs too. Identity assignment
   changes heredity numbers, so X85's `rho1` is not directly comparable with X73–X76; it is used here only for the symmetry
   measurement, which does not depend on it.

доска: принято 0, отклонено 0, отложено 0.
