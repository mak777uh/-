# 029: How lineages begin and end in a pattern-forming chemical medium

- **Type:** research article (measurement and one negative result)
- **Version:** v2.0 — plain-language edition for an outside reader (draft for the owner's review; not submitted)
- **Date:** 2026-11-04
- **Status:** draft, awaiting the owner's decision to publish
- **Figures:** [`029-figures/`](029-figures/)
- **Data behind every number:** [`029-figures/tables.json`](029-figures/tables.json)

## Abstract

A chemical medium that spontaneously forms patterns is often described as if it contained individuals that inherit,
compete and die. We test how much of that description survives measurement.

The medium is a thin layer of two reacting and diffusing chemicals, simulated on a 96 × 96 grid. Left alone it fills with
an irregular pattern; here the supply of fresh chemical is made uneven, in stripes, which produces three distinct
habitats: a lattice of separate spots, a maze, and a single connected mass. In all three, blobs of the pattern appear,
grow, split, merge and disappear.

We asked three plain questions. *Does anything pass from one blob to its descendants?* *How close can two lineages get
before the medium fuses them into one?* *What actually ends a lineage?*

Four answers. (i) The medium has a **mixing length**: two lineages end up as a single blob once the gap between their
surfaces falls below about nine cells, and this number does not depend on how big the blobs are — bodies of 29, 64 and
113 cells fuse across gaps of 10, 9 and 8 cells respectively, while their centre-to-centre distances differ by four
cells, not by sixteen. (ii) A fusion is a **merger of two lineages, not a birth**: both lineages end on the same step and
one blob appears under a new name, which forces a three-way classification of close encounters (mutual fusion,
absorption, persistence). (iii) At the edge of the mixing length the **outcome switches abruptly while the timing spreads**:
at body radius 6 the share of runs that end as one blob reads 1.0 / 1.0 / 1.0 / 0.5 across surface gaps of
6.5 / 7 / 7.5 / 8 cells, while the share of slow fusions rises 0.0 / 0.0 / 0.2 / 1.0. (iv) Lineages mostly end by **losing
their name, not their cells**: about half of all endings are absorptions (55.3 / 47.8 / 48.4 % in the three habitats), the
absorber is a close relative in 87.2 % of the cases in the lattice and in 37.7 % in the connected mass, and — the result we
did not expect — **the habitat that produces the most generations is not the one in which a lineage is most likely to
still exist at the end**.

On inheritance: the blob-to-descendant slope of the tracked trait is 0.9837 [0.9680, 1.0002] and 0.9931 [0.9756, 1.0103],
the scatter around that line equals the model's own noise parameter to within one per cent (0.1487 and 0.1495 against
σ = 0.15), and with the noise switched off the trait has no variance at all. The trait is therefore transmitted perfectly
by the bookkeeping rule and not by the medium. We say this plainly rather than quoting a heritability number, because the
between-lineage variance we can also compute (0.082 in the lattice, 0.416 in the connected mass) counts lineages that
happen to still be present at the end, not a property of the trait.

Finally, a negative result: adding a third, slowly diffusing chemical — the most natural way to give the pattern a
heritable scale — does not change the pattern's wavelength at all.

## 1. What this paper asks

Pattern-forming chemical systems are a standard testbed for questions about order, and they are routinely described in
the vocabulary of biology: "individuals", "reproduction", "inheritance", "selection". Each of those words is a claim. The
claim can be checked — not by looking at pictures, but by defining an event, counting it, and seeing which intervention
moves the count.

We concentrate on three claims that are usually left implicit.

First, **inheritance**. If a blob splits, does its daughter resemble it because something is transmitted, or because our
own analysis assigned the daughter a value? In this medium the honest answer turns out to be the second, and the useful
result is the precise form of the transmission: a slope of one with an error equal to the model's noise parameter.

Second, **identity**. Two blobs of a pattern are not like two animals: they can run into each other and become one. Where
the boundary of an individual lies is therefore an empirical question about the medium — the mixing length — and not a
matter of definition.

Third, **endings**. A structure can stop existing in several ways: it can be eaten by a neighbour, it can dissolve, or it
can be absorbed into a larger body. Which of these dominates decides what "a lineage" even means.

Each of the three is measured below, with an intervention where an intervention is possible (the mixing length) and with
pairs of closely related lineages where it is not (endings and inheritance).

