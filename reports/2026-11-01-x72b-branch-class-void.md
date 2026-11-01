# X72b: the readout works, the branch is not a per-structure class — second void, sharper

**Date:** 2026-11-01, 19:55 MSK. **Experiment:** X72b (branch heredity at the X71 boundary, five new worlds).
**Preregistration:** `reports/2026-11-01-x72b-branch-heredity-plan.md`.
**Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x72b_branch.json`; fields `_x72b_fields/` (600 files, not committed).

## What was run

Five worlds at `F = 0.035`, `k = 0.06`, `--init-jitter`, 6000 steps, with the **field saved every 50 steps** (121 snapshots per
world) and components logged at the same cadence. Each structure's branch was read from a 48-cell window spectrum (primary,
as registered) and a 64-cell window (robustness), split at 10.4 cells.

## The instrument now passes

This is the part X72 got wrong and this series got right. The local measure tracks the global one: correlation between the
median local wavelength and the global peak position **0.90–0.99** in all five worlds, local spread ~15 cells, and the
control is marked usable in 5/5. Whatever else is true, the branch readout is no longer measuring packing density.

## What the numbers say

| world | events | share of "wide" parents | parent concordance | surrogate concordance | difference |
|---|---|---|---|---|---|
| s171 | 144 | 0.76 | 0.97 | 0.95 | +0.02 |
| s172 | 189 | 0.90 | 0.90 | 0.90 | 0.00 |
| s173 | 167 | 0.85 | 0.92 | 0.91 | +0.01 |
| s174 | 162 | 1.00 | 1.00 | 1.00 | 0.00 |
| s175 | 175 | 0.97 | 0.96 | 0.95 | +0.01 |

Both the parent and the surrogate sit at the **ceiling**, and both are ~equal. That is not inheritance and not its absence:
in four of five worlds **85–100 % of classified events are on one branch**, so "does the daughter match her parent" is
answered by the world's own tendency before any parent is consulted. The registered refusal rule fires — one class > 75 % —
and the verdict is **void**.

With the 64-cell window the same thing happens more strongly (share wide 1.00 in every world, concordance 0.99).

## What this actually teaches

X71 reported two modes with ≥ 20 % of spectral power each in every run of the `F = 0.035` cell, and X72b reports 85–100 % of
local windows peaking on the wide branch. Both are true at once: the field carries a **dominant lattice** (12.0 cells) with
a **persistent secondary component** (8.73 cells), and a window's argmax is almost always the dominant one. The branch is
therefore not a discrete per-structure state that a daughter can inherit or not — it is a **world-level mixture**, and the
question has to be asked with spectral *weights*, not with a class.

So X71's "multistability" needs one clarification, which is the useful output of this second void: the coexistence is
**between attractors reached by different worlds**, plus a secondary mode that lives inside each world. Nobody has yet shown
a world in which two structures of different branches sit side by side as equals; what the data show is one dominant branch
per world with a minority component.

## What the third attempt needs

1. **Replace the class with two band powers per structure**: the fraction of local spectral power within ±1 bin of 12.0
   cells and of 8.73 cells. A daughter "takes the parent's branch" then means "the daughter's dominant band matches the
   parent's dominant band **and** the case is not at the ceiling" — the analysis must report the minority cases separately,
   because those are the only ones carrying information.
2. **Select events where the branches differ.** With 10–25 % minority structures, a within-world contrast is possible only
   if the analysis conditions on parent branch, which needs ~150 events per cell and gives ~20–40 informative events per
   world. Five worlds are not enough; this is a ten-world, 300-event-per-world question.
3. **Or change the question.** If the branch is a world property, the interesting quantities are the **switch rate** (how
   often a world changes branch) and what precedes a switch — not a parent–daughter concordance.

## Verdict

**Void** by the registered rule (one class dominates), with two positive by-products: the local-spectrum instrument is
validated (corr 0.90–0.99 against the global peak), and the branch is measured to be a world-level tendency rather than a
per-structure state. No claim about branch heredity is made in either direction, for the second time — and this time the
reason is a property of the medium, not of the instrument.
