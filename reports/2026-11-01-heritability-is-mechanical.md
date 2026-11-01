# The heritability we measured is mechanical

1 November 2026, 04:05. A check that took one command and removed a temptation.

## What was checked

The `x23` artifacts record, per run, `splits`, `parent_child_pairs` and `inheritability_r` — the correlation between a
parent's composition and its daughter's. At 03:20 those numbers looked like a finding: the fragmenting (heterogeneous)
world has **357.5** divisions per run against **17.5**, **885** parent–child pairs against **42**, and `r` = **0.972**
against **0.812**. The obvious story was "fragmentation manufactures lineages".

The competing story is that `r` is an artefact of the copying rule. In `scripts/field_track.py` a daughter **inherits the
parent's composition with a fixed mutation**, so fidelity is imposed by the rule, and the only interesting question is
whether it degrades when divisions are frequent.

## What was found

Across the 24 runs that record both quantities, **Spearman(splits, r) = +0.79**: more division goes with *higher*
measured fidelity, not lower.

| arm | low-division half, median `r` | high-division half, median `r` |
|---|---|---|
| heterogeneous | 0.970 (n = 7) | 0.975 (n = 7) |
| homogeneous | 0.733 (n = 5) | 0.829 (n = 5) |

There is no dilution trade-off in this world; if anything, frequent division *protects* fidelity, because a component
that keeps splitting is re-copied before its composition can drift. The difference between the arms (0.97 against 0.81)
is likewise explained: the homogeneous arm divides rarely, so its components are old and drifted.

## What it changes

**Before:** "heterogeneous inflow multiplies lineages, and lineages are where selection could act."
**After:** "heterogeneous inflow multiplies **divisions and parent–child events**; the measured heritability is
imposed by the copying rule and therefore says nothing yet about the medium."

This matters because the tempting version would have gone into the article and into the next design. The version that
survives is narrower and testable: selection needs variation that the copying rule does not guarantee, which is exactly
what criterion `S1` tests — does mean composition drift against the `eps = 0` control, with `I_obs > I_null(95 %)`.

## What is still true

- The division-rate contrast (357 against 17) is a fact about the two worlds and does not depend on the interpretation.
- The homogeneous world's lower `r` is a real consequence of long-lived components drifting, and it is worth one
  sentence: rare division means old structures, and old structures are drifted ones.
- The corridor to a selection claim exists; it just runs through `S1` and the null yardstick, not through `r`.

## Reproduction

    python - <<'EOF'
    # 24 runs, x23_*: spearman(selection.splits, selection.inheritability_r) = +0.79
    EOF

Artifacts: `morphogenesis/experiments/L1_field/x23_*.json`. Reference for the trade-off that does *not* appear here:
`library/lit-heredity-and-topology.md` §1 and §4.
