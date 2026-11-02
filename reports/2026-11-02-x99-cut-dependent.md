# X99 — the memory map is cut-dependent, and at 0.25 the order between inflows flips

**Date:** 2026-11-02, 17:35 MSK. **Experiment:** X99 (two inflows × two excursion thresholds, ten worlds each).
**Preregistration:** `reports/2026-11-02-x99-threshold-memory-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x99_f0{30,40}_thr{015,025}_s281-290.json` (40 runs), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x99_threshold_memory.json`.

## Registered verdict

**Void** — but on a clause that was mis-specified, and the mis-specification is mine. The rule required ≥10 mean components per cell;
the `F = 0.040` cell at threshold 0.15 reads **2.5**, because that world *is* a percolating maze — few, large components are its regime,
not a collapse. The same mistake was avoided in X88, where the percolating arm was checked by "few components **and** β₁ > 0"; here the
lattice floor was copied into a design that includes a maze cell.

The substantive result is legible anyway and is reported below, with the void standing.

## Numbers

| cell | threshold | half-life, per-world median | vs the 0.20 value | ρ₁ | pairs | components | median peak area |
|---|---|---|---|---|---|---|---|
| `F = 0.030` | 0.15 | **0.77** | −0.39 | 0.552 | 2 464 | 43.1 | 83 |
| `F = 0.030` | 0.20 (committed) | **1.16** | — | — | — | — | — |
| `F = 0.030` | 0.25 | **2.26** | **+1.10** | 0.479 | 3 635 | 54.4 | 33 |
| `F = 0.040` | 0.15 | **1.84** | −0.24 | 0.392 | 833 | 2.5 | 530 |
| `F = 0.040` | 0.20 (committed) | **2.08** | — | — | — | — | — |
| `F = 0.040` | 0.25 | **0.69** | **−1.39** | 0.474 | 3 021 | 23.2 | 70 |

## What this says

1. **The levels are not robust.** At `F = 0.030` the half-life runs 0.77 → 1.16 → 2.26 across cuts of 0.15 / 0.20 / 0.25 — a factor of
   almost three. At `F = 0.040` it runs 1.84 → 2.08 → 0.69. The registered rule's bar was a 0.4-division move; both inflows exceed
   0.8 at one cut or the other.
2. **The ordering between inflows flips.** At 0.20 the maze remembers longer than the lattice (2.08 against 1.16); at 0.15 the same
   ordering holds more weakly (1.84 against 0.77), but at 0.25 it **reverses** (0.69 against 2.26). So it is not only the magnitude of
   the map that belongs to the cut — the direction of the comparison does, too.
3. **Why this happens is not mysterious.** The excursion threshold changes which cells count as a structure, hence what "a structure's
   size" means: at 0.15 in the maze the components merge into 2.5 objects whose areas are ~530 cells, at 0.25 the same field breaks into
   23 objects of ~70 cells. Peak area is a threshold-defined quantity, and the memory is a function of peak area. A map built on it is a
   map of *that* definition.

## Consequence for what we published today

Claims 305/306 (the U-shaped memory, the two levels inside and outside the band) and §10fl stand **at threshold 0.20 and only there**.
They are not refuted — the measurement is correct — but they are **definition-bound**, and the text must say so. The same applies to
§10fa's older two-level numbers and to every half-life in the line: one cut, one definition, no robustness claim.

This is the third member of a family we have now met three times today: the pooled-versus-per-world half-life (§10ff), the logging
regime (§10fi), and now the excursion cut. In each case a number that looked like a property of the world was partly a property of a
choice. The pattern is consistent enough to state as a rule: **a half-life in this line is quoted together with its estimator and its
cut, or it is not quoted.**

## What would settle it properly

The three cuts disagree in direction, so the next step is not another cut but a definition that does not need one: a size measure in
the continuous field (for example the integral of `v` over a component's basin, or the area at half-maximum), computed without a binary
mask. That is a real design task, not a run; it is registered as X100 in the queue.

доска: принято 0, отклонено 0, отложено 0.
