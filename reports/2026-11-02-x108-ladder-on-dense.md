# X108 — the ladder and the specificity on the dense-field series

**Plan:** [`2026-11-02-x108-ladder-on-dense-plan.md`](2026-11-02-x108-ladder-on-dense-plan.md) (registered 17:58).
**Aggregates:** `l1_field_x101b_dense.json`, `l1_field_x102b_dense.json`. Twenty runs from X108: **the same worlds as X105**
(series and `uid_pairs` bit-identical, only `save_fields_every` differs), with a field at every logged step.

## Why it was worth rerunning

X101's ladder and X102's specificity were measured on fields saved every 50 steps, so only one peak in five had a field at its own
peak step and the basin definitions were available for 95 % / 80 % of pairs. X105 then showed the sparse series understates the maze
heredity by a quarter (0.384 → 0.480). Both downstream results had to be re-measured on the same worlds with a field at every step.

## The manipulation held, and the controls fired

| inflow | basin coverage (sparse → dense) | partition check | ρ₁(area) against X105 |
|---|---|---|---|
| 0.030 | 0.952 → **0.979** | 10/10 | 0.548 vs 0.548 ✓ |
| 0.040 | 0.800 → **0.937** | 10/10 | 0.480 vs 0.480 ✓ |

Both registered controls fired exactly: the excursion-set coefficient reproduces X105's on the same worlds to three decimals, and the
basins partition every field.

## The ladder

| definition | 0.030 sparse → dense | 0.040 sparse → dense | delta at 0.030 | delta at 0.040 |
|---|---|---|---|---|
| excursion set, `v > 0.20` | 0.531 → **0.548** | 0.384 → **0.480** | — | — |
| basin by steepest ascent | 0.300 → **0.335** | 0.174 → **0.110** | −0.231 → **−0.213** | −0.209 → **−0.370** |
| median size (area / basin) | 76 / 112 → 83 / 109 | 423 / 81 → 400 / 81 | | |

Registered verdict: **the ladder stands on dense fields** — the excursion-set-minus-basin delta is ≥ 0.15 in both cells (−0.213 and
−0.370). It is not merely unchanged: at the maze inflow it nearly **doubles**, because the basin measure stops tracking the heredity
that the excursion measure sees (0.480 against 0.110). With every peak measurable, the topological basin is a *worse* measure than it
looked when a fifth of the peaks were missing.

## The specificity

| inflow | threshold: parent / stranger / gap | basin: parent / stranger / gap | change |
|---|---|---|---|
| 0.030 | 0.548 / 0.246 / **0.302** | 0.334 / 0.245 / **0.089** | **−0.213** |
| 0.040 | 0.480 / 0.037 / **0.443** | 0.106 / 0.043 / **0.064** | **−0.379** |

The pre-registered criterion — a fall of ≥ 0.15 in the gap in at least one cell — is met twice over: **−0.213** and **−0.379**, the
latter larger than the sparse series' −0.225. So *specificity is definition-bound too* survives dense logging and gets stronger. The
stricter branch of the plan ("the collapse stands if the basin gap is ≤ 0.05 in both cells") did **not** fire: the basin gaps are
0.089 and 0.064 — small, but not zero, and the honest sentence is that under the basin definition a mother still beats a neighbour
slightly.

What changes in the *numbers* is the threshold-level specificity at the maze inflow: 0.443 (parent 0.480, stranger 0.037) against
0.215 sparse. At dense fields the maze cell is by far the most lineage-specific cell in the line — the sparse series had flattened it.

## Reading

The two results that depended on the sparse series both survive, and both are *sharper* at dense fields:

- heredity is strongest where the definition is an excursion set, and the maze cell makes that starker (0.480 vs 0.110);
- the parent-versus-neighbour gap is a property of the excursion-set definition too — it collapses by 0.21–0.38 when the definition
  changes, and the collapse is not smaller in the cell where heredity itself is largest.

The line's central sentence therefore gains a qualifier it did not have this morning: the maze cell is *more* lineage-specific and
*less* basin-specific than the sparse sample suggested. Both point the same way — what is inherited here is an excursion set, and the
topography of the field is the stage, not the message.

## Caveats

- Ten worlds per cell, one box, one grid, one `k`, one cut (0.20); per-cell coefficients are on 1 779–2 211 pairs.
- The worlds are X105's, not a new replication: the X108 series draws no new randomness (verified on seed 301: identical `series` and
  `uid_pairs`), so this is a re-measurement, not an independent sample.
- Basin coverage is 0.937 at 0.040 rather than 1.000: the remaining pairs lose their peak field for reasons the analysis counts but
  does not explain (X102's coverage was 0.839 on the same cell, so the field density was the limiting factor and is now mostly gone).
- X101's and X102's aggregates now exist in two versions (sparse and dense). Both stay in git: the sparse one is the registered
  original, the dense one is the correction, and the reports say which is which.

## Next

- **X96 (owner-approved, pilot registered):** the second diffusive species, the only untried scale channel.
- The ladder's two versions should be cited together from now on; a claim that quotes 0.300 / 0.174 at the basin definition is
  quoting a sparse-series number.

доска: принято 0, отклонено 0, отложено 0.
