# X160 — Does an external signal hold diversity through a mortality buffer? (pre-registration, 04.11)

**Status:** registered in the queue as `X160_mortality_buffer`, status `planned`. Not run yet: it needs one small change to
the pond world (a slow variable and a mortality gain, §Design), and the world is frozen while X158 runs. Nothing here is a
result.

## 1. Manipulation is connected

Three arms differ **only** in the signal that drives the world, not in its tempo. The signal enters a slow variable
`m(t)` — a leaky integrator with time constant `tau` — and `m` multiplies the per-step death probability of a cell
(`death ~ base * (1 + gain * (m - mean(m)))`). Every arm is normalised to the **same realised mean of m** and the same
`tau`, so the mean tempo is held equal by construction and only the *structure* of the signal differs:

| arm | signal file | what it preserves |
|---|---|---|
| constant | `lab/streams/const_ones.json` | nothing (flat) |
| real | `lab/streams/mic-2026-10-28.json` | the recording as it is |
| surrogate | `lab/streams/mic_iaaft-2026-10-29.json` | power spectrum and amplitude distribution, phase destroyed |

The comparison that matters is real against surrogate: if the medium carries information the world can use, the real
signal must beat a surrogate with the same spectrum and the same tempo. This is the same discriminator that killed the
"contact with the world" claim before (§10bo, where the real microphone was indistinguishable from a constant at equal
tempo), applied to the one channel that has never been tested.

## 2. Positive control fires

The control fires if **two** things hold. (a) With `gain` = 0 the three arms are bit-identical in `pop_time` and in the
cell count at every logged step — the buffer must be inert when its gain is zero, which is the anchor for the new code
path. (b) At `gain` = 3.0 the population must fall by at least 20 % against `gain` = 0 in the constant arm; if a mortality
buffer large enough to matter cannot move the population, the design is insensitive by construction and stops here.

## 3. Readout exists and varies

Readouts: `lineages_with_data`, the effective lineage count `q = 1`, deaths per 1000 cells, and the survival advantage of
the rarest lineage. They must vary across the three arms by more than the seed spread: the arm means must differ by at
least one between-arm standard error **and** the readout must not be pinned (a world where every lineage survives, or where
none does, carries no information).

## 4. Sensitivity arithmetic

The effect to be detected is a difference in effective lineages between real and surrogate. In the earlier equal-tempo
test (§10bo) that difference was 8.22 − 6.27 = 1.95 with 3 seeds per arm, i.e. inside the noise; the tempo effect, by
contrast, was 6.6 and therefore visible at n = 3. So the required sample is set by the *smaller* effect: with a seed sd of
about 2 effective lineages and a paired design (same seed, both signals), 20 seeds per arm give a standard error of 0.45,
which resolves a difference of 1.0 lineage. Runs are paired by seed. Total: 3 arms × 20 seeds × 3 values of `tau`
(300, 1 000, 3 000) = 180 runs of 1 800 steps, ~0.4 GPU-h at the pond's cost — CPU only, so wall time is the budget, not
GPU.

## 5. Refusal rule

If at every `tau` the real arm lies inside the bootstrap 95 % interval of the surrogate arm at equal tempo, the item is
recorded as **the structure of the signal does not matter in the mortality channel either** — the third independent
negative on the same hypothesis — and the "resonant medium" route is closed for this world with a named mechanism: no slow
variable to integrate into, and adding one does not help. If instead the real arm beats the surrogate at some `tau` but not
at others, the result is reported as a window in `tau` (the medium has a memory band), and the next item scans that band
finer.

## 6. What would kill it

A zero-gain anchor that is not bit-identical (the code path is not inert); a gain that does not move the population (no
manipulation); equal-tempo normalisation that drifts between arms (the comparison becomes tempo again); or a real-versus-
surrogate difference that disappears when the seed pairing is broken, which would mean the pairing, not the signal, made
it.

## 7. Implementation notes (not results)

The world needs two flags: `--memory-tau` (steps; 0 = off, and the off path must reproduce the current world bit-identically
on the anchor seed) and `--mortality-gain` (0 = off). The buffer is a scalar per world (`m`), updated as
`m += (s(t) - m) / tau` with `s` the signal sample at the world's tempo; the death probability of a cell is multiplied by
`1 + gain * (m - m_ref)`, where `m_ref` is the arm mean, so no arm gains or loses mass on average. The three signal files
already exist, including the phase-randomised and IAAFT surrogates, so no new data is needed.

Pre-registration written before any run; the run waits for the world freeze to lift (X158 still writing artifacts) and for
the anchor of the new path on the old seed.

## 8. Amendment 1 (2026-11-04 04:35, before any result was read)

The arithmetic of §4 assumed 0.4 GPU-hours for 180 runs, i.e. about eight seconds per run, extrapolated from the 600-step
anchor run at 2.5 s. The first four probe runs at 1800 steps took three to five minutes each and produced about a megabyte
of log apiece. The full 3 x 20 x 3 grid would therefore be twelve hours of wall time, not twenty-five minutes.

**Change, made before any outcome was inspected** (only the run count and the artifact size had been looked at, not a
single population or lineage number): the primary test is **one memory band, tau = 300, three arms, twenty paired seeds**
(60 runs, about four hours). The bands at tau = 1000 and 3000 become a separate queue item with the same design, to be run
if the primary test shows anything at all — comparing three bands against each other only makes sense after the primary
comparison has a direction.

Unchanged: the three arms and their normalisation (zero mean, unit standard deviation, so the mean of `m` is the same in
all of them), the positive controls (gate 0 bit-identical; a gain large enough to move the population), the readouts, the
readout-variation requirement, and the refusal rule (real inside the surrogate's interval at tau = 300 means the structure
of the signal does not matter in the mortality channel either).

The 600-step anchor did pass: the old code and the new code with `--memory-tau 0 --mortality-gain 0` agree in 131 of 131
summary fields, with `wall_seconds` the only difference (2.49 s against 2.74 s).