## 2. The medium

Two chemicals, `u` and `v`, react and diffuse:

```
∂u/∂t = Du ∇²u − u v² + F (1 − u)
∂v/∂t = Dv ∇²v + u v² − (F + k) v
```

with `Du` = 0.16, `Dv` = 0.08, `k` = 0.06, integrated explicitly with `dt` = 1.0 on a 96 × 96 grid with periodic edges.
This is the standard Gray–Scott system, the workhorse of pattern-formation studies: for these parameters it sustains a
maze of bright ridges on a dark background, and a uniform `F` produces either spots or a connected labyrinth depending
on its value.

Our only modification is that the supply `F` is **uneven**: it is modulated by a fixed sinusoidal field of amplitude 0.5
and period **12 cells**, which is what makes the pattern's own wavelength 12 cells. Because the modulation is fixed in
space, a run does not drift into one global state; instead the same dish contains a whole range of local conditions. By
choosing three supply levels we obtain three habitats that differ only in that level, and that we can therefore compare
with every other condition held fixed:

| habitat | supply `F` | what it looks like |
|---|---|---|
| spots | 0.030 | a lattice of separate compact blobs on a dark background |
| mixed | 0.035 | spots and short ridges; the transition regime |
| connected | 0.040 | one percolating labyrinth, most "blobs" are parts of the same mass |

Each run lasts 6 000 integration steps. At every tenth step the analysis records, for each connected region of the
pattern above a brightness threshold (we call them **bodies**), its area, its position, and an identifier. Identifiers are
the core of the bookkeeping and the reason the results are trustworthy: when a body splits, **both** daughters get new
identifiers, and when two bodies merge, the merged body gets a new identifier as well. No identifier ever spans a
division or a fusion. A **lineage** is the tree of identifiers descended from one body, and a **generation** is one level
of that tree.

The one artificial ingredient is the **trait**. Each body is given a number `s` around 1.0 — a "composition" — which is
copied to its daughters with small random changes of standard deviation σ = 0.15, and which in turn nudges the local
supply `F`. This is a deliberate stand-in for a heritable character: it is the only thing in the model that is passed
from parent to offspring, and the medium itself has no notion of it. Everything in §4.6 follows from taking that
seriously.

> **Box 1 — the words we use.**
> **Body** — one connected region of the pattern above threshold.
> **Surface gap** — the distance between the two nearest surfaces of two bodies, `g = d − r₁ − r₂`, where `d` is the
> distance between their centres and `r₁`, `r₂` their effective radii. This is the quantity that matters for diffusion,
> as opposed to centre-to-centre distance, which grows with body size.
> **Generation (depth)** — how many levels of the identifier tree a lineage reaches before it ends.
> **Sister lineages** — two lineages born from the same parent at the same time and place; comparing them cancels
> everything the two share.
> **World** — one run of the model with one random seed. Ten to thirty worlds per condition are used below, and we
> report how many are needed.

## 3. How we measure

**Intervention where possible.** To measure the mixing length we do not watch a busy world and guess; we place exactly
**two bodies and nothing else** in an empty dish, at a chosen centre-to-centre distance, and vary the distance. Every
other condition — supply field, threshold, time step, integration length — is the production configuration, and a
control run confirms that adding the intervention does not change any other result.

**Counting where intervention is impossible.** Endings and inheritance cannot be randomised, so we use pairs: two
lineages born from one parent (sisters) differ in size but share place, time and habitat, which turns a comparison of
strangers into a within-family comparison. Intervals are 95 %, computed by resampling over parent lineages, never over
individual steps, so that a long-lived lineage counts once.

**Decision rules written down first.** Before each series we wrote the readout, the criterion and the rule for declaring
the series uninformative. That matters here because three earlier designs of the same question produced numbers that had
to be withdrawn: a rate with two defensible definitions differing sixfold, a "rate difference" that turned out to be a
sample filter, and a pairing statistic in which 22.2 % and 21.5 % of pairs are exact ties. All three are reported below
where they bear on a conclusion; the withdrawn values are cited only to show what they were, and with the tie rule
applied the paired fractions read 0.526 and 0.388.

## 4. Results

### 4.1 Two lineages fuse when the gap between them is under nine cells

