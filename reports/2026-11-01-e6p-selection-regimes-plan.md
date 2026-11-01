# E6p — does selection need a survival channel, and does frequency dependence stop fixation?

1 November 2026, 05:10. Preregistration before the series, per `docs/preregistration-template.md`.

**Why this exists at all.** The field line already ran this question twice: `E6c` (composition affects growth) found
inheritance without selection, `E6d` (composition affects survival) found selection leading to fixation, `E6e`
(frequency-dependent survival) was the proposed repair. §10bx–§10bz record those results. **Their per-run artifacts lived
in `_hourly/` and are gone** — 36 files, none of them ever in git. The claims are therefore unverifiable today, and the
three-arm design below restores the evidence inside the repository rather than re-litigating the conclusion.

---

## 1. Manipulation is connected

Pilot, seed 171, 6000 steps, three regimes, run 1 November 05:00 (`_exports/e6p/`):

| regime | components | `s_mean` end | between-structure sd | splits | `r` |
|---|---|---|---|---|---|
| `beta = 0` (no survival channel) | 36 | 1.204 | 0.293 | 89 | 0.837 |
| `beta = 0.2`, `freq_dep = 0` | 1 | 1.553 | 0.000 | 49 | 0.773 |
| `beta = 0.2`, `freq_dep = 1` | 6 | 2.005 | 0.566 | 482 | 0.964 |

The three regimes produce different dynamics from the same seed. Dynamics hashes are recorded in the series index; the
pilot already shows the manipulation reaching the world (composition 1.204 / 1.553 / 2.005, structures 36 / 1 / 6).

## 2. Positive control fires

- **Control arm:** `beta = 0`, where composition cannot affect decay, so any drift is mutation plus inflow.
- **Observed effect:** the survival channel moves mean composition from 1.204 to 1.553 (`freq_dep = 0`) and to 2.005
  (`freq_dep = 1`) in the pilot.
- **Threshold that counts as "fires":** median paired drift above **+0.20**, i.e. well under the observed +0.35 and
  +0.80, with at least 8/10 seeds agreeing.

The control fires in the pilot, so the design cannot be a null by construction.

## 3. Readout exists and varies

- **Readouts:** `s_mean_last`, `s_sd_between_last`, `splits`, `parent_child_pairs`, `inheritability_r`, `components`.
- **Field in the artifact:** `selection.s_mean_last`; the pilot gives 1.204 / 1.553 / 2.005 across arms and 0.234 across
  seeds in earlier runs, so it varies.
- **Between-structure spread** (the "fuel" for selection) is 0.293 / 0.000 / 0.566 — it varies too, and the zero in the
  middle arm is itself a result (fixation collapses variation).

## 4. Sensitivity arithmetic

From the pilot and from `x23`/`x60` (10 seeds each):

- baseline per-seed `s_mean_last` in the control ≈ **1.20**
- the drift to detect: **+0.35** (`freq_dep = 0`) and **+0.80** (`freq_dep = 1`)
- between-structure sd: 0.29 to 0.57, so the *unpaired* spread is the same size as the smaller effect, which is why the
  design is **paired by seed**, as before
- with 10 paired seeds and a per-seed drift whose sign is what matters, the pre-declared criterion is a **sign rule**
  (≥ 8/10) plus the effect threshold above; no p-value is pre-declared, because a t-test on 10 seeds of an
  autocorrelated trajectory would overstate precision

## 5. Refusal rule

The series is worthless, not negative, if:

1. the control arm drifts by more than the treatment arms (then the readout is dominated by the inflow field, not by
   selection, and no arm difference is interpretable);
2. `s_mean_last` is identical across seeds within an arm (a saturated readout cannot carry a sign rule);
3. the three arms produce the same dynamics hash on the same seed (§1 failing in the series rather than in the pilot);
4. the fixation arm ends with more than 3 structures in most seeds, or the frequency-dependent arm with 1 — then the
   regimes are not what the pilot says they are, and the labels are wrong.

## Design summary

| element | value |
|---|---|
| world and settings | L1 field, grid 96, `dt = 1.0`, 6000 steps, heterogeneous inflow (amp 0.5, scale 12), `eps = 0` (no growth channel), mutation 0.15 |
| arms | `beta = 0` (control), `beta = 0.2 / freq_dep = 0` (survival, no frequency dependence), `beta = 0.2 / freq_dep = 1` (frequency-dependent survival) |
| seeds | 171–180, paired across arms |
| readout | `s_mean_last`, `s_sd_between_last`, `splits`, `parent_child_pairs`, `r`, `components` |
| criterion | median paired drift > +0.20 with ≥ 8/10 seeds for a selection claim; fixation defined as median `components` ≤ 1 |
| artifacts | `morphogenesis/experiments/L1_field/e6p_<arm>_s<seed>.json`, index `e6p_series_index.json` — **in git**, which is the point |

## What the result would decide

- If the survival channel drifts and the growth channel does not, the E6c/E6d conclusion is restored with repo evidence:
  **selection needs a channel without a matching cost.**
- If the frequency-dependent arm keeps several structures while drifting, then **diversity is held by frequency
  dependence**, not by selection strength — the same conclusion the pond line reached from the other side (§10by).
- If both survival arms fixate, then the earlier "fixation" result is a property of the inflow field's niches, and the
  next experiment is about niche turnover, not about the trait channel.

## Status

- [x] connected (pilot: three regimes, three different dynamics)
- [x] positive control fires (+0.35 and +0.80 against a +0.20 bar)
- [x] readout exists and varies (1.204 / 1.553 / 2.005; spread 0.29–0.57)
- [x] sensitivity computed (paired by seed, sign rule, effect threshold)
- [x] refusal rule written (four conditions)

**Run after the anchor: the control arm must reproduce an existing `beta = 0.2` run when `freq_dep` matches, and the
`beta = 0` arm must reproduce `x18`-style dynamics with no survival channel.**
