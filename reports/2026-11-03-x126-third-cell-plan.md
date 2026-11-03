# X126 — the third cell: is the consequence chain a gradient in inflow, or a step at percolation?

**Why.** Every consequence number in this line comes from two cells, `F = 0.030` (regular spots, "lattice") and `F = 0.040` (percolating, "maze"), and every one of
them differs by a factor of nearly two: depth +1.479 against +2.213, rate 6.06 against 18.96, end-survival +0.250 against +0.137, and the share of sister pairs
whose generation time is too short to measure 16 % against 47 %. With two cells the line cannot say whether the habitat acts as a **gradient** in inflow (more
food, shorter generations, deeper lineages) or as a **step** at the percolation transition. One cell between them decides between those readings, and it costs ten
runs.

## 1. Manipulation is connected

Ten worlds at `F = 0.035`, seeds 301-310 — the same seeds as `F = 0.030` and `F = 0.040`, so the three-cell comparison is **paired by seed** and the only thing
that varies is the inflow. Flags: byte-identical to `x108_series.py`'s `COMMON`, with one deliberate difference — fields are not saved, because `x108_series.py`
records that a field save is pure I/O and draws no randomness. The anchor is what proves the difference is inert: `F = 0.030`, seed 301, this script's flags,
against the committed `x108_f030_s301.json`, compared key by key, and **the series does not start unless that comparison is exact**.

The readouts are the definitions fixed by X125c, applied unchanged:

| readout | definition | filter |
|---|---|---|
| depth | mean paired sister difference, generations | none |
| rate | paired difference of `depth / generation time × 1000` | both generation times ≥ 50 steps; denominator printed |
| generation-time fraction | fraction of pairs in which the larger sister's generation time is longer | ties excluded (X93's rule) |
| below-floor share | fraction of pairs with a generation time < 50 steps | none — this is the readout that separates gradient from step |
| end-survival | paired difference in "the branch's subtree has a member at the last logged step" | none |

## 2. Positive control fires (numeric)

Four controls, all required. **The control fires if** all four hold:

1. **Anchor**: the `F = 0.030 / seed 301` rerun is identical to `x108_f030_s301.json` in `params`, `uid_pairs` and `per_step` (exactly, not within tolerance).
2. **Liveness** in all ten new runs under the structural rule: occupancy ≥ 0.05 and largest component ≥ 50 cells (X110b). A dead or shattered world is not a
   measurement of a habitat.
3. **Heredity** `ρ₁ ≥ 0.35` in the new cell (the two known cells give 0.548 / 0.480).
4. **The two known cells re-derive exactly** under the same analysis code: depth +1.479 / +2.213 to the digit, tie-excluded fractions 0.526 / 0.388, rate
   6.056 / 18.96 with denominators 957 of 1 142 and 638 of 1 195. If any of these moves, the analysis code is not the code that produced them and nothing in the
   new cell may be read.

## 3. Readout exists and varies

Per cell and readout: the point value, a bootstrap 95 % interval, and the count. Variation across the known cells is a factor of 1.5–3 in every readout
(`0.030` → `0.040`), so a third cell cannot be mistaken for either neighbour by construction. The readout that matters most is the **below-floor share**: 16 %
against 47 % is the largest relative difference between the cells, and it is the one that says whether the maze is a different kind of habitat or simply further
along the same axis.

## 4. Sensitivity arithmetic

Ten worlds give 800–1 200 sister pairs per cell (the known cells give 1 142 and 1 195). With ~1 000 pairs: the depth interval is ±0.2 generations, the rate
interval ±1–4 depending on the denominator, the tie-excluded fraction ±0.045, the below-floor share ±0.03, end-survival ±0.05. The declared resolution:

- a readout is a **gradient** if the new cell lies within **2 SE of the midpoint** between the two known cells (i.e. the chain interpolates linearly), and
- a readout is a **step** if the new cell lies within 2 SE of **one** neighbour while being more than 2 SE from that midpoint, and
- anything else is **non-monotone** and is published as such.

The midpoint is fixed here, before the data: `depth 1.846`, `rate 12.51`, `fraction 0.457`, `below-floor share 0.315`, `end-survival +0.194`.

## 5. Refusal rule (fixed before the run)

**Void** if the anchor is not exact, or any of the ten runs fails the structural liveness rule, or heredity < 0.35, or a cell has fewer than 800 pairs.

**A gradient** is published if the below-floor share and the depth contrast are both within 2 SE of the midpoint; **a step** if both sit within 2 SE of the same
neighbour and outside 2 SE of the midpoint; **a mixed result** (one gradient, one step) is published with the two readouts named, and is the outcome that says the
habitat acts on generations and on lineage depth through different channels — which would be a finding, not a failure. "Non-monotone" is a legitimate result too
and is not to be re-run until it looks monotone: the three cells are fixed by design, not by the answer.

## Design summary

| factor | value |
|---|---|
| manipulation | inflow `F = 0.035`, with `0.030` and `0.040` as the two known cells |
| runs | ten worlds, seeds 301-310, 6 000 steps, 96², dense logging every 10 steps, `--split-new-uid` |
| cost | ~20 min, ~28 MB of logs, no training, no GPU training lane |
| controls | exact anchor; structural liveness; heredity ≥ 0.35; the two known cells re-derive |
| readouts | depth, filtered rate with denominator, tie-excluded fraction, below-floor share, end-survival |
| artifact | `E09_pond/l1_field_x126_third_cell.json` |

Disk note: the host has 8.6 GB free, under the 10 GB line that governs training runs and archives; this series writes 28 MB of logs and no weights, so it does not
consume the budget the rule protects.

## Checklist

- [x] connected (same seeds, one flag difference, proven inert by an exact anchor)
- [x] positive control numeric (depth, fractions and rates of the two known cells must re-derive to the digit)
- [x] readout exists and varies (factor 1.5–3 between the known cells in every readout)
- [x] sensitivity computed (§4: intervals and the fixed midpoints)
- [x] refusal rule written, with "mixed" and "non-monotone" as real outcomes

## Status

Registered 2026-11-03 03:45 MSK, before the anchor and before the series. Light CPU run, no training.

## Amendment (03:52, before the series started)

Control 1 as written demanded that `params` be identical, which it cannot be: the protocol deliberately drops two field-saving entries. The anchor is therefore
compared **key by key with the two declared flags excluded** (`save_fields`, `save_fields_every`, plus the `fields_saved` marker), and the comparison prints them.
The anchor ran, returned `ANCHOR OK`, and the exact statement is: **every top-level key except `fields_saved` is identical, every `params` field except the two
flags is identical, and `uid_pairs` — the whole genealogy — is identical.** The worlds are the same worlds.
