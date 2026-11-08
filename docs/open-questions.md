# Open questions from the design audit

**What this is.** `docs/design-audit.md` checks every remark from the four reviews against the code. Fourteen
remarks cannot be settled by reading code: they are choices about what the world should be, or facts about
the literature. Each is written here as a **question with its context**, so that a literature search can
answer it, and so that the answer can be put straight into the change plan.

**How to use it.** Each question has: what is undecided, why it matters for the bench, what the candidate
answers are, what would decide it, and what to search for. An answer that arrives should be pasted under
"Answer" together with its source, and the corresponding row of the change plan updated.

---

## Q1. What is the smallest set of things a world must have to be a world?

**Undecided.** The bench has three worlds (an NCA field, a resource pond, a reaction–diffusion field) and no
statement of what they have in common. Without that statement, "the same phenomenon in two worlds" cannot be
distinguished from "two different things with one name".

**Why it matters.** Every claim of the form "organisation appeared" needs a definition of what a world is
before it can say what appeared.

**Candidate answers.**
- A world is a state space plus a transition operator plus a boundary condition.
- A world is what is conserved, what flows, and what limits the flow (the manifesto's P1).
- A world is a set of degrees of freedom plus the constraints that couple them.

**What would decide it.** A published treatment that derives the minimal ontology of a simulation from the
requirements of the questions it is meant to answer — not from the convenience of the implementation.

**Search for:** minimal ontology of simulation models; "what is a model" formal definition dynamical system;
requirements for artificial life worlds; conservation laws as modelling primitive; constraint-based
modelling versus parameter-based.

---

**Answer (partial).** No work derives a minimal set of world elements from the questions; the closest is
Taylor's methodological frame (list the low-level phenomena the target must explain, then build a model with
exactly those and nothing more) and the ODD protocol, which requires stating entities, state variables, scales,
processes, scheduling, initialisation and boundary. **What this settles:** a world is specified by a
**contract**, not by a grid; three worlds can share a contract without sharing a cell ontology. **What it does
not settle:** which contract. Sources: Taylor 2013 (arXiv 1710.06055); Grimm et al., ODD 2020
(10.18564/jasss.4259).

## Q2. Is a within-cell measure really not available as a knob?

**Undecided.** Manifesto 037's P3 says the primary measure is the fraction of a cell's behavioural variance
explained by its situation versus its record, and that this measure "cannot be moved by a bonus". The first
implementation of `k_readouts.py` was refuted on exactly this point: a between-cell bonus moved the
"within-cell" measure by 0.31. The rewritten version holds the property on synthetic data (a bonus moves it by
0.0000), but **no published result says that a within-subject variance decomposition is immune to
between-subject manipulation in general**.

**Why it matters.** If the property is not general, the measure is a knob with extra steps and P3 is empty.

**Candidate answers.**
- It is general: within-subject centring removes any between-subject additive shift by construction.
- It is not general: an interaction between the bonus and the situation can move the within-cell share.
- It holds only for additive manipulations, not for multiplicative ones.

**What would decide it.** A formal statement of which manipulations leave a within-unit variance
decomposition invariant, and which do not.

**Search for:** within-subject variance decomposition invariance; repeated-measures analysis manipulation
sensitivity; "variance explained" confound between-subject; intraclass correlation manipulation invariance.

---

**Answer: the general claim is FALSE, and the literature says so.** Three independent searches agree
that a within-unit variance decomposition is **not** automatically immune to between-unit manipulation. The
decisive counterexample: let the behaviour be `y = (1 + B_i)·S + R` with `S` the situation and `R` the record,
and let the bonus `B_i` be constant inside the unit but change the SENSITIVITY to the situation. The share
explained by the situation is `(1+B_i)²/[(1+B_i)²+1]` — 1/2 at `B_i=0`, 4/5 at `B_i=1`. Centring does not
remove it. **What survives:** an ADDITIVE manipulation, constant inside the unit, leaves the centred
deviations unchanged. **Consequences for P3 of manifesto 037:** the claim "the measure cannot be moved by a
bonus" must be replaced by "the measure is invariant to additive within-unit shifts and is NOT invariant to
manipulations that change the within-unit variance, the responsiveness, or the measurement noise". The
`--self-test` of `k_readouts.py` must cover all six cases, not only the additive one. Sources: Curran & Bauer
2011 (PMC3059070); Wang & Maxwell on global standardisation (PMC6696920).

