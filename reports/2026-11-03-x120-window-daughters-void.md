# X120 — void by its own control: daughters are an early-life property, so the time confound is weaker than assumed

**Plan:** [`2026-11-03-x120-window-daughters-plan.md`](2026-11-03-x120-window-daughters-plan.md) (02:02, registered before the run).
**Aggregate:** `l1_field_x120_window_daughters.json`.

## What happened

X120 was built to separate "cost of division" from "time to divide" by counting daughters inside a fixed **1 000-step** window after birth. Its own control fired
against it: the early count correlates with the whole-life count at **0.868** in the lattice and **0.983** in the maze — above the registered 0.8 bar, so the
window does not control time and the design is **void**.

## Why, and what that means

The correlation is the finding: **divisions in this medium happen early in a structure's life.** A 1 000-step window captures almost all of a structure's
daughters (0.98 of them in the maze), which means "many daughters" is not "lived long enough to divide a lot" — it is a property of the first fifth of a
life.

So X119's named confound — a long life giving more opportunities to divide — is **much weaker than the report assumed**. It is not zero (0.87 leaves variance),
but the mechanism I feared is largely absent: structures do not accumulate daughters over a long life; they either divide early or not at all.

The model still ran, and its other coefficients are worth recording although no verdict rest on them:

| cell | uids (excluded late births) | alive | area | daughters in 1 000 steps | start time |
|---|---|---|---|---|---|
| 0.030 | 1 891 (366) | 29.3 % | +0.013 (CI −0.060…0.062) | **−0.268 (CI −0.300…−0.215)** | −0.021 (CI −0.041…0.073) |
| 0.040 | 1 976 (17) | 2.3 % | +0.016 (CI 0.009…0.025) | **−0.021 (CI −0.025…−0.017)** | **+0.077 (CI 0.053…0.107)** |

Two things stand out. The early daughter count keeps a **negative** sign with an interval far from zero in both cells — the same direction as X119. And **start
time does not take the negative sign**: it is uninformative in the lattice and *positive* in the maze, so "later-born structures are less likely to be present"
is not what the model finds; if anything the opposite.

## The honest state of the cost-of-division claim

- X119's coefficient is not explained by "time to divide": divisions are early, and the windowed count behaves the same way.
- What remains uncontrolled is the **hazard** reading of age: an older structure has had more time to die *before* the horizon, and that is a different
  confound from "more time to divide". X120 cannot address it because a dead structure's age is its outcome.
- So the claim stays as written — *at fixed size, more daughters predicts lower own-survival; the mechanism is not identified* — with the caveat now sharper:
  **the time-to-divide mechanism is largely excluded, the hazard mechanism is not tested.**

## What would test the hazard reading

A survival analysis with a time axis: hazard of disappearing as a function of age and daughter count, using the intermediate snapshots rather than only the last
one. The logs carry every logged step, so the data exist; the model does not, and it is a different tool from the OLS used here. Registered in the queue as
X121.

## Caveats

- The void is about the **window**, not about the question: the windowed count is a legitimate variable, it simply failed the bar I set for it.
- 366 uids in the lattice were excluded for being born inside the last 1 000 steps (17 in the maze) — the maze's structures are born early enough that almost
  none are excluded, which is itself consistent with divisions happening early.
- One seed set, one box, the 0.20 cut; linear probability model; the maze's alive rate is 2.3 %.

доска: принято 0, отклонено 0, отложено 0.
