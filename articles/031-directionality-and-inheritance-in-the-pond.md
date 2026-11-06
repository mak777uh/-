# 031: Directionality and inheritance in the pond — what works, where the boundary is

- **Type:** research article (a negative result on inheritance plus a positive result with a measured mechanism on directionality)
- **Version:** v1.0
- **Date:** 2026-11-06
- **Status:** draft; not submitted, not deposited
- **Authors:** Morphogenesis Laboratory
- **Related reports:** [S0/A1](../reports/2026-11-05-s0-a1-directionality.md), [S1/A2](../reports/2026-11-05-s1-a2-move-ci.md),
  [S2/B1](../reports/2026-11-05-s2-b1-gradpos-taxis.md), [S2/B2](../reports/2026-11-05-s2-b2-tumble.md),
  [S3/D](../reports/2026-11-05-s3-d-transfer-env-families.md), [S4](../reports/2026-11-06-s4-reproducibility.md),
  [S5/C](../reports/2026-11-06-s5-c-lineage-selection.md), [S6/C3](../reports/2026-11-06-s6-c3-double-flip.md),
  [S7/C3b](../reports/2026-11-06-s7-c3b-new-environment.md), [S9/C2](../reports/2026-11-06-s9-c2-behavioural-trait.md),
  [S10/C2b](../reports/2026-11-06-s10-c2b-directionality.md), [S11/D](../reports/2026-11-06-s11-d-patches-insensitive.md),
  [S12/D2](../reports/2026-11-06-s12-d2-patches-sensitive.md), [S13/D3](../reports/2026-11-06-s13-d3-crowding-vs-drift.md),
  [S14/D4](../reports/2026-11-06-s14-d4-local-crowding.md), [S15/E1](../reports/2026-11-06-s15-e1-refresh-insensitive.md),
  [S16/E1b](../reports/2026-11-06-s16-e1b-refresh-window.md), [S17/F1](../reports/2026-11-06-s17-f1-food-competition-impossible.md),
  [S18/C4](../reports/2026-11-06-s18-c4-lineage-diversity.md)
- **Artifacts:** `morphogenesis/experiments/E09_pond/s{0..18}_*.json`, `p0_*.json`, `p1_*.json`, `s2_*.json`
- **Figures:** [`031-figures/`](031-figures/) — built by
  [`scripts/make_article_031_figures.py`](../scripts/make_article_031_figures.py) from artifacts only

## Abstract

We asked whether a simple world with a resource, death and reproduction can learn to behave better after its environment
changes — and whether such a skill can be inherited by descendants. The answer splits in two. **Directionality works, but
it runs into crowding:** a cell that steps towards the neighbour with more resource holds 0.475 of the favourable half
against 0.357 for the control on a patchy environment, and the advantage falls to +0.036 as the rich zone fills
(correlation of the advantage with rich-zone occupancy −0.57 over 18 points). **Inheritance does not work:** four tests —
lineage selection, a double flip back to the native environment, a flip to a new environment, and a heritable behavioural
trait with a transplant control — give a consistent null, and the null survives the removal of the lineage-monopoly
confound. Separately, three experiments turned out to be invalid by construction, and we record that rather than present
them as results.

**Keywords:** pond, directionality, taxis, inheritance, lineage selection, boundary of the setup

## 1. The question

The world: a 32×32 grid, a resource in the cells, organisms with energy on the cells. An organism spends energy on
upkeep, takes it from the resource of its own cell, reproduces when it accumulates mass, and dies when its energy runs
out. The resource arrives at a limited rate and has a ceiling.

The question we were interested in: **does behaviour appear in such a world that helps survive a change of environment —
and does it become fixed in descendants?**

A "yes" would mean: after the environment changes, the share of the living in the new favourable zone rises, and lineages
born later are systematically more successful than earlier ones. A "no" means: the share does not rise above chance, and
late lineages do not differ from early ones.

## 2. Context and predecessors

Two things in the literature set the frame. First: plasticity is useful only if the adaptation time is shorter than the
death time — otherwise the organism does not live long enough to use what it "understood" (this is our formal hypothesis
F-ADAPT in `formal/Survival.lean`). Second: selection on lineages requires that the variation of the trait be heritable and
that there be enough lineages — otherwise demographic noise is indistinguishable from selection.

