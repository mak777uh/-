# E19 — does turning the record on kill the body?

**Pre-registration:** [`2026-11-08-e19-record-kills-plan.md`](2026-11-08-e19-record-kills-plan.md), written before
the run. **Artifacts:** `morphogenesis/experiments/E19/` (60 runs). **Analysis:**
`python scripts/analyse_e19.py`.

## 1. What we looked at

Three arms of the same world, twenty seeds each, 300 steps, the same seeding:

| arm | `plastic_eta` | `plastic_gate` | what the cell does |
|---|---|---|---|
| `no_record` | 0.0 | — | does not act at all |
| `record_random` | 0.05 | `random` | acts, ignores its prediction |
| `record_pred` | 0.05 | `pred` | acts on its prediction |

The question was whether using the record reduces survival. The pre-registration predicted a reduction of
**at least 0.15** in the fraction of runs alive at the end, comparing `record_pred` with `record_random`.

## 2. What we found

| arm | runs | fraction alive at 300 | median alive | median moves |
|---|---|---|---|---|
| `no_record` | 20 | **0.90** | 524.5 | 0 |
| `record_random` | 20 | **0.75** | 668.5 | 17759 |
| `record_pred` | 20 | **0.80** | 620.0 | 11746.5 |

**The manipulation check passed:** the two acting arms differ in their number of moves (17759 against 11746),
so the gate reached the dynamics.

**The predicted effect did not appear.** The difference between `record_pred` and `record_random` is
**−0.05**, not −0.15, and in the direction of the record *helping* rather than hurting.

**By the pre-registered rule this is "not distinguishable at 20 seeds", not "no effect".** The standard error of
a difference of two proportions near 0.5 with 20 runs each is about 0.158, so a difference of 0.05 is well
inside the noise. **The prediction is not confirmed; it is also not refuted with this number of seeds.**

## 3. What the numbers do say, and it is not what we expected

**The largest difference in the table is not between the two record arms. It is between acting and not acting.**

`no_record` keeps **0.90** of its runs alive; the two acting arms keep **0.75** and **0.80**. **Movement costs
survival**, and that cost is bigger than anything the record does.

**And inside the acting arms the record helps rather than hurts:** `record_pred` (0.80) survives better than
`record_random` (0.75), and it does so with **fewer moves** (11746 against 17759). A cell that moves only when
its prediction says the food is worse moves less, and moving less is better in this world.

**So the mechanism we proposed in the pre-registration — "the prediction lags, so the cell moves to where the
food was" — is not what the data show.** The data show that the prediction *reduces* movement, and reducing
movement is what helps.

## 4. Why the original observation was misleading

The observation that started this experiment was two runs: `pond-v2-alive` with 13 cells alive and
`pond-v2-record` with 0. **Those two runs were made before the profile ordering bug was fixed**, so the
"record on" arm was not actually running with the record on — `plastic_gate` was being overwritten by the
argument default. **The observation that motivated the experiment was an artefact of a bug in the harness, not
a property of the world.**

**This is the second time in one day that a defect in the harness produced a plausible-looking result.** The
first was the E18 design, where the "no record" arm took no actions at all. Both were caught, but both cost a
series.

## 5. What this changes in the next experiment

1. **The interesting variable is movement, not the record.** The next experiment should hold the record fixed
   and vary the cost of moving, with `no_record` as the floor. The prediction to test: **survival falls
   monotonically with the number of moves**, and the record is a *modulator* of movement, not a cause of
   survival.
2. **Twenty seeds cannot separate 0.05 from zero on a binary readout.** Any further arm comparison on a
   fraction needs **at least 60 seeds per arm** to see a 0.10 difference, or a continuous readout instead.
3. **The harness needs a check that the arm it thinks it is running is the arm it runs.** Both failures today
   were of that kind: a field silently overwritten after it was set. A manifest field that names the arm and a
   gate that reads the artifact back and compares it to the manifest would have caught both.

## 6. What this does not establish

1. **It does not say the record is useless.** It says that at 20 seeds, in this world, the difference between
   using and ignoring the record is smaller than the noise.
2. **It does not say movement is bad in general.** It says that in this world, with these parameters, acting
   more is associated with dying more. The association is not a mechanism.
3. **It does not say anything about the living.** It is one measurement of one mechanism in one world.
