# What our own errors say about the limits of the current method

**A manifesto. Three claims about why the present designs cannot find the living, and what we build instead.**

---

## Abstract

We report the errors our own programme produced over 583 reports and 43 articles about a minimal artificial
world, and we draw a conclusion that is uncomfortable for us and, we think, general.

**Claim 1.** In five independent designs the manipulation did not reach the dynamics, and in four of those the
error was invisible until a reader recomputed the numbers. The errors had a common shape: **the design assumed a
mechanism was present and measured its consequences, without first establishing that the mechanism could act at
all.** This is not carelessness. It is what happens when a design is built from a hypothesis about a mechanism
rather than from a description of what the world does.

**Claim 2.** The designs available in the current literature — resource fields, signals, niches, memory, adaptive
controllers — are all **machines that grow out of conditions that were programmed in advance.** In every case we
tried, the "living" behaviour was a consequence of a term we had written, and the term's absence removed the
behaviour entirely. This is not a failure of tuning. It is a property of the class: **a system whose behaviour is
a function of parameters we set can only exhibit behaviour we could have set.**

**Claim 3.** Therefore we do not expect the next result to come from another pass over the same space. We propose
to **build the world from first principles**, state what those principles are, and test them experimentally — and
we state in advance what would falsify each one.

We also state the risk honestly: a claim that the current method cannot find something is a claim about a
boundary, and boundaries are easy to assert and hard to prove. We give the evidence we have and the experiments
that would break our own position.

---

## 1. The errors, and what they have in common

The programme ran five designs intended to make a heritable trait respond to selection, and four further designs
intended to make a signal pay. The public record is 583 reports and 43 articles; the register of eliminated
directions has 45 entries. The errors below are the ones that survived into a report before being retracted.

| # | the error | the shape of it | how it was found |
|---|---|---|---|
| 1 | a mechanism that added resource every step | a tap, not a feedback loop | recomputation |
| 2 | two arms given unequal doses | the comparison measured the dose | recomputation |
| 3 | an effect clipped by the resource ceiling | the recorded dose was not the dose applied | recomputation |
| 4 | a trait the world never read | the "selection" was a tautology | code reading |
| 5 | a "paired design" that was a no-op | the arms were already seeded identically | an independent referee |
| 6 | a signal advantage that did not replicate | one lead, ten seeds, p = 0.28 | an independent referee |
| 7 | a zero-cost control that could not fail | at zero cost the trait entered no equation | an independent referee |

**The common shape.** In every one of the seven, the design **assumed the mechanism was present** and then
measured its consequences. In none of them was there a step that established, **before the measurement**, that
the mechanism could act. The check that would have caught all seven is one sentence long: *compare two arms that
must differ; if they are bit-identical, the manipulation does not reach the dynamics.*

**Why this is structural, not accidental.** A design built from a hypothesis about a mechanism has the hypothesis
in it. The hypothesis decides what counts as the manipulation, what counts as the outcome, and what counts as a
failure. When the manipulation is inert, the design reports a null, and a null is indistinguishable from a
mechanism that does not work. **The design cannot tell "the mechanism is wrong" from "the mechanism is not
there."** That is not a bug in our code; it is a property of hypothesis-first design.

**What we changed.** Seven checks now run before a series: connectivity (the arms must differ), a positive
control, a response check, a sensitivity calculation, a refusal rule, a pre-registered manifest, and a report form
that forbids adjectives and requires the first steps. The manifest gate refuses an experiment that does not
record how the manipulation was checked to reach the dynamics. This is a repair of the method, and it is the
reason the rest of this document is not another list of failures.

---

## 2. Why the available designs can only imitate the living

We now state the claim that matters, and we state it in the strongest form we can defend.

**The claim.** Every design in the current literature that we could implement — a resource field with renewal, a
signal that predicts the field, a constructed niche, a memory of the past, an adaptive controller — is a
**machine whose behaviour is a function of conditions that were programmed in advance.** The living-looking
behaviour is a consequence of those conditions. Remove the condition and the behaviour disappears, exactly and
completely.

**The evidence from our own world.** Four designs were built to make a signal pay. In every one, the effect was
either absent, or equal in all arms, or smaller than the difference between two implementations of the same
control. The pattern was consistent: **the signal was a term in a rule, and the rule was ours.** The cell did not
use the signal; the rule did. A second line of evidence: when the trait was made to cost nothing, the trait
entered no equation at all, and the "selection" that had been reported was a tautology.

