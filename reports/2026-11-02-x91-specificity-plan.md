# X91 — is the long memory at the band's shoulders lineage memory, or just a region that looks like itself?

**Why.** The map says the medium is habitable at two shoulders of the band — `F = 0.025` (lattice, 39 components, half-life 1.82) and
`F = 0.040` (percolating maze, 6.9 components, half-life 2.08) — and not in the middle, where it divides plentifully but forgets within a
division. Before that sentence goes anywhere it needs the control that killed an earlier reading of the same kind: **a daughter's size may
follow her parent, or it may follow the place she was born.**

The sizes here are very different in the two shoulders: at 0.025 the structures are small spots among 39, at 0.040 they are parts of a
6.9-component maze. A parent–daughter correlation in a maze can easily be a statement about where the maze is thick rather than about
inheritance. X70 built the control for exactly this and it has an answer at 0.035 (+0.388 gap, 10/10 worlds); nobody has run it at the
shoulders.

This is an **analysis of stored artifacts** — X87's 60 worlds and X88's 40 — with no new runs.

## 1. Manipulation is connected

Five cells (`F = 0.025`, `0.030`, `0.035` from X87; `0.040`, `0.045` from X88), twenty worlds each, all with the split identity convention
and 50-step logging, so the genealogies are the same kind as the ones the method was built on. Connectedness: each cell must carry at
least **100 lag-1 division events** and a stranger must be found for at least 80 % of them; otherwise the cell cannot answer.

## 2. Positive control fires (numeric)

The `F = 0.035` cell is the one where X73 measured the effect with the same code and convention. **The control fires if** its parent
correlation lands in **[0.35, 0.55]** (X73: 0.457 with ten worlds) **and** the parent–stranger gap is positive. If it does not, the
implementation differs from X73's and the whole comparison is void.

## 3. Readout exists and varies

Per cell, over all lag-1 events: Spearman(ancestor peak area, descendant peak area) for the **parent**, the same for the **nearest
non-ancestor** at the daughter's first appearance (`x73_depth.stranger_peak`), and the **gap**. The gap is the readout: it says how much
of the resemblance is specific to the lineage rather than to the neighbourhood.

## 4. Sensitivity arithmetic

At 0.035 X73 had 2 140 events and a gap of 0.388; the cells here carry 3 700–4 900 pairs at 0.025–0.035 and 636–3 753 at 0.040–0.045. The
standard error of a Spearman coefficient at 500 events is ≈0.045, so a gap of **0.15** is 3σ and is the declared resolution. The 0.045
cell, with 636 pairs, resolves 0.15 at ≈2σ and is reported as weaker. Cost: **no runs**, ~10 minutes of CPU.

## 5. Refusal rule (registered before the run)

**Void** if a cell has fewer than 100 events, if a stranger is found for fewer than 80 % of events, or if the §2 control misses.

**Lineage memory** if the gap is at least **0.15** in at least three of the five cells, including at least one of the shoulders
(0.025 or 0.040).
**Regional resemblance** if the gap is below **0.05** in at least three cells, including at least one shoulder — then the "memory" at that
shoulder is a property of the place, not of the line.
**Mixed** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| worlds | X87 (0.025 / 0.030 / 0.035, 20 each) and X88 (0.040 / 0.045, 20 each) — 100 worlds, no new runs |
| identity | split convention, 50-step logging (as X73's method) |
| readout | parent vs nearest non-ancestor Spearman against the daughter's peak area, and the gap |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x91_lineage_specificity.json` |

## Checklist before the series

- [x] connected (100 events, 80 % stranger coverage per cell)
- [x] positive control fires (numeric band from X73, §2)
- [x] readout exists and varies (X73's gap 0.388 at 0.035; the shoulders are the open question)
- [x] sensitivity computed (§4: gap 0.15 at 3σ with 500 events)
- [x] refusal rule written, with "regional resemblance" as a real and expected outcome
- [x] no new runs: stated explicitly, because the question is about stored artifacts

## Status

Registered 2026-11-02 12:20 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
