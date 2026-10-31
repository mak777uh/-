# X53: omission design in the pond — preregistration (31.10.2026)

Written **before** any run, because the last five designs of this line were invalid and three of them could have been
rejected by arithmetic alone. The rule of §3c applies: no experiment about a difference is launched until the
arithmetic that could produce that difference has been computed.

---

## 1. Why this experiment, and why in the pond

The field world is exhausted as an instrument for behavioural questions (§10du): structures are inert, division is not
recorded, and a strong pulse produces no measurable response. The omission design — remove the event and see whether
behaviour still anticipates it (Saigusa et al. 2008) — needs a world where **behaviour is a number**.

In the pond, the number is **net growth of living cells** (`alive_series`, already recorded in every run).

## 2. What is measured, and what is deliberately not

**Readout:** `Δalive` — the change in living cells over the observation window (net growth).

**Not the readout, and why.** `born` (the division counter) **does not fire** on the growth path: in a run with 1469
living cells at step 700, `born = 0` and `died = 2103`. Growth here happens by cells appearing and moving
(`s.alive[dy, dx] = True; s.alive[sy, sx] = False`), not by division. Using `born` would have measured nothing while
looking like a behavioural variable — the same class of error as `X46`, caught before the run.

## 3. Sensitivity arithmetic (the part that decides the design)

From the ten habitable runs (`x43_hab_s*`, b = 0.02, 1500 steps), growth over the second half (750 steps):

| | |
|---|---|
| median | **436 cells** |
| min / max | 288 / 738 |
| sd between seeds | **145** |
| coefficient of variation | **0.333** |

**CV = 0.333 is above our own admissibility threshold of 0.3.** The unpaired readout is therefore too noisy to carry a
claim, and this is not a matter of effort but of arithmetic:

| effect to detect | cells | seeds per arm, unpaired (α = 0.05, power 0.8) |
|---|---|---|
| 10 % | 44 | **174** |
| 20 % | 87 | 44 |
| 30 % | 131 | 20 |
| 50 % | 218 | 7 |

**Consequence: the design must be paired.** Each seed runs twice — with the tide and without it — and the per-seed
difference is the statistic. Pairing removes the between-seed component, which is where the 0.333 comes from.

**The paired sd is not known yet and must not be assumed.** Pilot: 3 seeds × 2 arms, measure the sd of the differences,
then choose n. If the paired sd stays near the unpaired one, the pairing failed and the experiment is not run.

## 4. Design

| element | value |
|---|---|
| world | pond, `b = 0.02`, cost 0.03 (habitable, 10/10 survive) |
| tide | periodic bonus inflow, period 60 steps, width 10 steps |
| arms | **A**: tide throughout; **B**: tide throughout, **omitted** in the window [800, 1100) |
| window | steps 800–1100 (5 would-be pulses) |
| readout | `Δalive` inside the window |
| seeds | 10 pairs, same seed in both arms |
| steps | 1500 |

**Positive control, required before the omission arm is interpreted.** In arm A the growth during the *phase* of the
tide must differ from the growth outside it by **at least 30 %** (131 cells, 20 seeds equivalent). If it does not, the
tide does not reach the population and the whole experiment is insensitive — it will be recorded as such, not as a
null result.

**Criterion for "the world expects the event".** In arm B, growth inside the omission window must differ from arm A's
window growth in the direction of the tide's effect (i.e. as if the event were still happening), with the paired
difference exceeding the pilot sd at 95 %.

## 5. What would make this experiment worthless

Written down in advance so that it cannot be discovered afterwards:

1. the tide does not change growth (positive control fails);
2. the paired sd is as large as the unpaired one (pairing fails);
3. the window contains fewer than 3 would-be pulses;
4. cells die out before the window (then there is no behaviour to measure);
5. the tide's effect is not local (if it changes the whole field uniformly, there is nothing to anticipate).

## 6. Status

**Not run.** Blocked on the pilot that measures the paired sd. This document exists so that the next session does not
start from a plausible-sounding design that the arithmetic already rejects.

## 7. Machine checks

`scripts/pond_probe_adequacy.py` now records `born_series` and `died_series` alongside `alive_series`; the anchor holds
(alive identical over 700 steps with seed 171). The sensitivity numbers above are recomputed from
`morphogenesis/experiments/E09_pond/habitable/x43_hab_s*.json`.
