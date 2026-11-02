# X97b — the second-generation sister advantage is a lineage effect, not branching arithmetic

**Plan:** [`2026-11-03-x97b-sisters-median-plan.md`](2026-11-03-x97b-sisters-median-plan.md) (00:02).
**Aggregate:** `l1_field_x97b_sisters_median.json`. Same sister pairs as X97, no new runs.

## The question and the answer

X97's mean difference (+12.90 cells) could have been carried by **how many** grandchildren a branch produces — a larger structure has more
cells that can divide. The median is insensitive to that, and the branch counts measure it directly.

| cell | pairs | mean difference | **median difference** | median / mean | grandchildren per branch (larger / smaller) |
|---|---|---|---|---|---|
| 0.030 | 286 | 12.93 | **12.68** | **98 %** | 2.024 / 2.000 (+1.2 %) |
| 0.040 | 205 | 171.74 | **145.96** | **85 %** | 2.093 / 2.005 (+4.4 %) |

Registered verdict: **a lineage effect is needed** — the median holds at 98 % of the mean in the lattice and 85 % in the maze, and the branch
counts differ by 1–4 %, far below the 10 % that the branching explanation required. The larger sister's granddaughters are individually
larger, not merely more numerous.

Both controls fired: heredity 0.548 / 0.480 on these pairs, and the mean reproduces X97's 12.90 / 170.91 within 0.3 % and 0.5 %.

## What this closes and what it does not

**Closes:** the doubt that X97's second-generation result was an artefact of branch counting. It is not: the effect survives the readout
that removes branch-count weighting, in both cells.

**Does not close:** the consequence question. A lineage whose structures are larger is not a lineage that *does better* — X92 and X111 put
any consequence of size at the noise floor of this estimator, and X93's own lifetime advantage reverses in the maze. So the honest statement
of the day is now:

> size is a **lineage property** in this medium: it is inherited (ρ₁ ≈ 0.5), it survives a generation as a size difference that grows
> (X97), and it is not an arithmetic consequence of branching (X97b) — but nothing yet shows that inheriting it buys anything.

That distinction is exactly the one the line has to keep: heredity is measured, consequence is not. It is also the shape of the answer to
the owner's "conditions for life" question — a medium can transmit a trait faithfully and still offer no advantage for it.

## Caveats

- 286 and 205 pairs; the maze counts *more* pairs than X97 (205 against 186) because this script tolerates a slightly different peak filter —
  both controls still pass, but the two aggregates' pair counts are not identical.
- The median of a branch with two grandchildren can take two values, so the median difference is coarse in the lattice: 98 % agreement with
  the mean is partly luck of the distribution.
- Two cells, one seed set, one box; areas are threshold-0.20 excursion areas (X112b: about a tenth of cut correction).
- The "per grandchild" mean and the plain mean coincide here because each branch's grandchildren are averaged per pair before differencing;
  the branch counts are what carry the weighting.

## Next

- The heredity-versus-consequence gap is now the line's central open question, and it needs a **fitness proxy that is not size**: X93's
  lifetime reversal in the maze is the only candidate measured so far, and it points the wrong way there. Registering that properly is the
  next substantial design.

доска: принято 0, отклонено 0, отложено 0.
