# X161 — Integers are no more heritable than real numbers: the discrete state is re-drawn at every division (04.11)

**Question.** Everything this line has measured is continuous — area, elongation, log width, spacing — and continuous traits
dilute. Digital media inherit in **discrete** units: a lineage tree is a set of integers, and a discrete state cannot be
diluted halfway. If such a state is inherited, it is the mechanism a digital medium has and a physical one does not, which is
exactly why it deserves a measurement rather than an assumption.

Pre-registration: [`2026-11-04-x161-discrete-heredity-plan.md`](2026-11-04-x161-discrete-heredity-plan.md). Analysis only —
no new runs. Every field-track artifact already carries `uid_pairs` (parent → child edges) and `uid_outcomes` (each body's
first and last logged step, its peak area, its score at birth), so the trees were already on disk: 15 runs, **2 778
parent-daughter pairs**.

## Result

| trait | parent → daughter slope | correlation | shuffled-parent null (2.5-97.5 %) | per-run median slope |
|---|---|---|---|---|
| peak area (positive control) | **0.546** | 0.49 | — | 0.531 (0.31 to 0.79) |
| division order (children per division) | **−0.163** | −0.03 | [−0.240, 0.136] | 0.000 (−1.01 to 0.86) |
| lifespan (logged steps) | **0.101** | 0.05 | [−0.007, 0.199] | 0.076 (−0.39 to 0.74) |
| fertility (divides at all) | not testable | — | — | — |

The positive control fires: peak area reproduces the block's own value (0.55 pooled, 0.53 per-run median, against the 0.39-0.45
of the positional reconstruction in X156), so these trees are the same objects the rest of the line measured.

Neither discrete trait clears its null. Division order's pooled slope is **negative** and its per-run values run from −1.01 to
+0.86 with a median of exactly zero — the classic signature of a quantity that is re-drawn, not transmitted. Lifespan sits at
0.10 with a null reaching 0.20.

**Verdict: the discrete state is re-drawn at every division.** In this medium integers are no more heritable than real
numbers, and the digital ratchet that the literature promises — a discrete state that survives without dilution — **does not
exist here**.

## Fertility cannot be tested this way, and that is a fact about the design

A sterile body leaves no descendants, so it cannot transmit its sterility, and every parent in `uid_pairs` is by construction
fertile. The parent side of the comparison has no variance at all. Fertility's absence of inheritance is therefore a matter of
**definition**, not measurement, and the item says so instead of printing a null that would look like a result. Testing it
would need bodies tracked that never divide — a different design, and one that would have to follow non-dividing bodies for
their whole lives.

## What this changes

The article's answer to "what does a division transmit" now has its sharpest negative. Continuous traits are transmitted with
a slope well below one (0.39-0.45 for area, 0.20 for spacing, 0.59 for elongation), and the one class of trait that could
have been transmitted intact — an integer — is transmitted not at all. A digital medium does not automatically provide a
ratchet; it provides a discrete **notation**, and the notation alone carries nothing across the division. This is the
strongest support yet for the paper's framing that what is inherited here is a **field state**, not a code.

## Limits

Lineage trees are built from `uid_pairs`, i.e. from the tracking rule's own bookkeeping, so a trait that changed without
changing uid would be invisible; the area control shows the trees track real quantities, but not that they track all of them.
Division order takes only the values 2 and 3 (plus 0 for sterile), so its range is tiny and a transmission of 0.2 would be
hard to see even in 2 778 pairs. And the analysis pools runs of different lengths and different initial conditions; the
per-run slopes show the pooling is not hiding a consistent sign, but they do not remove the heterogeneity.

## What would kill it

A ten-run series at one initial condition where division order's slope is consistently positive across runs would say the
pooling hid a signal. A trait with a wider discrete range — the number of children over several divisions, or a body's
position in a cascade — would have more room to show transmission and is the fairer test of the same question.

## Next hypotheses

1. **A wider discrete trait**: the depth at which a lineage goes sterile, or a body's generation index at first division —
   integers with a real range, unlike the two-valued division order.
2. **A discrete state that is not a count**: the score class at birth (`s` binned into 0.2-wide bins, which is how the world's
   own trait mechanism works) — the world already has a discrete trait machinery, and this asks whether *that* is inherited.
3. **Tracking-invisible change**: a body whose uid changes without dividing would look like a division to this analysis; count
   how often uid changes with no split in the component count, and bound the error.
