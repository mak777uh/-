# X134b — with the placement now free, the wall is at 15–18 cells, and merging inside the wavelength is deterministic

**Plan:** [`2026-11-03-x134-mixing-plan.md`](2026-11-03-x134-mixing-plan.md), amendment 4.
**Aggregate:** `l1_field_x134b_mixing.json`. **Series:** 15 runs, three separations (12, 15, 18) × five seeds, `F = 0.030`, anchor exact.

## Why it was re-run

X135's single-disc control found that the first `--init-spots` branch placed the discs at **fixed centres** and discarded the seed-dependent mask, so the five "seeds" of the
X134 sweep were **one world measured five times** (identical merge step and identical subtree sizes at every separation). X134's threshold survived that as a
deterministic fact, but its replication language did not. The probe now places the pair at a **seed-derived offset**, separation preserved, and is anchored again
key-by-key with the flag absent.

## The result

| separation | absorbed | both alive | median steps to absorption | per-seed times |
|---|---|---|---|---|
| 12 | **5 / 5** | 0 / 5 | **19** | 20, 20, 20, 20, 20 |
| 15 | **5 / 5** | 0 / 5 | **49** | 60, 50, 60, 50, 50 |
| 18 | **0 / 5** | **5 / 5** | — | — |

**The wall is between 15 and 18 cells** — a tighter bracket than X134's 12–18, and it survived a change of placement, which is what a replication is for. The two
sides are still complete: 10 of 10 seeds merge at 12 and 15 cells, 5 of 5 keep both lineages at 18.

**And the seeds now differ where they should.** At 18 cells the five placements give five different subtree sizes (93, 66, 65/67, 117/127, 117/127), and at 15 they
give two distinct merge times (50 and 60 steps) — so the readout is sensitive to placement at the wall. At 12 cells the merge time is **20 steps in all five
placements**: well inside the wavelength, merging is placement-independent, which is what a deterministic instability looks like.

The wavelength in this habitat is 12 cells, so the mixing length is **slightly above one wavelength** (15–18 against 12) rather than exactly one. That correction goes
to X134's claim: the equality "one wavelength" was an artefact of a bracket that started at 12 and had no point between 12 and 18.

## What this changes in the record

1. **X134's threshold numbers** (12–18) become **15–18** — the old bracket was not wrong, it was coarse and its lower bound was the last tested separation inside the
   wavelength, not a measured edge.
2. **X134's replication claim** is corrected: its five seeds were copies. The wall itself is unaffected, and this run is what makes the statement replicated.
3. **The pattern-wavelength equality** is downgraded from "is" to "slightly above", and the CLAIMS row that said "the threshold sits between 12 and 18 cells where the
   period is 12" now carries the corrected bracket.

## Controls

The anchor is exact with the flag absent (`uid_pairs` identical; the only declared differences are the two field-saving keys and the inert `init_spots` parameter).
Every run starts as exactly two components, every run is alive, and the two-disc arms span both outcomes in the same proportions as X134. The placement dependence is
visible where it should be (18 cells, subtree sizes) and absent where it should be (12 cells, merge step 20 in all five).

## Caveats

- Three separations, five seeds, one inflow, one radius: this is a **targeted replication of the bracket**, not a re-run of the full sweep, and it is declared as such.
- The 3-cell bracket is the spacing's limit: the wall could be at 16 or 17.
- The five placements are five positions on a periodic grid of 96², not five different worlds; a placement near the domain edge would be a different test.

## Next hypotheses

1. **X136 — the bracket at 1-cell spacing around 16** and at three inflows: this is what turns "slightly above one wavelength" into a measured relation between the
   mixing length and `q'`.
2. **X135b — the maze at low forcing.** The percolating cell's seeding failed because the forcing overwrote it (X135 void); the same sweep at `--hetero-amp 0.15`
   would let the seeds survive long enough to say whether the maze's mixing length is longer.
3. **X137 — kin versus strangers at the same separation**, which the placement fix now makes possible: seed one disc as a daughter of the other's ancestor and
   repeat 12/15/18.

доска: принято 0, отклонено 0, отложено 0.
