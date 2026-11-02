# X106 — the crowding term: a property of places, of growth, or of persistence?

**Why.** X103d went looking for a confound and found an effect instead: in the lattice cell a daughter born farther from the nearest
**non-ancestor** peak grows into a larger excursion (`ρ = +0.358`, ten worlds out of ten), while the distance to her own mother's
peak carries nothing (`−0.008`). It is the first quantity in this line that is not about ancestry, and it says something simple and
testable: *room around a structure predicts its size.*

Three readings, and they are not the same claim:

- **a property of places** — the distance to the nearest neighbour describes where structures *can* grow, so it should predict the
  **mother's** area just as well as the daughter's (the coordinate is the same, no inheritance involved);
- **a constraint on growth** — it predicts the daughter's peak **area** but not how long she **lasts**;
- **a constraint on persistence** — it predicts both: a structure with room not only grows larger but lives longer.

## 1. Manipulation is connected

X100's twenty runs (seeds 291–300 per inflow), logs only — no fields, no GPU. For each ancestor–daughter pair: the daughter's birth
centroid and birth step, her peak area, her lifetime (last logged step minus first logged step), and the distance from her birth
centroid to the nearest component at that step that is not an ancestor (the X103d coordinate). For the "place" readout the same
distance is computed for the **mother** at the mother's own peak step. Connectedness: at least **100 pairs** per cell with a
non-ancestor peak present and a measurable lifetime.

## 2. Positive controls fire (numeric, both required)

1. **Heredity:** `ρ(mother's area, daughter's area) ≥ 0.35` in both cells.
2. **Replication:** the crowding coefficient on the daughter's area must reproduce X103d within **0.10** (+0.358 at 0.030, +0.103 at
   0.040). If the coordinate has drifted, nothing below is comparable and the analysis is void.

## 3. Readout exists and varies

Per cell: `ρ(d_near, daughter area)`, `ρ(d_near, mother area)`, `ρ(d_near, daughter lifetime)`, the partial of the daughter's area
given her lifetime (so "growth" is not just "persistence" in disguise), the medians of `d_near`, and the per-world coefficients for
the lifetime readout. Variation exists by construction — `d_near` has a median of 8.8 and 12.4 cells in the two cells and a wide
spread.

## 4. Sensitivity arithmetic

2 024 and 1 139 pairs, so the standard error of a Spearman coefficient is 0.022 and 0.030; the declared resolution is **0.10** (four
and three sigma). Lifetime is a coarse quantity (logged every 50 steps, so it takes values in multiples of 50) and is treated as
such: only coefficients of 0.20 or more are called real, and the per-world agreement is reported next to the pooled value.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 100 pairs, heredity below 0.35, or the replication control misses its band.

**A property of places** if `|ρ(d_near, mother area)| ≥ 0.20` with the **same sign** as the daughter's coefficient in the same cell —
the coordinate describes the place, and "crowding" is a fact about the medium's geometry, not about daughters.
**A constraint on growth** if the daughter's area coefficient is `≥ 0.20` and the lifetime coefficient is `|ρ| ≤ 0.10`.
**A constraint on persistence** if both are `≥ 0.20` with the same sign.
**Mixed** otherwise, printed cell by cell; and if the two cells disagree, the crowding term is reported as inflow-specific rather
than as a property of the medium.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs (logs only) |
| readout | `ρ(distance to the nearest non-ancestor peak, ·)` against daughter area, mother area and daughter lifetime |
| controls | heredity ≥ 0.35; X103d's coefficients reproduced within 0.10 |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x106_crowding.json` |

## Checklist

- [x] connected (100 pairs, non-ancestor peak present, lifetime measurable)
- [x] positive controls numeric (heredity ≥ 0.35; replication within 0.10)
- [x] readout exists and varies (median `d_near` 8.8 / 12.4 cells)
- [x] sensitivity computed (§4: SE 0.022 / 0.030, resolution 0.10; lifetime coarse, 0.20 floor)
- [x] refusal rule written, with "a property of places" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 17:11 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
