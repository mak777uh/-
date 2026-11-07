# K — patterns of thought from *The Awakening of Intelligence*, and what they mean for the pond

**What this file is.** Not a summary of the book. A record of **patterns of thought** found while reading it, each
checked against our own experiments: does the pattern appear in our world, what does it explain, and what
experiment would test it. The owner's idea: patterns are fractal and transfer between domains, so a strong mind's
*way of moving* may hold structures we have not tried.

**Source:** J. Krishnamurti, *The Awakening of Intelligence* (1973), 409 pages, 176 000 words, converted to text at
`_exports/k-awakening-of-intelligence.txt` (25 chunks). Read in order; this file grows as reading proceeds.

---

## P1. The image: a cell reacts to its own compressed memory, not to the event

**The move.** The mind forms an *image* from an event (an insult, a pleasure) and then reacts to the image rather
than to the event. The image is compressed memory standing in for the event. "If you do not form an image **now**,
the past images have no place."

**In our world.** Our cell has exactly such an image: `pred`, the exponential moving average of the resource. The
cell's step rule (`plastic_gate="pred"`) fires on `resource − pred`, i.e. on the **deviation from its own smoothed
memory**, not on the resource itself.

**What it explains.** E10: the cell could not distinguish the *pattern* of the signal (regular / random / clustered
/ matched) even when the dose was equal. A smoothed image **erases** exactly the temporal structure a pattern
consists of. The cell was not blind to the signal — it was looking at its own image of it.

**Testable.** Remove `pred` (react to the raw resource) and re-run E10's four patterns at equal dose. If the
patterns separate without `pred` and do not with it, P1 is the mechanism of the E10 null.

**Status:** hypothesis, not yet run.

---

## P2. Dependency on conditions hides the thing you wanted to see

**The move.** If you depend on conditions in order to see yourself, you will see the *conditions*, not yourself.
"Which means you depend on the environment to see yourself." And: "If I need them, then I am lost."

**In our world.** The cell depends on the signal to find food. In E8/E12 the *external* signal (unrelated noise)
**hurt** (−0.010) while the predictive one helped only weakly (+0.012, and only at one lead). The cell that
depends on a channel is at the channel's mercy.

**What it explains.** Why "more information" is not automatically better: a channel the cell depends on but cannot
verify is a liability, not a resource.

**Testable.** Give the cell a signal that is *sometimes* false (a fraction of events mislabelled). If dependency
is the problem, performance should fall **below** the no-signal control, not just lose the gain.

**Status:** partially supported by E8 (noise hurts); the "sometimes false" version not run.

---

## P3. "Not in principle — either it is so, or it is not"

**The move.** The interlocutor says "in principle, no". K refuses: "Not in principle. Either it is so, or it is
not." A principle is not evidence.

**In our world.** This is already our contract, and it earned its keep: on 07.11 four results were withdrawn
because they were true "in principle" (a signal advantage, a trait shift, a paired design) and false in the
numbers.

**What it explains.** Nothing new — it **confirms** the method. Recorded because it is the same move made in a
different domain, which is the point of this file.

---

## P4. The beginning is the first step and the last step

**The move.** There is no transitional period in which the rule is different. If the condition holds at the start,
it holds throughout. "The beginning is the first step and the last step."

**In our world.** We have repeatedly looked for **regimes**: "works at low density, not at high"; "works at lag 10,
not at lag 2". Each time we reported a *window* and then found the window did not survive replication.

**What it explains.** Possibly our "regimes" are artefacts of **when we looked**. Every headline result of 07.11
was computed on the **last window**; the referee's objection to E15 was precisely that other windows told a
different story.

**Testable.** For every curve experiment, report the effect **from the first 50 steps** as well as the last
window. If an effect is real it should be visible early; if it only appears late, it is accumulation or drift.

**Status:** a rule for future analyses, cheap to adopt.

---

## P5. Analysis is the denial of action

**The move.** "Analysis is the denial of action; action being always in the active present." Analysis involves
time, and each incomplete analysis becomes the knowledge from which the next analysis proceeds — so error
compounds and nothing is done.

