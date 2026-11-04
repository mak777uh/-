# X182 — Controlling the seeded site's local inflow (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X180 read the code and found where between-family dispersion comes from: `F_eff = F * (1 + hetero_amp * (2G - 1) * (2S - 1))`
with `S = 1` and `G = (sin(2*pi*y/12) * cos(2*pi*x/12) + 1) / 2`, a pattern **fixed for every seed** — so the inflow a pair
actually sees is `F_local = F * 2G` at the site where it is seeded, a factor between 0.5 and 1.5 of the nominal rate, set by the
seed's placement. X180 then found, across 17 cells with both outcomes present, that the runs which fuse sit at **lower** local
`G` (mean point-biserial −0.555; among non-saturated runs −0.529; the bottom local-inflow quartile fuses 83 % against 14 % in
the top, z = −8.06).

That correlation is per seeded site but not *controlled*: positions came from a jitter that is a deterministic function of the
seed, so `G`, the seed and any other seed-determined detail move together. This item makes the manipulation explicit — it
**selects seeds by their local `G`** at the site they seed, which is computable in advance from `default_rng(seed + 9187)`, so
the same nominal arm is run at five chosen levels of local inflow.

## 2. Positive control fires

The control fires if the pair's local `G` at the midpoint of the two seeded bodies, recomputed from the logged centres of each
run, lands inside the level it was selected for (tolerance 0.05), the peak stays inside [0.05, 2.0] at every read, and the
extreme levels are at least **0.5 apart in `G`** (i.e. a factor of at least two in `F_local`). Thresholds: 0.05 tolerance, and
0.5 of separation between the extreme levels. If the recomputed `G` disagrees with the selection in any run, that run is
reported and excluded, and the level's count is recorded as reduced.

## 3. Readout exists and varies

Primary: the share at each level with its Wilson interval. Secondary: X170's contact-time corridor where at least three runs
fuse, which must vary (sd ≥ 0.02).

## 4. Sensitivity arithmetic, and the prediction

Radius 3, gap 10, `F` = 0.030, 2 000 steps, **6 seeds per level, 5 levels** (30 runs), with the levels chosen from the observed
`G` range at that arm's grid positions so that the extremes differ by more than 0.5 in `G`.

Registered **before the run**, from X180's band table:

- bottom level (`G` ≈ 0.05-0.2, `F_local` ≈ 0.003-0.012): **share 0.5 to 1.0**;
- top level (`G` ≈ 0.8-0.95, `F_local` ≥ 0.048): **share 0.0 to 0.35**;
- the five levels ordered by `G` show a **negative** trend, tested with Cochran–Armitage on the selected levels' `G` values
  (one-sided for the negative direction), and the registered threshold is `p < 0.05` there.

With six runs per level the share's standard error is about 0.2, so the bottom-to-top gap of 0.6-0.7 is what the design can
see; a single level falling outside its interval is reported as noise rather than as a broken prediction, but a *monotone*
trend in the opposite direction would refute X180's reading.

## 5. Refusal rule

If the share falls with local `G` as predicted and the trend's one-sided p is below 0.05, the item is recorded as **the local
inflow is the hidden variable of the crossing**, and the consequence is written plainly: all of the block's crossing statements
should be re-read in `F_local = F * 2G`, and the nominal rate is a site-average rather than a per-run rate. If the share is flat
across levels, the item is recorded as **X180's correlation is not causal** — the seed, not the site, carries the effect — and
the band and crossing statements keep their original (nominal-rate) form. If the share rises with local `G`, the observation is
**reversed under control** and the block's readout itself needs re-examination.

## 6. What would kill it

The arm sits inside the steep part of the fusing range, so a level may saturate at 0 or 1 and carry no information; the design
therefore reports each level's Wilson interval and does not count a saturated level as evidence for the trend. And the
corridor, which needs several fusions per level, will be thin: six runs per level give a median on at most six contacts, so the
corridor is reported as a **description** of the levels, never as a comparison.

## 7. Implementation notes

Runner `scripts/x182_local_inflow.py` — seed selection helper inside the runner: for a target level, scan seeds and compute the
jittered site from `default_rng(seed + 9187).integers(-g//4, g//4+1, size=2)` with `g = 96`, evaluate
`G = (sin(2*pi*y/12)*cos(2*pi*x/12)+1)/2` at the pair's midpoint, and take the first six seeds in the level's band. Analysis
`scripts/x182_local_inflow_analyse.py` recomputes `G` from the logged centres, reports the per-level shares with Wilson
intervals, the Cochran–Armitage one-sided test on the selected `G`, and the corridor description. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x182_local_inflow.json`. Cost about fifteen minutes of CPU.
