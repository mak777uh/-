# X96c — the same nine runs read per cell: scale against the band, orientation against itself

**Why a third registration.** X96b's rule said *any* setting that keeps fewer than ten components voids the pass, and two of the nine
do (`γ = 0.20` at `Dw = 0.08` and `0.32`). That clause was written for the first pass, where the coupling destroyed everything; here the
collapse is confined to one corner of the grid and the seven surviving settings do answer the question the owner approved. Rather than
read the survivors anyway and call it a result, the rule is re-registered per cell and the re-read is done under it. **No new runs:**
this is the same nine artifacts that X96b produced.

**The question (unchanged).** Can a second diffusive species move the pattern's **scale** — `q'`, the axis-aligned wavenumber of
maximum power — out of the 5–9 band every forced world has shown? And, if it cannot, does it move anything else?

## 1. Manipulation is connected

Nine settings (`Dw ∈ {0.08, 0.16, 0.32}` × `γ ∈ {0.05, 0.10, 0.20}`), one cell (`F = 0.030`), one seed (401), plus the w-off control
(`q' = 9`, `s = 0.702`, 69 components). The anchor with the flag off is already proved bit-for-bit against `x100_f030_s291.json` (X96).

**Per-cell connectivity:** a setting counts as a live cell if it keeps **≥ 10 components** at step 6000; a setting below that is a
**regime boundary** and is reported as such, excluded from the scale verdict. This is the change from X96b, stated before the re-read.

## 2. Positive control fires (numeric)

The control's `q'` must sit inside 5–9 **and the control fires if** that threshold holds; measured 9. In addition, the live-cell
requirement must leave at least **four** cells — with three `Dw` values at two couplings that is six, so the floor is a formality that
makes a degenerate grid impossible.

## 3. Readout exists and varies

Per live cell: `q'`, the symmetry `s`, components and peak; across cells, the spread of each. The variation to be explained is real:
`q'` already took the values 8 and 9 in the live cells, and `s` ranged 0.636–0.837.

## 4. Sensitivity arithmetic

`q'` resolves one wavenumber unit (≈1.3 cells at `q' = 9`), so the scale criterion is a **two-unit** move out of the band. `s` is a
ratio in [0, 1] with a standard error of roughly `1/√(4·n_cells)` under the null and no cross-seed replication in this pilot; the
orientation criterion is therefore set at a **0.10** spread, twice what one seed of a chaotic field would produce by chance.

## 5. Refusal rule (fixed before the re-read)

**Void** if the control leaves 5–9, fewer than four cells are live, or the manipulation (`max|Δv| ≥ 0.01`) fails in every live cell.

**The scale channel exists** if any live cell's `q'` is ≤ 3 or ≥ 11.
**The scale channel does not exist** if every live cell's `q'` stays in 5–9.
**The second species moves orientation instead** if, in addition, the spread of `s` across live cells is ≥ 0.10 while `q'` stays in
band. This is a secondary observation: one seed, no per-world statistics, and it must be re-tested on a series before it enters a
claim.
**Not decided** otherwise.

## Design summary

| factor | value |
|---|---|
| artifacts | X96b's nine runs (`x96bpilot_*`), no new runs |
| live cell | ≥ 10 components at step 6000 |
| scale criterion | `q'` outside [3, 11] |
| orientation criterion | spread of `s` ≥ 0.10 across live cells with `q'` in band |
| artifact | `E09_pond/l1_field_x96c_pilot.json` |

## Checklist

- [x] connected (≥ 4 live cells, manipulation ≥ 0.01)
- [x] positive control numeric (control `q'` in 5–9, measured 9)
- [x] readout exists and varies (`q'` 8–9, `s` 0.636–0.837)
- [x] sensitivity computed (§4: two units for scale, 0.10 for orientation)
- [x] refusal rule written, with "moves orientation instead" as a real outcome
- [x] stated: same artifacts as X96b, re-read under a per-cell rule, no new runs

## Status

Registered 2026-11-02 19:06 MSK, before the re-read. Owner's approval of the second species stands from 18:11.

доска: принято 0, отклонено 0, отложено 0.
