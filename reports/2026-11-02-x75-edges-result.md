# X75: one band edge is shallow, the other falls out of its own control band — inconclusive by the registered rule

**Date:** 2026-11-02, 02:20 MSK. **Experiment:** X75 (depth curves at the multistable band edges).
**Preregistration:** `reports/2026-11-02-x75-edges-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x75_f0{33,37}_pattern_s171-175.json`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x75_edges.json`.

## Result

| cell | pairs (1/2/3) | ρ₁ | ρ₂ | ρ₃ | shuffle p95 | λ | half-life | registered check |
|---|---|---|---|---|---|---|---|---|
| **0.033** | 917 / 869 / 812 | **0.377** | 0.038 | 0.053 | 0.045 | 0.375 | (0.71) | **void**: ρ₁ below the 0.40 band |
| **0.037** | 1 080 / 996 / 882 | 0.456 | 0.192 | 0.039 | 0.052 | 0.292 | **0.56** | passes |
| 0.030 (X74) | 1 166 / 1 091 / 1 037 | 0.507 | 0.304 | 0.198 | 0.044 | 0.625 | 1.47 | — |
| 0.035 (X74) | 2 140 / 1 968 / 1 776 | 0.475 | 0.204 | 0.072 | 0.036 | 0.389 | 0.73 | — |
| 0.040 (X74) | 970 / 887 / 795 | 0.486 | 0.278 | 0.205 | 0.055 | 0.649 | 1.61 | — |

The registered verdict is **inconclusive**: `0.037` is shallow (half-life 0.56, the shortest in the whole table) while `0.033` fails
its control band by 0.023 and is void.

## What the numbers say anyway, and why they do not become a claim

The one usable edge supports the mixedness reading: at `0.037`, where X71c measured 4 of 5 worlds mixed, the half-life is
**0.56** — half the outer neighbours' 1.47 and 1.61, and shorter than the boundary cell's own 0.73. The other edge, `0.033`,
where X71c measured only 3 of 5 mixed, has ρ₁ = **0.377** and decays fast too (0.71), but 0.377 sits 0.023 below the band
`[0.40, 0.60]` that I fixed in advance from three cells.

Two things are true and neither is a licence to relax the rule after seeing the data:

- the deviation is small (0.023) relative to the spread of the three cells the band came from (0.475–0.507, spread 0.032) — so
  the band was tight by construction and the miss is within its own noise;
- but relaxing a control band because one cell missed it is exactly the move the line forbids. The cell stays void.

The substantive reading is therefore: **one edge is shallow and consistent with "mixedness makes memory short"; the other edge
cannot be judged with this protocol.** The pattern across the five cells is monotone in mixedness rather than in `F` — 0.030 (not
mixed) 1.47, 0.040 (not mixed) 1.61, 0.035 (mixed 5/5) 0.73, 0.037 (mixed 4/5) 0.56, 0.033 (mixed 3/5) — the last one being the
exception that fell out of its control band, and also the least mixed, which is the direction the mixedness reading predicts: less
mixed, weaker initial memory (ρ₁ 0.377 against 0.456).

## What would settle it

- **More worlds at 0.033**, not a wider band: ten worlds instead of five would tighten ρ₁'s estimate and show whether 0.377 is
  the cell's true value or a five-world accident. That is ~20 minutes.
- **Or the same measurement at 0.031 and 0.039** — cells that should be *less* mixed than the edges and *more* than 0.030/0.040.
  If their half-lives interpolate between 0.56 and 1.5 in the order of mixedness, the reading is confirmed without touching the
  control band.

## Honest summary

X75 does not confirm the surviving explanation and does not refute it. It adds one clean point (0.037 → 0.56) that points the
way the explanation predicts, and one void cell whose control miss is small enough to be interesting and large enough to matter.
Reported as inconclusive, with the next design already named.
