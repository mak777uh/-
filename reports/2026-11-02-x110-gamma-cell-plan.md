# X110 — how close to the edge does each cell sit? `γ_cell` by bisection

**Why.** X96d found something that is not about the second species at all: at the same 5 % cut in the autocatalysis (`γ = 0.05`,
`Dw = 0.64`), the lattice cell keeps all four diffusion lengths live in all three seeds, while the maze cell keeps **three, two and
one**. The percolating cell lives nearer the boundary of existence, and that boundary is measurable: the coupling at which a cell stops
being a pattern at all.

**The question.** What is `γ_cell` — the largest autocatalysis cut at which a cell still carries a pattern — for `F = 0.030` and
`F = 0.040`? This is the first quantity in the line that measures a cell's *distance from the edge* rather than a property inside it,
and it matters for the life question directly: a medium close to its own edge cannot absorb much of anything.

## 1. Manipulation is connected

Bisection on `γ` at fixed `Dw = 0.16`: `γ ∈ {0.10, 0.15, 0.20, 0.30, 0.50}`, three seeds (421–423) per cell, two inflows — **thirty
runs**, ~80 s each. The third field is on in every run (`--second-species --Dw 0.16`), so the manipulation is the coupling itself; the
`w`-off controls are X96d's six runs at the same seeds and inflows, which already give `q' = 9` (lattice) and `7` (maze) with 69 and
96 components.

Connectedness: the controls must be live (≥ 10 components) and their `q'` inside 5–9 — both already measured, so the anchor for this
series is an existing artifact, not a guess.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The weakest coupling stays alive:** at `γ = 0.10` **all six** runs must keep ≥ 10 components. X96d showed the maze survives at
   0.05, and X96b's first pass showed it dies at 0.20 in two of three diffusion lengths; if even 0.10 kills the maze, the bracket is
   lower and the series reports that instead of a boundary.
2. **The strongest coupling kills:** at `γ = 0.50` **no** run may keep ≥ 10 components (X96's first pass: every coupling ≥ 0.5 gave
   1 or 0 components). A series where 0.50 lives would say the collapse is not monotone in `γ` and the bisection is invalid.

## 3. Readout exists and varies

Per (cell, seed, γ): components and peak at step 6000, `q'` for the live ones. The readout spans the whole range by construction —
X96 gave 69 components at `γ = 0`, 4–18 at `0.20`, 0–1 at `0.50`.

## 4. Sensitivity arithmetic

The readout is a count of components at one snapshot with a hard floor of 10, so the resolution is the **bisection grid**: with
`γ ∈ {0.10, 0.15, 0.20, 0.30, 0.50}` the boundary is located to within a factor between consecutive points (1.5×–1.7×). Three seeds per
point mean the reported `γ_cell` is a **bracket** — the largest `γ` alive in at least two of three seeds — not a point estimate, and the
report says so.

## 5. Refusal rule (fixed before the run)

**Void** if a control's `q'` leaves 5–9, if `γ = 0.10` kills the field in any cell, or if `γ = 0.50` leaves a pattern anywhere.

**The cells differ in their distance to the edge** if the maze's `γ_cell` is below the lattice's by at least one bisection step (1.5×).
**The cells do not differ** if both brackets overlap.
**Not decided** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| runs | 30 (2 cells × 3 seeds × 5 couplings), `Dw = 0.16`, `γ` varied |
| readout | components at step 6000 (floor 10), `q'` for live runs |
| controls | `γ = 0.10` alive everywhere; `γ = 0.50` dead everywhere; X96d's w-off runs as the zero-coupling reference |
| artifact | `E09_pond/l1_field_x110_gamma_cell.json` |

## Checklist

- [x] connected (controls live, `q'` in band, 30 runs)
- [x] positive control numeric (`γ = 0.10` alive in 6/6, `γ = 0.50` dead in 30/30)
- [x] readout exists and varies (69 → 4 → 0 components across the range)
- [x] sensitivity computed (§4: bracket, one bisection step ≈ 1.5×)
- [x] refusal rule written, with "the cells do not differ" as a real outcome
- [x] stated: `γ_cell` is a bracket from a count, not a calibrated constant

## Status

Registered 2026-11-02 20:26 MSK, before the series. Owner's approval of the second species stands from 18:11.

доска: принято 0, отклонено 0, отложено 0.
