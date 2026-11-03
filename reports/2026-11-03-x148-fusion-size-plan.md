# X148 — does a seed divide because its fusion product is larger? (analysis, no new runs)

**Why.** X142 found the boundary between mutual coalescence (M) and persistence/absorption (A, P) at a surface gap of
8–9 cells, and X145 refuted the simple clock story: a lone radius-3 disc divides at 180 steps while a pair at gaps 1–8
is one body by step 50. What both experiments leave untouched is the natural alternative — that the **fusion product**
divides when it is **large enough**, and that the gap decides whether it gets there.

The areas at the fusion step are already visible in the arms and they are **not** monotone in the outcome (99 cells at
gap 1 and 287 at gap 11, both coalescing or dividing), so the naive "bigger product divides" is not obviously true
either. But they have never been compared at one-cell spacing across the boundary, with the seed as the unit.

## 1. Manipulation is connected

No new runs. The population is every arm of X142 plus the reused X136/X139/X140 arms, i.e. 75 runs whose full logs are
on disk, at radius 3 gap 1–11 and radius 4.5 gap 4–7. The manipulation whose effect is measured is the **gap**, which is
already in the file names; the quantity measured per run is the area of the single component at the step where the two
seeded uids disappear, and whether a seeded disc divided at or before that step.

## 2. Positive control fires (numeric)

Four controls. **The control fires if** all four hold:

1. **The classification reproduces X142 exactly**: M/A/P per arm identical to `l1_field_x142_coalescence.json`. A
   difference means the analysis moved, not the world.
2. **The fusion area is read on the right step**: at the fusion step there must be exactly **one** component, and its
   area must be within 10 % of the sum of the two seeded components one logged step earlier. Arms where the pair does
   not fuse within the horizon (P arms) have no fusion step and are excluded from the comparison, not set to zero.
3. **The number of seeds that divide** in arms 9–11 is the number X142 recorded (2, 3 and 3 of 5).
4. **Every quoted area is a per-seed number with its arm median**, and every median is printed with n.

## 3. Readout exists and varies

The fusion area already varies across arms from about 99 to 309 cells and within arms enough to see: at gap 10 the two
coalescing seeds have different products. The readout is therefore not stuck.

## 4. Sensitivity arithmetic

The comparison is a **rank** comparison within and across arms: for each arm, the seeds that divided against those that
did not, with the fusion area as the order. Five seeds per arm and 19 arms give at most 5 observations per arm, so no
continuous effect is claimed; what is claimed is a **sign** — whether the dividing seeds are, in each arm, the ones with
the larger fusion product. With 4 arms where both outcomes occur (gaps 9, 10, 11 at radius 3), a consistent sign in all
four is p = 1/16 by sign test; three of four is not enough to claim anything.

## 5. Refusal rule (fixed before the run)

**Void** if control 1 fails (the classification must reproduce X142), if control 2 fails (no clean fusion step), or if
control 3 fails.

The registered outcomes:

- **Size rules**: in every arm where both outcomes occur, the dividing seeds have the larger fusion product (rank
  separation 5/5 or 4/4), and the arm medians are ordered across the boundary. The mechanism then has a number — the
  product area at which the body divides — and the next run is a direct test of it.
- **Size does not rule**: the sign is inconsistent across arms, or the dividing seeds are the smaller ones. The
  mechanism is then something else — the timing of the contact, the shape of the product — and the report says so.
- **Not decidable**: fewer than three arms contain both outcomes (the arms are then too far from the boundary to
  compare), and the next design must place arms at the boundary rather than sweeping further.

## Design summary

| factor | value |
|---|---|
| runs | none new; 75 existing full logs (radius 3 gaps 1–11, radius 4.5 gaps 4–7) |
| unit | the seed, with its arm median; denominators printed |
| readouts | fusion-step area, whether a seeded disc divided, M/A/P per arm |
| controls | classification identical to X142; one component at the fusion step; the counts of dividing seeds; per-seed numbers |
| artifact | additions to `E09_pond/l1_field_x142_coalescence.json` under `fusion` |

## Checklist

- [x] connected (no new manipulation; the gap is already the arm, and the fusion step is read from each run's own log)
- [x] positive control numeric (classification must reproduce X142; the fusion area must be one component at 90 % of the pair's sum)
- [x] readout exists and varies (99 to 309 cells across arms)
- [x] sensitivity computed (§4: a sign test over the arms that contain both outcomes, 4 arms at most)
- [x] refusal rule written, with size-rules / size-does-not-rule / not-decidable as separate outcomes

## Status

Registered 2026-11-03 17:50 MSK, before the analysis. No runs.
