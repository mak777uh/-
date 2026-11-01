# X67: the heterogeneous concentration follows the box, so it is not a structure

1 November 2026, 13:45. Ten runs on a doubled domain. Preregistration:
[`2026-11-01-x67-bigger-box-plan.md`](2026-11-01-x67-bigger-box-plan.md), committed before the run.

The map left one question: on every grid tested, the heterogeneous arm's peak sat on the box scale (q = 1), and q = 1 is
the box by construction. So either the medium organises at the domain size — a boundary artefact — or at some fixed
physical scale that happened to coincide with the old 96-unit box. Doubling the domain while holding the cell size fixed
separates the two: a fixed 96-unit structure would appear at q = 2, the box at q = 1, the medium's wavelength at q = 16.

## Result

| physical time | homogeneous | heterogeneous |
|---|---|---|
| 2000 | q = 1 (192 units), share 0.774, H/ln 0.313 | q = 1, share 0.730, H/ln 0.342 |
| 4000 | q = 1, share 0.679, H/ln 0.412 | q = 1, share 0.249, H/ln 0.791 |
| 6000 | **q = 16 → 12.0 units**, share 0.230, H/ln 0.722 | **q = 1 → 192 units**, share 0.681, H/ln 0.421 |

**The control fired exactly:** on the doubled domain the homogeneous world still selects **12.0 units** (q = 16), the same
wavelength as on every other grid. The mapping and the physics are right.

**The heterogeneous peak moved with the box.** It was q = 1 on a 96-unit domain; it is q = 1 on a 192-unit domain. It is
not at q = 2 (a fixed 96-unit structure) and not at q = 16 (the medium's wavelength).

**Verdict: the organisation follows the domain.** The heterogeneous arm's concentration is a domain-scale imbalance, not a
structure with a physical size. Doubling the box doubles the thing that carries the power, which is what a boundary- or
domain-driven effect does and what a real structure does not.

## What this settles

The claim from X60, withdrawn at 11:00, restored at 13:10, is now in its final form for this stage:

> Heterogeneous inflow **suppresses the medium's pattern** — no 12-unit peak appears on any of five grids or two domain
> sizes — and what concentration the heterogeneous field does show is the **box itself**, not an alternative organisation.

So there is no "different structure" to describe: the heterogeneous world has less organisation, not other organisation.
That is a cleaner negative than anything the line has produced about this world, and it is the first claim in the whole
field series that has been tested against both resolution and domain size.

## What this does not establish

- Why the heterogeneous arm keeps 68 % of its low-q power at q = 1 with entropy 0.42 — a global imbalance could be a slow
  drift of total material, the largest-scale component of the inflow field, or the periodic boundaries. Distinguishing
  them is a modelling question, not a measurement one.
- Whether a still larger domain changes the picture. Two sizes bracket the box hypothesis; a third would confirm it as a
  law rather than a reading.
- Nothing about `dt = 1.0` versus `0.5` for the map: this run used `dt = 1.0` with `Du = 0.16` (cell size fixed), which is
  the 96-grid physics on a bigger domain, not a refinement.

## Artifacts

`morphogenesis/experiments/L1_field/x67_{pattern,homog}_s{171..175}.json`, fields in `x67_fields/` (30 arrays, 192²),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x67_box.json`. Scripts: `scripts/x67_series.py`,
`scripts/x67_analyse.py`.
