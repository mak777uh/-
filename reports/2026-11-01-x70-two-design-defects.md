# X70 had two design defects; the second one made every «5/5 seeds» statement about geometry vacuous

**Date:** 2026-11-01, 16:20–17:00 MSK. **Experiment:** X70 (size heredity in the neutral world).
**Artifacts:** `x70_*_s17x.json` (old), `x70d_*_s17x.json` (dense re-log), `l1_field_x70_spatial_strata.json`.
**Status:** both defects found and documented; the first is fixed, the second is being repaired by `x70r_series.py`.

## Short version

1. The spatial control the four external answers demanded could not be run on the existing artifacts: they keep one
   component snapshot per 1000 steps, so the structures present at a daughter's birth are mostly unknown — 50 of 925
   events matched with a tolerance, and those 50 were not a random subsample. The world was re-logged denser
   (`--sample-every 50`, field every 200 steps); the anchor holds bit-for-bit, so only the record changed.
2. On the dense record the control *passed* — and the passing numbers were identical to three decimals in all five seeds
   (0.441 every time). That was the tell: **in the neutral world the geometry does not depend on the seed at all.** The
   initial blob is fixed, and the seed reaches only the trait channel, which has no feedback (`beta = 0`, `eps = 0`). The
   five "seeds" are one universe with five different inert trait noises: `uid_pairs`, `areas` and `peaks` are identical,
   only `s_at_birth` and `s` differ.
3. Consequences, all of them corrections to what was written this morning: the 925 division events are **185 events
   copied five times**, the homogeneous arm's 100 events are **20 events copied five times**, and any «5/5 seeds» or
   «10/10 seeds» statement about X70 geometry is one observation, not five. Re-derived with the correct unit, the pairing
   null moves from p95 = 0.054 to **p95 = 0.127** (185 events), and the homogeneous arm stops being evidence at all
   (0.294 against p95 = 0.362, empirical p = 0.14).
4. What survives is the heterogeneous pattern arm: **185 events, correlation 0.334, against a pairing null with p95 =
   0.127** (empirical p < 0.0005). It is one world, so the honest wording is "in this world" and not "in five seeds".
5. To get genuine replication a knob was needed that moves the world without adding feedback: `--init-jitter` shifts the
   starting blob by the seed and varies its radius by ±20 %. Flag off reproduces the old artifacts bit-for-bit (checked on
   seed 171: `series`, `uid_pairs`, `uid_outcomes` identical). Flag on is deterministic per seed (two runs identical).
6. `x70r_series.py` ran the same neutral world with five genuinely different starting points (1034 events, per-world
   correlation 0.42–0.57), and all three controls were re-run on those worlds. Outcome: **heredity survives** — observed
   0.582 against a nearest-distance surrogate of −0.003, partial 0.545 controlling distance, occupancy and the local field.
   Numbers and verdict in [`2026-11-01-x70-spatial-control-result.md`](2026-11-01-x70-spatial-control-result.md). This
   report is kept as the record of the two defects, not as the result.

## What exactly was run

| step | command | what it produced |
|---|---|---|
| dense re-log | `python scripts/x70d_series.py` | `x70d_{pattern,homog}_s171-175.json`, 121 snapshots instead of 7, field every 200 steps |
| anchor | compare the 7 shared rows, `uid_pairs`, `uid_outcomes` | identical in both arms; `components_by_threshold` identical too |
| stratified control | `python scripts/x70_spatial_strata.py --prefix x70d --fields --write` | `l1_field_x70_spatial_strata.json` |
| corrected null | pairing shuffle inside one world, 2000 draws | pattern p95 = 0.127; homog p95 = 0.362 |
| replication | `python scripts/x70r_series.py` | `x70r_*_s171-175.json`, same world, five starting blobs |

## The stratified control, described before its numbers

The first control demanded a non-parent structure at the parent–child distance within ±4 cells; only 50 of 925 events
survived it and those were in tight, actively dividing places. The second design keeps every event: the surrogate is the
non-parent structure present at the daughter's birth that is **closest in distance** to her, and the observed-versus-
surrogate comparison is made **inside distance bins** (pooled quartiles), repeated inside occupancy tertiles, with a rank
partial correlation controlling distance and occupancy. A third pass uses the field itself: mean `v` and occupied fraction
in a radius-8 disc around the daughter's centroid, from the snapshot within 200 steps of her birth, both as strata and as
covariates. The decision bands were fixed in `docs/plan/10d-field-metrics-and-form.md` §10ep before any of this ran.

On the five copies (the only data available at that point) the control said: observed 0.441 against surrogate 0.018,
difference +0.423, present in the three nearest distance bins (0.65, 0.56, 0.56) and absent in the farthest (0.00),
partial correlation 0.513 controlling distance and occupancy and 0.444 after adding the two field statistics. The local
environment does not predict the parent's size (0.03) but does predict the daughter's (−0.32), so it cannot be the shared
cause; in its driest tertile the parent–daughter correlation is 0.055, i.e. heredity shows up only where the field is
locally rich.

**None of those numbers is independent evidence.** They are one world's 165 events, seen five times. They are written down
here because the pattern — heredity present at short distance, absent at long distance, absent in the driest environment —
is what the re-run has to confirm or destroy, and because stating it before the re-run is the only way it can be a
prediction rather than a fit.

## Blast radius, measured rather than assumed

The check is a hash of the `series` rows with the trait columns (`s_mean`, `s_sd_between`, `s_wild_fraction`,
`components_log`) removed, per seed, per arm. One distinct hash across seeds means the geometry was one world; 5–9 distinct
hashes means the seeds really did produce different worlds.

| family | seeds | distinct geometries | reading |
|---|---|---|---|
| `x70*`, `x68_ov03/05/07` (both arms) | 5 | **1** | one world, five inert copies — the defect |
| `x56_dt2.0`, `e6p_ctrl`, `e6q_ctrl_h` | 5–9 | **1** | same defect, older runs |
| `x58`, `x59_*`, `x60_*`, `x61l`, `x62_*`, `x63_*`, `x64_*`, `x65_*`, `x66_*`, `x67_*`, `e6p_surv*`, `e6q_survfd_h` | 5–9 | 5–9 | genuine replication; their «5/5»/«9/9» statements stand |

So the defect is exactly the `beta = 0` geometry arms and nothing else. This matters for today's milestone: the amplitude
dose (X59), the correlation length (X62), the scale sweep (X63), the grid map (X66), the bigger box (X67) and the
transmission ratio all have five or nine genuinely different worlds behind them. The lifetime ordering across identity
rules (X68) does not: it is one world per rule, so «0/5 seeds» there means «the single world disagrees», and the honest
form is a contrast between two single worlds that still has to be replicated.

## Why this matters beyond X70

The rule "the seed is replication" is a contract-level assumption, and in a world without feedback it is false by
construction. Anything measured on geometry alone in `beta = 0` arms has one world per configuration, however many seeds
the series index lists. The trait-channel conclusions of the day are unaffected, because the trait channel is exactly where
the seed does act; the geometry conclusions in neutral arms are affected, and the blast radius above says which ones.

## Next

1. Done: `x70r_series.py` finished, the stratified control was re-run on five genuinely different worlds, and the
   distance and environment structure of item "The stratified control" held (weakest far away, weakest in the driest
   field, parent-specific at every distance).
2. Re-read X68's seed language under the same rule; where the claim was per-seed, restate it as one world or re-run with
   `--init-jitter`.
3. Put the rule in the contract (`docs/design-checks.md`, §3c): a seed is replication only if the seed changes the world;
   a neutral world needs an explicit initial-condition knob, and the registration must name which channel the seed feeds.
