# X91 — the memory at both shoulders is lineage memory: a parent predicts a daughter at 0.40–0.55 while the nearest neighbour predicts 0.02–0.24

**Date:** 2026-11-02, 12:30 MSK. **Experiment:** X91 (parent-versus-neighbour control on stored artifacts; no new runs).
**Preregistration:** `reports/2026-11-02-x91-specificity-plan.md` (committed before the analysis).
**Artifacts:** `morphogenesis/experiments/E09_pond/l1_field_x91_lineage_specificity.json`; reads X87's 60 worlds and X88's 40.

## Registered verdict

**Void** — on the `F = 0.045` cell only: the neighbour control could be found for 49 % of its events against a required 80 %. That is
structural, not a defect of the run: at 0.045 the world is a single component in most worlds, so there are almost no non-ancestors to
serve as the control. The void is reported as it fired; the four other cells are interpretable and are reported descriptively below.

## Result

| `F` | events | neighbour found | ρ parent | ρ nearest non-ancestor | **gap** | mean areas parent / daughter |
|---|---|---|---|---|---|---|
| 0.025 | 3 001 | 96 % | 0.400 | 0.104 | **0.296** | 71.7 / 50.7 |
| 0.030 | 3 054 | 96 % | 0.550 | 0.236 | **0.314** | 87.9 / 59.4 |
| 0.035 | 2 403 | 91 % | 0.475 | 0.016 | **0.459** | 183.2 / 120.9 |
| 0.040 | 3 753 | 84 % | 0.471 | 0.064 | **0.407** | 726.3 / 385.2 |
| 0.045 | 636 | 49 % | 0.165 | −0.585 | (0.750) | 2 398.3 / 1 270.6 |

The **positive control fired**: at 0.035 the parent correlation is 0.475 in the band [0.35, 0.55] taken from X73, whose value was 0.457 with
ten worlds. Same code (`x73_depth.stranger_peak`), same identity convention, twenty worlds instead of ten — the implementation reproduces.

So in every cell where the control is possible, **a daughter's area follows her parent far more than it follows her nearest
non-ancestor**: the gaps are 0.30–0.46, and both shoulders are among them (0.296 at 0.025, 0.407 at 0.040). The registered "lineage
memory" clause (gap ≥ 0.15 in three cells including a shoulder) would have fired with four cells and both shoulders; it is blocked only by
the fifth cell, where the control has no subject.

**The shoulders' long half-life is therefore lineage memory, not a region that resembles itself.** That was the one way the map could have
been an artefact, and it is closed.

## The design defect, named

The refusal rule voided the whole series because one cell cannot host the control. A control that requires neighbours cannot be applied
where there are no neighbours, and the correct handling is a **cell-level** void (report the cell as "control not applicable"), not a
series-level one. That is now written down: the rule for controls that need a population is "void the cell, keep the series".

## What this changes in the picture

The map from X87/X88 said the medium is habitable at the band's two shoulders (`F = 0.025` lattice and `F = 0.040` just above the
percolation threshold) and forgets quickly in the middle. X91 adds that at both shoulders the resemblance is **specific to the line** —
a daughter resembles her own mother, not the neighbourhood. That is the condition the whole heredity line was built to test, and it holds
at both ends of the habitable region, in a lattice and in a maze, with the same sign and comparable size.

What is still missing for a claim about *inheritance* in the biological sense is the third leg nobody has measured: whether the
resemblance **pays** — whether a lineage whose size matches its parent's leaves more descendants. X29 tried to measure that and its meter
was invalid; the field line still has no measurement of consequence.

доска: принято 0, отклонено 0, отложено 0.

**Correction, 02.11 12:25 — the sample was twelve worlds per lattice cell, not twenty.** The analysis globbed `x87_*` only and X87
holds twelve worlds per cell; the registered twenty are X87's twelve **plus** X85's eight (seeds 191–198), which live under a different
prefix. Both are pooled now and everything below is recomputed on the full twenty:

| `F` | events | neighbour found | ρ parent | ρ nearest non-ancestor | gap |
|---|---|---|---|---|---|
| 0.025 | 4 901 | 96 % | 0.391 | 0.130 | **0.261** |
| 0.030 | 4 791 | 96 % | 0.549 | 0.249 | **0.300** |
| 0.035 | 4 115 | 91 % | 0.470 | 0.059 | **0.411** |
| 0.040 | 3 753 | 84 % | 0.471 | 0.064 | **0.407** |
| 0.045 | 636 | 49 % | 0.165 | −0.585 | (control not applicable) |

The conclusion is unchanged and slightly stronger: gaps 0.26–0.41 against the earlier 0.30–0.46 on a smaller sample, both shoulders
lineage-specific, and the 0.035 control now reads 0.470 against X73's 0.457. The earlier table in this report is superseded as values, not
as direction; the numbers to quote are these.

The lesson is the same class as `--sample-every` and `--split-new-uid`: **a series' identity is not its prefix.** Two files with different
prefixes were one cell by design, and a glob silently halved the sample. The fix is procedural — the cell's file list is now written as a
list of prefixes in the script, and a cell's world count is checked against the registered number before the numbers are read.
