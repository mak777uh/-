# X124 — void by its own control, and it found two inconsistencies the block must fix

**Plan:** [`2026-11-03-x124-coherence-plan.md`](2026-11-03-x124-coherence-plan.md) (02:47).
**Aggregate:** `l1_field_x124_coherence.json`.

## What the audit was for

X93 says the larger sister's **generation time** is longer; X113/X114 say her **lineage** reaches more generations per unit time. A longer denominator should
lower the rate unless depth grows faster, so the three numbers have to be mutually consistent. The audit was arithmetic on the same pairs.

## What it found instead

| cell | pairs | generation-time difference (larger − smaller) | depth difference | rate difference (recomputed) | X113c's rate | implied rate ratio |
|---|---|---|---|---|---|---|
| 0.030 | 1 142 | **−412.4 steps** (CI −517.9…−310.4) | +1.479 (CI 1.295…1.666) | **+36.6** (CI −6.9…78.1) | +6.06 | 0.253 |
| 0.040 | 1 195 | −28.2 steps (CI −60.4…6.9) | +2.213 (CI 1.959…2.475) | **+321.5** (CI 228.8…417.3) | +18.96 | 0.038 |

The registered control fired: the recomputed rate misses X113c's value by a factor of six and seventeen, so **the audit is void**. But the void is informative
twice over:

1. **The rate has two definitions.** X113c computed `depth / generation time × 1000` per uid and then took the mean of the *difference over all uids*; this audit
   computes the same formula per sister pair. Those are not the same contrast — the first weights uids, the second weights pairs, and the two disagree by an order
   of magnitude. The line has one word ("rate") for at least two quantities.
2. **X93's sign does not reproduce under a raw difference.** Here the larger sister's generation time is **shorter** by 412 steps with an interval excluding zero,
   while X93 reported a share advantage of +0.05 to +0.08 for the larger sister's lifetime. A *share* and a *raw difference* can disagree in sign when the sisters'
   sizes differ, but the line quotes X93 as if "the larger sister lives longer" were the raw statement.

Neither point is a contradiction of the medium; both are contradictions of the line's own vocabulary, and they are exactly what a coherence audit is for.

## What this means for the manuscript

Before any of these numbers travels, one definition of each of the three quantities has to be fixed and the affected aggregates recomputed with it:

| quantity | the two readings now in use |
|---|---|
| generation time | uid last − first (raw steps) **or** as a share of the pair's mean |
| rate | per-uid mean of `depth / generation time` **or** per-pair contrast of the same formula |
| depth | subtree generations, uncompressed — consistent everywhere |

Registered as X125: state the three definitions once, recompute X93's and X113c's numbers under the stated ones, and mark every old number with the definition it
used. Until then, the consequence claims cite **directions** (the larger sister's line goes deeper, and reaches generations faster) and not magnitudes.

## Caveats

- The audit's own numbers are not claims: it is void, and its rate column is a third definition, not a correction.
- Generation times are quantised by the 10-step logging interval, so a 412-step difference is 41 logging units — well above quantisation.
- One seed set, one box, the 0.20 cut.

доска: принято 0, отклочено 0, отложено 0.
