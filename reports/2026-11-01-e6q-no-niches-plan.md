# E6q — turn the niches off: is coexistence a property of the environment?

1 November 2026, 06:00. Preregistration before the run.

E6p produced a sentence: *selection is easy, coexistence is a property of the environment.* This is its direct test. Same
two regimes, same seeds, one thing changed — the inflow field becomes homogeneous (`hetero_amp` 0.5 → 0.0), so the world
has no niches to hold separate structures.

**Prediction, written before the data.** If coexistence needs niches, the frequency-dependent arm without niches ends
with **fewer than 2.5 structures** (the heterogeneous median from `l1_field_e6p_selection.json`) and fixates in more
seeds. If it keeps 2.5 or more, niches are not what holds the structures and the sentence is wrong.

---

## 1. Manipulation is connected

The two inflow fields already differ in dynamics on the same seed: `x18` heterogeneous against homogeneous gives different
component series (`[1, 11, 15, 20, 3, 6, 6]` against `[1, 1, 5, 2, 3, 4, 4]`, hashes `628da5a16fcb` / `e32e8f6e185c`), and
the E6p heterogeneous arms are on disk. Removing the inflow modulation therefore reaches the world; the run is not
manipulating a label.

## 2. Positive control fires

- **Control arm:** `ctrl_h` — `beta = 0` with homogeneous inflow; composition cannot affect decay, so its drift is the
  null.
- **Positive control:** the survival channel must **still** drift with niches removed. If the survival effect vanishes
  when the inflow is uniform, the manipulation stopped reaching the dynamics and nothing else in the series can be read.
- **Observed effect in the comparable heterogeneous world:** +0.835 (9/10 seeds) for `survfd`, +0.484 (10/10) for `surv`.
- **Threshold that counts as "fires":** median paired drift above **+0.20**.

## 3. Readout exists and varies

- **Readouts:** `components` (structures at the last snapshot), `s_mean_last`, `s_sd_between_last`, `splits`,
  `inheritability_r`.
- **Field in the artifact:** `heterogeneity.components_last`; the homogeneous `x60` arm ranges 2–9 across seeds, so the
  readout varies and is not pinned at the floor.

## 4. Sensitivity arithmetic

- **baseline to beat:** heterogeneous `survfd` median structures = **2.5**, fixation share 0.2 (E6p, 10 seeds).
- **effect worth detecting:** a drop of at least **one structure** in the median, or a rise in fixation share of at least
  **0.2**.
- **pairing:** the comparison is paired by seed — the same ten seeds, the same parameters, only `hetero_amp` changes — so
  the relevant spread is the per-seed difference, not the between-seed spread of either arm.
- **criterion:** median paired difference in structures **< 0** with at least **8 of 10** seeds agreeing, or fixation
  share ≥ 0.4 against 0.2. Below that, the prediction is not supported and is reported as unsupported.

## 5. Refusal rule

Worthless, not negative, if:

1. the homogeneous world dies in most seeds (median structures 0), so there is nothing to count — the world, not the
   hypothesis, failed;
2. `s_mean_last` is identical across all seeds in an arm (saturated readout);
3. the survival arm's composition does not drift at all (item 2 of the positive control failing), because then the trait
   channel is inert and the structure counts are meaningless.

## Design summary

| element | value |
|---|---|
| world and settings | L1 field, grid 96, `dt = 1.0`, 6000 steps, **homogeneous** inflow, `eps = 0`, mutation 0.15 |
| arms | `ctrl_h` (`beta = 0`), `survfd_h` (`beta = 0.2`, `freq_dep = 1`) |
| seeds | 171–180, the same seeds as E6p |
| comparison | paired by seed against the heterogeneous `survfd`/`ctrl` arms already on disk |
| criterion | median paired drop in structures < 0 with ≥ 8/10 seeds, or fixation share ≥ 0.4 |
| artifacts | `morphogenesis/experiments/L1_field/e6q_<arm>_s<seed>.json`, index `e6q_series_index.json` |

## Status

- [x] connected (heterogeneous and homogeneous fields differ on the same seed)
- [x] positive control fires (survival drift +0.835 in the comparable world; must persist here)
- [x] readout exists and varies (homogeneous `x60` arm: 2–9 structures)
- [x] sensitivity computed (paired by seed, one-structure drop or fixation +0.2)
- [x] refusal rule written (three conditions)
