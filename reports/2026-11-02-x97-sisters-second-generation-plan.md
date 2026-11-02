# X97 — does the sister advantage reach the second generation?

**Why.** X93 found that sisters differ: the larger sister lives longer by `+0.050` at `F = 0.025` (z 4.7) and `+0.082` at 0.030, nothing at
0.035, and the maze penalises the larger sister (`0.401`, z −8.9). Every one of those statements is about the *first* generation. The
question that decides whether the advantage is a property of a lineage rather than of one structure is whether it **persists into the
granddaughters**: if the larger sister's line does better in the next generation too, size is a lineage trait here; if it does not, the
first-generation effect is a one-off.

**And it needs no new runs.** The dense series carries `--split-new-uid`, so every daughter's own daughters are in `uid_pairs`, and the
three-level genealogy (mother → sister → granddaughter) can be read from the logs.

## 1. Manipulation is connected

X108's twenty runs (seeds 301–310, two inflows). For every mother with at least two daughters (sisters), and every pair of sisters, look
at the **granddaughters** — the daughters of each sister. Connectedness: at least **100 sister pairs** per cell whose two branches each
produce at least one granddaughter (X93 had sister pairs from the same logs; the granddaughter filter will cut the sample and the number is
reported).

## 2. Positive control fires (numeric)

Two controls, both required:

1. **Heredity on the same pairs:** `ρ(mother's peak area, daughter's peak area) ≥ 0.35` in both cells — the level this line has measured
   since X100 (0.548 / 0.480 on these worlds).
2. **The first-generation sister effect reproduces its sign at 0.030** (+0.05 in X93's measurement): the paired difference in *daughters'*
   area between the larger and the smaller sister must be positive in the lattice cell with `z ≥ 2`. If it is not, the pairing has drifted
   and nothing about granddaughters is comparable.

## 3. Readout exists and varies

Per cell: the paired difference in the **granddaughters'** peak areas (all granddaughters of the larger sister against all of the smaller,
averaged per sister pair), its bootstrap confidence interval and z, and the same difference measured on **lifetimes** as a secondary
readout. Variation exists by construction: X93's sister differences span −0.05 to +0.08 and the granddaughters' areas span an order of
magnitude.

## 4. Sensitivity arithmetic

With ~100 pairs per cell the standard error of a paired difference in area share is ~0.02–0.03; the declared resolution is a **0.05**
difference with a bootstrap 95 % interval excluding zero, i.e. about two standard errors. A difference smaller than that is reported as
"not resolved", not as a null.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 100 usable sister pairs, if the heredity control misses 0.35, or if the first-generation sister effect
fails its sign-and-z check.

**The advantage persists** if the granddaughters' paired difference is positive with a bootstrap 95 % interval excluding zero in the
lattice cell.
**The advantage is first-generation only** if that interval contains zero while the first-generation effect passed its own control.
**The advantage reverses** if the interval excludes zero on the negative side.
**Mixed** otherwise, printed per cell — and the maze cell is reported separately, because X93 found the **opposite** sign there.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs (dense logging, `--split-new-uid`) |
| readouts | paired difference in granddaughters' peak area (primary) and lifetime (secondary) between the larger and the smaller sister |
| controls | heredity ≥ 0.35; first-generation sister effect reproduces sign with z ≥ 2 at 0.030 |
| artifact | `E09_pond/l1_field_x97_sisters_second_generation.json` |

## Checklist

- [x] connected (100 sister pairs with granddaughters on both branches)
- [x] positive control numeric (heredity ≥ 0.35; first-generation effect sign with z ≥ 2)
- [x] readout exists and varies (X93's sister differences −0.05…+0.08; granddaughter areas span an order of magnitude)
- [x] sensitivity computed (§4: SE 0.02–0.03, resolution 0.05 with a bootstrap interval)
- [x] refusal rule written, with "first-generation only" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 23:50 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
