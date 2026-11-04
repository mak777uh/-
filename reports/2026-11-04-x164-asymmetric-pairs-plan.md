# X164 — The fusion crossing with unequal bodies (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

Every fusion measurement in this block used two bodies of the **same** seeded radius, so "the gap at which fusion happens"
has never been separated from "the gap between two equal discs". This item seeds one body of radius 3 and one of radius 6
at a fixed centre separation and asks whether the crossing moves. The manipulation is a new `--init-spots R1:SEP:R2` form
in `scripts/field_track.py` (the old `R:SEP` branch is untouched and the anchor confirms it: 300 steps, seed 701, 0 of 0
summary fields differ between the old and the new file).

Arms: surface gap 4, 6, 8 and 10 cells, i.e. centre separation 13, 15, 17 and 19 for the pair (3, 6). Controls: symmetric
pairs of the block's own design, r3 at gap 8 (separation 14) and r6 at gap 8 (separation 20), which in X158 fused 5/5 and
10/10. Five seeds per arm (931-935), 6 000 steps, `F` = 0.030, sample every 10 steps, everything else as in X158.

## 2. Positive control fires

The two symmetric controls must reproduce the block: r3 at gap 8 fuses in at least 4 of 5 runs and r6 at gap 8 in at least
4 of 5. If they do not, the series is not comparable to X158 and stops.

## 3. Readout exists and varies

Two readouts, both at the last logged step with two bodies: (a) the **surface gap** between the two components,
`|c1 − c2| − r1 − r2` with `r = sqrt(area/π)` and periodic boundaries, in cells; (b) the **fusion share** of the arm. The
gap must vary (standard deviation ≥ 0.1 cells across the twenty runs) and its median must lie between 0 and 6 cells.

## 4. Sensitivity arithmetic

The block's symmetric crossing is 10 ± 1 cells at every size (X158), and at one-step resolution the typical gap at the last
two-body step is 1.1-1.9 cells for the fast fusions (X166). The question here is therefore not the absolute value but the
**ratio**: with radii 3 and 6 the surface gap is the same quantity but the bodies differ by a factor of two, so a crossing
governed by the *smaller* body's diffusion length would move the surface gap the pair tolerates by roughly the ratio of the
radii, i.e. a few cells — larger than the one-cell spread the symmetric measurements showed. Five seeds per arm give a
fusion share with a Wilson interval about ±0.4 at a share of 0.5, which is enough to place the crossing inside or outside
the symmetric 10 ± 1 band; it is not enough to put an interval on the ratio itself.

## 5. Refusal rule

If the symmetric controls fail (§2), the series is not reportable. If the asymmetric arms fuse at every gap tested, the
crossing for that pair lies beyond the tested range and the item reports a lower bound only, not a number. If the
asymmetric arms fuse at no gap tested, the crossing is below the range and the item reports an upper bound. Neither is a
null result and neither is reported as "the ratio matters".

## 6. What would kill it

An asymmetric crossing inside the symmetric band (10 ± 1) with the same one-cell spread would say the crossing is a
property of the medium and not of the pair — a clean negative for the ratio hypothesis, and worth having. A crossing that
moves by a factor close to the radius ratio (two) would support it. A crossing that moves randomly between seeds would say
the seed, not the geometry, decides, and would send the item back to the design.

## 7. Implementation notes

Runner `scripts/x164_series.py`, analysis `scripts/x164_analyse.py` (fusion share, Wilson interval, gap at the last
two-body step, the same reconstruction as X157/X166). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x164_asymmetric.json`. Logs are ordinary ten-step logs and are committed as
compact projections plus the aggregate.