**In our world.** Our cell *analyses* every step: it computes the deviation from `pred`, decides whether to move,
and the decision is stored as a new `pred` for the next step. The analysis feeds itself.

**What it explains.** The "trap of inaction" (S22/G3): the adaptive prediction tracks the falling resource, so the
cell stops qualifying to move. The cell analysed its way into standing still.

**Testable.** Already partly tested (S22: baseline 0.340, greedy_ema 0.166). The prediction of P5 is stronger:
the trap should appear **whenever** the decision variable is a function of the cell's own past, and disappear when
it is not.

**Status:** supported by S22; the stronger form not tested.

---

## P6. The observer is the past

**The move.** "The analyser, what is he? He is the past, the accumulated knowledge of all the things he has
analysed. And with that knowledge — which is the past — he analyses the present."

**In our world.** `pred` *is* the past, and the gate compares the present against it. The cell's "observer" is its
own history.

**What it explains.** Why adding memory (E6) raised every arm equally instead of separating the patterns: a
richer past makes a better mirror of the past, not a better view of the present.

**Testable.** Same as P1: the `pred`-removal experiment separates P1 and P6 from the alternative "the cell lacks
a decoder".

**Status:** hypothesis.

---

## P7. Energy comes with the possibility of change

**The move.** "Energy comes with the possibility of change; if there is no possibility of change, then energy
wastes away." And: "most of us waste our energies in conflict."

**In our world.** A cell's energy is spent on upkeep, repair and movement. Conflict has a concrete analogue:
**movement that does not pay** is wasted energy. E1 measured exactly this: at 53.7 % density with slow recovery,
moving cost more than it gained (−0.030).

**What it explains.** The boundary of movement profitability is, in this language, the boundary between energy
spent and energy wasted.

**Testable.** Already measured (E1, 240 runs). The pattern adds a prediction: a cell in a **no-win** environment
should stop moving *before* it starves — which is the trap of inaction again (P5).

**Status:** consistent with E1 and S22.

---

## Open questions raised by the reading so far

1. Is `pred` the mechanism of the E10 null? (P1/P6 — one experiment settles it.)
2. Does a *sometimes-false* signal fall below the no-signal control? (P2)
3. Are our "regimes" artefacts of looking at the last window? (P4 — cheap to check on existing artifacts.)
4. Does the trap of inaction appear for *any* self-referential decision variable? (P5)

---

## P8. Correction of "what is" is itself the disorder

**The move.** "The moment you try to correct it, you are bringing disorder. But if you merely observe actually
what is, then what is, is order." And: "It is only when you try to change 'what is' that there is disorder;
because you want to change according to the knowledge which you have acquired. That knowledge is the past."

**In our world.** Our cell **corrects**: it compares the present to `pred` and steps when the deviation is
negative. The correction is driven by the past (`pred`), applied to a present that is not the past. That is the
"contradiction → distortion → disorder" chain in mechanical form.

**What it explains.** The trap of inaction (S22) is not a bug of the threshold — it is what **correction by the
past** does when the present is moving away from the past. The cell keeps correcting toward a description that is
already stale.

**Testable.** The `pred`-removal experiment (P1) tests this too, but P8 makes a sharper prediction: a cell whose
decision uses `pred` should do **worse the faster the environment changes**, and the disadvantage should grow
with the rate of change. That is a sweep, not a single point.

**Status:** hypothesis; the rate sweep is new.

---

## P9. Recording is what makes the hurt persist

**The move.** "You say something to me which hurts me, and the pain of that hurt is recorded. The memory of that
continues and when there is further pain, it is recorded again. So the hurt is being strengthened from childhood
on. Whereas, if I observe it completely... then it is not recorded as a hurt."

**In our world.** This is the **precise** mechanism of `pred`: every deviation is **recorded** into the average,
and the recording **strengthens** the image. A cell that is repeatedly short of food builds a `pred` that says
"food is low", and then judges every later step against that record.

**What it explains.** Why the trap is **sticky**: the more the cell experiences shortage, the more its record says
shortage, and the more it stops moving — even when food returns. S22's `greedy_ema` (0.166) against `baseline`
(0.340) is exactly this.

