# X111b — the same comparison with the reference cells named correctly

**Why this is a re-registration and not a rescue.** X111 voided on its own control: it required the sparse series to reproduce
`+0.191` at `F = 0.030` and `−0.041` at `0.040`, and the recomputation gave `+0.077` and `+0.021` on the `x100` series. The cause is a
transcription error in **this line's own plan**, not in the data: X92's corrected table (CLAIMS row 312) reads
**+0.191 / +0.067 / −0.041 / −0.046** for the cells **0.025 / 0.030 / 0.035 / 0.040**, and X111 took the 0.025 and 0.035 values for the
0.030 and 0.040 cells. Recomputing on X92's own series with the same code gives **+0.069** and **−0.042** — i.e. X92's `+0.067` and
`−0.046` to within 0.004.

So the code is right and the plan's reference was wrong. The corrected registration below names the references by cell.

## 1. Manipulation is connected

The same two series and cells as X111: `x100` (seeds 291–300, 50-step logging) and `x108` (seeds 301–310, 10-step logging), `F = 0.030`
and `0.040`, `uid_outcomes` fields (`peak`, `first`, `last`), lifetime `last − first + 1` — X92's own definitions. Connectedness: at
least 300 uids per cell and series, and median lifetime must differ between the series by the factor the logging implies.

**Stated up front, because X111's void made it plain:** the two series are **different worlds**, not the same worlds measured twice.
`--sample-every` is a physical parameter (the X85 rule), so no sparse twin of the dense worlds exists. This analysis therefore compares
two samples of the same design at two densities; it cannot separate a density effect from a sample effect, and the report says which
comparisons that leaves open.

## 2. Positive control fires (numeric)

**The reference is now per cell:** on X92's own series (`x85`+`x87` for 0.030, `x88` for 0.040) the recomputation must land within
**0.05** of **+0.067** and **−0.046** respectively, and the control **fires if** both hold. Plus the shuffle null: 1 000 within-cell
permutations must give a 95th percentile **≤ 0.15** in all four cell × series combinations.

## 3. Readout exists and varies

Per cell and series: `ρ(peak area, lifetime)`, the shuffle null, the uid count and the median lifetime. Variation exists: X92's own
values span 0.24 across cells and the two series' medians differ by a factor of 3.5.

## 4. Sensitivity arithmetic

1 800–4 900 uids, so the standard error of a coefficient is 0.014–0.023; the shuffle nulls sit at 0.03–0.06. The declared resolution for
a difference between the two series is **0.10** — twice the largest null and about five standard errors.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 uids in either series, if the per-cell control misses its ±0.05 band, or if a null exceeds 0.15.

**The sign is stable across densities** if both cells keep X92's sign in the dense series and `|Δρ| ≤ 0.10`.
**The sign is set by the sample, not the density** if the dense signs differ from the sparse ones but the magnitudes stay inside the
nulls — the comparison cannot then attribute the difference to anything.
**The sign moves with density** if `|Δρ| ≥ 0.15` in either cell while both series are above their nulls.
**Mixed** otherwise, per cell.

## Design summary

| factor | value |
|---|---|
| artifacts | `x100` (seeds 291–300) vs `x108` (seeds 301–310); reference recomputed on `x85`+`x87` / `x88` |
| readouts | `ρ(peak area, lifetime)` per cell and series, shuffle null, medians |
| controls | X92's per-cell values reproduced within 0.05; nulls ≤ 0.15 |
| artifact | `E09_pond/l1_field_x111b_area_lifetime.json` |

## Checklist

- [x] connected (300 uids, medians differ by the logging factor)
- [x] positive control numeric (per-cell references +0.067 / −0.046 within ±0.05; nulls ≤ 0.15)
- [x] readout exists and varies (0.24 span across cells, medians differ 3.5×)
- [x] sensitivity computed (§4: SE 0.014–0.023, nulls 0.03–0.06, resolution 0.10)
- [x] refusal rule written, with "the sign is set by the sample" as a real outcome
- [x] stated: different worlds, not one sample at two densities

## Status

Registered 2026-11-02 20:37 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
