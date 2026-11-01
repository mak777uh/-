# X71c — how wide is the multistable band? Half-steps either side of F = 0.035

**Question.** X71 sampled the inflow every 0.005 and found coexistence in exactly one cell: `F = 0.035` mixed, `F = 0.030`
and `0.040` single-valued. X71b showed that coexistence is stationary over 24 000 steps. What is still unknown is the
**width** of the window: one grid step of the sweep is not a measurement of it, it is the resolution of the sweep. If the band
is half a step wide, the earlier statement "one step" is an artefact of sampling; if it is 0.004 wide, the statement is a
measurement.

## 1. Manipulation is connected

The manipulation is the inflow, and it is known to move the pattern: X71 measured peak positions 8 → 11 bins across
`F = 0.025…0.055`, and X71b showed those positions are stationary for 24 000 steps at the boundary. The connectedness check
for this series is that the same response appears again at the two new inflows — the peak position at `F = 0.033` or `0.037`
must differ from at least one of the existing neighbours, otherwise the finer sweep is not resolving anything new.

## 2. Positive control fires

The positive control is that the two new cells reproduce the **already known** states of their neighbours within the same
run protocol: `F = 0.033` must be single-valued or mixed (a `struct` state), never a uniform field, and the same for
`F = 0.037`. A cell that lands in a degenerate state (peak at q = 1, no structure) is reported as such and excluded — the
question is about a band of the patterned regime, not about where the regime ends.

## 3. Readout exists and varies

Identical to X71 and X71b, deliberately: the radial structure factor of `v` at 24 000 steps, peak position, peak share, and
the strongest second mode at least three bins away; a world is **mixed** if both modes carry ≥ 0.2 of the power, **collapsed**
if one carries > 0.6 and no second mode reaches 0.2.

## 4. Sensitivity arithmetic

Two inflows (`0.033`, `0.037`) × five jittered worlds = ten runs of 24 000 steps. A 24 000-step run took 370–415 s in X71b,
so the series is about 65 minutes.

The decision is a count, not a p-value: with five worlds per cell, a cell is **mixed** if at least four of five worlds are
mixed, following the X71b rule. The width is then reported as an interval: the span of inflows whose cells are mixed, with
the honest statement that the sweep's resolution is now 0.002 and the band's edges are known to ±0.002.

## 5. Refusal rule

The series is declared **insufficient** if fewer than four worlds per cell are pattern-bearing (control §2), for either cell.
Otherwise:

- both new cells mixed → the band is at least 0.033–0.037 (three cells wide), and the earlier "one step" is a sampling
  artefact;
- one new cell mixed, the other single-valued → the band is at least 0.033–0.035 or 0.035–0.037 (two cells), and the width is
  reported as `0.002 < width < 0.005`;
- neither mixed → the band remains one sweep step (`0.030 < F < 0.040`), i.e. width ≤ 0.005, and the fine sweep confirmed
  X71's original resolution statement rather than widening it.

All three outcomes are informative, which is why the series is worth its hour.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.033`, `0.037` (`k = 0.06`), the two half-steps around the X71 boundary cell |
| arms | heterogeneous only (`amp 0.5`, static unit signal) |
| worlds | 5 per inflow, `--init-jitter`, seeds 171–175 |
| grid, step, horizon | 96, `dt = 1.0`, 24 000 |
| logging | components every 1000 steps; fields at 24 000 (`_x71c_fields/`) |
| readout | radial structure factor, X71/X71b two-mode rule |
| artifact | `morphogenesis/experiments/L1_field/x71c_f<F>_pattern_s<seed>.json`, aggregate `l1_field_x71c_width.json` |

## Status

Registered 2026-11-01 21:50 MSK, before the series. Ten runs, ~65 minutes.
