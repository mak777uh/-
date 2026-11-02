# X96 — a second diffusive species in the field: pilot on the only untried scale channel

**Owner's decision, 02.11 18:11 MSK: «пробуй конечно»** — recorded in `docs/decision-log.md`. Adding a third field is a new rule of
the world, not a parameter, which is why it waited for that sentence.

**Why this channel and no other.** The field line can move the *orientation* of the pattern with the environment (symmetry `s` =
0.421 / 0.674 / 0.848 at 0.025 / 0.030 / 0.035, X86) but never its *scale*: `q'` = 5–9 in all 35 forced worlds, a second spectral line
at 16× the power moves no period (X82), and the initial condition is closed as a channel — a full-field periodic start dies at three
amplitudes and two wavelengths, and a 5 % bias leaves `q'` at the medium's own value (X96b). In a reaction–diffusion system the one
quantity that sets a wavelength *by construction* is the ratio of diffusion lengths between the autocatalytic species and its
inhibitor. This world has never had a second length: `v` is the autocatalyst and its own decay is the only sink.

**The rule under test (and its exact form, so the pilot is not "something with a third field").**

```
uvv = u * v * v / (1 + gamma * w)          # the autocatalysis, weakened by the slow species
du  = Du*lap(u) - uvv + F_eff*(1 - u)
dv  = Dv*lap(v) + uvv - (F_eff + k_eff)*v
dw  = Dw*lap(w) + beta_w*(v - w)           # the slow species follows v with its own diffusion length
```

`w` starts equal to `v` (no impulsive transient), is clamped to [0, 1] like the other two, and the flags are `--second-species`,
`--Dw`, `--gamma`, `--beta-w`. With `--second-species` absent the equations are **byte-for-byte the current ones**, which the anchor
below checks against a committed artifact rather than against a fresh run.

## 1. Manipulation is connected

Pilot: one cell (`F = 0.030`, the lattice cell where `q'` is the sharpest known quantity), one seed (401), `Dw` ∈ {0.08, 0.16, 0.32}
(equal to, twice and four times `Dv`) × `gamma` ∈ {0.5, 1.5}, plus the `w`-off control: **7 runs**. Everything else is X100's flags
(`--steps 6000 --Du 0.16 --Dv 0.08 --k 0.06 --hetero-scale 12.0 --hetero-amp 0.5 --sample-every 50 --init-jitter`).

Two connectivity facts must hold before any readout is believed:

- **the anchor**: with `--second-species` off, seed 291 must reproduce the committed `x100_f030_s291.json` **bit-for-bit** (the
  `series` array, `uid_pairs` and `params` identical). A flag that changes the off-path is not a flag;
- **the manipulation reaches the dynamics**: between the `w`-off run and every `w`-on run, the final field must differ by
  `max|Δv| ≥ 0.01`. A third field that leaves the field unchanged is a dead term, not a channel.

## 2. Positive control fires (numeric)

The `w`-off run's `q'` must land in the band the medium has always shown, **5 ≤ q' ≤ 9** (X84/X82: every forced world). If the
unmodified code stops reproducing its own reading on a new seed, the seed is anomalous and the pilot is void.

## 3. Readout exists and varies

`q'` from `scripts/field_metrics.py` (`angular`, axis-aligned wavenumber of maximum power, `q_max = 14`) on the final field, plus the
`v`-field's component count and its peak amplitude as health checks. The readout varies by construction: `q'` is an integer-ish
argmax over a spectrum, and the pilot's whole question is whether it leaves [5, 9].

A pilot is not a series: one seed, no per-world statistics. It answers one question — *does the scale move at all* — and only a
band-exit is worth a series.

## 4. Sensitivity arithmetic

`q'` is a coarse instrument: its resolution is one unit of wavenumber (≈ 12/q̄ ≈ 1.3 cells at `q' = 9`). A pilot that moves `q'` by one
unit is **not** evidence; the criterion below therefore demands a **two-unit** move, which is about the width of the whole band
(5–9) and far outside the ±1 wobble seen across seeds. No power calculation is possible with one seed, which is why this is a pilot
and why the refusal rule has a "not decided" branch.

## 5. Refusal rule (fixed before the run)

**Void** if the anchor fails, the `w`-off control's `q'` falls outside 5–9, a `w`-on run dies (≤ 1 component at the end), or the
manipulation check fails for all six settings.

**The scale channel exists** if at least one setting, with a live field, gives `q' ≤ 3` or `q' ≥ 11` (a two-unit move from the band).
**The channel does not move the scale** if all six live settings give `q' ∈ [5, 9]` and the manipulation check fires in at least
three of them — that closes the fourth and last candidate channel, which is a result.
**Not decided** otherwise (for instance `q'` moves by one unit): the pilot then says what to sweep next, and the series is registered
on that.

## Design summary

| factor | value |
|---|---|
| runs | 7 (1 anchor + 6 settings), ~105 s each, GPU lane as usual |
| cell | `F = 0.030`, seed 401, X100's flags otherwise |
| rule | `uv²/(1+γw)` with `dw/dt = Dw∇²w + β_w(v − w)`, `w(0) = v(0)` |
| readout | `q'` from `field_metrics.angular`, component count, peak amplitude |
| artifact | `morphogenesis/experiments/L1_field/x96pilot_*.json`, aggregate `E09_pond/l1_field_x96_pilot.json` |

## Checklist

- [x] connected (anchor bit-for-bit against a committed artifact; manipulation check `max|Δv| ≥ 0.01`)
- [x] positive control numeric (`q'` of the `w`-off run inside 5–9)
- [x] readout exists and varies (`q'` is an argmax over the spectrum; the band 5–9 is the reference)
- [x] sensitivity computed (§4: one unit is noise, a two-unit move is the criterion)
- [x] refusal rule written, with "the channel does not move the scale" as a real outcome
- [x] stated: a pilot, one seed, no per-world statistics

## Status

Registered 2026-11-02 18:15 MSK, before the flag existed. The field runner is not edited while X108's series is in flight (the rule:
finish the series, then edit, then anchor, then run).

доска: принято 0, отклонено 0, отложено 0.