## Q3. What are the legitimate units of reproduction, and what is a "group genome"?

**Undecided.** `budding_unit = "colony"` makes the whole connected component the parent and averages its
genomes; `"cell"` makes one cell the parent; `"pair"` makes a cell plus a neighbour. The review proposes four
modes: cell-clonal, lineage-clonal, colony-mean, colony-heritable. **Which of these is a model of
reproduction, and which is a model of something else?**

**Why it matters.** A colony-mean genome is not clonal reproduction: two lineages that touch produce a
synthetic genome. Every statement about "inheritance" depends on which unit is meant.

**Candidate answers.**
- Only cell-clonal and lineage-clonal are reproduction; colony-mean is "blending inheritance", a different
  model with a different literature.
- Colony-heritable is legitimate if a group-level property is defined and transmitted independently of the
  member genomes (the major transitions literature).
- All four are legitimate, but they must be named differently.

**What would decide it.** A published treatment of group-level heredity that says what must be true for a
group to be a unit of selection.

**Search for:** major evolutionary transitions individuality; group selection unit of selection definition;
multilevel selection Price equation; clonal versus blending inheritance; "unit of reproduction" definition.

---

**Answer: averaging genomes is BLENDING inheritance, not clonal reproduction, and a colony so defined
is not a legitimate unit of selection.** The criterion from the major-transitions literature is that a
collective must have heritable variation in fitness at its own level, and Godfrey-Smith's three axes locate
it: bottleneck size (B), germ–soma specialisation (G), integration (I). `budding_unit = "colony"` has **no
bottleneck and no lineage**: two lineages that touch produce a synthetic genome that is the clone of neither
parent. **What to do:** (a) rename the mode so the word "clonal" never applies to it; (b) record the three
axes for every reproduction mode; (c) if a group genome is wanted, define the transmission operator
explicitly — the mean vector is a phenotype, not a genome. Sources: Godfrey-Smith 2009 (Conditions for
Evolution by Natural Selection); Okasha / Bourrat on Price versus contextual partitions (PMC7133510);
Doulcier et al. 2020 (PMC7440921).

## Q4. Should a cell grown by the rule inherit its parent's genome?

**Undecided.** Today a grown cell receives the genome that was pre-assigned to its grid position (activation
of a field); a budded cell receives its parent's genome with mutation. Both are legitimate; the world uses
both without saying which one a given result depends on.

**Why it matters.** "Is the trait inherited?" has a different answer depending on which path made the cell.
A result about selection on a trait is meaningless if most cells got their trait from a pre-assigned field.

**Candidate answers.**
- Growth should inherit from the parent (one model, consistent).
- Growth should be activation (the field is the "genetic reservoir"; the review calls this legitimate but
  says it must be named).
- Both, as separate modes with separate names, and the artifact records which.

**What would decide it.** Whether any published artificial-life world distinguishes activation from
reproduction, and how it names them.

**Search for:** artificial life "genetic reservoir"; NCA growth inheritance; "activation versus reproduction"
artificial life; genome inheritance in cellular automata growth.

---

**Evidence: activation and reproduction ARE distinguished in the literature, and the distinction is
operational.** Avida names the operations separately — `Inject` (external creation), `h-alloc` (memory
allocation), `h-copy` (instruction copying), `h-divide` (offspring separation); copying and division are
different operations, and injection is not a parent. Growing NCA uses ONE rule shared by all cells, so a new
active cell is not a genetic offspring at all. **What this settles:** a world may have both paths, but they
must be named and counted separately. **What it does not settle:** whether growth SHOULD inherit. **What we
do:** every artifact records `grown_genome = "field"`; the next step is `birth_mode` (`activation` /
`reproduction` / `injection`) per cell, and an inheritance analysis stratified by it. Sources: Ofria & Wilke
2004 (Avida); Mordvintsev et al. 2020 (Growing NCA).

## Q5. What is the right fix for an unstable diffusion coefficient?

**Undecided.** `Dw = 0.32` at `dt = 1` gives a high-frequency amplification of −1.56. Three fixes are
available: lower `Dw`, lower `dt`, or use an implicit scheme. Each changes what the third field means.

