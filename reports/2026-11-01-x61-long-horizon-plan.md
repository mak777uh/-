# X61-long — is the late concentration the start of selection, or a drift?

1 November 2026, 08:30. Preregistration before the run.

X58-lite left one question open. On the 128 grid the heterogeneous arm was broadband at physical times 2000 and 4000
(entropy 2.05 and 2.30) and then, by 6000, reached peak share 0.38 and entropy 1.97 — just short of the pre-declared
broadband bars. Two readings fit:

- **the start of selection**: the field is slowly concentrating on a mode and would continue, so "no selection" holds only
  for the transient;
- **a drift**: the largest-scale imbalance wanders, and the share hovers without a mode ever winning.

The discriminating variable is **time**, not grid. This run quadruples the horizon at the cheaper 96 grid, keeping
everything else identical to the `a50` arm of X59.

## 1. Manipulation is connected

Nothing is manipulated: this is the same world run longer. The check that the run is the same world is that its first
6000 steps must reproduce `x59_a50_s171` **bit-for-bit** — same command, longer horizon, so the prefix must match.

## 2. Positive control fires

The control here is the **early window of the same run**: at t = 6000 the arm must show what X59 showed —
splits in the hundreds (308 for `a50`) and entropy ≈ 2.27. If the long run does not reproduce its own beginning, the run
is not comparable to the series it extends.

## 3. Readout exists and varies

- **Readouts:** spectral entropy and peak share at t = 6000, 12 000, 18 000, 24 000 (fields saved at those steps);
  `splits`, `components`, `s_mean_last` at the end.
- **Observed at 96/6000:** peak share 0.25, entropy 2.27; at 128/6000: 0.41 and 1.68. The readout varies across time and
  grid, so a monotone trend over four points would be visible.

## 4. Sensitivity arithmetic

Five seeds, seed-averaged spectra, no p-values. The two readings are separated by a **direction over four points**:

- selection ⇒ peak share rises monotonically and passes **0.5**, entropy falls below **1.8**;
- drift ⇒ peak share stays within **0.35–0.45** with no monotone rise, entropy stays **≥ 1.9**.

The criterion is the conjunction of the two signs at the last point plus monotonicity over at least three of the four
times, not a threshold on a single number.

## 5. Refusal rule

Worthless, not negative, if:

1. the first 6000 steps do not reproduce `x59_a50_s171` (different world, not a longer one);
2. the field dies before 24 000 steps (components 0 in most seeds);
3. the peak mode jumps between unrelated q across the four times — then there is no single mode to follow and the
   question is malformed for this world.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, **24 000 steps**, `Du = 0.16`, `Dv = 0.08`, `F = 0.035`, `k = 0.06`, `beta = 0.2`, `freq_dep = 1`, mutation 0.15, `eps = 0`, hetero amp 0.5, scale 12 |
| arms | one (the `a50` world), five seeds |
| fields | saved at steps 6000, 12000, 18000, 24000 |
| criterion | §4 |
| cost | ≈ 340 s per run, 5 runs ≈ 30 min |
| artifacts | `morphogenesis/experiments/L1_field/x61l_a50_s*.json`, `x61l_fields/` |

## Status

- [x] connected (same command, longer horizon; prefix must match `x59_a50_s171`)
- [x] positive control fires (early window reproduces X59: hundreds of splits, entropy ≈ 2.27)
- [x] readout exists and varies (peak 0.25–0.41, entropy 1.68–2.27 across worlds)
- [x] sensitivity computed (direction over four points, two-sign criterion)
- [x] refusal rule written (three conditions)
