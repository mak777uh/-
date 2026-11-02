# X117 — void by interpretation: matching on the exposure cannot test whether the exposure matters

**Plan:** [`2026-11-03-x117-area-matched-plan.md`](2026-11-03-x117-area-matched-plan.md) (01:42).
**Aggregate:** `l1_field_x117_area_matched.json`.

## What the numbers did

| cell | equal-daughters subset (X116) | matched on daughters **and** area (±10 %) | 95 % CI | only larger / only smaller | pairs |
|---|---|---|---|---|---|
| 0.030 | 633, **+0.125** | 217, **+0.018** | [−0.018, 0.055] | 10 / 6 | 217 |
| 0.040 | 631, **+0.044** | 222, **0.000** | [−0.014, 0.014] | 1 / 1 | 222 |

Both controls fired: the equal-daughters contrast reproduces X116 within 5 %, and the mean area ratio was 1.57 / 4.87 before matching against ≤ 1.10 after. The
registered rule then fired: **"the survival advantage is fully arithmetic"** — both intervals contain zero.

## Why that verdict is not usable

**Area is the treatment, not a confound.** "The larger sister" *means* the sister with the larger area. Matching pairs on area compares sisters of equal
size, and by construction there is no size difference left to have an effect. That is conditioning on the exposure, and it can only produce a null.

The distinction that matters:

- X116 matched on the **number of daughters**, which is a *mediator* — a plausible mechanism through which size could act, and removing it is a real test.
  The advantage halved, which is informative.
- X117 matched on **area**, which is the *exposure itself*. Removing it cannot test whether size matters; it removes the question.

So the correct reading of X117 is narrow and does not contradict X115/X116: **the survival advantage is carried entirely by the size difference itself — there is
no part of it that survives holding size equal**, which is a tautology dressed as a result. The residual X116 found (0.125 in the lattice) was the remaining
size gap, not a size-independent lineage effect.

The honest state of the consequence claim is therefore exactly where X116 left it:
> the larger sister's line is alive at the end more often; about half of that is the number of daughters it has; the rest is the remaining size difference,
> and no measurement here separates those two.

## The design error, stated for the record

The plan's own control — "the area ratio must be at least 1.25 before matching and at most 1.10 after" — verifies that the matching worked, and that is
precisely the problem: a successful match on the treatment guarantees the null. The registration should have asked whether area **is** a confound (it is
not) rather than assuming that removing another difference is always an improvement.

**Rule earned:** a matched design states, for each variable it matches on, whether that variable is a **confounder** (associated with both exposure and
outcome, not on the causal path) or a **mediator** (on the path). Matching on a confounder tests the effect; matching on a mediator measures the share it
carries; matching on the **exposure** deletes the effect by construction and cannot be reported as a null.

## What would actually test the remaining question

Two designs, both registered as candidates and neither run:

1. **Exposure kept, mediator varied:** among pairs with the *same area*, compare survival between branches with more and fewer daughters. This asks whether
   branch count matters *independently of size* — the mirror image of X116, and the one that separates "more daughters" from "bigger".
2. **Different mediator:** match on the number of **cells at birth** (which is not the peak area) rather than on peak area, so the exposure's timing is
   controlled without controlling the exposure.

## Caveats

- The matched subsets are ~220 pairs per cell (of 633/631 at the daughters-only stage), so even a correct test at this depth would have resolution ≈ 0.07.
- Both controls passed; the void is interpretive, not statistical — a distinction the line should keep sharp, because a fired rule is not a licence to
  publish the sentence the rule was written for.
- One seed set, one box, one grid, the 0.20 cut.

доска: принято 0, отклонено 0, отложено 0.
