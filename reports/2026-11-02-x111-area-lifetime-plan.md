# X111 — does the sign of the size–lifetime relation survive a nine-times finer lifetime?

**Why.** X92 established that "bigger is fitter" is not a safe prior in this medium: `ρ(peak area, lifetime)` is `+0.191` and `+0.067`
at `F = 0.025 / 0.030` but `−0.041` and `−0.046` at `0.035 / 0.040`, with a shuffle null of 0.031–0.039. That measurement is built on
lifetimes quantised by the **50-step** logging interval: a structure whose true life is 60 steps and one whose true life is 110 both
report 50. X105 then showed the same logging interval was hiding a third of the maze cell's genealogies, and its dense series measures
lifetime in **10-step** units instead.

A sign that flips between inflows is a fragile object. This analysis asks whether the flip survives the finer measurement, on the two
cells the dense series covers.

## 1. Manipulation is connected

Two series of the same design at different logging densities: `x100` (seeds 291–300, `--sample-every 50`) and `x108` (seeds 301–310,
`--sample-every 10`, otherwise identical), both at `F = 0.030` and `0.040`. Per structure (uid): peak area (the largest logged area),
lifetime (last logged step minus first logged step), and the first appearance step. Nothing is computed from fields.

Connectedness: at least **300 uids** per cell with a measurable lifetime in both series (X92 used 2 486–3 932 across four cells), and
the density ratio must be visible: median lifetime must differ between the series by roughly the factor of five the logging implies.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The sparse series must reproduce X92 within 0.05**: `ρ ≈ +0.191` at 0.030 and `≈ −0.041` at 0.040 on seeds 291–300, and the control
   **fires if** both land inside that band. If the sparse recomputation drifts, the definition has changed and the comparison is void.
2. **The shuffle null must stay small**: 1 000 within-world permutations give a 95th percentile of `|ρ|`; if the null's 95th percentile
   exceeds 0.15 in either series, the readout is too coarse to call a sign.

## 3. Readout exists and varies

Per cell and series: `ρ(peak area, lifetime)`, the same with a partial control for first-appearance step (age), the median lifetime,
the number of uids, and the shuffle null. Variation exists by construction: X92's coefficients span 0.24 across inflows, and the
lifetime distributions of the two series differ by a factor of five in quantisation.

## 4. Sensitivity arithmetic

With 300–3 900 uids the standard error of a coefficient is 0.016–0.058, and the shuffle null gives the empirical resolution directly:
X92 measured it at 0.031–0.039. The declared resolution for a difference between the two series is **0.10**, which is about three
null widths; anything smaller is called "no difference".

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 uids in either series, the sparse control misses its ±0.05 band, or a null's 95th percentile
exceeds 0.15.

**The sign is a property of the medium** if the dense series reproduces the sparse sign in both cells and `|Δρ| ≤ 0.10`.
**The flip is a resolution artefact** if the dense series gives the same sign in both cells where the sparse series gave opposite signs.
**The sign changes with resolution** if the dense coefficients keep opposite signs but `|Δρ| ≥ 0.15` in either cell — then X92's numbers
are quoted with their logging density.
**Mixed** otherwise, printed per cell and series.

## Design summary

| factor | value |
|---|---|
| artifacts | `x100` (seeds 291–300) and `x108` (seeds 301–310), cells 0.030 / 0.040 |
| readouts | `ρ(peak area, lifetime)`, partial on age, median lifetime, shuffle null |
| controls | sparse series reproduces X92 ±0.05; null 95th percentile ≤ 0.15 |
| artifact | `E09_pond/l1_field_x111_area_lifetime_dense.json` |

## Checklist

- [x] connected (300 uids per cell, median lifetime differs by the logging factor)
- [x] positive control numeric (X92 reproduced ±0.05; null ≤ 0.15)
- [x] readout exists and varies (X92 spans 0.24 across inflows)
- [x] sensitivity computed (§4: SE 0.016–0.058, resolution 0.10)
- [x] refusal rule written, with "the flip is a resolution artefact" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 20:35 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