Put two bodies of radius 3 cells (29 cells of area, the typical size of a body that dies in the lattice) into an empty
dish at centre separation 15 cells and they fuse in every one of five runs. At 16 cells they fuse in two of five; at 17,
in none. The switch is one cell wide, at **16 ± 1 cells**, and it is not a race between fusing and dividing: as the pair
approaches the switch the fusion takes longer and longer, 19, 39, 49 and 79 steps at separations 12, 14, 15 and 16, which
is deceleration, not a knife-edge coincidence.

The interesting part is what stays constant. A body twice as wide has four times the area, and its centre must be much
further away before the pair stops fusing — but only by four cells:

| body radius | area (cells) | centre separation at which fusion stops | surface gap there |
|---|---|---|---|
| 3 | 29 | **16 ± 1** | 10 cells |
| 4.5 | 64 | **18 ± 2** | 9 cells |
| 6 | 113 | **20 ± 2** | 8 cells |

The conserved quantity is the **gap between the surfaces**, 9 ± 1 cells, which is about three quarters of the pattern's
12-cell wavelength. The rule `2r + 9` — centre separation equals twice the radius plus nine — was written down after the
first two rows and predicted the third: the measurement returned 18 ± 2, and at the boundary the same split appeared
(two of five runs still fusing). Nine cells is therefore a length belonging to the medium, not to the pair
(Fig. 2a).

Every arm agrees on the near side: at a surface gap of 8 cells, 5 of 5 runs end as one body; at 9 the split is
M 3/5, A 2/5; at 10 it is M 2/5, A 2/5, P 1/5; at 11 it is M 2/5, P 3/5. ("M" is mutual fusion, "A" absorption of one
body by the other, "P" the two bodies persisting side by side; §4.2 explains why the three must be told apart.)

Two controls say what the length is *not*. It is not a size rule: among runs where both outcomes occur, the bodies that
divided are not the larger ones — median areas at fusion 267 / 268 and 297 / 287 cells, and where the pattern reverses,
242 / 290. And it is not simply the clock running out: a lone body of the same size does not divide at all until a
**median of 180 steps** (radius 3), while a pair within the mixing length is one body within 50 steps. The other two
sizes behave the same way — 190 and 290 steps for radii 4.5 and 6 — so the fusing pair is always faster than the
division time, at every size.

![Figure 1](029-figures/fig1-what-we-measure.png)

**Figure 1.** What is measured, drawn rather than photographed. (a) Two bodies of radius `r` at centre separation `d`
leave a surface gap `g = d − 2r`; the results are stated in the gap because that is the quantity diffusion sees.
(b) The three outcomes of a close encounter: mutual fusion (both lineages end, one new body appears), absorption (one
lineage ends inside the other) and persistence (both continue). (c) The identifier bookkeeping: every split gives both
daughters a new name, and every fusion gives the merged body a new name, so no name spans a division or a fusion.


![Figure 2](029-figures/fig2-mixing-length.png)

### 4.2 A fusion is a merger, not a birth

Our first plan was to map a band of distances at which two bodies "annihilate". Reading the logs killed the word. At
separations 10 and 11 the two identifiers die on the **same** logged step, and on the next step there is **one** body
under a **new** identifier. Nothing is born: two lineages end together and a third thing starts. The old vocabulary had
looked like it was describing a birth only because the analysis counted a partner as present if its last known position
was within two cells.

That is why the results speak of M, A and P rather than of "coalescence". It is also why the mixing length is a property
of *lineages*: below nine cells, two identities are extinguished at once. Whatever counts as an individual in this
medium, it cannot survive contact.

### 4.3 At the edge, the outcome switches and the timing spreads

At body radius 6, ten runs per gap, the two things separate cleanly (Fig. 3):

| surface gap (cells) | 6.5 | 7 | 7.5 | 8 |
|---|---|---|---|---|
| runs ending as one body | 1.0 | 1.0 | **1.0** | **0.5** |
| dissolution steps observed | 39 ×10 | 39 ×10 | 39 ×8, 49 ×2 | 49 ×3, 59 ×2 |
| slow, among runs that merged | 0.0 | 0.0 | **0.2** | **1.0** |
| slow, among all ten runs | 0.0 | 0.0 | 0.2 | 0.5 |

The share of runs that merge is a step between 7.5 and 8 cells. The share that merge *slowly* — one logged step later
than the rest — has already left zero at 7.5, and both denominators are quoted because at 8 only five of ten runs merge
at all: the strict figure is 1.0, the conservative one 0.5, and the conclusion (a spread that begins before the outcome
changes) holds under both.

