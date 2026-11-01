# X74: the decay rate depends on the inflow — and the multistable boundary is where memory dies fastest

**Date:** 2026-11-02, 01:45 MSK. **Experiment:** X74 (two new inflow cells for the memory-decay rate).
**Preregistration:** `reports/2026-11-02-x74-rate-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x74_f0{30,40}_pattern_s171-175.json`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x74_rate.json`.

## Result

Ancestor–descendant peak-area correlation at lags 1 / 2 / 3, and the fitted decay:

| inflow | pairs (1/2/3) | ρ₁ | ρ₂ | ρ₃ | shuffle p95 | λ | half-life |
|---|---|---|---|---|---|---|---|
| 0.030 | 1 166 / 1 091 / 1 037 | **0.507** | **0.304** | **0.198** | 0.044 | 0.625 | **1.47** |
| 0.035 | 2 140 / 1 968 / 1 776 | 0.475 | 0.204 | 0.072 | 0.036 | 0.389 | **0.73** |
| 0.040 | 970 / 887 / 795 | **0.486** | **0.278** | **0.205** | 0.055 | 0.649 | **1.61** |

Lag-1 is almost identical in the three cells (0.475–0.507) — so **how much a daughter resembles her mother does not depend on the
inflow**. What depends on it is how fast that resemblance is forgotten: the half-life differs by a factor of **2.0** between
0.035 and 0.040.

## The shape, which the registered criterion did not anticipate

My preregistration said "supports the rate is a property of the medium if half-lives differ by ≥ 1.3 **in a consistent
direction**". The spread is there (2.0), the direction is not: the dependence is **non-monotone**, a U with its minimum at the
boundary cell. So the honest statement is narrower than the registered one: *the rate depends on the inflow; the dependence is
not monotone, and its minimum sits at `F = 0.035`.*

That minimum is the interesting part, because `F = 0.035` is exactly the **multistable cell** of X71/X71b/X71c — the narrow band
where two wavelengths coexist. Away from it the medium is decisive (one preferred scale) and memory lasts 1.5–1.6 divisions;
inside it the medium is indecisive, and memory lasts 0.73.

**The world that can be two things remembers less.** Two readings are consistent with the data and not separated here: (a) at the
boundary a structure's size is under two competing pulls, so a deviation is overwritten faster; (b) at the boundary the pattern is
more dynamic (more splitting and merging), so the parent's size is replaced by the daughter's faster for kinematic reasons. A
third measurement — the split rate per structure per 1000 steps in each cell — would separate them, and it is already available
in the same artifacts.

## What this changes

- "Limited heredity" now has a **parameter that varies with the medium**: half-life 0.73–1.61 divisions across a `ΔF` of 0.01,
  a factor of two for a 30 % change in the inflow. The depth of memory is not a constant of the world, it is a function of where
  in the parameter plane the world sits.
- The contrast with X72c sharpens: the mixture has no heredity anywhere measured, while size has a heredity whose *depth* varies
  with the medium — the two readouts are not two views of one thing.
- It gives a concrete, cheap next test: if the mechanism is kinematic (b), the split rate at 0.035 should be higher than at
  0.030/0.040; if it is competing pulls (a), the split rates should be similar and the *variance* of structure size larger at the
  boundary.

## What this does not say

- It does not identify the mechanism — that is the next measurement, not this one.
- Three inflows is not a curve; the minimum is located to ±0.005 and the shape between cells is unknown.
- Same limitations as X73: survival bias flattens the decay, peak area is a lifetime maximum, one box, one `k`.
