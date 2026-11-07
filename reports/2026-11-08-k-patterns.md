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

## What the reading has changed in our plan

1. **The `pred`-removal experiment is now the top priority.** P1, P6, P8, P9, P10, P11 all point at `pred`, and
   P11 can be **checked on existing data** before running anything.
2. **A new measurement rule:** report the effect **from the first steps**, not only the last window (P4).
3. **A new design requirement:** the decision must contain a term that is **not** a function of the past (P12).
4. **A new test type:** the **recovery test** (P9) — does the cell resume moving when food returns?

---

## Reading progress

- Pages 1–52 of 409 read (front matter, Part I conversation, Part II talk 1 through "thought is the response of
  memory").
- Next: the rest of Part II talk 1 (the questions on observer and observed, fragmentation, resistance).
