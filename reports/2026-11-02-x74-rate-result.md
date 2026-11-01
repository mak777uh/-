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

## The mechanism check, run and failed — both candidate explanations are refuted by the same artifacts

The report above named two candidates and a measurement that would separate them: if the faster decay at 0.035 is **kinematic**
(more splitting and merging), the split rate there should be higher than in the neighbouring cells; if it is **competing pulls**,
the split rates should be similar while the spread of structure sizes is larger at the boundary. Both were computed from the same
artifacts.

| cell | splits per component per 1000 steps | splits per 1000 occupied cells per 1000 steps | mean components | peak-area CV |
|---|---|---|---|---|
| 0.030 | 0.79 | **19 567** | 47.7 | 0.54 |
| 0.035 | 1.22 | **13 191** | 27.8 | 0.96 |
| 0.040 | **4.14** | 10 180 | 7.0 | 1.40 |

**Both predictions fail.** The split rate per component rises monotonically with `F` (0.79 → 1.22 → 4.14) — it is *highest* where
memory lasts *longest* (0.040), so a kinematic explanation cannot produce a U-shaped half-life. The area-normalised rate runs the
other way (19 567 → 13 191 → 10 180) and is monotone as well. And the size spread (CV 0.54 → 0.96 → 1.40) is monotone in `F` too,
not peaked at the boundary, so it cannot stand in for "competing pulls" either.

So the honest state is: the decay rate depends on the inflow with a minimum at the multistable cell, and **none of the three
obvious covariates — split rate per structure, split rate per area, size dispersion — explains it**. A U-shaped half-life in a
world where all three covariates are monotone means the mechanism is something the boundary cell has that the others do not, and
by construction that is exactly **two coexisting length scales** (X71–X71c). That reading is consistent but not established: this
analysis removes two explanations rather than confirming a third.

**What it would take to confirm the third:** an inflow where two scales coexist *without* the split-rate change — the band edge
(`0.033`/`0.037`, already measured for a different purpose) is the natural place, and the depth curve there is a 20-minute
re-analysis of `x71c` artifacts, which lack genealogies (1000-step logging) and would need the dense-logging version.
