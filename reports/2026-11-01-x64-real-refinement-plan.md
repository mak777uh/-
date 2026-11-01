# X64 — a real refinement: same physical domain, smaller step

1 November 2026, 10:15. Preregistration before the run. This replaces the withdrawn X58-lite.

The board remark **B-094** showed that X58-lite was not a refinement: the code has no Δx, the quantity that plays physical
diffusion is `dt·Du·Δx²`, and moving 96 → 128 while keeping `dt = 0.5` changed the physics. The pattern landed at 16 cells
instead of 12 exactly as `√Du` predicts, which confirmed the error rather than the claim.

This run does it properly, and the arithmetic comes first, because in this world refinement is not free.

## The arithmetic that constrains the design

Explicit Euler with the four-neighbour Laplacian is stable while `dt·Du ≤ 0.25`. If the lattice spacing is `Δx`, the
physical diffusivity is `Du·Δx²`, so refining by a factor `f` (same physical domain) requires `Du → Du·f²` and then
`dt ≤ 0.25/(Du·f²)`:

| grid | Δx | required `Du` | `dt` allowed | verdict |
|---|---|---|---|---|
| 96 | 1.000 | 0.16 | ≤ 1.56 | base |
| 128 | 0.750 | 0.28 | ≤ 0.88 | usable, but **dt was 0.5 and the physics changed** |
| **144** | **0.667** | **0.36** | **≤ 0.69** | **chosen: `dt = 0.5` is inside the bound** |
| 192 | 0.500 | 0.64 | ≤ 0.39 | **unstable at `dt = 0.5`; needs `dt ≤ 0.39` and four times the steps** |

So a genuine refinement costs at least four times the wall clock, and at 192 it costs even more because `dt` must shrink
too. Grid 144 with `dt = 0.5` is the cheapest honest refinement: `Δx` is two thirds of the base, and the stability bound is
respected with a margin of 0.69 against 0.5.

## Prediction, written before the data

If the mapping is now correct, the homogeneous arm must pattern at the **same physical wavelength**, 12 units, which at
this grid is 18 cells (`q = 144/18 = 8`). The heterogeneous arm should stay broadband, as it did at 96 and after 24 000
steps.

- **Scaling validated:** homogeneous peak within ±1 unit of 12 (λ = 17–19 cells) with entropy < 1.8.
- **Scaling still wrong:** homogeneous peak outside that band — then the physical mapping is wrong again and the number
  that comes out tells us how.

## 1. Manipulation is connected

Same two arms as everywhere in this line, same seeds, same amplitude (0.5) and correlation length (12 units = 18 cells at
this Δx). The inflow scale is rescaled with the grid so the physical pattern of forcing is unchanged.

## 2. Positive control fires

The **homogeneous arm must pattern**. If it does not, either the run is unstable or the scaling is wrong, and nothing about
the heterogeneous arm can be read. This is exactly the control that caught the last error.

## 3. Readout exists and varies

Seed-averaged spectral shares and entropy, plus β₀ and β₁ as in X60. At 96 the homogeneous arm gives peak share 0.45 and
entropy 1.52; at 128 it gave 0.41 and 1.68 with the wrong physics. Both vary enough to discriminate.

## 4. Sensitivity arithmetic

Five seeds per arm, seed-averaged spectra, no p-values. The discriminator is a **band**: λ within 17–19 cells for the
homogeneous arm. The band is one cell wide either side because the spectrum is binned by mode number (q = 8 gives exactly
18 cells; q = 7 gives 20.6, q = 9 gives 16). A wrong mapping shifts the peak by at least one mode, which is visible.

## 5. Refusal rule

Worthless, not negative, if:

1. any run produces NaN (the stability bound was mis-estimated);
2. the homogeneous arm does not pattern at all;
3. the peak moves between snapshots rather than settling — then there is no wavelength to compare.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid **144**, `dt = 0.5`, 12 000 steps (physical 6000), `Du = 0.36`, `Dv = 0.18`, `F = 0.035`, `k = 0.06`, `beta = 0.2`, `freq_dep = 1`, mutation 0.15 |
| arms | heterogeneous (amp 0.5, correlation 18 cells = 12 units) against homogeneous |
| seeds | 171–175 |
| fields | saved at steps 4000, 8000, 12000 (physical 2000 / 4000 / 6000) |
| criterion | homogeneous λ inside 17–19 cells, entropy < 1.8; heterogeneous broadband |
| cost | ≈ 6 min per run, 10 runs ≈ 60 min |
| artifacts | `morphogenesis/experiments/L1_field/x64_{pattern,homog}_s*.json`, `x64_fields/` |

## Status

- [x] connected (same arms, same seeds; inflow rescaled with Δx)
- [x] positive control fires (homogeneous must pattern; it did at 96 with entropy 1.52)
- [x] readout exists and varies (peak share 0.41–0.45, entropy 1.52–1.68 across grids)
- [x] sensitivity computed (a one-mode band discriminates the mapping)
- [x] refusal rule written (three conditions)
