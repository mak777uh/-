# X157 — where fusion actually happens (correction, 04.11.2026)

Status: closed. Source: `morphogenesis/experiments/E09_pond/l1_field_x157_gap_geometry.json`
(`scripts/x157_gap_geometry.py`, 171 two-body runs, 132 of them fusing). Queue item `X157_gap_geometry`.

**What this is.** An independent review of article 029 recomputed the mixing-length numbers from the raw worlds and
reported that (a) the radius-3 counts printed in §4.1 come from an older reach test and disagree with the M/A/P
classification, and (b) the "surface gap 9 ± 1, the same for all three sizes" is an arithmetic identity of the design,
not a measured stop: the discs grow during a run, and the arms that would show a stop at the larger radii were never run.
This report re-derives the geometry from the logs, which carry every component's area and centre every tenth step.

The review is `lab/reviews/2026-11-04-029-three-numbers.md`. It was right on both counts.

## What we now measure

**1. The bodies grow, and reach a common size before they meet.** A body seeded at radius 3 is 2.88 cells in effective
radius at the first logged step and **5.84** at the step before fusion; at radius 4.5 it goes 4.69 → 6.57; at 6, 6.00 →
8.47. Growth therefore erases most of the difference between the three sizes: by the time two bodies touch they are all
between 5.8 and 8.5 cells in radius, whatever we started with.

**2. At contact the surfaces are about two cells apart.** Over the 132 fusing runs the median surface gap at the last
step before the two bodies become one is **1.93 cells** (radius 3: 2.07 over 32 runs; 4.5: 1.89 over 30; 5.2: 1.69 over
10; 6: 1.93 over 60), with a full range of 0.9 to 4.9. This is the quantity diffusion actually sees, and it is the same
at every seeded size — the first genuinely size-independent measurement of the mixing length in this line.

**3. The design gap at which fusion stops being the rule cannot be located more precisely than 8–11 cells.** Counting a
run as "one body" when the two seeded bodies end as a single component (M and A together), the shares are:

| nominal radius | design gap 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|
| 3 | 5/5 | 5/5 | 4/5 | 2/5 | not run |
| 4.5 | 5/5 | 4/5 | not run | 0/5 | not run |
| 6 | 15/15 | not run | not run | not run | 0/5 |

So at every size fusion is the rule at a design gap of 8 cells or less, and it has stopped by 11 (4.5) or 12 (6); at
radius 3 the arm at 11 still fuses in two runs of five. The earlier claim — "the boundary is at 9 ± 1 cells, the same for
29, 64 and 113-cell bodies" — was an interpolation over three arms that were themselves the design, not a measurement,
and the arms at gaps 9–11 for the two larger sizes do not exist.

## The corrected statement

- **What the medium sets:** at contact the two bodies' surfaces are **1.9 cells apart** (median; 0.9–4.9 over 132 runs),
  i.e. about one sixth of the 12-cell wavelength, and this does not depend on the seeded size.
- **What the design sets:** two bodies fuse if their initial centre separation leaves a design gap of **8 cells or less**
  at every size tested; fusion has stopped by 11–12 cells; the boundary between 9 and 11 is unresolved because the arms
  were not run.
- **What the growth does:** the initial radius is largely erased (2.9 → 5.8 at radius 3), which is *why* the design-gap
  boundary does not scale with the seeded size — the medium makes the bodies nearly the same size before they meet.

## Consequences for article 029

1. §4.1 and the abstract's "(i)" are restated in the two quantities above; "16 ± 1" (the stopped-majority separation at
   radius 3) becomes "4 of 5 at 16 cells, 2 of 5 at 17" together with the design gap.
2. The rule `2r + 9` is withdrawn as a prediction of the third row: it was fitted to rows that were design parameters,
   and the third row (`20 ± 2`) is a bound between 8 and 12 cells, not a crossing at 20.
3. The table of three rows keeps the separations at which the outcome turns, but each row now carries the counts that were
   actually observed, and the "surface gap there" column becomes the last majority gap.
4. Figure 2 is rebuilt from this aggregate: share ending as one body against the design gap, per radius, with the
   unresolved gaps drawn as gaps rather than interpolated.
5. `docs/eliminations.md` gets a row: "the fusion boundary of the field line is at 9 ± 1 cells, the same for all body
   sizes" — refuted by X157 (it was design arithmetic, not a measurement).

## What would still kill the corrected statement

The contact gap of 1.9 cells is computed from `components_log` areas, which are the areas of the thresholded component
(`v > 0.2`), not of a fitted profile: a different threshold moves the radius and hence the gap. The report must state the
threshold; a re-run at a different threshold would move the number by roughly the thickness of the rim and is the test to
run next if anyone challenges the 1.9. The design-gap rows are five seeds per arm and are quoted as counts, not as rates.

## Next hypotheses

1. Recompute the contact gap at threshold 0.1 and 0.3 from the same logs after re-running a subset of arms (the threshold
   is a parameter of the tracker, so this needs a series, not a re-read).
2. Run the missing arms: radius 4.5 at design gaps 10 and 11, radius 6 at gaps 9, 10 and 11, ten seeds each — this is
   the only way the "8–11 cells" band becomes a crossing.
3. Ask whether the 1.9-cell contact gap is set by the wavelength (12 cells) or by the diffusion ratio, by repeating at a
   second wavelength (`F` = 0.030 against 0.040 changes the wavelength of the lattice as well as the shape of the docs).
