# X103c / X103d — position does matter, it is maternal, and there is a crowding term nobody asked for

**Plans:** [`2026-11-02-x103c-birth-distance-plan.md`](2026-11-02-x103c-birth-distance-plan.md) (17:10 MSK),
[`2026-11-02-x103d-peak-null-plan.md`](2026-11-02-x103d-peak-null-plan.md) (17:20 MSK), both registered before their runs.
**Aggregates:** `l1_field_x103c_birth_distance.json`, `l1_field_x103d_peak_null.json`. X100's twenty runs, no GPU.

Two voids came first ([`2026-11-02-x103-basin-position-void.md`](2026-11-02-x103-basin-position-void.md)): the basin-based design
lost pairs to a coverage denominator (0.599 against a 0.60 gate) and then, with the denominator fixed, failed its selection control
— the 54 pairs it lost at `F = 0.030` had much larger daughters (median 80 against 53). So the question was asked again without a
basin: the distance from the mother's peak centroid to the daughter's birth centroid, which exists for every pair whose two
structures were logged at all (`coverage_logged` = 1.000 in both cells; the structural loss of 6.5 % and 35.3 % is the world's
logging resolution, reported as such).

## X103c: the distance predicts nothing in the lattice and a lot in the maze

| inflow | pairs | median distance (cells) | ρ(distance, daughter area) | ρ(mother area, daughter) | partial area given distance | partial distance given area | worlds negative |
|---|---|---|---|---|---|---|---|
| 0.030 | 2 024 | 4.87 | **−0.008** | 0.531 | 0.570 | −0.246 | 7/10 |
| 0.040 | 1 139 | 10.82 | **−0.367** | 0.384 | 0.552 | −0.543 | **10/10** |

Registered verdict: **mixed** — the two cells disagree, and the answer is not one number. The maze-cell coefficient is not a pooling
artefact: all ten worlds are negative and the per-world values run from −0.21 to −0.45. In the lattice cell the per-world values
straddle zero (+0.22 to −0.13).

Two facts in that table matter as much as the coefficient:

1. **The mother's excursion area keeps its predictive power when the distance is controlled** — and gains a little (0.531 → 0.570,
   0.384 → 0.552). That is the criterion the preregistration set for "the topographic reading wins", and it did not fire. Position
   does not replace the inherited width.
2. **The distance term is negative**: a daughter born farther from her mother's peak grows into a *smaller* excursion. In the maze
   cell, where 57 % of daughters are born outside their mother's basin, that is a decay of the excursion with distance from the
   mother's maximum.

## X103d: the confound, tested and rejected

The obvious way to explain the maze coefficient was local geometry: in a labyrinth, "distance from a peak" is nearly the same
coordinate as "half-width of the arm", so *any* peak would do. The null readout is the distance to the nearest **non-ancestor** peak
at the daughter's birth step (ancestors and the mother excluded by walking `uid_pairs` upward):

| inflow | ρ(distance to the mother's peak) | ρ(distance to the nearest stranger peak) | contrast | worlds negative (mother / stranger) |
|---|---|---|---|---|
| 0.030 | −0.008 | **+0.358** | −0.350 | 7/10 / **0/10** |
| 0.040 | **−0.367** | +0.103 | **+0.265** | **10/10** / 2/10 |

Registered verdict for the maze cell: **maternal**. Stranger peaks do not carry the mother's information — they carry the *opposite*
sign, and weakly (0.10 against the mother's 0.37).

**And the internal null cell was not null.** The plan called the lattice cell a check with both coefficients near zero; instead the
stranger-peak distance is **+0.358 with all ten worlds positive**, i.e. a daughter born far from other peaks grows larger. That is a
crowding term — the distance to the nearest competitor, not to the mother — and it is a finding in its own right, not a defect of
the contrast: its sign is opposite to the maternal term, its per-world sign agreement is perfect, and it is exactly the kind of
quantity a medium-level account of size should have.

## What the three readouts together say

Size in this medium has (at least) three sources, and they are separable:

| term | lattice (0.030) | maze (0.040) | what it is |
|---|---|---|---|
| mother's excursion area | **0.531** | **0.384** | the inherited width of the excursion (X100–X102) |
| distance to the mother's peak | −0.008 | **−0.367** (10/10) | maternal decay: farther from her maximum, smaller |
| distance to the nearest stranger peak | **+0.358** (10/10) | +0.103 | crowding: farther from a competitor, larger |

Heredity is therefore *not* exhausted by the excursion width: in the percolating cell there is a maternal positional term, and in the
lattice there is a competitor term. None of the three replaces the others — each survives partialling out the others' variables (the
area's coefficient rises rather than falls when the distances are controlled).

This is a coherent picture of a medium rather than a mechanism, and it sharpens the X100–X102 claim instead of contradicting it: the
excursion set is what is *inherited*, and where a daughter sits decides how much of that inheritance she can express.

## Caveats

- Both cells are one box, one grid, one `k`, one excursion cut (0.20); X99's cut sensitivity applies to every area in the table.
- The maze cell's 1 139 pairs are 35 % of its genealogies — the ones whose structures lived long enough to be logged twice. Every
  maze number is a statement about **long-lived** structures; X92's area–lifetime relation says that is not a neutral selection, and
  X103b measured the 0.030 analogue of it (ratio 0.66 on 54 pairs). The dense-logging run (X105) is registered to remove it.
- The stranger-peak distance uses components present at the daughter's birth step; in a world with one giant component there is no
  stranger and the pair drops out (coverage 1.000 here, so this did not bite).
- The three terms are descriptive correlations on the same 2 000 and 1 100 pairs, not independent experiments: they are reported
  together because they were measured on the same pairs and separate in the partials.

## Next

- **X105 (registered, needs runs):** ten worlds per inflow at `--sample-every 10` instead of 50, so the maze cell's structural loss
  falls from 35 % to a few per cent and the maze numbers stop being about long-lived structures only. CPU only; logging density
  identical in both cells (the X85 rule).
- **X106 (registered, analysis):** the crowding term on its own — does the distance to the nearest stranger peak also predict the
  mother's area, and does it predict lifetime as well as size? If it predicts both, "crowding" is a geometric constraint on
  persistence, not on growth.

доска: принято 0, отклонено 0, отложено 0.
