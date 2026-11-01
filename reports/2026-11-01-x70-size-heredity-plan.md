# X70 — does the medium carry size heredity on its own?

1 November 2026, 15:12. Preregistration before the run.

Our published heritability (r = 0.97) is the copying rule talking: a daughter's composition is assigned from its parent's
plus noise. The medium itself is a continuous field, so the only thing it can genuinely transmit is **material state and
geometry**. This run measures the smallest honest version of that: does a daughter structure's **peak area** resemble its
parent's, in a world with no imposed trait channel at all?

Two observer facts make the question answerable, and both were added today:

- `--split-new-uid` gives daughters **their own identities** at a split. Without it, parent and daughter share a uid and
  their peak areas are inseparable — the first attempt at this measurement (preliminary correlation 0.32) was confounded
  exactly that way.
- `size_pairs` and `uid_pairs` record, per division event, the parent's and daughter's areas **and** their uids, and
  `uid_outcomes` carries each uid's peak area, so peak-to-peak comparison is now possible.

## The measurement

For every division event where both parent and daughter have a recorded peak area, compute the correlation and the
regression slope of **daughter peak area on parent peak area**, pooled across seeds within an arm.

## Prediction, written before the data

- **Medium carries heredity:** correlation ≥ 0.5 and slope ≥ 0.6 — a daughter's size is mostly determined by its parent's.
- **Regression to the medium's scale:** correlation < 0.3 or slope < 0.5 — sizes are reset by the dynamics, and the medium
  has no size lineage.
- **Intermediate:** anything else, reported as such.

The second outcome is what the preliminary single-seed pass suggests (0.32 and 0.37, confounded), and it would be a real
result: the pattern reconstructs itself at its own preferred scale, and a structure's size is a property of the medium
rather than of its ancestry.

## 1. Manipulation is connected

This is not a manipulated experiment: the world is neutral (`beta = 0`, `eps = 0`), so composition cannot feed back and the
field is identical across identity rules. The observer change (`--split-new-uid`) was anchored before this run: with the
flag off, `series` reproduce the existing artifact **bit-for-bit**.

## 2. Positive control fires

The division events must exist in quantity: at least **50 division events per arm** pooled over five seeds, otherwise the
correlation is not estimable. (The anchor run produced 185 events on a single seed, so the control should fire easily.)

## 3. Readout exists and varies

Peak areas across uids must span at least a factor of three (the anchor run: 108 to 452 cells).

## 4. Sensitivity arithmetic

Five seeds per arm, pooled events, no p-values: the criterion is a **correlation and a slope**, both reported with their
event count. With ~200 events per arm, a null correlation has a standard error near 0.07, so the 0.3 / 0.5 bands are
distinguishable.

## 5. Refusal rule

Worthless, not negative, if:

1. fewer than 50 division events per arm;
2. fewer than 30 events where **both** parent and daughter have a peak area recorded (the uid link can fail when the parent
   dies in the same step);
3. peak areas are identical across all uids (a broken reader).

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, **`beta = 0`, `eps = 0`** (no trait feedback), mutation 0.15 |
| arms | heterogeneous (amp 0.5) and homogeneous (amp 0.0) |
| seeds | 171–175 |
| observer | `--split-new-uid --overlap 0.5` |
| readout | correlation and slope of daughter peak area on parent peak area, per arm |
| criterion | §4 |
| cost | 10 runs ≈ 20 min |
| artifacts | `morphogenesis/experiments/L1_field/x70_{pattern,homog}_s*.json` |

## Status

- [x] connected (neutral world; the observer change is anchored bit-for-bit with the flag off)
- [x] positive control fires (185 events on one seed)
- [x] readout exists and varies (peak areas 108–452 cells)
- [x] sensitivity computed (bands 0.3 / 0.5, ~200 events, standard error near 0.07)
- [x] refusal rule written (three conditions)
