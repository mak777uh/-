# X96d — does the second species really move the orientation? A three-seed, two-cell series

**Why.** X96c, on one seed and one cell, found the only positive result of the second-species work: at couplings the medium can absorb
(`γ = 0.05–0.10`) the pattern's wavenumber stayed at 8–9 — inside the 5–9 band — while its **symmetry** spanned 0.636–0.837. That is a
single number per setting from a chaotic field, so it is a direction, not a result. This series tests it with replication.

**The question.** Within one inflow and one seed, does the orientation `s` depend on the inhibitor's diffusion length in a consistent
direction — and does `q'` ever move two units (the scale criterion) when `Dw` is pushed to `0.64`, four times further than the pilot?

## 1. Manipulation is connected

`γ = 0.05` fixed (the coupling the pilot showed harmless: a 5 % cut in the autocatalysis inside a structure), `Dw ∈ {0.08, 0.16, 0.32,
0.64}`, seeds **411–413**, inflows **0.030 and 0.040** — twenty-four runs with the third field, plus the **w-off control for every seed
and inflow** (six runs): **thirty runs**, ~100 s each on the GPU lane, about 50 minutes.

Connectedness: every w-on run must keep **≥ 10 components** at step 6000, and `max|Δv|` against its own seed's control must be
`≥ 0.01`. A run that collapses is a regime boundary at that corner and is reported as such for its cell, not used in the statistics.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The medium's own reading:** for each of the six seed × inflow controls, `q'` must sit inside **5 ≤ q' ≤ 9** and the control
   **fires if** that threshold holds in all six. A control outside the band makes that cell unreadable.
2. **The heredity-independent check that the field is a pattern:** the control keeps ≥ 10 components at 6000 in all six — the pilot's
   controls had 69.

## 3. Readout exists and varies

Per (seed, inflow): `q'` and `s` at `Dw = 0.08 … 0.64`, so each cell yields a Spearman coefficient between `Dw` and `s` (four points)
and between `Dw` and `q'`. Variation exists by construction: the pilot's `s` spanned 0.636–0.837 across three diffusion lengths, so the
spread to be replicated is about 0.20 and the resolution is 0.10.

## 4. Sensitivity arithmetic

Six cells (3 seeds × 2 inflows) give six independent Spearman coefficients on four points each. Under the null, a coefficient of
±0.8 or beyond has probability 1/12 per cell, so **four of six cells agreeing in sign at |ρ| ≥ 0.8** has a null probability below
0.001. That is the orientation criterion. For the scale: `q'` must move **two units** (outside 3–11) at `Dw = 0.64` in at least
**three of six** cells — the pilot already showed one unit is reachable at the death boundary, so two units in half the cells is the
conservative bar.

## 5. Refusal rule (fixed before the run)

**Void** if fewer than four cells have a live control, if any control's `q'` leaves 5–9, or if fewer than twenty w-on runs keep ≥ 10
components.

**The orientation effect replicates** if at least **four of six** cells give `ρ(Dw, s)` with the **same sign** and `|ρ| ≥ 0.8`.
**The orientation effect does not replicate** if at most two cells reach that bar, or if the signs split evenly.
**The scale channel opens** if `q'` leaves 3–11 at `Dw = 0.64` in at least three cells.
**Mixed** otherwise, printed cell by cell — and if the two inflows disagree, the claim is stated for the cell where the effect appears.

## Design summary

| factor | value |
|---|---|
| runs | 30 (24 w-on + 6 controls), seeds 411–413, `F = 0.030 / 0.040`, ~100 s each |
| rule | `u·v²/(1+γw)`, `dw/dt = Dw∇²w + 0.05(v − w)`, `w(0) = v(0)`, `γ = 0.05` |
| readouts | `ρ(Dw, s)` and `ρ(Dw, q')` per cell; `q'` at `Dw = 0.64` against the band |
| artifact | `E09_pond/l1_field_x96d_orientation.json` |

## Checklist

- [x] connected (30 runs; ≥ 10 components; `max|Δv| ≥ 0.01` per seed)
- [x] positive control numeric (six controls' `q'` in 5–9, fires if all six hold)
- [x] readout exists and varies (pilot spread 0.20, resolution 0.10)
- [x] sensitivity computed (§4: 4/6 cells at |ρ| ≥ 0.8, null < 0.001)
- [x] refusal rule written, with "does not replicate" as a real outcome
- [x] stated: `γ` fixed by the pilot; `Dw` extended to 0.64

## Status

Registered 2026-11-02 19:36 MSK, before the series. Owner's approval of the second species stands from 18:11.

доска: принято 0, отклонено 0, отложено 0.
