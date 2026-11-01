# X60 — the field run that keeps its snapshots: preregistration

1 November 2026. Written **before** the run, per `docs/preregistration-template.md`. Purpose: stop treating the field as
if it were only a component counter. The run does one new thing — it saves the `v` field at three snapshots — and that
single addition makes four questions answerable that are currently answered by argument.

Status: **not run**. Code change and anchor are specified in §6.

---

## 1. Manipulation is connected

Two runs identical except for the inflow heterogeneity, already on disk and already hashed on seed 171 (7 slices each):

- heterogeneous `x18_pattern_s171`: dynamics hash **`628da5a16fcb`**, components `[1, 11, 15, 20, 3, 6, 6]`
- homogeneous `x18_homog_s171`: dynamics hash **`e32e8f6e185c`**, components `[1, 1, 5, 2, 3, 4, 4]`

The hashes differ, so the manipulation reaches the dynamics. `X60` reuses exactly this pair of arms: the point of the
run is not a new manipulation but a new **readout** on the same manipulation.

## 2. Positive control fires

- **Control arm:** heterogeneous against homogeneous inflow, same seeds, same everything else.
- **Observed effect:** contrast **+3.57** components (median of per-seed time means: 6.43 against 2.86), **10/10** seeds
  positive at `dt = 1.0`.
- **Threshold that counts as "fires":** at least 8/10 seeds positive and a median contrast above +1.0.

The control fires on the existing data, so `X60` cannot be a null by construction: whatever the new readouts say, the
worlds they describe are demonstrably different in the old readout.

## 3. Readout exists and varies

- **Readout names:** `components` (β₀ at threshold 0.2), `beta1` (loops), `q_peak` and `lambda` (structure factor),
  `N_norm = N·λ²/A`.
- **Field in the artifact:** `series[].components` already varies within a run (`1 → 20 → 3`); across seeds the CV of
  the per-seed mean is **0.581** in the heterogeneous arm.
- **New readouts are not yet known to vary**, so they are gated: they are computed on the first **three seeds**, and the
  remaining seven are run only if β₁ takes at least two distinct values across those three seeds and the radial spectrum
  has a peak at least 3× the median of its tail.

## 4. Sensitivity arithmetic

Written before the criterion, from the existing `dt = 1.0` runs:

- **baseline** (heterogeneous, per-seed mean components) = **6.43**
- **sd between seeds** = **3.73**; homogeneous 2.86 ± 0.95
- **CV of the baseline** = **0.581**, above the 0.3 line, so the design must be **paired by seed** — it is.
- **effect worth detecting** in the count = the known +3.57 (relative 1.25); already detected with 10 seeds, no power
  problem for the re-check.
- **for β₁ the sd is unknown before the run.** Therefore no p-values are pre-declared for β₁: the rule is descriptive —
  medians and interquartile ranges, and a claim is made only if **at least 8 of 10 seeds** show the same sign of the
  heterogeneous-minus-homogeneous difference. With 10 seeds a p-value would be theatre; the sign rule is the honest
  version of the same statement.

## 5. Refusal rule

The series is declared **worthless, not negative**, if any of these holds:

1. The anchor in §6 fails — adding `--save-fields` changes the recorded series. Then the code is wrong and no data count.
2. The saved `v` arrays are missing, constant, or all-equal between arms at the same seed (a saving bug, not a world).
3. β₁ is identical in every run of both arms (the readout carries no information at this regime).
4. The radial structure factor of `v` has no peak above 3× the median of its tail in either arm (then `λ`, `q_peak` and
   `N·λ²/A` are undefined and the normalisation question cannot be asked at all).

## 6. Code change and anchor

- **Change:** add `--save-fields <dir>` to `scripts/field_track.py`; when set, write `v` as `float32` `.npy` at snapshots
  2, 4 and 6 (t = 2000, 4000, 6000), named `<out stem>_t<t>.npy`, i.e. `x60_pattern_s171_t2000.npy`. The flag must not
  consume the RNG and must be placed after the existing per-snapshot block.