**Testable.** The decisive test: give the cell a **recovery** — food returns after a long shortage. A cell with
`pred` should be **slow to resume moving**; a cell without `pred` should resume at once. This separates
"recording" from "threshold" and is a direct measurement of P9.

**Status:** hypothesis; the recovery test is new and cheap.

---

## P10. Resistance builds the wall that makes the hurt worse

**The move.** "You resist that hurt and therefore you build a wall. And when you build a wall you are isolating
yourself. Therefore you are strengthening the isolation, by which you will get more and more hurt."

**In our world.** The cell's `plastic_gate` is a **wall**: it acts only when the deviation crosses a condition.
A wall means the cell **ignores** most of what happens and reacts only to the crossings. And the wall is built by
the same record that is supposed to protect it.

**What it explains.** Why **more** signal did not help (E8, E12): the cell's wall filtered the signal before it
could be used. Adding a channel to a system that resists input adds nothing.

**Testable.** Open the wall: act on the **magnitude** of the deviation rather than on its sign (continuous
response instead of a gate). If the closed loop starts to respond to signal structure, the wall was the filter.

**Status:** hypothesis; a continuous-gate variant is a small change to the step rule.

---

## P11. The observer is the observed

**The move.** "The observer is the past... The observer is the observed, the two are not separate." And the
consequence: "where there is an observer separating himself from the thing he observes, there must be conflict."

**In our world.** This is the **structural** statement of P1/P6, and it has a measurable form: the cell's decision
variable is `resource − pred`, i.e. **the observed minus the observer**. They are not two quantities; they are one
difference. The cell cannot have a "view of the environment" separate from its own record — by construction.

**What it explains.** Why E10's four patterns were indistinguishable: the decision variable is a **difference
between the present and the past**, and a difference of that kind is invariant to many transformations of the
pattern. The cell was not failing to see the pattern; it was **looking at a quantity in which the pattern had
already cancelled**.

**Testable, and this is the sharpest test in the file.** Compute, for the E10 artifact, the actual distribution of
`resource − pred` under the four patterns. If the four distributions are **statistically indistinguishable**, the
null is explained mechanically and no experiment on the cell is needed — the information was destroyed **before**
the decision. That can be done on existing data.

**Status:** testable on data we already have.

---

## P12. Thought is the response of memory

**The move.** "Surely thought is the response of memory — memory as knowledge, memory as experience which has been
accumulated."

**In our world.** The cell's "thought" (its step decision) is **literally** the response of memory: `pred` is
accumulated experience, and the decision is a function of it. This is not an analogy; it is the implementation.

**What it explains.** It sets the ceiling: a cell whose only thought is the response of memory can **never** do
something that is not already in its memory. That is the same statement as the literature's "evolution inside a
given ontology" — and it is why our world plateaus.

**Testable.** Not directly; it is a **design constraint**. It says: to get novelty, the decision must contain a
term that is **not** a function of the past. That is a concrete design requirement for the next world.

**Status:** design principle.

---

## P13. Thought is never free — it can only imagine freedom

**The move.** "Thought is the response of the past, which may project itself into the future, going through the
present, modifying it as the future. But it is still the past. So thought is never free — how can it be? It can
imagine what is freedom, it can idealize what freedom should be, create a Utopia of freedom. But thought itself is
of the past and therefore it is not free, it is always old."

**In our world.** This is the strongest statement of the ceiling we keep hitting. Our cell's decision is a function
of `pred`; `pred` is the past. Therefore the cell **cannot** produce a decision that is not in its past. It can
only **re-weight** its past. Every mechanism we added — field, niche, signal, memory, decoder — was a
**re-weighting of the past**, and that is why each one either did nothing or helped equally in all arms.

**What it explains.** All of 07.11's nulls in one sentence. And the literature's "evolution inside a given
ontology" is the same statement in evolutionary language.

**Testable / design requirement.** Not a test — a **constraint on any future design**: the decision must contain a
term that is **not** a function of the cell's own past. Candidates: the present resource read **directly** (no
`pred`), or a term supplied from **outside** the cell's history (another cell, the environment's instantaneous
state).

**Status:** design principle, and the clearest one in the file.