**Why this is a property of the class, not of our tuning.** A parameter is a quantity we choose. A system whose
state evolves as a function of chosen quantities can produce, at best, the trajectories those quantities admit.
If the behaviour we are looking for is defined by *not* being a function of our choices, then no arrangement of
our choices can produce it. This is an argument about the form of the model, not about its size. A larger field,
a longer memory, a better controller: each is another chosen quantity.

**What this does not say.** It does not say that the living cannot be modelled. It says that **a model whose
degrees of freedom are all set by the modeller cannot exhibit a property defined as independence from the
modeller's choices.** The distinction matters, and we return to it in §4.

---

## 3. The boundary of the graph that grows from below

The scientific graph grows from below: a result is established, a neighbouring result is established, and the
edge advances one step at a time. This is the right way to make knowledge reliable, and it is the reason the
graph is trustworthy.

**It is also the reason the graph has not reached the question we are asking.** The graph advances by
**incremental extension of what is already established**. A question whose answer requires a **different
ontology** — not a better parameter, but a different kind of object — is not reachable by extending the edge. The
edge can only extend into the space the current ontology defines.

**Our reading of the evidence.** The models that have produced open-ended behaviour all did so by **adding a
mechanism to an existing ontology**: a new instruction, a new resource, a new interaction. None produced a new
ontology. The literature we surveyed is explicit about this: the boundary is not "we have not found the right
parameters" but "the class of models we build cannot generate a new class."

**What we therefore propose, and what it costs.** We propose to work **outside** the graph for the construction
and **inside** it for the validation:

1. **Outside:** build worlds from first principles, state the principles, and let the experiment decide. The
   principles are not taken from the literature; they are taken from what a world must have to be a world.
2. **Inside:** when a pattern appears, **descend it into the graph** — state it in the language of an established
   result, connect it to a citation, and design the experiment that would make it a result rather than an
   observation.

**The cost of this proposal is a real risk, and we state it.** Working outside the graph means that a result may
be **unrecognisable** to the graph when it arrives. The descent is the hard part, not the construction. A
manifesto that promised the construction would be enough would be dishonest; the work is in the descent.

---

## 4. First principles: what we will build from, and why each is more rigorous

We do not propose a new theory. We propose **four principles**, each of which is a statement about a world that
can be **falsified by an experiment we can run**, and each of which is **weaker** than the assumptions the current
designs make. Weaker assumptions are more rigorous, in the sense that matters: a result that survives a weaker
assumption is a stronger result.

### P1. A world is a set of constraints on flows, not a set of parameters

**The principle.** A world is specified by **what is conserved, what flows, and what limits the flow**. A
parameter is a number in a rule; a constraint is a relation that must hold. A cell that consumes a resource is
constrained by the conservation of that resource, not by a consumption rate we chose.

**Why it is more rigorous.** A parameter can be tuned until the behaviour appears; a constraint cannot. If a
behaviour appears under a conservation law, it is not an artefact of a number we picked. **A result under a
constraint is a result about the world; a result under a parameter is a result about the parameter.**

**What would falsify it.** A world built this way in which the behaviour is **identical** to the behaviour of the
same world with the constraint replaced by a tuned parameter. If the constraint adds nothing, the principle is
empty.

### P2. The environment is written by the agents and read by the agents, in both directions

**The principle.** The state that the agents modify must be **the same state that sets their own terms**. A field
that the cells deplete but which does not set their costs is a one-way coupling; it is not an environment in the
sense that matters.

**Why it is more rigorous.** A one-way coupling lets the modeller set the terms independently of the agents, which
is exactly the freedom that produces imitation. A two-way coupling **removes a degree of freedom from the
modeller**: the terms are now a function of the agents' history, and the modeller cannot set them.

**What would falsify it.** A two-way world in which the behaviour is the same as in the one-way world. If the
return path changes nothing, the principle is decoration.

### P3. The relation between a cell and its situation must be measurable inside the cell

