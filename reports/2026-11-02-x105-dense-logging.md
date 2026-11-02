# X105 — dense logging: the maternal decay is real, and the maze heredity was being underestimated

**Plan:** [`2026-11-02-x105-dense-logging-plan.md`](2026-11-02-x105-dense-logging-plan.md) (written at 17:10, series started 17:11:53).
**Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x105_dense.json`. Twenty new runs, seeds 301–310, two inflows,
`--sample-every 10` instead of 50.

## What was at stake

Every maze number in this line rested on structures that lived long enough to be logged twice: at `F = 0.040` **35.3 %** of
ancestor–daughter pairs had a member that never appeared in the component log, because the median lifetime is 89 steps and the
logging interval was 50 (X103's diagnosis). Two claims were therefore conditional: the maternal decay of X103c (`−0.367`, 10/10
worlds) and the crowding term of X103d/X106.

## The manipulation did what it was for

| inflow | pairs | logged | structural loss before → after | median distance (cells) | heredity ρ(mother, daughter) |
|---|---|---|---|---|---|
| 0.030 | 2 211 | 2 164 | 0.065 → **0.021** | 4.57 | **0.548** |
| 0.040 | 1 951 | 1 779 | 0.353 → **0.088** | 9.12 | **0.480** |

The maze cell's structural loss falls by a factor of four, and the lattice cell's by three. Among loggable pairs the instrument is
available for 100 % in both cells.

## Results

| inflow | ρ(distance, daughter area) | worlds negative | crowding ρ | worlds positive | partial area given distance |
|---|---|---|---|---|---|
| 0.030 | −0.041 | 8/10 | **+0.367** | **10/10** | 0.600 |
| 0.040 | **−0.329** | **10/10** | +0.182 | 9/10 | 0.648 |

Registered verdicts, both from the rule written before the series:

- **the maternal decay is robust to dense logging** — `−0.329` against X103c's `−0.367`, ten worlds out of ten, per-world values
  from −0.185 to −0.441. The sign control in the lattice cell also held (−0.041, inside the ±0.15 band).
- **crowding is robust** — `+0.367` against X103d's `+0.358`, ten worlds out of ten.

So neither of the two non-ancestral terms was an artefact of the visible subset. What changed is the *third* number:

**The maze heredity was being underestimated.** `ρ(mother, daughter)` is **0.480** at dense logging against **0.384** at the sparse
one — a quarter larger. That is the direction X92's area–lifetime relation predicted: the structures that made it into the sparse
sample are the long-lived ones, and long life and large area are inversely related in the maze, so the visible pairs were a
*compressed* subset. The lattice cell barely moves (0.531 → 0.548).

This makes the honest hierarchy of the day's numbers sharper: the maze cell's heredity is **0.480**, not 0.384, and the earlier value
was a lower bound produced by the logging interval rather than by the medium.

## What this does and does not change

- **Does**: the heredity ladder of X101 and the specificity of X102 were measured on the sparse series. Their *ordering* (excursion
  set > basin > core) is a property of definitions applied to the same pairs, so it should survive; their *levels* at 0.040 are
  probably also understated. Re-running X101/X102 at dense logging is now a cheap, well-posed analysis (same script, `x105` prefix).
- **Does not**: any conclusion about the lattice cell, whose structural loss was already small (0.065 → 0.021, heredity 0.531 →
  0.548).
- **Is still open**: the dense series is a *new* set of worlds (the X85 rule — logging density is physical), so this is a replication
  at a new density, not the same twenty runs at finer resolution.

## Caveats

- Seeds 301–310 are new; the comparison with X100 is a replication, not a paired refinement.
- Both cells have ten worlds; per-world coefficients are on 136–389 pairs.
- The crowding coefficient in the maze rose from 0.103 to 0.182 (9/10 worlds). It is still weaker than the lattice's 0.367 and still
  below the 0.20 floor this line uses for a "real" coefficient, so X106's reading — room matters in the lattice and not in the maze —
  is unchanged but no longer as sharp.
- All areas are at the 0.20 cut (X99).

## Artifacts: the dense logs are 2.4 MB per run, so git gets a projection

Twenty dense runs are 49 MB, and this repository's rule is that GitHub is thin memory. `scripts/compact_field_series.py` writes
`x105_*.compact.json` (5.9 MB in total, 15 % of the source) containing everything the log-only analyses read — `params`, `uid_pairs`,
and per logged step `[uid, area, cx, cy]` with positions rounded to 0.1 cell — plus the sha256 of the full run, so a reader can tell
the derivative from the original. Verified: recomputing from the compact files reproduces this aggregate exactly (`ρ(distance)` −0.041
and −0.329, heredity 0.548 and 0.480, 2 164 and 1 779 pairs). The full logs and the saved fields (`_x105_fields/*.npy`) stay on the
lab machine, exactly as `_x100_fields` does; analyses that need the fields (X101/X102) are re-run locally, which their aggregates
record.

## Next

- **X108 (registered, analysis):** rerun X101's definition ladder and X102's specificity on the dense series. Same scripts, the
  `x105` prefix; the question is whether the ladder's levels at 0.040 move up by the same quarter as the heredity did, and whether the
  basin gap (0.017 / −0.010) comes back.
- Dense logging should become the default for any future series in this line; the cost is ~105 s per run, unchanged, because the
  integration dominates.

доска: принято 0, отклонено 0, отложено 0.
