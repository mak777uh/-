# X98 — is the map threshold-dependent? The angular readout at four excursion cuts

**Why.** Every spectral number in the field line is computed on the excursion set `v > 0.2`, and X71c already taught us that a
conclusion can be a property of the cut rather than of the world ("the band is 0.002–0.005 wide" turned out to be the width of a smooth
crossover, and it moved with the threshold). The map of §10fg–§10fl — one period, a symmetry gradient, a U-shaped memory — rests on the
same readout, so the obvious reviewer question is whether it survives a different cut.

This is an **analysis of stored fields** (X85, X87, X88), no new runs.

## 1. Manipulation is connected

Four cells (`F = 0.025`, `0.030`, `0.035`, `0.040`), twenty worlds each, and **four thresholds** (`v > 0.15`, `0.20`, `0.25`, `0.30`). The
angular readout (`q'`, `s`) is computed from the same saved fields at every cut, so the only thing that changes is the excursion set. A
field whose mask is empty or full at some cut is recorded as unreadable at that cut, not as a number.

## 2. Positive control fires (numeric)

The `0.20` cut must reproduce the committed aggregate of §10fg exactly — `q'` ∈ {5,…,9} and never 11, symmetry medians
0.381 / 0.516 / 0.777 / 0.919 for the X71 cells is not what is recomputed here (different worlds), but the X87/X88 medians must match the
aggregate within 0.01. **The control fires if** the recomputed `0.20` medians for the four cells are within 0.01 of `l1_field_x86` /
`x87`'s values; if not, the implementation differs from the committed one and the comparison is void.

## 3. Readout exists and varies

Per cell and per cut: median `s`, its interquartile range, and the set of `q'` values. The readout of interest is the **ordering** of
the four cells' medians and the presence or absence of `q' = 11`.

## 4. Sensitivity arithmetic

`s` medians differ between cells by 0.10–0.25 (X86: 0.421 → 0.674 → 0.848), and the between-world spread at twenty worlds gives a
standard error of 0.025–0.036, so an ordering is resolved if the gap stays above **0.05**. Four cuts × four cells × twenty fields is
320 angular reads, ~2 minutes of CPU.

## 5. Refusal rule (registered before the run)

**Void** if the §2 control misses, or if more than 5 % of fields are unreadable at the `0.20` cut.

**Robust** if, at every cut, (a) the medians are ordered 0.025 < 0.030 < 0.035 < 0.040, (b) adjacent gaps stay above 0.05, and (c)
`q' = 11` appears in no cell.
**Cut-dependent** if any of (a)–(c) fails at any cut; the failing cut and the quantity are named.
**Mixed** if the ordering holds but a gap falls below 0.05 at some cut.

## Design summary

| factor | value |
|---|---|
| worlds | X85 + X87 (0.025 / 0.030 / 0.035) and X88 (0.040), twenty each — stored fields only |
| thresholds | 0.15, 0.20, 0.25, 0.30 |
| readout | median `s`, IQR, and the `q'` set per cell and cut |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x98_threshold.json` |

## Checklist before the series

- [x] connected (same fields at four cuts; unreadable masks reported as such)
- [x] positive control fires (numeric: the 0.20 cut reproduces the committed medians within 0.01)
- [x] readout exists and varies (gaps of 0.10–0.25 between cells against SE 0.03)
- [x] sensitivity computed (§4: ordering resolved if the gap exceeds 0.05)
- [x] refusal rule written, with "cut-dependent" as a real and expected outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 16:00 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
