# 032: What decides whether behaviour pays — movement, not the signal it follows

- **Type:** research article (two negative results that reorder an earlier positive one, plus one refuted mechanism)
- **Version:** v1.0
- **Date:** 2026-11-06
- **Status:** draft; not submitted, not deposited
- **Authors:** Ilya Vladimirov
- **Related reports:** [S19/G1](../reports/2026-11-06-s19-g1-recovery-rate.md),
  [S21/G2](../reports/2026-11-06-s21-g2-adaptation-trap.md), [S22/G3](../reports/2026-11-06-s22-g3-fixed-reference.md),
  [S23/G4](../reports/2026-11-06-s23-g4-fixed-reference-fast.md), [S24/G6](../reports/2026-11-06-s24-g6-mobility-control.md),
  [S25/G7](../reports/2026-11-06-s25-g7-equal-budget.md), [S26/H2](../reports/2026-11-06-s26-h2-signal-field.md),
  [S27/H4](../reports/2026-11-06-s27-h4-external-rhythm.md), [S28/H5](../reports/2026-11-06-s28-h5-memory-field.md),
  [S29/H6](../reports/2026-11-06-s29-h6-memory-curve.md), [S30/H7](../reports/2026-11-06-s30-h7-lifetime-curve.md),
  [S31/H8](../reports/2026-11-06-s31-h8-mobility-curve.md), [S32/H9](../reports/2026-11-06-s32-h9-distance-curve.md),
  [S33/H10](../reports/2026-11-06-s33-h10-displacement.md), [S34/H11](../reports/2026-11-06-s34-h11-field-vs-smoothing.md)
