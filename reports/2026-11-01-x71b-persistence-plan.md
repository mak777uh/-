# X71b — does the two-branch coexistence survive a long horizon, or is it a transient?

**Question.** X71 found that at `F = 0.035`, `k = 0.06` the field carries two wavelengths (12.0 and 8.73 cells) at the same
parameters, and that every world of that cell held both modes with at least a fifth of the spectral power each at
`t = 6000`. That is a statement about one horizon. Two readings fit it equally well:

- **bistability** — both modes are stable, and a world keeps both indefinitely;
- **transient coexistence** — the field is still choosing, and by a longer horizon one branch wins.

X70 measured heredity at this same inflow, so the difference matters: a transient would mean the "discrete branch" story has
a clock on it.

## 1. Manipulation is connected

No new manipulation: the inflow stays at the X71 boundary cell and the initial conditions are seed-dependent
(`--init-jitter`). The connectedness check is the one X71 used — the field must be in the mixed regime at `t = 6000` — and it
is carried over as a precondition: if a world has already collapsed to one mode by 6000, it is reported as collapsed, not as
evidence either way.

## 2. Positive control fires

The control is that the run reaches the same state X71 measured: at `t = 6000` the world must be classified as **mixed** in
X71's sense (two modes with shares ≥ 0.2, or two clusters of peak position). If a world does not reproduce the X71 state at
6000, the long-horizon result about that world says nothing.

## 3. Readout exists and varies

The readout is the same one X71 used — the radial structure factor of `v` — sampled at four horizons: **6000, 12 000,
18 000, 24 000** steps, with the field written at each. Per snapshot: peak position `q*`, its share, and the strongest
second mode at least three bins away, exactly as in `x71_analyse.py`. Variation across worlds and across horizons is what the
series has to show; a readout that is constant within a world cannot distinguish persistence from collapse.

## 4. Sensitivity arithmetic

Five worlds, four horizons, 24 000 steps each. The field is 96², `dt = 1.0`, so a 24 000-step run is four times a 6000-step
run (measured 70–110 s), i.e. about 6–7 minutes per world and roughly 35 minutes for the series.

The decision does not need a new instrument: a world is **mixed** at a horizon if it has two modes with shares both ≥ 0.2
(the X71 rule, unchanged). With five worlds, "persists" means at least four of five are still mixed at 24 000. That is the
same sign-count discipline the line uses elsewhere; no p-values on five worlds.

## 5. Refusal rule

The series is declared **uninformative** if fewer than four worlds reproduce the mixed state at `t = 6000` (the precondition
fails, and the question about persistence cannot be asked of worlds that never had two modes).

It is declared **bistable** if at least four of five worlds are still mixed at 24 000. It is declared **transient** if at
least four of five have collapsed to a single mode by 24 000, and **inconclusive** otherwise. "Collapsed" means one mode
holds more than 0.6 of the power and no second mode reaches 0.2.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

## Design summary

| factor | value |
|---|---|
| inflow | `F = 0.035`, `k = 0.06` (the X71 boundary cell) |
| arms | heterogeneous only (`amp 0.5`, static unit signal) |
| worlds | 5, `--init-jitter`, seeds 171–175 |
| grid, step, horizon | 96, `dt = 1.0`, **24 000** |
| logging | components every 1000 steps; fields at 6000, 12 000, 18 000, 24 000 (`_x71b_fields/`) |
| readout | radial structure factor at four horizons, X71's two-mode rule |
| artifact | `morphogenesis/experiments/L1_field/x71b_pattern_s171-175.json`, aggregate `l1_field_x71b_persistence.json` |

## Status

Registered 2026-11-01 21:00 MSK, before the series. Five runs, ~35 minutes. This is a follow-up of a positive result, so it is
registered with its own bands rather than folded into X71's report.
