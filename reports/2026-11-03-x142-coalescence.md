# X142 — mutual coalescence holds in every seed out to a gap of eight cells, and its time is a function of the gap alone

**Plan:** [`2026-11-03-x142-annihilation-plan.md`](2026-11-03-x142-annihilation-plan.md) (registered 15:45, two amendments
in flight; the first replaced the readout after the "annihilation" turned out to be a tolerance — see
[`2026-11-03-x139-void-annihilation.md`](2026-11-03-x139-void-annihilation.md)).
**Aggregate:** `l1_field_x142_coalescence.json`. **Runs:** 35 new (radius 3 gaps 3, 6, 7, 9; radius 4.5 gaps 4, 5, 6) plus
40 reused, 75 in the analysis.

## What was asked, and what changed under it

The sweep was registered to map an *annihilation band* — a region of gaps where two discs destroy each other. Reading
the merge step in X139's own logs killed that question before the first arm was analysed: at separations 10 and 11 the
two seeded uids die on the **same** logged step and the next step holds **one** component under a **new uid**. Both
arms are one event; the old labels differed only in whether the partner's last position fell inside a 2-cell reach
tolerance. The arms stayed, the readout changed: **M** (mutual coalescence — neither seed grows a daughter and both
subtrees are gone at the end), **A** (absorption — exactly one subtree alive), **P** (persistence — both alive).

## The result

| gap (cells) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| radius 3, class | M 5/5 | M 5/5 | M 5/5 | M 5/5 | M 5/5 | M 5/5 | M 5/5 | **M 5/5** | **M 3/5, A 2/5** | M 2/5, A 2/5, P 1/5 | M 2/5, P 3/5 |
| radius 3, median step both lineages gone | 10 | 10 | 10 | 20 | 20 | 30 | 40 | **50** | 70 | 80 | 115 |
| radius 4.5, class | – | – | – | M 5/5 | M 5/5 | M 5/5 | M 5/5 | – | – | – | – |
| radius 4.5, median step | – | – | – | 20 | 20 | 30 | 40 | – | – | – | – |

Two statements, both of them new:

1. **Mutual coalescence holds in every seed from contact out to a surface gap of eight cells**, and the gaps measured
   are complete at one-cell spacing from 1 to 11. The break is not a hole and not a band: at gap 9 three seeds of five
   still coalesce, at gap 10 two, at gap 11 two while three keep both lineages. The transition is a **thinning**, and
   it sits at gap 8–9, i.e. at separations 14–15 — inside the mixing length of §10hc, as it should be.
2. **The time is a function of the gap alone.** At every gap measured on both radii — 4, 5, 6 and 7 — the median time
   to mutual coalescence is **identical**: 20, 20, 30 and 40 logged steps. Doubling the radius (29 cells of area to 64)
   moves the centre distance by exactly `2R` and leaves the time untouched. The curve is monotone from the first logged
   step after seeding (gaps 1–3) through 20, 30, 40, 50, 70 and 80 steps — a floor at the logging quantum, then a rise
   of about ten steps per cell of gap, steepening to twenty beyond a gap of eight. (The aggregate records `t_dissolve`,
   which is this step number minus one: the last step at which the second seed still exists is the one before.)

The gap rule of §10hd said the *crossing* is set by the absolute gap. X142 says the same for the whole curve, on the
inner side and at one-cell spacing: what the pair does, and when, depends on the distance between the surfaces and not
on how big the structures are.

## The mechanism this points at

Read from the parent links rather than the component count, the arms differ in *whether a disc ever gets a daughter*:

| gaps | seeded disc splits before the pair is one body? | outcome |
|---|---|---|
| 1–8 | never — neither seed has a daughter at any step | both lineages end in the new body (M) |
| 9–11 | in some seeds, at steps 100–170 | the daughter(s) carry the lineage (A or P) |

A lone radius-4.5 disc splits at 150–280 steps and a lone radius-6 disc at 210–460 (`x140_sep0_s*`, `x138_sep0_s*`),
while a pair at gaps 1–8 is one body by step 10–50. So the boundary is a **race between touching and splitting**: a
pair coalesces when the two discs reach each other before either grows a daughter, and survives when a split happens
first. That is a mechanism with two measurable clocks, and the missing number — the split time of a lone **radius-3**
disc, the one this whole block uses — is registered as X145.

## Controls

The probe repeat (a fresh run of X139's gap-5 arm) came out **identical** in `series`, `uid_pairs` and summary
(key-by-key outside the volatile fields), so the path has not moved; every arm starts as two components; no run ends
empty; the reused arms reproduce what their series published — at gaps 6 and 9 (re-run because X136's logs for those
separations were retired) five of five seeds have a first death as X136 said, and the new classes only split those five
into M and A, which is exactly the refinement the void predicts. Three runs end structurally fragmented (one seed each
at gaps 5, 8 and 4.5/gap 7: a quarter of the grid in sixty-odd patches, largest under 50 cells) and are reported as
fragmentation, not as death.

One control fired in the wrong direction at first and is worth recording: `control 1b` demanded that the re-run arms
give "A ≥ 5", i.e. that they reproduce the old **label**. They give M 5/5, and the analyser printed a void. The control
was asking the new classes to reproduce a label the correction exists to remove; it now checks what must be conserved
(the number of seeds with a first death and the number with both lineages alive).

## Caveats

- Two radii, one inflow (`F = 0.030`), five seeds per arm, 6 000 steps, logging every 10 steps: the times are quantised,
  and "the second of the two uids is gone" is resolved only to one quantum.
- The radius-4.5 sweep covers gaps 4–7 only; the claim "the time depends on the gap alone" rests on four gaps, and the
  radius-4.5 breakdown (if any) between gaps 8 and 9 is not measured.
- "Mutual coalescence" is genealogical: neither seeded uid leaves a daughter and both are absent at the end. Whether the
  merged body's cells come from both discs in equal share is not measured here.
- The split times quoted for lone discs are medians over five seeds at radii 4.5 and 6, not at radius 3.

## Next hypotheses

1. **X145 — the lone radius-3 disc.** Five runs of `--init-spots 3:0`: if it splits at ~60 steps the boundary is the
   race, if at 150–200 it is not.
2. **X146 — does the coalescence time track the wavelength rather than the gap?** The 9-cell gap is three quarters of
   the 12-cell pattern; changing the pattern's wavelength (a second inflow where the readout's `q'` differs) would say
   whether the time curve scales with the pattern or with the cells.
3. **X147 — the radius-4.5 breakdown.** Gaps 8 and 9 at radius 4.5, four arms, to place the second radius's transition
   and test the "same gap, same boundary" prediction directly.

доска: принято 0, отклонено 0, отложено 0.
