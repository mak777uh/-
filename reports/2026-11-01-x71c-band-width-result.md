# X71c: the band is narrow — mixed at 0.037, not at 0.033, so the window is 0.002–0.005 wide at this threshold

**Date:** 2026-11-01, 23:10 MSK. **Experiment:** X71c (width of the multistable band).
**Preregistration:** `reports/2026-11-01-x71c-band-width-plan.md`.
**Artifacts:** `morphogenesis/experiments/L1_field/x71c_f{033,037}_pattern_s171-175.json`,
`_x71c_fields/`, aggregate `morphogenesis/experiments/E09_pond/l1_field_x71c_width.json`.

## Result

Two half-steps either side of the boundary cell, same 24 000-step protocol:

| inflow | mixed worlds (of 5) | states | peak / second-mode shares |
|---|---|---|---|
| 0.033 | **3** | mixed, mixed, single, single, mixed | 0.29–0.40 / **0.19–0.23** |
| 0.035 (X71b) | 5 | mixed ×5 | 0.23–0.40 / 0.21–0.26 |
| 0.037 | **4** | mixed, mixed, single, mixed, mixed | 0.25–0.42 / 0.16–0.28 |

The pre-registered bar was 4 of 5. `0.037` meets it, `0.033` does not, so the registered verdict is **narrow**: the band
covers `0.035–0.037`, i.e. `0.002 < width < 0.005` — the earlier "one sweep step" statement is now a measurement with an
upper and a lower bound, not a resolution artefact.

## The honest caveat, which the numbers make unavoidable

At `F = 0.033` two worlds sit at second-mode shares of **0.197** and **0.190** — a hair under the 0.2 threshold. At
`F = 0.037` one world is at 0.156 (clearly single). So the lower edge of the band is **knife-edge at the chosen threshold**:
if the cut were 0.19 instead of 0.20, `0.033` would be 5/5 mixed and the band would be twice as wide. The measurement is
therefore "the band's lower edge lies within a few hundredths of the 0.2 second-mode cut", not "the band is 0.003 wide" in
any threshold-independent sense.

That is a property of the instrument, and it is reported rather than smoothed: a band measured by a threshold is only as
sharp as the threshold, and the X71b observation (shares constant to two decimals over four horizons) is what makes the cut
defensible at all — the second mode is not drifting through 0.2, it sits just above or just below it.

## What this changes

- The multistable region is **narrow** (2–5 thousandths of inflow) but **stable in time** (X71b). Both statements are needed:
  a narrow band that persists for 24 000 steps is a real state of the medium; a wide band that decayed would be a transient.
- For any future "branch heredity" experiment the boundary inflow must be tuned to ±0.002, which the sweep now supports.
- The claim row in `manuscript/CLAIMS.md` keeps its status; the width and its threshold sensitivity belong in the report and
  in §10ev, which is where a reader will look for "how wide".

## What it does not say

- It does not locate the edges better than ±0.002 — that is the sweep's resolution, and reaching further needs quarter-steps.
- It does not say the band is symmetric around 0.035; measured, it is `[0.033, 0.035)` excluded and `[0.035, 0.037]` included,
  and the asymmetry is within one step.
- One box (96), one `k`, one threshold, five worlds per cell.

## Next

Quarter-steps (`0.034`, `0.036`) would halve the uncertainty, but the more informative experiment is different: hold
`F = 0.037` and re-run the second-mode cut at 0.15 and 0.25 to measure how much of the band's edge is instrument and how much
is the medium. That is a re-analysis of existing fields, not a new series.
