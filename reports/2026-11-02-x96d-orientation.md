# X96d — the orientation effect does not replicate, so the second species moves neither scale nor orientation

**Plan:** [`2026-11-02-x96d-orientation-plan.md`](2026-11-02-x96d-orientation-plan.md) (19:36).
**Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x96d_orientation.json`. Thirty runs (three seeds × two inflows × four `Dw`
plus a control per seed and inflow), `γ = 0.05`, ~80–110 s each.

## Registered verdict

> **the orientation effect does not replicate**: only 2 of 6 cells reach `|ρ| ≥ 0.8` (coefficients −0.4, +0.8, +0.4, +1.0, —, —).

The criterion was four of six cells agreeing in sign at `|ρ(Dw, s)| ≥ 0.8`. Two cells reached the bar and **they disagree in sign**:
−0.4 and +0.8 in the lattice, +1.0 in the maze (on three live diffusion lengths). X96c's one-seed spread of 0.636–0.837 was, as its
own plan said it might be, a property of one seed.

## What the series shows

| cell | control `q'` | live `Dw` (of 4) | `q'` at `Dw = 0.64` | `ρ(Dw, s)` |
|---|---|---|---|---|
| 0.030 seed 411 | 9 | 4 | 8 | −0.4 |
| 0.030 seed 412 | 9 | 4 | 8 | **+0.8** |
| 0.030 seed 413 | 9 | 4 | 8 | +0.4 |
| 0.040 seed 411 | 7 | 3 | 7 | **+1.0** |
| 0.040 seed 412 | 7 | 2 | 7 | — |
| 0.040 seed 413 | 7 | 1 | 8 | — |

Three things stand out, and the second is the one worth keeping:

1. **No scale move at all.** `q'` sits at 8–9 in every live lattice setting and at 7–8 in the maze, with `Dw` pushed to eight times
   `Dv`. The registered scale criterion (two units out of 3–11) never came close; the largest change anywhere is one unit.
2. **The maze cell is fragile.** At `γ = 0.05` — a 5 % cut in the autocatalysis inside a structure — the lattice cell keeps all four
   diffusion lengths live in all three seeds, while the maze cell loses half to three quarters of them (3, 2 and 1 live settings out of
   four). The percolating cell lives closer to the edge of the medium's existence, and a perturbation the lattice absorbs intact
   destroys it.
3. **Orientation is not a channel either.** With three seeds per cell the spread collapses to noise: the two cells that reach `|ρ| ≥ 0.8`
   point in opposite directions.

## Reading

The second diffusive species — the one mechanism that *should* set a Turing wavelength — moves **neither** the scale **nor** the
orientation of this medium, and it destabilises the cell where the medium is weakest. That closes the last untried channel for scale
with a measured negative, and it closes X96c's one-seed positive at the same time.

The line's statement about scale now has four measured negatives behind it: inflow changes morphology and memory but not the period
(X84, X99); the initial condition is closed (X96b); a second diffusion length is closed (this series); and a spatially varying inflow
sets orientation rather than wavelength (X52). **Wavelength is pinned by the reaction band `(F, k)` and the grid** — the remaining
candidate, and the one every negative is consistent with.

The fragility finding is a condition-of-life statement in its own right: the same perturbation that a lattice cell shrugs off takes the
percolating cell apart, so "how close to the edge a medium sits" is measurable as `γ_cell` — the coupling at which a cell stops being a
pattern at all. For the maze that threshold is between 0.05 and 0.10 in this parameterisation.

## Caveats

- One box, one grid, one `k`, one `γ`; `Dw` is the only varied axis, and four points per cell limit the coefficient to a rank statistic
  on four values.
- The maze cells with two or three live `Dw` values give a coefficient on 2–3 points (or none), which is why the criterion demanded
  agreement across cells rather than any single coefficient.
- The controls are healthy (all six `q'` inside 5–9) and the manipulation fires in every live cell, so the negative is not a failure of
  the readout.
- `γ_cell` is a descriptive name for the collapse boundary, not a calibrated constant: the maze collapse was observed at 0.05 and the
  lattice survived 0.20 in X96b's first pass — the two cells differ by at least a factor of four in tolerance.

## Next

- **X110 (registered, analysis):** measure `γ_cell` properly for both cells — a bisection on `γ` at `Dw = 0.16` with three seeds, ten
  runs, to put a number on "how close to the edge" each cell lives. This is the first quantity in the line that measures proximity to
  the boundary of existence rather than a property inside it.
- The scale question is closed; the queue's remaining field-line items are the specificity at a second cut (needs runs across
  thresholds) and X97 (siblings, second generation).

доска: принято 0, отклонено 0, отложено 0.

## Addendum (02.11, 20:52) — the fragility belongs to Dw, not to γ

X110b measured the coupling ceiling at a fixed short second length (Dw = 0.16) and found **γ_cell = 0.30 in both cells**, identical
under three liveness thresholds. So the sentence above — that the percolating cell lives closer to the edge of existence — is wrong as
written: at γ = 0.05 the maze lost its diffusion lengths because they were **long** (0.32 and 0.64), not because the coupling alone
broke it. The correct statement is narrower: *the maze cell tolerates a long-range inhibitor less*, while both cells survive the same
autocatalytic cut of a short-range one.

The correction is appended, not substituted; the paragraph above stays as written so the road is visible.

доска: принято 0, отклонено 0, отложено 0.
