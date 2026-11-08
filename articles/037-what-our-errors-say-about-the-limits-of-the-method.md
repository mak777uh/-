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

| # | the error | the shape of it | how it was found | where the evidence is |
|---|---|---|---|---|
| 1 | a mechanism that added resource every step | a tap, not a feedback loop | recomputation | `reports/` (6 mentions of the tap) |
| 2 | two arms given unequal doses | the comparison measured the dose | recomputation | `reports/` (116 mentions of dose) |
| 3 | an effect clipped by the resource ceiling | the recorded dose was not the dose applied | recomputation | `reports/` (12 mentions of the ceiling) |
| 4 | a trait the world never read | the "selection" was a tautology | code reading | `lab/reviews/2026-11-07-033-v3-independent.md` §"сквозная проверка кодом" |
| 5 | a "paired design" that was a no-op | the arms were already seeded identically | an independent referee | `lab/reviews/2026-11-07-033-independent.md` |
| 6 | a signal advantage that did not replicate | one lead, ten seeds, p = 0.28 | an independent referee | `reports/` and the 033 review round 2 |
| 7 | a zero-cost control that could not fail | at zero cost the trait entered no equation | an independent referee | `lab/reviews/2026-11-07-033-v3-independent.md` |

**A note on where the evidence is, because it matters for the argument.** Errors 1-3 and 6 are documented in our
own reports: we found them ourselves, by recomputing. **Errors 4, 5 and 7 are documented only in the referee's
reviews, not in our reports.** In those three cases the error was in a design we had already described as sound,
and it was an outside reader who found it. That asymmetry is itself part of the argument of §1: a
hypothesis-first design does not merely fail to catch its own errors; **it reports them as results.**

**The common shape — for three of the seven, not for all seven.** A referee of this document pointed out that
the shape fits errors 4, 5 and 7 and does not fit the other four, and the referee is right:

| # | does it fit "the mechanism was assumed present"? |
|---|---|
| 1 | **no** — the mechanism was present but **mischaracterised**: a tap was called a feedback loop |
| 2 | **no** — the comparison was **confounded** by unequal doses; bit-identity would have been the opposite failure |
| 3 | **no** — a **logging** error: the recorded dose was not the applied dose |
| 6 | **no** — the manipulation **did** reach the dynamics; the claim was **underpowered** (ten seeds, p = 0.28) |
| 4, 5, 7 | **yes** — the mechanism was assumed and was not there |

**So the common shape is not one shape but two, and only one of them is the one we claimed:**

- **absent mechanism** (4, 5, 7): the check is *compare two arms that must differ; if they are bit-identical,
  the manipulation does not reach the dynamics.*
- **present but misdescribed mechanism** (1, 2, 3, 6): the check is different, and it is the one we now run —
  *state what the manipulation does to the dynamics, in arithmetic, before the run.*

**The correction matters, and it weakens the claim in a way that must be stated.** We originally wrote that one
sentence would have caught all seven. It would have caught three. The other four needed a different instrument,
and the fact that we found them by recomputation rather than by a check is the actual finding: **we had no
instrument at all for "the mechanism is present but I have described it wrongly", and that is the more common
error of the two.**

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

**The evidence from our own world — and the result that contradicts the first version of this paragraph.** The
first version said: *four designs were built to make a signal pay; in every one the effect was absent, equal in
all arms, or smaller than the difference between two implementations of the same control.* **That is false against
our own record.** A referee checked it against article 034, which reports, on 20 seeds with R1 20/20:

| arm | paired difference vs `none` | seeds positive |
|---|---|---|
| `local` | +0.0117 | 14/20 |
| `wave` | +0.0080 | 11/20 |
| **`rule`** | **+0.0512** | **18/20** (binomial p ≈ 0.0004) |
| `ab` | +0.0172 | 15/20 |

**The `rule` arm is a real effect, and it is the case the first version of this paragraph said could not exist.**
The corrected statement is the one the select/specify distinction makes possible:

- **`rule` does not add a term to the dynamics.** It **modulates a cell's upkeep** as a function of the signal,
  and which cells benefit is then decided by **selection**. The signal is not a term we wrote into the behaviour;
  it is a quantity the cells compete over.
- **That is selection, not specification**, and it is exactly the class of design §2 says is *not* excluded by
  the argument.
- **The other three arms (`local`, `wave`, `ab`) are the specification case**, and there the first version's
  description holds: the effect was small, and in the `wave` case indistinguishable from the control.

**So the evidence supports a narrower claim than the one we first made:** in the designs where the signal was a
term in a rule, the effect was ours; in the one design where the signal modulated a cost and selection decided the
outcome, the effect was real. **The first version of this document reported the opposite, and it was wrong.**

**A second line of evidence, which survives.** When the trait was made to cost nothing, the trait entered no
equation at all, and the "selection" that had been reported was a tautology (review of 033 v3,
`lab/reviews/2026-11-07-033-v3-independent.md`). That result is about **specification**: a term at zero weight is
still a term, and it does nothing.

**Why this is a property of the class, not of our tuning — and where the argument is weakest.** A parameter is a
quantity we choose. A system whose state evolves as a function of chosen quantities can produce, at best, the
trajectories those quantities admit. A larger field, a longer memory, a better controller: each is another chosen
quantity. This is an argument about the form of the model, not its size.

**Stated this way, the argument is close to a tautology**, and a tautology is not a finding: "a system that can
only do what its parameters allow can only do what its parameters allow" is true and empty. The argument acquires
content only from its **second premise**, which is a definitional choice and must be named as one:

> **We define the property we are looking for as independence from the modeller's choices.**

