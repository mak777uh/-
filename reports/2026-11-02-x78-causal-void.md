# X78: the causal test failed on its own manipulation — the "matched scale" arm is not a patterned world at all

**Date:** 2026-11-02, 03:55 MSK. **Experiment:** X78 (impose the second scale instead of finding it).
**Preregistration:** `reports/2026-11-02-x78-causal-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x78_{match,mismatch}_s171-180.json`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x78_causal.json`.

## What was run

Same inflow (`F = 0.040`), same amplitude (0.5), same seeds, ten worlds per arm; the only difference was the prescribed spatial
wavelength of the hetero pattern: **8.7 cells** (supposedly matching the medium's own preferred 8.7) versus **12.0 cells**
(supposedly imposing a second scale).

## Result — one arm degenerates

| arm | components per world | lag-1 / 2 / 3 pairs | ρ₁ / ρ₂ / ρ₃ | λ | half-life |
|---|---|---|---|---|---|
| match (8.7) | **1.0** | 255 / 235 / 215 | 0.212 / 0.228 / 0.224 | 1.028 | not fittable |
| mismatch (12.0) | 6.8 | 1 897 / 1 698 / 1 465 | 0.476 / 0.300 / 0.228 | 0.692 | **1.88** |

The "matched" arm has **one component per world on average** — a world with no pattern to measure. Its lag-1 correlation is 0.21
on 255 pairs, λ > 1 (no decay at all), and no half-life exists. The manipulation did not change *which* scale the world prefers; it
changed the regime, and the comparison the preregistration asked for cannot be made.

The registered rule fires: "void if the two arms' spectra do not differ" was the wrong check — the arms differ enormously — and the
matched cell's lag-1 (0.212) leaves its control band `[0.40, 0.60]`, which the rule also names. **Void.**

## What the surviving arm nevertheless shows

The mismatched arm is an ordinary `F = 0.040` world: 6.8 components, ρ = 0.476 / 0.300 / 0.228, half-life **1.88** against X74's
**1.61** for the same cell. Two independent ten-world-ish samples of the same cell agree within ~15 %, which is a useful
consistency check on the depth measurement itself: the number is reproducible across series.

## Why the design failed, and what would fix it

`--hetero-scale` does not select a wavelength at which the medium patterns; it sets the wavelength of an inflow *modulation*. At
8.7 cells with `amp = 0.5` that modulation destroys the pattern instead of reinforcing it — the world falls to a single component.
To impose a second preferred scale properly one needs a **composite pattern** (two wavelengths in `G`), which the runner does not
support: `hetero-scale` is a single number. That is a code change (a second hetero component, summed before the `F_eff`
multiplication), an anchor, and then the same design.

So the causal test of the two-scale reading is **not done**, and the honest status of that reading stays where §10ey–§10fa left it:
a two-level pattern in the data, three monotone covariates excluded, and a mechanism that is described but not manipulated.

## What this round leaves

- The two-level statement (§10fa) is unchanged and now has a reproducibility check across two series (1.61 vs 1.88 for the same
  cell).
- The causal handle is identified precisely: a composite hetero pattern. That is the next design, and it needs ~40 lines in the
  runner plus an anchor, not a new idea.
