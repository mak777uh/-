# E19 — pre-registration: does turning the record on kill the body?

**Written before the run.** Date: 2026-11-08. Author: the leading agent, under the owner's standing instruction
to run experiments continuously.

## 1. What we saw, and why we are checking it

On 08.11, while fixing the world's energy accounting, two runs of the same world differed in one field:

| run | `plastic_eta` | alive at 300 steps |
|---|---|---|
| `pond-v2-alive` | 0.0 (no record) | **13** |
| `pond-v2-record` | 0.05 (record on) | **0** |

**The world is the same, the seed is the same, the seeding is the same.** The only difference is that in the
second the cell keeps a prediction of the local resource and acts on its error.

**That is one observation per arm, from a run made for another purpose.** It is not a result. This
pre-registration turns it into one.

## 2. The question

**Does turning the record on reduce survival, and if so, by how much?**

Stated as a prediction, so that it can be wrong:

> **P.** With the record on (`plastic_eta = 0.05`), the fraction of runs in which any cell is alive at step 300
> is **lower** than with the record off (`plastic_eta = 0.0`), by at least **0.15** in absolute terms.

**Why this direction.** A cell that acts on its prediction moves to where it expects food. If the prediction is
wrong — and it is, because it lags the resource by `plastic_eta` — the cell moves to where the food *was*.
Moving costs energy (`plastic_move_cost = 0.05`) and the cell leaves a place where it was eating. So a record
that is used can be worse than no record, and the mechanism is not mysterious.

**Why we might be wrong.** The two runs differ in more than the record: with `plastic_eta > 0` the cell also
*moves*, and movement changes which cells are neighbours, which changes growth, which changes everything. The
first design of E18 made exactly this mistake in the other direction (the no-record arm took no actions at all).
**So the third arm below exists to separate "the record" from "moving at all".**

## 3. The design

Three arms, twenty seeds each, the same world otherwise (`pond-v2-alive` parameters):

| arm | `plastic_eta` | `plastic_gate` | what the cell does |
|---|---|---|---|
| **`no_record`** | 0.0 | — | does not act at all |
| **`record_random`** | 0.05 | `random` | **acts**, but ignores its prediction |
| **`record_pred`** | 0.05 | `pred` | **acts on its prediction** |

**The comparison that answers the question is `record_pred` against `record_random`.** Both act; only one uses
the record. `no_record` is the floor and is reported, but it cannot separate "the record" from "moving".

**Twenty seeds** because the sensitivity block below says so.

## 4. What is measured

Per run:

- **`alive_final`** — living cells at step 300 (the primary readout);
- **`pop_time`** — the step at which the population first reached zero, if it did;
- **`plastic_moves`** — how many moves the cells made (the manipulation check);
- **`energy_total`** — total energy at the end;
- **`k_steps`** — the per-cell rows, so `situation_explained` can be computed for the two acting arms.

## 5. The manipulation check, before any result is read

**`record_random` and `record_pred` must differ in their behaviour.** If `plastic_moves` is identical in both,
the gate did not reach the dynamics and the run is invalid. This is checked first, and a run that fails it is
reported as invalid rather than as a result.

## 6. Sensitivity arithmetic, before the run

**The primary readout is a fraction of runs, not a continuous measure.** With 20 seeds per arm:

- a difference of 0.15 in the fraction alive corresponds to **3 runs out of 20**;
- the standard error of a difference of two proportions near 0.5 with 20 each is
  `sqrt(2 * 0.25 / 20) ≈ 0.158`;
- so **0.15 is at the edge of what 20 seeds can see**, and the run must be read as "the direction and the size",
  not as a significance test.

**A difference below 0.10 will be reported as "not distinguishable at this number of seeds", not as "no effect".**

**The secondary readout is `alive_final`**, which is continuous; its expected spread is unknown before the run,
and the first run will replace this guess with the measured value. **This is stated as a guess, not as
arithmetic.**

## 7. The refusal rule

**The series is declared invalid, and no verdict is given, if:**

1. `plastic_moves` is zero in an arm that should act;
2. `plastic_moves` is identical in `record_random` and `record_pred` (the gate did not reach the dynamics);
3. fewer than 15 of the 20 seeds produced an artifact;
4. the population is zero at step 300 in **all three** arms (then the world does not support life and the
   question cannot be asked in it).

## 8. What would make us stop and rethink

- **If `record_pred` and `record_random` do not differ**, the record is not being used, and the whole
  K-readout programme has nothing to measure. That would be a finding about the readout, not about the record.
- **If all three arms die**, the world's parameters are wrong and no behavioural question can be asked until
  they are fixed.

## 9. What this does not establish

1. **It does not say the record is useless.** It says whether *this* record, used *this* way, helps or hurts.
2. **It does not separate the record from movement** except through the `record_random` arm, and that arm is a
   different mechanism (a random share of steps), not a perfect control.
3. **It does not say anything about the living.** It is a measurement of one mechanism in one world.

## 1. Manipulation is connected

**The two acting arms must differ in their behaviour, and they do by construction:** `record_random` acts on a
random share of its steps while `record_pred` acts when its prediction says the resource is worse. **Checked on
the data, not on the argument:** if the median `plastic_moves` is identical in the two arms, the gate did not
reach the dynamics and the series is invalid. **This check caught a real failure on 08.11**: the first run of
this series had identical move counts because `plastic_gate` was being overwritten after the profile set it.

## 2. Positive control fires

**`no_record` is the positive control for "acting at all".**

- **сработал, если** `plastic_moves = 0` в этом плече (клетка действительно не действует) **и** доля прогонов
  с `alive_final > 0` не ниже **0.5** (мир поддерживает жизнь без действия).
- **не сработал, если** `plastic_moves > 0` (плечо действует, хотя не должно) **или** доля живых ниже 0.5
  (мир не поддерживает жизнь, и вопрос в нём не задаётся).

**The acting arms must show `plastic_moves > 0`**: an acting arm with zero moves is a failed manipulation, not
a null result. **Threshold: `plastic_moves >= 100` in the median**, because fewer than a hundred moves across
three hundred steps is not a behaviour, it is a coincidence.

## 3. Readout exists and varies

**`alive_final`** must take at least three distinct values across the twenty seeds of an arm. **If every seed
gives the same count, the readout does not vary and the arm measures nothing.** The first arm of this series
already shows the spread: 0 to 1024 across twenty seeds, median 524. **`pop_time`** is the secondary readout
and must likewise vary.

## 4. Sensitivity arithmetic

**The primary readout is a fraction of runs, not a continuous measure.** With twenty seeds per arm a difference
of 0.15 corresponds to three runs out of twenty; the standard error of a difference of two proportions near 0.5
with twenty each is `sqrt(2 * 0.25 / 20) ≈ 0.158`. **So 0.15 is at the edge of what twenty seeds can see, and a
difference below 0.10 will be reported as "not distinguishable at this number of seeds", not as "no effect".**
The secondary readout `alive_final` is continuous; its expected spread is unknown before the run and is
**stated as a guess, not as arithmetic** - the first run replaces the guess with the measured value.

## 5. Refusal rule

**The series is declared invalid, and no verdict is given, if any of these holds:**

1. `plastic_moves` is zero in an arm that should act;
2. `plastic_moves` is identical in `record_random` and `record_pred`, so the gate did not reach the dynamics;
3. fewer than 15 of the 20 seeds produced an artifact;
4. the population is zero at step 300 in all three arms, so the world does not support life.

**A series that fails the rule is reported as invalid, with the failing condition named, and is not counted as
either a positive or a negative result.**

