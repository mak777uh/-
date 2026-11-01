# The world that cannot pick a wavelength is the world with eighteen times the transmissions

1 November 2026, 07:35. A link between the two halves of the field line, found in data already on disk — no new run.

X60 and X58-lite established that the heterogeneous world does not select a pattern wavelength while the homogeneous one
does (12 units, q = 8). E6p and E6q established that the trait channel produces selection and that frequency dependence
prevents fixation. Nobody had put the two side by side. The four arms share everything except the inflow field and the
survival parameters, so they can be compared directly:

| arm | world | splits per run | parent–child pairs | `r` | mean composition |
|---|---|---|---|---|---|
| `e6p_survfd` | heterogeneous, frequency-dependent survival | **311.0** | **731** | 0.976 | 1.950 |
| `e6q_survfd_h` | homogeneous, same parameters | **17.5** | 42.5 | 0.812 | 1.119 |
| `e6p_surv` | heterogeneous, no frequency dependence | 22.5 | 47.5 | 0.775 | 1.487 |
| `e6p_ctrl` | heterogeneous, `beta = 0` | 89.0 | 185 | 0.931 | 1.077 |
| `e6q_ctrl_h` | homogeneous, `beta = 0` | 4.0 | 20 | 0.401 | 0.960 |

## What it says

**1. Transmission tracks the inflow field, by a factor of eighteen.** Same trait channel, same mutation, same seeds:
311 divisions against 17.5. Even with no feedback at all (`beta = 0`) the heterogeneous world produces 89 against 4. The
mechanism is direct: a field with many small components has many places for a component to pinch and split, and the
world that fails to select a wavelength is exactly the world that keeps its components small.

**2. Selection strength and transmission rate are not the same axis.** The frequency-dependent heterogeneous arm has
both the largest drift (+0.835) and by far the most divisions; the non-frequency-dependent arm has half the divisions and
a smaller drift. Whatever makes transmissions is the geometry of the field, not the strength of selection on the trait.

**3. Heritability still says nothing on its own.** `r` is highest where divisions are most frequent (0.976 against
0.812), which is the mechanical pattern already documented in
[`2026-11-01-heritability-is-mechanical.md`](2026-11-01-heritability-is-mechanical.md): the daughter copies the parent, so
fidelity is set by the copy rule and frequent division prevents drift. The number that differs between worlds is the
**count of transmission events**, not their fidelity.

## Why this matters for the line's question

The project asks what conditions a digital medium gives for something life-like. The two measurements now line up into
one sentence:

> **A medium without a selected pattern wavelength is a medium with high turnover: it fragments into small components,
> those components divide often, and division is where heritable variation is transmitted. The same heterogeneity that
> destroys pattern regularity multiplies the events through which lineages could exist.**

That is the first statement in this line that connects geometry to heredity with numbers on both sides, and it is
testable: if it is right, forcing the heterogeneous world to select a wavelength (for example by narrowing the inflow
correlation length) should cut the division count without touching the trait parameters.

## What is not claimed

- Splits and parent–child pairs are counts of events under the overlap rule, not verified lineages; the rule is the
  operational one from `field_track.py`.
- The comparison is between arms run in different series at different times; the parameters are matched but the machine
  state is not controlled beyond that.
- No claim that more divisions means more selection — item 3 above says the opposite is what the data show.

## Reproduction

`morphogenesis/experiments/L1_field/e6p_*_s*.json`, `e6q_*_s*.json`; medians over ten seeds per arm.
