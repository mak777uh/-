# X113b / X113c — the generation advantage is speed, not arithmetic

**Plans:** [`2026-11-03-x113b-depth-rate-plan.md`](2026-11-03-x113b-depth-rate-plan.md) (00:16, **void**),
[`2026-11-03-x113c-depth-rate-plan.md`](2026-11-03-x113c-depth-rate-plan.md) (00:26, the corrected control).
**Aggregate:** `l1_field_x113c_depth_rate.json`. Same pairs as X113, no new runs.

## X113b voided on a control that did not fit its own sample

A *rate* needs a usable lifetime, so the sample is restricted to uids with `life ≥ 50` steps: 83 of 1 087 uids excluded in the lattice, **369 of
877** in the maze. X113b then required the raw-depth contrast on that filtered sample to reproduce X113's unfiltered +1.479 / +2.213 within 5 %;
it came back at +1.351 / +1.987 (8.6 % and 10 % lower). That is the borrowed-control-band error the X85 rule forbids, committed by the plan and
not by the data.

X113c keeps the measurement and fixes the control: the filter's effect is measured **directly**, by computing the depth contrast on both
samples in the same run and allowing a 15 % shift.

## The result

| cell | usable uids (excluded) | rate contrast: generations per 1 000 steps | 95 % CI | ρ(area, rate) | per-division contrast | 95 % CI |
|---|---|---|---|---|---|---|
| 0.030 | 1 004 (83) | **+6.06** | **[5.03, 7.08]** | **0.414** | **+0.162** | [0.146, 0.180] |
| 0.040 | 508 (369) | **+18.96** | **[14.89, 23.30]** | 0.115 | **+0.124** | [0.105, 0.144] |

Registered verdict: **size buys speed.** In both cells the larger sister's line gains generations per unit time with an interval far from zero,
and `ρ(area, rate)` clears the 0.10 bar (0.414 and 0.115). The **per-division** contrast is also positive and excludes zero in both cells, so the
advantage is not produced by the number of divisions alone either: per child, the larger sister's line still goes deeper.

## What the day now says about consequence

Three statements, each with a different strength:

1. **Size is inherited** — ρ₁ = 0.548 / 0.480 on the dense series, and the room correction is 0.069 (X107/X109).
2. **Size is a lineage property that spans a generation** — the larger sister's granddaughters are individually larger (median 98 % of the mean,
   branch counts within 4 %; X97/X97b).
3. **Size buys generations, and it buys them at a faster rate** — +1.48 / +2.21 generations (X113) and +6.1 / +19.0 generations per 1 000 steps
   (X113c), with depth *negatively* correlated with lifetime.

So the chain the line has been trying to close since the morning is closed **in one currency**: a medium that transmits a trait faithfully also
pays for it in generations. What remains open is whether that payment matters for persistence — generations are a proxy for propagation, not for
survival, and the maze is where the lifetime advantage reverses.

## Caveats

- The maze filter excludes 42 % of uids (short-lived ones), so its rate contrast rests on the longer-lived half; the lattice loses 8 %.
- `rate = depth / life × 1000` is a ratio of two noisy quantities; the bootstrap intervals are on the paired sister differences, which is the
  right object, but they do not propagate measurement error in `life`.
- Depth is truncated by the 6 000-step horizon (median depth 3), so rate is an average over the run, not a steady-state rate.
- One seed set, one box, one grid; areas at the 0.20 cut (X112b: about a tenth of correction).

## Next

- The remaining open question is the one this currency cannot answer: does a faster-propagating line **persist** better? The candidates are
  survival of the whole lineage to the horizon and recovery after a perturbation; both need runs, not logs.

доска: принято 0, отклонено 0, отложено 0.
