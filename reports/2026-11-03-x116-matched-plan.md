# X116 — is the survival advantage mechanical? A matched-branch test

**Why.** X115 found the larger sister's line alive at the end +0.250 / +0.137 more often (CI far from zero, counts 324:39 and 178:14). But a larger structure
has more cells and often **more branches**, so it can lose members and still be present — the survival advantage could be arithmetic rather than a
property of the line. X97b answered that objection for the granddaughters' *sizes* (median 98 % of the mean, branch counts within 4 %); it was not
answered for survival.

**The test.** Match sister pairs on the confound: compare survival only among pairs whose two branches have the **same number of daughters**. If the
advantage survives matching, it is not the branch count.

## 1. Manipulation is connected

X108's twenty runs. For every sister pair with both branches measured: `n_a`, `n_b` = number of daughters of each sister; survival as in X115 (any
descendant present at the last logged step). Connectedness: at least **200 matched pairs** per cell (equal `n`), and the unmatched and matched subsets are
reported side by side, because a matched subset that is tiny would make the test weak rather than negative.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The full-sample contrast reproduces X115** within 5 % (+0.250 / +0.137) — the control fires if both hold, so this is the same measurement on a
   subset.
2. **Matching actually matches:** the mean difference in `n` between the larger and smaller sister must be **0.00** in the matched subset (by
   construction) and at least 0.1 in the full sample, so the confound exists before matching and is removed after.

## 3. Readout exists and varies

Per cell: the survival difference in the **matched** subset with a bootstrap 95 % interval, the counts (only larger / only smaller), and the mean number of
daughters in each arm. Variation exists: X115's full-sample difference is 0.25 with 324 against 39.

## 4. Sensitivity arithmetic

With ~200–600 matched pairs the paired-proportion SE is ≤ 0.035, so the declared resolution is **0.10** — twice the full-sample resolution of X115,
because matching discards pairs. An effect below that is "unresolved after matching", not "no effect".

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 200 matched pairs, the full-sample control misses its 5 % band, or the matching check fails.

**The advantage is not branch count** if the matched survival difference is positive with the interval excluding zero in both cells.
**The advantage was branch count** if the matched interval contains zero in both cells while X115's full-sample interval excluded it.
**Mixed** otherwise, cells reported separately.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs |
| readouts | survival difference among pairs matched on the number of daughters; full-sample contrast for the control |
| controls | full-sample reproduction within 5 %; the confound exists before matching |
| artifact | `E09_pond/l1_field_x116_matched.json` |

## Checklist

- [x] connected (200 matched pairs; matched and unmatched reported together)
- [x] positive control numeric (X115 reproduced within 5 %; matching check on the mean difference in `n`)
- [x] readout exists and varies (full-sample 0.25 with 324:39)
- [x] sensitivity computed (§4: SE ≤ 0.035, resolution 0.10)
- [x] refusal rule written, with "the advantage was branch count" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-03 01:36 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
