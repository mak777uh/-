# Three levels, measured: policy, mediator, closure

<!-- report-format: observation -->
<!-- report-kind: audit -->

**What this is.** The work of 08.11 that turned our own rules into something a machine can check. It is an
audit report: it reads artifacts that already exist and reports what they say. It does not measure a new run of
the world, so it carries no `situation_explained`, no `record_explained` and no first 20 steps — those belong to
an experiment report, and requiring them here would have been a mistake the first version of the gate made.

**Why it was done.** The model is `herness`: a harness is a network of atomic cells, and three levels must not
be mixed — **A. policy** (provable), **B. mediator** (provable for small code), **C. closure** (only measured,
never proved). Our repository had all three **in prose**: `lab/autonomy-rules.json`, the wrapper `lab.py run`,
and the claim "nobody bypasses the wrapper". None of them was checked by anything but our own reading.

## 1. What we looked at

Three things that existed only as prose, and the question for each: **can a machine tell whether it holds?**

## 2. What we saw

### A. Policy — now proved (Lean)

`formal/Policy.lean`, 9 theorems, compiles clean:

| id | statement |
|---|---|
| F-POLICY-1 | forbid beats allow — an action in both lists is not allowed |
| F-POLICY-2 | forbid beats the owner's consent — a forbidden action cannot be done even with permission |
| F-POLICY-3 | allowed-without-asking does not require the owner |
| F-POLICY-4 | allowed-without-asking is not forbidden |
| F-POLICY-5 | an action in exactly one list has a definite decision |
| F-POLICY-6 | an empty policy allows nothing (negative control) |

Repository total after the addition: **8 files, 40 theorems, 0 errors** (`scripts/lean_check.py`).

### B. Mediator — three implementations agree

`scripts/policy_diff.py` compares three independent implementations on 7 cases that exercise every branch:

| implementation | what it is |
|---|---|
| Lean | `formal/Policy.lean`, the proved model |
| Python | the rule that runs today in `scripts/check_autonomy.py` |
| Rust | `mediator/`, a compiled crate with **no dependencies** |

**Result: 3 implementations available, 7 cases, 0 disagreements.** The two conflict cases (allowed+forbidden,
owner+forbidden) both return "forbidden" in all three.

The Rust mediator has 6 unit tests of its own, all passing.

### C. Closure — measured, not proved

`scripts/closure_probe.py` plants a defect and checks that the machinery catches it:

| probe | defect planted | result |
|---|---|---|
| P1 | an artifact with no `lab/runs` manifest | caught |
| P2 | a run claiming a foreign owner | caught |
| P3 | a commit staging `.pt` weights | caught |
| P4 | a protected path staged without a decision-log entry | caught |
| P5 | two items marked `running` in the queue | caught |

**5 probes, 5 caught, 0 holes.** Closure is measured, and the measurement is now a command rather than a claim.

### D. The corpus audit

`scripts/audit_corpus.py` read all 320 artifacts in `morphogenesis/experiments/E09_pond/` and split them by
whether they can answer "did this help the cell, in the cell's own terms":

| category | count | what it means |
|---|---|---|
| A. record the cell's own measures | **300** | the audit can answer the question |
| B. record only the ranking metric | **0** | — |
| C. record neither | 20 | nothing to audit |

**The split matters: category A CAN answer the question, category C CANNOT answer it.** **This corrects an earlier belief of mine.** I had assumed the corpus was built entirely on the favourable
share, which is a ranking and is blind to order. It is not: **300 of 320 artifacts record the cell's own
measures**. The ranking was our *headline*, not our only record.

## 3. What it means

**The three levels are now separated and each is checked by the means appropriate to it.** A and B are proved;
C is measured; and the boundary between them is written down rather than remembered.

**Six defects were found today, and five of them were mine, not the code's:**

| defect | found by |
|---|---|
| a proof that did not compile (`simp` could not see `contains`) | Lean |
| a proof that did not compile (`rewrite` could not find the pattern) | Lean |
| generated Lean with no space before `⟩` | Lean |
| `check_autonomy` never looked at the run's owner | probe P2 |
| probe P2 grepped output instead of planting a defect | my own review |
| the comparison put all 7 cases into one policy, so the mediator was right and the test was wrong | the disagreement itself |

**That is the value of the exercise, and it is not the theorems.** The theorems are short. What the machines did
was refuse to let me be wrong quietly.

## 4. What we do not know

1. **The closure is measured on 5 probes, not proved.** There may be bypasses we did not think to probe. The
   number 5 is a measure of our imagination, not of the system.
2. **The Rust mediator is not wired into the running harness.** It exists, it is tested, and it agrees with the
   proved model — but `lab.py run` still uses the Python rule. Wiring it in is a separate change with its own
   risk.
3. **The policy in Lean is a model, not the policy file.** `formal/Policy.lean` proves properties of *a* policy
   structure; it does not read `lab/autonomy-rules.json`. The link between the file and the model is manual.
4. **The corpus audit counted artifacts, not conclusions.** It says 300 artifacts *can* answer the question; it
   does not yet say what the answer is.
5. **The mediator has no timing or memory bounds proved.** Its closure is small because the code is small, not
   because anything was proved about its resources.

## 5. What this changes in the next experiment

**Nothing in the world experiment changes.** What changes is what must be true before one runs:

- a new experiment needs a **manifest** (`scripts/check_experiment_manifest.py`), and the manifest may not
  describe an addition while the moratorium holds;
- a new report is either an **experiment report** (three readouts, first 20 steps) or an **audit report** (count
  of artifacts, honest split), and the gate now distinguishes them;
- a change to the policy must keep **three implementations in agreement** (`scripts/policy_diff.py`);
- a claim about closure must be a **probe with a planted defect**, not a sentence.

**The concrete next step is the one the reading named and this work did not touch: one run, no mechanism, three
readouts, observation from outside.** The infrastructure to record it now exists; the run does not.