**Why it matters.** The third field (`--second-species`) is an optional branch; an unstable default makes
every result from that branch suspect.

**Candidate answers.**
- Lower `Dw` to ≤ 0.25: keeps the explicit scheme, changes the wavelength the third field selects.
- Lower `dt`: keeps the physics, costs 2× the steps.
- Implicit scheme: keeps both, costs an implementation and changes the numerics of the other fields too.

**What would decide it.** What the third field is FOR: if it is a slower second scale, `Dw` is the parameter
that matters and `dt` should be lowered; if it is a numerical convenience, `Dw` should be lowered.

**Search for:** explicit finite difference stability condition 2D Laplacian; Gray-Scott two-species
diffusion; implicit versus explicit reaction-diffusion stability.

---

**Answer: the criterion is `D·dt/h² ≤ 1/4` for the explicit scheme with the 5-point Laplacian, and
lowering `Dw` is NOT a neutral fix.** All four searches give the same formula; the high-frequency mode has
amplification `1 − 8·D·dt`, so 0.32 gives −1.56 (unstable) and 0.24 gives −0.92 (stable with almost no
margin). **The choice depends on what the third field MEANS:** if `Dw` is a physical diffusion coefficient,
lower `dt` (or use an implicit/IMEX scheme) and keep `Dw`; if `Dw` is a free modelling parameter, lowering it
is a change of model and must be declared as one. **What we do:** `Dw` was lowered to 0.24 as an
**interim** correction; the model parameter and the integrator parameter must be separated, and the stability
condition must be a gate (it is: `world_invariants.py` W5). Sources: Cambridge lecture notes on 2D diffusion
stability; Langtangen, finite difference methods for diffusion.

## Q6. How much clipping is too much?

**Undecided.** `clamp(u + dt*du, 0, 1)` can hold a trajectory in range while the numerical correction becomes
part of the mechanism. The amount clipped is not recorded, and no threshold exists.

**Why it matters.** If clipping carries the pattern, the pattern is a property of the clamp, not of the
equations.

**Candidate answers.**
- Clipping below some fraction of the total mass per step is negligible.
- Any clipping at all invalidates the run.
- Clipping should be recorded and reported, with no threshold, and the reader decides.

**What would decide it.** A published criterion for when a positivity clamp changes the solution class.

**Search for:** positivity preserving schemes reaction-diffusion; clipping artefact numerical scheme; when
does clamping change the solution.

---

**Answer: there is no published acceptable fraction of clipping; the criterion is whether the
correction vanishes under refinement.** Clipping negative values is known to be non-conservative and to
introduce artificial mass; positivity-preserving schemes exist precisely so that clipping is unnecessary.
**Operational criterion:** record the clipped mass per step and compare it with the local truncation error of
the scheme; if the clipped mass is of the same order or larger, clipping is part of the mechanism. Any
clipping caused by the instability of Q5 is a scheme error, not a correction. **What we do:** add
`clipped_mass` and `clip_fraction` to the run artifact. Sources: Nguyen, Caboussat & Dabdub 2009 (mass
conservative positive definite integrator); projected dynamical systems (Nagurney).

## Q7. Should maintenance and repair be two named parameters?

**Undecided.** The fix for R5 keeps the name `repair_cost` and changes its meaning (charged only on a repair).
The alternative is to add `maintenance_cost` and keep `repair_cost` for repairs. The first is a silent
semantic change for every stored config; the second is a rename.

**Why it matters.** Every stored config with `repair_cost` set now means something different.

**Candidate answers.**
- Rename: `maintenance_cost` (new, defaults to the old `repair_cost`) plus `repair_event_cost`.
- Keep the name and document the change, with a version bump.
- Keep the name, and require every old config to state which meaning it used.

**What would decide it.** The bench's own rule about changing a world: a change of meaning is a change of
world and needs a version. The question is whether the version is enough or a rename is safer.

**Search for:** (methodological, not literature) — this is a question for the owner, not for a search.

---

## Q8. How should components be matched between snapshots?

**Undecided.** Real split and merge events need components matched across snapshots. Today the tracker uses
"best overlap ≥ 0.5". That threshold decides what counts as the same object.

**Why it matters.** Every lifetime, every heredity number and every split count depends on it.

