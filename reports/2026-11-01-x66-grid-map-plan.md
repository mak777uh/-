# X66 — the grid map with one time step: 96 and 108 at `dt = 0.5`

1 November 2026, 12:28. Preregistration before the run.

X65 showed the bracket at 120 did not resolve the grid transition, and it also exposed a confound: the **96** point in our
comparison was run at `dt = 1.0`, while 120 and 144 were run at `dt = 0.5`. We know from `X56` that the time step changes
counts and spectra substantially, so a map that mixes steps is not a map of resolution.

This run fixes the step at **0.5 for every grid** and adds the missing point at **108**, so that with 120 and 144 already
on disk the map has four resolutions sharing one step:

| grid | Δx | required `Du` | `dt` | new or existing |
|---|---|---|---|---|
| **96** | 1.000 | 0.16 | 0.5 | **new** (the old 96 point was `dt = 1.0`) |
| **108** | 0.889 | 0.2025 | 0.5 | **new** |
| 120 | 0.800 | 0.25 | 0.5 | existing (X65) |
| 144 | 0.667 | 0.36 | 0.5 | existing (X64) |

All four keep 6000 physical time (12 000 steps at `dt = 0.5`) and the same inflow in physical units (correlation 12 units =
12, 13.5, 15, 18 cells respectively).

## Prediction, written before the data

With the step held fixed, the map should become monotone in resolution or show a clean threshold; if the 96-at-0.5 point is
still broadband and the 108 point still broadband, while 144 selects, the transition sits between 108 and 144 and the 120
oddity was noise or a still-forming pattern. If 96-at-0.5 already selects, then the old "no selection at 96" result was a
`dt = 1.0` effect, not a resolution effect — which would be an even more interesting correction.

**The readout is the peak position relative to 12 units**, with concentration as a secondary. That is the lesson of X65 and
it is now the primary criterion, not an afterthought.

## 1. Manipulation is connected

Same two arms as everywhere, same seeds, same physical inflow. The only change at the new points is resolution and the
diffusion coefficient that keeps the physical diffusivity fixed.

## 2. Positive control fires

The **homogeneous arm must pattern at 12 units on both new grids** (12 cells at 96, 13.5 at 108). If it does not, the
scaling is wrong and nothing about the heterogeneous arm can be read.

## 3. Readout exists and varies

Peak position in cells and units, peak share, normalised entropy — all seed-averaged over five seeds at three snapshots.
Observed across the existing grids: peaks at 12 units where a pattern exists, share 0.20–0.45, normalised entropy
0.53–0.79. The readout varies more than any plausible error.

## 4. Sensitivity arithmetic

Five seeds per arm, seed-averaged spectra, no p-values. The band for "pattern at the medium's wavelength" is
**±1 cell** around the expected position (12 cells at 96, 13.5 at 108, which rounds to 13–14). A wrong mapping shifts the
peak by at least one mode, and the three existing grids show shifts of two to four cells when the mapping was wrong.

## 5. Refusal rule

Worthless, not negative, if:

1. any run produces NaN;
2. the homogeneous arm on either new grid misses its band by more than one cell;
3. the heterogeneous peak lands on a scale that is neither the pattern's nor the q = 1 box mode — then it is concentrating
   on something we have not identified, and the map cannot be read as resolution dependence.

## Design summary

| element | value |
|---|---|
| world | L1 field, grids **96** and **108**, `dt = 0.5`, 12 000 steps (physical 6000), `Du = 0.16` and `0.2025`, `Dv = 0.08` and `0.10125`, `beta = 0.2`, `freq_dep = 1`, mutation 0.15 |
| arms | heterogeneous (amp 0.5, correlation 12 units) against homogeneous |
| seeds | 171–175 |
| fields | saved at steps 4000, 8000, 12000 |
| criterion | §4, peak position primary |
| cost | ≈ 2.5 and 3.5 min per run, 20 runs ≈ 65 min |
| artifacts | `morphogenesis/experiments/L1_field/x66_g{096,108}_{pattern,homog}_s*.json`, `x66_fields/` |

## Status

- [x] connected (same arms; only resolution and the matching `Du` change)
- [x] positive control fires (homogeneous patterns at 12 units on 96 and 144)
- [x] readout exists and varies (share 0.20–0.45, normalised entropy 0.53–0.79 across grids)
- [x] sensitivity computed (a one-cell band; observed wrong mappings shift two to four)
- [x] refusal rule written (three conditions)
