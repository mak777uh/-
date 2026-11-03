# X125 — void by its own control, and the two corrections it forces on X124

**Plan:** [`2026-11-03-x125-definitions-plan.md`](2026-11-03-x125-definitions-plan.md) (03:04).
**Aggregate:** `l1_field_x125_definitions.json`.

## What the audit was for

X124 named two contradictions in the line's vocabulary: "rate" differing by an order of magnitude between X113c (6.06 / 18.96) and X124 (36.6 / 321.5), and
"generation time" being a raw difference in one place and a share in another. X125 was to state one definition per quantity and recompute both.

## What happened

The engine ran and the registered control fired:

| cell | pairs | generation time (larger − smaller) | share `g_big/g_small` | depth | rate, pair-weighted | rate, "uid-weighted" | X113c's rate |
|---|---|---|---|---|---|---|---|
| 0.030 | 1 142 | −412.4 (CI −514.8…−310.3) | 12.00 | +1.479 | +36.6 | +18.3 | +6.06 |
| 0.040 | 1 195 | −28.2 (CI −59.8…4.0) | 13.74 | +2.213 | +321.5 | +160.7 | +18.96 |

Control 2 required the rate to reproduce X113c within 10 %; it misses by a factor of three and eight. **Void.** The void is worth more than the result would
have been, because it produced three corrections — and the first one is to X124's own diagnosis.

## 1. X124's diagnosis was wrong: the rate difference is a filter, not a weighting

The X124 void said "X113c computed the formula per uid and took the mean over all uids; this audit computes it per sister pair — the first weights uids, the
second weights pairs". Reading `x113c_analyse.py` back: `rate_diff` is accumulated **inside the sister-pair loop** and averaged over pairs. X113c is
pair-weighted, exactly like X124. The two numbers differ by an order of magnitude for a different reason:

> X113c skips a pair unless **both** sisters' generation times are ≥ 50 steps (`MIN_LIFE`); X124 and X125 have no such filter.

Without the filter, a uid that lives three logging steps has `rate = d/3 × 1000`, and a handful of those dominate two thousand pairs. So the "order of
magnitude" was the denominator's lower tail, not the unit of aggregation. The line's own vocabulary was the smaller half of the problem; a silent sample
restriction was the larger half. **A filter is part of a definition, and a definition that is not printed is not a definition** — new rule in
[`docs/design-checks.md`](../docs/design-checks.md): *a filtered statistic names its filter in the same sentence as the number*.

My "uid-weighted" column above is a third quantity again — the mean over uids of the signed rates, which by symmetry is half the unfiltered pair contrast
(18.286 = 36.571/2). It equals no published number and should never have been called a check of one. The plan's control was mis-specified in the same way the
X124 void was: it asked a uid-level statistic to reproduce a pair-level one.

## 2. X93's "+0.05" is a proportion of pairs, not a share of the mean

`§10fq` reads: "larger sister lives longer **0.553**, cross-family control 0.502, difference **+0.050**, z 4.68" — with 1 978 pairs. 0.053 / sqrt(0.25/1978) = 4.7,
so the quantity is the **fraction of pairs in which the larger sister's generation time is longer**, compared against a cross-family control fraction. It is
not a share of the pair's mean, and X124/X125 both described it as one.

That changes the status of the X124 "contradiction" completely. A fraction of 0.553 and a mean difference of −412 steps are **compatible**: the majority of
pairs can favour the larger sister while a minority with very large negative differences pulls the mean the other way. Nothing in the medium is inconsistent;
the mean and the majority are different questions.

## 3. The mean-of-ratios is unusable and is withdrawn

`share = g_big/g_small` averaged over pairs gives 12.0 and 13.7 — meaningless, because the denominator approaches zero for short-lived uids. Any "share" of
generation time must be a ratio of means or a median of ratios, never a mean of ratios, and it must carry its filter.

## What survives

- The definitions themselves are unchanged and still right: generation time in logged steps, depth in generations, rate `d/g × 1000`.
- The depth contrast reproduces X113 exactly (+1.479 / +2.213, both intervals inside 10 %): the depth leg was never definition-bound.
- The generation-time mean difference reproduces X124 (−412.4 against −412.4): the engine is the same arithmetic.

## What this means for the manuscript

Until X125b lands, the consequence claims cite **depth** (unaffected, reproduced) and cite the generation-time and rate results only as *directions with
their statistic named*. The X124 void's own diagnosis paragraph is left in place — this report corrects it, it does not rewrite it.

Amendment registered as **X125b**: the filter printed with every rate, the four statistics of a paired difference (mean, median, fraction of pairs, ratio of
means) reported side by side, and X93's proportion recomputed on X108's pairs as a comparison across series rather than as a control.

## Caveats

- One seed set (X108's twenty runs), one box, the 0.20 cut.
- Generation times are quantised at 10 steps; a 412-step difference is 41 quanta.
- X93's series is not X108, so its 0.553 is a comparison, not a replication.

доска: принято 0, отклонено 0, отложено 0.
