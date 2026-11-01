# E6q: the prediction failed, and the reason is better than the prediction

1 November 2026, 06:25. Twenty runs, two regimes, no niches. Preregistration:
[`2026-11-01-e6q-no-niches-plan.md`](2026-11-01-e6q-no-niches-plan.md), written and committed before the first run.

## The prediction and its verdict

**Predicted:** with the inflow made homogeneous, the frequency-dependent arm ends with fewer than 2.5 structures (the
heterogeneous median from E6p), or fixates in at least 4 of 10 seeds.

**Observed:** 2.0 structures against 2.5, fixation 0.2 against 0.2 — and the paired difference is **−1.0 in only 5 of 10
seeds**. The per-seed differences run from −23 to +1, so the medians differ while the seeds do not agree.

**Verdict: prediction not supported**, by the criterion fixed in advance (median drop with ≥ 8/10 seeds agreeing). This
is a negative result and it is reported as one; the count of structures is too unstable across seeds for a one-structure
median shift to mean anything.

## What the run did show, and it was not the preregistered quantity

| world | arm | structures | `s` at end | fixation |
|---|---|---|---|---|
| heterogeneous | `beta = 0` | 36.0 | 1.077 | 0.0 |
| heterogeneous | `beta = 0.2`, `freq_dep = 1` | 2.5 | **1.950** | 0.2 |
| homogeneous | `beta = 0` | 4.0 | 0.960 | 0.0 |
| homogeneous | `beta = 0.2`, `freq_dep = 1` | 2.0 | **1.119** | 0.2 |

> **Caveat added at 06:35.** The eta = 0 control has no seed-dependent dynamics: its structure series is one
> deterministic trajectory repeated ten times, so "4.0 structures" is a constant, not a distribution. The paired
> comparison below is between the two **treatment** arms, which do vary. See
> [2026-11-01-seed-reaches-only-the-trait-channel.md](2026-11-01-seed-reaches-only-the-trait-channel.md).

The trait still drifts without niches — **+0.204 against the homogeneous control, 9 of 10 seeds positive**, just over the
+0.20 bar — so the survival channel is not inert and the series is not refused by its own rule 3.

But the *size* of the drift collapses: **+0.835 with niches, +0.204 without**, a factor of four. Selection does not need
the heterogeneity to exist; it needs it to matter.

## What that does to the E6p sentence

E6p concluded: *selection is easy, coexistence is a property of the environment.* E6q splits that sentence in two and
finds the environment on both sides:

1. **Drift:** exists in both worlds, but four times larger with niches. Heterogeneity amplifies selection.
2. **Coexistence:** the structure count falls from 36 to 2.5 with the survival channel regardless of niches, and the
   niche effect on that count is within seed noise. So the earlier "environment decides how many niches exist" was too
   strong for this readout: the trait channel, not the environment, is what destroys the many-structure state.

That is a correction to our own sentence from two hours ago, produced by the test we wrote for it.

## What is not claimed

- The +0.204 is a secondary, post-hoc observation from one series (the primary criterion was about structures). It
  clears the effect bar but it was not the preregistered endpoint.
- No p-values; the seeds are the unit and the sign rule was fixed in advance.
- 6000 steps, grid 96, one trait channel.

## Artifacts

`morphogenesis/experiments/L1_field/e6q_{ctrl_h,survfd_h}_s{171..180}.json`, index `e6q_series_index.json`, aggregate
`morphogenesis/experiments/E09_pond/l1_field_e6q_niches.json`, compared against `l1_field_e6p_selection.json`. Scripts:
`scripts/e6q_series.py`, `scripts/e6q_analyse.py`.

## Next

The count-of-structures readout is too noisy for this design — the honest next design compares the **distribution** of
structure counts across seeds rather than their median, or uses the count at several times, which the saved
`series` already allows without a new run.
