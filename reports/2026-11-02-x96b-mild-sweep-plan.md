# X96b — the coupling was too strong: a milder sweep of the second species

**Why this exists.** X96's first pass (registered 18:15) swept `gamma` ∈ {0.5, 1.5} at `Dw` ∈ {0.08, 0.16, 0.32} and **voided by its
own liveness rule**: with the third field on, the field collapses to one component (`max|Δv|` up to 0.43 against the control), and at
`gamma = 1.5` it dies outright. That is not a perturbation of the medium — it is a different medium, exactly the failure X78 taught us
to name ("the manipulation changed the regime, not the scale"). A `gamma` of 0.5 weakens the autocatalysis by a factor
`1/(1 + 0.5·w)`; with `w ≈ v ≈ 1` inside a structure that is a 33 % cut in the autocatalysis, which the world cannot absorb.

So the question the owner approved — *can a second diffusion length move the scale* — has **not been asked yet**. This pass asks it
with a coupling small enough that the pattern survives.

## 1. Manipulation is connected

One cell (`F = 0.030`), one seed (401), `Dw` ∈ {0.08, 0.16, 0.32} × `gamma` ∈ {0.05, 0.10, 0.20} — nine runs, X100's flags
otherwise. The anchor is unchanged and already passed bit-for-bit against `x100_f030_s291.json` with the flag off (18:39).

Connectedness: after the field on, the pattern must still be a pattern — **components ≥ 10 at the end** in every run (the w-off
control has 69), and the manipulation must reach the field: `max|Δv| ≥ 0.01` against the control. A run that keeps fewer than ten
components is a regime change and is reported as such, not as a scale result.

## 2. Positive control fires (numeric)

The w-off control's `q'` must sit inside **5 ≤ q' ≤ 9** — the band every forced world has shown (X84, X82), and **the control fires
if** that threshold holds. Measured here on seed 401:
`q' = 9`, `s = 0.702`, 69 components. The control is the same run the first pass used, so the comparison across the two passes is a
comparison at one control.

## 3. Readout exists and varies

`q'` and `s` from `field_metrics.angular` on the field at step 6000, plus components and peak at the end, plus `max|Δv|` against the
control. `q'` varies by construction: it is an argmax over the spectrum, and the first pass already produced 4 and 9 in two settings.

## 4. Sensitivity arithmetic

As in X96: one wavenumber unit is noise (≈1.3 cells at `q' = 9`), so the criterion is a **two-unit** move out of the band 5–9. With
nine settings the pilot can also show a *monotone* trend inside the band, which would be weaker evidence but worth reporting as a
gradient.

## 5. Refusal rule (fixed before the run)

**Void** if the control leaves 5–9, any run keeps fewer than 10 components, or the manipulation fails in every setting.

**The scale channel exists** if at least one live setting gives `q' ≤ 3` or `q' ≥ 11`.
**The channel does not move the scale** if every live setting stays inside 5–9 **and** `q'` does not vary monotonically with `Dw`
(the same value at all three `Dw` for a fixed `gamma`).
**A gradient without a move** if all settings stay inside 5–9 but `q'` changes monotonically with `Dw` at fixed `gamma` — then the
series is registered on that direction, with a wider `Dw` range.
**Not decided** otherwise.

## Design summary

| factor | value |
|---|---|
| runs | 9 (3 `Dw` × 3 `gamma`), seed 401, `F = 0.030`, ~105 s each |
| control | the same w-off run as the first pass (`q' = 9`, 69 components) |
| criterion | `q'` leaves [5, 9] by two units, with ≥ 10 components |
| artifact | `E09_pond/l1_field_x96b_pilot.json` |

## Checklist

- [x] connected (≥ 10 components, manipulation `max|Δv| ≥ 0.01`)
- [x] positive control numeric (control `q'` inside 5–9, measured: 9)
- [x] readout exists and varies (the first pass produced 4 and 9)
- [x] sensitivity computed (§4: two units out of the band)
- [x] refusal rule written, with "a gradient without a move" as a real outcome
- [x] stated: this pass exists because the first one was a regime change, and it is reported as a void

## Status

Registered 2026-11-02 18:47 MSK, before the runs. Owner's approval stands from 02.11 18:11.

доска: принято 0, отклонено 0, отложено 0.
