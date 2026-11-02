# X118 — at fixed size, does the number of daughters matter?

**Why.** X116 matched on the number of daughters (a **mediator**) and the survival advantage halved. X117 matched on area (the **exposure**) and the advantage
vanished — but that is what conditioning on the exposure must do, so it answered nothing (the void is recorded). The test that separates "more daughters"
from "bigger" keeps the exposure and varies the mediator the other way round:

> among sister pairs of **nearly equal area**, compare survival of the branch with **more** daughters against the branch with **fewer**.

If the mediator matters independently of size, that difference is positive; if all the action is size, it is zero.

## 1. Manipulation is connected

X108's twenty runs. Subset: pairs whose sister areas are within **±10 %** *and* whose daughter counts differ by at least one (so the mediator varies where the
exposure does not). Connectedness: at least **120 pairs** per cell; if fewer, the area window widens to ±15 % and the report says which was used.

## 2. Positive control fires (numeric)

Three controls, all required, because this design's whole point is that the two quantities are separated:

1. **Heredity** `≥ 0.35` in both cells (0.548 / 0.480).
2. **The area match holds:** the mean area ratio between the branches must lie in **[0.95, 1.05]** in the used subset — the exposure really is fixed.
3. **The mediator varies:** the mean difference in daughters must be **≥ 1.0** in the used subset — there is a contrast to measure.

## 3. Readout exists and varies

Per cell: the paired survival difference (more daughters minus fewer), its bootstrap 95 % interval, the counts (only the many-daughter branch survives / only
the few), and the mean area ratio and daughters difference in the subset. Variation exists: X116's equal-daughters subset gives 0.125 with 104:25, so the
survival signal is present and the question is whether it moves with the mediator at fixed size.

## 4. Sensitivity arithmetic

With 120–250 pairs the paired-proportion SE is ≤ 0.045, so the declared resolution is **0.12**. An effect below it is "unresolved at this depth", not absent.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 120 pairs even at ±15 %, heredity misses 0.35, the area ratio leaves [0.95, 1.05], or the daughters difference is below 1.0.

**The mediator matters independently of size** if the survival difference is positive with the interval excluding zero in both cells.
**The mediator adds nothing beyond size** if the interval contains zero in both cells.
**Mixed** otherwise, cells reported separately.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs |
| subset | areas within ±10 % (±15 % fallback), daughter counts differing by ≥ 1 |
| readouts | paired survival difference (more daughters − fewer), area ratio, daughters difference |
| roles | area = **exposure** (held fixed), daughters = **mediator** (varied) |
| controls | heredity ≥ 0.35; area ratio in [0.95, 1.05]; daughters difference ≥ 1.0 |
| artifact | `E09_pond/l1_field_x118_mediator.json` |

## Checklist

- [x] connected (120 pairs; the window used is stated)
- [x] positive control numeric (heredity, area ratio, daughters difference)
- [x] readout exists and varies (X116's 0.125 with 104:25)
- [x] sensitivity computed (§4: SE ≤ 0.045, resolution 0.12)
- [x] refusal rule written, with "adds nothing beyond size" as a real outcome
- [x] roles named: exposure held, mediator varied
- [x] no new runs: stated

## Status

Registered 2026-11-03 01:46 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
