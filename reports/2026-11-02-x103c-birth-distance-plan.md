# X103c — distance only: the third and last design on stored snapshots

**Two voids came before this plan, and both were the design's fault, not the world's.**

1. X103 gated coverage at 0.60 over *all* ancestor–daughter pairs and came back at 0.599 for `F = 0.040`, because 622 of 1 761
   pairs have an ancestor or daughter that was never logged (median lifetime 89 steps against a 50-step logging interval). Among
   pairs whose peaks exist, the instrument was available 0.973 and 0.925.
2. X103b fixed that denominator and added a selection control (median daughter area, kept versus dropped, inside [0.75, 1.33]).
   At `F = 0.040` it passed (1.24), but at 0.030 it failed hard: **0.662** — the 54 pairs lost to the basin definition (a mother
   whose peak pixel has no drainage basin) had much larger daughters (median 80 against 53).

So the basin is the problem: needing it loses pairs, and the pairs it loses are not a random subset. This design keeps the
question and drops the basin.

**Question (unchanged).** Does *where* a daughter is born relative to her mother predict how large her excursion becomes — and
does the mother's own excursion area keep its predictive power once the position is known? If position replaces the area, heredity
is topographic; if it adds a term without replacing it, the picture is additive; if it does nothing, the inherited quantity is the
excursion's width and the valley is only the stage.

## 1. Manipulation is connected

Two inflows (`F = 0.030`, `0.040`), ten worlds each, X100's runs. Per pair: the mother's peak centroid and the daughter's birth
centroid (her first logged appearance). **No basin, no label, no radius** — the predictor is the torus distance between the two
centroids, in cells. This is available for every pair whose two structures were logged at all, so the only loss is the structural
one: **35 % of the maze cell's pairs have an unlogged member** (X103's diagnosis), which is a limitation of the artifacts and is
reported as a number, not gated.

Connectedness: at least **600 usable pairs** per cell (so both cells can carry a per-world readout of ten worlds at ≥ 30 pairs) and
coverage among loggable pairs at least **0.90**.

## 2. Positive control fires (numeric)

On the kept pairs, the mother's excursion area must still predict the daughter's: `ρ(mother, daughter) ≥ 0.35` in both cells
(full samples 0.531 / 0.384). This is the heredity the ladder rests on, measured in the regime of this experiment.

An honest negative control is added because this design has one obvious artefact: **the distance cannot correlate with the
daughter's area through the mother's size**, but it *can* correlate with position across the lattice, so the analysis reports the
coefficient **per world** and how many of the ten worlds agree in sign. A pooled coefficient carried by one or two worlds is
reported as such.

## 3. Readout exists and varies

Per cell: `ρ(distance, daughter area)`, `ρ(mother area, daughter area)` (control), the partial of the mother's area given the
distance, the partial of the distance given the mother's area, the median distance, and the per-world coefficients.

## 4. Sensitivity arithmetic

Usable pairs: about 2 000 at 0.030 and 1 100 at 0.040 (X103's `pairs_logged`), so the standard error of a Spearman coefficient is
0.022 and 0.030. The declared resolution is **0.10** — four and three sigma. A per-world coefficient on 30–340 pairs has a much
wider interval, which is why the per-world table is used for **sign agreement**, not for magnitude.

## 5. Refusal rule (fixed before this run)

**Void** if a cell has fewer than 600 usable pairs, coverage among loggable pairs below 0.90, or a heredity control below 0.35.

**Skirt reading survives** if in both cells `|ρ(distance, daughter)| ≤ 0.10` and the partial of the mother's area given the
distance stays within **0.10** of the control value.
**Topographic reading wins** if in both cells `|ρ(distance, daughter)| ≥ 0.20` and the partial of the mother's area falls **≥ 0.15**
below the control value.
**Additive** if `|ρ(distance, daughter)| ≥ 0.20` in at least one cell and the partial of the mother's area stays within 0.10 of the
control value in both.
**Mixed** otherwise, cell by cell, with the per-world sign table — and if the cells disagree, the answer is "not one number" and
the next step is **not** another analysis of these artifacts but a run with denser logging (X105 below).

## Design summary

| factor | value |
|---|---|
| artifacts | X100's twenty runs, seeds 291–300 per inflow |
| predictor | torus distance from the mother's peak centroid to the daughter's birth centroid, cells |
| response | the daughter's peak excursion-set area at `v > 0.20` |
| controls | heredity on the kept pairs (≥ 0.35); per-world sign agreement |
| gate | 600 usable pairs, coverage among loggable pairs ≥ 0.90 |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x103c_birth_distance.json` |

## Checklist

- [x] connected (600 pairs, coverage among loggable pairs ≥ 0.90)
- [x] positive control numeric (heredity ≥ 0.35), plus a per-world sign table against pooling artefacts
- [x] readout exists and varies (distance 0 to the box scale)
- [x] sensitivity computed (§4: SE 0.022 / 0.030, resolution 0.10)
- [x] refusal rule written, with "additive" and "mixed → new runs" as real outcomes
- [x] stated: not blind — X103 gave the same readout under a basin-based design

## Registered next step if the cells disagree (X105)

Ten worlds per inflow at `--sample-every 10` instead of 50, so a structure that lives 89 steps is logged nine times instead of
once and the maze cell's structural loss falls from 35 % to a few per cent. Cost: ten short CPU runs per cell (the field line runs
on CPU), no GPU, and the logging density is fixed in advance for both cells (the X85 rule: logging frequency is a physical
parameter, so the two cells of one series must share it).

## Status

Registered 2026-11-02 17:02 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
