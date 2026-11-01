# X64: the refinement worked, and it took the claim down with it

1 November 2026, 10:55. Ten runs at grid 144, five per arm. Preregistration:
[`2026-11-01-x64-real-refinement-plan.md`](2026-11-01-x64-real-refinement-plan.md), committed before the run.

This replaced the withdrawn X58-lite. The scaling is now the one the code actually implements: physical diffusivity is
`Du·Δx²`, so at `Δx = 2/3` the coefficient is `0.36` and `dt = 0.5` stays inside the stability bound (`dt·Du = 0.18`).
Physical time is kept at 6000 by running 12 000 steps.

## The scaling is validated — for real this time

| snapshot | homogeneous arm |
|---|---|
| physical 2000 | q = 1 (not yet patterned), entropy 1.49 / 3.00 |
| physical 4000 | q = 7, λ = 13.7 units, entropy 2.06 |
| physical 6000 | **q = 8, λ = 12.00 units**, share 0.374, entropy **1.86 / 3.00** |

The homogeneous world lands on **exactly 12.00 physical units** at this resolution — the same wavelength as on the 96 grid.
The mapping is right, the run is stable, and the positive control fired.

## And the heterogeneous arm now patterns too

| snapshot | heterogeneous arm |
|---|---|
| physical 2000 | q = 1, share 0.286, entropy 2.25 / 3.00 |
| physical 4000 | q = 1, share 0.192, entropy 2.38 / 3.00 |
| physical 6000 | **q = 1, share 0.447, entropy 1.84 / 3.00** |

At the same physical time the heterogeneous arm reaches share 0.447 — *more* concentrated than the homogeneous one's 0.374,
and with the same normalised entropy (1.84/3.00 = 0.61 against 1.86/3.00 = 0.62).

Compare the 96 grid at the same physical time: heterogeneous share 0.24 with entropy 2.23 of 2.48, i.e. **0.90 of the
maximum** — nearly flat, while the homogeneous arm sat at 0.61.

**So the difference between the arms exists at 96 and vanishes at 144.**

## What this means, without softening it

The claim from X60, X58-lite and X61 — *heterogeneous inflow prevents wavelength selection* — **does not survive a
correctly scaled refinement**. It is a property of the 96-cell grid, not of the medium:

| grid | cells per pattern wavelength | heterogeneous normalised entropy | homogeneous normalised entropy |
|---|---|---|---|
| 96 | 12 | **0.90** (flat) | 0.61 (selected) |
| 144 | 18 | **0.61** (selected) | 0.62 (selected) |

At the coarse grid the modulation has 12 cells per period, which is exactly the pattern's own period; at 144 it has 18.
The pattern cannot sustain itself on so few cells per wavelength when the inflow also varies at that scale, so it shatters
— which is precisely the **non-Platonic** effect Davis describes: a pattern that exists at one discretisation and not at
another.

The pre-declared verdict for this run came out "wrong" because the entropy bar (1.8) was missed by 0.06 — and that bar was
itself mis-specified, because entropy's maximum depends on how many modes the grid allows (ln 12 against ln 20). The
normalised entropies above are the comparable quantity. So the *criterion* was wrong and the *run* was informative; both
are recorded.

## What survives, and what does not

| claim | status |
|---|---|
| homogeneous inflow selects a 12-unit wavelength | **holds**, on both grids |
| the physical mapping `D = Du·Δx²` is right | **holds** — 12.00 units at two resolutions |
| heterogeneous inflow *prevents* wavelength selection | **withdrawn**; it delays it at 96 only |
| the transient perforated web (β₁) at 96 | untouched by this run, but now also suspect at other grids |
| divisions per component track the inflow (X59 dose) | untouched — that is a count, not a spectrum |

## What follows

The line's spectral claims must be restated as **"at 96 cells per 96-unit domain"**, and the natural next experiment is a
convergence series in the true sense: 96 → 144 → 192 (with `dt ≤ 0.39` at 192), three arms, to see where the heterogeneous
spectrum stops being flat. That is a multi-hour campaign and it should be planned, not improvised at the end of a night.

This is the second time today that the refinement machinery has overturned a claim of mine, and the first time it did so
by working correctly.

## Artifacts

`morphogenesis/experiments/L1_field/x64_{pattern,homog}_s{171..175}.json`, fields in `x64_fields/` (30 arrays), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x64_refinement.json`. Scripts: `scripts/x64_series.py`,
`scripts/x64_analyse.py`.

## Addendum, 11:15 — the topological half, from the same saved fields

The X60 correction note says the perforated web (β₁) was untested at other grids. It is testable for free here: the fields
are saved, and the same functions give β₀, β₁ and the largest-cluster share at 144.

| physical time | β₀ het / hom | β₁ het / hom | Δβ₁ (seeds) | largest share het / hom |
|---|---|---|---|---|
| 2000 | 6.0 / 1.0 | **14.0 / 1.0** | **+13.0 (4/5)** | 0.959 / 1.000 |
| 4000 | 3.0 / 3.0 | 12.0 / 9.0 | +4.0 (3/5) | 0.968 / 0.952 |
| 6000 | 2.0 / 3.0 | **17.0 / 4.0** | **+12.0 (3/5)** | 0.969 / 0.951 |

**The direction survives, the evidence weakens.** At 96 the excess was 10/10 seeds at the early time; here it is 4/5, and
later 3/5. Five seeds cannot distinguish "the effect is real but noisy at this grid" from "the effect is half the size".
What can be said: the heterogeneous field has more loops at every snapshot, with a median excess of +13 and +12 holes at the
first and last, and the sign never reverses.

Note also that at physical time 2000 the two arms differ hugely in occupancy (0.52 against 0.21), so the matched-occupancy
control used in X60 is not optional here — it has not been run at 144, and until it is, the +13 should be read as
"heterogeneous world occupies more area and has more holes", not as a separated effect.

**Status of the β₁ claim after both grids:** same sign at 96 (10/10) and 144 (4/5, 3/5), magnitude uncertain, occupancy
control missing at 144. That is a hypothesis with two supporting grids, not a result.
