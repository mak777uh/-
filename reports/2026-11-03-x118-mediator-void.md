# X118 — void by design: near-equal-area sisters with different daughter counts barely exist

**Plan:** [`2026-11-03-x118-mediator-plan.md`](2026-11-03-x118-mediator-plan.md) (01:46).
**Aggregate:** `l1_field_x118_mediator.json`.

## What happened

The design keeps the exposure fixed (sisters within ±10 %, widened to ±15 %) and varies the mediator (different numbers of daughters). The subset came back at
**22 pairs** in the lattice and **17** in the maze, with mean area ratios of 0.919 and 0.906 — outside the registered [0.95, 1.05] band even after widening.

Registered rule fired: **void** (fewer than 120 pairs, area ratio outside the band). No verdict is reported.

## Why this is structural, not bad luck

The two conditions of the subset fight each other:

1. **Sisters resemble each other in size** — that is the heredity this line has measured all day (ρ₁ ≈ 0.5). Near-equal-area sisters are therefore the
   exception, not the rule: a ±10 % window on a distribution whose sister correlation is 0.5 leaves a small tail.
2. **Among near-equal-area sisters, the daughter counts must differ** — and daughter count is itself correlated with area (bigger structures have more
   cells that can divide; X97/X116), so the same tail is further thinned.

The intersection is empty in practice. Matching cannot separate two quantities that the population ties together: the design asked for cells that the medium
does not produce in quantity. That is worth recording as a property of the medium — **size and daughter count are not separable by matching inside sister
pairs** — and not as a failed attempt.

## What it rules out

- The matched-pair route to "does the mediator matter at fixed size" is closed at this sample size. Any future attempt needs either many more worlds (a run)
  or a different design.
- The numbers that *did* come out (3:0 in the lattice, 1:1 in the maze) are too few to read and are not reported as evidence in either direction.

## The design that can answer it

A **model-based** separation instead of a match: pool all uids and fit `P(alive at the end) ~ log(area) + daughters`, with a bootstrap over worlds for the
intervals. Matching asks for cells where the two predictors are independent; a regression uses the whole cloud and estimates each coefficient with the other
held fixed statistically. Registered as X119.

## Caveats

- The void is about the **subset**, not about the question: nothing here says the mediator is irrelevant.
- The area ratio of the few surviving pairs (0.92 / 0.91) is itself informative: even the closest sister pairs are ~8 % apart, which sets the resolution a
  matching design could ever reach on these data.
- One seed set, one box, the 0.20 cut.

доска: принято 0, отклонено 0, отложено 0.
