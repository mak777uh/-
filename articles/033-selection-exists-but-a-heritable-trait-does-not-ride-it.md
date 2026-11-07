# 033: Selection exists, but a heritable trait does not ride it — a negative result

- **Type:** research article (short format, one result: a negative one)
- **Version:** v2.0 — **rewritten after the independent referee verdict "does not hold" on v1.0**
- **Date:** 2026-11-07
- **Status:** draft; not deposited
- **Authors:** Ilya Vladimirov
- **Previous article of the series:** [032](032-what-decides-whether-behaviour-pays.md)
- **Artifacts:** `morphogenesis/experiments/E09_pond/s{55,58,63,64,65,66,67,85,86}_*.json`
- **Review of v1.0:** `lab/reviews/2026-11-07-033-independent.md`

## Corrections in this version

v1.0 claimed four positive findings. The independent referee recomputed every number from the raw
artifacts and returned "does not hold", with thirteen specific findings. This version applies them:

1. **"Paired design" removed from the text.** The referee read the code and showed that every arm already
   created its own generator with the same seed, so the "pairing fix" changed nothing. The word is gone.
2. **Statistics withdrawn.** Paired t over ten seeds was 1.15 (p = 0.28) and the sign test 8/10 (p = 0.109).
   The signal claim is now reported as **not shown**, not as a result.
3. **"The mechanism is the lead" withdrawn.** The lag sweep is non-monotone (0: −0.011, 2: −0.001,
   5: −0.011, 10: +0.012), so a lead cannot be the mechanism.
4. **"Properties matter only in the poor zone" corrected.** The rich-zone energy differential is +0.061 at
   SE 0.0101, i.e. z ≈ 6.0 — weaker by a factor of 2.8, not absent.
5. **The trait shift is reported as not distinguishable from drift**, with the referee's numbers.
6. **`s66` is now reported**: the rich zone with a tenfold stronger effect shifts 8× harder, which
   contradicts the v1.0 headline and is the reason the headline is withdrawn.
7. **The "1:30" ratio is removed** — it compared the mean trait with its spread, two different quantities.
8. **"Strong selection" is reworded**: the numbers are quartile differences in the probability of
   surviving, not selection coefficients.

## The line this article continues

Article 032 ended with a limit: a cell that moves 0.14 cells per lifetime cannot use long-range
information, so the amount it moves matters more than the signal it follows. That leaves a prior question.
**Is there anything in this world to select on at all?** If there is, **can a heritable trait ride it?**
This article answers by measuring what the world already contains, and it reports a negative answer to the
second half.

**Keywords:** selection, heritability, environment, negative result, boundary of the setup

## 1. What was measured

**The world.** Unchanged: a 32×32 grid, resource in the cells, organisms with energy, proportional income,
death at zero energy, reproduction on accumulated mass. R1 (mean deaths ≥ 10 and mean living ≥ 10) holds in
every run cited here.

**The quantities.** For every living cell: its age (how many steps it has lived), its local density (living
cells within Chebyshev radius 2), its energy, and whether it stands in the top half of cells by current
resource. For each, the probability of surviving a 20-step horizon is compared between the low and the high
quartile. The difference is a **quartile difference in the probability of surviving** — not a selection
coefficient.

## 2. There is a great deal to select on

| quantity | P(survive): low → high quartile | P(divide): low → high |
|---|---|---|
| energy | 0.551 → 0.686 (**+0.135**) | 0.964 → 0.530 (**−0.434**) |
| age | 0.560 → 0.667 (**+0.106**) | 0.926 → 0.620 (**−0.306**) |
| density | 0.550 → 0.654 (+0.104) | 0.875 → 0.744 (−0.131) |
| richness of the cell | 0.580 → 0.621 (+0.041) | 0.880 → 0.752 (−0.128) |

Replicated on ten fresh seeds: every differential reproduced within 0.02 (energy +0.135 → +0.154, age
+0.106 → +0.113), on 754 observations. **The world discriminates strongly, on energy and age.**

## 3. A heritable trait does not ride it

Five designs were tried. Three produced data; two produced none worth reporting, and are listed as such.

