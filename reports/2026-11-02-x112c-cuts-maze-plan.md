# X112c — the same cut sweep at `F = 0.040`, where X99 found the inflow ordering reversing

**Why.** X112b gave a clean asymmetry in the lattice cell: the level moves one step with the cut (0.554 / 0.548 / 0.445 at 0.15 / 0.20 /
0.25) and the specificity gap does not (0.284 / 0.302 / 0.326). But X99 found something the lattice did not do: at the 0.25 cut the
**ordering between inflows reverses** — the half-life at 0.030 and 0.040 swaps places. If a level can swap order between cells with the
cut, then a cut-stability statement measured in one cell is not a statement about the medium.

**The question.** At the maze cell (`F = 0.040`), do the level and the gap move with the cut the way they do in the lattice — and does the
**order between the two cells** reverse at 0.25?

## 1. Manipulation is connected

Twenty runs at `F = 0.040`, seeds 301–310 (the worlds X108 measured at 0.20), `--threshold 0.15` and `0.25`, X100's flags otherwise. The
0.20 reference is X108's own maze numbers: `ρ₁ = 0.480` and gap **0.443** (`l1_field_x101b_dense.json`, `l1_field_x102b_dense.json`).

Connectedness: every run must keep **≥ 10 components** at 6000 under its own threshold, and each cut must give at least **300 pairs**.
The maze is the fragile cell (X110b: one percolating body at 0.10–0.30 coupling), so a cut that dissolves the population is reported as
unreadable rather than as a null.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **The world is unchanged:** the ODE does not see the threshold, so each run's peak amplitude at step 6000 must agree with X108's run at
   the same seed within **0.01**, and the control **fires if** that holds for all twenty.
2. **The 0.20 reference is quoted, not recomputed:** 0.480 and 0.443 from the dense aggregates.

## 3. Readout exists and varies

Per cut: `ρ₁`, the specificity gap, the median area, the pair count, the coverage. Variation exists by construction: in the lattice the same
sweep moved the level by 0.103 and the gap by 0.024, and the maze's 0.20 gap (0.443) is the largest in the line, so a cut effect has
room to show.

## 4. Sensitivity arithmetic

Ten worlds per cut; the maze's dense series carries 1 951 pairs at 0.20 and the lattice's 0.25 cut gave 3 161, so 300–3 000 pairs per cut
and SE 0.018–0.058. The declared resolution is **0.10** for the level and **0.15** for the gap, as in X112b. The comparison across cuts is
paired because the worlds are shared.

**The cross-cell comparison** (does the order reverse?) has a resolution of the two cells' SEs combined, i.e. about **0.08** at the
0.25 cut; a swap smaller than that is not called a reversal.

## 5. Refusal rule (fixed before the run)

**Void** if a cut keeps fewer than 10 components in any run, gives fewer than 300 pairs, or if the world-unchanged control fails.

**The level is cut-bound** if `|ρ₁(cut) − 0.480| ≥ 0.10` for at least one cut; **cut-stable** if both are ≤ 0.05.
**The gap is cut-bound** if `|gap(cut) − 0.443| ≥ 0.15` for at least one cut; **cut-stable** if both are ≤ 0.10.
**The cross-cell order reverses at 0.25** if `ρ₁(maze, 0.25) > ρ₁(lattice, 0.25) + 0.08` while at 0.20 the maze is below the lattice
(0.480 < 0.548). **It does not** if the maze stays below the lattice by more than 0.08 at both cuts.
**Mixed** otherwise, printed per cut.

## Design summary

| factor | value |
|---|---|
| runs | 20 (seeds 301–310 × thresholds 0.15 and 0.25), `F = 0.040`, ~75 s each |
| reference | X108 at 0.20: `ρ₁ = 0.480`, gap 0.443 |
| cross-reference | X112b's lattice values at the same cuts: 0.554 / 0.445 |
| controls | ODE independent of the threshold, run-by-run within 0.01; the 0.20 reference is quoted |
| artifact | `E09_pond/l1_field_x112c_cuts_maze.json` |

## Checklist

- [x] connected (≥ 10 components, ≥ 300 pairs, world-unchanged check)
- [x] positive control numeric (threshold does not enter the ODE, within 0.01 per run)
- [x] readout exists and varies (the lattice sweep moved the level by 0.103; the maze gap is 0.443)
- [x] sensitivity computed (§4: SE 0.018–0.058, resolution 0.10 / 0.15, cross-cell 0.08, paired across cuts)
- [x] refusal rule written, with "the order does not reverse" as a real outcome
- [x] stated: the same worlds as the 0.20 reference, because the threshold is an observer parameter

## Status

Registered 2026-11-02 22:55 MSK, before the runs.

доска: принято 0, отклонено 0, отложено 0.
