# X61-long: no, the concentration is not the start of selection

1 November 2026, 09:00. Five runs of 24 000 steps. Preregistration:
[`2026-11-01-x61-long-horizon-plan.md`](2026-11-01-x61-long-horizon-plan.md), committed before the run.

## The question

On the 128 grid the heterogeneous arm was broadband at physical times 2000 and 4000 and then, at 6000, reached peak
share 0.38 with entropy 1.97 — just short of the bars fixed in advance. Two readings fit: selection slowly starting, or a
large-scale drift. The discriminating variable is time, so the same world was run four times longer at the cheaper grid.

The run is comparable by construction: its first 7 snapshots reproduce `x59_a50_s171` **exactly**, checked before the
remaining seeds were started.

## Result

| steps | peak mode | peak share | spectral entropy |
|---|---|---|---|
| 6 000 | q = 1 | 0.247 | 2.27 / 2.48 |
| 12 000 | q = 11 | 0.150 | 2.34 / 2.48 |
| 18 000 | q = 1 | 0.282 | 2.20 / 2.48 |
| 24 000 | q = 11 | 0.250 | 2.20 / 2.48 |

**Verdict: neither.** The share does not rise monotonically (0.247 → 0.150 → 0.282 → 0.250), it never approaches the 0.5
bar, and the entropy stays at 2.20–2.34 against a maximum of 2.48 — as flat a spectrum as this measurement produces. The
peak mode alternates between q = 1 and q = 11 with nothing to prefer either.

So the 0.38 seen at 128 was not the beginning of anything. On four times the horizon the heterogeneous world still selects
no wavelength, and it keeps a constant division rate: median **860 divisions** over 24 000 steps against 308 over 6 000 —
the same rate per step, four times the events.

## What this settles

The X60/X58 claim is now the strongest version it can be at this cost:

> **In this world heterogeneous inflow does not merely delay wavelength selection — it prevents it, on every horizon and
> grid we have tested.** The homogeneous arm selects twelve units within 4 000 time units; the heterogeneous arm has not
> selected anything after 24 000, and its spectrum stays near the flat maximum.

That also removes the caveat the X58 report had to carry ("never was too strong a word — it is a window"). It is not a
window for the spectrum. It *is* still a window for the hole count (X60: β₁ excess gone by t = 6000), and the two
statements are now cleanly separated: **topology of the transient, spectrum of the medium.**

## What it does not settle

- Grid 96, five seeds, one amplitude. The 128 grid was run only to 12 000 steps.
- The division rate is constant, but whether those divisions transmit anything selectable is E6p's question, and the
  answer there was: they transmit mechanically.
- A longer horizon could still surprise, but at a rate of one observation per 6 000 steps and no trend across four of
  them, the burden of proof has moved to whoever claims selection.

## Artifacts

`morphogenesis/experiments/L1_field/x61l_a50_s{171..175}.json`, fields at four times in `x61l_fields/` (20 arrays),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x61l_horizon.json`. Scripts: `scripts/x61l_series.py`,
`scripts/x61l_analyse.py`.
