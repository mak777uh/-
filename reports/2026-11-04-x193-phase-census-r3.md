# X193 — the phase census at the smaller bodies (04.11)

**Question.** X192 censused the 144 phase classes at radius 6 gap 9 and found the mechanism's sharpest form: at one inflow value the
bridge ratio spans 0.006-0.454, the worlds above that value's median ratio fuse 1.0 against 0.111 below, and the logistic slope of
fusion on the ratio is 6.094 (z 5.76). This item runs the same census at **radius 3 gap 10** and asks whether the phase decides there
too and whether the sign of the inflow-outcome relation is reversed, as X190 found at this arm (0 of 5 cold sites fused against 3 of
5 warm). Preregistration `reports/2026-11-04-x193-phase-census-r3-plan.md`.

**Result: all four registered criteria pass — the mechanism is the same and its sign is set by size.**

| `F_local` | classes | contact ratio range | spread | fusion share |
|---|---:|---|---:|---:|
| 0.015 | 4 | 0.22319–0.22319 | 0.0 | 0.0 |
| 0.01701 | 16 | 0.17353–0.28508 | 0.11155 | 0.0 |
| 0.01875 | 16 | 0.1874–0.28555 | 0.09815 | 0.0 |
| 0.0225 | 14 | 4e-05–0.37535 | 0.37531 | 0.2857 |
| 0.0235 | 28 | 5e-05–0.33132 | 0.33127 | 0.2857 |
| 0.02625 | 12 | 0.00187–0.33536 | 0.33349 | 0.3333 |
| 0.03 | 44 | 0.00289–0.40363 | 0.40074 | 0.7273 |
| 0.03375 | 4 | 0.04603–0.04603 | 0.0 | 1.0 |
| 0.0365 | 4 | 0.41933–0.41933 | 0.0 | 1.0 |
| 0.0375 | 2 | 0.40028–0.40028 | 0.0 | 1.0 |

1. **the ratio depends on the phase at fixed inflow — PASSES.** At `F_local` = 0.03, the most crowded value with
   44 classes, the ratio spans 0.00289–0.40363, a spread of **0.40074** against a bar of 0.05.
2. **the outcome follows the bridge at fixed inflow — PASSES.** Worlds above that value's median ratio fuse **0.5** more
   often than those below (Fisher p = **0.0001**, bar 0.3): with the inflow held fixed, the bridge separates the outcomes at
   the smaller bodies too.
3. **the sign of the inflow relation is reversed — PASSES.** The fusion share rises from **0.0** at `F_local` = 0.015 to
   **1.0** at 0.0375 (Spearman **0.413** over classes and **0.515** over the nine value means, against −0.378 and
   −0.833 at radius 6). X192's monotone-decrease criterion therefore does not apply at this arm and is not counted; the reversal was
   registered in its place.
4. **the logistic slope of fusion on the ratio is positive — PASSES**, **4.854** (se 1.792, z = **2.71**) over all
   144 worlds.

**What this settles.** The line has one mechanism, not two laws with opposite signs. In both censuses the bridge at fixed inflow decides
the outcome, and the inflow's own sign follows from how the bridge moves with the body size: at radius 3 a stronger inflow leaves a
**thicker** bridge between the small bodies and they fuse (**1.0** of the top value against **0.0** at the bottom), while
at radius 6 the same stronger inflow thins the bridge between the large ones and they separate again. X190's two-population reversal
(0/5 against 3/5 at the site level) is the sample version of the same table. That is also why X186's radius-6 exceptions and X187's
weak radius-6 Fisher p read weak: those pools average over phases.

**Limits.** One arm, one representative world per phase class; the class unit rests on X190's zero within-site spread and X191's zero
within-phase spread, and X194 tested the unit on the observational pool rather than here. The smaller-body census has 44 classes at its
most crowded value, so its within-value contrast is better powered than radius 6's 26, and its bottom values carry only 2-4 classes
each — the reversal's low end is the thin end of the table. The outcome remains a transient coalescence.

**Next hypotheses.** (1) The mechanism's sign as a function of size: run the census at two intermediate radii (4 and 5, gaps chosen to
keep the same nominal inflow band) to find where the sign flips, which is a real prediction of the bridge account and not of a
level-based law. (2) Re-read X186's per-cell slopes over phase classes at radius 6, where this census says the pooling hides the
variable. (3) A two-seed-per-class census at radius 3 (44 of 144 classes at one value) to price the class unit where the contrast is
strongest. Artifact: `morphogenesis/experiments/E09_pond/l1_field_x193_phase_census_r3.json`.
