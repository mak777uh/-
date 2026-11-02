# X103d — the confound made explicit: mother's peak or *any* peak?

**Why this is not another forking path.** X103c's registered verdict came out **mixed**, as written: at `F = 0.030` the birth
distance carries nothing (`ρ = −0.008`, 7/10 worlds negative, per-world magnitudes ≤ 0.22), at `F = 0.040` it carries a strong
negative (`ρ = −0.367`, **10/10 worlds negative**, per-world −0.21 … −0.45). Two explanations survive, and X103c could not separate
them:

- **maternal** — a daughter born farther from her mother's peak inherits a narrower excursion, because the mother's own excursion
  decays with distance from her peak;
- **local geometry** — in the maze cell the distance from a peak is nearly the same coordinate as "half-width of the lattice arm",
  so *any* near peak would do; the reading is about the medium's local structure, not about the mother.

Denser logging (X105) does **not** separate them: it removes the 35 % structural loss, not the confound. The discriminator is a
null readout that the stored logs already support: the distance to the nearest **non-ancestor** peak at the daughter's birth step.
If stranger peaks predict her size as well as her mother's, the term is local geometry; if her mother's does clearly better, it is
maternal.

## 1. Manipulation is connected

Same pairs and worlds as X103c (X100's runs). For each daughter: her birth centroid and birth step, her mother's peak centroid,
and the nearest peak among the components present at her birth step that are **not her ancestors** (the mother is excluded, and so
is every uid reachable upward in `uid_pairs`, so the control cannot accidentally be a grandmother). Torus distances, cells.
Connectedness: at least **100 usable contrast pairs** per cell (pairs where a non-ancestor peak exists at the birth step) and
coverage among loggable pairs at least **0.60** — this control needs one more thing from the logs (another component in the same
frame), so its denominator is stated as before.

## 2. Positive control fires (numeric)

`ρ(mother's area, daughter's area) ≥ 0.35` in both cells on the contrast pairs, and `ρ(distance to the mother, daughter's area)`
must reproduce X103c's sign and order of magnitude (**−0.01 and −0.37**) — otherwise the pair set has drifted and the comparison is
void.

## 3. Readout exists and varies

Per cell: `ρ(d_mother, area)`, `ρ(d_other, area)`, their difference in absolute value, the medians of both distances, and the
per-world coefficients for both. Variation exists by construction: the two distances are different coordinates with medians that
differ (X103c's median mother distance is 4.9 and 10.8 cells).

## 4. Sensitivity arithmetic

The contrast is a difference of two Spearman coefficients **on the same pairs**, which removes the world-to-world variation exactly
as X102's paired gap did. With 2 000 and 1 100 pairs the standard error of each coefficient is 0.022 and 0.030; the difference has
a smaller error than either, so the declared resolution is **0.10** in the difference, three to four sigma.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 100 contrast pairs, coverage among loggable pairs below 0.60, the heredity control below 0.35, or
`ρ(d_mother, area)` outside **±0.10** of X103c's value for that cell.

**Local geometry** if in the maze cell `|ρ(d_other)| ≥ 0.20` and `|ρ(d_mother)| − |ρ(d_other)| ≤ 0.10`: stranger peaks carry the
same information, so the negative term is about where the daughter sits in the medium, and the maternal reading is dropped for that
cell.
**Maternal** if in the maze cell `|ρ(d_mother)| ≥ 0.20` and `|ρ(d_mother)| − |ρ(d_other)| ≥ 0.15`: the mother's position carries
information that other peaks do not.
**Nothing to explain** if `|ρ(d_other)| < 0.20` and `|ρ(d_mother)| < 0.20` (the expected reading of the lattice cell, which serves
as the internal null).
**Mixed** otherwise, printed cell by cell.

The lattice cell is a check, not a claim: it is where X103c saw nothing, so both coefficients are expected near zero, and a large
coefficient there would say the contrast design itself is picking up size structure.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs, seeds 291–300 per inflow |
| readouts | distance to the mother's peak; distance to the nearest non-ancestor peak at the birth step |
| response | the daughter's peak excursion-set area at `v > 0.20` |
| controls | heredity ≥ 0.35; X103c's coefficients reproduced within ±0.10 |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x103d_peak_null.json` |

## Checklist

- [x] connected (100 contrast pairs, coverage among loggable pairs ≥ 0.60)
- [x] positive control numeric (heredity ≥ 0.35; X103c reproduced within ±0.10)
- [x] readout exists and varies (two different distances, medians 4.9 / 10.8 cells)
- [x] sensitivity computed (§4: paired difference, resolution 0.10)
- [x] refusal rule written, with "local geometry" as a real outcome
- [x] stated: the lattice cell is an internal null, not a claim

## Status

Registered 2026-11-02 17:20 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
