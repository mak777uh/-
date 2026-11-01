# X65 — where does the selection appear? Bracket the transition at 120

1 November 2026, 11:30. Preregistration before the run.

X64 showed the spectral result is grid-dependent: at 96 cells the heterogeneous arm never selects a wavelength, at 144 it
selects like the homogeneous one (normalised entropies 0.61 against 0.62), with the physical wavelength preserved in both
(12 units). The difference between the two runs is the number of cells per pattern period: **12 at grid 96, 18 at grid
144**.

This run puts a point between them: grid **120**, Δx = 0.8, which gives **15 cells per period**. Same physical domain,
diffusion rescaled the same way (`Du = 0.16/0.8² = 0.25`), `dt = 0.5` (`dt·Du = 0.125`, well inside the stability bound),
physical time 6000 by running 12 000 steps.

**Prediction, written before the data.**

- If the transition is sharp and sits at the *pattern scale itself* (a pattern needs roughly 16+ cells per period to be
  stable against a modulation of its own period), then at 15 cells the heterogeneous arm is still **broadband**
  (normalised entropy ≥ 0.8) while the homogeneous arm selects.
- If the transition sits below 15, the heterogeneous arm at 120 **already selects** (normalised entropy ≤ 0.7), and the
  threshold is between 12 and 15.

Either outcome maps the boundary; there is no third reading that leaves it unmapped.

## 1. Manipulation is connected

Same two arms as everywhere: heterogeneous inflow (amp 0.5, correlation 12 units = 15 cells at this Δx) against
homogeneous. The inflow scale is rescaled with the grid so the physical forcing pattern is unchanged.

## 2. Positive control fires

The **homogeneous arm must pattern at 12 units** (15 cells, q = 8 at this grid). If it does not, the scaling is wrong or
the run is unstable and nothing about the heterogeneous arm can be read. This control has now caught one error (X58-lite)
and validated one mapping (X64), so it is the right one.

## 3. Readout exists and varies

Normalised spectral entropy (`H / ln(number of modes)`) and peak share, seed-averaged, at physical times 2000/4000/6000.
Observed across grids: 0.90 (96, heterogeneous), 0.61 (144, heterogeneous), 0.62 (144, homogeneous), 0.61 (96,
homogeneous). The readout separates the two regimes by 0.29, far more than any run-to-run wobble seen so far.

## 4. Sensitivity arithmetic

Five seeds per arm, seed-averaged spectra, no p-values. The two pre-declared outcomes are separated by 0.1 in normalised
entropy (0.8 against 0.7) around the observed values 0.61 and 0.90; the discrimination is a **threshold on a seed-averaged
quantity**, not a difference of two noisy medians.

## 5. Refusal rule

Worthless, not negative, if:

1. any run produces NaN;
2. the homogeneous arm does not land within 14–16 cells (its own physical wavelength, 12 units, is 15 cells here);
3. the heterogeneous entropy falls outside both pre-declared bands (0.7–0.8), leaving the transition unmapped.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid **120**, `dt = 0.5`, 12 000 steps (physical 6000), `Du = 0.25`, `Dv = 0.125`, `F = 0.035`, `k = 0.06`, `beta = 0.2`, `freq_dep = 1`, mutation 0.15 |
| arms | heterogeneous (amp 0.5, correlation 15 cells = 12 units) against homogeneous |
| seeds | 171–175 |
| fields | saved at steps 4000, 8000, 12000 |
| criterion | homogeneous at 14–16 cells; heterogeneous normalised entropy ≥ 0.8 (broadband) or ≤ 0.7 (selecting) |
| cost | ≈ 4 min per run, 10 runs ≈ 40 min |
| artifacts | `morphogenesis/experiments/L1_field/x65_{pattern,homog}_s*.json`, `x65_fields/` |

## Status

- [x] connected (same arms; inflow rescaled with Δx)
- [x] positive control fires (homogeneous at 96 and 144 patterned at 12 units)
- [x] readout exists and varies (0.61–0.90 across grids and arms)
- [x] sensitivity computed (threshold on a seed-averaged quantity, 0.1 separation)
- [x] refusal rule written (three conditions)
