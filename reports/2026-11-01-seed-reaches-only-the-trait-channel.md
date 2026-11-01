# In the field world the seed reaches the dynamics only through the trait channel

1 November 2026, 06:35. A property of the world that we had never stated, found by asking why ten control seeds produced
identical structure series.

## What was found

In both E6p and E6q the **control arms** (`beta = 0`, so composition cannot affect decay) produce **byte-identical**
`components` and `areas` series across all ten seeds:

| arm | components identical across seeds | areas identical |
|---|---|---|
| `e6p_ctrl` (heterogeneous, `beta = 0`) | **yes** | **yes** |
| `e6q_ctrl_h` (homogeneous, `beta = 0`) | **yes** | **yes** |
| `e6p_surv`, `e6p_survfd`, `e6q_survfd_h` | no | no |

The cause is structural, not a bug in the series writer: the field world has **no seed-dependent initial condition and no
seed-dependent inflow**. The trajectory of `u` and `v` is deterministic given the parameters. Everything that varies
between seeds — the composition of each component, the mutations, the splits — lives in the trait channel, and it reaches
the field only through `eps` (growth) or `beta` (survival). With `beta = 0` and `eps = 0`, the ten "seeds" are one run.

## What this does and does not change

**Does not change:** the E6p drift and the E6q paired comparison are both computed on readouts that *do* vary across
seeds. `s_mean_last` in the control is not identical (1.204 for seed 171 against 1.027 for 172), because composition
drifts under its own mutation even without feedback. Both paired tests remain valid.

**Does change:** any sentence of the form "the control has N structures, spread S" is wrong for this world — the control
has **one** structure series, repeated. Specifically:

- E6p's "control: 36 structures, spread 0.437" — the spread belongs to composition, not to structures.
- E6q's "homogeneous control: 4.0 structures" is a single deterministic value; the 10 seeds add nothing to it.

## Why this matters beyond bookkeeping

A reviewer who opened two control files would find identical component series and would be right to ask what the seeds
are for. The answer is: in this world, seeds measure the trait channel, and only that. A control with `beta = 0` is a
single sample, and the honest description is "one deterministic field trajectory per arm, ten trait realisations".

## What follows for design

1. Any future arm whose purpose is to give a **baseline with seed variance** needs either `beta > 0` or an explicit
   seed-dependent perturbation of the initial condition — the world does not provide one.
2. Statements about the distribution of structure counts can only be made for arms with a live feedback channel; for
   `beta = 0` arms the count is a constant.
3. This also explains an older observation: the field line's "10 seeds" were always cheap, because nine of them changed
   nothing in the geometry — the variation we kept quoting (`sd 3.73` in `x18`) comes entirely from the composition
   feedback that `beta = 0.2` provides.

## Reproduction

    python - <<'EOF'
    # components/areas of e6p_ctrl_s171..s180 are identical; s_mean_last is not
    EOF

Artifacts: `morphogenesis/experiments/L1_field/e6p_ctrl_s*.json`, `e6q_ctrl_h_s*.json`. Related: the same property
underlies `reports/2026-11-01-e6p-selection-result.md` and `2026-11-01-e6q-no-niches-result.md`.
