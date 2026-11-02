# X86 — the symmetry curve is placed: 0.42 / 0.67 / 0.85 at `F` = 0.025 / 0.030 / 0.035

**Date:** 2026-11-02, 06:45 MSK. **Experiment:** X86 (sixty worlds, three inflows, one logging regime).
**Preregistration:** `reports/2026-11-02-x86-symmetry-curve-plan.md` (committed before the run).
**Artifacts:** `morphogenesis/experiments/L1_field/x86_f0{25,30,35}_pattern_s201-220.json` (60 runs), fields `_x86_fields/`,
aggregate `morphogenesis/experiments/E09_pond/l1_field_x86_symmetry_curve.json`.

## Result

Twenty jittered worlds per inflow, all at `--sample-every 50` (the X82/X85 regime), 6000 steps, field saved at 6000.

| `F` | symmetry `s`, median | IQR | sd | range | SE of the median | axis period `q'` |
|---|---|---|---|---|---|---|
| 0.025 | **0.421** | 0.365–0.609 | 0.138 | 0.325–0.766 | 0.031 | 4, 5, 6, 7, 8 |
| 0.030 | **0.674** | 0.519–0.762 | 0.163 | 0.301–0.818 | 0.036 | 8, 9, 10 |
| 0.035 | **0.848** | 0.778–0.880 | 0.110 | 0.435–0.901 | 0.025 | 7, 8, 9 |

**Verdict: curve placed.** The preregistered positive control fired — the medians are ordered and the 0.025→0.035 gap is **0.427**
against a required 0.15 — and both adjacent steps exceed the declared resolution: **+0.253** (0.025 → 0.030, 5.3σ) and
**+0.174** (0.030 → 0.035, 3.9σ).

The 0.030 value independently corroborates X85's 0.671 measured on eight different worlds (seeds 191–198): 0.674 against 0.671. That is
a replication to three hundredths across two series in the same regime, and it is the strongest statement this aggregate supports
about reproducibility — earlier guesses at the level differed by 0.07, that difference was mostly the small samples.

## The one number in the plan that was too optimistic

The sensitivity arithmetic assumed `sd(s)` = 0.07–0.10 from X85's eight worlds and predicted a standard error of 0.016–0.022. With
twenty worlds the observed `sd` is **0.110–0.163**, so the standard error is **0.025–0.036** and the resolution is **≈0.08**, not
0.05. Both registered steps clear it, but the plan's resolution claim was off by a factor of two and is corrected here.

The spread itself is a fact about the world: `s` varies by ±0.15 between worlds that differ only in their initial jitter. A cell's
median needs ~25 worlds to be pinned to ±0.03.

## The secondary readout is not available, and the reason is structural

The plan expected these worlds to serve the heredity question later "without a new run". They cannot: `--split-new-uid` is off (X71's
identity convention, chosen so the symmetry numbers match X71's), and without it the identity tracker keeps **4–7 uids** per run and
`uid_pairs` is **empty** — X71 has exactly the same 0 pairs, which is why X71 never measured heredity either. With the split
convention the same runs give 209–250 pairs (X74, X85).

So the registered refusal rule, which required ≥400 lag-1 pairs, would have voided the series over a readout the series was never
able to produce. The two readouts are separated in the aggregate: the curve is judged on its own gate and **passes**; the memory
readout is declared unavailable with its cause. This is a defect in the preregistration, not in the run, and it is recorded as such.

## What this changes

1. **`s` is now a usable x-axis**: 0.42 / 0.67 / 0.85 with standard errors 0.03, 0.04, 0.03 for the three inflows. Every memory number
   in this line can be quoted against it with its regime named.
2. **The period is not per-world constant.** X86's `q'` spans 4–10 bins (9.6–24 cells) and at `F = 0.025` several worlds are coarse
   (19–24 cells). None is 11, so the X84 refutation of the "8.7-cell branch" stands, but "one period ≈ 12 cells" is a **median**
   statement with real spread, and X84's review said 5–9 where the 50-step regime gives 4–10.
3. **A series serves only the readouts its identity convention allows.** This is now the second such lesson from the same flag
   (`--sample-every` was the first): both are physical/analytical parameters that must be chosen for *every* question the series will
   be asked, not just the primary one.

## Next, and it needs new worlds

The memory-versus-symmetry question can only be asked on worlds that have both readouts. X85's 24 worlds have both (split on, 50-step)
and gave within-cell coefficients of −0.33 / −0.25 / −0.02 with a pooled partial correlation of 0.00 — underpowered, not decisive.
Bringing those cells to twenty worlds each costs **36 runs** (~55 minutes, seeds 221–232) and answers it at the precision the curve
now has.

доска: принято 0, отклонено 0, отложено 0.
