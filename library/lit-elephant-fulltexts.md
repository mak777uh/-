# Feeling the elephant: four papers read end-to-end

31.10.2026. Following the harvest of 80 real papers, I downloaded and read four in full — the ones closest to our own
situation. This is not a summary of abstracts; the texts were extracted from the PDFs and read (`_hourly/fulltexts/`).

The short version: **the literature does not say "refine until it converges". It says the opposite is possible, and it
has a name for it.** That changes what our `X56` can claim.

---

## 1. Davis & Bongard, *Step Size is a Consequential Parameter in Continuous Cellular Automata*, ALIFE 2022

DOI `10.1162/isal_a_00526`, arXiv `2205.12728` — 3 pages, read in full.

**What they did.** Took continuous cellular automata (Lenia and its relatives), where the update is

```
A(t + dt) = A(t) + dt · f(A(t))
```

and swept `dt` while holding the rule fixed.

**What they found.**

- A minimal glider is stable only between roughly `dt = 0.245` and `0.978`; smaller or larger and it vanishes.
- A second pattern under the same rules is most stable near `dt = 0.1`, and at that value is only *pseudo*-stable —
  sensitive to initial conditions, grid dimensions and floating-point precision, and it eventually destabilises after
  thousands of steps.
- Behaviour changes **qualitatively** with `dt`: the same starting "frog" hops at 0.1, meanders at 0.025, corkscrews at
  0.0125, and occasionally explodes at 0.13.

**The sentence that matters for us**, quoted because it is the whole point:

> "This defies the expectation that in simulations of physical system we typically expect greater accuracy as the step
> size approaches zero. What would be considered systematic error in simulating billiard ball trajectories is essential
> for self-organization by some CA patterns."

They also explicitly contradict Chan's suggestion that decreasing `dt` asymptotically approaches the ideal simulation:
for several patterns, a lower step size gives *different behaviour or no pattern at all*.

## 2. Davis, *Non-Platonic Autopoiesis of a Cellular Automaton Glider in Asymptotic Lenia*, ALIFE 2024

DOI `10.1162/isal_a_00786`, arXiv `2407.21086` — 4 pages, read in full.

**Context.** Kojima & Ikegami (2023) had removed Lenia's clipping operation and argued that non-Platonic behaviour
probably depended on clipping, and that asymptotic Lenia (ALenia) gliders are likely unaffected.

**What Davis found.** An ALenia glider that persists for 100 steps at `Δt = 0.2` and **disappears at 0.17 or 0.26** —
with no clipping anywhere. When simulated at *too fine* spatial or temporal resolution, it "no longer maintains its
morphology or dynamics".

**Why this is the sharpest case for us.** The fix was applied, and non-Platonicity remained. Robustness is not
guaranteed by removing the suspected mechanism; it has to be tested **per pattern**, not per simulator.

**The term.** "Non-Platonic autopoiesis": the pattern's self-maintenance exists in the simulation, not in the ideal
continuum the equations describe. That is not a coding error. It is a statement about **which object the claim is
about**.

## 3. Kojima & Ikegami, *Implementation of Lenia as a Reaction-Diffusion System*, ALIFE 2023

DOI `10.1162/isal_a_00638`, arXiv `2305.13784` — abstract and formulation read.

**What they did.** Showed that asymptotic Lenia can be described by differential equations, is **independent of
time-step ticks** (unlike original Lenia), and is mathematically equivalent to a generalisation of the kernel-based
Turing model; then implemented it as a reaction–diffusion system ("RD Lenia").

**Why it matters.** It shows that the timestep dependence of original Lenia is traceable to a specific operation —
clipping into `[0, 1]` — and that removing it yields a formulation with a genuine continuous-time limit. This is the
constructive answer: not "beware artefacts", but "here is a scheme whose limit exists".

## 4. Pilat, Suzuki & Arita, *Dealing with Rounding Error Problems in Evolutionary Physical Simulation*, 2012

