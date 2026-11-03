# X127 — a lineage dies either by vanishing or by being absorbed, and the three cells may differ in which

**Why.** X126 closed with a trade-off measured but unexplained: in the percolating cell the larger sister's branch survives to the end **+0.1372** of the time against
**+0.2496** in the lattice and **+0.2984** in the middle cell. The plan's first next step was "count cuts per lineage". Reading the logs before writing the
instrument says that "cut" is the wrong word for what the tracker records, and that a better distinction is already measurable.

A uid ends in exactly two ways under `--split-new-uid`: it **divides** (its daughters appear — the identity rule of X122/X123) or it **disappears** (no daughters).
The second case is what all the persistence numbers count as death. But disappearing has two very different meanings in a percolating body: the structure's cells may
**vanish** (real death) or they may **become part of a neighbouring structure** (absorption — the cells are alive, the lineage's identity is not). The logs carry
`area` per component per step, so the difference is measurable without a new run: if a uid disappears and the surviving components grow by about its area, its cells
went somewhere; if they do not, its cells are gone.

That is the question X127 asks, because it decides how the X126 trade-off is read: **is the maze lethal, or is it homogenising?**

## 1. Manipulation is connected

No new worlds. Three cells of ten worlds each, already on disk and already the ones every consequence number uses: `x108` at `F = 0.030` and `0.040`, `x126` at
`0.035` (X126, anchored bit-for-bit). The manipulation is the inflow, measured by X126; this run applies an **instrument** to it, and the instrument's premise is
that the cells differ in what it measures: the largest component at the last step is 55 / 441 / 935 cells (X126), so at `0.040` there is essentially one body and
at `0.030` there are many isolated spots. Connectedness: every death in every world is classified, and the death count per cell is reported.

Definitions, fixed here:

| quantity | definition |
|---|---|
| **death** | a uid present at step `t` and absent at `t+1` with **no daughters** (a uid that divided is not a death) |
| **absorbed** | at its death step the surviving uids' total area grows by ≥ 50 % of the dead uid's area |
| **vanished** | the survivors' total area grows by ≤ 10 % of the dead uid's area |
| **unclear** | anything between (reported, never silently merged into the other two) |
| survivors' growth | Σ area of the uids present at both `t` and `t+1`, at `t+1` minus at `t` |

## 2. Positive control fires (numeric)

Four controls, all required. **The control fires if** all four hold:

1. **End-survival reproduces X126** to four decimals in all three cells: +0.2496 / +0.2984 / +0.1372, with the same pair counts 1 142 / 1 106 / 1 195.
2. **Heredity** `ρ₁ ≥ 0.35` in each cell (0.548 / 0.421 / 0.480).
3. **The area budget closes**: for every death step, the change in total occupied area equals the dead uid's area plus the area of uids born at `t+1` minus the
   area lost by shrinking survivors, within 2 cells. This is the control that the premise is *measured*: if the accounting does not close, the classification is
   arithmetic on noise.
4. **Coverage**: absorbed + vanished + unclear equals the death count in every cell, and every death is attributed to a world and a step.

## 3. Readout exists and varies

Per cell: deaths, the three shares, the median dead area, and the number of deaths whose survivors were within one structure-radius of the dead centroid (the
"adjacent" census, reported as a descriptive number, not as the criterion). Per sister pair: each branch's death fate, and the paired difference in
"the branch's lineage ended by absorption". Variation is expected and checkable in advance: with 1 body against 10–20 spots, the composition cannot be the same
in `0.040` and `0.030`.

## 4. Sensitivity arithmetic

Ten worlds per cell. From X126's pair counts, 963 of 1 195 maze pairs have **neither** branch alive, so deaths number in the hundreds per cell; the smallest cell
(0.030, 138 pairs with neither alive) still supplies well over a hundred death events across ten worlds. A share over 200 deaths has SE 0.035, so a difference of
0.10 between cells is 2.8 σ. **Declared resolution: 0.10 in the absorbed share**, and any cell with fewer than 100 deaths is void rather than "no difference".

## 5. Refusal rule (fixed before the run)

**Void** if any cell has fewer than 100 deaths, or heredity < 0.35, or end-survival misses X126 by more than 0.01, or the area budget fails to close within 2 cells
for more than 5 % of deaths.

**The maze is homogenising** if the absorbed share at `0.040` exceeds that at `0.030` by more than the declared 0.10, and the vanished share moves the other way.
**The maze is lethal** if the absorbed share does not rise and vanished deaths dominate in `0.040`.
**Mixed** if absorbed rises but the shares of unclear exceed 0.20 — in which case the instrument is reported as not sharp enough at this grid and the reading is
deferred, not guessed.

## Design summary

| factor | value |
|---|---|
| artifacts | `x108` (0.030, 0.040) and `x126` (0.035), ten worlds each, dense logs on disk |
| manipulation | inflow, already measured; this run applies an instrument |
| readouts | death count, absorbed / vanished / unclear shares, paired fate difference, adjacency census |
| controls | end-survival reproduces X126; heredity; the area budget closes; coverage is total |
| artifact | `E09_pond/l1_field_x127_absorption.json` |

## Checklist

- [x] connected (every death in every world classified; counts reported per cell)
- [x] positive control numeric (end-survival to four decimals against X126; area budget to 2 cells)
- [x] readout exists and varies (largest component 55 / 441 / 935, so one body against many spots)
- [x] sensitivity computed (§4: 200+ deaths, SE 0.035, declared resolution 0.10)
- [x] refusal rule written, with "the instrument is not sharp enough" as a real outcome

## Status

Registered 2026-11-03 05:06 MSK, before the run. No new worlds, no GPU: reads committed dense logs plus the ten X126 logs on disk.
