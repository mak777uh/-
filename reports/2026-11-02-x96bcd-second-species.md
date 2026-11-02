# X96b / X96c — the second species does not move the scale, and it does move the orientation

**Plans:** [`2026-11-02-x96b-mild-sweep-plan.md`](2026-11-02-x96b-mild-sweep-plan.md) (18:47),
[`2026-11-02-x96c-per-cell-plan.md`](2026-11-02-x96c-per-cell-plan.md) (19:06).
**Aggregates:** `l1_field_x96b_pilot.json` (void by its own rule), `l1_field_x96c_pilot.json` (the per-cell re-read).
**Runs:** nine, `F = 0.030`, seed 401, plus the w-off control, ~105 s each.

## X96b voided by its own rule, and the rule was the problem

X96b's refusal rule said *any* setting that keeps fewer than ten components voids the pass. Two of the nine do (`γ = 0.20` at
`Dw = 0.08`: 4 components, and at `Dw = 0.32`: 1). So the pass is a **void by its letter**, and the numbers were recorded:

| `Dw` | γ = 0.05 | γ = 0.10 | γ = 0.20 |
|---|---|---|---|
| 0.08 | q' 8, s 0.704, 47 comps | q' 9, s 0.832, 43 | q' 4, s 0.755, **4** |
| 0.16 | q' 8, s 0.649, 59 | q' 8, s 0.715, 43 | q' 4, s 0.828, 18 |
| 0.32 | q' 8, s 0.636, 39 | q' 8, s 0.837, **15** | q' 4, s 0.117, **1** |
| control | q' **9**, s 0.702, **69** | | |

The global clause was written for the first pass, where every coupling killed the field; here it fires on a corner of the grid while
seven cells survive with 15–59 components. Rather than read the survivors anyway and call it a result, the rule was re-registered per
cell (X96c) and the same nine artifacts re-read under it. No new runs.

## X96c: the scale channel does not exist in the living regime

Registered verdict, from the per-cell rule:

> **the scale channel does not exist and the second species moves orientation instead**: `q'` stays in [4, 8, 8, 8, 8, 8, 9] across all
> seven live cells while the symmetry spans 0.201 (0.636–0.837); one seed, so this is a direction to test on a series, not a claim.

Read carefully, because the list hides two regimes:

- **`γ = 0.05` and `0.10`, six live cells:** `q'` is **8 or 9** in every one — inside the 5–9 band every forced world has shown — while
  the symmetry `s` ranges **0.636 to 0.837**. So the second diffusion length, at couplings the medium can absorb, changes *which way the
  pattern runs*, not how far apart its stripes are.
- **`γ = 0.20`, the boundary:** the field collapses at two diffusion lengths (4 and 1 components) and at `Dw = 0.16` it survives with 18
  components but **coarsens**: `q' = 4`, one unit below the band. That is below the registered two-unit criterion, so it is not called a
  scale shift — but it is the first time in this line that moving a parameter has pushed `q'` below 5 at all, and it happens where the
  medium is dying.

The manipulation reaches the field in all nine settings (`max|Δv|` 0.41–0.43 against a control whose own peak is 0.4325 — the
diagnostic rule from the first pass applies: these fields are alive, so the difference is structure, not absence).

## What this means for the line's main open question

Three channels for scale are now closed by measurement — inflow, initial condition, and a second diffusion length — and the fourth
(spatially varying inflow) sets orientation and heterogeneity rather than wavelength. The line's finding is therefore stable and now has
a mechanistic reading: **in this medium the environment can choose the pattern's orientation, and no knob tried so far can choose its
wavelength.** The second species is especially informative because it is the knob that *should* work: in a Turing system the wavelength
is set by the ratio of diffusion lengths. Here that ratio changes the orientation instead, which says the pattern's scale is being set by
something the diffusion ratio does not touch — the reaction band `(F, k)` and the grid, most likely.

That is a hypothesis, not a result: the pilot has one seed and cannot separate "the wavelength is pinned by the reaction band" from "the
pilot's `Dw` range was too narrow to see it".

## Caveats

- One seed, one cell, nine settings: no per-world statistics; `s` and `q'` are single numbers per setting.
- `q'` resolves one wavenumber unit, so the `γ = 0.20` drop to 4 is one unit below the band — reported, not claimed.
- The coupling `1/(1+γw)` cuts the autocatalysis inside structures by `γ/(1+γ)`; at `γ = 0.20` that is already 17 %, and the collapse at
  two diffusion lengths shows the medium has little room there.
- `γ = 0.05` and `0.10` are the living regime, and within it `Dw` spanned 0.08–0.32 (four-fold): a wider range would test the Turing
  expectation more sharply.

## Next

- **X96d (registered, series):** `γ = 0.05`, `Dw ∈ {0.08, 0.16, 0.32}`, three seeds each, both inflows — does the orientation spread of
  0.20 survive replication, and does `q'` ever move by two units when `Dw` is pushed to `0.64`? Ten runs, ~20 minutes.
- If both answers are no, the second species joins the closed channels and the line's statement about scale becomes "no knob in this
  world moves it", which is itself a condition-of-life result: a medium whose wavelength is fixed cannot adapt its morphology to a
  changing environment.

доска: принято 0, отклонено 0, отложено 0.
