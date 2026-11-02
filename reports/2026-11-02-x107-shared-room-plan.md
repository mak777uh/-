# X107 — is part of the lattice heredity a shared-room effect?

**Why.** X106 showed that in the lattice the distance to the nearest non-ancestor peak predicts the **mother's** own area (`+0.397`)
slightly better than her daughter's (`+0.322`): room is a property of the place, not of the lineage. Daughters, however, are born
close to their mothers (median 4.9 cells at `F = 0.030`), so mother and daughter usually occupy the **same room**. If room predicts
both areas, then part of the parent–daughter correlation — the 0.531 that the whole line rests on — may be a shared environment
rather than an inherited width.

This is the one internal check that could reduce every heredity number in this line, so it is worth doing before the numbers travel.

## 1. Manipulation is connected

X100's logs, two inflows, ten worlds each; the same pairs as X106, which means the same requirement of a non-ancestor peak at the
mother's peak step and a measurable lifetime is **not** needed here — only the non-ancestor distance for the mother. At least
**100 pairs** per cell, and the mother-distance coordinate must cover at least **50 %** of the ancestor–daughter pairs.

## 2. Positive control fires (numeric, both required)

1. **Heredity:** `ρ(mother area, daughter area) ≥ 0.35` in both cells (full samples 0.531 / 0.384).
2. **The room coordinate:** `ρ(d_near of the mother, mother's area)` must reproduce X106 within **0.10** (+0.397 at 0.030, −0.038
   at 0.040). If it has drifted, the partial below is measuring a different coordinate and the analysis is void.

## 3. Readout exists and varies

Per cell: the control coefficient, `ρ(mother area, daughter area | d_near of the mother)`, the drop (control minus partial), the
partial controlling **both** mother and daughter `d_near`, and the per-world coefficients of the control and of the partial. The
partial varies over a plausible range because `d_near` correlates with the mother's area at 0.40 — the shared variance is there to
be removed if it exists.

## 4. Sensitivity arithmetic

1 834 and 800 pairs (X106's coverage), so the standard error of each coefficient is 0.023 and 0.035; a partial with one control
loses little. The declared resolution is **0.10**, four and three sigma. Drops smaller than that are reported as no drop.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 100 pairs, coordinate coverage below 50 %, heredity below 0.35, or the room control outside ±0.10
of X106.

**Heredity is not a shared-room effect** if in **both** cells the drop is `≤ 0.10`.
**Heredity is partly a shared-room effect** if in the lattice cell the drop is `≥ 0.15` but the residual stays `≥ 0.25`.
**Heredity is mostly a shared-room effect** if in the lattice cell the residual falls **below 0.25**.
**Mixed** otherwise, printed cell by cell — and if the lattice and the maze disagree, the claim is stated for the lattice only, where
the room coordinate has an effect to remove.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs (logs only) |
| readout | `ρ(mother area, daughter area)` before and after controlling the mother's `d_near` (and both `d_near`s) |
| controls | heredity ≥ 0.35; the room coefficient reproduces X106 within 0.10 |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x107_shared_room.json` |

## Checklist

- [x] connected (100 pairs, coordinate coverage ≥ 50 %)
- [x] positive controls numeric (heredity ≥ 0.35; room coefficient within 0.10 of X106)
- [x] readout exists and varies (room–area correlation 0.40 in the lattice)
- [x] sensitivity computed (§4: SE 0.023 / 0.035, resolution 0.10)
- [x] refusal rule written, with "mostly a shared-room effect" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 17:15 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
