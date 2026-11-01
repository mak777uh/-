# X78b: an imposed second scale shortens memory by 1.43× — the right direction, not the full effect

**Date:** 2026-11-02, 04:30 MSK. **Experiment:** X78b (composite two-scale pattern at the robust `F = 0.030` cell).
**Preregistration:** `reports/2026-11-02-x78b-two-scale-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x78b_two_scale_s171-180.json`, fields `_x78b_fields/` (10 snapshots),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x78b_causal.json`.

## The manipulation reached the world

This was the point X78 failed on, so it is checked first and separately.

| check | result |
|---|---|
| world stays patterned | **30.6 components per world** on average (pilot predicted 31) |
| enough genealogies | **1 464 / 1 438 / 1 394** pairs at lags 1–3 |
| composite put **two peaks** into the spectrum | **9 of 10 worlds** carry a maximum near q ≈ 8 and another near q ≈ 11 (12.0 and 8.7 cells) |

The runner's new `--hetero-scale2` / `--hetero-mix2` (off by default, anchored bit-for-bit on `x78_mismatch_s171`) does what it was
added for: it imposes two preferred scales, and the field keeps both.

## The effect

| cell | ρ₁ | ρ₂ | ρ₃ | λ | half-life |
|---|---|---|---|---|---|
| `0.030`, single scale (X74) | 0.507 | 0.304 | 0.198 | 0.625 | **1.47** |
| `0.030`, **two imposed scales** (X78b) | **0.498** | **0.228** | **0.129** | 0.509 | **1.03** |

Lag-1 is unchanged (0.498 against 0.507 — the initial resemblance does not care about the pattern), and the decay is steeper: the
half-life falls from 1.47 to **1.03**, a factor of **1.43**.

## The verdict, and why it is "inconclusive" rather than "supports"

The registered rule required the half-life to be **below 1.0** *and* at least 1.3× shorter. The factor is 1.43 (satisfied), the level
is 1.03 (missed by 0.03). So the registered verdict is **inconclusive**, and the number is reported as it stands rather than rounded
into the supporting band.

The substantive reading is narrower than "the two-scale reading is confirmed" and stronger than "no effect": **an imposed second
scale moves memory in the predicted direction, by about a third, but not to the level of the medium's own multistability**
(0.56–0.73 for `F = 0.033–0.037`). Two candidate explanations, not separated here:

1. **Prescribed ≠ intrinsic.** The composite pattern sets the inflow's spatial structure but the field's own preferred scale still
   dominates the dynamics; a prescribed second scale is a weaker perturbation than the two genuinely competing attractors of the
   band.
2. **The band's shallow memory is partly about the inflow being near a transition** (spot phase vs labyrinth), which the composite
   does not reproduce at `0.030`.

Both predict that the effect should grow as the imposed second scale gets closer to being dynamically competitive — testable by
raising the mix toward 1.0 (which, at `0.040`, killed the world, so the test has a narrow window).

## What this changes

- The two-level statement of §10fa survives with an addition: memory depth is **malleable by prescribing scales**, in the direction
  the mixedness reading predicts, and the malleability is partial.
- The causal handle now exists in the runner (`--hetero-scale2`, `--hetero-mix2`), anchored, so any future world can be given two
  scales on demand.
- The honest formulation for the write-up: "imposing a second scale at a single-scale inflow shortens the memory half-life by a
  factor 1.4, while the medium's own two-scale band shortens it by 2.1–2.5" — an effect in the same direction, of smaller size.

## What this does not say

- It does not show that two scales are the *only* cause inside the band; the band also sits near a phase boundary.
- Ten worlds, one inflow, one composite mix (0.5). The mix axis was not swept; at `0.040` the composite killed the world at every
  amplitude tried, so the sweep window is narrow and must be registered per inflow.
