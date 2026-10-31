# Questions for the next run through models — 1 November 2026

Prepared after reading twelve works (six in full, six partially). Each question says what we already know, what we do
not, what kind of paper would answer it, and what changes if it is answered. The aim is **not** a bibliography but the
shortest path to knowing whether we are ahead of the literature, behind it, or repeating an old argument.

Context in one paragraph. We run a Gray–Scott world at grid 96, `dt = 1.0`, four-neighbour Laplacian, periodic
boundaries. Our headline claim was that heterogeneous inflow roughly doubles the number of threshold components
(+3.57). Three tests on 31.10 qualified it: the contrast falls to a plateau of +1.00 at `dt = 1.0` and to 0.00 at
`dt = 0.5`; the magnitude at half the step is +1.24; and our grid comparison was not a refinement at all, because
resolution in this family enters as a `1/Δx²` coefficient on diffusion.

---

## Q1. How does the field separate a transient from a steady state in pattern-forming systems?

**We know.** Within a single run the contrast decays: quarters of physical time give +4.00, +1.00, +1.00, +1.00 at
`dt = 1.0` and +2.00, −2.00, 0.00, 0.00 at `dt = 0.5`. Between 6000 and 12 000 units the *time-integrated* estimator
does not decay (+3.57 → +3.69), which is why the effect looked steady.

**We do not know.** Whether "transient advantage in the number of patterns" is a recognised observable with a standard
estimator, or whether everyone reports integrals and nobody says so.

**What to look for.** Papers on transient coexistence and transient diversity in spatially extended systems; work that
distinguishes "how many patterns at time t" from "how many on average"; any convention for reporting both.

**What changes.** If a standard exists, we adopt it and rewrite §4.5 in its terms. If not, we state both estimators
explicitly — which we already do — and this becomes a small methodological note.

## Q2. Is there a mechanism behind the step dependence we measured?

**We know.** The effect weakens with the step: +3.57 at `dt = 1.0`, +1.24 at `dt = 0.5`, and the scheme is unstable at
`dt = 2.0`. Davis & Bongard (2022) show that patterns in continuous cellular automata live only in a window of `dt`;
Davis (2024) shows a glider that dies at both 0.17 and 0.26 with no clipping.

**We do not know.** *Why* our contrast shrinks. Candidate explanations we cannot yet distinguish: (a) at smaller `dt` the
threshold-crossing events are resolved differently, so fewer components appear and disappear between snapshots; (b) the
effective diffusion per unit time changes with `dt`; (c) the structure lifetime in steps grows, so a wider step admits
more ephemeral fragments.

**What to look for.** Work on how discretisation affects **pattern statistics** rather than pattern existence; scaling
of pattern density or counts with step size; anything relating `dt` to the lifetime of a structure.

**What changes.** If (a) is right, our lifetime measurement is partly an artefact of sampling and needs a correction by
snapshot density. If (b), we have a diffusion confound and `X58` is the answer. If (c), the effect is real but its
magnitude is not comparable across `dt` — which is what we now say.

## Q3. Is "number of connected components above a threshold" ever a legitimate observable in this model family?

**We know.** Our own sweep says it measures fraying: at threshold 0.30 both worlds shatter into ~30 pieces; at 0.20 both
are one cluster with the largest share 0.95 and 0.99. Davis (2023) uses persistence of gliders; Joe (2016) uses
persistence landscapes on Gray–Scott; Spector et al. (2025) classify Turing patterns by persistent homology.

