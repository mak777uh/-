# X66: the map, and the withdrawal of my own withdrawal

1 November 2026, 13:05. Twenty runs at two new grids. Preregistration:
[`2026-11-01-x66-grid-map-plan.md`](2026-11-01-x66-grid-map-plan.md), committed before the run.

Two things were wrong with the grid comparison before this run. First, the 96 point was run at `dt = 1.0` while the others
were at `0.5`, so the map mixed resolution with time step. Second, and worse, after X65 I had been reading the map through
**concentration** (share and entropy) instead of through **where the peak sits**. This run fixes both.

## The map, all points at `dt = 0.5`

| grid | cells per period | homogeneous peak | heterogeneous peak | heterogeneous share | H/ln |
|---|---|---|---|---|---|
| 96 | 12 | **none** (q = 1, box scale) | q = 1 (box) | 0.429 | 0.661 |
| 108 | 13.5 | **12 units** | q = 1 (box) | 0.162 | 0.802 |
| 120 | 15 | **12 units** | 8.73 units | 0.307 | 0.665 |
| 144 | 18 | **12 units** | q = 1 (box) | 0.447 | 0.616 |

## What it says

**1. The homogeneous world selects 12 units wherever it patterns at all** — 108, 120, 144. On 96 at `dt = 0.5` it does not
pattern inside the same physical time (its peak is still the box). That is a resolution effect with a sharp edge: a pattern
with a 12-unit wavelength needs more than 12 cells per period at this step. At `dt = 1.0` the same 96 grid *does* pattern,
so the requirement is step-dependent — consistent with everything else we have measured about this scheme.

**2. The heterogeneous world never peaks at 12 units — on any of the four grids.** Its peak is either the box mode
(q = 1: 96, 108, 144) or an intermediate scale (8.73 units at 120). Concentration varies (share 0.16 to 0.45) but the
*position* does not: it is never the medium's wavelength.

**3. Which means the withdrawal of X60 was itself wrong.** At 11:00 I withdrew "heterogeneity prevents wavelength selection"
because at 144 the heterogeneous arm's normalised entropy (0.61) matched the homogeneous one's (0.62). That comparison used
concentration and ignored position — and position is what the sentence was always about. At 144 the heterogeneous arm is
concentrated **on the box scale**, not on 12 units. So the original claim stands, and it stands more sharply than before:
heterogeneity does not stop the field from concentrating; it stops it from concentrating **on the medium's own pattern**.

I have now withdrawn and un-withdrawn this claim in the space of two hours, and both times through the same mistake in
miniature: judging by a summary number instead of by the quantity the sentence names.

## What the corrected claim is

> At 96, 108, 120 and 144 cells — with the time step held at 0.5, the physical domain fixed and the diffusion rescaled
> accordingly — the homogeneous world selects the medium's 12-unit wavelength, and the heterogeneous world does not: its
> power concentrates on the box scale or on an intermediate scale, never on 12 units. The coarse grid additionally fails to
> pattern in the homogeneous case, which sets a lower bound on the resolution a 12-cell pattern needs at this step.

## What this does not establish

- Whether the heterogeneous arm's box-scale peak is a finite-box artefact or a genuine large-scale organisation. A larger
  domain at the same Δx would answer it, and that is a different run.
- Why the heterogeneous peak sat at 8.73 units on 120 and nowhere else — one point, five seeds.
- Nothing about `dt = 1.0` maps: the four points here share `0.5`, and the 96-at-1.0 point came from a different series.

## Artifacts

`morphogenesis/experiments/L1_field/x66_g096_*`, `x66_g108_*` (40 files), fields in `x66_fields/` (60 arrays), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x66_map.json` which also reads the 120 and 144 fields from X65 and X64.
Scripts: `scripts/x66_series.py`, `scripts/x66_analyse.py`.
