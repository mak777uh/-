# X113b — is the generation advantage faster propagation or more division events?

**Why.** X113 found that the larger sister's line reaches **+1.479** and **+2.213** more generations, with the size–depth partial at 0.459 / 0.340
and depth *negatively* correlated with lifetime. Two mechanisms can produce that count:

1. **faster propagation** — the line converts time into generations at a higher rate, i.e. generation time is shorter;
2. **more division events per cell** — a larger structure simply has more cells that can divide, so it accumulates generations without being
   faster.

The number that separates them is a **rate**: generations per 1 000 steps of lifetime. If the rate advantage survives, size buys *speed*; if it
vanishes, X113's count is arithmetic.

## 1. Manipulation is connected

The same uids and sister pairs as X113 (X108's dense logs). Per uid with descendants: `depth` (as in X113), `life` from the component log, and
`rate = depth / life × 1000`. Connectedness: at least **300 uids** per cell with `life ≥ 50 steps` (one logged interval) — a rate from a
shorter life is noise and is excluded, and the excluded count is reported.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **Heredity on the same pairs** `≥ 0.35` in both cells (0.548 / 0.480 measured); the control **fires if** both hold.
2. **The X113 count reproduces:** the sister contrast in raw depth must reproduce +1.479 and +2.213 generations within 5 %, i.e. this is the
   same sample measured a second time, not a new one.

## 3. Readout exists and varies

Per cell: the sister contrast in **rate** (paired, bootstrap 95 % interval), `ρ(area, rate)`, the median rate, and the same contrast for
**generations per division** (`depth / subtree`), which is the arithmetic-versus-speed question asked a second way. Variation exists: the
depth advantage is 1.5–2.2 generations and lifetimes span a factor of several, so the rate varies over a wide range.

## 4. Sensitivity arithmetic

1 142 and 1 195 sister pairs; the rate is noisier than a count (a ratio of two noisy quantities), so the declared resolution is **0.10
generations per 1 000 steps** with a bootstrap interval excluding zero, and the same 0.10 for generations per division. A rate effect below
that is reported as unresolved rather than absent.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 uids with a usable rate, if heredity misses 0.35, or if the raw-depth contrast does not reproduce X113
within 5 %.

**Size buys speed** if the rate contrast is positive with the interval excluding zero **and** `ρ(area, rate) ≥ 0.10` in both cells.
**The count was arithmetic** if the rate contrast's interval contains zero or `|ρ(area, rate)| ≤ 0.05` in both cells.
**Mixed** otherwise, with the two cells reported separately — the maze is where X93's lifetime advantage reverses, so the two can disagree.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs, the same pairs as X113 |
| readouts | sister contrast in generations per 1 000 steps and per division; `ρ(area, rate)` |
| controls | heredity ≥ 0.35; raw-depth contrast reproduces X113 within 5 % |
| artifact | `E09_pond/l1_field_x113b_depth_rate.json` |

## Checklist

- [x] connected (300 uids with life ≥ 50; excluded count reported)
- [x] positive control numeric (heredity ≥ 0.35; X113 reproduced within 5 %)
- [x] readout exists and varies (depth advantage 1.5–2.2; lifetimes span a factor of several)
- [x] sensitivity computed (§4: resolution 0.10 generations per 1 000 steps)
- [x] refusal rule written, with "the count was arithmetic" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-03 00:16 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
