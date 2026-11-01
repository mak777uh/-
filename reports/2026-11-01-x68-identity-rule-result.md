# X68: the lifetime contrast belongs to the feedback channel, not to the geometry

1 November 2026, 14:35. Thirty runs, three identity rules, in the one regime where the rule is separable from the
dynamics. Preregistration and its amendment:
[`2026-11-01-x68-identity-rule-plan.md`](2026-11-01-x68-identity-rule-plan.md), both committed before the data.

## The check that changed the experiment

The first design varied the overlap cutoff with the feedback channel on (`beta = 0.2`), and its own leak check rejected the
run within one seed: `components` differed between rules. The reason is structural and worth stating separately:

> Composition is carried **per component**, inherited along the identity, and it modulates local growth. Change which
> daughter inherits which parent's composition and you change the field.

So in this world **the identity rule is part of the dynamics**, not a lens on it. That makes the original design
impossible — a lifetime difference between rules would confound the rule with a different trajectory — and it is the first
time one of our own design checks has killed a design before it produced a number.

The amended design switches the feedback off (`beta = 0`, `eps = 0`), where the field is identical across rules by
construction. The leak check then passed (`leaks: 0`), so any difference in lifetimes is the rule's doing.

## Result — and it reverses the published ordering

| overlap rule | heterogeneous median lifetime | homogeneous median lifetime | seeds with hetero below |
|---|---|---|---|
| 0.3 (loose) | **5999** | 4030 | 0/5 |
| 0.5 | **5044** | 1565 | 0/5 |
| 0.7 (strict) | **2607** | 1565 | 0/5 |

The published numbers — median 57 steps in the heterogeneous world against 4046 in the homogeneous one — were measured with
the feedback **on**. In the same geometry with the feedback **off**, the ordering is the opposite at every rule: the
heterogeneous components live **longer**, not shorter.

## What this means

**1. The lifetime contrast is a property of the feedback channel.** The short-lived fragmentation we published is produced
by composition inheritance feeding local growth — the two-channel world — and not by the spatial organisation of the field.
Without that channel the same field fragments into fewer, longer-lived components.

**2. Lifetimes are rule-dependent in magnitude.** In the neutral world the heterogeneous median moves from 5999 to 5044 to
2607 as the cutoff rises from 0.3 to 0.7 — a factor of 2.3 — and the number of uids moves from 1 to 7 to 47. Any lifetime
number must therefore name its rule, and the published 57 and 4046 must carry the same label.

**3. The ordering is stable within a regime.** All five seeds agree at every rule, in both directions across regimes. So
the rule changes the magnitude, and the feedback channel changes the sign — which is a cleaner statement than "lifetimes
are sensitive".

## What this does to the published sentence

The v1.6 text quotes lifetimes with their rule attached, which was the right instinct and is now shown to be necessary
rather than cautious. What it does **not** say, and now must, is that the contrast belongs to the **feedback world**: it is
a statement about a trait carried along lineages and paying for its carrier's growth, not about structures in a field.

That is a strictly better sentence, and it was found by a check that was written to protect the number rather than to
attack it.

## What is not claimed

- Five seeds per rule in the neutral world; the sign agreement is 5/5 everywhere but the design is small.
- The neutral world is not the published world: `beta = 0` removes the very channel whose effect we are comparing. The
  comparison across regimes is between designs, not between runs of one design.
- Nothing here says the published 57/4046 are wrong — they are correctly measured *in their own regime*, and now correctly
  labelled.

## Artifacts

`morphogenesis/experiments/L1_field/x68_ov{03,05,07}_{pattern,homog}_s{171..175}.json` (30 files), aggregate
`morphogenesis/experiments/E09_pond/l1_field_x68_identity.json`. Scripts: `scripts/x68_series.py`,
`scripts/x68_analyse.py`.
