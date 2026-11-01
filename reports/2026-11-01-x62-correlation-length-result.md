# X62: the prediction was wrong, and the reason is a resonance

1 November 2026, 09:25. Fifteen runs. Preregistration:
[`2026-11-01-x62-correlation-length-plan.md`](2026-11-01-x62-correlation-length-plan.md), committed before the run.

## The prediction and its verdict

**Predicted:** divisions ordered `scale 4 > scale 12 > scale 24` — turnover tracking the density of boundaries in the
inflow, on the reasoning that finer modulation breaks the field into smaller pieces.

**Observed:**

| correlation length | divisions | parent–child pairs | `r` | structures | entropy | peak mode |
|---|---|---|---|---|---|---|
| **4** | **20** | 44 | 0.82 | 3 | 2.16 | q = 1, 0.20 |
| **12** | **308** | 682 | 0.97 | 3 | 2.27 | q = 1, 0.25 |
| **24** | **175** | 389 | 0.97 | 2 | **1.96** | **q = 6, 0.33** |

**Not supported.** The ordering is 12 > 24 > 4 — the extreme pair differs by a factor of 0.11, the wrong way, and only
1 of 5 seeds agrees with the prediction. This is a negative result and it is recorded as one.

## What the failure says, post hoc — and labelled as post hoc

The maximum is not at the finest modulation but at the **correlation length closest to the pattern's own wavelength**
(12 units). Both ends are quieter: at scale 4 the inflow varies faster than the pattern can respond, so it averages out and
the field behaves almost like a homogeneous world — 20 divisions, a third of the smooth-world figure; at scale 24 the
patches are large enough to hold a pattern, the boundaries are sparse, and turnover falls to 175.

That reads as a **resonance**: fragmentation is maximal when the environment varies on the scale the pattern wants to use.
Not "more heterogeneity, more turnover", which is what the amplitude experiment suggested and what this prediction
assumed. Amplitude controls *how strongly* the field is pushed; correlation length controls *whether the push lands on
the structures at all*.

**The spectrum agrees with the second half.** At scale 24 the peak moves off q = 1 for the first time in this line
(q = 6, share 0.33, entropy 1.96) — patches large enough to pattern do begin to pattern. At scales 4 and 12 the spectrum
stays broadband.

## Why this is worth more than the prediction

It changes the sentence from last night. "Heterogeneity buys turnover at the cost of organisation" was written from two
points on one axis (amplitude) and read as monotone. It is not monotone in the other axis, and the reason is structural
rather than statistical: an environment can only fragment what it can reach, so the relevant variable is the **ratio of
the environmental scale to the pattern scale**, not the amount of heterogeneity.

## What would make it a curve instead of three points

A sweep at scale 6, 8, 16, 32 with the same five seeds — four more arms, about thirty minutes — would show whether the
maximum really sits at 12 and how sharp it is. Until then this is three points and a mechanism, which is enough to state
as a hypothesis and not enough to state as a law.

## What is not claimed

- Five seeds per arm; the ordering is the evidence and it failed, so the resonance is a post-hoc reading of three points.
- Amplitude and correlation length both change the occupied area, so neither knob is pure geometry.
- Divisions are events under the overlap rule, not verified lineages.

## Artifacts

`morphogenesis/experiments/L1_field/x62_{s04,s12,s24}_s{171..175}.json`, fields in `x62_fields/` (45 arrays), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x62_scale.json`. Scripts: `scripts/x62_series.py`, `scripts/x62_analyse.py`.
