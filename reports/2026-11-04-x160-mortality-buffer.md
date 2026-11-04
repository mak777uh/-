# X160 — A mortality buffer on an external signal does not hold diversity (04.11)

**Question.** Diversity is lost in this medium even when the inflow varies, because every route tried so far multiplies
*inflow*, and a multiplicative advantage accumulates wherever it lands (§10cg). The storage effect says the buffer must act
on **mortality**: a slow variable that makes death likelier in a bad phase should let a rare type wait out that phase, which
is the one mechanism for coexistence this world has not yet been tested for.

Pre-registration: [`2026-11-04-x160-mortality-buffer-plan.md`](2026-11-04-x160-mortality-buffer-plan.md), with Amendment 1
(one `tau` band, twenty seeds) and Amendment 2 (three code faults and the income). Three arms × twenty seeds × 1 800 steps,
`tau` = 300, `gain` = 0.02, income 0.030, grid 32: `const` (a flat signal — the null), `real`
(`lab/streams/mic-2026-10-28.json`), `surrogate` (its tempo-matched IAAFT twin).

## The manipulation had to be repaired twice before it existed

The first grid produced nothing: all three arms with identical `pop_time` (742.0) and zero kills. That was not a null
result but a manipulation that never reached the dynamics, caught by the pre-registered positive control. Three faults,
each sufficient on its own: the signal was loaded onto the config while the hook read the instance; the kill count was
truncated to an integer and was therefore zero while the population was small; and the reference was the buffer's own
running mean, which makes the deviation ≈ 0 by construction (measured −1.06, with a kill probability of 4.6·10⁻⁸). All
three are recorded in `docs/incidents.md` §14, and the summary now reports `memory_calls`, `memory_dev_mean`,
`memory_prob_mean` and `killed_by_memory` for every run, so a silent buffer can never again be mistaken for a null.

A second, independent defect was found by the same probe: at income 0.02 against update_cost 0.03 the world goes extinct
within about a hundred steps, so the original grid was insensitive **by construction**. A sweep at 600 steps showed that
income is not the lever — 4/5 survivors at 0.030, 0.034 and 0.038 alike, with seed 801 dying at every level and
`clonal_fraction` at 0.98-0.99 everywhere — so the grid ran at income 0.030 with the world's near-monoculture and its
one-in-five extinction risk recorded in the amendment before any arm was compared.

## Result — the buffer fires, and diversity does not improve

| arm | runs | buffer firing | kills total | `memory_dev_mean` | survivors | active cells (median) | `clonal_fraction` |
|---|---|---|---|---|---|---|---|
| const (null) | 20 | no | 0 | 0.00 | 6/20 | 0 | 0.834 |
| real | 20 | yes | 11 220 | 0.74 | 3/20 | 0 | 0.809 |
| surrogate | 20 | yes | 13 618 | 0.04 | 6/20 | 0 | 0.836 |

The buffer fired in both active arms, so the manipulation reached the dynamics this time. The active arms finish **at or
below** the null: −0.025 for the real stream and +0.002 for its tempo-matched surrogate. And the real stream is worse than
its own surrogate on both readouts — 3/20 survivors against 6/20, and a lower clonal fraction — which is the opposite of
the storage-effect prediction.

The mechanism is visible in the two deviation means. The real stream is temporally structured, so its leaky buffer sits
above its long-run mean for long stretches (`dev` = 0.74) and the extra mortality lands in **clumps**; the surrogate has
the same amplitude spectrum but no slow structure, so its buffer hovers at zero (`dev` = 0.04) and its kills are spread
thinly. Clumped mortality in a world that is already marginal kills the population rather than sheltering a rare type.

## Verdict

This is the outcome the pre-registration named in advance: the real arm does not beat its tempo-matched surrogate, so the
item is recorded as **the structure of the signal does not matter in the mortality channel either** — the third
independent negative on the same hypothesis, after the inflow buffer and the field-heterogeneity series. The "resonant
medium" route is now closed for this world with a named mechanism: there is no slow variable to integrate into, and adding
one does not help; on the contrary, a structured buffer at this scale is destabilising.

## Limits — and they are serious

The world went extinct in fourteen of twenty runs in the null arm, so the diversity readout rests on six survivors against
three. That is too few to put an interval on the difference, and the honest statement is a **direction with weak power**,
not a measured effect size. The design therefore did not fail by being insensitive (the buffer fired in every run) but by
being run in a world that mostly dies: at grid 32 with four start cells and 1 800 steps, survival itself is the dominant
outcome, and any diversity statistic is conditional on it.

## What would kill it

A repeat in a world that survives — patch mode, or more start cells, or income high enough that the null arm keeps four
fifths of its runs alive — would test whether the negative is about the mechanism or about running the experiment near
extinction. If, in such a world, the real arm still fails to beat its surrogate, the negative stands on better ground; if
it beats it, the conclusion here is an artefact of the marginal world and must be withdrawn.

## Next hypotheses

1. **The same buffer in a world that lives**: patch mode with twelve start cells, so that the null arm survives 16/20 and
   the diversity readout has power. This is the first item the negative asks for.
2. **Buffer on birth instead of death, with the same reference**: does the reference fix alone change the inflow story?
   (Cheap, and it separates "channel" from "reference".)
3. **Clumped versus smooth mortality at equal total kills**: the mechanism suggested above, tested directly by drawing the
   kill times from the real stream's excursions versus a shuffled version with identical counts.
4. **A local buffer** (per patch rather than global): the storage effect in nature is spatial, and a global scalar is the
   crudest possible carrier.

Report: `reports/2026-11-04-x160-mortality-buffer.md`; aggregate
`morphogenesis/experiments/E09_pond/x160_memory/x160_memory.json` (with the `analysis` block); runner
`scripts/x160_series.py`; analysis `scripts/x160_analyse.py`; world change in `morphogenesis/world/pond.py` and
`morphogenesis/world/run_pond.py`.
