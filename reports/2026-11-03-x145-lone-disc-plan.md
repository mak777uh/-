# X145 — when does a lone disc split, and is the mixing length that race?

**Why.** X142's corrected readout (amendment 2) leaves the boundary between *mutual coalescence* and *persistence*
unexplained. Reading the merge step suggests a mechanism: a pair in coalescence ends because the two discs **touch
before either splits**, while a pair that persists is one where a disc **splits first** and the daughters carry the
lineage. The numbers on both sides already exist in different experiments:

| what | steps | source |
|---|---|---|
| lone radius-4.5 disc splits | 150, 150, 190, 230, 280 | `x140_sep0_s*` (F = 0.030) |
| lone radius-6 disc splits | 210, 290, 290, 290, 460 | `x138_sep0_s*` (F = 0.030) |
| pair at gap 8 coalesces | 40-50 | X136 (`x136_sep14`) |
| pair at gap 10 coalesces | 70-170 | X136 (`x136_sep16`) |
| pair at gap 11 | 100-170, and 3/5 seeds split at 150-170 | X136 (`x136_sep17`) |

The mixing length (gap 9-10, separation 15-16) is where the coalescence time reaches the order of the splitting time.
But the missing number is the one that matters: **a lone radius-3 disc** — the disc that is actually used in the whole
mixing-length block — has never been run alone in this world. If it splits at, say, 60 steps, then the pair at gap 8
merging at 50 is inside the split time and the pair at gap 10 is outside it, and the mixing length is a race between
two measurable times rather than a length in its own right.

## 1. Manipulation is connected

`--init-spots 3:0` places one radius-3 disc: the flag's two centres coincide, so the initial condition is a single
disc and nothing else (`x140_sep0_s*` and `x138_sep0_s*` are the same construction at other radii, and both were used
as controls by their own series). Same inflow `F = 0.030`, same seeds 601-605, same 6 000 steps, same dense logging.
The manipulation is the **absence of a partner**, which is what the comparison needs.

| arm | runs | source |
|---|---|---|
| radius 3, one disc | **5 new** | this run |
| radius 4.5, one disc | 5 | reused from X140 |
| radius 6, one disc | 5 | reused from X138 |

## 2. Positive control fires (numeric)

Four controls. **The control fires if** all four hold:

1. **The reused arms reproduce their split times** as recorded above (radius 4.5: 280, 190, 230, 150, 150; radius 6:
   210, 460, 290, 290, 290). A change means the readout moved.
2. **The new arm starts as one component** of area ≥ 20 cells at the first logged step, and it is one disc, not two.
3. **The new arm's world never empties** (occupancy ≥ 5 % of the grid at the last step).
4. **The split time is read from the parent links**, not from the component count: the first step at which a uid
   present from the start has a daughter.

## 3. Readout exists and varies

The split time of a lone disc already varies across radii and seeds (150 to 460 steps), and within a radius by more
than 2× (150 to 280 at radius 4.5), so the readout is not stuck at a floor or a ceiling before the new arm is run.

## 4. Sensitivity arithmetic

Five seeds per radius, split times reported per seed with their median; the resolution is the 10-step logging
quantum. The comparison that matters is an **order-of-magnitude** one — coalescence at gaps 1-8 happens at 10-50
steps, splitting at radii 4.5 and 6 at 150-460 — so a five-seed median at radius 3 is enough to place the disc on one
side or the other. No continuous difference is claimed, and no threshold is applied.

## 5. Refusal rule (fixed before the run)

**Void** if a reused arm misses its recorded split times (control 1), if the new arm does not start as one component
(control 2), or if a run ends empty (control 3).

The registered outcomes:

- **The disc splits early** (median ≤ 100 steps): coalescence at gaps 1-8 happens *before* the disc would split, and
  the mixing length is the gap at which the merge time reaches the split time — a race between two measured times.
- **The disc splits late** (median ≥ 150 steps, in line with radii 4.5 and 6): the split time is not the boundary at
  radius 3, and the mixing length comes from the pair's own dynamics, not from a single disc's instability.
- **The disc never splits** in 6 000 steps: the pairs at gaps 10-11 that split are being *triggered* by the contact,
  and the mechanism is the interaction, not a clock.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots 3:0` (one disc, same additive construction as X134b/X138/X140) |
| runs | 5 new at `F = 0.030` (seeds 601-605), 10 reused |
| readouts | first split step per seed, components at the end, occupancy |
| controls | reused arms reproduce their split times; one component at the start; the world never empties; split read from parent links |
| artifact | `E09_pond/l1_field_x145_lone_disc.json` |

## Checklist

- [x] connected (the manipulation is the absence of a partner; the same construction at other radii is already a control)
- [x] positive control numeric (two reused radii must reproduce their split times seed by seed)
- [x] readout exists and varies (150 to 460 steps across radii and seeds)
- [x] sensitivity computed (§4: an order-of-magnitude comparison, five seeds, 10-step quantum)
- [x] refusal rule written, with early split / late split / never splits as separate outcomes

## Status

Registered 2026-11-03 16:10 MSK, before the run. Light field run, no training.
