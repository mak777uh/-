# X65: the bracket did not resolve — and the criterion was too narrow

1 November 2026, 12:00. Ten runs at grid 120, five per arm. Preregistration:
[`2026-11-01-x65-grid120-bracket-plan.md`](2026-11-01-x65-grid120-bracket-plan.md), committed before the run.

The point of the run was to bracket the grid transition: at 96 cells (12 cells per pattern period) the heterogeneous arm
never selects; at 144 (18 cells) it does. This put a point at 120, i.e. 15 cells per period, with two pre-declared readings.

## Result

| physical time | heterogeneous | homogeneous |
|---|---|---|
| 2000 | q = 1, share 0.242, H/ln = 0.788 | q = 1, share 0.568, H/ln = 0.534 |
| 4000 | q = 1, share 0.241, H/ln = 0.791 | q = 8, **12.00 units**, share 0.202, H/ln = 0.778 |
| 6000 | q = 11, **8.73 units**, share 0.307, H/ln = 0.688 | q = 8, **12.00 units**, share 0.224, H/ln = 0.789 |

**The criterion was met by 0.012 and I do not believe it.** The heterogeneous normalised entropy at the last snapshot is
0.688 against a bar of 0.70 — technically "already selecting", therefore "transition between 12 and 15 cells". But the
peak sits at **8.73 units**, not at the medium's 12, and the homogeneous arm at this grid is itself weak (share 0.202–0.224
against 0.43–0.45 at 96 and 144). A field that concentrates on a scale that is not the pattern's is not selecting the
pattern.

**So the honest verdict is "unmapped".** The bracket does not resolve the transition, and it shows why: my criterion
measured *concentration* but not *what was concentrated on*. The second is the substantive question and should have been in
the criterion from the start.

## What the three grids actually say

| grid | cells per period | heterogeneous peak (units) | heterogeneous share | homogeneous share |
|---|---|---|---|---|
| 96 | 12 | — (q = 1, no pattern) | 0.24 | 0.45 |
| 120 | 15 | 8.73 (not 12) | 0.31 | 0.22 |
| 144 | 18 | — (q = 1, but concentrated) | 0.447 | 0.374 |

The pattern's share rises with resolution (0.24 → 0.31 → 0.447) while the homogeneous arm is non-monotone (0.45 → 0.22 →
0.37). Whatever is happening is not a clean function of cells per period, and one bracket point was not enough to see that —
which is itself the result.

## What changes

- The X64 conclusion stands in its narrow form: at 144 the heterogeneous spectrum is as concentrated as the homogeneous
  one, and at 96 it is not. The *transition* between them is not located, and 120 shows the two arms behaving unlike either
  endpoint.
- The criterion for any future grid study must include the **peak position relative to 12 units**, not only entropy.
- The grid question needs more points, not one bracket: 96, 108, 120, 132, 144 with the same five seeds, and the peak
  position as the readout. That is about an hour and a half of GPU time and is the natural next campaign.

## What is not claimed

- Five seeds, seed-averaged spectra, no p-values.
- One bracket point cannot distinguish "smooth transition", "non-monotone", and "the 120 run is still forming".

## Artifacts

`morphogenesis/experiments/L1_field/x65_{pattern,homog}_s{171..175}.json`, fields in `x65_fields/` (30 arrays), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x65_bracket.json`. Scripts: `scripts/x65_series.py`, `scripts/x65_analyse.py`.
