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

---

## Amendment 2 (written 04.11, before any arm comparison was read)

The first grid ran and produced **nothing**: three arms with identical `pop_time` (742.0) and `killed_by_memory` = 0 in all
sixty runs. That is not a null result, it is a manipulation that never reached the dynamics, and the positive control of
§2 caught it. Three independent faults, all fixed, all recorded in `docs/incidents.md` §14:

1. the signal values were loaded onto the config while the hook read the instance, so the hook returned at its first line;
2. the kill count was truncated to an integer (`int(gain·dev·n)`), which is zero while the population is small;
3. the reference was the buffer's own running mean, so `dev` was ≈ 0 by construction — measured −1.06 with a kill
   probability of 4.6·10⁻⁸.

With the reference taken from the stream's long-run mean and per-cell Bernoulli killing, a one-step probe kills cells
(8 in 900 steps), and the summary now reports `memory_calls`, `memory_dev_mean`, `memory_prob_mean` and
`killed_by_memory` for every run.

## Second defect, found by the same probe: the design was insensitive by construction

At `income = 0.02` against `update_cost = 0.03` the pond goes extinct at step 21 in a single probe and at step 109 in a
seeded run with four start cells (`alive_cells = 0` in the final block). A world that is empty cannot express a storage
effect, so the whole grid was insensitive **regardless of the buffer** — the §3c failure, not a code failure. A sweep at
600 steps is running to choose an income at which the control arm survives in at least four of five seeds.

## What changes, and what is fixed before the data

1. **Reference.** `dev = m − mean(stream)`, where the mean is the one written by the loader from the signal file, not a
   running mean of `m`. Fixed before any arm was compared.
2. **Killing.** Per cell with probability `min(1, gain·dev)`, expectation unchanged for large populations.
3. **Income.** Set to the lowest level of the sweep at which the control survives in ≥ 4/5 seeds at 600 steps, and the
   number is recorded in this amendment before the grid starts: **income = 0.030**. The sweep (600 steps, five seeds, no
   buffer) gave 4/5 survivors at 0.030, 0.034 and 0.038 with `alive_cells` in the final block of 0/891/560/244/899,
   0/878/570/274/905 and 0/870/585/314/914 — i.e. **income is not the lever**: seed 801 goes extinct at step 109 at every
   level, and `clonal_fraction` sits at 0.98-0.99 everywhere. That is recorded here as a property of the world at grid 32
   with four start cells (near-monoculture with a one-in-five extinction risk), not as a reason to look for another knob.
   The buffer's room is therefore narrow by construction, and the readout that decides is `clonal_fraction`, not survival.
4. **Grid.** Three arms (`const`, `real`, `surrogate`) × **twenty** seeds (801-820), 1 200 steps (the runner's
   `STEPS` is 1 800 and the step count is therefore 1 800, not 1 200), `tau = 300`, `gain = 0.02`, grid 32, income 0.030.
   Sixty runs, about two and a half hours. The seeds and the step count are those of the runner that is actually
   executing; the ten-seed figure earlier in this amendment was written before checking the runner and is corrected here
   while the const arm - the null arm - is the only one that has run.
5. **Positive control (b), sharpened.** Not merely "the active arms die differently": `killed_by_memory > 0` in both
   active arms, and `memory_dev_mean` non-zero. A run that reports zero kills is a failed run, reported as such.
6. **Readout.** `clonal_fraction` at the end and the survival of both types; the buffer is supposed to slow the loss of
   diversity, so the statistic that decides is the between-arm difference in `clonal_fraction` at step 1 200, with the
   `const` arm as the reference.

## What would make this amendment dishonest

Choosing the income by looking at the *difference between arms* rather than at *whether the control survives*. Only the
latter was looked at: the sweep runs no buffer at all, so it cannot show an arm difference.