That definition is not forced. The alternative definition is the one the field mostly uses: *a property is
interesting if it is hard to produce and was not put there on purpose*, where "on purpose" means at the level of
the mechanism, not at the level of the parameter. Under that definition, a parameterised model **can** produce
interesting behaviour — the behaviour is not a term we wrote, even though the parameter is a number we chose.

**The two definitions are not equivalent, and the choice between them is the actual content of this manifesto.**
We choose the second half of the field's definition — *not put there on purpose* — and we sharpen "on purpose" to
"at any level, including the choice of which parameters exist". That sharpening is what makes the claim
falsifiable: §5 states what would show it is empty.

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

**Our reading of the evidence, restated as ignorance rather than as a boundary.** A referee of this document
made the decisive objection: **as written, the claim cannot fail.** "A different ontology" was defined only
negatively — *not a better parameter, but a different kind of object* — and with no operational test, any result
can be absorbed: if a new object appears, it is called an extension of the same ontology; if none appears, it is
called the prediction. **That is exactly what §5 of this document condemns as a slogan, and the claim was one.**

**The defensible version, which is what we now assert:**

> **The designs we surveyed have not produced a new kind of object. We do not know whether they can.**

That is a statement about a survey and about our ignorance. It is not a theorem about a class, and it does not
support the programme on its own.

**What would make it a boundary rather than an observation** — the operational test the first version lacked:

1. **Name the kind of object in advance.** Before the experiment, write down what a new kind of object would be in
   this world, in the world's own terms (a new conserved quantity, a new relation between cells, a new level at
   which selection acts), and what would count as its appearance.
2. **Name what would count as an extension.** If the candidate is expressible as a re-parameterisation of an
   existing kind, it is an extension — and that judgement is made **before** the result is known.
3. **Pre-register both.** The test is then falsifiable in the ordinary sense: a candidate that satisfies (1) and
   not (2) refutes the claim.

**We also correct a citation.** The first version said "the literature we surveyed is explicit about this". It is
not. Sayama & Nehaniv (2024, arXiv:2402.03961) list autopoiesis and self-examination reproduction as **open
problems** — *"it remains unclear how one could integrate..."* — not as a proven boundary. Citing an open problem
as an established limit is the kind of error this document is about, and a referee caught it.

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

### P4. In a finite, deterministic, closed system, unbounded novelty is impossible — this is a theorem, not a principle

**We withdraw P4 as a principle and state it as what it is.** A referee of this document pointed out that P4 has
two readings, and under neither is it a falsifiable principle:

- **trivial reading** — *behaviour computable only from a record is computable from the record* — true by
  definition and excludes nothing;
- **substantive reading** — *a finite closed deterministic system cannot produce unbounded novelty* — true, but it
  is a **theorem**, and a theorem is not falsified by an experiment.

**The theorem, with its assumptions and its source.** For a finite deterministic closed system, the Poincaré
recurrence time is an upper bound on any appearance of unbounded novelty: the trajectory must repeat. Adams,
Zenil, Davies and Walker (2017, *Scientific Reports* 7:997, doi 10.1038/s41598-017-00810-8) state this directly
and derive the corollary we were reaching for: **unbounded evolution is possible only for a subsystem that
interacts with an external environment.**

**What this changes about how we use it.** We do not test it; we **use its assumptions as a design constraint**.
A world in which we hope to see novelty must be **open** (something enters that the system does not produce),
**not finite-and-deterministic in its state space**, or **stochastic**. That is a checklist, not a hypothesis, and
it is the one genuinely deductive part of this document.

**What would violate its assumptions** (which is the only thing that can be "tested" here): a world that is
**closed** in the sense of the theorem, and still produces novelty. If we find one, the theorem's assumptions do
not apply to it, and we say so rather than claiming a refutation.

**What we keep as our own claim, now separated from the theorem.** The theorem says novelty cannot come from a
closed record. It does **not** say where it must come from. Our claim — that it must come from the environment,
another agent, or a source that is not a function of the record — is a **design choice**, and we label it as one.

### Why these four, and what the "fewer knobs" argument got wrong

The first version of this document said: each principle removes a degree of freedom, therefore rigour here means
having fewer knobs. **A referee showed that this argument cannot stand, for two reasons, and both are right.**

**First, it contradicts §2.** §2 says dependence on a parameter is the defect; §4 said fewer parameters is the
virtue. If parameter dependence is the problem, then removing parameters cannot be the solution — the model
becomes *less* able to differ from its alternatives, which makes it *harder* to falsify, not easier. Removing a
degree of freedom can strengthen a result or weaken it, and which one happens depends on whether the removed
freedom was one the modeller could have used to manufacture the result.

**Second, the four are not the same kind of thing.** The table below separates them honestly:

| | principle | what it constrains | kind |
|---|---|---|---|
| P1 | constraints on flows, not parameters | **the model** | methodological preference, with a definition |
| P2 | the environment is written and read by the agents | **the model** | **a claim about the world** |
| P3 | the primary measure is within-cell | **what may be reported** | **a claim about the world, and a measurement rule** |
| P4 | novelty cannot come from a closed record | **what may be claimed** | **a theorem, with assumptions** |

**Only P2 is a claim about the world that a single experiment can refute.** P1 is a choice of how to build; P3 is
a rule about what counts as evidence; P4 is a theorem we use as a design constraint. Presenting four items of
different kinds as one argument was a category error, and the corrected version says so.

**What the four do have in common, stated without the false arithmetic:** each one **moves a decision from after
the result to before it** — which constraints, which coupling, which measure, which assumptions. That is the
honest version of the "fewer knobs" intuition: not fewer parameters, but **fewer decisions left open until after
we have seen the data.**

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
