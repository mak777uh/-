# X103 — is heredity topographic after all? *Where* in the mother's basin, not how big it is

**Why.** X102 closed the definition ladder with an uncomfortable symmetry: the *level* of size heredity falls from 0.531 / 0.384
(excursion set at `v > 0.20`) to 0.300 / 0.174 (drainage basin) and 0.176 / 0.058 (core at half the local maximum), and its
*specificity* — a daughter follows her own mother rather than her nearest non-ancestor — falls with it, from 0.312 / 0.215 to
0.017 / −0.010. Yet the same check showed that ancestry is not invisible in the topography: a mother's peak site sits inside her
daughter's basin 0.398 / 0.187 of the time against a stranger's 0.132 / 0.081. So the basin is not blind — its *area* is simply the
wrong quantity.

That leaves exactly two readings, and X102 named the test that separates them:

- **skirt reading** — what is inherited is the width of the excursion above a fixed level; the basin is only the stage, and a
  daughter's position inside it should carry little beyond her mother's excursion area;
- **topographic reading** — heredity is a property of the valley, not of the structure: what a daughter inherits is *where she
  starts* (and the local depth there), so position within the mother's basin should predict her size, and the mother's excursion area
  should lose its predictive power once position is known.

This is an **analysis of stored snapshots** (X100's twenty runs, fields at every logged step). No GPU, no new runs.

## 1. Manipulation is connected

Two inflows (`F = 0.030`, `0.040`), ten worlds each, the same ancestor–daughter pairs X100/X101/X102 used. For every pair the analysis
needs: the mother's peak frame and peak pixel, her basin (steepest ascent, `x101_analyse.basins`), and the daughter's **birth
position** — her centroid at the first logged step at which she exists. Connectedness: at least **100 pairs** per cell with both a
mother basin and a daughter birth position, and basin coverage at least **60 %** of the pairs.

Positions are on a torus; distances are torus distances, in cells, so the primary predictor needs no normalization. A daughter born
outside her mother's basin is not dropped — that is exactly the interesting case — and the fraction born outside is reported.

## 2. Positive control fires (numeric)

On **this same subset of pairs**, the mother's excursion-set area must still predict the daughter's area: `ρ(mother, daughter) ≥ 0.35`
in both cells. This is the heredity the whole ladder rests on; if the subset that happens to have a mother basin and a birth position
has lost it, the subset is not representative and the analysis is void. (The full-sample values are 0.531 and 0.384; the band is set
from the subset's own size, not borrowed from another regime.)

## 3. Readout exists and varies

Per cell, on the same pairs:

| quantity | what it is |
|---|---|
| `rho_dist` | Spearman(birth distance from the mother's peak, daughter's peak area) |
| `rho_partial_area` | Spearman(mother's area, daughter's area), controlling birth distance |
| `rho_partial_dist` | Spearman(birth distance, daughter's area), controlling the mother's area |
| `frac_outside` | share of daughters born outside the mother's basin |
| `rho_r` | the same as `rho_dist` for the normalized radius `r = distance / R`, `R` = the radius of the mother's basin (farthest basin pixel from her peak), reported as a robustness check |

The readout varies over a plausible range: distances run from 0 (a daughter on her mother's peak) to well beyond a basin radius, so a
coefficient of zero is a measurement, not an absence of contrast.

## 4. Sensitivity arithmetic

Pairs: ~1 800 at `F = 0.030` and ~950 at 0.040 (X102's basin coverage), so the standard error of a Spearman coefficient is
`1/√(n−1)` ≈ **0.024** and 0.032. A partial correlation with one control loses little. The declared resolution is therefore
**0.10** — about 4σ at 0.030 and 3σ at 0.040 — and the decision thresholds below sit at or above it. Nothing smaller will be called
a difference.

## 5. Refusal rule (registered before the run)

**Void** if a cell has fewer than 100 usable pairs, basin coverage below 60 %, or a positive control below 0.35 (§2).

**Skirt reading survives** if, in **both** cells: `|rho_dist| ≤ 0.10`, `|rho_partial_dist| ≤ 0.10`, and `rho_partial_area` stays
within **0.10** of `rho_control` (the unpartialled value on the same subset).
**Topographic reading wins** if, in **both** cells: `|rho_dist| ≥ 0.20` **and** `rho_partial_area` falls **≥ 0.15** below
`rho_control`.
**Mixed** otherwise, printed cell by cell — and if the two cells disagree in direction, the report says "the answer is not one
number" rather than averaging them.

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs (fields at every logged step), seeds 291–300 per inflow |
| predictor | torus distance from the mother's peak to the daughter's birth centroid, in cells; `r = distance / R_basin` as a check |
| response | the daughter's peak excursion-set area at `v > 0.20` |
| control | the mother's own area on the same subset, plus the unpartialled coefficient as the reference |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x103_basin_position.json` |

## Checklist before the analysis

- [x] connected (100 pairs, 60 % basin coverage, positions on a torus)
- [x] positive control fires (numeric: `ρ(mother, daughter) ≥ 0.35` on the subset)
- [x] readout exists and varies (distance 0 → beyond a basin radius)
- [x] sensitivity computed (§4: SE 0.024 / 0.032, resolution 0.10)
- [x] refusal rule written, with "topographic reading wins" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 16:55 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
