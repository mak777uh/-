# X158 — turning the fusion band into a crossing (pre-registration, 04.11)

**Status:** registered before any run. Series `scripts/x158_crossing.py`; analysis `scripts/x158_analyse.py`.

## 1. Manipulation is connected

X157 replaced one wrong number with two right ones and left an explicit gap: the design gap at which fusion stops
being the rule is known only as "between 8 and 11 cells", because the arms at gaps 9-11 for radii 4.5 and 6 were never
run, and the radius-3 arms at 10 and 11 rest on five seeds (4/5 and 2/5). The article therefore states a band. This
item runs the missing arms so that the band becomes a measured crossing, with intervals, at three body sizes.

**The manipulation.** The knob is the initial centre separation of two seeded discs at a fixed radius, i.e. the design gap; every other parameter is held at the block's value. **Connection.** Same runner, same inflow (`F` = 0.030), same grid and same logging quantum as X142/X145/X147/X150/X151/
X153/X157; the only change is which (radius, separation) pairs are run and how many seeds. The hypothesis is not that the
crossing exists — X157 already saw it fall at radius 3 — but that **it falls in the same place for all three sizes,
in design-gap terms**, and that the fall is at most two cells wide.

## 2. Positive control fires

The arms already measured must reproduce, because they are re-run at seeds that were never used: radius 6 at gap 8
(separation 20) must end as one body in **at least 4 of 5** runs, and radius 3 at gap 8 (separation 14) likewise. The
control fires if the share at gap 8 is at least 0.8 in both radii; it fails if either is below 0.6, which would mean the
new seeds or the CPU device changed the physics rather than the design.

## 3. Readout exists and varies

The readout is the share of runs that end as one body. It varies across the tested gaps if at least two arms differ by
0.4 or more. If every tested arm gives the same share, the item is recorded as insensitive by construction and no
crossing is claimed.

## 4. Sensitivity arithmetic before the run

Ten seeds per arm. For a true share of 0.5 the standard error of the observed share is 0.158, so a single arm cannot
separate 0.5 from 0.7. The axis, however, is integer gaps and the prediction is a monotone fall from 1.0 to about 0.2
over two cells: with 10 seeds per point such a fall is visible (the probability that a 1.0 arm reads ≤ 0.7 or that a 0.2
arm reads ≥ 0.5 is under 0.03 for a binomial at those rates). The resolution claimed is therefore **one cell** on the
gap axis, with Wilson intervals reported per arm and no interpolation. With 5 seeds (the arms inherited from X150/X151)
the interval at 0.5 is 0.5 wide, which is why the old arms are reported as counts and not as a curve; the new arms at
the three radii carry 10.

Runs: radius 4.5 at gaps 10 and 11 (separations 19, 20); radius 6 at gaps 9, 10 and 11 (separations 21, 22, 23); radius
3 at gaps 10 and 11 (separations 16, 17). Seeds 701-710 everywhere, so no seed is reused from an earlier arm. Sixty runs,
6 000 steps each, one inflow, `--device cpu`.

## 5. Refusal rule

If for some radius every tested gap in 9-11 gives a share ≥ 0.8, that radius has no crossing inside the tested band: the
report says so and does not extrapolate past 11. If a radius gives ≥ 0.8 at 9 and ≤ 0.2 at 10, the crossing is reported
as a step between those two cells. If the three radii disagree by more than one cell, the "flat in body size" claim of
X157 is recorded as **not supported** and the crossing is reported per radius, without a single number.

## 6. Decision table, fixed now

| outcome | what is written |
|---|---|
| all three radii fall from ≥ 0.8 at 9 to ≤ 0.2 at 11 | "the crossing is at 10 cells for all three sizes, i.e. flat in body size; the band of X157 is one cell narrower" |
| the radii fall at different cells by one | "the crossing is at 10 ± 1 cells; the fall is not resolved further at ten seeds" |
| a radius does not fall inside 9-11 | "radius R does not cross inside 9-11; the flatness claim holds only for the radii that do" |
| the radii differ by two or more cells | "the crossing scales with the seeded size after all"; the X157 sentence is amended, not withdrawn |
| the gap-8 control is below 0.6 | the item is stopped, the device is checked, and nothing is written about the crossing |

## 7. What would kill this item

A gap-8 control that fails (device or seed artefact); a readout that does not vary; or a crossing that moves by two or
more cells between radii, which would make the single "design gap" statement wrong rather than merely imprecise.
