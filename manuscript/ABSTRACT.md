# Abstract — Project Morphogenesis (draft for arXiv / grant applications)

**Working title.** Conditions, not shapes: what keeps an organisation maintaining itself.

## The question

Most work on morphogenesis and artificial life asks what pattern appears. We ask a different question:
**under what conditions does an organisation keep itself alive at all?** A living system here is a
process, not a form: maintaining a boundary costs energy, an error ends the trajectory, and luck is
passed to the next generation. The centre of the work is therefore the environment and its parameters,
not the pattern it produces.

## Method

The project is a computational bench with three instruments: CPU (texts, tests, statistics), GPU
(training and censuses), and **Lean** (proofs about our own definitions and invariants). The third
instrument is governed by explicit rules so that it does not become decoration: every formal hypothesis
has an identifier (`F-<area>-<n>`), a formulation written **before** the check together with "what would
refute it", a link to the code it protects, and a Python analogue that tests the same property on
concrete numbers — or an explicit statement of why no such test exists.

Claims are governed by a **claims matrix** (`manuscript/CLAIMS.md`): no row, no claim. Each row carries a
status (confirmed / refuted / open / forbidden), a closed report or artifact as evidence, and the
**maximum wording** that may enter the manuscript. A stronger wording counts as an error even if it
"sounds more scientific". Results are never rewritten silently: a changed result adds a new row with a
date and a link.

## What has been established so far

The project records five turns rather than hiding them: **goal** (the ring did not become an attractor),
**map** (a census of what the system generates on its own), **replication** (the class does not reproduce
on new seeds), **phase** (the class depends on the training horizon), and **environment** (we look for the
conditions of self-maintenance rather than for a shape). The morphology line was stopped on 23.10.2026
after yielding three transferable lessons — the class is a phase of a trajectory, the model has a
measurable signature, a shape is held by the price of maintaining it — and this closure is documented, not
erased, because in that world there was no metabolism and therefore nothing to test "life" with.

## Formal fragment

Seven Lean files model budget, order, closure, ignition, survival, territory and adaptation. The
strongest proved statements are of the form "the accounting invariant holds on any sequence of steps"
(induction over the step relation), which is exactly the kind of claim a simulation cannot establish.
The CI step is honest: if Lean is not installed, that is a **skip**, not a proof.

## What this paper does not claim

- It does not claim that the system is alive, or that the model reproduces biology.
- It does not claim generality beyond the measured seed sets and horizons; each claim row states its
  boundary explicitly.
- The three open experiments are reported as open, not as suggestive evidence.

## Why it may be worth funding or publishing

Because the discipline is the contribution: a claims matrix with a maximum admissible wording, formal
hypotheses with a falsification clause fixed in advance, and a lab record that keeps failures. Reusable
by anyone who runs computational experiments and wants to know which sentences their data actually
licence.

## Artifacts

- claims matrix: `manuscript/CLAIMS.md`; changelog of result changes: `manuscript/CHANGELOG.md`
- formal method rules: `docs/formal-method.md`; models: `formal/*.lean`
- lab state: `lab/` (`cycle.json`, `insights.json`, `lit-queue.json`, `formal.json`)
- path of the five turns: `docs/path.md`, reports under `reports/`
