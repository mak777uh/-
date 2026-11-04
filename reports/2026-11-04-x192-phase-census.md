# X192 — the phase census at the largest size (04.11)

**Question.** X191's five-level sweep passed one of three criteria and the reason turned out to be structural: the local inflow of a
pair is a function of the **phase** (position modulo the pattern's 12-cell period), and the phase map is finite. Enumerating it gives
144 classes whose `F_local` takes only nine values, up to 26 classes to a value — so "five sites per level" was always five draws from
a class of up to 26, and a step in `F_local` is nine steps wide. This item replaces the sample with **the population**: one world per
phase class, 144 runs at radius 6 gap 9, one seed each, same readout (contact-moment bridge ratio). Preregistration
`reports/2026-11-04-x192-phase-census-plan.md`.

**Result: the bridge depends on the phase at fixed inflow, and the outcome follows it there — the strongest form this line has for
the mechanism.**

| `F_local` | classes | contact ratio range | spread | fusion share |
|---|---:|---|---:|---:|
| 0.015 | 8 | 0.18418–0.49182 | 0.30764 | 1.0 |
| 0.01701 | 16 | 0.19247–0.47313 | 0.28066 | 1.0 |
| 0.0225 | 26 | 0.00555–0.45354 | 0.44799 | 0.3846 |
| 0.0235 | 20 | 0.00598–0.01612 | 0.01014 | 0.2 |
| 0.02625 | 20 | 0.01069–0.48223 | 0.47154 | 0.2 |
| 0.03 | 24 | 0.00726–0.39916 | 0.3919 | 0.5 |
| 0.03375 | 12 | 0.04216–0.06174 | 0.01958 | 0.3333 |
| 0.0365 | 12 | 0.01397–0.03278 | 0.01881 | 0.0 |
| 0.0375 | 6 | 0.00287–0.01008 | 0.00721 | 0.0 |

Registered criteria, one at a time:
1. **the ratio depends on the phase at fixed inflow — PASSES decisively.** At `F_local` = 0.0225, the most crowded value with
   26 classes, the ratio spans **0.00555–0.45354**
   (spread **0.44799**, bar 0.05). Nine of the nine values show a spread, four of them above 0.28.
2. **the ratio falls with the inflow — FAILS over classes, PASSES over the value means.** Spearman **-0.378** over the 144 classes
   (bar −0.5) but **-0.833** over the nine value means: within one value the phase adds more scatter than the step between values,
   so the trend lives in the means.
3. **the outcome follows the bridge at fixed inflow — PASSES, and this is the item's point.** At `F_local` = 0.0225 the
   worlds above that value's median ratio fuse **1.0** of the time against **0.1111** below
   (difference **0.8889**, bar 0.3, Fisher p < 0.001): with the inflow held fixed, the bridge alone separates the
   outcomes.
4. **the outcome falls with the inflow — PASSES**: fusion share 1.0 at `F_local` = 0.015 against
   0.0 at 0.0375.

Over all 144 worlds the logistic slope of fusion on the ratio is **6.094** (se 1.058, z = 5.76), so the
bridge is not a correlate of the outcome but a strong predictor of it: one unit of bridge ratio (the whole measured range) moves the
log-odds by about six.

**What this changes about the law.** The local-inflow law, as X183-X186 measured it, is a statement about the **mean over phases**: at
one inflow value the phase moves the bridge by up to 0.45 and the fusion share from 0 to 1. So the law's boundary condition is not
"a stronger inflow fuses less" but "a *thinner bridge* fuses less, and the inflow sets the bridge only on average". That also explains
X186's radius-6 exceptions and X187's weak radius-6 Fisher p in one stroke: cells and seed groups pool phases, and pooling averages
away the variable that actually decides.

**Limits.** The census is per phase class with one representative world each: X190's zero within-site spread and X191's zero
within-phase spread are the evidence that a class is one world, and both are reported beside this census; a class with two different
worlds would break the unit. Nine values with unequal class counts make the class-level Spearman weight the crowded values, which is
why both correlations are reported. The census is one arm (radius 6 gap 9); nothing here says the smaller bodies behave the same, and
X190 found the opposite sign at radius 3. And a fusion share at one `F_local` is measured across its classes, not across time: the
outcome remains a transient coalescence.

**Next hypotheses.** (1) The same census at radius 3 gap 10 — if the phase decides there too with the opposite sign, the law has one
mechanism with a size-dependent sign rather than two laws. (2) Re-express X183's 139-run AUC, X186's per-cell slopes and X187's
radius-6 Fisher p over **phase classes** rather than runs: if their scatter is phase pooling, the published numbers change and their
intervals were too narrow. (3) A census with two seeds per class, to price the class unit directly rather than infer it.
Artifact: `morphogenesis/experiments/E09_pond/l1_field_x192_phase_census.json`.
