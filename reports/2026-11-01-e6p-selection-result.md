# E6p: selection works through survival, and frequency dependence stops fixation

1 November 2026, 05:50. Thirty runs, three regimes, ten paired seeds, artifacts in git. This re-asks the question of
`E6c`/`E6d`/`E6e`, whose evidence no longer exists (`_hourly/`, 36 files, never committed), so the conclusion is now
checkable rather than remembered.

Preregistration: [`2026-11-01-e6p-selection-regimes-plan.md`](2026-11-01-e6p-selection-regimes-plan.md). Anchor:
the frequency-dependent arm on seed 171 reproduces `x60_pattern_s171` **bit-for-bit**, so the pipeline is the same one
that produced the topology result.

## Result

| arm | `s` at end | spread between structures | splits | `r` | structures | share of seeds fixed |
|---|---|---|---|---|---|---|
| `beta = 0` (control) | 1.077 | 0.437 | 89 | 0.931 | 36.0 | 0.0 |
| `beta = 0.2`, `freq_dep = 0` | 1.487 | **0.000** | 22.5 | 0.775 | **1.0** | **0.9** |
| `beta = 0.2`, `freq_dep = 1` | **1.950** | 0.201 | **311** | **0.976** | 2.5 | 0.2 |

Paired drift of mean composition against the control, seed by seed:

- **survival channel, no frequency dependence: +0.484, 10/10 seeds positive** — meets the pre-declared bar (+0.20, 8/10);
- **frequency-dependent survival: +0.835, 9/10 seeds positive** — also meets it, and is the larger of the two.

## What this settles

**1. Selection needs a channel without a matching cost.** The growth channel (`E6c`) produced inheritance (r = 0.97) and
variation, but no directional drift, because fast growth eats its own food. The survival channel produces drift in 10 of
10 seeds. That conclusion is now backed by files in the repository.

**2. Strong directional selection fixates.** With survival and no frequency dependence, 9 of 10 seeds end with **one**
structure and the between-structure spread collapses to exactly zero. Fixation was not a hypothesis in the prereg — it is
the refusal-rule item that would have invalidated the arm, and it happened.

**3. Frequency dependence stops fixation but does not restore diversity.** The frequency-dependent arm keeps several
structures (median 2.5, fixation in 2 of 10 seeds) and drifts further (+0.835 against +0.484). Compared with the control's
36 structures, however, 2.5 is a monoculture with two survivors, not a community.

**4. The two axes come apart.** The strongest drift and the greater diversity appear in the *same* arm, so "more selection
means less diversity" is false here: frequency dependence raises drift and holds a few structures simultaneously. What it
cannot do is keep the control's richness.

## What this does to the line's overall story

The pond line reached the same shape from the other side (§10by): diversity grows from **environmental heterogeneity**,
not from selection strength. Here the field adds the mechanism — frequency dependence turns a winner-take-all into a
standoff, while the environment decides how many niches exist at all.

That is the closest thing to a general sentence this project has produced about its own medium: **selection is easy,
coexistence is a property of the environment.**

## What is not claimed

- No p-values: ten autocorrelated trajectories would overstate precision; the criterion was a sign rule and an effect
  threshold, both fixed before the data.
- "Fixation" is defined operationally (median structures ≤ 1), not dynamically.
- The trait changes decay only; nothing here says a *different* trait could not be selected through growth under other
  parameters.
- 6000 steps, grid 96: nothing about longer horizons or finer grids.

## Artifacts

`morphogenesis/experiments/L1_field/e6p_{ctrl,surv,survfd}_s{171..180}.json` (30 files), index
`e6p_series_index.json`, aggregate `morphogenesis/experiments/E09_pond/l1_field_e6p_selection.json`. Scripts:
`scripts/e6p_series.py`, `scripts/e6p_analyse.py`.

## Next hypothesis

If coexistence is a property of the environment rather than of the trait, then **turning niches off should collapse
diversity even with frequency dependence**: the same `survfd` arm on a homogeneous inflow should end with fewer structures
than the 2.5 measured here. That is one arm, ten seeds, twenty minutes — and it is the direct test of the sentence above.
