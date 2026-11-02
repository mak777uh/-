# X90 — void by its own control: at `F = 0.050` even twelve thousand steps give no division in the median world

**Date:** 2026-11-02, 11:55 MSK. **Experiment:** X90 (twelve thousand steps at the fading edge).
**Preregistration:** `reports/2026-11-02-x90-trickle-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x90_f0{48,49,50}_pattern_s271-278.json` (24 runs), fields `_x90_fields/`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x90_trickle.json`.

## Registered verdict

**Void.** The control required the `F = 0.050` cell to reach a median of at least one event per world at the doubled horizon, so that a
ratio could be taken at all. It reached **0**. A ratio against a median of zero does not exist, and the series therefore cannot decide
"stopped" against "slow" at that inflow.

## What it did measure, descriptively

| `F` | pairs per world at 6 000 (X88/X89) | at 12 000 (this run) | ratio | components |
|---|---|---|---|---|
| 0.048 | 2.0 | **2.0** (range 0–4) | 1.0 | 1.0, β₁ > 0 in 8/8 |
| 0.049 | 1.0 | **2.0** (range 0–2, mean 1.25) | 2.0 | 1.0, β₁ > 0 in 8/8 |
| 0.050 | 0.3 | **0.0** (range 0–2, mean 0.75) | — | 1.0, β₁ > 0 in 8/8 |

- At **0.049** the count doubles with the horizon, so reproduction there is rare but continuing.
- At **0.048** it does not double — all events happen within the first 6000 steps, i.e. that world's divisions are a **transient**, not a
  steady rate.
- At **0.050** the median is zero at 12 000 steps: six events across eight worlds, and most worlds never divide at all.

So the honest picture is not "a rate that decays smoothly" but "**a transient whose duration shrinks with inflow**": at 0.048 the
transient is over before 6000 steps; at 0.049 it is still running at a low level; at 0.050 it is over before the run starts producing
anything countable.

## The design error, which is mine

The control was written as "median at least one event", which is satisfied only when there is something to compare — so the cell where
the question matters most is exactly the cell that voids the series. The right instrument for "does the last trickle stop" is a **rate
over a long horizon with enough worlds**, not a ratio of small-integer medians: at 0.75 events per world and 8 worlds, the Poisson
uncertainty on the cell mean is ±0.3, which is the size of the whole effect.

A decisive answer would need either ~50 000 steps at 0.050 (about four hours of GPU for one cell) or a bigger box (more components, more
chances to divide). Neither is worth it for the purpose: the heredity line needs hundreds of pairs, and at 0.050 it has none at any
horizon short of absurd. The phenomenological question is answered well enough by what is here — **above 0.049 the medium stops dividing
in practice** — and the write-up should say "in practice" rather than "in principle".

## What stands from this series

- The three cells are the same regime as X89: single component, β₁ > 0 in all 24 worlds, components 1.0. The maze does not die; it stops
  dividing.
- The transition from "divides sometimes" to "does not divide" happens between 0.049 and 0.050, and it is visible only as a count of
  rare events — which is why the honest statement is a bound, not a rate.

доска: принято 0, отклонено 0, отложено 0.