---

## P14. Recording is the same act for pleasure and for fear

**The move.** "The very process of recording is knowledge, which is the past, and thought is the past. So thought,
as pleasure, is sustained... So thought sustains and gives nourishment to pleasure as well as to fear. Thought is
responsible for this."

**In our world.** `pred` does not know whether it is recording plenty or shortage — it is a **symmetric average**.
The same mechanism that lets a cell "remember" a good patch also makes it **stuck** in a bad one. There is no
separate "good memory" and "bad memory"; there is one recorder.

**What it explains.** Why we could not fix the trap by tuning: any change that makes the record **more useful** in
plenty makes it **more sticky** in shortage. The mechanism cannot be tuned to be good at one and bad at the other.

**Testable.** Sweep the smoothing rate `plastic_eta` over a wide range, in **both** a stable and a
suddenly-changing environment. P14 predicts the optimum is **different** in the two, so no single value is good
for both — and that the best stable-environment value is the worst changing-environment value.

**Status:** hypothesis; the two-environment sweep is a clean test.

---

## P15. Thought has a rational function and an irrational one — and they are the same machinery

**The move.** "There must be the exercise of thought in doing things. Technologically, in the office, when you
cook... knowledge must function perfectly. There is the rationality, the logic of thought in action. But also
thought becomes totally irrational when it sustains pleasure or fear."

**In our world.** The cell's `pred` is **rational** when the environment is stationary (a good estimate of where
food is) and **irrational** when the environment changes (an estimate of where food *was*). **Same code, opposite
verdict** — the difference is entirely in the environment.

**What it explains.** Why our results were **contradictory across experiments**: the same `pred` helped in E1's
fast-recovery cells and hurt in the slow-recovery ones. We reported this as "the sign depends on recovery rate" —
but the pattern says something sharper: the sign depends on **whether the environment is stationary relative to
the record's own timescale**.

**Testable.** The ratio `(environment change time) / (record time constant)` should predict the sign of the
effect. If it does, `pred` is not "good" or "bad" — it is **matched or mismatched**, and the sign is a function of
that ratio. That is a **quantitative law**, not a regime.

**Status:** testable on existing artifacts (E1 has three recovery rates; E15 has three strengths).

---

## P16. "As you think, what you think, you are"

**The move.** "As you think, what you think, you are. You think you are greater than somebody else, that you are
inferior... what you think you are."

**In our world.** The cell **is** its decision rule. There is nothing else to it — no separate "cell" behind the
rule. So its identity is exactly `resource − pred`, and the record is not something the cell *has*; it is
something the cell *is*.

**What it explains.** Why "adding" a mechanism never produced a new kind of agent: there is no substrate to add
to. A mechanism added to a cell is a mechanism added to **the same rule**, i.e. a re-weighting (P13 again).

**Testable.** Not directly; it is the **justification** for the next design step: to get a different agent, the
**rule** must be different, not the parameters.

**Status:** design principle.

---

## P17. Resistance is what creates the separation it is trying to escape

**The move.** "The moment you resist, you are separate from the noise... The noise goes on, I can cut myself off
from it by resisting it, putting a wall between myself and that noise. Then what takes place, when I resist
something? There is conflict, isn't there?" And: "as long as there is resistance, there must be conflict."

**In our world.** The gate is the wall. And the wall does something specific: it **creates the separation** it was
built to manage. A cell that resists the environment (acts only on threshold crossings) is thereby **separated**
from the environment — it stops reading it continuously and reads only the crossings.

**What it explains.** Two of our results at once. (a) E8/E12: adding a signal to a cell with a wall added nothing,
because the wall filtered it. (b) The trap of inaction: the wall is where the cell "protects" itself from a
falling resource, and the wall is exactly what stops it acting.

**Testable.** Replace the gate with a **continuous** response (act on the magnitude of the deviation, not on its
sign). If the cell then responds to the *structure* of the environment rather than only to crossings, the wall was
the filter. Small change to the step rule; same experiment as E10.

**Status:** hypothesis; the continuous-gate variant is the cheapest test in this file.

---

## P18. The description is not the described