**Competition for space as a subject in its own right.** Our result "cells compete for space, not for food" is not new as a
setup: the literature treats space itself as a limiting resource with locally density-dependent payoffs, and shows that the
inefficiency of space use has a transition at one density and a peak at another [1]. This matches our picture: the advantage
of directionality is largest at low density and falls when the zone fills. An important difference: in our world one grid
cell holds one organism (S17/F1), whereas in forager-mobility models several agents may occupy a site [2] — which is exactly
what allows the competition for food that we structurally lack.

**Searching along a resource gradient.** Our mechanism — local greed towards the neighbour with more resource — is a special
case of searching along a gradient. A known result: local search behaviour keyed to density-dependent fitness limits the
speed and extent of spread and promotes the clustering of populations [3]. Our data (rich-zone occupancy rising
0.025 → 0.348 while the resource there barely moves) is a direct observation of such clustering.

Our setup differs from classical models in that the environment is given not by equations but by a resource field, and
behaviour is not an agent's strategy but a step rule that we switch on and off.

**Context references:**
[1] Mathew A.M., Sasidevan V. *Modelling competition for space: Emergent inefficiency and inequality due to spatial
self-organization among a group of crowd-avoiding agents.* arXiv:2407.21537.
[2] *Food Income and the Evolution of Forager Mobility.* Scientific Reports 9 (2019), s41598-019-42006-2.
[3] Rowell J.T. *The limitation of species range: a consequence of searching along resource gradients.* PMC2760341 (2009).

## 3. Methods

**The environment.** A 32×32 grid. Layouts: `gradient` (the resource decreases from top to bottom), `patches` (three rich
patches in the corners, the rest poor), `uniform`. The resource ceiling depends on the layout; so does the inflow. An
environment change is a sharp flip (`flip_at`), a smooth drift (`drift_at`/`drift_steps`), or a second flip (`flip2_at`)
that either returns to the original orientation or rotates the environment by 90° (`flip2_mode`).

**The non-degenerate regime.** Proportional income: `income = baseline·res·4`. Upkeep is `update_cost + repair_cost`. At
`res = 0.2` the net balance is −0.028 per step; at `res = 1.0` it is +0.100. This is what makes death real and stops the
population from "living on everything".

**The metric.** The share of the living in the favourable zone: for `gradient` the current half of the gradient (it flips
with the environment), for `patches` the top 50% of cells by current resource. In addition, the process metric
`move_ci = (steps up − steps down)/total steps` along the current gradient.

**Validity rules (fixed before the runs).** R1: mean deaths ≥ 10 and mean living ≥ 10. R2: no occupancy if the integral of
the living is < 20. R3: "indifferent" is accepted only if R1 holds and three seeds agree.

**What was not done.** The defaults of `config.py` were not changed; every engine edit is additive and, when switched off,
gives the previous world bit-for-bit.

## 4. Results

### 4.1 Directionality: it works, but it decays

![The advantage of directionality and its decay](031-figures/fig1-the-advantage-decays.png)

*Figure 1.* **A.** The share of the living in the rich zone: local greed against the control, window by window after
seeding on a patch (S12/D2). **B.** The gap (greed − control) at three population densities (S13/D3): the denser the
population, the smaller the gain.

| test | what was measured | result |
|---|---|---|
| S1/A2 | `move_ci` when stepping to the best neighbour | +0.042 before the flip, −0.003 after → occupancy ~0.513 is dispersal, not taxis |
| S2/B1 | taxis by gradient position | `move_ci` +0.32…+0.34 after the flip |
| S12/D2 | patches, colony seeded on a patch | share in the rich zone 0.475 against 0.357 for the control |
| S12/D2 | the same, by the end | +0.036 (decay) |
| S13/D3 | density sweep | gap 0.221 / 0.118 / 0.057 at sparse / base / dense population |
| S14/D4 | rich-zone occupancy | correlation of the advantage with occupancy **−0.57** (18 points) |
| S15/E1 | patch inflow rate | at 4.0 and 12.0 the patch does not deplete (inflow > consumption) → the regimes are indistinguishable |
| S16/E1b | below the depletion threshold (0.5 / 2.0) | depleting the zone **does not rescue** the advantage: gap 0.117 → −0.022 |

**The mechanism.** Directionality brings cells into the rich zone; the zone fills; the gain from knowing how to get there
falls. At low density the loop does not close, because there is room for everyone — and there the gap is largest.

