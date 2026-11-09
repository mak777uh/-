# E20 — pre-registration: does moving cost survival?

**Written before the run.** Date: 2026-11-09. Author: the leading agent, under the owner's standing instruction
to run experiments continuously.

## 1. What we saw, and why we are checking it

E19 compared three arms of one world and found that **the largest difference was not between the arms that used
a record and the arms that did not, but between acting and not acting**:

| arm | fraction alive at 300 | median moves |
|---|---|---|
| `no_record` (does not act) | **0.90** | 0 |
| `record_random` (acts, ignores the record) | **0.75** | 17759 |
| `record_pred` (acts on the record) | **0.80** | 11746 |

**The arms that move survive worse than the arm that does not.** And among the arms that move, the one that
moves LESS survives better. That is two observations pointing the same way, from one series, and neither was
predicted.

## 2. The question

**Does survival fall as the number of moves rises, and is the record only a modulator of movement?**

Stated so that it can be wrong:

> **P.** Across arms that differ only in how much they move, the fraction of runs alive at step 300 falls
> **monotonically** with the median number of moves, and the difference between the most-moving and the
> least-moving arm is **at least 0.15**.

**Why this direction.** A move costs energy (`plastic_move_cost = 0.05`) and takes the cell away from a place
where it was eating. More moves should mean less energy and less survival.

**Why we might be wrong.** E19's two acting arms differ in *two* things at once — how many moves, and what
decides them. A monotone relation across arms that differ in both is not a causal statement. **The
`--plastic-move-cost` arm below exists to separate the cost of moving from the number of moves.**

## 3. The design

Four arms, twenty seeds each, the same world (`pond-v2-alive` parameters), 300 steps:

| arm | what differs | what it tests |
|---|---|---|
| **`still`** | `plastic_eta = 0` | the floor: no movement at all |
| **`moves_cheap`** | `plastic_eta = 0.05`, `plastic_move_cost = 0.0` | moves as much, pays nothing |
| **`moves_base`** | `plastic_eta = 0.05`, `plastic_move_cost = 0.05` | moves as much, pays the normal price |
| **`moves_dear`** | `plastic_eta = 0.05`, `plastic_move_cost = 0.20` | moves as much, pays four times |

**The arm that answers the question is `moves_cheap` against `moves_base`.** Both move; only one pays. If
survival falls when the price rises, the cost of moving is what hurts. If it does not, the number of moves is
what hurts, and the price is irrelevant.

## 1. Manipulation is connected

**The three moving arms must differ in their energy, not necessarily in their move count.** `moves_cheap` pays
nothing per move, `moves_base` pays 0.05, `moves_dear` pays 0.20, so the total energy spent on moving must
differ by a factor of at least four between `moves_cheap` and `moves_dear`. **Checked on the data:** if the
median `energy_total` is the same in those two arms, the price did not reach the dynamics and the series is
invalid.

## 2. Positive control fires

**`still` is the positive control for "not moving".**

- **сработал, если** `plastic_moves = 0` в этом плече **и** доля прогонов с `alive_final > 0` не ниже **0.5**.
- **не сработал, если** `plastic_moves > 0` (плечо движется, хотя не должно) **или** доля живых ниже 0.5.

**The moving arms must show `plastic_moves >= 100` in the median**; fewer than a hundred moves across three
hundred steps is a coincidence, not a behaviour.

## 3. Readout exists and varies

**`alive_final`** must take at least three distinct values across the twenty seeds of an arm, and
**`energy_total`** must do the same. **If either is constant within an arm, that arm measures nothing.**

## 4. Sensitivity arithmetic

**The primary readout is the fraction of runs alive, a proportion.** With twenty seeds per arm the standard
error of a difference of two proportions near 0.5 is `sqrt(2 * 0.25 / 20) ≈ 0.158`. **E19 showed a difference of
0.15 between the still and moving arms, which is at the edge of what twenty seeds can see.** **This series
therefore uses twenty seeds but will be read as a direction, not as a significance test**, and a difference
below 0.10 will be reported as "not distinguishable at this number of seeds".

**The secondary readout `energy_total` is continuous**; its spread is unknown before the run and is stated as a
guess, not as arithmetic.

## 5. Refusal rule

**The series is invalid, and no verdict is given, if:**

1. `plastic_moves` is zero in an arm that should move;
2. `plastic_moves` is identical in `moves_cheap` and `moves_dear` (the price did not reach the dynamics);
3. `energy_total` is identical in `moves_cheap` and `moves_dear` (the price reached nothing);
4. fewer than 15 of the 20 seeds produced an artifact;
5. the population is zero at step 300 in all four arms.

## 6. What would make us stop and rethink

- **If `moves_cheap` and `moves_base` do not differ**, the price of moving is not what hurts, and the E19
  observation is about the number of moves rather than their cost. That would be a different mechanism and a
  different next experiment.
- **If all four arms die**, the world's parameters are wrong again, and no behavioural question can be asked.

## 7. What this does not establish

1. **It does not establish that movement is bad in general.** It measures one world with one price schedule.
2. **It does not separate the number of moves from their direction.** A move toward food and a move away are
   counted the same here.
3. **It does not say anything about the living.** It is one measurement of one mechanism in one world.