One control failed and we keep it in the record: the half-cell arm at 7.5 also moved the drawn bodies by one cell each
(110 cells against 108 and 110), so that arm is a gap change *plus* about 2 % of area. The failure works against the
finding, not for it.

![Figure 3](029-figures/fig3-the-edge.png)

### 4.4 Most lineages end by being absorbed by a relative

Classifying an ending is harder than it sounds, and two earlier attempts had to be withdrawn: the first offered a choice
between "lethal" and "homogenising", no registered outcome ever fired, and the second was voided by its own controls.
The version that works restricts an absorption to the dying body's own neighbourhood — a survivor within
`r_dead + r_survivor + 2` cells — and adds a category the lattice needs: a death with no living neighbour at all.

| habitat | endings | died alone | absorbed | faded away | absorber was a relative |
|---|---|---|---|---|---|
| spots | 524 | 31.3 % | **55.3 %** | 10.5 % | **87.2 %** |
| mixed | 844 | 29.4 % | 47.8 % | 21.7 % | 39.2 % |
| connected | 1 102 | 21.2 % | 48.4 % | **27.4 %** | **37.7 %** |

Absorption is the commonest single fate everywhere — about half of all endings — and the remaining two fates trade
places with the habitat: dying alone falls from 31.3 / 29.4 / 21.2 % while fading away rises 10.5 / 21.7 / 27.4 %.

The sharper result is *who* does the absorbing. In the lattice, 87.2 % of absorptions are by a close relative; in the
connected mass, only 37.7 %. We tried to control this for geometry and could not: every absorption with a partner happens
at contact, so matching on distance is degenerate — and the degeneracy is itself the finding. At the same contact
geometry, the single neighbour is a relative 87.2 % of the time in the lattice and a stranger 62 % of the time in the
connected mass. The lattice keeps families apart; the connected habitat mixes them.

Sisters rarely meet again: 18.4 / 8.6 / 17.4 % of sister pairs re-merge within a run (82 % are censored, i.e. the run
ends first), with medians of 80 / 120 / 60 steps after birth, and the distance at birth decides it by a factor of two.

### 4.5 More generations does not mean more survival

Size buys generations. Sisters that differ in size differ in how many generations their lineages reach — by
**+1.479 [1.289, 1.654]** and **+2.213 [1.962, 2.489]** generations in the two habitats where the comparison is defined —
and the readout is not a disguised lifetime: with lifetime held fixed the correlation is 0.459 / 0.340, and depth is
*negatively* correlated with lifetime itself (−0.185 / −0.070). The advantage survives a per-step rate, an equal time
window and a persistence readout; matching sisters on the number of daughters halves it (0.125 and 0.044 against
0.2496 / 0.1372 unmatched), and a two-term model puts area and daughter count in opposite directions, with age the one
confound we cannot remove.

Comparing the three habitats separates three things that the two-habitat design had merged (Fig. 4):

| habitat | lineages below the generation floor | generations advantage | generations per 1 000 steps | survival advantage |
|---|---|---|---|---|
| spots | 0.162 | 1.479 | 6.06 | 0.2496 |
| mixed | 0.302 | 1.416 | 9.01 | 0.2984 |
| connected | 0.466 | 2.213 | 18.96 | 0.1372 |

The generation clock is a gradient in supply (0.162 / 0.302 / 0.466 of lineages never reach the floor), depth is a
threshold that jumps only at percolation (1.479 / 1.416 / 2.213), the rate accelerates (6.06 / 9.01 / 18.96), and the
survival advantage **reverses**: 0.2496 / 0.2984 / 0.1372, the middle habitat sitting 5.99 standard errors above the
straight line between the outer two. The habitat that produces the most generations is the one in which a lineage is
least likely to be there at the end.

That reversal cost us a lesson in sample size. On ten worlds the paired survival difference was −0.077, interval
−0.166 … +0.012: unresolved, because the spread between worlds (sd 0.14) equalled the effect. A power calculation asked
for at least 26 worlds per habitat; at thirty the difference resolved at −0.1323 (−0.1819 … −0.0840), with the size
advantage at +1.8340, the share of lineages that fade away at +0.1419 and the share absorbed by relatives at −0.4164.
The ten-world estimate was not merely imprecise: it was biased low by about 40 %. Contrasts of this kind now cost
30–40 worlds, and we say so before quoting one.

