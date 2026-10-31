# The elephant: simulation artifacts are a discipline, and we have been reinventing it under pressure

Written 31.10.2026 after harvesting and reading the real literature (94 → 80 papers via OpenAlex, then the abstracts of
the ones that matter). This is not a bibliography; it is what the field already knows, mapped onto our own failures.

---

## 1. What already exists — and it is a discipline, not anecdotes

The question "how do we know a simulation result is not an artifact of the simulation" has a name and a canon:
**verification and validation (V&V)** of computational models.

| work | what it establishes | verified |
|---|---|---|
| **Oberkampf & Roy, *Verification and Validation in Scientific Computing*, Cambridge University Press, 2010**, DOI `10.1017/cbo9780511760396` (1557 citations) | The systematic framework: **code verification** (does the code solve the equations we think?), **solution verification** (how large is the numerical error — discretisation, iteration, round-off?), **validation** (does the model correspond to reality?), and uncertainty quantification. | DOI resolved; abstract read |
| **"Verification of Computer Simulation Models", Management Science 14(2), 1967**, DOI `10.1287/mnsc.14.2.b92` (423 citations) | The problem was already framed **sixty years ago**, in management science, as a philosophical and statistical one — not as a coding nuisance. | DOI resolved; abstract read |
| **Morrison, "Computer Simulation: The Cooperation between Experimenting and Modeling", Philosophy of Science, 2007**, DOI `10.1086/519029` | Simulation is an **explorative cooperation** between experiment and model; the model is modified by the data during the process. Explains why "just run it and look" is epistemically unsafe. | DOI resolved; abstract read |
| **Parker, "Does matter really matter? Computer simulations, experiments, and materiality", Synthese, 2008**, DOI `10.1007/s11229-008-9434-3` | Whether a simulation can be an experiment at all, and what follows for its validity. | DOI resolved; open full text located |
| **Taylor et al., "The Past, Present, and Future of Artificial Life", Frontiers in Robotics and AI, 2014**, DOI `10.3389/frobt.2014.00008` | The field's own review, fourteen themes; shows that ALife has **no V&V tradition of its own** — it relies on community norms and replication. | DOI resolved; open full text |
| **Lehman et al., "The Surprising Creativity of Digital Evolution", Artificial Life 26(2), 2020**, DOI `10.1162/artl_a_00319` | The anecdote collection: digital evolution repeatedly surprises researchers, including by exploiting simulator bugs. | DOI resolved; abstract read |
| **Mitchell, Crutchfield, Hraber, "Revisiting the Edge of Chaos", 1993**, DOI `10.48550/arxiv.adap-org/9303003` | A cautionary classic in our own field: the "edge of chaos" story weakened when the experiment was redone with better statistics. | open full text |

**The elephant.** What we improvised as gates — anchors, negative controls, "check the manipulation reached the
dynamics", "compute the sensitivity before running" — are **fragments of V&V**, rediscovered one failure at a time. The
field has names for them, a taxonomy of error, and standard tests. We should use the names and the tests.

## 2. The standard taxonomy, and where each of our failures sits

| error class (V&V) | what it means | our instance |
|---|---|---|
| **code verification** | the code does not do what we think | `X46`: three arms with identical dynamics, because the lead only changed a recorded label. The manipulation was never connected. |
| **solution verification** | numerical error is large enough to matter | **never tested by us** — see §4 |
| **model formulation error** | the model cannot produce the phenomenon at all | the pond at `b = 0.002`: income ceiling 0.008 against cost 0.03. No adaptation was possible; we spent a day measuring its absence. |
| **analysis / statistical artifact** | the statistic manufactures the effect | `I(ΔS_t; ΔE_{t+1})`: differencing creates lag information out of a simultaneous response (external review, 31.10). |
| **observation error** | the sampling is not what we think | "1.67 cells" taken from the last snapshot; across the trajectory it is 22.45 — the random level. |
| **domain of validity** | the claim exceeds the parameter range tested | "the regime does not matter" at n = 20, where equivalence was never established. |

This mapping is the useful part: **we did not have five unrelated accidents. We had five known error classes**, three of
which a discipline already teaches how to test.

## 3. What we already do, under other names

| V&V practice | our name for it |
|---|---|
| code verification by independent path | **anchor**: bit-for-bit comparison against a pre-change run |
| negative control / surrogate | shuffled cue, shuffled positions, ghost arm |
| sensitivity analysis | amplitude dome, dose sweep, `b_crit` arithmetic |
| validation against an independent regime | grid 96 vs 128; 6000 vs 12 000 steps |
| provenance and reproducibility | manifests, journal, content hashes, artifact table |
| refusing a claim without an artifact | `claims_lint`, the "no row, no claim" rule |

That is a respectable list — assembled by necessity, not by reading V&V.

## 4. The one standard test we have never run

**Solution verification: does the headline number survive a refinement of the numerical scheme?**

Every number we publish comes from `dt = 1.0` and a four-neighbour Laplacian. In a continuous automaton, changing the
step or the grid can change the pattern — that is exactly the "non-Platonic" worry. We varied the **grid** (96 → 128,
where the effect reproduced with a weaker interval) but we have **never varied `dt`**, and never checked convergence.

This is cheap and it is the single most standard thing a computational paper is expected to do:

> **`X56_step_convergence`** — recompute the headline contrast (durable structures 1.3 vs 1.2; components 6.50 vs 2.81)
> at `dt = 0.5` and `dt = 2.0`. If the contrast holds in sign and rough magnitude, we state that the result is
> step-converged. If it does not, the number is an artifact of the integrator and must be reported as such.

Cost: 2 arms × 3 step sizes × 10 seeds × 6000 steps ≈ 60 runs, a few hours. It is the difference between "we report a
number" and "we report a converged number".

## 5. What this changes in the article

One sentence, and it should be added once `X56` is done:

> "The results are stable under refinement of the numerical scheme: changing the time step by a factor of two leaves the
> contrast in sign and within X % of its value at `dt = 1.0`."

Or, if they are not stable: the honest statement that the contrast depends on the integrator, which is a result in
itself and a warning for anyone reproducing it.

## 6. What we should not do

**Do not adopt the whole V&V apparatus.** Full validation against reality is impossible for our objects — there is no
"real" Gray–Scott world to validate against. What transfers is the part about **internal consistency**: code
verification, solution verification, negative controls, sensitivity, domain of validity. The rest — uncertainty
quantification with priors, model-form uncertainty — would be theatre in a world we invented.

## 7. The lesson in one paragraph

Humanity has already built the answer, and it is unglamorous: name your error classes, test the code against itself,
refine the scheme until the number stops moving, keep negative controls, and publish the range in which the claim holds.
We arrived at most of that by failing five times in one day. The one piece we never built is the simplest: **check that
the number stops moving when the numerics get better.** That is `X56`, and it should have come before the article, not
after.

---

## Sources, with what was actually checked

| checked | how |
|---|---|
| existence, venue, year, DOI of every work cited here | Crossref / DataCite via `scripts/verify_references.py` |
| content of the seven works above | abstracts from OpenAlex (`_hourly/lit_harvest3.json`), plus open full texts where listed |
| full texts read end-to-end | **none yet** — abstracts only; the three closest to our case (rounding 2012, molecular-evolution 1994, mutation biases 1999) have no abstracts and remain unread |

That last line matters: this page is a map, not a substitute for reading. `X55` and `X56` are the queue items.