**What the gap means quantitatively.** The first window gives +0.118, the last +0.036. With three seeds and a scatter of
order 0.02–0.03 the last number **lies within the scatter**: it should be read as "the gain stopped being noticeable", not
as a measured quantity. The article's claim — that a gain exists at the start and decays — rests on the monotonicity across
densities (S13) and on the correlation with occupancy (S14), not on that last number.

**A caveat about the correlation.** −0.57 is computed over 18 points (3 regimes × 6 windows), and points within one run are
dependent: neighbouring windows of one seed are not independent. No p-value is therefore given or claimed; the conclusion
"the relation is negative" rests on the monotonicity across regimes.

![Why the advantage falls](031-figures/fig2-why-it-decays.png)

*Figure 2.* **A.** The rich zone fills with the living (solid lines), but its resource barely falls (dashed) — cells get in
each other's way by occupying space, not by eating. **B.** The gap against rich-zone occupancy, across every regime and
window: correlation −0.57.

**A refinement: competition for space, not for food.** A direct measurement (S15/E1, S16/E1b) showed that the resource on
rich cells barely falls (0.26 → 0.22) although occupancy rises (0.025 → 0.348). Cells obstruct each other **physically**: a
neighbouring cell is occupied, so the step is impossible. Moreover, with our settings a patch cannot deplete at all: the
inflow (0.200 per step) exceeds one cell's consumption (0.160 per step), and two organisms cannot stand on one grid cell.
A test below the depletion threshold (`inflow_rich < 3.2`) showed that **depleting the zone does not rescue the advantage**:
cells leave it as soon as it empties, and the gap goes negative in one window (−0.022).

**Refuted variants.** There are two. The first is smoothing the signal (a 5×5 window mean, "seeing the whole patch"): it
does not help — the smoothed arm sits between the control and plain greed. The second is refreshing the rich zones (the
hypothesis that if the zone does not have time to fill, the advantage becomes stable): it was not confirmed either with a
full or with a depleting zone.

**Why this is not a parameter artefact.** We checked every available lever (S17/F1): lowering `baseline_income` lowers both
consumption and income at once; lowering upkeep does not change how much a cell eats; lowering `resource_regen` starves the
poor zone, which is already lethal; lowering `patch_inflow_rich` was tested in S16. The cause is structural: **only one
organism can stand on a grid cell**, so consumption per cell is capped by one cell, and the inflow cannot be lowered without
killing the whole world. Competition for food requires allowing several organisms per cell — a change to the physics of the
world, which we did not make.

### 4.2 Inheritance: four tests, independent by mechanism

![Four tests of inheritance](031-figures/fig3-the-four-nulls.png)

*Figure 3.* Four tests of inherited adaptation. In all of them the arms converge to ~0.50 after the environment changes —
the level of a random distribution over the two halves. The double flip (S6) and the new environment (S7) both produce
recovery, and the same one; the heritable trait — both mobility (S9) and directionality (S10) — makes no difference, and the
transplant changes nothing.

**A caveat about independence.** The four tests are independent **by mechanism**, but not by data: they all run on the same
world, with the same metric and the same seeds. Agreement therefore strengthens the conclusion about the mechanism, but does
not replace an independent replication on another world.

| test | what was checked | result |
|---|---|---|
| S6/C3 | double flip A→B→A | recovery 0.648 against 0.356 for the control — but this is a return to the native environment |
| S7/C3b | flip to a NEW environment C | 0.609 — almost as good as the native one; both arms converge to ~0.50 (dispersal) |
| S9/C2 | heritable mobility + transplant | 0.459 against 0.533 for the null; the transplant changes nothing |
| S10/C2b | heritable directionality + transplant | 0.429 / 0.431 / 0.427 — all arms coincide; high vs low trait ≤ 0.005 |
| S18/C4 | lineage monopoly removed (quota 0.25, refractory 20) | lineages double (28.3 → 57.4), the top share falls (0.938 → 0.798), yet high vs low trait still differ by ≤ 0.02 |

**Conclusion.** In this setup inherited adaptation does not arise. What is observed after an environment change is
dispersal and survival, not selection on a trait. One lineage holds 95–97% of the population, late lineages stay at 1–5%,
and their share in the favourable zone does not grow. The last row matters: the null is not an artefact of that monopoly —
when the monopoly is removed, the trait still does not sort.

### 4.3 What turned out to be invalid (and why that matters)