| attempt | how the trait acted | data | outcome |
|---|---|---|---|
| energy bonus, effect 0.5 | added energy each step | 1 seed, 300 steps | probe only — not evidence |
| energy bonus, effect 5.0 | ten times stronger | 1 seed, 300 steps | probe only — not evidence |
| division threshold 24 | set the threshold | 5 seeds | **9 divisions in both arms** — insensitive by construction |
| division threshold 8 | same, lower | 5 seeds | 148/147 divisions; trait drifted |
| trait inside the upkeep rule | changed the energy spent | 5 seeds | trait drifted |

Over five seeds the mean trait alternated sign (−0.0001, +0.0001, −0.0005, +0.0004, −0.0002, −0.0011).
**This is drift, not selection.**

**The trait shift is not distinguishable from drift.** For the poor-centre planting (see §4) the last
window mean is −0.000527 with a between-seed standard deviation of 0.000595 (t = −3.15, sign test 11/14);
the control arm in an earlier series drifted faster (−0.0001487). The referee's verdict is that the shift
cannot be separated from drift at this sample size, and this article accepts that verdict.

## 4. What was tried to rescue it, and what it showed

**Planting in the poor centre.** The colony was planted at (16,16), where the resource is 0.2 against 1.0 in
the patches. The planting position and the zone it falls in are now **written into the artifact**
(`s85_e13_zone_and_pairing.py` records `plant_xy`, the block mean and the class). The trait drifted down
there, but not distinguishably from drift.

**The rich zone with a tenfold stronger effect (`s66`).** This is the result that withdraws the v1.0
headline: in the **rich** zone, with the trait's effect multiplied by ten, the trait shifts by −0.00409 —
**eight times harder** than anything seen in the poor zone. So the v1.0 claim that a trait "can only ride
selection where the environment is hard" is **false**: with a strong enough effect it rides in the easy
environment too.

**Halving the food in the rich zone (`s67`).** Selection reappears (−0.0002…−0.0007) but only at the weak
level of the poor zone, not stronger as a proximity-to-threshold mechanism would predict. That mechanism is
therefore **not supported**.

## 5. Signals: not shown

A signal that predicts the food was tested with leads of 0, 2, 5 and 10 steps. The result is
**non-monotone**: −0.011, −0.001, −0.011, +0.012. With ten seeds the paired t is 1.15 (p = 0.28) and the
sign test 8/10 (p = 0.109). **The advantage is not shown.** Four earlier attempts to show it failed to
replicate for a reason the referee identified: the runs were not paired by randomness, and the "fix" for
that did not change the code path.

## 6. What this article concludes

**Selection exists in this world, and it is strong.** A heritable trait does **not** ride it in any of the
five designs tried. The reason is scale — the trait moves a cell's fate far less than the noise in that
fate — and the shift that does appear cannot be separated from drift at the sample sizes used.

## 7. What this does not show

- It does not show that evolution is impossible in general; only that these five designs do not produce it.
- It does not show that the environment does not matter: `s66` shows the opposite, which is why the v1.0
  headline is withdrawn.
- It does not show that signals are useless: only that the advantage is not demonstrated at ten seeds.

## 8. Where we move next

- **A stronger trait.** `s66` suggests the effect must be large enough to compete with the noise; the next
  design should size the trait against the measured spread *before* running, not after.
- **A trait that changes position rather than upkeep.** Position is the one quantity §2 shows selection acts
  on, and no design yet makes position heritable.

## 9. Reproducibility

Artifacts: `s55_e7_full`, `s58_e7_replication`, `s63_e7f_full`, `s64_e7g_poor_zone`,
`s65_e7g_replication`, `s66_e7h_rich_strong`, `s67_e7i_rich_less_food`, `s85_e13_zone_and_pairing`,
`s86_e13_full`. Scripts: `s55_e7_what_is_selectable.py`, `s62_e7e_trait_in_rule.py`,
`s63_e7f_position_vs_property.py`, `s85_e13_zone_and_pairing.py`. Runs on CPU, R1 checked in every run.
