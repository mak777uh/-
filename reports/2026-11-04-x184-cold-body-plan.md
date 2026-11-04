# X184 — Controlling the local inflow at the colder body (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

The medium's fixed pattern makes the inflow at a site `F_local = F * (1 + 0.5 * (2G - 1))` with
`G = (sin(2*pi*y/12) * cos(2*pi*x/12) + 1) / 2`, and `--init-spots` places the pair at a site jittered by
`default_rng(seed + 9187)`, so both `F_local` values of a pair are computable before the run. X183 asked which of the candidate
readings of "the pair's inflow" organises the block's own rate ladder (109 runs at radius 3, measured gap 10, `F` = 0.026 to
0.036) and answered it: the nominal rate discriminates with AUC 0.606 and cannot discriminate at all within a level (0.5 by
construction), while **the local inflow at the colder of the two bodies** discriminates with AUC 0.878 overall and a mean of
0.898 *within* the four nominal levels, and it halves the deviance of a one-parameter logistic fit (96.9 against 144.6). The
midpoint phase, the natural first guess, is anti-predictive (AUC 0.213).

This item makes that manipulation explicit rather than observational: **seeds are selected by the local inflow at their colder
body**, so the same nominal arm is run at five chosen levels spanning the full factor-of-1.5 range.

## 2. Positive control fires

The control fires if the recomputed local inflow at the colder body lands inside its level (tolerance 0.002 in `F_local`, about
0.07 of `F`), the peak stays in [0.05, 2.0] at every read, and the extreme levels are at least **0.018 apart in `F_local`**.
Thresholds: tolerance 0.002, separation 0.018. A run whose recomputed level misses is reported and excluded, with the level's
count reduced.

**Amendment before the run (04.11, recorded rather than silently applied).** The registered separation of 0.030 assumed the
colder body's inflow could be driven to the pattern's ends (0.015 to 0.045). It cannot: `--init-spots` places the two bodies
**horizontally**, `SEP` = 16 cells is 120 degrees of the pattern's 12-cell period, so when one body is cold the other is
middling — the colder body's inflow is capped. Measuring the cap over 4 000 seeds gives **0.015 to 0.0375**, and no seed reaches
0.045. The levels are therefore re-set to five points spanning that range (0.0155, 0.020, 0.025, 0.030, 0.036), the registered
separation becomes 0.018 and is stated in the analysis; the prediction's intervals below are unchanged, since they were read
off X183's ladder in `F_local` and not off the wildly-wrong span.

## 3. Readout exists and varies

Primary: the share at each level with its Wilson interval. Secondary: X170's contact-time corridor where at least three runs
fuse, reported as a description per level, never as a comparison.

## 4. Sensitivity arithmetic, and the prediction

Radius 3, gap 10, `F` = 0.030, 2 000 steps, six seeds per level, five levels (30 runs). Registered **before the run**, from
X183's ladder (shares 0.30, 0.41, 0.40, 0.65 at nominal rates 0.026, 0.030, 0.033, 0.036) read through the local-inflow law:

- coldest level (`F_local` ≈ 0.015-0.017): **share 0.05 to 0.40**;
- warmest level (`F_local` ≈ 0.035-0.038): **share 0.45 to 0.95**;
- the five levels ordered by `F_local` show a **positive** trend; Cochran–Armitage one-sided for the positive direction with a
  registered threshold of `p < 0.05`.

Six runs per level give a share standard error near 0.2, so the design sees a bottom-to-top gap of 0.4 or more; a monotone
trend in the opposite direction would refute X183's answer, and a flat result would say the ladder's collapse was a
within-ladder accident. The narrower span is the design's main weakness and is stated as such in the report.

## 5. Refusal rule

If the share rises with the local inflow at the colder body and the one-sided p is below 0.05, the item is recorded as **the
run-level rate is the local inflow, and the nominal rate is a site average** — with the consequences stated: the block's
crossing and band statements are re-read in `F_local` (in particular the per-arm share dispersion is the site spread, not
noise), and the "cliff" reading of X178 is partly the spread of `F_local` inside one nominal arm. If the share is flat, the
item is recorded as **the collapse was an artefact of the ladder** and the nominal form of the block's statements stands. If
the share falls with the local inflow, the observation is reversed under control and the readout needs re-examination.

## 6. What would kill it

The cell is not saturated at either end (X181 and the ladder put its nominal share near 0.4), so the design should have room;
but each level is six runs, and a level landing on 0 or 6 carries no information about the trend. The report gives every
level's Wilson interval and does not count a saturated level as evidence. The colder body is used because X183 says so; if the
causal site is instead the bridge between the bodies, the level labels will scatter, and that outcome is recorded as a failed
identification rather than as a null effect.

## 7. Implementation notes

Runner `scripts/x184_cold_body.py` selects seeds by `min` of the two bodies' `G` (computed with the runner's own copy of the
arithmetic) and runs radius 3, gap 10, `F` = 0.030, seeds from the low thousands that are not used by X181 or X182. Analysis
`scripts/x184_cold_body_analyse.py` recomputes both bodies' `G` from the logged centres, reports per-level shares with Wilson
intervals and the Cochran–Armitage one-sided test on `F_local`, and the corridor description. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x184_cold_body.json`. Cost about fifteen minutes of CPU.
