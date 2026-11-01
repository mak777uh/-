# X72c — branch heredity, third attempt: band powers instead of a class, ten worlds instead of five

**Why a third attempt.** Two earlier attempts failed for two different reasons and both are now understood. `X72` used a
stand-in (nearest-neighbour spacing) that measured packing density rather than wavelength — an instrument failure that the
contract now forbids. `X72b` used a valid instrument (48-cell local spectrum, correlation 0.90–0.99 with the global peak) but a
**class**: the argmax landed on the dominant branch in 85–100 % of structures, so parent–daughter concordance and the
surrogate both sat at the ceiling (0.90–1.00) and the question could not be asked. The diagnosis was explicit: the branch is a
**world-level mixture**, not a per-structure class, so the readout has to be continuous.

X71b and X71c fixed the other half of the design: the coexistence is stationary over 24 000 steps and sits in a narrow band
around `F = 0.035` (`k = 0.06`), with second-mode shares of 0.19–0.28 at the boundary. A heredity measurement therefore has to
run at that inflow, with enough worlds to catch the minority cases that carry the information.

## 1. Manipulation is connected

No manipulation is applied to the world; the manipulation is the **readout**. Connectedness is the instrument control
carried over from X72b, re-measured here: the local band powers must track the global spectrum — the correlation between the
median local `p_wide` and the global share of the q = 8 mode must be **≥ 0.5** in each world and the local measure must
separate the band cells (`F = 0.030` → wide dominant, `F = 0.040` → narrow dominant) in the same protocol.

## 2. Positive control fires

Three numbers, all before the heredity statistic is read.

1. **Instrument tracking:** median over worlds of `corr(local p_wide, global wide share)` **≥ 0.5**, and the spread of `p_wide`
   across structures within a world **≥ 0.20** (a constant readout cannot correlate with anything).
2. **Both regimes present:** in the pooled data, at least **15 %** of events must have a minority parent (`p_wide < 0.5` when
   the world is wide-dominant, or the reverse) — these are the only events where a class could differ, and the earlier
   attempts died precisely here.
3. **Ceiling avoided:** pooled `p_wide` must lie in **0.15–0.85**; outside that range the readout is saturated and the
   correlation is again unmeasurable.

## 3. Readout exists and varies

Per structure and per snapshot, a 48-cell window around its centroid (periodic wrap), radial spectrum, and the **band powers**.
Units are the window's, not the box's: a 12.0-cell wavelength appears in a 48-cell window at `q_win = 48/12 = 4` and an 8.73-cell
one at `q_win = 48/8.73 ≈ 5.5`, so `p_wide` = the fraction of local power in `q_win = 3–4` and `p_narrow` = the fraction in
`q_win = 5–6`, with `p_other = 1 − p_wide − p_narrow`. (Written after the first draft used the 96-box bin numbers, before any run.)
All global-spectrum references elsewhere in this plan are in 96-box bins; the two are kept apart deliberately, because mixing
them was the arithmetic that produced the X58 mistake.

Per division event (`uid_pairs`; birth from `uid_outcomes.first`), parent values come from the last snapshot **before** the
birth and daughter values from the first **at or after** it (fields every 50 steps, so the gap is ≤ 50 steps).

Two statistics:

- **continuous:** Spearman `rho` between parent `p_wide` and daughter `p_wide` over all events, per world and pooled;
- **discrete, on minority events only:** concordance of the dominant band (parent's dominant band equals daughter's), compared
  with the same statistic computed on a nearest-distance non-parent surrogate.

## 4. Sensitivity arithmetic

Ten worlds at `F = 0.035`, 6000 steps, fields every 50 steps; X72b measured 88–102 s per run, so the series is ~17 minutes.
Each world yields ~175 events (X70 measured 175–234), so ~1 700 events pooled; with ~20 % minority events that is ~340
informative events, and a binomial band at 95 % over 340 is about ±0.05 — enough to see a 0.15 difference. The continuous
correlation uses all ~1 700 events; for `rho = 0.15` the Fisher band is about ±0.05, so 0.15 is the smallest effect worth
calling.

## 5. Refusal rule

**Void (instrument)** if control 1 fails in more than two worlds, or control 3 fails. **Underpowered (not a null)** if fewer
than 50 minority events are pooled: the discrete statistic is then reported as unmeasured, and only the continuous one is
judged. **Supports branch heredity** if `rho ≥ 0.15` pooled **and** positive in **≥ 8 of 10 worlds**, **and** the observed
concordance exceeds the surrogate's by **≥ 0.15** on the minority events, **and** `rho` exceeds the p95 of a within-world
permutation of parent values (2000 draws). **Not supported** if pooled `rho ≤ 0` or the surrogate is higher. Anything else is
**inconclusive**, with all numbers printed.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

## Design summary

| factor | value |
|---|---|
| inflow | `F = 0.035`, `k = 0.06` (the X71b/71c boundary cell) |
| worlds | **10**, `--init-jitter`, seeds 171–180 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every 50 steps; **fields every 50 steps** (`_x72c_fields/`, not committed) |
| readout | 48-cell window spectrum → `p_wide` (q 7–9), `p_narrow` (q 10–12) |
| statistics | Spearman on band powers; concordance on minority events; nearest-distance surrogate; permutation null |
| artifact | `morphogenesis/experiments/L1_field/x72c_pattern_s171-180.json`, aggregate `l1_field_x72c_branch.json` |

## Status

Registered 2026-11-01 23:40 MSK, before the series. Ten runs, ~17 minutes. Third attempt at the same question, with the
instrument and the statistic both changed — which is why the criteria are re-registered rather than reused.