**Candidate answers.**
- Best overlap ≥ 0.5 (current).
- Hungarian assignment on overlap, one-to-one.
- Overlap graph with split/merge as many-to-many events.

**What would decide it.** A published treatment of object tracking in cellular/field systems that states the
consequences of the matching rule.

**Search for:** object tracking overlapping components correspondence; cell tracking lineage assignment
overlap threshold; watershed segmentation identity across frames.

---

**Answer: 0.5 is not canonical, and the choice has measurable consequences.** Trackers use absolute or
relative overlap thresholds that differ by tool (Lineage Mapper uses 0.2 in its example), and the Cell
Tracking Challenge evaluates not only overlap but complete tracks, branching correctness and cell-cycle
accuracy. The documented consequence of a wrong rule: false divisions and broken tracks from over- or
under-segmentation. **Our own case is the sharp one:** a symmetric split gives each daughter exactly half the
parent, so the verdict flips on the sign of the inequality and on the denominator. **What we do:** the counter
now uses a RELATIVE threshold (a parent counts if it holds at least half of the best share of that child);
the next step is a sensitivity sweep over 0.2 / 0.3 / 0.5 showing how lifetimes and division counts move.
Sources: Matula et al. 2015 (AOGM, PLOS ONE); Cell Tracking Challenge 2023 (s41592-023-01879-y); TrackMate
overlap tracker keys.

## Q9. Should two worlds in one bench be allowed different boundary conditions?

**Undecided.** The field world is periodic, the pond is absorbing. Neither states it in the config.

**Why it matters.** If results from the two worlds are ever compared, the boundary is a confound.

**Candidate answers.**
- Different boundaries are fine as long as they are recorded, because the worlds answer different questions.
- All worlds should share a boundary so that comparisons are meaningful.
- The boundary should be a variable in its own right, with a run that varies it.

**What would decide it.** Whether the literature treats boundary conditions as part of the model or as a
numerical detail.

**Search for:** boundary conditions in ecological simulation models; periodic versus absorbing boundaries
population models; edge effects in lattice models.

---

**Answer: a boundary is part of the model whenever the interaction scale is comparable to the domain;
it is a numerical detail only in the limit of a large homogeneous system.** The literature is explicit:
periodic and absorbing boundaries give qualitatively different fates for spreading populations, a lethal
boundary can be modelled by a Robin condition, and edge effects appear in lattice Lotka–Volterra. Periodic
boundaries replace one artefact with another rather than removing all of them. **What we do:** `boundary` is
now in the config and in the artifact; the remaining obligation is to show that a difference between two
worlds is not explained by the boundary alone. Sources: Cantrell & Cosner (effects of spatial heterogeneity);
GROMACS periodic boundary conditions; ODD on toroidal space.

## Q10. Full diff or hashes for a dirty working tree?

**Undecided.** A run on a modified tree records `dirty=true` but not what was modified.

**Why it matters.** Such a run cannot be reconstructed from the artifact.

**Candidate answers.**
- Record `{path, sha256}` for each modified file: small, verifiable, but the content is lost if the file
  changes later.
- Record the full `git diff`: complete, but can be large and can contain secrets.
- Refuse to run on a dirty tree at all.

**What would decide it.** The bench's own rule: the repository is thin memory. A diff is content; a hash is a
pointer.

**Search for:** (methodological) — this is a question for the owner.

---

## Q11. Should the initial condition be periodic?

**Undecided.** The seed disc is Euclidean, so near the edge it is cut. A wrapped seed changes the initial
condition of every past run.

**Why it matters.** The initial mass is a factor that differs between centre and corner seeds.

**Candidate answers.**
- Wrap the seed distance (consistent with the dynamics).
- Keep the cut and record the initial mass as a factor.
- Both, as a config option.

**What would decide it.** Whether the literature treats an initial condition as part of the model or as a
convenience.

**Search for:** initial conditions periodic domain; seeding in periodic lattices.

---

**Answer: the initial condition is part of the problem, and in a periodic world the seed must use the
minimum-image distance.** The literature on periodic domains is unambiguous: distances are computed by the
minimum-image convention, and the domain must not be smaller than twice the interaction range. **Our numbers
confirm the defect:** a disc of radius 2 has 13 nodes at the centre and 6 at a corner, so the initial mass
depends on where the seed is placed. **What we do:** the seed must be built with toroidal distance, or the
initial mass must be recorded as an explicit factor. Sources: ODD (initialisation is a model element);
GROMACS minimum-image convention.

