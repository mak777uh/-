# X129 — is the kin advantage only geometry? Who lives next door at the same distance

**Why.** X128b found that where a lineage's cells are taken in the lattice the absorber is a relative in **87.2 %** of cases (54.6 % siblings), while in the percolating
cells **61–62 %** of absorptions go to strangers. The obvious deflationary explanation is geometry: daughters are born adjacent, so in a world of isolated spots the
only structure close enough to take a dying one is its own sibling. If that is all there is, the "family world" is a restatement of "the spots are far apart".

The logs carry centroids, so the deflationary explanation is testable without new runs: **at the same contact distance, is the absorber kin or a stranger?** In a
percolating body the nearest neighbour is whoever the body put there; in the lattice it is a sibling by construction. If the kin share at matched distance differs
between the cells, kinship is not proximity — it is **who lives next door**, which is a property of how the habitat arranges structures.

## 1. Manipulation is connected

No new worlds: the thirty dense logs of X108 and X126. The absorptions and their partners are exactly X128b's (same local budget, same partner rule, same
thresholds), so the census is comparable by construction.

| quantity | definition |
|---|---|
| **distance** `d` | Euclidean distance between the centroids of the dead component at `t` and of the absorber at `t+1`, in cells |
| **contact-normalised distance** `δ` | `d / (r_dead + r_absorber)` with `r = sqrt(area/π)`; `δ ≈ 1` means touching, `δ < 1` means overlapping |
| **matched band** | absorptions with `δ ≤ 1.5`, i.e. in physical contact, declared before the data |
| **kin share in the band** | the share of sibling + aunt + cousin + distant among the partnered absorptions inside the band |

Connectedness: every partnered absorption of X128b gets a distance; the counts inside and outside the band are printed, and the partner count must reproduce X128b
(290 / 403 / 531).

## 2. Positive control fires (numeric)

Four controls. **The control fires if** all four hold:

1. **The partner count reproduces X128b** exactly: 290 / 403 / 531.
2. **Sanity of the distance measure**: in the lattice, kin absorbers must be **nearer** than unrelated ones (median `δ` lower), otherwise the metric is not measuring
   what it claims and the run is void.
3. **Heredity** `ρ₁ ≥ 0.35` and **end-survival** reproduces X126 (+0.2496 / +0.2984 / +0.1372).
4. **The band is populated**: at least 100 partnered absorptions inside `δ ≤ 1.5` in every cell, so the matched comparison is a comparison and not a handful.

## 3. Readout exists and varies

Per cell: median `δ` for all partnered absorptions and split by kin/stranger, the share inside the band, the kin share inside the band with a bootstrap interval,
and the same outside it. Variation is guaranteed if the deflationary explanation is wrong: the lattice's neighbours are siblings by construction, a body's are not.

## 4. Sensitivity arithmetic

For the smallest census (290 partnered absorptions in the lattice), a share inside a band holding 70 % of them (203) has SE 0.035, so the declared resolution is
**0.10** on the kin share within the band. A difference under 0.10 is reported as "no difference at this resolution" and the geometric explanation stands.

## 5. Refusal rule (fixed before the run)

**Void** if the partner count misses X128b, or the sanity control fails in the lattice, or heredity/survival controls miss, or a cell has fewer than 100 partnered
absorptions inside the band.

**Geometry explains it** if the kin share within the band differs between the lattice and the maze by less than the declared 0.10 — the "family world" is then the
shape of the world, and the corrected sentence is that absorption goes to **whoever is adjacent**, with the lattice's adjacency being kin by construction.
**Who lives next door** if the matched kin share differs by more than 0.10 — then the habitat arranges who is adjacent, and kinship is a property of the habitat,
not of the split rule alone.
Mixed is not a third outcome here: the statistic is one number per cell and the rule is a threshold on its difference.

## Design summary

| factor | value |
|---|---|
| artifacts | the thirty dense logs of X108 and X126 |
| readouts | `δ` by class, band population, kin share inside and outside the band |
| controls | partner count reproduces X128b; kin nearer than strangers in the lattice; heredity and survival; band population ≥ 100 |
| artifact | `E09_pond/l1_field_x129_geometry.json` |

## Checklist

- [x] connected (every X128b partner gets a distance; band counts printed)
- [x] positive control numeric (partner count exact; a sanity ordering that can fail)
- [x] readout exists and varies (kin-by-construction against a body's neighbours)
- [x] sensitivity computed (§4: SE 0.035 over 203 absorptions, resolution 0.10)
- [x] refusal rule written, with the deflationary outcome as a named result

## Status

Registered 2026-11-03 05:24 MSK, before the run. No new worlds, no GPU.
