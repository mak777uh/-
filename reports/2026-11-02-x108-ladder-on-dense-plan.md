# X108 — the ladder and the specificity on the dense-field series

**Why.** X105 showed that the sparse series **understated** the maze heredity by a quarter (0.384 → 0.480) because the pairs that
appear in a 50-step log are the long-lived ones and, in the maze, lifetime and area are inversely related (X92). The two results that
sit downstream of that number were measured on the sparse series:

- **X101's ladder** — 0.531 / 0.384 (excursion set) → 0.300 / 0.174 (basin) → 0.176 / 0.058 (core), verdict "heredity needs the cut";
- **X102's specificity** — the parent-beats-neighbour gap falls from 0.312 / 0.215 to 0.017 / −0.010, verdict "specificity is
  definition-bound too".

Both used fields saved every 50 steps, so only a fifth of the measured peaks had a field at the peak step and the basin definitions
were available for 95 % / 80 % of pairs. X108 reruns **exactly the same twenty worlds** (X105's seeds, flags and logging density)
with `--save-fields-every 10`. Saving a field draws no randomness — checked on seed 301: the `series` and `uid_pairs` arrays are
identical to X105's, only `save_fields_every` differs — so this is the same sample of worlds with a five-times denser field archive,
not a new replication.

## 1. Manipulation is connected

Twenty runs (seeds 301–310 × two inflows), fields in `_x108_fields` at every logged step (600 per run). The ladder needs, per pair,
a field at the ancestor's and the daughter's peak steps. Connectedness: basin coverage at least **0.90** in both cells (X101: 0.952
and 0.800) and at least **100 pairs**.

## 2. Positive control fires (numeric, both required)

1. **The excursion-set rho1 must reproduce X105 on the same worlds**: `|ρ₁(area) − 0.548| ≤ 0.02` at 0.030 and `|ρ₁(area) − 0.480| ≤
   0.02` at 0.040. This is the check that the pair population has not changed while the field archive got denser.
2. **The basins partition the field in every world** (`partitions_ok == worlds` in both cells), as in X101.

## 3. Readout exists and varies

Per cell: `ρ₁` for the excursion-set area, the basin area and the relative core, their medians, the coverage, and the specificity gap
under both definitions on the same daughters (X102's readout). Contrast exists by construction — X101's medians differ by a factor of
four between definitions.

## 4. Sensitivity arithmetic

The pairs are the same 2 211 / 1 951 as X105 (structural loss 0.021 / 0.088), so the standard error of a coefficient is 0.022 / 0.030
and the declared resolution is **0.10**. For the specificity gap the paired structure makes the difference's error smaller; the
resolution stays 0.10, as in X102.

## 5. Refusal rule (fixed before the run)

**Void** if basin coverage is below 0.90 in either cell, pairs below 100, the rho1 reproduction misses its ±0.02 band, or the partition
check fails in any world.

**The ladder stands on dense fields** if the excursion-set-minus-basin delta is still `≥ 0.15` in both cells.
**The ladder's gap was a sparse-series artefact** if the delta falls to `≤ 0.10` in both cells.
**Mixed** otherwise, printed cell by cell.

**The specificity collapse stands** if the basin gap is `≤ 0.05` in both cells.
**The collapse was a sparse-series artefact** if the basin gap is `≥ 0.15` in at least one cell **and** the delta from the threshold
gap is `≤ 0.15` in that cell.
**Mixed** otherwise.

Both verdicts are reported separately; they answer different questions and one may move while the other does not.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs (X105's worlds, a field at every logged step) |
| analyses | `x101_analyse.py --prefix x108 --fields _x108_fields`, `x102_analyse.py --prefix x108 --fields _x108_fields` |
| controls | excursion-set rho1 within ±0.02 of X105; basins partition every field |
| artifacts | `l1_field_x101b_dense.json`, `l1_field_x102b_dense.json` |

## Checklist

- [x] connected (coverage ≥ 0.90, 100 pairs, 600 fields per run)
- [x] positive controls numeric (rho1 within ±0.02 of X105; partitions in every world)
- [x] readout exists and varies (medians differ fourfold between definitions)
- [x] sensitivity computed (§4: SE 0.022 / 0.030, resolution 0.10)
- [x] refusal rule written, with "the gap was a sparse-series artefact" as a real outcome
- [x] stated: the worlds are X105's, not a new replication

## Status

Registered 2026-11-02 17:58 MSK, before the X108 aggregates were produced (the series itself started at 17:52; it reruns X105's
worlds and draws no new randomness).

доска: принято 0, отклонено 0, отложено 0.
