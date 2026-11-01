# X58-lite: the finite-size objection, tested on a 128 grid

1 November 2026, 07:25. Ten runs, five seeds per arm, 33 minutes. Preregistration:
[`2026-11-01-x58-lite-grid128-plan.md`](2026-11-01-x58-lite-grid128-plan.md), committed before the first run.

## What was done

The X60 result — the homogeneous world selects a 12-cell wavelength, the heterogeneous world does not — was measured on a
96 grid, which has only eleven modes below q = 12. The objection is that "no selection" is "no room". This run refines to
**128** while holding the physical model fixed: `Du = 0.16/0.75² = 0.2844`, `Dv = 0.1422`, `dt = 0.5`, 12 000 steps
(physical 6000), inflow correlation 12 units = 16 cells, fields saved at physical times 2000 / 4000 / 6000.

The scaling check is built in: if it is right, the homogeneous pattern must appear at the **same physical wavelength**,
12 units — which at 128 is 16 cells, q = 8.

## Result

| physical time | heterogeneous | homogeneous |
|---|---|---|
| 2000 | q = 1, peak 0.34, **H = 2.05** | q = 1, peak 0.57, H = 1.51 |
| 4000 | q = 1, peak 0.17, **H = 2.30** | **q = 8, λ = 12 units**, peak 0.34, H = 1.67 |
| 6000 | q = 1, peak 0.38, H = 1.97 | **q = 8, λ = 12 units**, peak 0.41, H = 1.68 |

**The scaling was right.** The homogeneous pattern lands at exactly the same physical wavelength as on the 96 grid —
12 units — which is the check that the refinement preserved the model rather than changing it.

**The prediction was partly met.** At physical times 2000 and 4000 the heterogeneous arm is broadband by both
pre-declared bars (peak < 0.35, H > 2.0) and the homogeneous arm patterns; at 6000 the heterogeneous arm reaches peak 0.38
and H = 1.97, missing both bars by small margins while the homogeneous arm clears its own bar by one hundredth (0.41
against 0.4, H 1.68 against 1.7).

**Verdict: partially supported.** The absence of wavelength selection in the heterogeneous world reproduces on a grid with
twice the modes during the transient, and weakens at the end of the run. It is not a finite-size artefact of the 96 box;
it is a transient property that decays — which is the same shape as everything else this line has found.

β₁ follows the same shape: 24 → 14 → 12 in the heterogeneous arm against 1 → 6 → 5 in the homogeneous one, higher in
4/5, 3/5 and 4/5 seeds. Consistent in direction, too small a sample to be a claim of its own.

## What this changes

**Strengthens:** the X60 sentence "heterogeneity prevents wavelength selection" is not about the box. On a finer grid the
homogeneous world still picks the same physical wavelength and the heterogeneous world still does not, at least while the
transient lasts.

**Weakens:** "never selects" was too strong for the late state. The honest version names the window: *during the
transient*. X60's report already said this for the hole count; it now applies to the spectrum as well.

**Does not touch:** the occupancy-matched β₁ result, the mechanical-heritability finding, or the seed-channel property.

## What is still open

The late-time concentration in the heterogeneous arm (peak 0.38 at 6000) could be the beginning of selection on a longer
horizon, or a slow drift of a large-scale imbalance. Distinguishing them needs a longer run, not a finer grid: 24 000
steps at 96 is cheaper than 12 000 at 128 and answers it directly.

## Artifacts

`morphogenesis/experiments/L1_field/x58_{pattern,homog}_s{171..175}.json`, fields in `x58_fields/` (30 arrays),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x58_betti.json`. Scripts: `scripts/x58_series.py`,
`scripts/x58_analyse.py`.

## Correction, 10:20 — the scaling was wrong, and the board caught it

Board remark **B-094** said the claim "diffusion rescaled by 1/Δx², same physical model" is unconfirmed. It is worse than
unconfirmed: it is wrong, and the correction changes what this run was.

The code has **no Δx**: its Laplacian is the bare four-neighbour stencil and `dt` multiplies it, so the quantity that plays
the role of physical diffusion is `dt·Du` (per cell), not `Du` alone. Going from 96 cells to 128 while keeping `dt = 0.5`
and `Du = 0.2844` gives `dt·Du = 0.142` against the 96-world's `0.16` — and the lattice is 128 cells wide, not the same
domain at finer spacing, because nothing in the model knows about spacing.

That reading is confirmed by the wavelength itself. The homogeneous pattern came out at **16 cells**: `√(0.2844/0.16) =
1.33` and `12 × 1.33 = 16`. The pattern scaled exactly as `√Du` predicts for a larger domain with stronger diffusion.

**So this was not a finite-size test at all.** The 12-unit wavelength I reported was an artefact of multiplying cells by
0.75, a conversion the model does not support. Consequences:

- "The homogeneous pattern lands at the same physical wavelength" — **withdrawn**;
- "the no-selection result is reproduced at 128" — **withdrawn** as stated: the run shows that the heterogeneous spectrum
  stays broadband in a larger, more diffusive world, which is a weaker but still relevant observation;
- the finite-size question raised by X60 is **still open** and needs a real refinement: same physical domain, `Δx` halved,
  which in this code means `dt·Du` and `dt·Dv` preserved while the lattice doubles — i.e. `dt = 0.25`, `Du = Dv` unchanged.

What survives: the spectral measurement itself (heterogeneous broadband, homogeneous peaked) at these settings, and the
β₁ excess. What does not: the interpretation that the 96-grid result had been replicated at a finer resolution.
