# X202 — clone-pair reproduction and clean-clone decomposition (05.11, pre-registration)

**Status:** pre-registration, written before any X202 run. New field re-runs (CPU, `field_track.py` / X198 COMMON, F=0.030, 400 steps). No physics changes.

## Question

X200 found 44/841 disagreeing worlds (5.2%) concentrated where two seeds of one phase sat at different edge distances (|Δedge| median 6 vs 0). X201's edge intervention was insensitive (saturated at 0 on the chosen strata). X202 asks, on **sensitive (non-zero-baseline) strata** drawn from X200's *reproducible* disagreeing worlds (same edge => same outcome across x196/x198 copies; different edge => different outcome): (1) do those disagreements **reproduce** on rerun with the original seeds? (2) do outcomes still disagree when phase **and edge distance** are held fixed (a clean clone, isolating noise/position beyond the edge metric)?

## 1. Manipulation is connected

Re-runs use the exact same seeds/geometry/params as the source slices (deterministic census/jitter as X198), so phase and position are identical to the originals. The "edge-varied" arm replays the two members of a reproducible disagreeing pair (different |Δedge|). The "edge-fixed" arm searches, for the same (cell,phase), additional seeds whose realized edge distance equals one member's edge (±0 cells) — if found, phase and edge are both fixed. Manipulation is position/seed at fixed physics.

## 2. Positive control fires

Positive control = **reproduction of the historical pair**: for each selected world, rerunning the two original seeds must reproduce at least one of the two historical outcomes per member and, pooled over the selected pairs, the rerun disagreement rate must be **>= 50%** of the historical disagreement direction (i.e. the sensitive signal is real, not a logging artifact). Fires if >= 3 of 6 selected pairs reproduce their original (fused, unfused) ordering/difference.

## 3. Readout exists and varies

Readout: binary fusion (component count reaches 1 over 400 steps), identical to X198/X200. Selected strata are X200 worlds with historical 50/50 outcomes across edge-different members and cross-copy agreement (reproducible) — so baseline variation exists by construction.

## 4. Sensitivity arithmetic

6 worlds × 2 original members (repro, 12 runs) + up to 2 edge-fixed alternates per world where feasible (<=12 runs) = **~18–24 runs** total, 400 steps CPU each. This is a targeted sensitivity check, not a precision estimate: 6 reproducible pairs give clear directional read (reproduce vs not; disagree at fixed edge vs agree). Feasibility of edge-fixed alternates is reported (R1).

## 5. Refusal rule

- **R1 (edge-fixed feasibility):** if < 4 of 6 worlds yield >=1 edge-fixed alternate seed (same phase, |Δedge|==0 to a member), the clean-clone arm is under-powered and reported as descriptive only.
- **R2 (non-reproduction):** if < 2 of 6 pairs reproduce their historical disagreement on rerun, the stratum is not a stable sensitive signal; conclude non-reproducible/noise and do not attribute to edge.
- **R3 (phase/param check):** any rerun whose recomputed phase/params differ from target is excluded and reported.

## Criteria (registered)

- **C1 (reproduction):** >= 3/6 selected pairs reproduce the historical disagreement (opposite outcomes) on rerun.
- **C2 (edge, sensitive):** among reproduced-disagreeing pairs, the outcome tracks edge distance in the same direction as the historical pair in >= 3/4 of such pairs.
- **C3 (clean clone):** among worlds with edge-fixed alternates, within-(phase,edge) disagreement rate is reported; if > 0 with n>=4, position/seed noise exists beyond edge. (Descriptive threshold, given small n.)

## Artifacts

`scripts/x202_clone_repro.py --write` → `morphogenesis/experiments/E09_pond/l1_field_x202_clone_repro.json`; report `reports/2026-11-05-x202-clone-repro.md`; card §10jl (next after jk).