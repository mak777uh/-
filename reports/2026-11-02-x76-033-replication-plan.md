# X76 — ten worlds at `F = 0.033`: is the weak initial memory of that cell real, or a five-world accident?

**Why.** X75 measured the depth curve at the two band edges. `F = 0.037` came out shallow (half-life 0.56, the shortest in the
table), and `F = 0.033` fell out of its control band with ρ₁ = **0.377** against the registered band `[0.40, 0.60]` — a miss of
0.023, smaller than the spread of the three cells the band came from (0.032). The cell is void by the rule and cannot be relaxed
afterwards. The right response is not to widen the band but to **measure the cell better**: ten worlds instead of five.

If ρ₁ at 0.033 is really ~0.38, then the cell has the weakest initial memory of the five measured, and its shallow decay is
consistent with the mixedness reading: the least mixed edge starts from a weaker memory and loses it fast. If ten worlds move ρ₁
into the band, the void was a sampling accident and the cell joins the table like any other.

## 1. Manipulation is connected

The inflow is the same as X75's `0.033` cell, run with the same protocol; connectedness is the genealogy yield — at least 400
lag-2 pairs pooled (twice X75's 869, because ten worlds instead of five). Nothing is changed except the number of worlds, which is
the point: this is a **replication of one cell**, not a new design.

## 2. Positive control fires

The control fires if **ρ₁ pooled lies in [0.40, 0.60]** — the same band as X75, unchanged. Two secondary numbers are reported
without being gates: the cross-lineage shuffle p95 at each lag, and the per-world ρ₁ spread (a wide spread means the pooled value
is an average of different worlds rather than a property of the cell).

## 3. Readout exists and varies

Identical machinery to X73–X75: Spearman(ancestor peak area, descendant peak area) at lags 1–3, `λ` as the geometric mean of
`ρ₂/ρ₁` and `ρ₃/ρ₂`, half-life `ln 0.5 / ln λ`, cross-lineage shuffle null at every lag.

## 4. Sensitivity arithmetic

Ten runs, 6000 steps, 50-step logging, no fields: X75's five runs at this inflow took 96–110 s each, so ~18 minutes. Five worlds
gave 917 lag-1 pairs; ten should give ~1 800, halving the Fisher band on ρ₁ from ±0.06 to ±0.04. Against a 0.023 miss, that is
the difference between "cannot tell" and "can tell".

## 5. Refusal rule

**Void** if lag-2 pairs are below 400 or the shuffle p95 exceeds 0.10.

**Passes** if pooled ρ₁ ∈ [0.40, 0.60]: the cell is ordinary and X75's void was sampling.
**Confirms the weak memory** if pooled ρ₁ < 0.40 *and* the per-world ρ₁ values are consistent (fewer than two worlds above 0.45):
the cell genuinely starts weaker.
Anything else — ρ₁ inside the band but with two or more worlds outside — is **inconclusive**, reported with the per-world table.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

## Design summary

| factor | value |
|---|---|
| cell | `F = 0.033`, `k = 0.06` (the same cell as X75, replicated) |
| worlds | **10**, `--init-jitter`, seeds 171–180 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every **50** steps, no fields |
| artifact | `morphogenesis/experiments/L1_field/x76_f033_pattern_s171-180.json`, aggregate `l1_field_x76_033.json` |

## Status

Registered 2026-11-02 02:30 MSK, before the series. Ten runs, ~18 minutes.
