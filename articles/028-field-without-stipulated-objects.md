# A field without stipulated objects: how a component counter passed itself off as diversity

**Version:** v1.5 (2026-10-31), English edition of v1.4
**Author:** Vladimirov Ilia Sergeevich
**License:** CC0 1.0 (public domain) — see `LICENSE`
**DOI:** withdrawn — the record was deleted on 2026-10-31 (the DOI resolves to a tombstone); a corrected version will be published as a new record.
**Status:** an article about a finished line of work; two claims were weakened and one conclusion rewritten after
external review and a code check.

---

## 1. The question

Can organisation — bodies, inheritance, selection — arise in a medium where **nothing is stipulated**: no cells, no
division rules, no lineage labels, only equations? And if it can, **how many bodies** does such a medium support and
what does that number depend on?

Five external reviews of our earlier work made the same point: a world with stipulated cells studies the ecology of
stipulated replicators, not the emergence of organisation. This line is the answer: a medium with nothing but
diffusion, autocatalysis and decay.

**What we found, in the end.** Organisation arises. Inheritance is measurable. Selection acts. But the **main
quantitative result of the line had to be rewritten**: what we took for "the number of coexisting bodies" is the
**intensity of fragmentation**. The number of durable bodies barely depends on the environment.

This article is about how we discovered that, and why we think the error is more instructive than the result.

---

## 2. Context: three levels of claims

Following the laboratory's editorial standard, we separate them explicitly.

**Verified core** — numbers obtained from artifacts in the repository; they can be recomputed.

**Hypothesis** — what we think about those numbers and how we will test it.

**Metaphor** — why this might matter for the question of "conditions for life in a digital medium". A metaphor is not
presented as a result.

---

## 3. Method

### 3.1. The medium

Two diffusing quantities with autocatalysis and decay (the Gray–Scott model):

```
∂u/∂t = Du ∇²u − u v² + F (1 − u)
∂v/∂t = Dv ∇²v + u v² − (F + k) v
```

`u` is material, `v` its autocatalytic form, `F` the inflow, `k` the decay. There are no "cells": the observer is only
a **threshold on `v`**, which splits the field into connected components **after the fact**.

**Arms.** Uniform inflow `F = const` versus spatially heterogeneous `F(x,y) = F·(1 + A·G(x,y))`, where `G` is a static
pattern. Further arms: a varying pattern (periods 300 and 3000), global noise (inflow fluctuates in time but is
**identical across the whole field**), and different amplitudes `A`.

### 3.2. What counts as a component

A connected region with `v > 0.2` (4-connectivity), at least 5 cells. Each component receives a **stable identifier**
(`uid`), inherited from the parent when the overlap is ≥ 0.5 — this allows measuring **lifetime**, not just a count.

### 3.3. Rules that emerged along the way

- compare over a horizon of ≥ 6000 steps or by a time integral, not by the final snapshot (the final count is noisy:
  CV 0.78–0.93);
- `CV > 0.3` ⇒ make no claim;
- the number of seeds follows the expected dispersion, not convenience (at sd ≈ 4.5 one needs 20, not 3);
- **claims of no difference** must be tested for equivalence, not by "an interval containing zero";
- every claim carries a file with its assumptions, budget and artifacts, checked by a script.

---

## 4. Results

### 4.1. Organisation arises

From a single seeded spot, structures appear, divide and die; the number of components at its peak, per run of the
`x17_static` arm (n = 10), has **median 23 and range 9–74** (the homogeneous arm: median 7, range 5–12;
`x17_*`, field `series[].components`). Without autocatalysis the null control is empty: the mechanism is necessary,
this is not an artifact of the threshold.

### 4.2. Structures have a boundary, and it is not an artifact of resolution

The material contrast between a structure and its local surroundings is **0.52–0.62**. Moving from a 96 to a 128 grid
changes it by **2 %**. For comparison: colonies in the discrete world give a contrast of 1.09, that is, they have no
independent boundary. This is the basis on which we say the field has **bodies** while colonies do not.

### 4.3. Inheritance and variation

The trait `s` (a number affecting the decay rate) is transmitted from the parent to the daughter component: the
parent → daughter correlation is **r = 0.97** (n = 320–457 splits).

