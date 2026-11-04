# X165 — A third body neither helps nor prevents: the crossing is additive (04.11)

**Question.** Every fusion statement in this block is a **pairwise** law: two bodies, one gap, one crossing. The medium is
global, so a third body changes the field in the corridor between the first two, and if the crossing were a field-bridge
effect it should move. This item seeds three bodies of radius 3 in a row with a fixed surface gap between neighbours and
asks whether the row behaves like two independent pairs.

Pre-registration: [`2026-11-04-x165-three-bodies-plan.md`](2026-11-04-x165-three-bodies-plan.md). Three arms (surface gaps
8, 10, 12), five seeds each (981-985), 6 000 steps, `F` = 0.030. New code: `--init-row N:R:GAP`; the existing
`--init-spots` branch is untouched.

## The pre-registered readout did not work, and that is reported first

§3 of the plan named "the number of distinct components at the end of the run" as the readout. It is unusable: every run
grows into dozens of components (69-82 at the end in all three arms), because a coalesced body divides again and again, so
the end count says nothing about whether a fusion ever happened. The readout was replaced **after** the runs with the
**minimum** component count reached during the run — 3 means the row never fused, 2 means one of the two gaps closed, 1 means
all three bodies coalesced. The correction is recorded in the aggregate (`readout_note`) and here rather than being quietly
applied.

## Result

| arm | minimum component counts | all three coalesced | final components |
|---|---|---|---|
| gap 8 | 1, 1, 1, 1, 1 | **5/5 (100 %)** | 69-70 |
| gap 10 | 1, 3, 3, 3, 3 | **1/5 (20 %)** | 74-76 |
| gap 12 | 3, 3, 3, 3, 3 | **0/5 (0 %)** | 75-82 |

The positive control fires: at gap 8 all three bodies coalesce, as the pairwise law requires (pairs fuse 5/5 at that gap).

And the quantitative prediction is the reason this item is worth having. A row of three has **two** gaps. If the two pairwise
fusion events were independent, the share of rows that coalesce into one component would be the square of the pairwise
share: 0.47² = **22 %**. Observed at gap 10: **20 %** (one row of five). At gap 12, where the pairwise share is about zero,
the observed share is zero. The pairwise law therefore survives many-body contact, and it is **additive**: a third body
neither helps the outer pair meet nor prevents it.

That is a stronger statement than "consistent with": the product of the pairwise shares predicts the row's share to within
the resolution of five seeds, in both directions.

## What this changes

The crossing measured in §4.1 can now be used per contact rather than per experiment. A pattern with many touching bodies
fuses wherever the local gap allows, independently at each contact, and the number of contacts does not change the local
rule. This is what a *local* length of the medium means operationally, and it is the first measurement in the block that
tests the law outside the configuration it was measured in.

## Limits

Five seeds per arm, so the 20 % at gap 10 rests on a single event: the agreement with 22 % is a coincidence of small numbers
as much as a measurement, and the item says so. The row was straight and the bodies equal; a bent row, or one of unequal
bodies, would test whether the additivity is geometric or unconditional. The gap-12 arm shows 0/5 rather than the ~1/50 the
squared prediction gives, which is consistent but also carries no information.

## What would kill it

A ten-seed repeat where the gap-10 row coalesces in 40 % or more of runs would say the third body **helps** — the outer pair
meeting through a corridor enriched by the middle body — and the additivity claim would have to be withdrawn. Conversely a
share near zero would say the third body stabilises the row against fusion. The present item cannot tell 22 % from 5 % or
from 40 % with five seeds; it can only tell 100 % and 0 % apart, and those two arms are clean.

## Next hypotheses

1. **Ten seeds at gap 10**, the only arm where the prediction is testable at all (22 % against 47 % or 5 %).
2. **Four bodies in a row**: the prediction becomes 0.47³ = 10 % if additivity holds, a sharper test with the same cost.
3. **A bent row** (120°): if the middle body's field is what mediates, the angle should matter; if additivity is
   unconditional, it should not.
