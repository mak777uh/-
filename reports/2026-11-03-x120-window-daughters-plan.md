# X120 — cost of division or time to divide? Daughters counted in a fixed early window

**Why.** X119 (unregistered, recorded post hoc) found that at fixed size, more daughters predicts **lower** own-survival: `−0.429` (CI −0.509…−0.345) in the
lattice, `−0.051` in the maze. The named confound is time: a structure that lived longer had more opportunities to divide, and a longer life also changes the
chance of being present at the last step. Conditioning on lifetime cannot answer this — for a dead structure its lifetime *is* the outcome.

**The test.** Count daughters in a **fixed window after birth** rather than over the whole life. A structure that divides fast does so inside the window; a
structure that merely lived long has no advantage in the count, because the window is the same for everyone.

## 1. Manipulation is connected

X108's twenty runs. Per uid: `alive` (present at the last logged step), `log(peak area)`, `daughters_1000` = number of its children first appearing within
**1 000 logged steps** of its own birth, and `start` = its first appearance (steps). Connectedness: at least **800 uids** per cell with a defined birth step
and a window that lies entirely inside the run (a uid born in the last 1 000 steps is excluded, and the excluded count is reported).

## 2. Positive control fires (numeric)

Two controls, both required:

1. **Heredity** `≥ 0.35` in both cells (0.548 / 0.480) — the control fires if both hold.
2. **The window is doing the controlling:** the correlation between `daughters_1000` and the whole-life daughter count must be **below 0.8**. If the early
   count is simply the late count, the window adds nothing; the measured value is printed and a value above 0.8 voids the design as a re-labelling.

## 3. Readout exists and varies

Per cell: OLS of `alive ~ 1 + log(area) + daughters_1000 + start`, with 500 world-level bootstrap draws, all four coefficients and their intervals, the
alive rate, and the correlation from control 2. Variation exists: X119's daughters coefficient is −0.429 and the early count spans 0–5.

## 4. Sensitivity arithmetic

~800–2 000 uids, so coefficient standard errors are small and the bootstrap intervals are narrow; the declared resolution is an interval excluding zero, with
the caveat that the maze alive rate (3 %) leaves few survivors. A change of sign between X119's whole-life coefficient and this windowed one is treated as the
signal — the same model, one variable replaced.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 800 usable uids, heredity misses 0.35, or the window-to-lifetime daughter correlation reaches 0.8.

**A cost of division survives the time control** if `daughters_1000` is negative with the interval excluding zero in both cells.
**The negative sign was time** if `daughters_1000`'s interval contains zero in both cells while X119's whole-life coefficient excluded it.
**Mixed** otherwise, cells reported separately — and if `start` takes the negative sign instead, the report says that age, not division, is what the model is
finding.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs |
| model | `alive ~ 1 + log(area) + daughters_1000 + start`, world-level bootstrap |
| new variable | daughters counted within 1 000 steps of birth (time-controlled) |
| controls | heredity ≥ 0.35; early-versus-lifetime daughter correlation < 0.8 |
| artifact | `E09_pond/l1_field_x120_window_daughters.json` |

## Checklist

- [x] connected (800 uids; exclusions for late births reported)
- [x] positive control numeric (heredity ≥ 0.35; correlation < 0.8, printed)
- [x] readout exists and varies (X119's −0.429; early count 0–5)
- [x] sensitivity computed (§4: intervals excluding zero; maze caveat)
- [x] refusal rule written, with "the negative sign was time" as a real outcome
- [x] registered **before** the run — the X119 breach is not repeated

## Status

Registered 2026-11-03 02:02 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