The caveat without which this number reads stronger than it is — and it is harsher than "an adoption control is
needed": **inheritance here is stipulated, not emergent.** `s` is stored in the observer's dictionary keyed by
component number, reaches the grid only as a decay multiplier, and at division is copied by an assignment with added
noise. Therefore `r = 0.97` is **the fidelity of the copying rule together with mutation**, that is, a calibration of
the implementation. What remains empirical is something else: **selection** through this trait (0.957 → 1.294),
because decay genuinely depends on `s`. For inheritance to become physical, the trait must live in the medium — a
third, slowly diffusing quantity (`X32`).

### 4.4. Selection acts through a channel, not through strength

When `s` affects **survival** (decay), the mean `s` moves up: **0.957 → 1.294** (n = 3, 6000 steps). When the same
trait affected **growth rate**, there was no selection: fast growth depletes material, and the gain is offset by the
cost.

### 4.5. Heterogeneity of inflow: the main number

If the inflow is spatially heterogeneous, the number of components is roughly **twice** as large, and this is stable:

| horizon | homogeneous | heterogeneous | difference |
|---|---|---|---|
| 6000 steps | 2.86 | **6.43** | +3.57 |
| **12 000 steps** | **2.81** | **6.50** | **+3.69** |

Difference over 12 000 steps: **+3.69**, bootstrap 95 % CI **[1.27; 7.08]** (10 runs per arm). Doubling the horizon did
not reduce the difference but slightly increased it (3.57 → 3.69) — a steady state, not a transient.

On a 128 grid: 5.64 versus 3.71 (n = 20), difference 1.93, CI **[0.14; 7.07]**, Mann–Whitney z = 2.57. The lower bound
is close to zero: the effect reproduces in direction, but on that grid it is at the edge of resolution.

### 4.6. The regime of heterogeneity: no difference detected (claim weakened)

Static, fast variation (period 300) and slow variation (3000): 6.29 / 6.14 / 6.29 (20 runs each).

**Here we must correct ourselves.** We used to write "the regime does not matter". That is not a valid formulation:
the interval of the difference **[−1.71; 3.64]** contains zero, but zero inside an interval is **not proof of
equality**. An equivalence test (the whole interval inside ±margin) **does not pass** at n = 20. The correct statement
is: "no difference **detected**". To claim equality one needs 60+ seeds.

### 4.7. Randomness alone does not produce diversity

| arm | median component count (30 seeds) |
|---|---|
| constant inflow | 2.86 |
| random, but **identical across the field** | 3.71 |
| **different in different places** | **5.57** |

Spatial pattern versus global noise: **+1.86, CI [+0.43; +3.93]** — significant.
Global noise versus constant inflow: +0.86, CI [−0.14; 2.43] — **no difference detected** (and equivalence is not
established here either: the interval is wider than the margin).

### 4.8. Amplitude: a dome with a maximum near 0.5

| amplitude | heterogeneous | homogeneous | difference | 95 % CI | significant |
|---|---|---|---|---|---|
| 0.2 | 4.14 | 2.86 | +1.29 | [−0.21; 2.71] | no |
| 0.5 | 6.43 | 2.86 | **+3.57** | [1.27; 7.08] | yes |
| 0.8 | 5.64 | 2.86 | **+2.79** | [1.21; 4.00] | yes |

Weak heterogeneity produces no distinguishable zones, strong heterogeneity pulls everything into one; the middle works.

### 4.9. The rewritten conclusion: the counter measures fragmentation

Here the line turned. We looked not at the final snapshot but at **lifetime** (10 seeds per arm, 6000 steps, a
snapshot every 500). The numbers of this table are computed by `python scripts/field_lifetimes.py --write` from the
artifacts `x23_{static,homog}_s{171..180}` and stored in the aggregate `lifetimes_matrix.json`; runs with seeds
181–200 are **not** included (a separate extension, and with 24 files the medians shift to 54 and 132 — hence the
design is fixed by an explicit seed list).

| arm | structures per run | **living ≥ 1500 steps** | short-lived | median life | peak area |
|---|---|---|---|---|---|
| heterogeneous | **5.9** | **1.3** | 4.6 | **57 steps** | 97 cells |
| homogeneous | **1.7** | **1.2** | 0.5 | **4046 steps** | **4575 cells** |

The distribution of lifetimes confirms this from another side: in the heterogeneous world **22 %** of structures live
longer than 1500 steps, in the homogeneous one **71 %**; short-lived ones (up to 500 steps) are **75 %** and **24 %**
respectively.

**The number of durable structures is the same in both worlds: 1.3 versus 1.2.** The entire increase in the component
count (5.9 vs 1.7) consists of **ephemeral fragments** (4.6 vs 0.5) with a median life of 57 steps.

