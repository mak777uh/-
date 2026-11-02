# X110b — liveness is not a component count: an amendment registered before the maze column exists

**What happened.** X110's registered control says "`γ = 0.50` leaves no pattern anywhere". The lattice column contradicts it at one seed:
`x110_f030_g050_s423` ends with **16 components** and would count as alive, while its neighbours at the same coupling end with 1. Looking
at what those 16 components are settles it:

| run | components | occupied fraction | largest component | reading |
|---|---|---|---|---|
| `f030 γ=0.10 s421` | 49 | **0.253** | 205 | a pattern |
| `f030 γ=0.30 s421` | 13 | **0.102** | 185 | still structured — big blobs plus fragments |
| `f030 γ=0.50 s421` | 1 | 0.004 | 37 | dead |
| `f030 γ=0.50 s423` | **16** | 0.040 | **23** | **speckle**: sixteen equal 23-cell blobs |

A dying field does not always go to zero components — it can shatter into many tiny ones. A component **count** therefore cannot separate
"pattern" from "speckle", and X110's liveness rule was wrong: the quantity that separates them is how much of the field is occupied and
whether any structure is big.

**The amendment, registered before the maze column exists** (the lattice is complete, the maze has none of its 15 runs yet, so the
amendment cannot be tuned to the boundary it will measure):

## 1. Manipulation is connected

Same thirty runs as X110, no new runs. Per run at step 6000: components, occupied fraction, and the areas of the components.

## 2. Positive control fires (numeric)

The amendment is fixed by the two reference points above, not by a fit:

- **alive** ⇔ `occupied ≥ 0.05` **and** `max component area ≥ 50`;
- the control fires if **every `γ = 0.10` run is alive** (observed: occupied 0.25, max area ~205) **and every `γ = 0.50` run is dead**
  (observed: occupied 0.004–0.040, max area 23–37). Both bands are an order of magnitude apart, so the thresholds sit roughly in the
  geometric middle and the report shows the sensitivity to 0.04/0.06 and 40/60.

## 3. Readout exists and varies

`γ_cell` per cell = the largest coupling alive in at least two of three seeds, on the amended liveness. The whole grid varies by design:
occupied 0.25 → 0.10 → 0.04 across `γ = 0.10 → 0.30 → 0.50` at one seed.

## 4. Sensitivity arithmetic

The readout is a bracket on a five-point grid; the amendment adds two thresholds, so the report prints `γ_cell` at the nominal
(0.05, 50) and at the two alternatives. If the bracket moves under either alternative, the report says the boundary is threshold-sensitive
rather than quoting one number.

## 5. Refusal rule (fixed before the maze column exists)

**Void** if the control fails at either end (a `γ = 0.10` run not alive, or a `γ = 0.50` run alive under the nominal thresholds), or if
the three threshold sets give three different `γ_cell` values for the same cell.

**The cells differ in their distance to the edge** if the maze's `γ_cell` is at least one grid step below the lattice's, under all three
threshold sets.
**The cells do not differ** if the brackets overlap under all three.
**Threshold-sensitive** otherwise — and then the honest output is a range, not a number.

## Design summary

| factor | value |
|---|---|
| artifacts | X110's thirty runs, re-read |
| liveness | `occupied ≥ 0.05` **and** `max area ≥ 50` (alternatives 0.04/40 and 0.06/60) |
| readout | `γ_cell` per cell as a bracket, three seeds, two-of-three rule |
| artifact | `E09_pond/l1_field_x110b_gamma_cell.json` |

## Checklist

- [x] connected (thirty runs on disk; components, occupied and areas recorded in every run)
- [x] positive control numeric (`γ = 0.10` alive, `γ = 0.50` dead, bands an order of magnitude apart)
- [x] readout exists and varies (occupied 0.25 → 0.10 → 0.04)
- [x] sensitivity computed (§4: two alternative threshold sets, printed)
- [x] refusal rule written, with "threshold-sensitive" as a real outcome
- [x] stated: registered while the lattice column was known and the maze column did not exist

## Status

Registered 2026-11-02 20:42 MSK. The lattice column was complete when this was written; the maze column was not started.

доска: принято 0, отклонено 0, отложено 0.
