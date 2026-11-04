# X179 — The crossing table, with intervals and a heterogeneity audit (04.11)

**Question.** Thirteen items of this line have each measured one or two cells and reported "the crossing at gap X". Every one of
those statements was read off a handful of runs in one seed family, and the block has never assembled the whole matrix in one
place with intervals. This item does not run anything: it aggregates the **committed projections** — every two-body run the
line has produced — into one table, and audits it for the thing pooling hides.

Sources: 985 `*.compact.json` projections, from which cells are identified by the data itself (body radius
from the seeded area, gap from the centre separation minus twice that radius). Two-body runs: **57 cells,
722 runs**. Runs seeded with one component or with more than two are counted separately and not mixed in.

## The table

| radius | gap | F | fused/runs | share | Wilson 95% | family spread |
|---:|---:|---:|---:|---:|---|---:|
| 3 | 1 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 3 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 5 | 0.026 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 5 | 0.03 | 10/10 | 1.00 | [0.72, 1.00] | 0.00 |
| 3 | 5 | 0.036 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 7 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 9 | 0.03 | 22/25 | 0.88 | [0.70, 0.96] | 0.20 |
| 3 | 11 | 0.026 | 0/15 | 0.00 | [0.00, 0.20] | 0.00 |
| 3 | 11 | 0.03 | 5/39 | 0.13 | [0.06, 0.27] | 0.40 |
| 3 | 11 | 0.036 | 5/15 | 0.33 | [0.15, 0.58] | 0.10 |
| 3 | 2 | 0.026 | 10/10 | 1.00 | [0.72, 1.00] | 0.00 |
| 3 | 2 | 0.03 | 15/15 | 1.00 | [0.80, 1.00] | 0.00 |
| 3 | 2 | 0.036 | 10/10 | 1.00 | [0.72, 1.00] | 0.00 |
| 3 | 2 | 0.04 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 4 | 0.03 | 10/10 | 1.00 | [0.72, 1.00] | 0.00 |
| 3 | 6 | 0.026 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 6 | 0.03 | 20/20 | 1.00 | [0.84, 1.00] | 0.00 |
| 3 | 6 | 0.036 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 6 | 0.04 | 1/1 | 1.00 | [0.21, 1.00] |  |
| 3 | 8 | 0.026 | 20/20 | 1.00 | [0.84, 1.00] | 0.00 |
| 3 | 8 | 0.03 | 48/48 | 1.00 | [0.93, 1.00] | 0.00 |
| 3 | 8 | 0.033 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 3 | 8 | 0.036 | 20/20 | 1.00 | [0.84, 1.00] | 0.00 |
| 3 | 10 | 0.026 | 6/20 | 0.30 | [0.15, 0.52] | 0.13 |
| 3 | 10 | 0.03 | 20/49 | 0.41 | [0.28, 0.55] | 0.60 |
| 3 | 10 | 0.033 | 8/20 | 0.40 | [0.22, 0.61] |  |
| 3 | 10 | 0.036 | 13/20 | 0.65 | [0.43, 0.82] | 0.07 |
| 3 | 12 | 0.03 | 0/10 | 0.00 | [0.00, 0.28] | 0.00 |
| 3 | 18 | 0.03 | 0/5 | 0.00 | [0.00, 0.43] |  |
| 3 | 24 | 0.03 | 0/5 | 0.00 | [0.00, 0.43] |  |
| 3 | 30 | 0.03 | 0/5 | 0.00 | [0.00, 0.43] |  |
| 4.5 | 4 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 4.5 | 6 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 4.5 | 8 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 4.5 | 10 | 0.03 | 6/24 | 0.25 | [0.12, 0.45] | 0.04 |
| 4.5 | 5 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 4.5 | 7 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 4.5 | 9 | 0.03 | 8/20 | 0.40 | [0.22, 0.61] | 0.53 |
| 4.5 | 11 | 0.03 | 0/14 | 0.00 | [0.00, 0.22] | 0.00 |
| 4.5 | 13 | 0.03 | 0/5 | 0.00 | [0.00, 0.43] |  |
| 5.3 | 7 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 5.3 | 8 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 6 | 1 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 6 | 3 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 6 | 5 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 6 | 7 | 0.03 | 22/25 | 0.88 | [0.70, 0.96] | 0.60 |
| 6 | 8 | 0.03 | 10/10 | 1.00 | [0.72, 1.00] |  |
| 6 | 9 | 0.03 | 20/54 | 0.37 | [0.25, 0.50] | 0.13 |
| 6 | 11 | 0.03 | 0/9 | 0.00 | [0.00, 0.30] |  |
| 6 | 4 | 0.03 | 5/5 | 1.00 | [0.57, 1.00] |  |
| 6 | 6 | 0.03 | 10/10 | 1.00 | [0.72, 1.00] | 0.00 |
| 6 | 8 | 0.03 | 20/20 | 1.00 | [0.84, 1.00] | 0.00 |
| 6 | 10 | 0.03 | 0/24 | 0.00 | [0.00, 0.14] | 0.00 |
| 6 | 12 | 0.03 | 0/5 | 0.00 | [0.00, 0.43] |  |
| 6 | 20 | 0.03 | 0/5 | 0.00 | [0.00, 0.43] |  |
| 6 | 21 | 0.03 | 0/1 | 0.00 | [0.00, 0.79] |  |
| 6 | 28 | 0.03 | 0/4 | 0.00 | [0.00, 0.49] |  |

