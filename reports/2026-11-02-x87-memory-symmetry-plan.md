# X87 — memory against symmetry, on worlds that carry both readouts (X85's cells brought to twenty)

**Why.** The curve is placed (X86: `s` = 0.421 / 0.674 / 0.848 for `F` = 0.025 / 0.030 / 0.035, SE 0.025–0.036). The question that
survives from the whole two-scale programme is whether the size memory depends on that coordinate. X85 asked it on 24 worlds and could
not answer: the within-cell coefficients were −0.33 / −0.25 / −0.02 against a bar of −0.5, the pooled partial correlation controlling
inflow was 0.00, and its own control voided the series because the band was borrowed from another logging regime.

X86's sixty worlds cannot help: with `--split-new-uid` off they carry no genealogies at all (0 `uid_pairs`). So the test needs worlds
with **both** readouts — the split convention *and* the saved field. X85's 24 have them (seeds 191–198, split on, 50-step logging).
This series adds **twelve worlds per cell** (seeds 221–232), bringing each cell to twenty, with flags identical to X85's.

## 1. Manipulation is connected

Three inflows, twelve new worlds each, flags identical to X85 (`--split-new-uid`, `--sample-every 50`, `--hetero-scale 12.0`,
`--hetero-amp 0.5`, 6000 steps, field at 6000, `--init-jitter`). Flag parity with X85 is checked and reported; if any physical flag
differs, the pooled analysis is void because the cells would mix conventions.

Connectedness: each new cell must produce ≥400 lag-1 pairs and ≥10 components, and its `s` range must exceed 0.05 — otherwise the
cell contributes no spread to correlate and is void.

## 2. Positive control fires (numeric)

Two bands, both from the same regime, both measured before this run:

- the pooled `F = 0.030` lag-1 correlation must lie in **[0.45, 0.56]** (X74's 0.507, same split convention);
- the `F = 0.035` cell's median `s` must lie in **[0.78, 0.90]** (X85's 0.870 and X86's 0.848, both 50-step; the band is their
  envelope widened by the observed world-to-world sd of 0.11–0.16).

**The control fires if** both hold on the pooled twenty worlds. If either misses, the series is void: the worlds would not be the ones
the curve and the memory numbers come from.

## 3. Readout exists and varies

Per world: `s` (angular), `q'`, `rho1..3` from `uid_pairs`, per-world `lambda` and half-life (where both ratios are positive), and the
component count. Pooled per cell: `rho1` with its world-level Spearman against `s`, and the pooled partial correlation of `rho1` with
`s` controlling inflow over all sixty worlds (X85's 24 + these 36).

## 4. Sensitivity arithmetic

With twenty worlds per cell the standard error of a Spearman coefficient is ≈1/√19 = 0.23 under the null, so a within-cell `|rho|` of
**0.5** is ≈2.2σ and is the declared resolution; the pooled sixty worlds resolve `|rho|` of **0.45**. `s` itself is placed to ±0.03
(SE 0.025–0.036 from X86). Cost: 36 runs at ~90 s ≈ **55 minutes**.

## 5. Refusal rule (registered before the run)

**Void** if a cell has <10 components, <400 lag-1 pairs, a dead field (std < 0.01), an `s` range narrower than 0.05, if flag parity
with X85 fails, or if the §2 control misses either band.

**Symmetry carries memory** if, over the pooled twenty worlds per cell, Spearman(`rho1`, `s`) is **<= −0.5 in at least two of three
cells** and the pooled partial correlation controlling inflow is **<= −0.45**.

**Symmetry does not carry memory** if the coefficient is **>= +0.5 in at least two cells**, or if **all three** lie in **[-0.3, +0.3]**.
Anything else is **inconclusive**, printed in full with the per-cell coefficients and the partial correlation.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.025`, `0.030`, `0.035`, `k = 0.06` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5`, `const_ones` signal |
| worlds | **12 new per cell**, seeds 221–232, pooled with X85's 8 (seeds 191–198) → 20 per cell |
| identity | **`--split-new-uid` on** (the heredity convention; stated because it decides which readouts exist) |
| logging | **`--sample-every 50`**, identical to X85 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| field | saved at 6000, `_x87_fields/` |
| artifact | `morphogenesis/experiments/L1_field/x87_f{025,030,035}_s221-232.json`, aggregate `l1_field_x87_memory_vs_symmetry.json` |

## Checklist before the series

- [x] connected (pairs, components, `s` spread — all three gate a cell)
- [x] positive control fires (numeric, same-regime bands, §2)
- [x] readout exists and varies (X85 shows both vary; eleven of twelve fittable in the earlier cells)
- [x] sensitivity computed (§4)
- [x] refusal rule written, with flag parity as a void condition
- [x] both conventions named (identity and logging) because each decides which readouts exist

## Status

Registered 2026-11-02 06:55 MSK, before the series. Thirty-six runs, ~55 minutes.

доска: принято 0, отклонено 0, отложено 0.
