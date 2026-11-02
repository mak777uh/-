# X115 — does the faster line persist? Survival to the horizon, paired within sister pairs

**Why.** X113–X114 closed the consequence question in one currency: the larger sister's lineage reaches more generations, and it reaches them faster, on
equal windows. The currency that remains untested is the one that matters for "conditions for life": does a faster line still **exist at the end**?

That is answerable without new runs. For each sister pair, ask whether each branch's subtree has a member present at the last logged step. The pair is
its own control — same mother, same frame, same world.

## 1. Manipulation is connected

X108's twenty runs (restored and verified against the committed aggregates, see X114). For every sister pair, each branch is "alive at the end" if any
descendant of that sister (including the sister herself) appears in the **last logged step** of the run. Connectedness: at least **300 sister pairs** per
cell; the number of pairs where both branches survive, only one, and neither is reported, because a cell where everything survives cannot discriminate.

## 2. Positive control fires (numeric)

Two controls, both required:

1. **Heredity** `≥ 0.35` in both cells on the same pairs (0.548 / 0.480).
2. **The pairing reproduces X113:** the sister contrast in **depth** must come out at +1.479 / +2.213 within 5 %, i.e. these are the same pairs measured
   for a new question, not a new sample.

## 3. Readout exists and varies

Per cell: the paired difference in end-survival between the larger and the smaller sister (proportion), with a bootstrap 95 % interval; the counts of
"both / only the larger / only the smaller / neither"; and, as a secondary readout, the **number of living descendants at the end** (count ratio), which
is sensitive to how much of the line survives rather than whether it does.

## 4. Sensitivity arithmetic

~1 100–1 200 pairs per cell; with a paired proportion the SE is at most `1/(2√n)` ≈ 0.015, so the declared resolution is **0.05** in the survival
difference with an interval excluding zero. A difference below that is "not resolved", not "no effect". The secondary count readout is a ratio, reported
with the same interval.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 usable pairs, heredity below 0.35, the depth control missing its 5 % band, or if **every** pair has both branches
alive at the end (no discrimination — the run's horizon is too short for this question and it must be said so rather than reported as a null).

**Faster lines persist better** if the survival difference is positive with the interval excluding zero in both cells.
**No consequence in persistence** if the intervals contain zero in both.
**Mixed** otherwise, cells reported separately — and the maze is where X93's lifetime advantage reverses, so a split is informative rather than odd.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs (restored, verified) |
| readouts | paired end-survival difference; living descendants at the end |
| controls | heredity ≥ 0.35; depth contrast reproduces X113 within 5 % |
| artifact | `E09_pond/l1_field_x115_persistence.json` |

## Checklist

- [x] connected (300 pairs; both/one/neither counts reported)
- [x] positive control numeric (heredity ≥ 0.35; X113's depth contrast within 5 %)
- [x] readout exists and varies (survival counts spread over both/one/neither)
- [x] sensitivity computed (§4: SE ≈ 0.015, resolution 0.05)
- [x] refusal rule written, with "no discrimination" as an explicit void
- [x] no new runs: stated

## Status

Registered 2026-11-03 01:20 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