**The move.** "Knowing that the description is not the described." Repeated throughout: the map is not the
territory; the word is not the thing.

**In our world.** This is `pred` again, in its most general form: `pred` is a **description** of the resource, and
the cell acts on the description. Every mechanism we built was a **better description** — a field, a memory, a
signal — and every one failed to change the outcome, because a better description of a moving thing is still not
the thing.

**What it explains.** Why our "add a channel" strategy had a ceiling: we kept improving the description.

**Testable / design requirement.** The decision must use the **described** (the instantaneous resource) at least
in part, not only the description. That is the `pred`-removal experiment again, now with a reason.

**Status:** design principle.

---

## P19. Relationship is not dependence; dependence destroys relationship

**The move.** "To be related means not to be dependent on each other, not to escape from your loneliness through
another, not to try to find comfort, companionship, through another. When you seek comfort through another, are
dependent... can there be any kind of relationship? Or are you then using each other?"

**In our world.** This is the **sharpest available statement about our cells' interaction**, and it says our world
has **no relationship at all**. Cells are not related to each other; they are **adjacent**. They exchange nothing,
they do not depend on each other, they do not use each other. Each is alone in its cell, reading only its own
resource.

**What it explains.** This is, in one sentence, why nothing social ever appeared in our world: **there is no
relationship to have**. No cooperation, no conflict, no niche, no inheritance of environment — because a cell's
only relation is to its own cell.

**And it is the design requirement for the next world.** Not "add a social mechanism", but: **create a relation
that is not dependence and not isolation.** Concretely: cells must be able to **affect each other's terms** (the
resource they receive, the cost they pay) **without one being able to extract from the other**. That is the
difference between a shared environment (which we have) and a relationship (which we do not).

**Testable.** A minimal version: let a cell's upkeep depend on the **state of its neighbours** (not on their
identity, not on a transfer). If any structure of dependence appears — cells clustering where upkeep is low,
moving away where it is high — then a relationship exists and can be studied. If nothing appears, the world is
still a set of isolated cells.

**Status:** hypothesis; this is the most promising **design** direction in the file.

---

## P20. "You are the world" — the agent and its environment are one process

**The move.** "We are the world and the world is us. The world is each one of us... Each one of us is that
culture; the community is each one of us — we are not separate from it."

**In our world.** Our cells **are** the resource field in the sense that they deplete it; but the field is not
**them**. There is a one-way relation: cells read the field, the field does not read the cells. The pattern says
the interesting case is the **two-way** one.

**What it explains.** Why niche construction (E3) failed: we made the field **written by** cells, but the cells did
not **read** what they wrote in a way that changed their own terms. The loop was open at the reading end.

**Testable.** The two-way version: the field that cells write must be the field that **sets their own upkeep**.
Then "the world is us" becomes a measurable loop rather than a metaphor.

**Status:** hypothesis; overlaps P19 and is the same design move.

---

## What the reading has changed in our plan (updated)

1. **The `pred`-removal experiment is the top priority** (P1, P6, P8, P9, P10, P11, P13, P18).
2. **Check on existing data first:** is `resource − pred` statistically indistinguishable across E10's four
   patterns? (P11) — zero new runs.
3. **The continuous-gate test:** act on the magnitude, not the sign (P17) — cheapest change to the step rule.
4. **The recovery test:** does a cell with `pred` resume moving when food returns? (P9)
5. **The two-environment sweep:** is the best smoothing rate different in stable vs changing environments? (P14)
6. **The ratio law:** does `(change time)/(record time constant)` predict the sign of the effect? (P15) — on
   existing E1/E15 artifacts.
7. **New measurement rule:** report the effect **from the first steps**, not only the last window (P4).
8. **New design requirement:** the decision must contain a term that is **not** a function of the cell's past
   (P13, P18).
9. **The design direction for the next world:** create a **relationship** between cells — a two-way dependence
   that is neither isolation nor extraction (P19, P20).

---

## Reading progress

- Pages 1–59 of 409 read (Part II talk 1 complete, start of talk 2 "Relationship").
- Next: the rest of talk 2 (loneliness, love, death), then talk 3 (religious experience, meditation).
