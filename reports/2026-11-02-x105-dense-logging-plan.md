# X105 — dense logging: the maze cell stops being a sample of long-lived structures

**Why.** Every number in this line at `F = 0.040` is conditioned on structures that lived long enough to be logged twice. The
diagnosis is arithmetic (X103): the maze cell's median lifetime is 89 steps, the logging interval is 50, and 35.3 % of
ancestor–daughter pairs have a member that was never logged at all. The basin-based analysis then showed the same selection biting a
second way: the 54 pairs it lost at 0.030 had daughters of median area 80 against 53 (X103b). So two questions cannot be settled on
the stored artifacts:

1. is the **maternal decay** term of X103c (`ρ(distance, daughter) = −0.367`, 10/10 worlds at 0.040) a property of the medium, or of
   the long-lived structures that happen to be visible?
2. is the **crowding** term of X103d (`+0.358`, 10/10 worlds at 0.030) equally robust?

This series logs every 10 steps instead of 50, so the median-lifetime structure is logged nine times instead of once and the
structural loss should fall below 10 %.

**What this series is not.** It is not X100 at finer resolution. `--sample-every` decides how many trait draws a world makes (the X85
rule: logging frequency is a physical parameter), so the seed produces a different world at 10 than at 50 even with the trait channel
inert (`beta = 0`, `eps = 0`, `freq-dep = 0`). The comparison inside this series is **cell against cell at the same density**; the
comparison with X100 is a **replication** at a new density, not a refinement of the same worlds.

## 1. Manipulation is connected

Twenty runs: two inflows (`F = 0.030`, `0.040`) × ten seeds (301–310), `field_track.py` with **exactly X100's flags** except
`--sample-every 10` and the output prefix. Connectedness is the point of the series and is measured from the logs:

- **structural loss below 10 %** in both cells (X100: 6.5 % at 0.030, 35.3 % at 0.040);
- at least **100 ancestor–daughter pairs** per cell;
- the components log must remain smaller than the fields archive (no disk surprise): the log grows by ~5×, from ~1 MB to ~5 MB per
  run, and the fields stay at one per 50 steps as in X100.

## 2. Positive controls fire (numeric, both required)

1. **Heredity on the new pairs:** `ρ(mother's excursion area, daughter's peak area) ≥ 0.35` in both cells (X100: 0.531 / 0.384). If
   denser logging changes the pair population enough to destroy heredity, the series has changed the world too much and is void.
2. **The known coefficients replicate in sign:** the distance coefficient must be **negative and ≤ −0.20 in the maze cell**
   (X103c: −0.367) and must stay **within ±0.15 of zero in the lattice cell** (X103c: −0.008). A sign flip in either cell would say
   the earlier readout was an artefact of the visible subset.

## 3. Readout exists and varies

Per cell, on the pairs: the median distance, the median annualised pair count per world, the structural loss, `ρ(distance, daughter)`,
the crowding coefficient `ρ(distance to the nearest non-ancestor peak, daughter)`, and the per-world coefficients for both. Contrast
exists by construction — X103c's medians are 4.9 and 10.8 cells and the distributions are wide.

## 4. Sensitivity arithmetic

At X100's density the cells carried 2 024 and 1 139 pairs; with nine times more logged appearances the maze cell should gain pairs,
not lose them, so the standard error of a coefficient is at worst `1/√(1139−1)` = **0.030** and the declared resolution is **0.10**
(three sigma). The per-world table (ten worlds) is used for sign agreement, not magnitude.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 100 pairs, structural loss ≥ 10 %, heredity below 0.35, or a sign that contradicts §2.

**The maternal decay is robust** if the maze cell's distance coefficient is `≤ −0.20` (sign negative) and at least **8 of 10 worlds**
are negative.
**The maternal decay was a selection artefact** if the maze coefficient falls to `|ρ| ≤ 0.10` or its per-world sign agreement is below
6/10.
**Mixed** otherwise.
**Crowding is robust** if the lattice coefficient is `≥ 0.20` with at least 8/10 worlds positive; **not robust** if `|ρ| ≤ 0.10` or
agreement below 6/10; mixed otherwise.

## Design summary

| factor | value |
|---|---|
| runs | 20 (`F = 0.030`, 0.040 × seeds 301–310) |
| runner | `scripts/field_track.py` via `scripts/x105_series.py`, X100's flags exactly, `--sample-every 10` |
| cost | ~105 s per run on the current hardware, ~35 min total, no GPU contention with the field line |
| artifact | `morphogenesis/experiments/L1_field/x105_*.json` + `x105_series_index.json`; analysis aggregate `E09_pond/l1_field_x105_dense.json` |

## Checklist

- [x] connected (structural loss < 10 %, 100 pairs per cell, log size bounded)
- [x] positive controls numeric (heredity ≥ 0.35; maze coefficient ≤ −0.20, lattice within ±0.15 of zero)
- [x] readout exists and varies (distances 4.9 / 10.8 cells, wide distributions)
- [x] sensitivity computed (§4: SE ≤ 0.030, resolution 0.10)
- [x] refusal rule written, with "the term was a selection artefact" as a real outcome
- [x] stated: not X100 at finer resolution — the seed makes a different world at a new logging density (X85 rule)

## Status

Registered 2026-11-02 17:10 MSK, before the series.

доска: принято 0, отклонено 0, отложено 0.
