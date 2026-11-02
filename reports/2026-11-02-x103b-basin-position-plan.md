# X103b — where in the mother's basin, re-registered with the denominator fixed

**This is not a blind preregistration and says so.** X103 voided on a coverage gate that counted structurally unloggable pairs
(622 of 1 761 at `F = 0.040`), and its exploratory numbers were printed before this plan was written. The criteria below are
therefore fixed **in the knowledge of those numbers**; what this re-analysis adds is a denominator that measures the instrument,
a **selection measurement** of the dropped pairs, and a primary predictor that divides out the basin's own scale. The claim that
can come out of it is limited to what those additions test — the numbers themselves are already known and are not re-discovered.

**Question.** X102 left two readings: heredity is the **width of the excursion** (the basin is only the stage), or heredity is
**topographic** (what a daughter inherits is where she starts inside the valley). The test is whether the daughter's position
inside her mother's basin predicts her size, and whether the mother's excursion area keeps its coefficient once the position is
known. Same artifacts as X103: X100's twenty runs, no GPU.

## 1. Manipulation is connected

Two inflows (`F = 0.030`, `0.040`), ten worlds each, X100's runs, fields at every logged step. Per pair: the mother's peak frame
and pixel, her basin by steepest ascent, the daughter's birth centroid (first logged appearance). Distance is torus distance in
cells; the **primary predictor** is `r = distance / R`, where `R` is the mother's basin radius (farthest basin pixel from her peak),
because `r` divides out the basin's own scale and `R` itself is a size that X102 showed carries no heredity.

Connectedness: at least **100 usable pairs** per cell and **coverage among pairs whose peaks exist** at least **0.90** — the
instrument's availability, not the world's logging resolution. The structural loss is reported separately: how many pairs have an
ancestor or a daughter that was never logged.

## 2. Positive control fires, and the subset is checked for selection (numeric)

Two numeric controls, both required:

1. **Heredity control:** on the kept pairs, `ρ(mother's area, daughter's area) ≥ 0.35` in both cells (full samples: 0.531 and
   0.384). If the subset has lost the heredity the ladder rests on, the subset is not representative and the analysis is void.
2. **Selection control:** the kept and the dropped pairs must agree in scale — the ratio of median daughter peak areas
   `kept / dropped` must lie within **[0.75, 1.33]** in each cell. Outside that band the subset is the long-lived tail (X92:
   lifetime and area are related), the report says which way the numbers are biased, and no claim is made even if the readout is
   clean.

## 3. Readout exists and varies

Per cell, on the kept pairs: `ρ(r, daughter)`, `ρ(distance, daughter)` (secondary), `ρ(mother's area, daughter)` (the control
value), the partial of the mother's area given `r`, the partial of `r` given the mother's area, the share of daughters born
outside the mother's basin, and the medians of distance, `R` and `r`. Contrast exists by construction: `r` runs from 0 to beyond 1.

## 4. Sensitivity arithmetic

The kept subsets are 1 970 and 1 054 pairs (X103), so the standard error of a Spearman coefficient is 0.023 and 0.031; a partial
with one control loses little. The declared resolution is **0.10**, four and three sigma respectively. Nothing smaller is called a
difference, and a cell pair that disagrees in sign is reported as disagreement, not averaged.

## 5. Refusal rule (fixed here, before the re-run)

**Void** if a cell has fewer than 100 usable pairs, coverage among loggable pairs below 0.90, heredity control below 0.35, or the
selection ratio outside [0.75, 1.33].

**Skirt reading survives** if in **both** cells `|ρ(r, daughter)| ≤ 0.10` and the partial of the mother's area given `r` stays
within **0.10** of the control value.
**Topographic reading wins** if in **both** cells `|ρ(r, daughter)| ≥ 0.20` **and** the partial of the mother's area given `r`
falls **≥ 0.15** below the control value.
**Additive** if `|ρ(r, daughter)| ≥ 0.20` somewhere **and** the partial of the mother's area given `r` stays within 0.10 of the
control value — position adds a term without replacing the inherited width.
**Mixed** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs, seeds 291–300 per inflow |
| primary predictor | `r = distance / R`, `R` the mother's basin radius |
| response | the daughter's peak excursion-set area at `v > 0.20` |
| controls | heredity on the subset (≥ 0.35); selection ratio of median daughter areas in [0.75, 1.33] |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x103b_basin_position.json` |

## Checklist

- [x] connected (100 pairs, coverage among loggable pairs ≥ 0.90)
- [x] positive controls numeric (heredity ≥ 0.35; selection ratio in [0.75, 1.33])
- [x] readout exists and varies (`r` from 0 to beyond 1)
- [x] sensitivity computed (§4: SE 0.023 / 0.031, resolution 0.10)
- [x] refusal rule written, with "additive" as a real outcome
- [x] stated: not blind — the exploratory numbers of X103 are known

## Status

Registered 2026-11-02 16:59 MSK, before the re-run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
