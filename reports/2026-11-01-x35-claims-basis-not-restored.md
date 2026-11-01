# X35: the numbers are in git, the arms are not — six claim rows stay at "observation"

**Date:** 2026-11-01, 20:50 MSK. **Item:** `X35_restore_claim_artifacts`, closed as *not repairable mechanically*.
**What was attempted:** restore the basis of six published claim rows from `наблюдение` to `статистика` by matching their
numbers to aggregates that the audit of 01.11 said already exist.

## What is actually true

The audit promised: "all named aggregates exist — `v8_matrix.json`, `frequency_start_control.json`, `lab/runs/20261025T*-w2bud_*.json` — match each of the six numbers to a field, restore `статистика`, one hour". Checked one by one:

| row | number in the claim | where it is | in an aggregate? |
|---|---|---|---|
| 60 | `pop_time 11885`, isolation `403/304` | `colinv4_fd10_AinvB_inherit_n20_seed10.json`, `found_n1_seed10.json` | no |
| 65 | `+10.7 % random`, `+11.3 % learn`, `+21 %` on the gradient | `colinv3_*` / `colinv4_*` (74 files) | no |
| 66 | `71313 ± 5701`, `70956 ± 5409`, `58890 ± 5436`, `71792 / 72121 / 79469` | `colinv4_*`, `b2d_patches_adapt_*`, `found_n*_seed*` | no |
| 68 | `pop_time 8144 / 3563 / 2629`, `sd 28 тыс. → 5.4–5.7 тыс.` | `found_n*`, `colinv4_*` | no |

Three aggregates were opened and searched field by field: `frequency_matrix.json`, `frequency_matrix_v2.json`,
`frequency_start_control.json` contain **none** of those numbers. The only aggregator in the repository that touches this
family, `scripts/colony_matrix.py`, covers design 3 (`colinv3_*`) and reports **growth rates**, not `pop_time` medians;
run on the pond directory it produces 24 rows with growth values 0.66–2.86 and does not contain any of the claim numbers.

## Why a guess would be worse than the downgrade

The arm labels live in the **file names** (`colinv3_fd10_AinvB_inherit_seed1.json`: frequency dependence, invasion
direction, policy) and nowhere else: the artifacts carry `summary` and `log` but no `params`. The claims name three policies
(`random`, `learn`, `fix`) while the files offer two (`random`, `inherit`) plus a variant of the invasion direction, and
nothing in the repository records which file is which policy. Rebuilding an aggregate on a guessed mapping would produce a
number that *looks* verified — a new aggregate with a fresh hash, pointing at real files — and that is exactly the failure
mode the downgrade was introduced to prevent.

So the six rows stay at `наблюдение`, and the honest statement is narrower than the audit's: **the numbers are in git, the
arm mapping is not.** `наблюдение` is the correct basis for a number whose protocol cannot be reconstructed from the
repository.

## What would actually restore them

1. The original protocol document (or the runner) that says which file family is `random`, which is `learn`, which is
   `fix`, and what "согласованный старт" changed. If it exists in scratch or in an old report, one paragraph would be enough.
2. An aggregator in the repository that reads `summary.pop_time` across a family and writes per-arm medians and spreads,
   with the arm from the filename and the mapping from point 1. Roughly 60 lines, in the shape of `x70_analyse.py`.
3. A note in the claim row naming the aggregate and the field, as `claims_lint.py` requires.

Until (1) exists, the rows are correct as they are: the claim is supported by observation, not by a reproducible statistic.

## Note on the other rows

Rows 47 and 52 (half-life versus generation; invader not retained) were not in this batch — the first is already marked
`опровергнуто`, and the second's evidence (`v8_matrix.json`) does exist and is cited in the report of 24.10. Nothing was
changed in `manuscript/CLAIMS.md`, because a basis is not restored by editing a word.
