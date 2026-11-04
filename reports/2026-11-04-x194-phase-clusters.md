# X194 — how many worlds do the published pools contain? (04.11)

**Question.** X192 showed the phase decides the bridge at fixed inflow, and X190/X191 that seeds within a site and sites within a phase
are clones. Every pooled statistic of the line was computed over runs, and a run count is an upper bound on the number of independent
worlds. This item counts them in the observational pool — the ladder and its siblings, with every `x18*`/`x19*` pool excluded because
those were selected by the inflow or by the phase — and compares the same statistic bootstrapped over runs and over worlds.
Preregistration `reports/2026-11-04-x194-phase-clusters-plan.md`.

**Result: the refusal fired — the natural pools are nearly all singletons, and the published intervals do not need widening.**

| quantity | value |
|---|---|
| runs in the observational pool | 757 |
| worlds (position × arm: radius bin, gap, `F`, steps) | **633** |
| distinct positions alone | 227 |
| largest world | 5 runs |
| singleton worlds | 549 |
| worlds whose runs disagree in outcome | 2 |
| pooled AUC, local inflow → fusion, over runs | 0.65169 |
| the same over homogeneous worlds | 0.65962 |
| bootstrap 95% interval, resampling runs | 0.611–0.6931 (sd 0.0207) |
| bootstrap 95% interval, resampling worlds | 0.617–0.7015 (sd 0.0219) |

Registered predictions: one passed and two failed. The pool is **not** mostly singletons-by-run in the way X192's mechanism would
suggest — 633 worlds for 757 runs is 0.84 of the runs, far above the registered third
(failed); 84 worlds do hold more than one run (passed); and resampling worlds widens the interval by only
**1.06×** against a registered 1.3× (failed). The fourth registered prediction had no like-for-like comparator and is recorded as not
testable rather than as a failure: the line's 0.982 AUC was measured on a purpose-built arm, not on this pool.

**What this means, including for X192's own next step.** The worry that the published observational numbers were carried by a handful
of worlds is **unfounded**: the clones live in the arms that were laid out on purpose, where the same site or phase was repeated by
design. Holding the arm fixed, X187's four groups fall from 6 runs to 5 or 4 worlds each, and its Fisher p moves only from
0.0606 to 0.0606 at radius 3 and from
0.2273 to 0.2778 at radius 6 (these are this item's own groups and
outcome definition, not a re-computation of X187's published tests, and they are labelled as such in the aggregate). So X192's
hypothesis that the published numbers needed re-expression over phases is withdrawn for the observational pool and stands only for the
selected arms.

**Limits.** The pools differ in `F`, steps and geometry, so a "world" groups runs that are not replications of one another; the counts
are reported per arm as well as pooled, and the pooled figure describes the pool, not one experiment. Two worlds out of
633 still disagree in outcome, so the arm-held world is a good but not perfect unit — the price of the class unit, stated
rather than hidden. And a selected arm legitimately counts runs by design; nothing here corrects X183-X187's own denominators.
Artifact: `morphogenesis/experiments/E09_pond/l1_field_x194_phase_clusters.json`.
