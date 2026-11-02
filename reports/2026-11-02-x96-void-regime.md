# X96 (first pass) — the coupling is a regime change, not a perturbation: a void, and what it teaches about the range

**Plan:** [`2026-11-02-x96-second-species-plan.md`](2026-11-02-x96-second-species-plan.md) (registered 18:15, owner's approval 18:11).
**Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x96_pilot.json`. Seven runs, `F = 0.030`, seed 401, ~25–110 s each.

## What was asked

Whether a second diffusive species with its own diffusion length can move the pattern's **scale** — the one coordinate the field line
has never been able to move. The rule: `uvv = u·v²/(1 + γ·w)` with `dw/dt = Dw∇²w + β_w(v − w)`, `w(0) = v(0)`.

## The anchor passed, and that is the durable part

With `--second-species` absent, seed 291 reproduces the committed `x100_f030_s291.json` **bit-for-bit** (`series` and `uid_pairs`
identical, 110 s). The third field is therefore a true flag: off is the old world, unchanged, checked against an artifact in git rather
than against a fresh run.

## The pilot voided by its own liveness rule

| setting | `Dw` | γ | `q'` | `s` | components at 6000 | field mean | max\|Δv\| vs control |
|---|---|---|---|---|---|---|---|
| control (w off) | — | — | **9** | 0.702 | **69** | 0.128 | — |
| dw008_g05 | 0.08 | 0.5 | 4 | 0.116 | 1 | 0.002 | 0.4325 |
| dw008_g15 | 0.08 | 1.5 | — | — | **0** | 0.000 | 0.4325 |
| dw016_g05 | 0.16 | 0.5 | 4 | 0.101 | 1 | 0.002 | 0.4325 |
| dw016_g15 | 0.16 | 1.5 | — | — | **0** | 0.000 | 0.4325 |
| dw032_g05 | 0.32 | 0.5 | — | — | **0** | 0.000 | 0.4325 |
| dw032_g15 | 0.32 | 1.5 | — | — | **0** | 0.000 | 0.4325 |

The control is healthy (`q' = 9`, symmetry 0.702, 69 components) and the manipulation reaches the field — but what it does is
**annihilate it**. Every `w`-on setting ends with a near-empty field: mean amplitude 0.000–0.002 against the control's 0.128. The two
`γ = 0.5` runs leave a single small blob (`max 0.36`, mean 0.002); the rest are numerically dead (`max = 0.0`).

The identical `max|Δv| = 0.4325` across all six settings is not a coincidence and not a bug: it is the **control's own peak**, because
the `w`-on fields are empty and the difference is just the control. That number is a useful diagnostic of exactly this failure mode —
when `max|Δv|` equals the reference's maximum, the manipulated field is gone.

**Why it collapsed is arithmetic, not mysterious.** Inside a structure `w ≈ v ≈ 1`, so the factor `1/(1 + γ·w)` is `1/(1 + 0.5) = 0.67` at
`γ = 0.5`: the autocatalysis is cut by a third everywhere the pattern lives. Gray–Scott lives in a narrow `(F, k)` band; a third off the
reaction term is not a perturbation, it is a different world. The `Dw` axis never got a chance to matter: all six runs died for the same
reason, and the collapse is independent of `Dw` by construction.

## What the void buys

1. **The useful range is small.** A coupling that leaves the medium alive must keep `γ·w ≲ 0.05–0.1` inside a structure, i.e.
   `γ ≈ 0.05–0.2`, not 0.5–1.5. The mild sweep (X96b, registered before these runs were read) uses exactly that range.
2. **A diagnostic for the next time.** If `max|Δv|` against the control equals the control's peak amplitude, the manipulation destroyed
   the field. That check costs one line and catches a whole class of "the manipulation moved the readout" claims.
3. **The anchor discipline held.** The third field is expensive to add (a new equation in the world) and cheap to verify with an
   artifact-level comparison; that comparison is what makes the mild pass interpretable.

## Caveats

- One cell, one seed: this is a pilot, and its job was to find whether the knob does anything at all, not to estimate an effect.
- `q' = 4` with one component is **not** a scale reading: a single blob has no wavelength, and `angular` returns a number for it
  anyway. The `components` column is what keeps that honest.
- If the mild pass also fails to keep ≥ 10 components, the coupling form itself (`1/(1+γw)` on the autocatalysis) is too blunt and a
  different wiring — `k` modulated by `w`, or `w` as a reactant rather than an inhibitor — should be tried before the channel is called
  closed.

## Next

- **X96b** (registered 18:47): `γ ∈ {0.05, 0.10, 0.20}` × `Dw ∈ {0.08, 0.16, 0.32}`, nine runs, live-field requirement ≥ 10
  components, same two-unit criterion for `q'`.

доска: принято 0, отклонено 0, отложено 0.
