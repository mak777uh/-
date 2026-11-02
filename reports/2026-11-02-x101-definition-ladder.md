# X101 — three definitions of "size", one ladder: heredity is strongest exactly where the definition is an excursion set

**Date:** 2026-11-02, 20:05 MSK. **Experiment:** X101 (basins by steepest ascent on the stored snapshots of X100; no new runs).
**Preregistration:** `reports/2026-11-02-x101-watershed-plan.md` (committed before the analysis).
**Artifacts:** `morphogenesis/experiments/E09_pond/l1_field_x101_watershed.json`.

## Registered verdict

**Heredity needs the cut** — the preregistered clause for a basin measure that moves ρ₁ by at least 0.20 in one cell. It moved by
−0.231 at `F = 0.030` and −0.209 at 0.040.

Both controls fired: the threshold-based ρ₁ reproduced X100's own values within 0.02 (0.531 and 0.384), and the basins partitioned the
field in all twenty worlds (no cell lost, none doubled).

## The ladder

Three definitions of the same thing, evaluated on the **same ancestor-descendant pairs** (2 165 pairs at 0.030, 1 761 at 0.040):

| definition | what the boundary is | ρ₁ at 0.030 | ρ₁ at 0.040 | median size at 0.030 | median size at 0.040 |
|---|---|---|---|---|---|
| excursion set, `v > 0.20` | an absolute level | **0.531** | **0.384** | 76 | 423 |
| basin by steepest ascent | the field's own topology | 0.300 | 0.174 | 112 | 81 |
| basin at half the local maximum | a level relative to each structure | 0.176 | 0.058 | 18 | 17 |

The ordering is the same in both inflows, and it is monotone in one property: **how much the definition behaves like a fixed absolute
excursion**. The absolute cut gives the strongest heredity; the topological basin, which merges structures across saddles and pools
neighbours (112 cells against 76), gives about 60 % of it; the relative core gives a third or less.

## What this settles, and what it costs us

It settles the question X99 opened. The map is not merely "definition-bound" in the sense that its numbers move; the **strength of
heredity itself** is a function of the definition, and the absolute excursion set of 0.20 sits at the strong end of a ladder that spans a
factor of three in ρ₁.

The reading that fits everything measured today: what the medium passes from mother to daughter is **how far the excursion spreads** —
an extensive property of a fixed-density region — and not the peak height (X100's core) nor the drainage basin (which is a property of the
whole field's topography rather than of the structure). On that reading, the "definition dependence" is not a defect of the measurement
but the finding: the inherited object *is* the excursion set, and any measure that stops being an excursion set stops measuring it.

The cost is real and belongs in the text: every heredity number in this line is a number about excursion sets at 0.20, and the
sensitivity is now known to be a factor of three, not a whisker.

## What is next, and what is not

- **Not** a fourth definition. Three now span the space: absolute level, topology, relative level. A fourth would refine a ladder whose
  shape is already clear.
- **Yes** to the one question the ladder raises: does the *specificity* result of X91 (parent beats nearest neighbour) survive the weaker
  definition? If the parent–stranger gap also shrinks with the definition, then "heredity" is even more narrowly an excursion-set concept;
  if the gap stays, the specificity is robust even where the level is not. That can be answered on the snapshots already on disk,
  registered as X102.

доска: принято 0, отклонено 0, отложено 0.
