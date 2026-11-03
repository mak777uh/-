# X125 — one definition per quantity, and the affected numbers recomputed under it

**Why.** X124 found the line using one word for two quantities: "rate" was `depth / generation time × 1000` per uid in X113c and the same formula per sister pair
in X124 (6.06 against 36.6), and "generation time" was a raw difference in X124 (the larger sister's **shorter** by 412 steps) and a share of the pair's mean in
X93 (the larger sister's **longer** by 0.05–0.08). Neither finding is wrong; the vocabulary is. This fixes it.

## 1. Manipulation is connected

X108's twenty runs, the sister pairs used by X97/X113/X124 (≥ 1 000 per cell). Three quantities, each defined once, with its unit of aggregation named:

| quantity | definition | aggregated as |
|---|---|---|
| **generation time** `g` | the uid's last logged appearance minus its first, plus one, in logged steps | per uid; contrasts are **raw step differences** within a pair |
| **depth** `d` | the longest descendant chain below the uid, in generations | per uid; contrasts are raw generation differences |
| **rate** `r` | `d / g × 1000` — generations per 1 000 steps of that uid's own generation | per uid, and the **pair contrast is the difference of the two uids' rates** (the unit of the claim is the pair) |

The share form (`g_big / g_small`) is kept as a **separate, named** readout (`share`), never as a substitute for the raw difference.

## 2. Positive control fires (numeric)

Two controls, both required (the control fires if both bands hold):

1. **Heredity** `≥ 0.35` in both cells (0.548 / 0.480).
2. **The definitions reproduce their sources on the same pairs:** depth contrast reproduces X113 (+1.479 / +2.213) within 10 %, and the **uid-weighted** rate
   contrast reproduces X113c (+6.06 / +18.96) within 10 %. The second is the check that the recomputation is the same arithmetic as the original, only named.

## 3. Readout exists and varies

Per cell: the raw generation-time difference, the share, the depth difference, the **pair-weighted** rate difference and the **uid-weighted** rate difference, each
with a bootstrap 95 % interval, and the counts. Variation exists: X124's raw difference is −412 steps with an interval excluding zero.

## 4. Sensitivity arithmetic

1 000–1 200 pairs; generation times quantised by the 10-step logging interval, so a 412-step difference is 41 quanta. The declared resolution is an interval
excluding zero for each readout, and a stated rule for which one is published: **the pair-weighted rate**, because the claim is about pairs.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 1 000 pairs or either control misses its band.

**The vocabulary is fixed** if all five readouts are reported with their unit, the two rate statistics are both printed, and the difference between them is stated as
a property of weighting rather than as an error.
**Contradiction** if the pair-weighted and uid-weighted rate contrasts have opposite signs — then no single sentence can be published until the weighting is
chosen by the design, not by convenience.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs |
| readouts | raw generation time, share, depth, pair-weighted rate, uid-weighted rate |
| controls | heredity ≥ 0.35; depth and uid-weighted rate reproduce X113/X113c |
| artifact | `E09_pond/l1_field_x125_definitions.json` |

## Checklist

- [x] connected (1 000 pairs per cell)
- [x] positive control numeric (depth and uid-weighted rate reproduce their sources)
- [x] readout exists and varies (−412 steps with an interval excluding zero)
- [x] sensitivity computed (§4: 41 quanta; pair-weighted chosen by design)
- [x] refusal rule written, with "contradiction between weightings" as a real outcome
- [x] definitions stated once, with units

## Status

Registered 2026-11-03 03:04 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
