# X124 — do the generation-time and generation-rate results agree with each other?

**Why.** Two results from this block use the same word for different things, and the identity rule (X122/X123) makes the difference explicit:

- **X93**: the larger sister's *generation time* is longer — her uid lives longer before it divides (a +0.05 share advantage at `F = 0.025`, +0.082 at 0.030,
  reversing in the maze).
- **X113/X114**: the larger sister's *lineage* reaches more generations **per unit time** — `+6.06 / +18.96` generations per 1 000 steps.

These pull in opposite directions: a longer generation time is a longer denominator, so the rate should fall unless the numerator (depth) grows faster. Either the
two findings are consistent and the depth effect dominates, or one of them is mis-measured. The audit is arithmetic, not a new experiment.

## 1. Manipulation is connected

X108's twenty runs, the same sister pairs as X97/X113 (at least 1 000 per cell). Per pair: each sister's **generation time** (uid last appearance − first + 1),
her **subtree depth** (X113's definition), and her **rate** (depth / generation time × 1000). Connectedness: 1 000 pairs per cell; the counts are reported.

## 2. Positive control fires (numeric)

Three controls, all required (the control fires if all three bands hold), because this audit checks other results:

1. **X93's sign reproduces:** the larger sister's generation time must exceed the smaller's with an interval excluding zero in the lattice cell (X93: longer), and
   in the maze it must be shorter or null (X93: reversed).
2. **X113's sign reproduces:** the larger sister's depth must exceed the smaller's with an interval excluding zero in both cells (+1.479 / +2.213).
3. **The rate reproduces:** +6.06 / +18.96 per 1 000 steps within 10 %.

## 3. Readout exists and varies

Per cell: the paired differences in generation time, depth and rate, each with a bootstrap 95 % interval, and the **decomposition**: the mean depth ratio divided
by the mean generation-time ratio, which must equal the rate ratio for the three numbers to be coherent.

## 4. Sensitivity arithmetic

1 000–1 200 pairs; generation times are logged in 10-step units and span a wide range, so the paired differences are well resolved. The declared resolution is an
interval excluding zero, and the coherence check is exact arithmetic on the means (a ratio identity), not a statistical test.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 1 000 pairs or any of the three controls misses its band.

**The results are coherent** if the depth ratio exceeds the generation-time ratio in the same direction as the rate (i.e. the sign of the rate difference follows
from the two components), and the ratio identity holds to 1 %.
**Contradiction** if the rate difference has the opposite sign to what the components imply.
**Mixed** otherwise, cells reported separately.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs, the sister pairs of X97/X113 |
| readouts | paired generation time, depth, rate; the ratio decomposition |
| controls | X93's generation-time sign; X113's depth +1.479/+2.213; the rate +6.06/+18.96 |
| artifact | `E09_pond/l1_field_x124_coherence.json` |

## Checklist

- [x] connected (1 000 pairs per cell)
- [x] positive control numeric (three reproductions)
- [x] readout exists and varies (generation times span a wide range)
- [x] sensitivity computed (§4: interval excluding zero; exact ratio identity)
- [x] refusal rule written, with "contradiction" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-03 02:47 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