Separately: the largest component holds **98–99 %** of the occupied area in both arms, and between snapshots the
heterogeneous world turns over **~65 %** of its component count against **0.00** in the homogeneous one.

**The conclusion we are obliged to state plainly.** Heterogeneity of inflow **does not create more bodies**. It
**fragments one body into short-lived pieces**, and the counter records that as "more components".

### 4.10. The threshold decides: both worlds are a single percolation cluster

External reviews warned that a component holding 98–99 % of the area often means a connected network rather than a
body. The test is a threshold sweep (10 seeds per arm):

| threshold | heterogeneous: components / largest share | homogeneous: components / largest share |
|---|---|---|
| 0.10 | 1.0 / 1.000 | 2.0 / 0.992 |
| **0.20** (working) | **3.0 / 0.950** | **2.0 / 0.992** |
| 0.25 | 8.0 / **0.764** | 3.0 / 0.982 |
| 0.30 | 28.5 / **0.136** | 39.0 / **0.137** |

**Percolation is present in both worlds**: at a threshold of 0.30 both break into about 30 pieces. At the working
threshold of 0.2 we are in the supercritical regime — **one connected network spanning the field**.

**The difference between arms is not in the number of bodies but in proximity to the threshold.** The heterogeneous
world breaks earlier (at 0.25 the largest share is 0.764 against 0.982): its network is **more frayed**, and the same
threshold counts more pieces in it.

Hence the precise definition of our quantity: "number of threshold components" is a measure of the **fraying of one
percolation cluster**, not a number of bodies and not a number of types.

This is a multi-threshold statement, and multi-threshold analysis of Gray–Scott already exists: Joe (2016) analyses
the model with **persistence landscapes** over a concentration threshold, and Spector, Harrington & Gaffney (2025)
classify Turing patterns by persistence homology. Our sweep is in effect a β₀(threshold) curve, and we cite it as
such rather than as a new idea; what we add is the observation that in *our two regimes* the count at one threshold is
uninformative about the number of bodies. Such a cluster has no boundary of its own
(it depends on the threshold) and no reproduction as a whole, so it cannot be called an individual.

### 4.11. Heredity is stipulated by code, not emergent

A code check (31.10) changed the strength of the §4.3 claim. The trait `s` is stored in a **Python dictionary** keyed
by component number, reaches the grid only as a decay multiplier, and at division is copied by the assignment
`new_s[cid] = comp_s[parent]` with added mutation noise.

Therefore `r = 0.97` is **the fidelity of our copying rule together with mutation**, that is, a calibration of the
implementation. An adoption control does not remove this problem: it would test our own code.

What remains empirical is **selection** through this trait (0.957 → 1.294), because decay genuinely depends on `s`.
The honest formulation: "a trait that **we** made heritable is subject to selection".

**A correction we owe to external review (31.10).** Five independent model reviews answered eight of our open
questions. Two answers changed our text. First, our measure of "adequacy" — mutual information between first
differences — **manufactures lag information out of a purely simultaneous response**: if the environment is
independent noise and the state merely copies it, the differenced series share a term with opposite signs, giving a
correlation of −0.5 and about 0.2 bits with no predictive ability at all. Our numbers (+0.0386 against 0.0000) must
therefore be read as *predictive dependence inside the consumption loop*, not as prediction. Second, memory is
necessary only for a **departed** cue: a memoryless system predicts perfectly when the current signal already
determines the future. The line "truth about the outside" is therefore not closed as logically impossible; what is
established is narrower — *without a retained state only the currently visible signal is usable*.

**An attempt to make transmission physical** (`X32`). The trait was moved into the medium — a slowly diffusing field
`h`; decay depends on the local value, and a component's trait is **read** from the field. Result: `r = 1.0` on
356–631 parent–daughter pairs in all ten runs. That is **not a success but a change of question**: at division the
daughter cells are the parent's own cells, the boundary merely pinches, so the trait is continuous and coincides
exactly. With a physical trait, inheritance is **trivial**; what becomes interesting is divergence after division.

### 4.12. Selection in the physical channel: right direction, too little strength

Series `X34b` (10 seeds, 6000 steps, `beta = 1.2`, mutation at pinches):

| | |
|---|---|
| median mean trait | **1.0212** (start 1.0, shift **+0.0212**) |
| median between-structure spread | 0.0466 |
| `r` | 1.0 in all runs (356–631 pairs) |
| seeds with a positive shift | **8 of 10** |
| criterion "shift > 2 sd across seeds" | **not met** (+0.0212 against 0.0380) |