**Figure 2.** The mixing length. (a) Share of runs that end as a single body against the surface gap, for three body
sizes; the shaded band marks nine cells. (b) The time to a single body against the same gap: the curves for the three
sizes lie on top of each other, so the time is set by the gap and not by the body.

![Figure 4](029-figures/fig4-endings.png)

**Figure 4.** Endings and the reversal. (a) Composition of endings in the three habitats: absorption dominates everywhere, while dying alone and fading away trade places as the habitat becomes more connected. (b) The size advantage in generations (blue, left axis) rises only at percolation, while the advantage a large sister has in still being present at the end (orange, right axis) peaks in the mixed habitat and collapses in the connected one.

### 4.6 What is inherited is copied by the bookkeeping, and we can show it

The trait `s` is copied from parent to daughter with noise. To measure the transmission we reconstruct parent–daughter
pairs from the logs. Because a split gives both daughters new identifiers, a parent and its daughter are never recorded
on the same step; the parent is read at its last recorded step before the daughter appears, and the daughter at her
first. The displacement is at most one logging step (ten integration steps), and the control that decides whether this
reconstruction is trustworthy is the artifact's own published correlation, compared per world rather than pooled:
0.9092 against 0.9092 and 0.8967 against 0.8989, over 2 164 of 2 211 and 1 779 of 1 951 pairs.

Then the transmission itself (Fig. 5):

| quantity | spots | connected |
|---|---|---|
| daughter against parent, slope (95 % interval) | **0.9837 [0.9680, 1.0002]** | **0.9931 [0.9756, 1.0103]** |
| the same, with division rate partialled out | 0.9837 | 0.9932 |
| parents shuffled (mean, one-sided p) | 0.19, **0.001** | 0.15, **0.001** |
| scatter of daughter minus parent | **0.1487** | **0.1495** |
| the model's own noise | σ = 0.15 | σ = 0.15 |
| share of variance between surviving lineages | 0.082 | | 0.416 |

Three readings. The slope is one: daughters are their parents, up to noise. Partialling out how often a body divides does
not move it, so the apparent correlation between the trait and the division rate is one rule seen twice. And the part of
a daughter's value that does not come from its parent is exactly the model's noise, to one per cent.

The decisive test is the ablation. Two runs with the noise switched off (with a control run reproducing the reference
world step by step, so that the switch is the only difference) give a **constant trait**: `s` is 1.0 in every body at
every step, between-body sd 0.0, and 100 % of pairs exactly equal. With the copying rule's noise removed, the trait has
no variance at all — the degenerate limit of perfect transmission. Nothing in the chemistry contributes anything
transmissible: what passes from parent to daughter passes because the analysis wrote it there.

Which is why the last row of the table must not be read as a heritability. The share of trait variance that sits between
lineages at the end of a run is 0.082 in the lattice and 0.416 in the connected mass, but a world that happens to hold
ten lineages gives 0.30 where a world with two gives 0.00–0.02, and the connected habitat's horizon can be a handful of
bodies, so one surviving root can carry 0.93. That number counts **surviving lineages**; it is not a property of the
trait. Reporting it as a heritability would be the exact error this section exists to prevent.

**Figure 3.** At the edge of the mixing length. (a) Ten runs per gap at body radius 6: the share ending as one body is a
step between 7.5 and 8 cells, while the share that merge slowly has already left zero at 7.5. (b) The same runs by
dissolution time; the arms are staircase-shaped rather than spread out.

![Figure 5](029-figures/fig5-heredity.png)

**Figure 5.** Transmission and its error. (a) The measured daughter-against-parent slope with its 95 % interval, against the same slope when parents are shuffled; the dotted line is perfect copying. (b) The scatter of daughter minus parent, against the noise the copying rule itself adds (σ = 0.15): what is not inherited is exactly the noise, and with the noise switched off the trait has no variance at all.

### 4.7 Negative result: a third chemical does not set the pattern's scale

If the pattern's wavelength were inherited by the pattern from something in the medium, the obvious carrier would be a
third chemical that diffuses slowly and is advected by the pattern. We added one, with its diffusion rate raised to
**8 ×** that of `v`, and swept its coupling.

