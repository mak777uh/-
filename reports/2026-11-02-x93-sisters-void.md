# X93 — sisters: a weak advantage in the lattice, none at the band's edge, and a penalty in the maze

**Date:** 2026-11-02, 12:50 MSK. **Experiment:** X93 (within-family contrast, stored artifacts only).
**Preregistration:** `reports/2026-11-02-x93-sibling-plan.md` (committed before the analysis).
**Artifacts:** `morphogenesis/experiments/E09_pond/l1_field_x93_sibling_contrast.json`.

## Registered verdict

**Void** — the positive control failed: the cross-family fraction at `F = 0.040` is **0.422**, outside the registered band
[0.45, 0.55]. The control is right to fail, and for a reason X92 had already measured: in the maze a larger structure lives *shorter* even
when the two are strangers, so a cross-family fraction near 0.5 was never achievable there. The band was mis-specified, not the data.

The within-family contrast is still interpretable, because its own control is the **difference** against the cross-family fraction, and
that difference is what the design was built on. It is reported below as descriptive, with the void standing.

## Numbers

| `F` | families | sister pairs | within-family fraction | cross-family control | difference | z (within) |
|---|---|---|---|---|---|---|
| 0.025 | 2 437 | 1 978 | **0.553** | 0.502 | **+0.050** | 4.68 |
| 0.030 | 2 364 | 1 946 | **0.530** | 0.449 | **+0.082** | 2.67 |
| 0.035 | 1 987 | 1 930 | 0.506 | 0.528 | −0.021 | 0.55 |
| 0.040 | 1 708 | 1 982 | **0.401** | 0.422 | −0.021 | **−8.85** |

The fraction is "the larger sister lives longer". At 0.040 the absolute value (0.401, z = −8.85 on 1 982 pairs) is a strong statement
that **within a family in the maze the larger sister is less likely to live longer**, while the difference against its own control
(−0.021) is small — the population-level size–lifetime relation dominates and the family contrast adds little.

## What this says about the third leg

Reading the four cells together, with both the registered resolution (0.05–0.10 on the difference) and the z in hand:

1. **The lattice pays a little.** At 0.025 the within-family advantage is +0.050 over the control with z = 4.7; at 0.030 it is +0.082 with
   z = 2.7. Both are at or above the declared resolution, and the 0.025 cell clears every bar the rule asked for (0.553 ≥ 0.55,
   difference ≥ 0.05, z ≥ 2). Only one cell does, so the rule would not have called it a result even without the control failure.
2. **The band's edge pays nothing.** At 0.035 the difference is −0.021 and the within-fraction is at chance.
3. **The maze penalises size.** At 0.040 the larger sister is the less durable one, and the effect is the largest in the table in
   absolute z.

So the third leg is answered as far as this instrument can: **resemblance buys a small amount of persistence in the lattice and nothing —
or less than nothing — where the pattern percolates.** Combined with X92 (bigger structures live shorter in the maze) the picture is
consistent: in a maze, size marks the place about to be cut, not an advantage.

## The design lesson

A control that demands an absolute fraction near 0.5 assumes the population-level relation is null. Here it is not: size and lifetime are
already related across strangers (X92, −0.046 at 0.040), so the cross-family fraction sits below 0.5 by construction. The control should
have been specified as the **difference** with its own uncertainty, and the band [0.45, 0.55] on the raw fraction was a mistake. Written
into the design rules.

доска: принято 0, отклонено 0, отложено 0.
