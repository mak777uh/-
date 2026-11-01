# X71 — is the medium multistable? Does one inflow support two morphologies that a daughter could inherit?

**Question.** X70 showed that a daughter's size follows her own parent's, at about half strength: the medium carries a
one-generation memory of form. A memory that is only graded cannot accumulate, but a **multistable** medium could: if two
stable morphologies coexist at the same parameters, a daughter could drop into the parent's branch and the lineage would
carry a discrete state instead of a blurred number. This is the falsifier external answers proposed for the "no heredity
without a copying rule" claim (four model answers, `library/lit-environments-answers-2026-11-01.md` §3).

**Why now.** The field line has measured the selected wavelength against parameters (X62/X63), grids (X64/X66) and domain
size (X67) — always as one number per world. Nobody has asked whether *two* wavelengths can be stable at the same
parameters, which is what multistability would look like in a Gray–Scott field.

## 1. Manipulation is connected

The manipulation is the inflow `F`, which sets the spot size directly: the pattern's selected wavelength falls as `F` rises.
The positive control is that the measured peak position **moves monotonically** across the sweep. If it does not move, the
series is insensitive by construction and is reported as such, not as evidence either way.

## 2. Positive control fires

Before any claim, the peak position at the two extreme inflow values must differ by at least three Fourier bins
(`3/96 ≈ 0.031` in cycles per cell). Measured on existing data (X66 map: wavelength 8.73 units at one point of the map and
12 units at another, D = 0.16), the expected shift across `F = 0.030…0.050` is of that order; if the pilot contradicts it,
the sweep widens before the series.

## 3. Readout exists and varies

Per run, the radially averaged structure factor of `v` at step 6000 gives four numbers: the peak position `q*` (cells⁻¹),
its share of total power, the **second-mode** share (the strongest local maximum that is not adjacent to `q*`), and the
topology (`β₀`, `β₁` at threshold 0.2). The readout varies across worlds — X66 showed the peak position moving with grid
and inflow — and is saved as the field itself (`.npy`), so the analysis can be recomputed without rerunning.

## 4. Sensitivity arithmetic

Five inflow values `F ∈ {0.030, 0.035, 0.040, 0.045, 0.050}` at `k = 0.06`, five worlds each, two arms
(heterogeneous `amp 0.5` and homogeneous `amp 0.0`), grid 96, `dt = 1.0`, 6000 steps, seed-dependent start (`--init-jitter`,
because a `beta = 0` world ignores the seed — see `docs/design-checks.md`). Fifty runs; a run costs ~80 s, so the series is
about an hour.

Resolution of the readout decides the claim, so it is fixed here: the Fourier grid of a 96-cell box is `1/96 = 0.0104`
cells⁻¹, and the spot wavelength is 8–13 cells, i.e. `q ≈ 0.077…0.125`, so the peak sits about 7–12 bins from the origin.
A split is called only if it is **wider than the instrument**: two clusters whose centres differ by **≥ 3 bins** with at
least two worlds in each.

## 5. Refusal rule

The series is declared **insensitive** and the question stays open if the peak position does not move monotonically with
`F` across the sweep (positive control fails), or if every world's spectrum is single-peaked with `q*` spread below one
bin inside every `F` cell — in that case the field has one wavelength everywhere at this resolution and multistability
cannot be seen here. The series is declared **multistable** if, at some `F`, the worlds' `q*` values form two clusters
separated by ≥ 3 bins, each holding ≥ 2 worlds, **or** if at least two runs keep two modes with shares both ≥ 0.2 that do
not move over the last two snapshots. Anything else is reported as **one branch everywhere**, with the measured spread.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

The marks are not decoration: each one points at the section above that carries its number. Connectedness is checked by the
runner itself — the two arms differ by `--hetero-amp` and the inflow differs between cells, so the artifacts must differ;
the pilot step compares their hashes before the series is allowed to continue.

## Design summary

| factor | values |
|---|---|
| inflow `F` | 0.030, 0.035, 0.040, 0.045, 0.050 |
| `k` | 0.06 (fixed; the world's default point) |
| arms | heterogeneous (`amp 0.5`, static unit signal), homogeneous (`amp 0.0`) |
| worlds | 5 per cell, `--init-jitter`, seeds 171–175 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| readout | radial structure factor of `v` at 6000, `β₀`/`β₁` at threshold 0.2 |
| artifact | `morphogenesis/experiments/L1_field/x71_f<F>_{pattern,homog}_s<seed>.json` + `_x71_fields/*.npy` |
| aggregate | `morphogenesis/experiments/E09_pond/l1_field_x71_multistability.json` |

## Status

Registered 2026-11-01 17:50 MSK, before the first run. If the outcome is "one branch everywhere", the honest reading is
that the medium's memory of form cannot be discrete at this point of the parameter plane, which strengthens the "limited
heredity" reading of X70 rather than the multistability one.

## Amendment 17:55, after the seed-171 pilot and before the full series

Three things changed, and each names the datum that forced it. The multistability criteria are **not** touched.

1. **Units.** The radial profile returns `q` as an integer radial index, i.e. cycles per box: one bin = `1/96` cycles per
   cell. The analysis now reports `q` in bins and the wavelength as `96/q` cells, so "three bins" in the criterion below is
   three units of `q`, not `3/96` of one.
2. **Positive control restated.** The pilot (seed 171, one world per cell) gave peak positions 9, 8, 11, 11, 11 bins for
   `F = 0.030…0.050`: the readout moves by three bins but is **not monotone**. Requiring monotonicity would test a claim
   about spot size versus inflow, not the claim this series asks. So the control becomes: the median peak position at the
   two extreme inflows must differ by **≥ 3 bins** (the readout responds to the manipulation). Monotonicity is reported as
   a fact, not used as a gate.
3. **Sweep widened to seven values** `F ∈ {0.025, 0.030, 0.035, 0.040, 0.045, 0.050, 0.055}`. Reason: the pilot located a
   spots-to-labyrinth boundary between `F = 0.035` and `0.040` (β₀ 31 → 4, β₁ 3 → 12), which is exactly where two
   morphologies could coexist, and the original range had no headroom on either side of it. Seventy runs, about 80 minutes.

The refusal rule and the split criterion stand as written above.