**We do not know.** Whether anyone states the limitation explicitly ("the count at a fixed threshold is not a
well-defined observable"), or whether our percolation framing is a rediscovery.

**What to look for.** Excursion-set and percolation analyses of reaction–diffusion patterns; critiques of spot counting;
the standard alternative (largest-cluster share, correlation length, Betti curves).

**What changes.** Either we cite and stop claiming novelty, or we make the limitation explicit as a contribution.

## Q4. How does one track the identity of structures through time in continuous media?

**We know.** We inherit `uid` when the overlap between snapshots is ≥ 0.5, and this gives lifetimes with median 57 steps
(heterogeneous) versus 4046 (homogeneous). A search across our whole corpus for "tracking identity components lifetime"
returns **nothing relevant**.

**We do not know.** Whether overlap-based identity is standard; how sensitive lifetimes are to the threshold; how to
correct for snapshot density (at `dt = 0.5` we have twice as many snapshots).

**What to look for.** Tracking of patterns in reaction–diffusion (watershed, level-set, persistent homology of excursion
sets, optimal transport); any paper reporting lifetime distributions of spots and its sensitivity to the tracking rule.

**What changes.** This is the weakest methodological link in our strongest claim. If a standard exists, we redo the
lifetimes with it and report both.

## Q5. Where does the field stand on Bedau's open problems that we touch?

**We know.** Bedau et al. (2000) distilled fourteen open problems; the ALife review by Aguilar et al. (2014, DOI
`10.3389/frobt.2014.00008`) states that there have been advances in all of them but **all remain open**. Ours touch #2
(transition to life in an artificial chemistry in silico), #3 (whether fundamentally novel living organisations can
exist), #6 (what is inevitable in open-ended evolution), #7 (minimal conditions for evolutionary transitions), #10
(information processing for evolving systems).

**We do not know.** What has been settled since 2014 in those five, and what the current standard of evidence is.

**What to look for.** Reviews of progress on the fourteen problems; "open-ended evolution" assessment literature; any
work claiming progress on #3 or #6 with a measure.

**What changes.** It tells us whether our negative results are contributions to an open problem or answers to a
question the field has moved past.

## Q6. What of verification and validation transfers to agent-based and ALife models?

**We know.** The V&V canon (Oberkampf & Roy 2010; Naylor 1967) was written for partial differential equations. Wilson et
al. (2014) and Sandve et al. (2013) give the cheap part: tests, review, version control, recorded seeds, textual claims
tied to results.

**We do not know.** Whether anyone has adapted V&V properly to agent-based or ALife models, and what is considered the
minimum standard there.

**What to look for.** V&V for agent-based models; validation of individual-based simulations; "model docking" as a
practice (Axtell et al. 1996 is in our corpus, unread).

**What changes.** Our design gate (`docs/design-checks.md`) claims to be a fragment of V&V. If an adapted standard
exists, we should follow its vocabulary rather than invent ours.

## Q7. Are there scaling laws for structure counts in reaction–diffusion systems?

**We know.** Our counts depend on the threshold, the step, the grid and the inflow heterogeneity, and we have no theory
for any of those dependencies.

**We do not know.** Whether the literature has scaling relations — count per unit area versus `F`, `k`, diffusion, grid —
that would let us say which of our numbers is a property of the medium and which of the discretisation.

**What to look for.** Scaling analyses of spot density in Gray–Scott; relations between pattern wavelength and
parameters; anything predicting how many spots a given domain holds.

**What changes.** This is the question that would most strengthen the line: with a scaling law, the step dependence
becomes a correction rather than a caveat.

---

## What we will do with the answers

| if | then |
|---|---|
| Q1 gives a standard estimator | rewrite §4.5 in its terms, keep both numbers |
| Q2 gives a mechanism | we can finally say *why* the contrast weakens, instead of only that it does |
| Q3 shows prior work | cite it, drop any novelty claim about percolation |
| Q4 gives a tracking standard | redo lifetimes, report both — this is the weakest link |
| Q5 shows the field has moved | reposition our negative results or drop the framing |
| Q6 gives an adapted V&V | align `design-checks.md` with it |
| Q7 gives a scaling law | the step dependence becomes a correction, not a caveat |

## Collection hints for the librarian

Priority order: **Q4, Q2, Q1** — they touch numbers we have already published. Then Q7, Q3. Q5 and Q6 are context and
can wait. Every item should arrive with a DOI, a year, and a one-line statement of what it actually shows — the
31.10 catalogue taught us that existence and content are different checks.
