# X3 closed: the claims comparator now compares, instead of reporting

**Date:** 2026-11-01, 20:40 MSK. **Item:** `X3_claims_expect_column` (queue), closed.
**Change:** `scripts/claim_comparator.py` gained an `expect` block; the six claim specifications in `lab/claims/` carry the
values they are supposed to produce.

## What was broken

`claim_comparator.py` recomputed each claim's contrast from the aggregate, printed it, checked that the *rule* held
(bootstrap interval excludes zero, or is inside a margin), and reported. What it never did was **compare the number to the
number that was written down**: a claim could stay "confirmed" while its contrast drifted, because nothing in the repository
recorded what the contrast was supposed to be. The audit of 01.11 called it "the gate that forgot to check values", and its
absence is what let `X35` happen — six rows whose numbers exist but whose provenance nobody could reconstruct.

## What was added

Each specification may carry

```json
"check": { "expect": { "contrast": 2.786, "median_a": 5.643, "median_b": 2.857, "n_a": 10, "n_b": 10, "tolerance": 0.02 } }
```

and the comparator now fails when the recomputed value differs from the recorded one by more than the tolerance (counts are
compared exactly, values to 0.02). The tolerance is deliberately tight: the six aggregates are committed, the computation is
deterministic, so any change above rounding is a change of the artifact and must be an explicit decision, not a silent drift.

## The six values, written down for the first time

| claim | contrast | arms (median a / median b) | n per arm |
|---|---|---|---|
| `L1_amplitude_domain` | 2.786 | 5.643 / 2.857 | 10 / 10 |
| `L1_global_noise_equals_constant` | 0.857 | 3.714 / 2.857 | 10 / 10 |
| `L1_heterogeneity_doubles` | 3.335 | 6.478 / 3.143 | 50 / 50 |
| `L1_pattern_beats_global_noise` | 1.857 | 5.571 / 3.714 | 30 / 30 |
| `L1_regime_irrelevant` | 0.143 | 6.286 / 6.143 | 20 / 20 |
| `L1_static_beats_varying` | 0.143 | 6.286 / 6.143 | 20 / 20 |

## Controls

- **Positive:** with the values as they are, `claim_comparator.py --ci` returns 0 with six claims and no refusals.
- **Negative:** setting `L1_regime_irrelevant.expect.contrast` to 9.99 makes the gate fail with
  `дрейф значения contrast: ожидалось 9.99, получено 0.143 (допуск 0.02)` and exit code 1. The value was restored
  afterwards, and the gate is green again.

## What this does not fix

The comparator still only speaks about the six claims that have a specification in `lab/claims/`. `manuscript/CLAIMS.md`
holds far more rows without a machine-checkable spec, and `X35` showed that some of them cannot be reconstructed at all. The
`expect` mechanism is the right shape for the ones that can: a specification, a value, a tolerance, and a gate that fails
when the artifact moves.