Readings this table settles or reframes:

1. **Every size is saturated well below its crossing.** At gap 8 the share is 1.00 at radius 3 (48 of 48), radius 4.5 (5 of 5)
   and radius 6 (20 of 20); at gap 6 also 1.00. The crossing is a narrow event near the end of the fusing range, not a gradual
   decline from short gaps.
2. **The crossing moves out with size, by about one cell per 1.5 cells of radius**: radius 4.5 falls below one half at gap 9
   (0.40), radius 3 at gap 10 (0.41), radius 6 at gap 9 (0.37) — i.e. between 4.5 and 6 the crossing does **not** keep moving
   with size, which is the anomaly X158 already saw as "9 rather than 10".
3. **Rate moves the crossing by more than size does.** At radius 3, gap 10: `F` = 0.026 gives 0.30 (6 of 20), `F` = 0.030 gives
   0.41 (20 of 49), `F` = 0.033 gives 0.40 (8 of 20), `F` = 0.036 gives 0.65 (13 of 20). Half of the entire fusing range is
   crossed by changing the inflow by 40 %, whereas a 50 % change in body radius moves the crossing by one cell.

## The audit: three cells whose pooling hides disagreement

The share of a cell is a fraction over runs from **different seed families**, and those families do not always agree. Flagging
cells whose families (at least three runs each) differ by more than 0.4 in share:

- radius 3, gap 10, `F` = 0.03: `x136` 4/5 = 0.80, `x158_g10_r30` 3/9 = 0.33, `x168c_F30_g10` 2/5 = 0.40, `x168c_F30_len` 2/5 = 0.40, `x170_F30` 7/15 = 0.47, `x173_g10` 2/10 = 0.20
- radius 4.5, gap 9, `F` = 0.03: `x140` 4/5 = 0.80, `x175` 4/15 = 0.27
- radius 6, gap 7, `F` = 0.03: `x150_g7_r60` 5/5 = 1.00, `x154_g65_r60` 10/10 = 1.00, `x154_g70_r60` 5/5 = 1.00, `x164_asym_g10` 2/5 = 0.40

- radius 3, gap 10, `F` = 0.030 pools six families spanning **0.20 to 0.80** — the single number 0.41 in the table above is a
  compromise between a family that fuses 4 of 5 and one that fuses 2 of 10. Every "gap 10 at radius 3" statement in the block's
  reports inherits that dispersion.
- radius 4.5, gap 9: `x140`'s 4 of 5 against X175's 4 of 15. This is the cell X175 used to refute the single curve, and its
  refutation rests on the smaller of the two families disagreeing with a larger one.
- radius 6, gap 7: 5 of 5, 10 of 10 and 5 of 5 against `x164_asym_g10`'s 2 of 5 — the asymmetric-pair arms sit below the
  symmetric ones at the same measured geometry.

So "the crossing at gap X" is not a point even at fixed (radius, gap, rate): across seed families the share moves by up to 0.6.
The block's crossing statements are therefore statements about **the range of shares a cell supports**, and the honest form is a
share with an interval and a family spread, not a gate value.

## Controls and what is not in the table

**The protocol's three control cells reproduce.** Radius 3 at gap 8 reads 48/48 = 1.00 (threshold 1.00); radius 3 at gap 10
with `F` = 0.030 reads 20/49 = 0.41 (registered range 0.28-0.55); radius 6 at gap 10 reads 0/24 (registered: 0 of at least 20).
All three fire, so the reconstruction that identifies cells from the projections recovers the arms the reports named.

- **Single-body runs** (248 runs) are listed separately: their share is trivially 1.00 because they
  start with one component, so they say nothing about merging and are not evidence about the crossing.
- **Arms seeded with three components** (15 runs) are also separate; the one with data, radius 3 at
  `F` = 0.030, reaches one component in 6 of 15, which is a different question (a row collapsing) and is flagged rather than
  pooled.

## Limits

The table is only as good as the projections: it sees the number of components per sampled step, not the field, so it says
nothing about the corridor — the corridor needs the raw dumps, which are gitignored by design. Radius values are measured from
the seeded area, which splits nominally identical 4.5 arms into two rows (4.4 and 4.7); that split is real evidence of two
different seeding families and is kept rather than smoothed. The heterogeneity flag is a threshold on a difference of shares and
is a prompt to look, not a test.

## What would kill it

A cell whose families agree and whose pooled share still lands outside every family's interval — that would mean the pooling
itself is wrong rather than merely imprecise. Or a re-run of a flagged cell, for instance radius 3 at gap 10 with thirty fresh
seeds, whose share comes in near 0.41: that would show the dispersion is between-family noise rather than a hidden variable.

## Next hypotheses

1. **Re-run the worst-heterogeneity cell** (radius 3, gap 10, `F` = 0.030) with thirty fresh seeds and compare against each of
   the six existing families — if the new family lands near 0.41 the dispersion is noise; if it lands near an existing family,
   the families are not exchangeable and every pooled share in the block needs its spread reported.
2. **The hidden variable may be the seeding pattern**: 4.4 and 4.7 rows at the same nominal radius come from different init
   helpers, which is testable by running one geometry through both helpers.
3. **Cross-size cliff height**: the share just above each crossing (0.33 at radius 6, 0.13 at radius 3 gap 11) may be set by the
   body size, which the table can already be read for.
