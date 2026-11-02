# X112c-a — the liveness floor is a component count in the lattice and a structural test in the maze

**What happened, and what I had already seen.** X112c's plan inherited X112b's liveness rule: a run counts as readable only if it keeps
**≥ 10 components** at step 6000. In the maze cell that rule is wrong, and X110b already established why: the percolating cell carries
**one or two** structures by construction (X110b: `F = 0.040` has 2 components and 41 % occupied at `γ = 0.10`), so a count of ten rejects
healthy maze runs and accepts shattered speckle.

The amendment was written after the first two of twenty runs had landed, and the analyser had already printed their summary line: **98 of
196 pairs, one run flagged as below the floor, `ρ₁ = 0.150` at `cut = 0.15`**. That is partial data and it is disclosed here rather than
quietly dropped; what it does not do is enter any verdict, because the verdict is computed at the end from all twenty runs.

## 1. Manipulation is connected

Twenty runs at `F = 0.040`, seeds 301–310, `--threshold 0.15` and `0.25` — X112c's series, unchanged. The liveness test becomes the one
X110b registered and validated:

**alive ⇔ `occupied ≥ 0.05` and the largest component ≥ 50 cells.**

Both quantities are already in every run's log (`series[].occupied`, `series[].areas`), so no re-run is needed.

## 2. Positive control fires (numeric)

1. **The 0.20 reference is quoted:** `ρ₁ = 0.480`, gap 0.443 (X108's dense maze numbers). The control fires if the recomputation at 0.15 and
   0.25 is compared against a reference that exists — i.e. if both reference fields are present in the aggregates.
2. **The structural floor separates:** for every one of the twenty runs the amended test must give a verdict that agrees with X110b's
   observation for this cell — alive at the coupling that keeps a body (X110b's `γ = 0.10` runs have 0.39–0.41 occupied and components of
   1 333–3 030 cells, so they pass by a wide margin) and dead for a speckle (X110b's `γ = 0.50` runs have 0.008 occupied and 37-cell
   components, so they fail both tests).

## 3. Readout exists and varies

Unchanged from X112c's plan: `ρ₁`, the specificity gap, the median area, the pair count and the coverage per cut. The maze's 0.20 gap
(0.443) is the largest in the line, so a cut effect has room to show.

## 4. Sensitivity arithmetic

Unchanged: SE 0.018–0.058, resolution 0.10 for the level, 0.15 for the gap, 0.08 for the cross-cell reversal. The amendment changes only
which runs are readable, not what is measured.

## 5. Refusal rule (fixed before the remaining eighteen runs are read)

**Void** if a cut gives fewer than 300 pairs or if a run fails the structural liveness test.

**The level is cut-bound** if `|ρ₁(cut) − 0.480| ≥ 0.10` at either cut; **cut-stable** if both are ≤ 0.05.
**The gap is cut-bound** if `|gap(cut) − 0.443| ≥ 0.15`; **cut-stable** if both are ≤ 0.10.
**The cross-cell order reverses at 0.25** if `ρ₁(maze, 0.25) > ρ₁(lattice, 0.25) + 0.08 = 0.525` — the lattice value 0.445 is X112b's.
**Mixed** otherwise.

## Design summary

| factor | value |
|---|---|
| runs | X112c's twenty, unchanged |
| liveness | `occupied ≥ 0.05` and largest component ≥ 50 (X110b's rule) |
| reference | X108 maze at 0.20: `ρ₁ = 0.480`, gap 0.443 |
| cross-reference | X112b lattice at 0.25: 0.445 |
| artifact | `E09_pond/l1_field_x112c_cuts_maze.json` |

## Checklist

- [x] connected (structural liveness, ≥ 300 pairs, twenty runs)
- [x] positive control numeric (the floor separates X110b's alive and dead cases by an order of magnitude)
- [x] readout exists and varies (maze gap 0.443 at 0.20)
- [x] sensitivity computed (§4: resolution 0.10 / 0.15 / 0.08)
- [x] refusal rule written, with "the order does not reverse" as a real outcome
- [x] stated: written after two of twenty runs were summarised, which the plan discloses

## Status

Registered 2026-11-02 23:18 MSK, with two of twenty runs on disk.

доска: принято 0, отклонено 0, отложено 0.
