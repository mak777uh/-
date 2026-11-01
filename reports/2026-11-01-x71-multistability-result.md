# X71: the medium is multistable in a narrow band — two wavelengths are stable at the same inflow, and both live inside one run

**Date:** 2026-11-01, 19:30 MSK. **Experiment:** X71, the Q7 falsifier.
**Artifacts:** `morphogenesis/experiments/L1_field/x71_f*.json` (70 runs), `_x71_fields/*_t6000.npy`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x71_multistability.json`.
**Preregistration:** `reports/2026-11-01-x71-multistability-plan.md` (amended once, before the series, after the pilot).
**Plan section:** §10eq.

## Verdict

At the boundary between the spot phase and the labyrinth phase the field supports **two wavelengths at the same
parameters**. At `F = 0.035`, `k = 0.06`, five independently started worlds split into two groups: two settle at
**12.0 cells** (q = 8 bins) and three at **8.73 cells** (q = 11 bins) — and **all five runs carry both modes at once**, each
holding at least a fifth of the spectral power. That is multistability in the strong sense: not "different worlds end up
differently", but "one world contains both".

Outside that band the medium is single-valued: 12.0 cells at `F ≤ 0.030` (spread 1 bin), 8.73 cells at
`F = 0.040…0.050` (spread 0 bins). The band is one inflow step wide, which is exactly why it had never been seen: earlier
sweeps sampled the phase, not the boundary.

## The sweep, pattern arm

| F | q per world (bins) | wavelength (cells) | clusters | runs with two modes |
|---|---|---|---|---|
| 0.025 | 7, 7, 8, 8, 8 | 12.0–13.7 | one (spread 1) | 0 |
| 0.030 | 9, 8, 11, 8, 8 | 8.7–12.0 | one (spread 3, no gap ≥ 3) | 0 |
| **0.035** | **8, 11, 11, 8, 11** | **12.0 vs 8.73** | **two: 2 and 3 worlds** | **5 of 5** |
| 0.040 | 11, 11, 11, 11, 11 | 8.73 | one | 2 of 5 |
| 0.045 | 11 ×5 | 8.73 | one | 0 |
| 0.050 | 11 ×5 | 8.73 | one | 0 |
| 0.055 | 6, 6, 11, 11, 11 | 16.0 vs 8.73 | two (flagged) | 0 |

Topology moves with the same parameter and explains the band: β₀ falls 67 → 31 → 4 → 1 and β₁ rises 0 → 0 → 11 → 37 → 87
between `F = 0.030` and `0.050`. The coexistence sits where the spots are neither stable nor gone.

## Positive control, and what it cost

The preregistered control is a **response**, not monotonicity: the peak position must move by ≥ 3 bins between the extremes.
It does — 8 → 11 bins in the pattern arm (12.0 → 8.73 cells), span exactly 3 — and the control fires. Monotonicity does not
hold (8, 8, 11, 11, 11) and is reported as a fact, not used as a gate. This distinction was written into the plan at 17:55,
after the one-seed pilot showed the same shape, and before any of the five-world data existed.

The homogeneous arm fires too (span 7 bins) but only because its `F = 0.055` worlds degenerate: q = 1 bin, β₀ = 1, β₁ = 1,
i.e. the field fills or dies and the spectrum is trivial. Its remaining cells are single-valued (spread ≤ 1 bin). So the
homogeneous arm **cannot** show multistability here, and that is a statement about the arm, not about the world.

## What this changes about heredity

X70 measured a **graded** memory: a daughter's area follows her parent's at about half strength, one generation deep. In a
multistable band the same measurement would have a different shape: the daughter should take the parent's **branch**, and
the correlation should become bimodal concordance rather than a slope. That is now a concrete, falsifiable next step
(X72 below), and it is the first time this line has a candidate mechanism for heredity that is **discrete** rather than
diluted.

It also sharpens the answer to the owner's question. "Conditions for life in a digital medium" is not one condition: this
band is a condition under which the medium can hold **more than one form of itself** at fixed parameters — a prerequisite
for a lineage carrying a state instead of a blur.

## What this does not say

- It does not say the two branches are attractors in the strict sense; it says two wavelengths coexist at t = 6000 with
  ≥ 20 % power each in every world of the F = 0.035 cell. Persistence over longer horizons is untested.
- The `F = 0.055` split is **flagged, not counted as evidence**: q = 6 bins is 16 cells, close to the box scale (6 bins is
  the third radial mode of a 96-cell box), and a domain-scale mode can masquerade as a second morphology. The F = 0.035
  split does not have this problem — 8 and 11 bins are both far from the box scale.
- Resolution: three bins is `3/96 ≈ 0.031` cycles per cell; a split narrower than that would be invisible here, and the
  band could be wider than one inflow step.
- One box (96), one horizon (6000), one threshold (0.2), one second-mode cut (0.2 of power).

## Next

1. **X72 — branch heredity at the boundary.** Seed one parent at `F = 0.035`, let it divide, and ask whether the daughter
   takes the parent's branch (8 or 11 bins) more often than a surrogate structure at the same distance. The instrument is
   already built (`x70_analyse` per-run spectra + `x70_spatial_null` surrogates); the difference is that the readout becomes
   a **classification** (branch concordance) instead of a correlation, so it needs a binomial criterion, not a slope.
2. **Persistence:** re-run the F = 0.035 cell at 24 000 steps. If one branch wins, it is a transient coexistence; if both
   persist, it is a genuine bistability.
3. **Widen the boundary:** half-steps `F = 0.033, 0.037` to measure how wide the band really is — the current data cannot
   tell one inflow step from three.
