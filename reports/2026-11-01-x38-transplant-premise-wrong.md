# X38 closed: the density test already uses every struct transplant we have

**Date:** 2026-11-01, 21:05 MSK. **Item:** `X38_transplant_replication` (queue), closed — premise wrong, not "replication missing".

## What the item said

`X38` asked to replicate the transplant analysis "from 216 rows to 1000+", on the grounds that the density effect
(+0.231, CI [−0.013; +0.232], p = 0.29) rested on too few rows and that `transition_matrix_rep_exploratory.json` — 1296 rows
— had not been used for it.

Both halves are wrong, and the arithmetic is in the files.

## What the files show

| file | rows | struct-sourced rows | kept their class | died |
|---|---|---|---|---|
| `transition_matrix_exploratory.json` | 144 | **24** (12 `struct_1` + 12 `struct_2`) | 3 | 14 |
| `transition_matrix_rep_exploratory.json` | 1296 | **216** (108 + 108) | **21** | **126** |

The numbers §10dh-доп reports — 216 rows, 21 kept, 126 died — are exactly the struct subset of the 1296-row matrix. So the
density test already uses **all** struct transplants that exist: 12 targets × 3 source seeds × 3 noise seeds per class.

The 1296 rows are not "more of the same": they are the same design with **more source families** (`death` 648,
`uniform_dark` 324, `uniform_bright` 108). Replicating the density test on all 1296 would mix transplant outcomes with
sources that have no structure to keep, which is a different question.

## Verdict

**Nothing to recompute; no replication was missing.** `X38` is closed with that correction. The limitation noted in
§10dh-доп stands and is now stated precisely: the conclusion rests on **21 surviving transplants**, and raising that number
requires new runs of *struct sources* — 5–10 times the current 216, i.e. about 1000–2000 struct transplants, not re-reading a
bigger file.

## What this changes in the plan

§10dh-доп's limitation paragraph said "нужна репликация в 5–10 раз больше (216 → 1000+ строк)". That is still true, but it
must say **struct rows**: the 1296-row file already exists and does not help. The correction is appended to §10dh-доп.
