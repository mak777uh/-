# X96b pilot — the scale cannot be imposed through the initial condition either

**Date:** 2026-11-02, 13:25 MSK. **Kind:** pilot (three single runs, not a series) — recorded because a negative answer here
removes a whole channel from the queue.

**Why it was tried.** X82 showed that modulating the inflow cannot move the morphological period: a second spectral line at up to
sixteen times the power of the first leaves `q'` where it was. X84 showed the medium has **one** period. The remaining untried channel
that needs no new world rule was the **initial condition**: instead of a single seed drop, start the field with a periodic pattern at a
chosen wavelength and ask whether the grown structures inherit it.

**What was run.** Runner gained `--init-pattern-cells` / `--init-pattern-fill` / `--init-pattern-binary` (flags off = old behaviour,
anchored: `--init-pattern-cells 0` reproduces the flags-off run bit-for-bit — `series` and `uid_pairs` identical, 600 steps).
`F = 0.030`, 6000 steps, seed 171, everything else as X74.

| start | outcome |
|---|---|
| full-field periodic, 8.7 cells, fill 1.0, binary | **died**: 0 components at 6000 |
| full-field periodic, 24 cells, fill 1.0, binary | **died**: 0 components at 6000 |
| full-field periodic, 8.7 cells, smooth, fill 0.5 | **died**: 0 components at 6000 |
| seed drop **plus** weak periodic bias, 8.7 cells, fill 0.05 | survived, 68 components; spectral peak at bin **9** (4602) with bin 8 at 3765 and bin 11 at 3309 |

## Reading

1. **A periodic start does not pattern at all.** A field pre-filled with the reaction mixture on a cosine lattice relaxes to the uniform
   state and dies, at both 8.7 and 24 cells and at two amplitudes. The medium needs a **nucleus**, not a seed field — an initial
   condition that is everywhere periodic is not a stronger version of the drop, it is a different and lethal one.
2. **A weak bias does nothing to the period.** With the drop restored and a 5 % periodic bias added, the grown pattern peaks at bin 9
   against the medium's own 8 — one bin, i.e. inside the ±1 bin spread that X74 already reports across worlds.
3. Therefore the window between "bias too weak to matter" (5 %) and "seed strong enough to kill" (50–100 %) is where a real test would
   have to live, and it is narrow. Nothing here suggests it contains an effect of the size the inflow channel already failed to produce.

## What this closes

The initial-condition channel is **not** a way to impose the scale, on this evidence. Two channels are now closed by measurement
(inflow, X82; initial condition, here) and the third — a **second diffusive species** — is a new world rule and therefore on the owner's
desk (queue `X96_scale_channel`, `waiting_on: owner`). Until that is decided, the field line has no way to ask what a genuinely
two-scale medium would do, and says so.

**Honest limits of the pilot:** one seed, one inflow, three starts, one horizon; no positive control beyond the survived/failed contrast
itself, because a pilot is a screen for whether a series is worth registering, not a measurement. If the second-species channel is
approved, this pilot's job is to have prevented a 40-run series that would have died on its first cell.

доска: принято 0, отклонено 0, отложено 0.
