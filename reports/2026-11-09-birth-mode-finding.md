# Finding: 96 % of cells arrive by activation, not by reproduction

**Date:** 2026-11-09. **Source:** `python scripts/inheritance_by_birth.py --dir morphogenesis/experiments/E20`,
37 artifacts, 24 985 cells.

## The numbers

| how the cell arrived | cells | share |
|---|---|---|
| **activation** (grown by the rule; genome from the pre-assigned field) | **24 082** | **0.964** |
| **reproduction** (budded; genome from the parent, with mutation) | **903** | **0.036** |

## Why this matters

**In this world almost nothing is inherited.** A cell grown by the rule receives the genome that was
pre-assigned to its grid position when the field was created; there is no parent. Only 3.6 % of cells came from
a bud, and only those have a parent whose genome they carry.

**So a parent-child correlation computed on the whole population would be measuring, 96 % of the time, the
correlation between a cell and the random value that was already sitting in its position.** That is not
inheritance; it is the initial condition.

**This is the mechanism behind the third review's remark** (R6 in `docs/design-audit.md`): "genome inheritance at
growth is not defined". It was recorded then as a documentation gap. It is larger than that: **it is a
quantitative fact about the world**, and it was invisible until the per-cell `birth_mode` was recorded on
2026-11-09.

## What this does not say

1. **It does not say the world is broken.** Growing by a rule is a legitimate model; what was missing is the
   record of which path made a cell, and that record now exists.
2. **It does not invalidate the earlier inheritance numbers** — it says they need re-reading. Every series that
   reported a parent-child correlation before 2026-11-09 pooled the two paths, and the pooled number is
   dominated by activation. **Those numbers are not wrong; they are about a different quantity than the word
   "inheritance" suggests.**
3. **It does not say reproduction is rare in every mode.** `budding_unit = "cell"` and the other modes were not
   measured here; this is one profile (`pond-v2-record`) at one horizon (300 steps).

## What to do

1. **Every inheritance analysis is stratified by `birth_mode` from now on** — the tool is
   `scripts/inheritance_by_birth.py`.
2. **The earlier inheritance claims in `docs/world-design.md` §10* are marked** as pooled over both paths, with a
   pointer to this finding. They are not deleted; they are qualified.
3. **The next experiment on inheritance asks the question only of the 3.6 %** — and if that fraction is too
   small for a correlation, the answer is that this world cannot answer it in this configuration, which is
   itself the result.
