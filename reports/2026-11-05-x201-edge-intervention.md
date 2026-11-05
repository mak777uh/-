# X201 — edge-distance intervention (05.11)

Pre-registration: [`2026-11-05-x201-edge-intervention-plan.md`](2026-11-05-x201-edge-intervention-plan.md) (committed before the runs).
Aggregate: [`l1_field_x201_edge_intervention.json`](../morphogenesis/experiments/E09_pond/l1_field_x201_edge_intervention.json).
Code: [`scripts/x201_edge_intervention.py`](../scripts/x201_edge_intervention.py). CPU, `field_track.py` / X198 COMMON, 400 steps, F = 0.030.

## Question

X200 found an observational association: clone-worlds that disagreed differed in distance to the domain edge (median |Δedge| 6.0 cells vs 0). X201 intervenes: at fixed geometry, fixed phase (mod 12) and identical parameters, place the same pair at near/mid/far edge distances and read fusion.

## Design (as run)

2 geometries (r=4 gap=10 sep=18; r=4 gap=9 sep=17) × 4 phases × 3 edge bins (near <=14, mid 15–22, far >=23) × 4 seeds = 96 planned; **80 runs completed** (r4_g9 had no feasible near-bin seeds for the selected phases — R1/R2 triggered for that bin). Phases were chosen from X200's disagreeing worlds.

## Result

| arm | near (n, share) | mid (n, share) | far (n, share) | far − near |
|---|---|---|---|---|
| r4_g10 | 16, **0.0** | 16, **0.0** | 16, **0.0** | 0.0 |
| r4_g9 | (none, R1) | 16, **0.0** | 16, **0.0** | n/a |

C1 (|Δshare| >= 0.25) **fails**. C2 (>=2 phases, same-direction non-zero difference, near vs far) **fails**. C3 (phase/params preserved) holds by construction of the census (targeted phases, identical params). R1/R2 applied to r4_g9 near bin.

## Verdict

**The intervention is insensitive at these phase/position choices: outcomes saturated at 0.** The registered causal reading ("edge distance moves fusion") is **not supported** here — not because it was refuted at a sensitive operating point, but because the chosen configurations produced no fusions in any bin. This is consistent with X200's correlation being specific to the particular arm/seed placements that generated disagreement, and/or with these census-selected positions sitting in a non-fusing region of the phase/position space despite matching the phase class.

X200's core finding stands unchanged: (cell, phase) fixes local inflow but leaves position free (a labelled world). X201 does **not** establish edge distance as a general cause; it establishes that a naive edge intervention at these phases lacks sensitivity.

## Next hypotheses

1. **Sensitive edge test:** repeat the intervention on configurations with a **non-zero baseline** fusion probability (screen: pick (geometry, phase, position) strata where historical share is ~0.3–0.7), so C1 has power. Pre-register binning and the baseline screen.
2. **Clean clone-pairs:** hold phase *and* edge distance fixed (and geometry/params) and measure true within-world disagreement — isolates noise from position.
3. **Edge band in the mixed model:** add a rounded edge-distance band as a covariate/random component to X199's fit; if it absorbs variance, the "world" effect is partly positional.

## §10 card text (for the lead)

### §10jk — X201 — edge distance intervention at fixed phase (05.11)

X200 showed that clone-world disagreements concentrate where two seeds of one phase sit at different distances from the domain edge (median |Δedge| 6.0 vs 0 cells). X201 intervened (pre-registered, 80 runs, CPU, field_track/X198 params, F=0.030, 400 steps): at fixed geometry and fixed phase (mod 12), the same pair was placed in near/mid/far edge bins (r4_g10: 16/16/16; r4_g9: mid/far 16/16, near infeasible for selected phases). **All 80 runs ended unfused (share 0.0 in every bin);** C1/C2 fail, R1/R2 apply to g9 near. The test is **insensitive at these phase/position choices** (saturated at 0), so edge distance is not established as a general cause here; X200's finding remains that (cell, phase) fixes local inflow but leaves position free. Next: a sensitive version on non-zero-baseline strata, and/or a clean clone-pair design holding edge distance fixed.