# Claims audit, 03.11: what the manuscript still says, and what moved under it

3 November 2026, 23:05. The first step before any paper: find out where the manuscript stopped, and whether the numbers
it already contains are still the numbers we would write today.

**Inputs.** `manuscript/paper.md` v3.5 (frozen 28.10, 1 584 lines); `manuscript/CLAIMS.md` (186 rows: 143 `статистика`,
39 `наблюдение`, 2 `суждение`, 1 `доказательство`, 1 `тест`); `manuscript/CHANGELOG.md` (last entry 02.11, X101–X107);
`lab/queue.json` (56 X-items closed on 02–03.11); 171 reports dated 02–03.11.

## The frontier

The last result the manuscript knows is **X107**. Everything after it is missing — not "thin", missing.

| where | last content | date |
|---|---|---|
| `paper.md` §4k.1 | X101–X107 (size heredity), stops before the dense remeasurement | 02.11 |
| `CHANGELOG.md` | entry for X101–X107 | 02.11 |
| `CLAIMS.md` | one row for the field line after X107 (X154, added today) | 03.11 |
| `manuscript/README.md` map | `L1_field → §4k, §4k.1` — no row for any 03.11 block | — |

The freeze is not a coverage failure of the gates: X-items are queue items, not `registry.json` experiments, so
`lab.py validate` has nothing to compare them against. The map is green because it covers the experiments it knows.

## What the manuscript says that is now wrong

These are corrections, not additions. Each one is a sentence a reader could check.

**1. The ladder in §4k.1 is the sparse version.** The table (0.531 / 0.384 for the excursion set, 0.300 / 0.174 for the
basin, medians 76 / 423 and 112 / 81) was measured on fields saved every 50 steps. X108 re-measured the same worlds with
a field at every step:

| definition | 0.030 sparse → dense | 0.040 sparse → dense |
|---|---|---|
| excursion set `v > 0.20` | 0.531 → **0.548** | 0.384 → **0.480** |
| basin by steepest ascent | 0.300 → **0.335** | 0.174 → **0.110** |
| median size area / basin | 76 / 112 → 83 / 109 | 423 / 81 → 400 / 81 |

The ladder survives and gets **stronger** at the maze inflow (Δ −0.370 against −0.209 sparse), but the numbers in the
table must be the dense ones. The manuscript already carries X105's caveat that the sparse series understates the maze
cell by a quarter; the table itself never followed.

**2. The specificity collapse is overstated.** §4k.1 says the parent-versus-stranger gap falls "0.312 / 0.215 →
**0.017 / −0.010**", i.e. to zero. That is the sparse basin gap. Dense (X108): threshold gaps **0.302 / 0.443**, basin
gaps **0.089 / 0.064**. So:

- the collapse is real and large (−0.213 and −0.379);
- the stricter registered branch — *"the basin gap is ≤ 0.05 in both cells"* — **did not fire**;
- the honest sentence is "small, but not zero: under the basin definition a mother still beats a neighbour slightly",
  and at the maze inflow the threshold gap is **0.443**, the largest in the line, not the 0.215 the manuscript prints.

**3. The third field is described as future work and it is not.** §4k ends with *"to make heredity physical the trait
must live in the medium — a third slowly diffusing quantity (X32)"*. X96 implemented it, anchored it bit-for-bit, and
answered: **no scale channel in the living regime** (`q'` stays 7–9 while `Dw` spans 8×`Dv`), orientation moves instead
(0.636–0.837), and it does not replicate (X96d: 2 of 6 cells at |ρ| ≥ 0.8, opposite signs); `gamma_cell` = **0.30** in
both cells (X110). The sentence must become a result with a negative in it.

**4. The threshold axis is missing from §4k.1.** §4k's boundary contrast (0.52–0.62, stable to resolution at 2 %) is
fine and is *not* what the cut sweep measured. The cut sweep measured the heredity coefficient: at cuts 0.15 / 0.20 / 0.25
`ρ₁` = 0.554 / 0.548 / 0.445 in the lattice and 0.408 / 0.480 / 0.420 in the maze, while the parent-versus-stranger gap
is cut-stable (deltas −0.018 / +0.024 and within a 0.10 bar; X112b, X112c). So the level is cut-bound by one step and the
specificity is not — a caveat that belongs next to the ladder in §4k.1, where the threshold is a free parameter of the
observer. *(This finding corrects the first version of this audit, which put the cut axis on §4k's contrast; those are
two different quantities.)*

## What has no home yet: three blocks, 56 items

### A. The second species and the definition axis (X96–X112c, 9 items)

