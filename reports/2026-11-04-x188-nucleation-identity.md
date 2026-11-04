# X188 — nucleation as a count of bodies, on the X187 runs (04.11)

**Question.** X187 manipulated the colder body's inflow at two levels in two arms and reproduced X186's sign flip under selection
(+0.67 at radius 3 gap 10, −0.33 at radius 6 gap 9), but its registered mechanism readout turned out to be the outcome restated
(1 exactly when the pair fused, 0 exactly when it did not, 24 of 24 runs), so nucleation was left **untested**. This item asks the
same question with a readout that is not a function of the outcome. Preregistration
`reports/2026-11-04-x188-nucleation-identity-plan.md`, amended **before** any analysis: uids are re-issued at every division (the
two seeded bodies carry 1 and 2, the merge leaves 2, the next sample already shows 3 and 4), so identity cannot trace the pair and
the test counts bodies by **spatial continuation** instead.

**Result: the flip is not nucleation by continuation either.** At radius 6 gap 9 the warm level carries
**1.267** other bodies inside the 24-cell window per fixed sample against **1.033** for the cold level — a
difference of **+0.234**, below the registered bar of 0.5 — so the warm level coalesces less there without holding more bodies
around the pair. At radius 3 gap 10 the same manipulation moves the count **+0.842**, i.e. more, while it coalesces
more; the count and the outcome do not even move together across arms.

| arm | level | `F_local` | share | other bodies in window | field-wide |
|---|---|---:|---:|---:|---:|
| radius 3 gap 10 | cold | 0.0173 | 0 of 6 = 0.00 | 0.961 | 32.472 |
| radius 3 gap 10 | warm | 0.0300 | 4 of 6 = 0.67 | 1.803 | 33.581 |
| radius 6 gap 9 | cold | 0.0170 | 6 of 6 = 1.00 | 1.033 | 33.894 |
| radius 6 gap 9 | warm | 0.0300 | 4 of 6 = 0.67 | 1.267 | 37.105 |

**The readout is not a function of the outcome, and it is not discriminating at the binary level.** All
24 of the 24 runs have other bodies in the window at some fixed sample, so "positive" does not
predict "fused" and the X187 failure does not repeat; but a count that is positive nearly everywhere is weak evidence in either
direction, which is why the registered bars are differences of means and why the exploratory packet below is labelled as such.

**Exploratory, not registered: the contact window.** The fixed-sample average pools the one-component phase with the late phase in
which the field holds thirty bodies, so the interval 50-250 steps (around contact) is reported separately: other bodies in the
window read 0.0 (radius 6 cold) against 0.167 (radius 6 warm), and
0.087 against 0.643 at radius 3, with field-wide means of 1.36-1.57 bodies. If
anything the local signature of a warm site is stronger in the arm where the law keeps its sign.

**Limits.** The window is centred on the pair's current centre, so a nucleated body the pair carries along is counted while one
that drifts off is not; the two counts (window and field-wide) are both reported. Three-seed groups, integer counts of 0-3, and
a heavily time-dependent quantity: the bars are set at that scale and nothing is claimed below them.

**Next hypotheses.** The mechanism now has to be sought in the **field** rather than in component counting: whether a warm site
leaves a weaker bridge between the bodies at contact, which is X170's reading re-asked by local inflow and size
(`reports/2026-11-04-x189-bridge-plan.md`). Artifact: `morphogenesis/experiments/E09_pond/l1_field_x188_nucleation_identity.json`.
