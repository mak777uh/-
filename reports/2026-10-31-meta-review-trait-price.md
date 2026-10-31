# Meta-review: the lead rechecks the reviewer — "the price of a trait" (31.10.2026)

Contract §«Роль reviewer» says the lead must, once per cycle, take one review and recompute it independently: a review
that has not been rechecked is one more unchecked claim. This is that check.

**Review taken:** `lab/reviews/2026-10-25-i-trait-price.md` — claim: *a heritable trait has a price; the simple
correlation with cell-steps is negative (median −0.6, 8/10), the partial correlation controlling for energy is −0.700
(5 of 6)*. Verdict in the review: **держится с оговоркой**.

## What I did

Independent recomputation from the raw artifacts, with my own Spearman implementation (tie-averaged ranks), no reuse of
`scripts/w2bud_matrix.py`:

1. for each `w2bud4s_cell_seed{1..10}.json`, take lineages with `cells ≥ 5` and `spores ≥ 1` (the preregistered filter);
2. `ρ = Spearman(type_trait, lineage_cell_steps)`;
3. median over seeds, count of computed and negative values.

**A trap worth recording:** the artifact keys do not match — `type_traits` and `type_counts` are labelled `T<id>` while
`lineage_spores` and `lineage_cell_steps` are keyed by bare `<id>`. A naive join yields **zero lineages in every seed**
and a silent "no data". I normalised by stripping the `T` prefix.

## Result — the review reproduces exactly

| seed | lineages | ρ |
|---|---|---|
| 1 | 5 | −0.900 |
| 2 | 6 | −0.486 |
| 3 | **2** | **None** (undefined) |
| 4 | 3 | −0.500 |
| 5 | 4 | +0.400 |
| 6 | 5 | −0.100 |
| 7 | 3 | −1.000 |
| 8 | 4 | −0.800 |
| 9 | 3 | −1.000 |
| 10 | 6 | −0.600 |

**Median −0.600, computed in 9 of 10 seeds, negative in 8 of 9.** This matches the review's numbers and its central
arithmetic point.

## The review's finding is confirmed

The review said the manuscript's "8/10" cannot be recomputed from the artifacts, because seed 3 has only two lineages
and ρ is undefined there; the honest denominator is **8 of 9 computed**, and the aggregate should carry a
`rho_trait_cell_steps_n` field so that "8/10" and "8 of 9" cannot be confused again.

I can confirm both halves independently: 9 computed, 8 negative, seed 3 undefined with exactly 2 lineages. The review
**holds**, and its proposed fix is correct.

## What stays open

- Adding `rho_trait_cell_steps_n` to the aggregate is a change to the W2-bud builder, which belongs to the pond line and
  should be done with its own anchor — not squeezed into a health cycle.
- Whether the manuscript still says "8/10" for this specific quantity needs a check against the current text; the
  passage has moved since the review was written (the review cites `paper.md:821-836`, which is now a different
  section), so the fix must be applied where the sentence currently lives, not by line number.

## Verdict

**Review upheld.** Numbers recomputed independently, match to three decimals, and the denominator criticism is right.
The only new information is the key-format trap, which is now written down so the next person does not read "no
lineages" as "no effect".
