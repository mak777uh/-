# X93 — do sisters pay for size? A within-family contrast with lifetime as the outcome

**Why.** The third leg of the heredity claim is consequence: resemblance is not inheritance until a larger structure does better. Two
attempts failed for opposite reasons — X29's meter was invalid (a selection differential in an arm where the trait cannot act), X92's
correlation was mechanical (the component that divides is by construction the large one, so area and out-degree share an object).

The fix is a **within-family contrast**: compare sisters born from the same mother at the same moment. The mother, the place and the time
are then fixed by construction, and no mechanical link survives — a sister's area and a sister's lifetime are different quantities. This is
an **analysis of stored artifacts** (X85 + X87 + X88), no new runs.

## 1. Manipulation is connected

Four cells (`F = 0.025`, `0.030`, `0.035` lattice; `0.040` percolating), twenty worlds each, split identity convention. A usable family is
a mother with **at least two daughters** that both have a recorded lifetime and differ in peak area. Connectedness: each cell must supply
at least **200 usable sister pairs**; otherwise the cell cannot answer and is void (cell-level, not series-level — the rule earned in
X91).

## 2. Positive control fires (numeric)

The contrast has an obvious null that is not 0.5-by-assumption: pair each daughter with a **pseudo-sister from a different mother** in the
same world (same snapshot, matched by birth time ±1 snapshot). **The control fires if** that cross-family fraction lies in **[0.45, 0.55]**
in every cell — i.e. the pairing machinery itself does not manufacture a preference. If it does, the series is void.

## 3. Readout exists and varies

Per cell: over all sister pairs with unequal areas, the fraction in which the **larger sister has the longer lifetime**, with a binomial z
against 0.5; and the same fraction for cross-family pseudo-pairs. The readout is the **difference** between the two fractions.

## 4. Sensitivity arithmetic

With 200 pairs the standard error of a fraction is 0.035, so a difference of **0.10** from 0.5 is ≈2.8σ; with 1 000 pairs it is 0.016 and
0.05 is 3σ. The declared resolution is therefore **0.10 with 200–500 pairs, 0.05 above 1 000**. Cost: **no runs**, ~15 minutes of CPU.

## 5. Refusal rule (registered before the run)

**Void** (cell-level) if fewer than 200 usable pairs or if no lifetime is recorded for one of the sisters.

**Size pays within the family** if the larger-sister fraction is at least **0.55**, at least **0.05** above the cross-family control, and
above 0.5 at **z ≥ 2** in at least two cells.
**Size does not pay within the family** if the fraction is within **0.03** of the control in at least three cells.
**Mixed** otherwise, printed cell by cell with both fractions and their z.

## Design summary

| factor | value |
|---|---|
| worlds | X85 + X87 (0.025 / 0.030 / 0.035) and X88 (0.040) — twenty per cell, stored artifacts only |
| family | mother → daughters from `uid_pairs`; area and lifetime from `uid_outcomes` |
| readout | fraction of sister pairs where the larger sister lives longer, against the cross-family control |
| artifact | `morphogenesis/experiments/E09_pond/l1_field_x93_sibling_contrast.json` |

## Checklist before the series

- [x] connected (200 usable pairs per cell, else cell-level void)
- [x] positive control fires (numeric: cross-family fraction in [0.45, 0.55], §2)
- [x] readout exists and varies (147 families with ≥2 daughters in one world at 0.025 alone)
- [x] sensitivity computed (§4: 0.10 at 200 pairs, 0.05 above 1 000)
- [x] refusal rule written, with cell-level void as earned in X91
- [x] no new runs: stated, because the question is about stored artifacts

## Status

Registered 2026-11-02 12:40 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
