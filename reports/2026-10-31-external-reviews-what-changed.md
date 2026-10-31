# What the five external reviews changed (31.10.2026)

Five independent model reviews answered our eight questions. This is not a summary: only what **changes** our work.
Two findings hurt, one corrects arithmetic, and several give the line a place in the literature.

---

## 1. It hurts: our Q8 measure is invalid, and it undermines `X46`

**The finding.** `I(ΔS_t ; ΔE_{t+1})` — mutual information between first differences — **can manufacture lag
information out of a purely simultaneous response**. One review gives the analytic case: if the environment is
independent noise and the state merely copies it, `ΔS_t = E_t − E_{t−1}` and `ΔE_{t+1} = E_{t+1} − E_t` share the term
`E_t` with opposite signs, so their correlation is **−0.5** and the MI is about **0.2075 bits** — with no predictive
ability whatsoever.

That is exactly our situation: the shuffled arm gave **0.175** against **0.053** for the moving one, and we already
suspected the measure was catching the simultaneous response. The reviews say the suspicion was right and name the
cause. Correct statistics: **conditional transfer entropy** `I(Y_{t+1} ; X_t | Y_t)`, **time-shifted surrogates**
instead of i.i.d. shuffling, **power simulation before the experiment**, and pooling runs rather than pretending 60
snapshots suffice.

**What it costs us.** The MI numbers of `X46` (§10dq) cannot be used as evidence. Worse, the geometric measure we
leaned on ("structures sit on the current event, 1.67 cells") was computed on the **last snapshot only**.
Recomputed across the whole trajectory:

| moment | distance from the trait centroid to the current event |
|---|---|
| first snapshot | 47.0 |
| **all snapshots** | **22.45** — the random level on a 96 torus (average ≈ 24) |
| last snapshot | 1.67 |

So the centroid converges onto the current event **only late in the run**, and the "1.67 cells" statement was a
late-phase fact presented as a general one.

**What survives.** The direction: at no point is the centroid closer to the future position than to the present one
(`lead40`: 23.21 versus 22.45 across all snapshots; 41.3 versus 1.67 at the end). "No anticipation" stands;
"structures sit on the event" **does not**.

**Action taken.** §10dq rewritten as a correction, the claim marked as not established, and the experiment replaced by
an **omission design** (`X49`), which the reviews recommend as the gold standard (Saigusa et al. 2008: remove the
event and see whether behaviour still anticipates it). Omission design does not need differencing and does not depend
on a surrogate choice.

---

## 2. It hurts less: `Q1` — memory is needed for a *vanished* cue, not for anticipation in general

**The finding.** No theorem says "anticipation requires memory" in general. A memoryless system can predict perfectly
when the current signal already determines the future (Becker, Mugler & ten Wolde: for a Markov signal, instantaneous
reading is optimal). What is necessary is that **information about the departed cue is retained somewhere** — and a
continuous field is already a state that can retain it.

**What changes.** We must not close "truth about the outside" as logically impossible. The precise statement:
*without any retained state, only the currently visible signal is usable; for a cue that has vanished, the information
must be held by the medium.* That keeps `X48` (memory) justified without over-claiming.

Counterexample worth knowing: Voss's anticipatory relaxation uses a delayed term `y(t−τ)` — it looks like "no model"
but it **is** memory. So the "no memory" camp has no physical example.

---

## 3. Arithmetic correction: our habitability threshold is `b ≈ 0.0075`, not `0.002`

One review did what we should have done: from `income ≤ 4·b·own` and `cost = 0.03` on the same unit,

```
b_crit = 0.03 / 4 = 0.0075
```

| `b` | income ceiling | ratio to cost | our observation |
|---|---|---|---|
| 0.002 | 0.008 | 0.27 | 20 of 21 die |
| **0.0075** | 0.030 | **1.00** | break-even, no growth margin |
| 0.010 | 0.040 | 1.33 | **still died** (max 274) |
| 0.020 | 0.080 | 2.67 | 10 of 10 survive |

