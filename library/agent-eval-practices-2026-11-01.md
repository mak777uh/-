# How to evaluate an agent — what the literature and the harnesses actually give us (2026-11-01)

Collected for later use: the methods that are **checkable**, the numbers that come with them, the mechanisms the coding
harnesses enforce, and what this laboratory adopted immediately versus what is parked. Sources were read on 01.11.2026;
every claim carries a link.

## 1. The one idea worth more than the rest

Evaluation is a **three-part contract**, and a benchmark usually specifies only the first part:
`task validity` (the task can only be solved by the capability we claim to measure) + `outcome validity` (a positive score
really means the task was solved) + `reporting` (what must be published for the number to be checkable). The ABC checklist
turns that into ~30 binary items (T.1–T.10, O.*, R.1–R.13) and scores them 1/0 per item, averaged per section. Audited on ten
popular benchmarks: **7/10 fail task validity, 7/10 fail outcome validity, 10/10 have reporting gaps**
([2507.02825](https://arxiv.org/abs/2507.02825), [site](https://uiuc-kang-lab.github.io/agentic-benchmarks/)).
The sharpest defects are instructive rather than exotic: a **do-nothing agent scores 38 % on τ-bench**, an agent that
**overwrites the test cases inside SWE-Lancer's zipped test bundle reaches 100 %**, and fixing a single hidden scorer defect
moved one benchmark's success rate from **94.3 % to 65.5 %**.

## 2. Numbers worth remembering

| What | Number | Source |
|---|---|---|
| Ground-truth-error correction of a CI | `µ = e + (1−2e)p′`, `σ² = µ(1−µ)`, half-width `1.96σ/√N`; with `e = 11.65 %` a reported 74.9 % becomes 69.1 % [66.8, 71.4] | [2507.02825](https://arxiv.org/html/2507.02825v5) |
| pass@k / pass^k | `pass^k = E_task[C(c,k)/C(n,k)]`, `pass@k = 1 − E_task[C(n−c,k)/C(n,k)]` | [2406.12045](https://arxiv.org/pdf/2406.12045) |
| Reliability collapse with repeats | GPT-4o τ-retail **61 % pass^1 → under 25 % pass^8** | [2406.12045](https://arxiv.org/pdf/2406.12045) |
| Cost at equal accuracy | HumanEval: LATS(GPT-4) 88.0 % at **$134.50** vs GPT-4 zero-shot 89.6 % at **$1.93**; ≈2 orders of magnitude | [2407.01502](https://arxiv.org/html/2407.01502v1) |
| Reproducibility of reported numbers | re-runs moved several published accuracies by 3–15 points (e.g. 94.4 → 88.0) | [2407.01502](https://arxiv.org/html/2407.01502v1) |
| Minefield annihilation | final score `= score(mitestones) × I(no minefield violated)`; a violated must-not event zeroes the whole trajectory | [2408.04682](https://arxiv.org/pdf/2408.04682) |
| Judge as a gate | a judge that always says "correct" has **κ = 0.00** while agreeing with humans 80 % of the time | [AWS Grounded Evals, via 2507.03825-adjacent literature](https://arxiv.org/abs/2507.02825) |
| Harness minimalism | mini-SWE-agent (100 lines, **829** system-prompt tokens) matches Claude Code (16 581 tokens) within 5 points at **3× lower cost** | [Shandong University study, reported 23.10.2026](https://venturebeat.com/ai/) |
| Trajectory judging | Agent-as-a-Judge agrees with human consensus **90 %** vs **70 %** for LLM-as-a-Judge on DevAI (55 tasks, 365 requirements) | [2410.10934](https://arxiv.org/pdf/2410.10934) |
| Reliability profile | 12 metrics in consistency / robustness / predictability / safety; K = 5 runs, J = 5 paraphrases, fault injection p = 0.2 | [2602.16666](https://arxiv.org/abs/2602.16666) |

## 3. What this laboratory adopted immediately (01.11)

1. **UNKNOWN is not success.** `scripts/claim_comparator.py` used to return "passed" for a claim whose check kind was not
   implemented, and the gate runs with `--ci` — so an unimplemented check was green. It now reports `unknown` and fails under
   `--ci`. This is the third state the reliability and audit literature insists on (`PASS / FAIL / UNKNOWN`, with UNKNOWN
   never counted as a pass).
2. **A positive control must be a number, not a tick.** `scripts/check_design.py --scan-plans` required the five section
   headings and five `[x]` marks, so "positive control fires" could be a checkbox with no value. From 2026-11-02 the section
   must carry a value and a threshold ("fires if …"). Plans written earlier are **not** rewritten — editing a preregistration
   after the data is exactly the failure the rule exists to prevent — and are grandfathered explicitly.
3. **Claims carry the value they must produce** (`X3`, same day): `check.expect` with a tolerance turns the comparator from a
   reporter into a gate; a planted wrong expectation fails with exit 1.

## 4. Parked, with the reason

| Practice | Why parked | What would unblock it |
|---|---|---|
| Minefield annihilation of invalid runs | the field line has no `nan`/`collapse` runs in the current series; the rule would be untested code | first aggregate that contains an `invalid_reason` — apply `score × I(no invalid run)` there and report both numbers |
| Oracle + trivial-agent row per experiment family | costs a run per family and the field line's "trivial" is not obvious (a uniform field is a legitimate state) | one family at a time, starting with the pond line where a do-nothing policy exists |
| Ground-truth-error-corrected CI | needs `e`, an audited annotation-error rate; we have no annotation layer | applies to the transplant matrices, where class labels are the ground truth and can be re-checked by hand |
| Cost per verified result | cost exists (`wall_time_sec`, GPU-hours), the rollup does not | sum `wall_time_sec` over the arms named in a claim's evidence; one number per claim |
| Holdout/tuning split in registrations | only E02b ever had a real split | add a `split:` block to the template and fail when slices intersect |
| Reliability profile (4 axes) | our repeats are seeds, not stochastic runs; consistency is already gated by `check_seed_replication.py` | a four-field block in the series aggregate: consistency, robustness, predictability, safety |
| LLM-as-judge | no LLM in the loop, and the literature's own numbers (κ = 0.00 for an always-pass judge) argue against using one where a test exists | nothing; deliberately not adopted |

## 5. What the coding harnesses enforce that a lab does not

The eight harnesses surveyed (Claude Code, Factory droids, pi, openclaude, Cline, SEAL, auggie, Cursor) converge on four
mechanisms that are **enforcement**, not advice:

1. **Per-event hooks with a blocking contract.** Claude Code documents ~33 events and, crucially, *which* of them can block
   (`PreToolUse`, `Stop`, `TaskCreated`, `PreCompact`, `WorktreeCreate` can; `PostToolUse`, `SessionStart`, `SessionEnd`
   cannot). A gate that cannot block is a log line
   ([hooks](https://code.claude.com/docs/en/hooks.md)).
2. **Machine-tested permission rules.** Factory ships each rule with `tests.match` / `tests.noMatch` fixtures that the
   validator executes, so the guard itself is regression-tested
   ([permission-rules](https://docs.factory.com/autonomy-and-safety/permission-rules.md)). This is the pattern our
   `check_autonomy.py` should grow: today it has a negative control by hand, not fixtures in CI.
3. **Gate policy profiles with conservative aggregation.** SEAL's `pass | fail | warn | blocked | unknown`, overall = the most
   conservative of the row statuses, and **every non-pass must cite the artifact that caused it**
   ([gate-policy](https://github.com/ajhcs/SEAL/blob/main/plugin/docs/gate-policy.md)). Our `verify` is a flat list; a
   profile would let "explore" and "before publication" differ honestly.
4. **Session transcripts as provenance.** pi stores sessions as an append-only tree (`id`/`parentId`), so branching never
   rewrites history ([session-format](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/session-format.md));
   Claude Code keeps one plaintext `.jsonl` per session plus `file-history/`
   ([sessions](https://code.claude.com/docs/en/sessions.md)). Our analogue — `lab/runs/*.json`, `reports/`, git history — is
   good for runs and weak for *decisions*: why a queue item was closed, what was tried and rejected.

Two honourable mentions worth stealing cheaply: a **`Stop` hook that refuses to end until the report and manifest exist**,
and a **review-guidance file** (`REVIEW.md`) so a reviewer checks this lab's invariants rather than generic style.

## 6. What this changes about how we work

- The lab's own audit (same day) found that **every** practice above already exists in some form, except that two of them
  let a weak result pass green — both are now closed (§3).
- The remaining gap is not knowledge but **fields**: `pass^k` next to `sign_agreement_k`, a `null` arm, a `split` block, a
  cost rollup, a four-field reliability block. Each is a small edit to an existing aggregate and a line in the template.
- The literature's most transferable single sentence for us: **"a benchmark is a measurement, and the measurement needs its
  own control"** — which is exactly the lesson of `X72` (the proxy that measured packing density instead of wavelength) and
  of `X29` (a selection differential of +0.148 where the trait cannot act).

## 7. Queue for reading (not yet read in full)

- `2507.02825` — read in full (checklist, formulas).
- `2407.01502` — read in full (Pareto, audit numbers).
- `2406.12045` — read in full (pass^k definitions, costs).
- `2602.16666` — abstract + metric table; the 12 formulas are extracted above, full text to read.
- `2408.04682` — abstract + score formula; the milestone DAG construction deserves a full read before we copy it.
- `2507.05257` — abstract + competency table; only if we ever build a memory axis.
- Harness docs — read; the four mechanisms in §5 are the extract.