## Q12. Generated model text, or a model that matches its text?

**Undecided.** `field_inherit` computes `F_eff` from `s_ref` and describes it as `s̄`. Two fixes: generate the
description from the parameters, or change the model to use the mean.

**Why it matters.** A description that disagrees with the code is the error class the whole bench exists to
prevent.

**Candidate answers.**
- Generate: one source of truth (the parameters), the text is derived.
- Change the model: the mean is what was intended and the code is wrong.
- Both: generate the text and add a test that the text matches the code.

**What would decide it.** Which was intended. The code comment says `s_ref` was chosen deliberately so that the
mean can change; the text says otherwise. **This is a question for the owner, not for a search.**

---

## Q13. Which events should enqueue a literature question automatically?

**Undecided.** The librarian works when asked. The owner wants it to work automatically. Which events should
trigger a search?

**Why it matters.** A queue that fills with noise is worse than no queue.

**Candidate answers.**
- A gate fails with a message the bench has never seen before.
- A manifest is written with `sensitivity: unknown`.
- A report contains "we do not know" or "unexplained".
- A new parameter is introduced without a citation.

**What would decide it.** The bench's own history: which of these would have caught a real gap. The triggers
listed in `AGENTS.md` §3a are "нужен параметр", "стало хуже", "будем перебирать", "не проверяли" — those are
the four the project already knows about.

**Search for:** (methodological) — this is a question for the owner.

---

## Q14. What counts as "the same mechanism" across series?

**Undecided.** A meta-analysis across experiments needs to group artifacts by mechanism. `trait_effect` in one
series and `signal_gain` in another may be the same mechanism with two names, or two mechanisms.

**Why it matters.** Without a grouping rule, the meta-analysis reports per-series numbers and no meta-pattern.

**Candidate answers.**
- A mechanism is a named config field.
- A mechanism is a named config field plus the code path it activates.
- A mechanism is a declared tag in the manifest, assigned by the author.

**What would decide it.** Whether the literature has a vocabulary for "the same mechanism under two names".

**Search for:** ontology of mechanisms in biology; mechanism individuation philosophy of science; "same
mechanism" criteria.

---

**Answer: a mechanism is individuated by the phenomenon it explains and by its causal organisation,
not by a parameter name.** The mechanist literature (Machamer, Darden & Craver) defines a mechanism as
entities and activities organised so as to produce a phenomenon; Glennan's minimal definition drops the
requirement of regularity; individuation is relative to the phenomenon. **Operational test for `trait_effect`
versus `signal_gain`:** they are the same mechanism only if they explain the same phenomenon AND an
intervention in one changes the other in the same way (mutual manipulability). If the phenomenon is the same
but the interventions are independent, they are two mechanisms sharing a functional name. **What we do:** the
meta-analysis must group by causal organisation, and record `same_mechanism` / `related_mechanism` /
`unresolved` rather than forcing a merge. Sources: Machamer, Darden & Craver 2000; Stanford Encyclopedia,
Mechanisms in Science; Rubenstein et al. 2017 (causal consistency).

## Summary table

| # | question | can a search answer it? | blocks which change |
|---|---|---|---|
| Q1 | minimal ontology of a world | yes | the whole design (Part 5, 11–13) |
| Q2 | is a within-cell measure a knob | yes | P3 of manifesto 037 |
| Q3 | units of reproduction and group genome | yes | change 13 |
| Q4 | inheritance at growth | yes | change 12 |
| Q5 | unstable diffusion coefficient | yes | change 6 |
| Q6 | how much clipping is too much | yes | change 6 |
| Q7 | maintenance versus repair naming | **no, owner** | change 11 |
| Q8 | component matching rule | yes | change 5 |
| Q9 | different boundary conditions | yes | change 4 |
| Q10 | diff or hashes | **no, owner** | change 3 |
| Q11 | periodic initial condition | yes | change 4 |
| Q12 | generated text or changed model | **no, owner** | change 7 |
| Q13 | automatic literature triggers | **no, owner** | change 9 |
| Q14 | what is "the same mechanism" | yes | change 10 |
