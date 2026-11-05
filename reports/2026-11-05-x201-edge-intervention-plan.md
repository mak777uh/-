# X201 — edge-distance intervention: is the free coordinate causal? (05.11, pre-registration)

**Status:** pre-registration, written before any X201 run. New field series (CPU, the same field_track path as X198).

## Question

X200 found that the world label (cell, phase mod 12) is nearly a cluster (ICC 0.9816, 44/841 worlds disagree, 5.2%) but
**not** a sufficient statistic: disagreement is concentrated where two seeds of one phase sit at different distances from the
domain boundary (median edge-distance difference 6.0 cells in disagreeing worlds vs 0 in agreeing ones; 30/72 worlds at
radius 4 gap 10, 12/36 at gap 9, zero elsewhere). X201 turns that correlation into an intervention: at a **fixed** geometry,
**fixed** phase and **identical** parameters, place the same pair at several distances from the edge and read whether the
fusion share moves with distance.

## 1. Manipulation is connected

The intervention moves the pair's absolute position by integer multiples of the stripe period (12 cells), which preserves the
phase `(x mod 12, y mod 12)` and therefore the local inflow (G is periodic with period 12). The geometry (radius, gap, sep) and
every parameter are identical to X198 (F = 0.030, 400 steps, grid 96, the same `COMMON` block and `field_track.py`). Only the
distance to the nearest domain edge changes. `field_track.py` and the world physics are **not** modified. Seeds are selected by a
deterministic census (scan of seeds, as in X198) that picks, for each target phase, seeds whose resulting edge distance falls in
pre-declared bins.

## 2. Positive control fires

The positive control is **within-cell outcome variation at the chosen geometries**: at radius 4 gap 10 the arm-level fusion share
in X198 is **0.2361** (not saturated), and at gap 9 it is **0.5972** — both strictly inside (0, 1), so the outcome can move. The
control fires if, pooling across phases at a fixed geometry, the fusion share differs by **>= 0.25** between the nearest-edge and
farthest-edge bins (an absolute difference, read as the count difference over the fixed number of runs per bin). A second,
phase-level control: at least **2** of the target phases show a non-zero difference in the same direction between the two
extreme bins, confirming the move is not driven by one phase.

## 3. Readout exists and varies

Readout: binary fusion outcome per run (component count drops to 1 over the recorded 400-step series), identical to X198/X199/
X200. It exists for every committed run and varies at both chosen geometries (shares 0.236 and 0.597 in X198, and 30+12
disagreeing clone-worlds in X200 at those geometries).

## 4. Sensitivity arithmetic

Design: **2 geometries** (r=4, gap=10, sep=18; r=4, gap=9, sep=17) × **4 phases** per geometry × **3 edge-distance bins**
(near: edge <= 14 cells; mid: 15–22; far: >= 23, measured as the minimum distance to the nearest domain edge over the four
body centres) × **4 seeds** per (geometry, phase, bin) = **96 runs**. At 400 steps on CPU each run is short (seconds). Per bin
per geometry that is 16 runs; a 0.25 share difference (4 of 16) is detectable as a directionally consistent shift across 4
phases (the phase-level control). This is an intervention sized to detect the magnitude X200's correlation implies, not a
precision estimate; the bin boundaries are fixed from the X200 edge-distance distribution (disagreeing median difference 6
cells, agreeing 0) and will be reported even if a bin is under-filled (refusal rule R1).

## 5. Refusal rule

- **R1 (bin coverage):** if any (geometry, bin) collects fewer than 8 runs across its phases, the analysis reports the actual
  counts and drops power claims for that bin; if fewer than 2 phases are represented in a bin, the phase-level control is not
  evaluated for that bin.
- **R2 (phase feasibility):** a target phase is kept only if the census finds >= 1 seed in at least 2 of the 3 bins; phases that
  cannot be placed at different edge distances (given periodicity and the sep) are replaced from a pre-listed backup set, and
  replacements are logged. If < 3 phases per geometry are feasible, the geometry is reported as under-powered rather than
  pooled into a claim.
- **R3 (confound guard):** if the edge bins differ systematically in a parameter other than position (they must not: same params,
  same phase class), the run is discarded. If the realized phase (recomputed from the saved run) differs from the target, that
  run is excluded and reported.
- **R4 (interpretation):** a share difference that appears in only one geometry is reported as geometry-specific (consistent with
  X200, where the association lived in g9/g10) and is **not** generalized to "edge distance causes fusion" in general.

## Criteria (registered before the runs)

- **C1 (causal shift):** at a fixed geometry, the pooled fusion share in the far-edge bin differs from the near-edge bin by
  >= 0.25 in absolute value.
- **C2 (phase consistency):** >= 2 of the 4 target phases at that geometry show a non-zero difference in the same direction
  between near and far bins.
- **C3 (phase preserved):** >= 95 % of runs recompute to their target phase (mod 12) and identical parameter vectors; failures
  are listed, not silently dropped.

Refutation of the causal reading: C1 fails at both geometries (no share movement with edge distance), or the movement reverses
between geometries with no phase-consistent pattern — in which case X200's correlation is a confound of the specific arm/seed
placements, not a boundary effect.

## Artifacts (to be produced)

- `scripts/x201_edge_intervention.py` (census + run, `--write`, reuses `field_track.py`/X198 `COMMON`), raw series
  `morphogenesis/experiments/L1_field/x201_*.json` (compacted), aggregate
  `morphogenesis/experiments/E09_pond/l1_field_x201_edge_intervention.json`;
- report `reports/2026-11-05-x201-edge-intervention.md` with a §10 card text;
- card §10jk in `docs/plan/10d-field-metrics-and-form.md` and a world-design row. No change to article 030 until a v2.2
  package is assembled.