- **Artifacts:** `morphogenesis/experiments/E09_pond/s{19,22,23,24,25,26,27,28,29,30,31,32,33,34}_*.json`
- **Previous article of the series:** [031](031-directionality-and-inheritance-in-the-pond.md), DOI
  [10.5281/zenodo.24012536](https://doi.org/10.5281/zenodo.24012536)

## Abstract

The previous article of this series reported that local resource-greedy movement helps in a patchy pond world, but that
its advantage shrinks as the rich zone fills. This article asks the next question: **what decides whether a movement rule
pays at all?** Three candidate answers were tested and two of them were wrong.

First, we asked whether the sign of the advantage depends on how fast the resource recovers. It does: with slow recovery
the greedy rule *loses* to a non-moving control (gap −0.078 to −0.205, all three seeds negative), with fast recovery it
wins (+0.036 to +0.101). Second, we asked what causes the loss, and found a *trap of inaction*: the step rule fires only
when the cell's prediction exceeds the actual resource, and the prediction is an exponential average that tracks the
falling resource, so the cell stops noticing that it is in a bad place — at step 300 only 3 of 45 cells still qualified
to move, and by step 400, 102 of 108 living cells sat on depleted cells. Third, we asked whether removing the adaptation
fixes it. It does, dramatically (+0.338 instead of −0.174), **but the reason is not the reference**: with the number of
moving cells held equal, the two references are indistinguishable (0.238 vs 0.246) and both are worse than the control.
The dominant variable is *how much the cell moves*, not *what it compares with*.

We then tested a continuous diffusing signal field in four designs: built from the living cells (no effect — its gradient
duplicates local information), driven by an external rhythm (no effect — it carries information unrelated to food),
carrying the memory of where the food was (a real gain, +0.038…+0.045), and finally compared against plain smoothing of
the resource (no difference: 0.299 against 0.297). The field is unnecessary; what helps is looking at a *neighbourhood*
rather than at a single cell. A direct measurement explains why: a cell moves 0.14 cells from its birth cell in a whole
lifetime, so it cannot use long-range information at all.

**Keywords:** pond, directionality, habituation, mobility, memory, boundary of the setup

## 1. The question

The previous article established that a cell stepping towards the neighbour with more resource holds a larger share of the
favourable zone than a non-moving control, but that the gain decays as the zone fills. That leaves the mechanism open: is
the gain a property of the *rule* (which way to step), of the *environment* (how fast food comes back), or of something
else entirely?

This article separates those. The world is the same as in the previous article: a 32×32 grid, a resource in the cells,
organisms with energy on the cells, proportional income, death when energy runs out, reproduction on accumulated mass. The
non-degenerate regime is unchanged, and R1 (mean deaths ≥ 10 and mean living ≥ 10) is checked in every run.

## 2. Context

Two ideas from the literature frame the work. First, mobility in agent-based foraging models is known to interact with
population density and with resource depletion and replenishment rates, so that the return from moving can be lower than
the return from staying put when the neighbourhood is crowded [1]. Second, plasticity is useful only if the adaptation
time is shorter than the death time — our formal hypothesis F-ADAPT — which is the frame in which a *fast* adaptation
could be harmful rather than helpful.

What this article adds is a controlled separation: the same world, the same seeds, and one knob at a time, so that the
question "what decides whether behaviour pays" gets a measured answer rather than an interpretation.

**References cited in this article:**
[1] *Food Income and the Evolution of Forager Mobility.* Scientific Reports 9 (2019), s41598-019-42006-2.

## 3. Methods

**The world.** Unchanged from the previous article. The patchy layout has three rich patches; a colony is seeded on one of
them, because seeding in the poor centre makes the experiment insensitive by construction (the cells starve before
direction can matter — this was measured and is recorded in the previous article's withdrawn experiments).

**The metrics.** The favourable share — the fraction of living cells standing on the top 50% of cells by current resource —
and, for the stability questions, its within-window standard deviation. The process metric is the number of moves per step.

**The arms.** Each experiment varies one knob: the resource recovery rate, the reference the step rule compares against,
the number of moving cells, the field design, the memory lag, the field's lifetime, the cell's mobility, or the distance
between the old and the new food.

**Sensitivity arithmetic before each run (contract §3c).** No experiment was started without first computing whether the
manipulation could reach the dynamics: income at a full patch is 0.160 per step and upkeep is 0.060, so a colony on a patch
is viable in every regime used; the patch inflow was checked against one cell's consumption before any depletion test.

## 4. Results

### 4.1 The sign of the advantage depends on how fast food returns

| recovery | control | greedy (adaptive reference) |
|---|---|---|
| slow (regen 0.010) | 0.340 | **0.166** (gap −0.174) |
| fast (regen 0.040) | 0.325 | 0.361 (gap +0.036) |

With slow recovery the greedy rule **loses**. All three seeds are negative by the end (−0.138, −0.105, −0.278). This is the
first place in the series where the behaviour is actively harmful rather than merely useless.

### 4.2 The cause is a trap of inaction, not crowding

The step rule fires only when `resource < pred`, and `pred` is an exponential average of the resource. When the resource
falls, the prediction falls with it, the error goes to zero, and the cell stops qualifying to move:

| step | living | on depleted cells (resource < 0.3) | cells qualifying to move |
|---|---|---|---|
| 100 | 19 | 14 | — |
| 300 | 45 | 43 | **3** |
| 400 | 108 | **102** | — |

A cell that has adapted to a bad place no longer notices that it is in one.

### 4.3 Removing the adaptation fixes it — but not for the reason it looks like

Replacing the adaptive reference with a fixed one (the resource at seeding time) changes the picture completely:

| window | control | adaptive reference | fixed reference |
|---|---|---|---|
| 0–100 | 0.363 | 0.405 | 0.501 |
| 300–400 | 0.288 | 0.185 | 0.663 |
| 500–600 | 0.340 | **0.166** | **0.678** |

The sign flips: −0.174 becomes +0.338. But two controls demolish the natural reading. The fixed reference is better at
*both* recovery rates (+0.338 slow, +0.350 fast), so it is not a cure for the slow regime; and it makes about ten times
more cells move (338 against 22 per step). With the number of moving cells held equal, the gain falls from +0.338 to
+0.094, and with an **absolute** equal budget the two references are indistinguishable:

| arm (near-equal absolute budget) | favourable share | moves per step (last window) |
|---|---|---|
| control | 0.340 | 0 |
| adaptive reference | 0.238 | 13.5 |
| fixed reference | 0.246 | 16.1 |

**The dominant variable is how much the cell moves, not what it compares with.** The "adaptation trap" is a trap of
inaction.

**A limitation of that control, stated plainly.** The budget was set to 20 cells per step for both reference arms, but the
adaptive arm never reached it: its own qualifying count is lower, so it moved 13.5 cells per step against 16.1 in the
fixed arm. The two arms are therefore *near*-equal, not exactly equal, and the fixed arm still moves about 19% more. That
residual difference works **against** the article's claim (the arm that moves more does not do better), so the conclusion
is not an artefact of the imbalance — but the control does not isolate the reference as cleanly as "equal budget" would
suggest.

### 4.4 A continuous signal field: four designs, one conclusion

The owner of the project proposed a continuous field — a diffusing "chemical" signal — that could carry information at a
distance and oscillate. It was implemented additively (with every field parameter at zero the world is bit-for-bit the old
one, checked by an anchor) and tested in four designs:

| design | favourite share | verdict |
|---|---|---|
| field built from living cells | 0.318 | no effect: its gradient duplicates local information |
| external travelling wave (phase) | 0.332 | no effect: carries information unrelated to food |
| external wave, level-adaptation | 0.330 | same as phase-following |
| **memory field** (source = resource `lag` steps ago) | **0.297** | **a real gain** against the 0.260 control |
| **plain smoothing of the resource** | **0.299** | **matches the memory field** |

The memory field is the only variant with a gain, and it is worth +0.038…+0.045. But it can be replaced by smoothing the
resource over a neighbourhood, with no field, no diffusion and no memory. What helps is looking at a *neighbourhood* rather
than at a single cell.

### 4.5 Why: the cell barely moves

Tagging each living cell with its birth position gives the direct answer:

| mobility | mean displacement from birth | 90th percentile |
|---|---|---|
| 1 | **0.14 cells** | 1.0 |
| 3 | **0.19 cells** | 1.0 |

A cell lives and dies within about one cell of where it was born. It cannot use long-range information, which is why the
field's "distance to the food" does not matter, and why the field is equivalent to local smoothing.

### 4.6 The memory optimum: one lever works, three do not

The memory length has a clear optimum (lag 10–40 beats no memory by +0.035…+0.047). Four levers were tested against it:

| lever | shifts the optimum? |
|---|---|
| rate of environmental change | no (0.297 / 0.299 / 0.292) |
| lifetime of the field (decay) | no (0.300 / 0.297 / 0.294) |
| distance to the food | no (0.298 / 0.300 / 0.299) |
| **cell mobility** | **yes** (best lag 10 at mobility 1, 40 at mobility 3) |

The simple formula "optimal lag ≈ distance / mobility" was tested and **refuted**: the distance half does not hold. The
mechanism behind the mobility half is the same as in §4.5 — a faster cell reads a wider neighbourhood, so it can use a
longer memory.

## 5. Discussion

**What this means.** Across two lines of work the same lesson repeats: the signal a cell follows matters far less than
whether it moves at all, and how much. Adaptive references suppress movement and therefore hurt; fixed references and
fields help only insofar as they restore movement; and a field of any design adds nothing that local smoothing does not.

**What was refuted, and why that is the result.** Three natural explanations were tested and failed: that the memory
optimum tracks the environment's change rate, that it tracks the field's lifetime, and that it tracks the distance to the
food. Two field designs that looked promising were shown to carry no usable information. Reporting these as results rather
than quietly dropping them is what makes the remaining claims credible.

**What cannot be concluded.** We do not show that fields are useless in general — only that in a world where a cell moves
one cell per lifetime, a field cannot be more than a local smoother. Nor do we show that the mobility is "the" variable;
we show that it dominates the reference in this setup.

## 6. What this does not show

- It does not show that the world is alive, adaptive or intelligent in any strong sense.
- It does not show that behaviour cannot pay in general — only what decides it here.
- It does not give a quantitative law for the memory optimum; that remains open.

## 7. What would change the answer

- If cells could occupy the same site (several organisms per cell), competition for food would become possible, and the
  mobility-dominated picture might change. This needs an engine change and was not made.
- If a field could predict where food will be rather than where it was, it would carry information the cell cannot get
  locally; that design was not tested.

## 8. Where we move next

The open quantitative question is the memory optimum: four levers were tested, one (mobility) moves it, and no formula
fits. The next step is to measure the relationship between mobility and the optimal lag on more than three mobility levels,
and to check whether the optimum is set by the *width of the neighbourhood the cell reads* rather than by mobility as such
— which is what §4.5 and §4.6 together suggest.

## 9. Reproducibility

Every number comes from artifacts under `morphogenesis/experiments/E09_pond/`; the scripts are
`morphogenesis/scripts/s{19,22,23,24,25,26,27,28,29,30,31,32,33,34}_*.py`. Runs were on CPU (the environment has no CUDA
build of PyTorch), 3 seeds, 600 steps, with R1 checked in every run and reported alongside each result.

The engine additions made for this article (the continuous field, the second flip, the environment rotation) are additive:
with every new parameter at zero the world reproduces the previous one bit-for-bit, checked by an anchor run after each
addition (`alive 489 / died 5093 / correct_after 0.47229`).