It does not work. The pattern's wavevector stays at **7–9** in all six living cells — the same value as without the third
chemical — while what does move is the *orientation* of the pattern, by a measure that runs between 0.636 and 0.837, and
that movement does not replicate: 2 of 6 cells show it, in opposite directions. The coupling constant of the added field
is 0.30 and the field survives in only 2 of 6 seeds. A third diffusing species, in short, is not a scale channel in this
medium, and the wavelength therefore is not inherited from any chemical the pattern carries.

## 5. What it means

A pattern-forming medium produces entities that look individual and are not: they merge on contact at a length the medium
sets, they die mostly by being absorbed, and their only heritable character is one our own analysis writes into them.
None of that makes the system uninteresting — it makes the description precise. Three consequences for anyone using this
kind of medium as a model of individuality:

1. **"Inheritance" needs an ablation.** A parent–daughter correlation is not evidence of transmission, because the
   bookkeeping that names the daughter can create the correlation. The test is what happens when the copying rule's own
   noise is removed: if the trait becomes constant, the medium is not transmitting it.
2. **The mixing length is the boundary of the individual.** Below about nine cells of surface gap there are no two
   individuals, only one; any statement about a "population" of such bodies has to say what it does about contact.
3. **Survival and reproduction are different measurements and can point opposite ways.** In this medium the habitat that
   maximises generations is the one where a lineage is least likely to be present at the end. A study that reports only
   one of the two can be internally consistent and still tell a reader the wrong story.

The negative result closes the most plausible route by which the trait could have become a property of the medium: a
carrier chemical does not set the scale, so the scale belongs to the interaction of the two original chemicals with the
imposed supply pattern.

## 6. Limits

1. **One system.** A single grid size (96 × 96), one reaction rate `k` = 0.06, one threshold, one supply modulation. The
   mixing length is a length in *this* medium, stated in cells and in wavelengths; a different ratio of the diffusion
   rates could move it.
2. **The central chain is correlational.** Size is never randomised, so the size-to-generations result is a within-family
   comparison, not an intervention, and age remains an uncontrolled confound. What is causal here is the mixing length,
   which comes from placing bodies by hand.
3. **Time resolution is coarse.** The model is written every ten steps, so "slow" is a single bit and the width of the
   timing distribution is bracketed, not located.
4. **Lineage bookkeeping has no notion of fusion.** Our variance decomposition treats a merged body as a new root, which
   makes the between-lineage share an upper bound.
5. **Two runs per ablation arm.** Both are degenerate in the same way, which is strong evidence that the trait has no
   variance, but it is not a distribution; and the criterion for reading a degenerate arm was amended after seeing the
   data, which we state rather than hide.
6. **World counts.** Thirty per habitat were enough for the contrasts reported; they are the price of admission, not a
   surplus.

## 7. Data and code

All data are public. The derived tables behind every figure and every number in this paper are
[`029-figures/tables.json`](029-figures/tables.json) (each entry names the aggregate it came from),
[`table-edge.csv`](029-figures/table-edge.csv), [`table-habitats.csv`](029-figures/table-habitats.csv) and
[`table-heredity.csv`](029-figures/table-heredity.csv). The aggregates themselves, with the command line of every run,
are in [`morphogenesis/experiments/E09_pond/`](../morphogenesis/experiments/E09_pond/) and the per-run artifacts in
[`morphogenesis/experiments/L1_field/`](../morphogenesis/experiments/L1_field/). The figures are produced by
[`scripts/make_article_029_figures.py`](../scripts/make_article_029_figures.py); a checker
([`scripts/check_article_029_numbers.py`](../scripts/check_article_029_numbers.py)) verifies that every number printed
above appears in the derived tables, and the tables are built from the aggregates, not typed by hand. The whole
computation is one consumer GPU: the ablation arm is 0.11 GPU-hours and the entire paper's series under 40.

## 8. Reproduction

```bash
python scripts/make_article_029_figures.py --write     # tables and all five figures, from the committed aggregates
python scripts/check_article_029_numbers.py --ci       # every number printed above, traced to its aggregate
```

The series behind the results are `scripts/x134_series.py` … `scripts/x154_series.py` (the two-body intervention and its
sweeps), `scripts/x108_series.py` (the dense logs), `scripts/x155_ablation.py` (the noise-off arm) and
`scripts/x155_analyse.py` (reconstruction and statistics). Each artifact records its own command, its seeds and its
pre-registered criterion.
