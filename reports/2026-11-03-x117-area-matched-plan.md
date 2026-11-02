# X117 — match on area too: does any survival advantage remain?

**Why.** X116 removed the branch-count confound and found the survival advantage halving (0.250 → 0.125) and falling to a third (0.137 → 0.044), with a residual
that excludes zero in both cells. But after matching on the number of daughters, the **larger sister is still larger**: her area is the very thing that defines
"larger". If the residual is the remaining size difference, then the survival advantage is arithmetic all the way down and the line has no lineage effect in
survival.

**The test.** Among sister pairs whose branches have the same number of daughters, keep only those whose **areas are within ±10 %**. Then the two branches of a
pair are matched on both the branch count and the size, and any survival difference is neither of those.

## 1. Manipulation is connected

X108's twenty runs. Per pair: number of daughters of each sister, peak area of each sister, survival as in X115 (any descendant present at the last logged
step). The matched subset requires (a) equal daughter counts and (b) `|area_big − area_small| / max(area) ≤ 0.10`.

Connectedness: at least **150 matched pairs** per cell at ±10 %; if a cell has fewer, the window widens to ±20 % and the fact is stated — a tight match that
leaves fifty pairs is a weak test, not a negative one, and the report says which window was used.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The X116 contrast reproduces** within 5 % on the same equal-daughters subset (+0.125 / +0.044), so this is the same measurement narrowed further.
2. **The matching bites:** the mean area ratio between the branches must be **at least 1.25 in the full sample** and **at most 1.10 in the matched subset** —
   the confound exists before and is removed after.

## 3. Readout exists and varies

Per cell: the survival difference in the area-matched subset, with a bootstrap 95 % interval, and the counts only-larger / only-smaller. Variation exists:
X116's equal-daughters subset gives 0.125 with 104:25.

## 4. Sensitivity arithmetic

With 150–350 matched pairs the paired-proportion SE is ≤ 0.04, so the declared resolution is **0.12** — larger than X116's 0.10 because the second match
discards more. An effect below it is "unresolved after matching", never "no effect".

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 150 matched pairs even at ±20 %, the X116 control misses its band, or the matching check fails.

**A genomic-like lineage effect remains** if the area-matched survival difference is positive with the interval excluding zero in both cells.
**The survival advantage is fully arithmetic** if the interval contains zero in both cells while X116's equal-daughters interval excluded it.
**Mixed** otherwise, cells reported separately.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs |
| readouts | survival difference among pairs matched on daughters **and** area (±10 %, widening to ±20 % if needed) |
| controls | X116 reproduced within 5 %; area ratio ≥ 1.25 before, ≤ 1.10 after |
| artifact | `E09_pond/l1_field_x117_area_matched.json` |

## Checklist

- [x] connected (150 matched pairs; the window used is stated)
- [x] positive control numeric (X116 within 5 %; the matching check on area ratio)
- [x] readout exists and varies (0.125 with 104:25 on the daughters-only subset)
- [x] sensitivity computed (§4: SE ≤ 0.04, resolution 0.12)
- [x] refusal rule written, with "fully arithmetic" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-03 01:42 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
