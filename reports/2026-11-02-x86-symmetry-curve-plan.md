# X86 — placing the symmetry curve: how much of `s(F)` survives twenty worlds per inflow?

**Why.** X84 measured a smooth rise of the symmetry `s` from 0.38 at `F = 0.025` to 0.92 at `F >= 0.040` and this became the new
backbone of the field line (one period, a symmetry coordinate). X85 then voided itself by borrowing a control band from X71 — and the
reason was not seed scatter: `--sample-every` is a **physical** parameter (trait mutations are drawn at every sampled step), so X71's
1000-step worlds and X85's 50-step worlds are different regimes. Within the 50-step regime the levels are 0.603 (X82, 5 worlds) and
0.671 (X85, 8 worlds) at `F = 0.030`, while the 1000-step regime gives 0.516.

So the curve's **direction** replicates across everything and its **level** is unresolved at the precision the line now needs. Every
memory number in this line is reported against `F`, and `s` was proposed as the better x-axis; placing that axis is the prerequisite
for the next heredity test, which needs no new runs once the worlds exist.

This series does exactly one thing: measure `s` at three inflows with **twenty worlds each, in one logging regime**, and report the
curve with its between-world spread.

## 1. Manipulation is connected

Three inflows (`F = 0.025`, `0.030`, `0.035`), twenty jittered worlds each (seeds 201–220), one logging density (50 steps) shared
with X82 and X85 so the numbers are comparable. The manipulation is not a flag on `s`; `s` is measured per world from the saved
field, and the design's power comes from that world-to-world spread. Connectedness is checked by the spread: a cell whose `s` range is
narrower than 0.05 has nothing to place and is void.

## 2. Positive control fires (numeric)

The instrument must see the curve it saw before. **The control fires if** the three cell medians are ordered
`s(0.025) < s(0.030) < s(0.035)` **and** `s(0.035) − s(0.025) >= 0.15`, which is what every previous series shows (1000-step regime:
0.38 → 0.52 → 0.78; 50-step: 0.40 → 0.67 → 0.87). A second, weaker check: the 0.030 median must land in **[0.50, 0.78]**, the envelope
of the two existing 50-step series (0.603 and 0.671) widened by their own spread. If the ordering or the gap fails, the series is void
— the instrument, not the world, would be in question.

## 3. Readout exists and varies

Per world: `s` (angular, `P_diag/(P_diag+P_axis)` at the prescribed diagonals), the axis period `q'`, field std, components, and the
depth readout (`rho1..3`, per-world `lambda` and half-life) so the same worlds can serve the heredity question later without a new run.

The reported quantity is the **median of twenty** with its interquartile range and its full range, per inflow, plus the world-level
correlation of `s` with `q'` (does a more locked pattern also have a different period? X84 says no, and this tests it with power).

## 4. Sensitivity arithmetic

Observed within-cell `sd(s)` is 0.07–0.10 (X85 at 0.030: 0.503–0.808). With twenty worlds the standard error of a cell median is
therefore **0.016–0.022**, so a gap of 0.05 between inflows is 2.3–3.1σ and is the declared resolution; the 0.15 gap required by the
control is 7σ. Cost: 60 runs at ~95 s ≈ **95 minutes** of the GPU lane, ~2.5 GB of fields.

## 5. Refusal rule (registered before the run)

**Void** if a cell has <10 components, <400 lag-1 pairs, a dead field (std < 0.01), an `s` range narrower than 0.05, or if the §2
control does not fire.

**Curve placed** if the three medians differ by at least 0.05 pairwise in the expected direction; then the values are quoted with
their standard errors as the axis for the memory work.
**Curve flat within resolution** if two adjacent medians differ by less than 0.05 — then `s` is not a usable x-axis at this precision
and the memory line keeps `F` as its coordinate.
Anything else is **inconclusive**, printed in full.

## Design summary

| factor | value |
|---|---|
| inflows | `F = 0.025`, `0.030`, `0.035`, `k = 0.06` |
| pattern | single scale, `--hetero-scale 12.0`, `--hetero-amp 0.5`, `const_ones` signal (as X71/X85) |
| worlds | **20 per cell**, seeds 201–220, `--init-jitter` |
| logging | **`--sample-every 50`** (the X82/X85 regime; stated because it is physical) |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| field | saved at 6000, `_x86_fields/` |
| artifact | `morphogenesis/experiments/L1_field/x86_f{025,030,035}_s201-220.json`, aggregate `l1_field_x86_symmetry_curve.json` |

## Checklist before the series

- [x] connected (`s` measured per world; narrow spread voids a cell)
- [x] positive control fires (numeric ordering and gap, §2)
- [x] readout exists and varies (0.40 / 0.67 / 0.87 already seen)
- [x] sensitivity computed (§4: SE 0.016–0.022, resolution 0.05)
- [x] refusal rule written, including "curve flat within resolution" as a real outcome
- [x] logging regime fixed and declared (the X85 lesson)

## Status

Registered 2026-11-02 05:13 MSK, before the series. Sixty runs, ~95 minutes.

доска: принято 0, отклонено 0, отложено 0.
