# X139 void — the "annihilation" was a distance tolerance in the analyser, and there is no third fate

**Found** 03.11 16:00, while checking the 11-cell arm of X139 against the neighbouring arms before reading X142's
first results. **Corrected:** X139's report, its claim, §10hf, the world-design table and the reports index. **What
survives:** the merge-time curve and the mixing length, under a different name.

## What was claimed

X139 reported that at a five-cell surface gap (radius 3, separation 11) the two seeded lineages do not merge and do
not coexist: in 5/5 seeds both end with **no descendants at all** while the world stays alive. That was published as
a **third fate — annihilation** — and entered the block as the inner edge of the mixing length, with X142 registered
to map the band.

## What the logs actually show

Read at the merge step, the two arms that were given different names are the same event:

| separation | gap | last step with uid 1 and uid 2 | components then | next logged step | old class | what it is |
|---|---|---|---|---|---|---|
| 10 | 4 | 10 | 2 — `(1, 61, 52, 54)` and `(2, 61, 62, 54)` | 20: **one** component, uid **3**, area 165 | "absorbed 5/5" | two discs became one body |
| 11 | 5 | 10 | 2 — `(1, 52, 51.5, 54)` and `(2, 52, 62.5, 54)` | 20: **one** component, uid **3**, area 151 | "**annihilated** 5/5" | two discs became one body |

In both arms the two seeded uids disappear on the **same** logged step, the next step holds a single component
carrying about the sum of both areas, and that component is a **new uid** (uid 3, from which every later uid
descends; neither seed ever has a daughter). The field does the same thing at separation 10 and at separation 11.
Nothing in the world distinguishes them.

## Why the readout distinguished them

`x139_analyse.py` counted a lineage as lost "by absorption" only if, at the step the dead uid ended, the partner's
last position was within `r_dead + r_other + 2` cells:

- separation 10: radii `sqrt(61/π) = 4.41` each, threshold **10.81**, centre distance **10** → "absorbed";
- separation 11: radii `sqrt(52/π) = 4.07` each, threshold **10.14**, centre distance **11** → "not absorbed".

Everything else was "unresolved", and that class was published as annihilation. The label was decided by whether one
comparison fell on either side of a **2-cell tolerance**, and the tolerance sat almost exactly where a one-cell change
in the manipulation moved the quantity being tested. The old readout also reported the **first** death of the pair:
at separation 14 the first uid dies at step 39 and is called "absorbed", but the second dies ten steps later and the
body is again a new uid. "Absorption" was therefore never a statement that one lineage swallowed the other — it was a
statement that one lineage ended first.

## What is true instead

The three fates, defined without a tolerance (unit: the arm, denominator: its usable seeds):

- **M — mutual coalescence.** Neither seeded uid ever has a daughter and both subtrees are gone at the last step. The
  discs became one body before either could grow a lineage.
- **A — absorption.** Exactly one seeded subtree is alive at the last step.
- **P — persistence.** Both seeded subtrees are alive at the last step.

Under these definitions the radius-3 curve reads:

| gap | 1 | 2 | 3 | 4 | 5 | 7 | 8 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|
| class | M 5/5 | M 5/5 | M 5/5 | M 5/5 | **M 5/5** | M 5/5 | M 5/5 | M 2/5, A 2/5, P 1/5 | M 2/5, P 3/5 |
| first logged step with neither seed | 10 | 10 | 10 | 20 | **20** | 40 | 50 | 80-170 | 100-170 |

Gap 5 is not a hole: it is the same mutual coalescence as gaps 1–8, at the same ten-step quantum as gap 4. The
transition to "the pair survives as two lineages" still sits between gaps 9 and 10 (separation 15 and 16), so the
**mixing length of 16 ± 1 cells stands** — as the separation at which two seeded structures stop coalescing within
the horizon, not as the separation at which one absorbs the other.

## What this retracts and what it keeps

- **Retracted:** the "third fate" of annihilation; the claim that at five cells the pair is destroyed rather than
  merged; the reading of the inner edge as a destruction band; the registered outcomes of X142 that described a band.
- **Kept, renamed:** the merge-time curve (1, 1, 10, 10, 19, 40, 50, 79 steps at gaps 1–10 — monotone once gap 5 is
  measured instead of labelled); the mixing length and its gap rule (`2R + 9`); the slowdown towards the crossing.
- **Weakened:** every statement of the form "one seeded lineage takes the other in". The readout cannot make it: the
  merged body is a new uid, so what it observes is the end of a lineage, not its transfer into another.

X142 continues with the corrected readout; its arms are unchanged, and its measured quantity is now **how far out
mutual coalescence reaches** — at radius 3 up to at least gap 8, with gaps 6 and 9 being re-run because X136's full
logs for those separations were retired before the compact projections existed.

## The rule this adds

`docs/design-checks.md`: **a classification threshold may not be compared against the manipulation itself.** If a
class is decided by a distance tolerance and the sweep moves that distance by one cell per point, the tolerance will
eventually decide the labels — here it produced a "third fate" that was one comparison away from the label of the
neighbouring arm. Before a class boundary is published, the margin between the measured quantity and the threshold
must be shown to be larger than the step of the sweep, and the class must be defined so that it does not depend on a
tolerance at all.

## Files

`reports/2026-11-03-x139-slowing.md` (correction appended), `manuscript/CLAIMS.md` (§10hf claim replaced),
`docs/plan/10d-field-metrics-and-form.md` §10hf, `docs/world-design.md`, `reports/README.md`,
`scripts/x142_analyse.py` (the corrected readout), `lab/queue.json` (X139 and X142 notes).

доска: принято 0, отклонено 0, отложено 0.