Three experiments had to be withdrawn — not because they gave an "inconvenient" answer, but because the manipulation never
reached the dynamics:

1. **S5/C (lineage selection).** It was set up with `type_mode="fixed"`, and in that mode `register_births()` is not called,
   so inheritance and mutation did not work at all: the arms coincided bit-for-bit and the trait did not vary (std = 0, zero
   mutations).
2. **S11/D (the first patchy test).** Cells were seeded in the centre, where the balance is −0.028 per step, while the
   nearest rich patch was 9.2 cells away: the moving arms starved out before arriving.
3. **S6/C3, the first version.** The second flip was implemented by mirroring the state from outside the engine, but the
   environment's position is a function of the step counter, not of the state, so the environment did not change and both
   arms stayed in the same one.

In all three cases we caught the error before drawing conclusions and recorded it as an invalid setup rather than as a
negative result.

## 5. Discussion

**What this means.** The world has a working behavioural mechanism (local greed) and a measurable reason for its limit
(crowding of the rich zone). This is not "intelligence" and not "adaptation" — it is an observed class of behaviour and its
boundary.

**Competing interpretations.** The decay of the advantage could be explained by the population mechanically spreading over
the map. We separated these explanations with the density sweep and the direct measurement of rich-zone occupancy: spreading
leaves a residue of +0.02…+0.035 that does not depend on density, while the bulk of the effect is explained by competition.

**What cannot be concluded.** We do not show that inheritance is impossible in principle — only that in this setup (one
dominant lineage, little variation, a short horizon) it produces no visible selection, and that removing the dominant
lineage does not change that. We also do not show that directionality is "useful" — it is useful only while the zone is not
full.

**A limitation of the method.** Some early results (B1/B1b) were taken on different hardware, and on CPU they do not
reproduce bit-for-bit: plastic runs depend on the backend. We mark such numbers as hardware-dependent and do not rely on
them as "stable recovery".

## 6. What this does not show

- It does not show that the world is "alive" or "adaptive" in any strong sense.
- It does not show that inheritance is useless in general — only in this setup.
- It does not show the optimality of any of the mechanisms tested.

## 7. What would change the answer

- Inheritance might start to work with more lineages (reducing the founder's dominance) or over a longer horizon with
  periodic environment changes — the first of these was tested in S18/C4 and did not change the null.
- Directionality might give a stable gain at low density with a constant inflow of new rich zones (that is, when the zone
  does not have time to fill).

## 8. Where we move next

**What the literature said.** A search on our questions (items B-Q051…B-Q053 in `lab/lit-queue.json`) gave three footholds.
First, "space as a limiting resource" is an established frame with a non-trivial prediction: inefficiency has a transition at
one density and a peak at another [1], which matches our maximum gain at low density. Second, models in which several agents
may occupy a site [2] allow exactly the competition for food that we structurally lack (S17/F1). Third, local search along a
gradient is known as a mechanism of clustering and of limiting spread [3] — our data on rising occupancy with a stable
resource is a direct observation of it.

**The next step.** Test whether the advantage of directionality survives when **several organisms may occupy a cell** — the
only lever that, by S17/F1, can create competition for food. The engine edit is additive (with it switched off the world is
bit-for-bit), but it changes the physics of the world and therefore needs the owner's decision. The prediction from the
literature [2]: with shared occupancy of a site, the gain from mobility should depend on the rate of resource recovery, not
only on density — and that is the testable difference from our present result.

## 9. Reproducibility

Every number comes from artifacts under `morphogenesis/experiments/E09_pond/`; the scripts are
`morphogenesis/scripts/s{5,6,9,10,11,12,13,14,15,16,18}_*.py` and `p0_flip_metric.py`. Runs were on CPU (the environment has
no CUDA build of PyTorch), 3 seeds, 600 steps, with R1 checked in every run.

**The numbers are checked by machine, not by eye.** The script
[`scripts/check_article_031_numbers.py`](../scripts/check_article_031_numbers.py) re-reads the artifacts and compares every
headline number of this article with them (20 checks, tolerance 0.002–0.01):

```bash
python scripts/check_article_031_numbers.py   # 0 failures out of 20 checks
```

The check was written after the first pass over the article and **immediately found two bugs in itself** (it mis-parsed the
`s13`/`s16` schema, whose rows carry a `regime` field) — that is, it verifies rather than rubber-stamps. The prose is checked
against the artifact, never the other way round.
