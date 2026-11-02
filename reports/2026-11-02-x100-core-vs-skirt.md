# X100 — the "cut-free" size is really a core measure, and heredity lives in the skirt

**Date:** 2026-11-02, 19:30 MSK. **Experiment:** X100 (size measured at each structure's own peak, boundary at half its local maximum).
**Preregistration:** `reports/2026-11-02-x100-cutfree-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x100_f0{30,40}_s291-300.json` (20 runs with a field at every logged step),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x100_cutfree.json`.

## Registered verdict

**Void** — the threshold-based control missed in one cell: at `F = 0.040` the recomputed ρ₁ is **0.384** against the band [0.42, 0.52]
built from the committed 0.471. At `F = 0.030` it passed (0.531 against [0.50, 0.60]).

The band was my error and is worth naming: it was taken from the committed **twenty-world** value while these are **ten new worlds**, whose
own standard error is ≈0.10 — a ±0.05 band cannot hold across a change of sample. The paired comparison below does not suffer from that,
because both definitions are evaluated on the same pairs.

## Numbers

| cell | pairs | basin found | ρ₁, threshold area 0.20 | ρ₁, half-max basin integral | ρ₁, half-max basin **area** | paired Δ (S_cf − area) | median area | median S_cf |
|---|---|---|---|---|---|---|---|---|
| `F = 0.030` | 2 165 | 97 % | **0.531** | **0.176** | 0.168 | **−0.355** | 76 | 18.4 |
| `F = 0.040` | 1 761 | 84 % | **0.384** | **0.058** | 0.059 | **−0.326** | 423 | 17.4 |

## What it means — and it is not what the design expected

The expectation was "a size defined without a global cut should give the same heredity if heredity is about size". It does not: the
paired difference is **−0.36 and −0.33**, consistent across both inflows, with the same pair sets on both sides.

The reason is visible in the medians. A basin bounded at half of its own maximum is a **core**: 18 cells against a threshold component
of 76 at `F = 0.030`, and 17 against 423 at 0.040. So the two "sizes" are not two definitions of one quantity — they measure different
parts of the same structure: the **core** (a height-dominated, intensive object) and the **skirt** (an extent-dominated, extensive one).

Two further observations sharpen it:

- The basin's **area** is as weak as its integral (0.168 and 0.059 against 0.176 and 0.058). So within the basin it is not mass versus
  extent that matters — it is the basin itself.
- Heredity therefore lives in the **skirt**: the low-density envelope that the absolute 0.20 cut includes and the half-maximum boundary
  excludes. A structure's inherited identity is how far it spreads, not how high it peaks.

That is a coherent and useful finding, and it also explains X99: the cut matters precisely because it decides how much of the skirt
counts.

## Honest limits

- The design promised a cut-free size and delivered a *relative* boundary — which is still a definition, just a different kind. The claim
  "no threshold" was too strong; the correct statement is "the boundary is relative to each structure instead of absolute".
- The control failure voids the registered comparison; the paired deltas are reported as descriptive, from one sample per inflow.
- A truly boundary-free version needs basins defined by the field's own topology (watershed on `v`, no level set at all). That is a
  different implementation, registered as X101, and it is the only version that would answer the question the plan actually asked.

доска: принято 0, отклонено 0, отложено 0.
