# X68 on real worlds: the lifetime reversal holds at loose overlap, mostly at medium, and **not** at strict overlap

**Date:** 2026-11-01, 17:20 MSK. **Experiment:** X68 (identity rule sensitivity in the neutral world), replicated.
**Artifacts:** `morphogenesis/experiments/L1_field/x68r_{ov03,ov05,ov07}_{pattern,homog}_s171-175.json` (30 runs),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x68r_identity.json`.
**Runner:** `scripts/x68r_series.py`; analysis `scripts/x68r_analyse.py --write`.

## Why it was rerun

X68 lives in the neutral world (`beta = 0`, `eps = 0`), and in that world the seed does not move the geometry: the starting
blob is fixed and the seed only feeds the trait channel. The `lifetimes` blocks of the five seeds are byte-identical, so
"0/5 seeds" in the X68 report meant *one world disagreeing with the prediction*, not five. The rerun keeps the measurement
and changes only the replication route: `--init-jitter` moves the starting blob by the seed and varies its radius by ±20 %.
Positive control per rule: five distinct geometries in the heterogeneous arm (5/5); in the homogeneous arm 4/5, because a
homogeneous world can converge from two different starts onto the same dynamics — recorded, not hidden.

## Result, per world

Lifetimes are measured on the uid timeline (median over uids, `lifetimes.median_life_steps`), exactly as in X68.

| rule | hetero medians (5 worlds) | homog medians (5 worlds) | direction | worlds |
|---|---|---|---|---|
| 0.3 loose | 5999, 5999, 5999, 5999, 5999 | 2846, 3985, 4030, 3985, 3091 | hetero **longer** | **5/5** |
| 0.5 medium | 4400, 4505, 5999, 3777, 5999 | 2846, 3985, 1565, 3985, 2713 | hetero longer | **4/5** |
| 0.7 strict | 871, 1128, 1417, 1118, 712 | 2846, 3985, 1565, 3985, 2713 | hetero **shorter** | **5/5** |

uid counts explain the shape. At the loose cutoff the heterogeneous world runs as **one** lineage for the whole horizon
(1 uid, median at the 5999-step ceiling); at the strict cutoff the same world fragments into 35–66 uids, because an edge
that loses a fifth of its overlap is re-identified as a new component. The homogeneous arm moves much less (2–5 uids).

## What this corrects

The X68 report said the reversal — heterogeneous components living *longer* than homogeneous ones, opposite to the
published feedback-regime number — holds at **all three** rules with 5/5 seeds. On real worlds it holds at the loose rule
(5/5, unanimous), holds in four of five worlds at the medium rule, and **reverses back at the strict rule** (5/5
unanimous): there heterogeneous components live 712–1417 steps against 1565–3985 for homogeneous ones, which is the
direction of the original published contrast.

The old single world happened to sit at 2607 against 1565 at the strict cutoff and looked like a reversal; it was one
draw of the starting blob among five, and two of the five real worlds are below the homogeneous arm by a factor of two and
more. So the sentence "the ordering reverses at all three rules" is withdrawn, and what replaces it is narrower and more
useful: **the direction of the lifetime contrast is a property of the identity rule**, and the rule moves it monotonically
from "heterogeneous lives longer" (loose) through a split verdict (medium) to "heterogeneous lives shorter" (strict).

## What this does not say

- It does not return to the published 57 against 4046. That contrast was measured in the feedback regime; here there is no
  feedback, and the strict-rule numbers (712–1417 against 1565–3985) still differ from the published ones in magnitude.
- The homogeneous arm converges from two of five starts; its geometry is less seed-sensitive, so its five worlds are
  really four and a duplicate. That is stated rather than corrected by more runs.
- Lifetimes remain threshold-, rule- and horizon-bound: the loose arm's 5999 is the horizon, not a measured lifetime.

## Next

1. The strict-rule fragmentation (35–66 uids, lifetimes of a few hundred steps) is the first place where the identity rule
   visibly manufactures entities. A dedicated run at the strict cutoff with `--split-new-uid` would separate "edges lose
   overlap" from "genuine division", which decides whether the short lifetimes are physics or bookkeeping.
2. The synthesis sentence about lifetimes now needs the rule named for every number; done in the same commit.
3. X70 taught the general lesson (a neutral world ignores its seed); X68 is the first arm repaired by it, and the blast
   radius table in [`2026-11-01-x70-two-design-defects.md`](2026-11-01-x70-two-design-defects.md) is updated to say so.