Beyond the sentence in §4k above, the block's own result is a negative: a third slowly diffusing field does **not**
create a scale channel in the regime where the world is alive; what moves is orientation of the diffusion, and that does
not replicate. `gamma_cell` = 0.30, and the fragility X96d saw belongs to `Dw`, not to `gamma`. **Place:** rewrite the
last paragraph of §4k (§4k's "X32" sentence), no new section needed.

### B. Identity: what makes the end of a lineage an end (X97–X132, 24 items, 6 of them voids)

This block is one argument in five steps and has **no section at all**:

| step | result | numbers |
|---|---|---|
| size buys generations | sister contrast, partial with depth | +1.479 (1.289–1.654) / +2.213 (1.962–2.489) |
| size buys speed | rate version, after X113b was voided | +6.06 / +18.96 generations |
| the advantage is not window or occupancy | equal 3 000-step window; persistence | +0.407 / +0.638; +0.250 / +0.137 |
| matching on daughters halves it | exposure, not parenthood alone | 0.250 → 0.125; 0.137 → 0.044 |
| the identity of the ending | absorption ≈ half of all endings; **the lattice keeps families apart, percolation mixes them** | 55.3 / 47.8 / 48.4 % absorbed; sisters merge back 18.4 % (median 80 steps); sibling-neighbour 87.2 % (lattice) vs stranger 62 % (maze) |
| world level | the death fates separate habitats; the survival contrast does not | vanished +0.178, kin −0.443, survival **−0.077 unresolved at ten worlds** |

X132 then resolved the last line at thirty worlds and **moved the headline**: paired end-survival difference
**−0.1323 (CI −0.1819 … −0.0840)** against −0.077 on ten seeds. Power price 30–40 worlds. A block that also produced
four honest voids (X124, X125, X128 — coherent, and instructive) and one retired contradiction (X125c: 22 % ties, the
fractions 0.526 / 0.388 with X93's values inside both intervals).

**Place:** a new §4k.2, *"What makes the end of a lineage an end"* — five paragraphs, one table, the voids named in
one sentence each rather than in five.

### C. Coalescence is not reproduction (X134–X154, 15 items)

Also homeless, and it is the cleanest positive result of the line:

| claim | numbers |
|---|---|
| the mixing length is a **wall**, not a gradient | 10/10 seeds merge at 8 and 12 cells, none at 18 (X134), replicated and freed from placement (X134b: 15–18) |
| the crossover and the rule | 16 ± 1 cells at radius 3; **2r + 9** (radius 4.5 → 18 ± 1, 5/5 at 16, 2/5 at 18) |
| the rule is not size | in the three arms where both outcomes occur, the dividing seeds are not the larger ones (X148) |
| the boundary moves inward with the radius | radius 4.5 at gap 8 is M 3/5, A 2/5 where radius 3 is M 5/5 (X147); saturation at radius 6 (X150) |
| **the outcome steps, the time mixes** | radius 6, gap 7.5: 10/10 merge, all at step 39; gap 8.0: 5/10 merge at 49, 5 stay separate; slow fraction 0.0 / 0.0 / 0.2 / **1.0** (X153, X154) |
| the merge is mutual, and it is not a birth | mutual coalescence in every seed out to a surface gap of 8 (X142); a lone disc divides at a median of 180 steps (X145) |

**Place:** a new §4k.3, *"Coalescence is a merger, not a birth"* — the registered control 3 that **failed** must appear
in it verbatim (radius 6 has 113 cells, not "at most 2 per disc"), because it is the same kind of admission §4k.1 makes
about the sparse series.

## Hygiene that follows

1. `CLAIMS.md` has no rows for blocks A, B, C except X154's. Nine rows are needed (three per block), each with its basis
   type; the four corrections above need **new** rows, not edits of the old ones — the file's rule is append-only, and
   two of them (the ladder and the specificity collapse) contradict sentences that are already standing in the draft.
2. The map (`manuscript/README.md`) should gain one row per new section, or the next audit will start from X154 and
   repeat this work.
3. The manuscript is in Russian; all of the above must be written in English (31.10 decision). That is a translation of
   the new text, not of the whole book — worth deciding separately.

## Order of work this audit implies

| # | step | size | why first |
|---|---|---|---|
| 1 | fix the four wrong sentences in §4k / §4k.1, with dense numbers and the failed branch named | 1 hour | they are already wrong, and cheap |
| 2 | write §4k.3 (coalescence) | ~1 day | strongest result, self-contained, no dependency on X155 |
| 3 | write §4k.2 (identity) | ~1 day | it carries the X132 correction and the voids |
| 4 | X155, then one paragraph in §4k.2 or a new §4k.4 on heredity | 0.1 GPU-h + a day | decides whether the heredity sentence is "mechanical" or has a number |
| 5 | decide about the pond as a second paper, and about translating the book | owner | the gate: E02c closed, independent reproduction, owner's ok |

Steps 1–3 together are the skeleton of the field paper, and none of them depends on a new run.

доска: принято 2, отклонено 0, отложено 0 (B-095, B-096 on 03.11, both accepted; no new remarks raised by this audit).
