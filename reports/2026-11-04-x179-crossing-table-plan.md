# X179 — The crossing table: protocol (written before the aggregation was run, 04.11)

This item runs nothing and measures no new world; it reads every committed projection and assembles the crossing matrix. Because
it is an aggregation rather than an experiment, the five design checks are recorded here as the constraints the aggregation had
to satisfy, and the rule that fixes which cells may be pooled was written before the table was built.

## 1. Manipulation is connected

The manipulation is the **selection of runs**. A run enters the table if its first logged step holds exactly two components; the
cell is the triple (measured body radius, measured surface gap, inflow `F`), with the radius from `sqrt(area/pi)` and the gap
from the centre separation minus twice that radius. Runs with one or with three or more seeded components are counted separately
and never pooled into a two-body cell. The check is that the reconstruction recovers the arms the reports named: radius 3 arms
report gap 10 at `F` = 0.030 and the measured cell must be the same, and the table's totals must exceed the sum of the named
series without including controls.

## 2. Positive control fires

The control fires if the table reproduces **three known cells within their own intervals**: radius 3 at gap 8 with a share of
**1.00**, radius 3 at gap 10 and `F` = 0.030 with a share between 0.28 and 0.55, and radius 6 at gap 10 with a share of 0.00
over at least 20 runs. Thresholds: 1.00, > 0.28, and 0 of ≥ 20. If any of the three fails, the reconstruction is wrong and the
table is not published.

## 3. Readout exists and varies

The readout is the share with a Wilson interval. It must vary across cells (it must not be 0 or 1 in every cell) and every cell
with fewer than five runs must carry its interval in the table, so that no cell is read as a point.

## 4. Sensitivity arithmetic, and the pooling rule

Cells pool runs from different seed families. The rule, fixed before the table: a family enters the audit when it contributes
**at least three runs**, and a cell is flagged heterogeneous when the largest and smallest family shares differ by **more than
0.4**. The flag is a prompt to look, not a test; the table reports the spread for every cell regardless, so a reader can see the
dispersion without the threshold mattering. The arithmetic behind 0.4: with three runs a family's share moves in steps of 0.33,
so a gap of more than 0.4 means at least two steps, which sampling noise alone produces in fewer than one cell in ten under a
common share of 0.4.

## 5. Refusal rule

If the table fails check 2, the item is recorded as a failed reconstruction and nothing is claimed. If more than a third of the
cells are flagged heterogeneous, the item's headline is the heterogeneity itself and **no crossing value is quoted from the
table**; crossing values are then quoted only per family. If fewer than a third are flagged, the crossing values are quoted with
their pooled intervals and the flagged cells are named as exceptions.

## What would kill the table

A cell whose families agree with each other and whose pooled share still lies outside every family's interval — that would mean
the pooling, not the noise, is the problem. Also: a mismatch between the reconstructed cells and the arm names in the reports,
which would mean the radius or gap reconstruction is wrong.

## Implementation

`scripts/x179_crossing_table.py` reads `morphogenesis/experiments/L1_field/*.compact.json`, writes
`morphogenesis/experiments/E09_pond/l1_field_x179_crossing_table.json`, and prints the table with intervals, the family spreads
and the flagged cells. No runs, no new raw artifacts, no field dumps: the whole item is reproducible from the repository alone.