**Conclusion:** selection in the channel "trait in the medium → decay" **works in direction but is weak in
magnitude** — half the threshold set before the data. Selection cannot be claimed.

### 4.13. Form does not transfer — and its portability is not predictable

Here the line produced its strongest negative result, and it came **not from new runs**: the data had been in the
repository since 23 October and had never been brought together.

The morphospace census (`E02b`) contains a **transplant matrix**: a finished state is placed into 12 canonical
environments and one observes whether it keeps its class.

| source | kept its class | died |
|---|---|---|
| `struct_1` | **12/108** (11 %) | 54/108 |
| `struct_2` | **9/108** (8 %) | **72/108** |
| `uniform_bright` | 1/12 | 7/12 |
| `death` | 69/72 | — |

A structure almost always **loses its class in a foreign environment, and most often dies**.

**The second question: what distinguishes the survivors?** If organisation transfers, the 8–11 % who survive should
share a property. Comparing properties of the **source** (before transplantation), 21 survivors against 126 dead:

| property | survivors | dead |
|---|---|---|
| source density | 0.775 | 0.543 |
| stability in the last quarter | 1.000 | 1.000 |
| return step | 50 | 50 |

The density difference is **+0.231**, bootstrap 95 % CI **[−0.013; +0.232]** (contains zero), permutation test
**p = 0.29**.

**Conclusion.** **No measured property of the source predicts survival.** Form not only fails to transfer — its
portability is not predicted by anything we know how to measure.

**The caveat without which this reads stronger than it is:** 21 survivors is few. "Not established" is not
"refuted"; excluding a density effect requires a replication 5–10 times larger.

---

## 5. Why everything kept failing: the world was uninhabitable, and it was a constant

A day and a half of measurements — selection, adequacy, accumulation — gave zero or weak effects. The cause turned
out to be not in the metrics and not in the structure, but in **arithmetic**.

**Income** of an inhabitant is bounded by `income = min(own, 4·b·own)` with `own ≤ 1.0`. At the standard `b = 0.002`
the income ceiling is **0.008** per step. The **cost** of existence is **0.03**. The ratio is **0.27**.

**A cell paid almost four times more than it could physically earn.** No pattern, no selection and no metric can
repair that: the medium is uninhabitable **by a constant**.

**The break-even point is `b = 0.0075`** (`b_crit = cost / 4`). Our own sweep shows that the *working* threshold lies
**above** break-even: at `b = 0.010` (ratio 1.33) the population still dies (maximum 274 cells), and only `b = 0.02`
(2.67) survives in 10 of 10 runs. That is sharper than "uninhabitable by a constant": the boundary is 0.0075, and the
practical threshold is higher. The principle itself is classical — maintenance energy (Pirt 1965) and the
`P_F = P_S − P_M` condition of NutMEG — so our contribution here is a **methodological warning**: check habitability
before interpreting an absence of adaptation.

**A sweep over the coefficient** (cost fixed, 1200 steps):

| `b` | income ceiling | to cost | alive at the end |
|---|---|---|---|
| 0.002 | 0.008 | 0.27 | 0 |
| 0.010 | 0.040 | 1.33 | 0 |
| **0.020** | **0.080** | **2.67** | **2118** |

**Confirmation on 10 seeds** (1500 steps, cost 0.03): **10 of 10** survived, median **2131.5** cells, range 2092–2166
(from the median −1.85 % / +1.62 %; range/median **3.54 %**), resource under the living 0.975.

**As a side result, a chemostat does not help.** A lower bound on resource (0.05–0.4) changes nothing: income is
proportional to `own`, so raising the floor raises income only up to `4·b·own`. **The coefficient binds, not the
level.**

This changes the order of conditions: the first is **economic habitability**, not diversity, not signal and not rules.

## 6. What evolves in a habitable world: a self-model, not a world-model

Once the world became habitable, "adequacy" (information about the future of the environment) stopped being zero for
the first time. But a test with **two targets at once** split the result in two:

| arm | resource **under the living** | resource **in empty cells** |
|---|---|---|
| high cost | **+0.0386** | **0.0000** |
| low cost | +0.0184 | 0.0000 |
| zero cost | +0.0188 | 0.0000 |

