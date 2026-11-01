# Seven questions for the next run: environments and rules borrowed from living systems

1 November 2026, 15:05. Written to be sent to external models. Each question states what we already know, what we do not,
and **what changes in our design if the answer is one way or the other** — a question that cannot change anything is not
worth sending.

Context the models need, in one paragraph: we run a two-species reaction–diffusion world (Gray–Scott) on a 96×96 periodic
grid, and we treat thresholded connected components as "structures". We found that heterogeneous resource inflow destroys
the medium's own pattern wavelength, multiplies divisions of structures about eighteen-fold, and that our measure of
"heritability" (r = 0.97) is a property of the copying rule we imposed, not of the medium. We now want to know what a
*proper* environment would look like — one in which heredity, memory or inheritance arise from the medium and the
inhabitants rather than from a line of code.

---

## Q1. Ecological inheritance: what is the minimal operational definition?

Niche construction and ecological inheritance are well established conceptually (Odling-Smee, Laland). What we lack is an
operational recipe for a continuous medium: how much must a structure modify its surroundings before a daughter's
prospects are measurably changed by *what the parent left* rather than by the parent's own state?

- **What would answer it:** a minimal model (PDE or cellular) in which the modified environment is the *only* channel of
  transmission, with a measured effect size.
- **What changes:** whether we add a slow "habitat" field to our world (our option 2), and what magnitude it needs to be
  measurable above the inflow noise.

## Q2. Compositional heredity without a template: what has actually been measured?

There are claims that compositional genomes — a mixture that reproduces its own composition — can be inherited in
prebiotic compartments, and that fidelity depends on the interval between divisions. We could not verify the key paper
(see `library/lit-heredity-and-topology.md`), so we treat it as a lead.

- **What would answer it:** the primary sources with the actual measured quantity (fidelity versus division interval, or
  whatever they used), and whether the effect survives without a catalyst that is itself inherited.
- **What changes:** if the effect is real and measured, our world can implement it as a third species that is consumed and
  produced by structures; if it is only conceptual, we should not build on it.

## Q3. Heredity of *size* rather than composition: does anyone measure it in pattern-forming systems?

We can measure whether a daughter structure's peak area resembles its parent's, once daughters get their own identities.
A preliminary pass on one seed gives a correlation of 0.32 with slope 0.37 — some memory, far from a lineage.

- **What would answer it:** any study that measures parent–offspring similarity of a *geometric* property in a
  reaction–diffusion or cellular-automaton pattern system, with the analogue of a heritability coefficient.
- **What changes:** whether "size heredity" is a known null (structures regress to the medium's preferred scale) or an
  open measurement we can contribute.

## Q4. What rules from living systems are actually used as *medium* rules, not agent rules?

We can implement competition, decay, chemotaxis or quorum sensing, but most such rules are written for agents. Which of
them have been implemented as *field* rules in continuous media, and what did they change?

- **What would answer it:** a short list of field-level rules with references: resource competition (Monod-type uptake),
  chemotaxis (Keller–Segel), quorum sensing thresholds, division-of-labour switches.
- **What changes:** the menu of world modifications we consider next, and which of them are known to produce
  qualitatively new behaviour rather than a rescaled version of what we have.

## Q5. Stigmergy and the environment as memory: is there a measured example in a physical medium?

Ants and slime moulds leave traces that guide later individuals. In a continuous medium, a trace must decay and diffuse —
so "memory" has a lifetime.

- **What would answer it:** a physical or simulated system where the trace's decay time is measured and shown to control
  the collective behaviour (e.g. Physarum transport networks, termite mound models).
- **What changes:** whether a "trail" field is worth adding, and what decay rate would make memory longer than a
  generation.

## Q6. Dormancy and seed banks: is temporal storage a cheaper inheritance channel than spatial modification?

A dormant structure can survive a bad interval and reappear — inheritance through time rather than through space. In our
world, structures that fall below the threshold simply vanish.

- **What would answer it:** minimal models of dormancy in spatial ecology or microbiology with a measured effect on
  coexistence, and the smallest implementation that changes dynamics (a hysteresis threshold? a slow state variable?).
- **What changes:** whether we add hysteresis — the cheapest possible memory, one line of code — before anything more
  elaborate.

## Q7. What would falsify "the medium cannot carry heredity by itself"?

This is the question we most need and the one least likely to be asked. Our current reading is that in a two-species
reaction–diffusion medium, heredity is either imposed (our copy rule) or trivial (the pattern reconstructs itself).

- **What would answer it:** a published example of a two-species reaction–diffusion system with *no imposed genotype* in
  which a lineage-level property (size, period, composition) is nevertheless transmitted with measured fidelity across
  several generations.
- **What changes:** if such an example exists, we should reproduce it before building anything new; if not, our negative
  result is a contribution and should be stated as such.

---

## Search list, if the models can search

- niche construction minimal model PDE; ecological inheritance simulation measurable effect
- compositional heredity compartment division fidelity; "compositional genome" prebiotic measured
- heritability of spot size reaction-diffusion; parent-offspring similarity pattern forming system
- Monod uptake reaction-diffusion; Keller-Segel chemotaxis pattern coexistence; quorum sensing field model
- stigmergy decay trace Physarum transport network model; termite mound model decay
- dormancy seed bank spatial model coexistence threshold hysteresis
- non-Platonic / discretisation-dependent heredity; pattern memory in cellular automata

## What we would do with the answers, in order

1. If Q6 gives a cheap hysteresis recipe, implement it first — it is one line and it converts "structures vanish" into
   "structures wait", which changes every count we have.
2. If Q1 or Q5 gives a measurable modification strength, add the habitat or trail field (a day of work, with anchor).
3. If Q2 or Q7 gives a real example of medium-borne heredity, reproduce it before extending ours.
4. If Q3 shows size heredity is a known null, we report our 0.32 as confirmation rather than as a finding, and stop.
