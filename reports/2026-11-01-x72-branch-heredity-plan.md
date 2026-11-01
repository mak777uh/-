# X72 — at the multistable boundary, does a daughter take her parent's branch? (analysis of existing data)

**Question.** X71 found that at `F = 0.035`, `k = 0.06` the field supports two wavelengths at the same parameters —
12.0 cells and 8.73 cells — and that both modes live inside a single run. X70 found a *graded* memory of size. Put
together, they predict something stronger and discrete: at the boundary a daughter should sit on the **same branch** as her
parent more often than a non-parent structure at the same distance does. If that holds, the medium carries heredity of a
*state*, not only of a blur.

`F = 0.035` is exactly the configuration of the X70 replication runs (`x70r_*`), so no new runs are needed: this is a
re-analysis of data already in git. Because the data exist, the criteria below are fixed and committed **before** the
analysis script is run, and the report will say so.

## 1. Manipulation is connected

The manipulation is not applied here; the manipulation was made when the worlds were run (inflow `F = 0.035` versus the
sweep's other cells). What this analysis must show first is that the two branches of X71 are **present in this data**:
spacings between neighbouring structures must fall into two groups, not one. If they do not, the branch variable does not
exist here and the test is void regardless of what it returns.

## 2. Positive control fires

The positive control is presence of both classes: **each branch must hold at least 25 % of the classified division
events** in the pooled data, in the pattern arm. A classification that puts 95 % of events in one class cannot detect
concordance — it would return a concordance near 1 for parents, surrogates and shuffled labels alike.

## 3. Readout exists and varies

Per division event (`uid_pairs`, birth step from `uid_outcomes.first`), the parent's branch is read at the last logged
snapshot at or before the birth and the daughter's at the first at or after it. The branch is a **class**, derived from the
local spacing of the structure: for each component at a snapshot, the distance to the nearest other component centroid on
the torus; a structure is **wide** if that distance is `>= 10.4` cells (the midpoint between X71's 12.0 and 8.73, fixed
here) and **narrow** otherwise. The spacing is a proxy for the local wavelength, chosen because it needs only the component
log that already exists; the alternative — a local spectrum in a 32–48 cell window — has coarser resolution than the
difference it would have to resolve.

Readout: **concordance**, the fraction of classified events where parent and daughter share a branch.

## 4. Sensitivity arithmetic

Events available: 175 division events per world in the pattern arm at `F = 0.035`, five worlds. If the two branches are
roughly 60/40 and heredity were perfect, concordance would be 1.0; with no heredity it equals the prior collision
probability, `p² + (1−p)² ≈ 0.52`. The surrogate control sets the empirical baseline instead of this arithmetic, so the
detectable effect is limited by the number of classified events: with ~150 per world, a binomial band at 95 % is about
±0.08, so a difference of **0.15** between parent and surrogate concordance is detectable in each world separately. That
number is the criterion.

## 5. Refusal rule

The analysis is declared **insensitive** if fewer than 60 % of division events can be classified (parent or daughter
without a logged neighbour), or if one class holds more than 75 % of events in the pooled pattern arm (the positive control
fails). It is declared **supports branch heredity** if parent concordance exceeds the surrogate's by **at least +0.15 in the
pooled pattern arm and in at least 4 of 5 worlds**, and if it also exceeds the p95 of a shuffle null that permutes parent
branches across events within a world (2000 draws). It is declared **not supported** if the pooled difference is ≤ 0 or if
fewer than 2 worlds reach +0.15. Anything in between is reported as inconclusive with the numbers.

The homogeneous arm is computed and reported but **not** used as evidence: X71 shows it cannot hold two branches there
(its `F = 0.055` cell degenerates and its remaining cells are single-valued).

## Checklist before the analysis

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

Connectedness is not applicable in the usual sense (no manipulation is applied now); instead the control in §1 is that the
branch variable exists in the data at all, and §2 is that both classes are populated.

## Design summary

| factor | value |
|---|---|
| data | `x70r_pattern_s171-175.json` (already in git, `--sample-every 50`, `--init-jitter`) |
| world count | 5 |
| events | division pairs from `uid_pairs` (~175 per world) |
| branch proxy | nearest-neighbour centroid distance, threshold 10.4 cells |
| statistic | concordance (parent–daughter branch agreement) |
| controls | nearest-distance surrogate; within-world permutation of parent branches, 2000 draws |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x72_branch.json` |

## Status

Registered 2026-11-01 19:45 MSK, before the analysis script was written. No GPU, no new runs; if the verdict is positive the
follow-up is a *prospective* series with the branch readout pre-registered on fresh worlds, because a re-analysis of X70's
data can never be as strong as the original experiment.
