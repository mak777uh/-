# P8b closed: a claim may only cite an artifact that is in git, and the check is now a gate

**Date:** 2026-11-01, 20:55 MSK. **Item:** `P8b_cited_artifacts_gate` (queue), closed.
**Tool:** `scripts/check_claim_artifacts.py`, in `make verify` and CI.

## Why it was open for a week

`lab/retention-policy.md` proposed the gate on 26.10 and nothing implemented it: `claims_lint.py` checks that an artifact
path *exists on disk*, which is a different statement — a file in a scratch directory exists and is still not part of the
record. `X35` was the cost: six claim rows sat downgraded for days because their numbers lived in per-run files whose arms
nobody could reconstruct.

## What the gate does

It reads every `.json` token in `manuscript/CLAIMS.md` and in the six specifications under `lab/claims/`, normalises the
relative prefixes (`../`, `./`) against the citing file, and requires each token to be either tracked by git or present on
disk. `_hourly/` references are excluded here and counted by `check_hourly_refs.py`, which has its own documented baseline
of 93 — a known gap stays in one place instead of being reported twice.

## The result, which is the point

**48 distinct `.json` tokens, 3 excluded (`_hourly/`), 0 broken.** The claims of this repository cite artifacts that are
actually in git. That is worth stating because the opposite was assumed: the audit of the queue expected this gate to open a
large list of offenders. It opens none.

Negative control: a planted specification citing `morphogenesis/experiments/E09_pond/does_not_exist_42.json` makes the gate
fail with exit code 1 and names the file and the token; removing it returns 0.

## What it still does not catch

- **Bare names.** A row that cites `v8_matrix.json` without a path is accepted if any tracked file has that name. That is
  deliberate (the matrix rows are written that way), and it means the gate cannot tell which of several same-named files was
  intended.
- **Provenance beyond existence.** A tracked artifact can still be the wrong one; only reading the number back (the `expect`
  mechanism of `X3`) catches that.
- **Reports.** Only the claims matrix and its specifications are scanned. Reports cite aggregates too, and a report citing a
  lost file is the same class of error — that is `P9` territory, and it is still open.
