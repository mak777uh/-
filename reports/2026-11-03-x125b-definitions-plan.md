# X125b — the filter printed with the number, and the four statistics of one paired difference

**Why.** X125 voided by its own control and produced three corrections ([void](2026-11-03-x125-definitions-void.md); aggregate
`l1_field_x125_definitions.json`). The rate gap between X113c and X124 is a **sample filter** (both sisters' generation times ≥ 50 steps), not a weighting;
X93's "+0.05" is a **proportion of pairs**, not a share of a mean; the mean-of-ratios is unusable. This amendment settles all three in one run: the same pairs,
the same definitions, with the filter printed and the four statistics side by side.

## 1. Manipulation is connected

X108's twenty dense runs, the sister pairs used by X97/X113/X124 (≥ 1 000 per cell, both cells). Three quantities, one definition each, and — the new part —
each with the filter and the statistic stated in the same sentence as the number:

| quantity | definition | filter | published statistic |
|---|---|---|---|
| **generation time** `g` | uid's last logged step − first + 1, in logged steps | none (all pairs) | **median** paired difference, and the **fraction of pairs** in which the larger sister's `g` is larger |
| **depth** `d` | longest descendant chain below the uid, in generations | none | **mean** paired difference |
| **rate** `r` | `d / g × 1000` — generations per 1 000 steps of that uid's own generation | **both sisters' `g` ≥ 50 steps** (≥ 5 logging quanta) | **mean** paired difference, pair-weighted |

Why these statistics and not others: generation time is unbounded above and its mean is tail-dominated (X125: mean −412 with a ±100 interval while `g` spans
2–1 500 steps), so the median and the majority sign are the readable pair statistics. Depth is a small integer (0–5): no tail, so the mean is fine. Rate is
bounded below by the filter and its contrast is the claim, so the pair-weighted mean is the published one. **The choice is made here, before the run, so it
cannot be made by whichever number looks best afterwards.**

The four statistics are always printed for the generation-time readout: mean, median, fraction of pairs with a positive difference, and ratio of means. The
ratio of means is printed **instead of** the mean of ratios, which X125 withdrew (mean of `g_big/g_small` = 12.0 / 13.7, driven by denominators near zero).

## 2. Positive control fires (numeric)

Three controls, all required; the control fires if all three bands hold in both cells:

1. **Heredity** `≥ 0.35` (0.548 / 0.480).
2. **Depth contrast** reproduces X113 (+1.479 / +2.213) within 10 % — the leg that was never definition-bound, so it must not move.
3. **Filtered pair-weighted rate reproduces X113c** (+6.056 / +18.96) within 10 % — this is the direct test of the X125 void's diagnosis: *if printing the
   filter is the whole difference, this control fires; if it misses, the diagnosis is wrong and the void stands.*

A fourth number is printed and is **not** a control: X93's proportion (0.553 at 0.030, 0.401 at 0.040) recomputed on X108's pairs. Different series, so a
disagreement is a cross-series comparison to report, not a void.

## 3. Readout exists and varies

Per cell: `g`'s mean, median, fraction positive, ratio of means; `d`'s mean and interval; `r`'s filtered mean and interval, plus the unfiltered mean as
sensitivity; the tail decomposition of the generation-time difference (mean of the positive part, mean of the negative part, share of pairs beyond ±1 000
steps); counts of pairs and of the pairs the filter drops. Variation is not an issue — the X125 interval excludes zero in the lattice and the fraction is a
population quantity over ~1 100 pairs.

## 4. Sensitivity arithmetic

1 100–1 200 pairs per cell. `g` is quantised at 10 steps, so a 412-step difference is 41 quanta and a median is resolved to one quantum. A proportion over
1 100 pairs has a standard error of √(0.25/1 100) = 0.015, so a 0.55 against 0.50 is 3.3 σ — the X93 effect is detectable at this n. For the filtered rate:
the filter drops pairs, and the dropped count is reported; if it drops below 1 000 pairs the run is not sensitive and is void by §5.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 1 000 pairs after the filter, or if heredity < 0.35, or if the depth control or the filtered-rate control misses its band.

**The vocabulary is fixed** if the filtered rate reproduces X113c (the X125 diagnosis holds), the depth control holds, and the generation-time mean and median
are both reported with their signs — in that case the published sentence for generation time is the median plus the fraction, and the mean is published as a
tail-dominated quantity with the decomposition that shows why.

**Contradiction** if the mean and the median of the generation-time difference have opposite signs: then the pair statistic and the magnitude statistic
disagree about the direction, no single sentence may be published, and the design must choose by asking which question the claim is about — the typical pair
or the total.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty dense runs |
| readouts | `g` mean/median/fraction/ratio-of-means, `d` mean, `r` filtered mean (+ unfiltered sensitivity) |
| controls | heredity ≥ 0.35; depth reproduces X113; filtered rate reproduces X113c |
| comparison | X93's proportion, recomputed on X108 (not a control) |
| artifact | `E09_pond/l1_field_x125b_statistics.json` |

## Checklist

- [x] connected (1 100+ pairs per cell, both cells)
- [x] positive control numeric (depth and filtered rate reproduce their sources; heredity floor)
- [x] readout exists and varies (X125's lattice interval excludes zero; median resolved to one 10-step quantum)
- [x] sensitivity computed (§4: 41 quanta; SE of a proportion 0.015 at n = 1 100)
- [x] refusal rule written, with mean-vs-median disagreement as a real outcome
- [x] every statistic carries its filter and its unit

## Status

Registered 2026-11-03 03:09 MSK, before the run. No GPU, no new worlds: reads X108's committed logs.