**The principle.** The primary measurement is **the fraction of a cell's behavioural variance explained by its
current situation, versus the fraction explained by its own history.** Not a ranking of cells against each other.
A ranking is blind to the difference between an ordered and a disordered system: two cells can have the same rank
and be one in harmony and one in conflict.

**Why it is more rigorous.** A between-cell measure can be produced by a parameter (give one arm a bonus and its
rank rises). A within-cell measure cannot: it compares a cell to its own situation, so no term we add can move it
except by changing what the cell reads. **The measure is not available to us as a knob.**

**What would falsify it.** A case in which the within-cell measure and the between-cell measure rank the same
worlds in the same order, **for reasons that are not trivial**. If the two measures never disagree, the first
adds nothing.

### P4. Novelty must enter from outside the agent's own history

**The principle.** An agent whose state is a record can compute only functions of that record. Therefore novelty
cannot originate inside the agent; it must enter from **the environment, another agent, or a source that is not a
function of the record.** This is a **constraint on the architecture**, not a preference.

**Why it is more rigorous.** It is a **deduction**, not an assumption: it follows from what a record is. An
architecture that violates it is not a candidate for open-ended behaviour, and can be excluded **before** the
experiment rather than after. **A principle that excludes designs in advance is more rigorous than a search that
tests them one by one.**

**What would falsify it.** A cell whose entire state is a record, in a world with no external source of novelty,
that nevertheless produces behaviour not predictable from its record. We do not believe this is possible, and we
state it as a claim we would be glad to be wrong about.

### Why these four and not others

Each of the four **removes a degree of freedom from the modeller**:

| principle | the freedom it removes |
|---|---|
| P1 constraints, not parameters | the freedom to tune until the behaviour appears |
| P2 two-way coupling | the freedom to set the agents' terms independently |
| P3 within-cell measurement | the freedom to move the metric with a bonus |
| P4 novelty from outside | the freedom to claim novelty inside a closed record |

**This is the whole argument in one line: rigour here means having fewer knobs.** A design with fewer knobs
produces results that are harder to produce and therefore worth more.

---

## 5. What we will do next, and what would make us stop

**The programme, in order.**

1. **Build the world from P1 and P2.** A world specified by conservation and flow, with the agents' terms set by
   the state the agents themselves write.
2. **Measure with P3.** The primary readout is the within-cell decomposition. Every run reports it.
3. **Test P4 as an exclusion.** Before any experiment, check whether the architecture violates P4. If it does, the
   experiment is not run.
4. **Descend every pattern into the graph.** A pattern that cannot be stated in the language of an established
   result is not a result; it is an observation, and it is reported as one.

**What would make us stop.** We commit to three stopping conditions, stated before the work:

- **If a world built under P1 and P2 produces behaviour that is also produced by a tuned-parameter version of the
  same world, P1 and P2 are empty** and the programme has no basis.
- **If the within-cell measure never disagrees with the between-cell measure, P3 is empty.**
- **If a cell violating P4 produces behaviour not predictable from its record, P4 is false** and the architecture
  constraint is wrong.

**We will report these outcomes as results, not as failures.** A manifesto that cannot fail is a slogan.

---

## 6. What this document does not claim

1. **It does not claim that the living has been found.** Nothing has been found. This is a statement of method.
2. **It does not claim that the current literature is wrong.** It claims that a class of designs cannot reach a
   particular question, and it gives the argument for the class, not for the literature.
3. **It does not claim that working outside the graph is safe.** §3 states the cost: the descent is the hard part.
4. **It does not claim that our seven errors are representative.** They are the errors we made; we argue they have
   a common shape, not that they are a sample.
5. **It does not claim that the four principles are new.** Conservation, two-way coupling, within-subject
   measurement and the limits of a record are old ideas. What is new here is the **use of all four together as a
   constraint on what may be built**, and the commitment to falsify each.

---

## Appendix: where the evidence is

| claim | where to check |
|---|---|
| seven errors, in the order reported | `docs/eliminations.md`, `reports/` |
| the five design checks and the manifest gate | `scripts/check_experiment_manifest.py`, `scripts/check_design.py` |
| the within-cell measure | `scripts/k_readouts.py` (self-test on synthetic data) |
| the four principles as constraints on a design | `lab/experiments/E18.json` (the first manifest written under them) |
| the corpus and its limits | `reports/2026-11-08-corpus-audit.md` |