**The organism's state predicts the resource it consumes itself and carries no information at all about resource
where it does not reach.** The measure and its control are computed by `python scripts/adequacy_mi.py --write`
(aggregate `adequacy_mi.json`): `I(Δenergy_t ; Δresource_{t+1})` minus shuffling, 5 seeds per arm; in the `free` arm
1 of 5 seeds gave a positive difference for empty cells, while the median is 0.0000.

And the price of error sharpens precisely the **self-model** (0.039 against 0.018) — naturally: only its own trace is
available to the organism.

**And it is confirmed by an intervention, not only by correlation.** Observational mutual information cannot separate
causal paths: "state now predicts resource later" has two explanations. We blocked one. With `ghost_no_consumption` the
organism **still receives income but the resource does not decrease** — its action on the medium is severed, everything
else unchanged (cost, growth, division). The anchor holds: with the flag off, alive and energy are identical to a run
made before the change over 700 steps.

| arm | resource under the organism | resource in empty cells |
|---|---|---|
| normal | **+0.0362** (10/10 > 0) | 0.0000 (0/10) |
| **ghost** | **0.0000** (**0/8 > 0**) | 0.0000 (0/8) |

**The dependence vanishes when the action is blocked.** So it was a consequence of the organism's own footprint, not
of external dynamics. The claim is now causally tested rather than observed.

**The conclusion we consider the main one.** In our worlds evolution can build a **model of its own trace** and cannot
build a **model of the world**. The reason is constructive: the organism has no organ that touches the outside.
Everything it senses is a consequence of its own actions.

---

## 7. Discussion

### 7.1. Why the error is instructive

For a day and a half we believed we had found a mechanism maintaining diversity in a medium without stipulated
objects. The counter doubled, the effect was stable on two grids and over a 12 000-step horizon, the intervals
excluded zero.

The error was not in the statistics but **in the object**: we measured connected regions in a snapshot and spoke of
bodies. Until we learned to track **lifetime**, we had no way to distinguish "more bodies" from "more fragments".

The irony is that changing the metric required no new runs: the data were already there, but there were no identifiers
of continuation in them. We added `uid` — and the answer changed to the opposite in meaning.

### 7.1a. Three results about one thing

| measurement | what was found |
|---|---|
| boundary of a body (§4.10) | depends on the threshold: at 0.30 both worlds break into ~30 pieces — the "dominant" is a connected network |
| mechanism of transmission (§4.11) | stipulated by code; moved into the medium, inheritance becomes trivial (a pinch, not a copy) |
| transfer of organisation (§4.13) | 8–11 % keep their class, 50–67 % die, and **nothing measured predicts who survives** |

Adding up: what we called a "structure" has **no boundary independent of the threshold, no mechanism of transmission
of its own, and no portable organisation**. There is no individual in our world — there are local solutions of a
"state + environment" pair that look like bodies while we observe them in their own environment and at one threshold.

### 7.2. What follows for the question of life

Stated cautiously: in a continuous medium organisation arises, traits are transmitted, selection acts through the
survival channel, but the medium supports **about one durable body**, and external heterogeneity increases not their
number but the number of fragments.

This is not "life" and not "consciousness" — we have no operational definitions for them (and the laboratory's
editorial standard forbids such words without definitions). It is an **observed class of behaviour and its
boundaries**: emergence is there, multiplication of bodies is not.

### 7.3. Three levels

**Core (data).** The numbers of §4.5–4.13 are recomputable from `morphogenesis/experiments/L1_field/` and the
aggregates.

**Hypothesis.** We think "dominant plus flickering fringe" is a percolation regime: one connected network, not a body.
Tested by a threshold sweep (`X26`) — confirmed.

**Metaphor.** "Life in a digital medium requires not activity but a stable difference of conditions" is a metaphor,
not a result. Our data say only that a difference of conditions changes the **intensity of fragmentation**.

---

## 8. Limitations

1. **One substrate** (Gray–Scott), one grid in the main series, one pattern scale. Transfer was not tested.
2. **The largest component may be a percolation labyrinth** rather than a body: the threshold sweep is done (§4.10),
   and it says exactly that.
3. **Inheritance is stipulated by code** rather than emerging from the medium: `s` lives in the observer's dictionary
   and is copied by assignment. `r = 0.97` is a calibration of the copying rule. Moving it into the medium makes
   transmission trivial.
4. **Two claims weakened** ("the regime does not matter", "global noise does not differ"): equivalence is not
   established at n = 20.