DOI `10.1007/s10015-012-0038-0` — 4 pages, read in full.

**What they did.** A simple virtual creature on a plane, moved by a neural controller, with fitness = displacement.
They varied the **initial position** by multiples of 0.001 and recorded fitness.

**What they found.** Fitness varies chaotically with initial position — a plot that should be a straight line is noise.
The cause is floating-point rounding, and it appears after only a few steps and grows with evaluation time. With 10 000
steps, single precision gives mean 96.4 with sd 56.5. Double precision does **not** rescue long runs (mean 69.4 at
10 000 steps). In an evolutionary run, this variation lets selection discard fit individuals by accident.

**Their proposed remedies**, in order of cost: evaluate every individual at the **same initial position**; design the
fitness so that position-dependent variation cannot swamp real differences; use higher or fixed-point precision where
appropriate.

**Their honesty is worth copying.** They note that rounding chaos is "not necessarily a disadvantage" — ALife is often
criticised for being too orderly, and chaos adds perturbation. The problem is not that the noise exists; it is that it
leaks into the fitness signal.

---

## The elephant, now in focus

Three ideas carry the weight, and none of them is "artifacts are bad".

**1. Numerical dependence is not automatically an artifact.** A phenomenon can be a genuine property of the discrete
model and have no continuum counterpart. Davis's vocabulary — **non-Platonic** — is the right one: the claim must say
which object it is about.

**2. Refinement is a test of the claim, not a purification.** If a pattern vanishes at finer resolution, that does not
prove it was "wrong"; it proves the claim "this exists in the continuum limit" is false, while "this exists at this
`dt`" may remain true. The failure mode the field actually names is **over-claiming the limit**, not running a coarse
scheme.

**3. A fix does not guarantee robustness.** Davis 2024 is a counterexample to the fix of 2023. Every mechanism suspected
of producing non-Platonic behaviour has to be tested pattern by pattern, and after the fix as well as before it.

## What this does to our `X56`

`X56` is running (step convergence of the headline contrast). Before reading these papers I would have written the
interpretation as: "if the contrast does not survive, it was an artifact." **That formulation is wrong**, and it is wrong
in the direction that would make us throw away a real result.

The correct decision rule, adopted now:

| outcome at `dt = 0.5` and `2.0` | what we write |
|---|---|
| contrast keeps sign and magnitude | "the contrast is step-robust at the tested range, and no continuum claim is made" |
| contrast changes magnitude but keeps sign | "the effect is a property of the discrete scheme; we report the range of `dt` in which it holds" |
| contrast vanishes or reverses | "the contrast is **non-Platonic**: it exists at `dt = 1.0` with this Laplacian and does not survive refinement. We report it as a property of this scheme, not of the equations" |

Note that **all three outcomes are publishable**, and none of them is "we were wrong". What would have been wrong is
claiming the continuum version without testing it — which is exactly what we had been doing, because we never varied
`dt`.

## What we still have not read

Fourteen of the twenty titles in the last harvest remain unread: Huberman & Glance (1993) and Nowak et al. (1994) on the
update-rule dispute; Darius & Rojas (1994) on simulated molecular evolution; Woolley (2022) on boundary conditions;
Theiler et al. (1992) on surrogate data; Rechtsteiner & Bedau (1999) on neutral models; Axtell et al. (1996) on docking;
Wilson et al. (2014) and Sandve et al. (2013) on computing practice; Davis (2023) on Gray–Scott spatial resolution,
which is the one I most want next, because it treats **our** model.

They are queued (`X55`), not claimed as read.

## Sources

Full texts in `_hourly/fulltexts/*.txt` (extracted with `pypdf`), PDFs alongside. Citations verified through Crossref:
`10.1162/isal_a_00526`, `10.1162/isal_a_00786`, `10.1162/isal_a_00638`, `10.1007/s10015-012-0038-0`.
