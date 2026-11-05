# P0 — behavior metric under deadly price + gradient flip (05.11, pre-registration)

**Status:** pre-registration before the registered metric runs. Builds on `docs/plan-alive.md` P0 (deadly price exists; metric is open). Uses `morphogenesis.world.run_pond.PondRun` with gradient layout + `flip_at`, proportional income, prefilled resource, and lethal upkeep (calibrated so both deaths and survivors occur). No physics/world changes.

## Question

After the environment flips, does survival differ between the "correct" (resource-rich) and "incorrect" (resource-poor) zone? (Plan-alive P0 criterion: after the flip, survival in the correct zone must statistically differ from the incorrect one; otherwise the environment is still indifferent to behavior.)

## 1. Manipulation is connected

The environment is a gradient resource field (rich/poor by row, via pond gradient position). At `flip_at` the gradient inverts (`_gradient_position`), so the spatially rich side moves. The metric reads, per step, alive cells and cumulative deaths in `rich/mid/poor` zones (same zone definition as `pond.state.deaths_by_zone`: rich > 2/3*resource_max, poor < 1/3). Before/after split is by step < `flip_at` vs >= `flip_at`. No world code changes.

## 2. Positive control fires

Positive control = **deadly price produces both deaths and survivors** (price matters). The control fires if, over the registered run (3 seeds, 300 steps), mean deaths >= 10 and mean final alive >= 10 (non-degenerate). If both are ~0 (no pressure) or alive ~0 (total collapse), the regime is not a valid test of behavior-under-pressure and is reported as a calibration failure (R1), not as "environment indifferent".

## 3. Readout exists and varies

Readouts: (a) alive-population share in rich vs poor, integrated before and after flip (`alive_rich / (alive_rich+alive_poor)` per period); (b) deaths rich-share; (c) final alive/died. They exist per step from pond state/zones and vary when the population occupies zones.

## 4. Sensitivity arithmetic

3 seeds × 300 steps (flip at 150) at grid 32. With the positive control met (>=10 deaths and >=10 alive on average), a consistent rich-zone occupancy bias (e.g. share 0.65 vs 0.35) across seeds is detectable as a directional difference; per-seed before/after and cross-seed mean are reported. This is a directional/criterion check per plan-alive, not a high-precision effect-size estimate.

## 5. Refusal rule

- **R1 (degenerate):** if positive control fails (mean deaths < 10 or mean alive < 10), report calibration failure; do not interpret zone differences.
- **R2 (no occupancy):** if (alive_rich+alive_poor) integrated count is < 20 in a period, that period's share is undefined/reported as no-occupancy.
- **R3 (honesty):** "environment indifferent to behavior" is claimed only if R1 passes and rich-share after flip is not distinguishably different from before (same direction/magnitude across seeds reported; with 3 seeds, report concordance, not a p-value claim).

## Artifacts

`scripts/p0_flip_metric.py` → `morphogenesis/experiments/E09_pond/p0_flip_behavior.json` (+ per-seed rows); report `reports/2026-11-05-p0-flip-behavior-metric.md`; card in plan-alive follow-up / pond as appropriate.