5. **Strict coexistence is not measurable in the field**: components merge faster than invasion can be measured.
   Three instruments in a row produced artifacts.
6. **Inflow `F` enters two places** (inflow and decay), so "the same mean" does not mean the same realised inflow; a
   factorial design has not been run.
7. **The number of seeds** at key points (10–20) is below what narrow intervals require; 30–60 seeds is planned.
8. **A world-model has not been obtained** in any world: the organism predicts only its own trace (§6).

---

## 9. Next hypotheses

| id | hypothesis | test | criterion |
|---|---|---|---|
| `X31` | "the regime does not matter" and "noise does not differ" can be established at 60 seeds | 60 seeds per arm | the whole interval inside ±1 component |
| `X37` | selection is visible not in the shift of the mean but in the differential among survivors | `S` = mean trait of survivors − of the dead | `S > 0` with an interval excluding zero |
| `X38` | the portability of form is indeed unpredictable | replication of transplants to 1000+ rows | interval of the median difference excludes zero |
| `X39` | accumulation of novelty is distinguishable on our field | activity statistics in the Flow-Lenia form (type = `s` bin, activity = mass) | activity above the shadow in ≥7 of 10 seeds |
| `X46` | a signal separated from the event by a delay is used by structures | cue leading the event by 20 and 40 steps | trait centroid moves towards the leading cue |
| `X48` | memory, not sensing, is what distinguishes prediction from response | slow variable integrating the signal, with a long relaxation time | structures survive (≥5) and the centroid moves to the leading cue |

---

## 10. Reproducibility

```bash
# from the repository root
python scripts/field_track.py --steps 6000 --sample-every 500 \
  --eps 0.0 --beta 0.2 --freq-dep 1.0 --mutation 0.15 \
  --hetero-amp 0.5 --hetero-signal lab/streams/const_ones.json \
  --seed 171 --out x.json          # heterogeneous arm

python scripts/field_track.py --steps 6000 --sample-every 500 \
  --eps 0.0 --beta 0.2 --freq-dep 1.0 --mutation 0.15 \
  --hetero-amp 0.5 --seed 171 --out y.json   # homogeneous arm (no pattern)

python scripts/l1_field_matrix.py --write     # aggregate
python scripts/field_lifetimes.py --write     # lifetimes (§4.9)
python scripts/adequacy_mi.py --write         # adequacy (§6)
python scripts/claim_comparator.py            # audit of claims
python scripts/check_article_numbers.py --ci  # every number of this article against its aggregate
```

Requires Python with `numpy` and `torch` (GPU not required; on CPU a 6000-step run on a 96 grid takes minutes).
Artifacts: `morphogenesis/experiments/L1_field/` (275 files), aggregates `l1_field_matrix.json` and
`lifetimes_matrix.json`, pond artifacts in `morphogenesis/experiments/E09_pond/{habitable,adequacy}/`, claims in
`lab/claims/`, sections of the line in `docs/world-design.md`.

**Checked against artifacts:** every number of §4.5–4.13, §5 and §6 is recomputed by
`scripts/check_article_numbers.py` (15 checks, run in `make verify`). The caveats of §4.3, §4.11 and §8 correspond to
the limitations recorded in `docs/world-design.md` (§§10db–10dr) and in `lab/claims/*.json`.

---

## 11. Changelog

| version | date | change |
|---|---|---|
| v1.5 | 2026-10-31 | English edition of v1.4 with the corrected numbers: the lifetime shares (22 % / 71 %, 75 % / 24 %) are stated in §4.9, the median cell count is 2131.5, and every number is now checked against its aggregate by a script |
| v1.4 | 2026-10-31 | §4a: uninhabitability was a constant (income 0.008 against cost 0.03), habitable regime confirmed 10/10; §4b: adequacy turned out to be a self-model — 0.0000 about resource in empty cells |
| v1.3 | 2026-10-31 | §4.11–4.13: heredity is stipulated by code, selection in the physical channel is weak (shift +0.0212 < 2 sd), form does not transfer and is not predicted (8–11 % survive) |
| v1.2 | 2026-10-31 | §4.10: threshold sweep — both worlds are one percolation cluster; `X26` complete |
| v1.1 | 2026-10-31 | §4.3 rewritten: heredity is stipulated by code, `r = 0.97` is a calibration of the copying rule; hypothesis `X32` added |
| v1.0 | 2026-10-31 | first version: the field line as a whole, with the rewritten conclusion about fragmentation and the claims weakened after external review |
