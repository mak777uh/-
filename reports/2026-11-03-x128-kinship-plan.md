# X128 — when a lineage loses its name, do its cells go to kin?

**Why.** X127 changed what "death" means in this line: 75.7–84.5 % of a lineage's deaths are **absorptions** — the dead uid's area reappears in the surviving
structures, so the cells live on and only the name ends. That leaves one question that decides how to read every persistence number: **who takes the cells?**
If the absorber is usually a sibling or a cousin, then absorption is continuity inside a family — the lineage's material survives in a relative, and "name
loss" is a bookkeeping event. If the absorber is usually a stranger, absorption is a takeover, and the maze is where lineages are eaten.

The logs carry the whole genealogy (`parent` per uid) and the areas per component, so the question is answerable without a single new run.

## 1. Manipulation is connected

No new worlds: the same thirty dense logs (X108 at `F = 0.030` and `0.040`, X126 at `0.035`) that produced X113–X127. The manipulation is the inflow,
already measured; this run adds a **partner** to each absorption.

| quantity | definition |
|---|---|
| **absorber** | among the uids present at both `t` and `t+1`, the one whose area grew most; it must account for **≥ 50 % of the total survivor growth**, otherwise the absorption is **diffuse** and is reported as such (no partner is invented) |
| **sibling** | the absorber and the dead uid have the same mother |
| **cousin** | same grandmother, different mother |
| **aunt/uncle** | the absorber is a sibling of the dead uid's mother, or vice versa |
| **distant kin** | a common ancestor within three generations, none of the above |
| **unrelated** | no common ancestor within three generations of either |

Connectedness: the census is applied to every absorbed death in every world, and the counts per class are printed; the number of absorptions reproduces X127.

## 2. Positive control fires (numeric)

Four controls, all required. **The control fires if** all four hold:

1. **The absorbed share reproduces X127** to four decimals: 84.5 % / 78.7 % / 75.7 % of the same death counts.
2. **End-survival reproduces X126**: +0.2496 / +0.2984 / +0.1372 with pair counts 1 142 / 1 106 / 1 195.
3. **A partner is identifiable** for at least **80 %** of absorbed deaths in every cell (the rest are diffuse or untraceable). Below that the census describes a
   minority and the run is void, not "mostly diffuse".
4. **Heredity** `ρ₁ ≥ 0.35` (0.548 / 0.421 / 0.480).

## 3. Readout exists and varies

Per cell: the five shares with counts, the median age of the swallowed structure (its own birth to its death), and the median area of the absorber at the death
step. Variation is expected: in the lattice a split's daughters are adjacent spots that can re-merge, while in one percolating body the absorbing surface is
everywhere, so the kinship composition cannot be the same in `0.030` and `0.040`.

## 4. Sensitivity arithmetic

X127 gives 444 / 664 / 834 absorbed deaths in the three cells; if 80 % of them have a partner, the smallest census is 355, so a share has SE 0.027 and the
declared resolution is **0.08** between cells. A cell landing under 100 classified deaths is void by §5 rather than "no difference".

## 5. Refusal rule (fixed before the run)

**Void** if fewer than 100 absorbed deaths have an identifiable partner in a cell, or heredity < 0.35, or the absorbed share misses X127 by more than 0.01, or
end-survival misses X126 by more than 0.01, or the diffuse share exceeds 0.20 in a cell.

**Continuity inside a family** if sibling + cousin + aunt + distant kinship exceed 0.50 in **all three** cells: absorption is then a family event and the line's
"deaths" are name losses within lineages.
**Takeover by strangers** if `unrelated` exceeds 0.50 in any cell, and in that cell the reading is that the cells change hands between families.
**Mixed** otherwise, with the shares printed — and if the maze's `unrelated` share exceeds the lattice's by more than the declared 0.08 the report names the maze
as the cell where lineages are eaten, without extending that to the others.

## Design summary

| factor | value |
|---|---|
| artifacts | the thirty dense logs of X108 and X126 |
| readouts | five kinship shares, median swallowed age, median absorber area, diffuse share |
| controls | absorbed share reproduces X127; end-survival reproduces X126; partner identifiable ≥ 80 %; heredity |
| artifact | `E09_pond/l1_field_x128_kinship.json` |

## Checklist

- [x] connected (every absorbed death gets a partner or the diffuse label; counts printed)
- [x] positive control numeric (two published numbers reproduced to four decimals, plus a partner-coverage floor)
- [x] readout exists and varies (one body against many isolated spots)
- [x] sensitivity computed (§4: 355 classified deaths minimum, SE 0.027, resolution 0.08)
- [x] refusal rule written, with "diffuse" and "mixed" as real outcomes

## Status

Registered 2026-11-03 05:14 MSK, before the run. No new worlds, no GPU: the genealogy and areas are already in the logs.