- **Anchor (mandatory before the series):** rerun seed 171 heterogeneous with the flag on and compare the `series` to
  `x18_pattern_s171.json` with `python scripts/check_determinism.py`; the summary must match exactly (only `wall_seconds`
  and `config.git_commit` may differ). Recorded in the report as "anchor: bit-for-bit, old branch; new branch — determinism:
  matched/failed".
- **Disk:** 3 snapshots × 96² × 4 B ≈ 110 KB per run, 20 runs ≈ 2.2 MB; the arrays go into git because the whole point is
  that someone else can recompute β₁ without the GPU.

## Design summary

| element | value |
|---|---|
| world and settings | L1 field, Gray–Scott, 4-neighbour periodic Laplacian, grid 96, `dt = 1.0`, `Du = 0.16`, `Dv = 0.08`, `F = 0.035`, `k = 0.06`, 6000 steps, 7 snapshots |
| arms | heterogeneous inflow (`hetero_amp 0.5`, `scale 12`) against homogeneous, **paired by seed** |
| window | whole run; the count contrast additionally reported on matched times `t ≥ 2000` as in `l1_field_cadence.json` |
| readout | `components`, `beta1`, `q_peak`, `lambda`, `N_norm`; secondary: largest-cluster share, mean component area |
| seeds | 171–180 (10), of which the first 3 gate the new readouts |
| criterion | count contrast reproduces at ≥ 8/10 seeds; β₁ claim only at ≥ 8/10 same sign; λ reported with its spectrum |

## What this run decides

- whether the fragmented field is **spots** (β₀ high, β₁ low) or a **labyrinth torn by the threshold** (β₁ high) — a
  different claim about what heterogeneity does, decided by one measurement;
- whether the contrast survives **wavelength normalisation** `N·λ²/A`, which is the only route from "more pieces" to a
  statement about the medium rather than about the ruler;
- whether lifetimes in §4.5 can be reported under a persistence definition instead of the overlap rule;
- and, if β₁ turns out to be the discriminating quantity, it becomes the morphology label for every later run in this
  line, replacing the by-eye classes.

## Status

- [x] connected (hashes `628da5a16fcb` / `e32e8f6e185c` differ)
- [x] positive control fires (+3.57, 10/10)
- [x] readout exists and varies (`components`, CV 0.581); new readouts gated on 3 seeds
- [x] sensitivity computed (sd 3.73, CV 0.581, paired by seed, sign rule for β₁)
- [x] refusal rule written (four conditions above)

**Run after the anchor passes, not before.**

## Anchor result — passed, 1 November 04:20

The flag was implemented and tested before any series:

| test | result |
|---|---|
| flag is inert — `series` with and without `--save-fields` | **identical, bit-for-bit** (`_exports/anchor-x60/off.json` against `on.json`) |
| reproduces the stored artifact — all fields that existed in `x18_pattern_s171` (`step`, `components`, `areas`, `s_mean`, `s_sd_between`, `occupied`, `invader_area`, `s_wild_fraction`) | **identical** |
| summary | components `[1, 11, 15, 20, 3, 6, 6]`, `splits` 482, `parent_child_pairs` 1182, `r` 0.964 |
| fields written | 3 files, 36 992 B each (`96 × 96 × float32` + header), snapshot tag `on_s171_t{2000,4000,6000}.npy` |
| wall time | 81 s without saving, 97 s with (seed 171, grid 96, 6000 steps, CUDA) |

The one difference from the old artifact is a schema addition made by later probes (`components_log`, `pulse_on`), not a
change in dynamics — the comparable fields match exactly.

Artifacts: `morphogenesis/experiments/L1_field/anchor_x60/` (two JSONs and the three arrays, so the anchor is checkable
without rerunning). The remaining 19 runs of the series are **not** started: they need the owner's go-ahead, per §3.
