# X98 — void, and the reason is a category error worth recording: the angular map has no threshold

**Date:** 2026-11-02, 16:10 MSK. **Experiment:** X98 (registered as a threshold-robustness check on the map).
**Preregistration:** `reports/2026-11-02-x98-threshold-plan.md` (committed before the analysis).
**Artifact:** `morphogenesis/experiments/E09_pond/l1_field_x98_threshold.json`.

## Registered verdict

**Void** — the positive control fired against the check itself. The `0.20` cut was required to reproduce the committed medians within
0.01 and missed on all four cells: 0.58 against 0.385 at 0.025, 0.772 against 0.679 at 0.030, 0.903 against 0.837 at 0.035, 0.958
against 0.935 at 0.040. The control did its job.

## Why it missed — and this is the finding

`q'` and `s` in the committed aggregates are computed from the **continuous field**. My registered design computed them from a **masked**
field (`v` where `v > threshold`, zero elsewhere), and multiplying a field by a binary mask convolves its spectrum with a window
function — so the "thresholds" I compared were not cuts of the same statistic, they were four different statistics. The numbers moved by
0.02–0.07 per cell, which is exactly the size of the gap the design was trying to resolve.

In other words the question "is the angular map threshold-dependent?" is a **category error**: the angular readout does not use the
excursion threshold at all. The threshold enters the *component* side of the line — components, peak areas, `β₀/β₁`, and therefore the
memory numbers — and nowhere else.

## What the failed check does establish

Running the four thresholds anyway is informative about the map's shape, because all four agree on the ordering even though their levels
differ:

| cut | medians (0.025 → 0.040) | ordered | gaps > 0.05 | `q' = 11` present |
|---|---|---|---|---|
| masked 0.15 | 0.530 / 0.762 / 0.881 / 0.950 | yes | yes | in 1 cell |
| masked 0.20 | 0.580 / 0.772 / 0.903 / 0.958 | yes | yes | in 2 cells |
| masked 0.25 | 0.609 / 0.780 / 0.903 / 0.966 | yes | yes | in 2 cells |
| masked 0.30 | 0.635 / 0.762 / 0.885 / 0.962 | yes | yes | in 2 cells |

So under every variant of the wrong statistic the ordering of the four cells survives with gaps above 0.05, and `q' = 11` appears only as
an occasional world, never as a cell's median — consistent with X84's refutation of a systematic 8.7-cell branch. That is a weak
corroboration, not a control.

## What remains genuinely untested

**The memory numbers do depend on the excursion threshold** — `peak area` is defined on `v > threshold`, and every half-life in
§10ff–§10fl is computed from those areas. Re-deriving them at a different cut needs the genealogy rebuilt at that cut, which the stored
artifacts do not contain (the `uid_pairs` were made at 0.2 during the run). So the honest state is: the angular map is threshold-free by
construction, the memory map is threshold-dependent and **untested** at any other cut. A two-cell series at `--threshold 0.15` and
`0.25` (forty runs, ~1 h) would settle it; registered in the queue as X99, waiting on nobody.

доска: принято 0, отклонено 0, отложено 0.