**What changes.** Our §10dn states the ratio but not the threshold. And our own sweep already shows the effective
threshold is **above** break-even (0.010 dies at ratio 1.33), which the review predicted ("the ceiling is an upper
bound, so the real threshold is likely higher than 1"). That is a stronger and more useful statement than "the world
was uninhabitable by a constant": *the break-even constant is 0.0075, and the practical threshold is above it.*

**Literature place.** Maintenance energy (Pirt 1965), NutMEG `P_F = P_S − P_M`, protocell viability conditions
(Piedrafita et al.). Our result is then a **methodological warning** (check habitability before interpreting absence
of adaptation), not a new principle.

---

## 4. Literature place for the percolation result

No review found a critique of counting spots at a fixed threshold in Gray–Scott — and one found a **direct
methodological predecessor**: Joe (2016, thesis) analyses Gray–Scott with **persistence landscapes** over a
concentration threshold, and Spector, Harrington & Gaffney (2025) classify Turing patterns by persistence homology.

**What changes.** We keep the concrete finding (our two regimes are one percolation cluster; the threshold decides) but
**drop the general novelty claim** and cite: Wang & Ouyang (spots as a population variable with birth/death rates),
Joe (2016), Spector et al. (2025). Our `X26` sweep is literally a β₀(v) curve — we can say that, which is better than
presenting it as a new idea.

---

## 5. Literature place for "selection destroys variation"

Not a general law. Known retention mechanisms, and which are implementable in our world without new entities:

| mechanism | implementable as | cost |
|---|---|---|
| negative frequency dependence | make the interaction coefficient a function of local frequencies | low — reuses existing fields |
| **spatially varying optimum of the existing trait** | `k` optimum varies in space | **lowest** — one coefficient |
| cyclic dominance (spiral waves) | three types, Reichenbach 2007 | medium — needs types |
| dormancy / seed bank | a state with reduced maintenance cost | medium — new state |

**What changes.** Our §10dk conclusion is a **limitation of this class of media**, not a law. The next series should
use *spatially varying advantage of the existing trait*, with a rare-variant invasion test — not just "more
heterogeneity of resource", which the review warns can merely speed up the leader.

---

## 6. Name for the self-model result

Von Holst's **reafference / exafference** distinction, efference copy and comparator models; closed-loop identification
needs **persistent excitation** — an external signal orthogonal to the organism's own actions.

**What changes.** Our §4b wording becomes sharper and more defensible:

> detected predictive dependence for the resource that is inside the consumption loop; no independent external
> predictive ability detected.

And the operational test is named: **block the organism's action on the resource** (a "ghost" run) and see whether the
dependence survives. That is `X50`.

---

## 7. Venue for the negative result

**Artificial Life (MIT Press)** first, then ALIFE conference; precedent for the genre: Vasas, Szathmáry & Santos
(PNAS 2010) — "lack of evolvability in self-sustaining autocatalytic networks" — an organisation exists, a stronger
property does not follow. A "Why It Didn't Work" workshop existed at ALIFE 2022.

**What changes.** Title should state the measured limit, not "we found nothing": e.g. *"Organization without
transferable individuality in a reaction–diffusion world"*. And do not promise that the Zenodo preprint (CC0) is
compatible with the journal's prior-publication policy — that is a question for the editors.

---

## 8. What we do now — order of actions

| # | action | why now |
|---|---|---|
| 1 | **Rewrite §10dq** as a correction; mark the claim not established | it may be cited as published |
| 2 | **Recompute saved series** with conditional TE + time-shift surrogates (`X51`) | no new runs needed; the data exist |
| 3 | **`X49` omission design** | the recommended test; replaces the flawed one |
| 4 | **Update §10dn** with `b_crit = 0.0075` and the "threshold above break-even" observation | arithmetic, one paragraph |
| 5 | **Add citations** for percolation, habitability, variability, reafference, venue | cheap, prevents false novelty |
| 6 | **`X52` spatially varying optimum** | the reviews' cheapest retention mechanism |

---

## Honest summary

Of the eight questions, **four are now answered by the literature** in a way that changes our text (Q1, Q3, Q4, Q6),
**two give ready experiments** (Q2 omission, Q5 spatially varying optimum), **one gives a venue** (Q7), and **one
invalidated a measure we used** (Q8).

The most useful outcome is not the list of references. It is that **Q8 caught us using a statistic that manufactures
the effect it is supposed to detect** — and that `X46`'s conclusion survived only because the geometry pointed the
same way, while the "1.67 cells" phrasing did not survive a check across the whole trajectory.
