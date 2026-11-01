# X70 after repair: heredity is pair-specific and survives every spatial control; magnitude ~0.5, not 0.33

**Date:** 2026-11-01, 16:00–17:20 MSK. **Experiment:** X70 (size heredity in the neutral world), repaired.
**Artifacts:** `x70r_{pattern,homog}_s171-175.json` (five genuine worlds), `l1_field_x70r_size.json`,
`l1_field_x70_spatial_strata.json` (`"prefix": "x70r"`).
**Reports:** this one; the design defects are in [`2026-11-01-x70-two-design-defects.md`](2026-11-01-x70-two-design-defects.md);
pre-registration in [`-x70-size-heredity-plan.md`](2026-11-01-x70-size-heredity-plan.md) and plan §10ep.

## Verdict in one paragraph

In the neutral world a daughter's peak area follows **her own** parent's, in **all five** genuinely different worlds:
correlations 0.491 / 0.468 / 0.566 / 0.423 / 0.548 (mean **0.499**), each above its own pairing null (p95 = 0.11–0.13),
slopes 0.38–0.57 (mean 0.45). The signal is not the place: against a non-parent companion at the same distance it is
**0.582 against −0.003** (841 events, difference +0.585, cluster-bootstrap 95 % interval +0.47…+0.68, 5/5 worlds above
+0.10), and the rank partial correlation controlling distance, local occupancy and two local field statistics is
**0.545**. Heredity is strong where the field is locally rich (0.18 → 0.49 → 0.63 across local-environment tertiles) but
the environment does not predict the area itself (−0.02 against the daughter, 0.11 against the parent), so richness
**modulates** heredity rather than producing it. The homogeneous arm stays **unresolved**: 73 events, 1 of 3 estimable
worlds above its own null. About **45 %** of the parent's deviation survives one division — the same "limited heredity"
category as before, with a larger and now replicated coefficient.

## What changed from the morning numbers, and why

| quantity | morning (15:00) | after repair | reason |
|---|---|---|---|
| worlds behind the pattern arm | 5 claimed, **1 actual** | 5 actual | seeds did not move the geometry in a `beta = 0` world |
| events | 925 | 1034 (175–234 per world) | five different starting blobs, not five copies |
| correlation | 0.334 | **0.499** mean (0.423–0.566) | the morning value was one draw of the starting blob |
| pairing-null p95 | 0.054 | 0.106–0.130 | the 925-event null had five copies and was too tight |
| homogeneous arm | 0.294 against p95 0.159 | 0.367 against p95 0.335; 1/3 worlds exceed | five copies of 20 events; now reported as unresolved |

The morning number was not wrong arithmetic; it was one world's arithmetic quoted as five. The tell was that the
stratified control returned 0.441 to three decimals in every seed.

## The stratified control, in the order it was decided

The four external answers demanded a control for proximity: parent and daughter share local inflow, so an area correlation
is expected even at zero transmission. Three passes were registered before their numbers (plan §10ep), and all three were
run on the repaired artifacts.

**1. Distance-stratified, nearest-distance surrogate.** Every division event is kept; the surrogate is the non-parent
structure present at the daughter's birth that is closest in distance to her; the comparison is made inside distance
quartiles.

| distance bin (cells) | events | observed | surrogate | reading |
|---|---|---|---|---|
| 0.2–4.5 | 211 | 0.768 | −0.005 | parent specific |
| 4.5–6.6 | 210 | 0.661 | −0.012 | parent specific |
| 6.6–13.1 | 210 | 0.673 | 0.003 | parent specific |
| 13.3–59.6 | 210 | 0.225 | 0.001 | weak but positive |

Weighted: observed 0.582, surrogate −0.003, difference **+0.585**, bootstrap over (world, snapshot) clusters
**+0.47…+0.68**, and every one of the five worlds above +0.10. A companion's size does not predict the daughter's size in
any bin; the parent's does, and most strongly when it is close.

**2. Local occupancy.** Tertiles by the number of structures present at the daughter's birth: 0.422 / 0.581 / 0.433 against
surrogates 0.018 / −0.038 / 0.005. No monotone crowding story.

**3. The field itself.** Mean `v` and occupied fraction in a radius-8 disc at the daughter's centroid, from the snapshot
within 200 steps of her birth (835 of 841 events covered).

| local-environment tertile | mean v range | events | observed | surrogate |
|---|---|---|---|---|
| driest | 0.00–0.124 | 279 | 0.183 | 0.015 |
| middle | 0.124–0.148 | 278 | 0.488 | 0.013 |
| richest | 0.148–0.199 | 278 | 0.630 | −0.048 |

So heredity is **modulated by the local environment** — weak in the driest third, strong in the richest — but the
environment is not its source: it does not predict the daughter's peak area (−0.022) and barely the parent's (0.111).
Partial rank correlation controlling distance, occupancy and both field statistics: **0.545**.

## What this does not say

- It does not say the daughter inherits a *value* faithfully. Slopes of 0.38–0.57 with intercept mean that roughly half the
  deviation is erased within one division; lines still cannot grow from this channel alone.
- It does not rescue the homogeneous arm. With 73 events over five worlds and one world above its null, that arm is
  unresolved, and the morning claim that it matched (`0.294`) was five copies of twenty events.
- The surrogate needs a companion present at birth, so the control speaks for **841 of 1034** events (81 %); the missing
  19 % are places where the daughter was the only structure, and nothing can be said about them from this data.
- Peak area is a thresholded quantity (`0.2`) and a lifetime maximum; the numbers belong to that ruler and that window
  (6000 steps, grid 96).

## Files

| what | where |
|---|---|
| five repaired worlds | `morphogenesis/experiments/L1_field/x70r_{pattern,homog}_s171-175.json` |
| size aggregate, per world | `morphogenesis/experiments/E09_pond/l1_field_x70r_size.json` |
| stratified spatial control | `morphogenesis/experiments/E09_pond/l1_field_x70_spatial_strata.json` |
| field snapshots (not committed) | `morphogenesis/experiments/L1_field/_x70r_fields/*.npy` |
| runners | `scripts/x70r_series.py`, `scripts/x70_spatial_strata.py`, `scripts/x70_analyse.py --prefix` |

## Next

1. Carry the same three-pass control to the **trait channel** (X68 lineages), where the seed does act: does a lineage's
   composition inheritance also survive a nearest-distance surrogate?
2. The zero-transmission arm has no transmission *rule*, so "heredity" here is the field's own memory. The next falsifier
   is a multistability scan of `(F, k)`: if two morphologies coexist at the same parameters, heredity should become
   bistable (daughter takes the parent's branch) rather than graded.
3. Register the `--init-jitter` knob as the standard replication route for every future `beta = 0` arm, so this defect
   cannot recur (rule in [`../docs/design-checks.md`](../docs/design-checks.md), gate
   `check_seed_replication.py`).
