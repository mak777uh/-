# X67 — is the heterogeneous peak the box, or a real 96-unit structure?

1 November 2026, 13:12. Preregistration before the run.

X66 established that on four grids (96, 108, 120, 144 cells, all at `dt = 0.5`) the homogeneous world picks the medium's
12-unit wavelength and the heterogeneous world never does: its peak sits on the **box scale** (q = 1) on three grids and on
an intermediate scale on one. That leaves the obvious objection: q = 1 *is* the box by construction, so "the heterogeneous
field organises at the domain scale" may be a statement about the boundary conditions rather than about the medium.

The test is to change the box while holding the cell size fixed. Grid **192** with Δx = 1 means a domain of **192 units**
— twice the one used in every run so far — with the same `Du = 0.16`, `Dv = 0.08`, `dt = 1.0` and the same 6000 physical
time (6000 steps, since `dt = 1.0`).

**Three outcomes, all pre-declared, and they mean different things:**

| heterogeneous peak at | reading |
|---|---|
| q = 1 (192 units) | the organisation follows the **box** — a boundary/domain artefact, not a property of the medium |
| q = 2 (~96 units) | there is a **real 96-unit structure** that the old box happened to fit exactly; the medium organises at a fixed scale, not at the box |
| q = 16 (12 units) | the field selects the medium's wavelength after all, and the earlier result was resolution-limited |

The homogeneous arm is the control: it must pattern at 12 units, i.e. q = 16 at this domain, or the run is not measuring
the same world.

## 1. Manipulation is connected

Only the domain size changes (192 cells instead of 96, cell size unchanged). The inflow keeps its physical correlation
length of 12 units = 12 cells, so the forcing pattern is the same size in the same units.

## 2. Positive control fires

The homogeneous arm must peak at **12 units (q = 16)**. If it patterns at some other scale, the mapping between domain and
wavelength is wrong and nothing about the heterogeneous arm can be read.

## 3. Readout exists and varies

Peak mode, peak share and normalised entropy, seed-averaged over five seeds, at t = 2000, 4000, 6000. Across the existing
grids the peak has landed on q = 1, on 8.73 units and on 12 units, so all three pre-declared outcomes are represented in
the data already; the readout can distinguish them.

## 4. Sensitivity arithmetic

Five seeds per arm, seed-averaged spectra, no p-values. The three outcomes are separated by **mode number**, a discrete
quantity: q = 1, 2 and 16 are far apart, and a peak within ±1 mode of any of them is unambiguous. The only risk is a
*split* peak (two comparable maxima), which is what the refusal rule covers.

## 5. Refusal rule

Worthless, not negative, if:

1. the homogeneous arm does not peak at 12 units (q = 16 ± 1);
2. the heterogeneous spectrum has two comparable peaks (within 20 % of each other) — then there is no single scale to
   report;
3. any run produces NaN or a dead field.

## Design summary

| element | value |
|---|---|
| world | L1 field, grid **192** (domain 192 units), `dt = 1.0`, 6000 steps, `Du = 0.16`, `Dv = 0.08`, `beta = 0.2`, `freq_dep = 1`, mutation 0.15 |
| arms | heterogeneous (amp 0.5, correlation 12 cells = 12 units) against homogeneous |
| seeds | 171–175 |
| fields | saved at t = 2000, 4000, 6000 |
| criterion | §4, three pre-declared modes |
| cost | ≈ 5.5 min per run, 10 runs ≈ 55 min |
| artifacts | `morphogenesis/experiments/L1_field/x67_{pattern,homog}_s*.json`, `x67_fields/` |

## Status

- [x] connected (only the domain changes; cell size and forcing fixed)
- [x] positive control fires (homogeneous at 12 units = q 16)
- [x] readout exists and varies (peaks at q = 1, 8.7 units, 12 units already observed)
- [x] sensitivity computed (mode numbers 1, 2, 16 are discrete and far apart)
- [x] refusal rule written (three conditions)
