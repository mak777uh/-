# X89 — the lineages do not switch off, they fade: pairs per world fall 2.4× per half-step and reach zero smoothly

**Date:** 2026-11-02, 10:35 MSK. **Experiment:** X89 (four half-steps between `F = 0.045` and `0.050`).
**Preregistration:** `reports/2026-11-02-x89-lineage-edge-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x89_f0{46,47,48,49}_pattern_s261-268.json` (32 runs), fields `_x89_fields/`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x89_lineage_edge.json`.

## Registered verdict

**Graded disappearance** — the preregistered rule for "monotone fall with no single step reaching 10×". The lineage count falls by a
factor 2.0–3.3 at every half-step, so there is no inflow at which reproduction stops; it becomes rarer.

## Numbers

| `F` | lag-1 pairs per world (median, range) | components | single-component worlds | β₁ > 0 |
|---|---|---|---|---|
| 0.045 (X88) | 31.8 | lattice | 0/20 | — |
| 0.046 | **13.0** (8–19) | 1.0 | **8/8** | 8/8 |
| 0.047 | **6.0** (4–11) | 1.0 | 8/8 | 8/8 |
| 0.048 | **2.0** (0–2) | 1.0 | 8/8 | 8/8 |
| 0.049 | **1.0** (0–2) | 1.0 | 8/8 | 8/8 |
| 0.050 (X88) | 0.3 | 1.0 | 20/20 | 20/20 |

Steps between neighbours: **2.4×, 2.2×, 3.0×, 2.0×, 3.3×**. The positive control fired — the 0.046 cell carries 13 pairs per world
against the required 10, so the edge was inside the measured range and the series did not miss it.

Two facts worth naming:

1. **The world is already a maze at 0.046.** Every one of the 32 new worlds is a **single component** with β₁ > 0 (holes present), and it
   *still divides* — 13 times per world at 0.046, once at 0.049. So "one component" is not the same as "no reproduction": the maze
   buds rarely. What disappears across this range is not the ability to divide but its **rate**.
2. **The decay is geometric in inflow.** A factor of 2.4 per 0.001 of inflow, i.e. the lineage count halves roughly every **0.0008** of
   `F`. Over the whole range measured (0.045 → 0.050) that is a factor of ~100, spread evenly.

## What this means for the heredity line

The boundary the heredity work needs is not a wall but a slope. At 0.050 a world produces one division event per three to four worlds;
the heredity statistics we use need hundreds of pairs, so the *measurable* edge (400 pairs) sits near `F ≈ 0.046`, while the
*phenomenological* edge (no divisions at all) is above 0.050 or does not exist. A medium whose divisions become arbitrarily rare is not
a medium without inheritance — it is a medium where inheritance is not observable, and the two should not be confused in the write-up.

That also gives the life question a quantitative shape: the rate at which a medium creates new individuals is a **continuous function of
its place in the parameter plane**, decaying by a factor ~2.4 per 0.001 of inflow here, rather than a threshold to be crossed.

## What is open

- Above 0.050 the lineage count goes below our resolution (0.3 per world). Whether it reaches exactly zero, or keeps a residual trickle,
  needs either longer horizons (more chances to divide) or a bigger box. Not urgent.
- The same scan at a different `k` would tell whether the "melt" of the lattice into a maze and the fading of divisions are one
  transition or two.

доска: принято 0, отклонено 0, отложено 0.
