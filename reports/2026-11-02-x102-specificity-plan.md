# X102 — does the *specificity* of inheritance survive a weaker size definition?

**Why.** X91 established, under the excursion set at `v > 0.20`, that a daughter's size follows her **parent** (0.39–0.55) far more than
her **nearest non-ancestor** (0.06–0.25), gaps of 0.26–0.41. X101 then showed that the *level* of heredity collapses down a ladder of
definitions: 0.531 / 0.384 for the excursion set, 0.300 / 0.174 for a topological basin, 0.176 / 0.058 for a basin at half the local
maximum.

The open question is the one that decides how to describe this medium: does the **gap** — the part X91 actually measured — collapse with
the level, or is specificity robust where the level is not? If the gap survives, "a daughter resembles her mother more than her
neighbours" is a statement about the medium. If the gap collapses too, then even the specificity is a property of the excursion-set
definition, and the line's central claim must say so.

This is an **analysis of stored snapshots** (X100's twenty runs), no GPU.

## 1. Manipulation is connected

Two inflows (`F = 0.030`, `0.040`), ten worlds each. For every daughter the analysis needs: her parent, her nearest non-ancestor at the
snapshot of her first appearance (the X73 control), and both sizes under both definitions. Connectedness: at least **100 pairs** per cell
and the basin definition must be available for at least **80 %** of them.

## 2. Positive control fires (numeric)

The threshold gap must be **positive in both cells** — that is X91's result reproduced on these ten-world samples. **The control fires if**
gap > 0 at both inflows; a non-positive gap would mean the pairing or the stranger lookup differs from X91's and the comparison is void.

## 3. Readout exists and varies

Per cell: `ρ(parent, daughter)`, `ρ(nearest non-ancestor, daughter)` and their difference, computed twice — once with the excursion-set
area at 0.20, once with the topological basin area (steepest ascent, no level set) — **on the same daughters**, so the two gaps are
paired.

## 4. Sensitivity arithmetic

The gap under the strong definition was 0.26–0.41 in X91 on 2 400–3 000 pairs; here the samples are ~2 000 and ~1 700 pairs, and the
paired structure removes the world-to-world variation. The declared resolution is a **change of 0.15** in the gap; with ~1 700 pairs a
gap difference of 0.15 is ≈2σ.

## 5. Refusal rule (registered before the run)

**Void** if a cell has fewer than 100 pairs, basin coverage below 80 %, or a non-positive threshold gap (§2).

**Specificity is robust** if the basin gap stays within **0.15** of the threshold gap in both cells **and** remains at least **0.15**
absolute.
**Specificity is definition-bound too** if the gap falls by **≥ 0.15** in at least one cell.
**Mixed** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs (fields at every logged step) |
| definitions | excursion set at `v > 0.20`; basin by steepest ascent |
| control | the nearest non-ancestor at the daughter's first appearance (X73's rule, returning the uid this time) |
| readout | gap between parent and stranger correlations, per definition, on the same daughters |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x102_specificity_ladder.json` |

## Checklist before the series

- [x] connected (100 pairs, 80 % basin coverage)
- [x] positive control fires (numeric: threshold gap > 0 in both cells)
- [x] readout exists and varies (X91 gaps 0.26–0.41; X101 levels 0.53 / 0.30)
- [x] sensitivity computed (§4: gap change 0.15 at ~2σ)
- [x] refusal rule written, with "specificity is definition-bound too" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 20:20 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
