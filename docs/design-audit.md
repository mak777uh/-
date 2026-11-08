# Design audit: every remark from the four reviews, checked against the code

**What this is.** Four independent analyses of the bench were received on 08.11. They disagree, and three of
the four did not open the repository. This document takes **every remark**, checks it against the code or the
data, records the verdict, and puts a **change plan** beside it. Remarks that cannot be settled by reading
code are moved to `docs/open-questions.md`, which is written for a literature search.

**Status of each verdict:** `CONFIRMED` (the code does what the remark says), `WRONG` (it does not),
`FIXED` (was true, fixed on 08.11), `OPEN` (cannot be settled here), `N/A` (not applicable to this
repository).

---

## Part 0. What the four reviews are, and how much to trust each

| # | review | opened the code? | verdict it gives | how it is used here |
|---|---|---|---|---|
| 1 | "first-principles analysis of the bench" | **no** (it says so in its own second answer) | 9/10, "a reference" | used only for the list of claims to check; its praise is not evidence |
| 2 | "concept analysis from the declared architecture" | **no** (it says so explicitly) | holds with reservations | its methodological remarks are the strongest of the four; several are already in manifesto 037 |
| 3 | "independent technical analysis" | **yes**, with line references | would stop expansion and run a model-integrity cycle | **the most valuable**; every claim was checked below |
| 4 | "field analysis" | **partly** | concrete numerical risks | its stability arithmetic is checked below and holds |

**The lesson of the comparison itself:** the review that opened the code found four defects; the review that
did not open it found none and gave 9/10. **A review that does not read the code cannot find a defect in it.**
That is worth recording for the future: the bench's own gate for "a review is done" should require that the
reviewer names the file and line of every claim.

---

## Part 1. The world (`morphogenesis/world/`)

### R1. Budding created energy when the spore had more than two cells

**Remark (review 3).** The parent pays `budding_cost` once, but each spore cell receives `pay * 0.5`, so three
or four cells create energy from nothing; and `mobility_spent` is subtracted from every cell instead of being
shared.

**Check.** Measured directly (`_budget_check.py`, then `tests/test_model_integrity.py`):

| `spore_cells` | energy created |
|---|---|
| 1 | −4.00 |
| 2 | 0.00 |
| 3 | **+4.00** |
| 4 | **+8.00** |

**Verdict: CONFIRMED, then FIXED.** The spore now receives exactly what the parent paid, shared among its
cells, minus mobility.

**Change plan.** Done. Guard: `test_budding_conserves_energy_for_every_spore_size` and
`test_budding_energy_per_cell_is_the_share`.

---

### R2. A second, hidden tap: `max(pay * 0.5, 1.0)`

**Remark.** Not in any review; found while fixing R1.

**Check.** With `budding_cost = 0.2` and `spore_cells = 1` the parent paid 0.2 and the spore received
`max(0.1, 1.0) = 1.0`. The world printed 0.8 per budding event, and three mobility tests pinned that floor as
normal.

**Verdict: CONFIRMED, then FIXED.** The floor is gone; the mobility budget is `budding_cost / spore_cells`.

**Change plan.** Done. Guard: the three rewritten mobility tests derive the budget instead of hard-coding it.

---

### R3. A step was unaffordable at exactly its price

**Remark.** Not in any review; found while fixing R2.

**Check.** `if budget <= cost: break` — a spore whose budget equalled the price took no step. Invisible while
the budget was floored at 1.0.

**Verdict: CONFIRMED, then FIXED.** The condition is now `budget < cost`.

**Change plan.** Done. Guard: `test_expensive_mobility_limited_by_budget`.

---

### R4. Age killed although the docstring says it is diagnostic only

**Remark (review 3).**

**Check.** The module docstring: "Возраст — только диагностика, не причина смерти". The code:
`dies = alive & (... | (s.age > cfg.max_age))`. A test, `test_old_cell_dies_of_age`, asserted the death.

**Verdict: CONFIRMED, then FIXED.** Age no longer kills. The test is now
`test_old_cell_does_not_die_of_age`.

**Change plan.** Done. **A lesson worth keeping:** code, prose and test agreed on the wrong answer. A test can
guard a defect.

---

### R5. `repair_cost` was a maintenance cost wearing a repair's name

**Remark (review 3).**

**Check.** `spent = cfg.update_cost + cfg.repair_cost`, charged to every living cell every step, before the
repair roll.

**Verdict: CONFIRMED, then FIXED.** `update_cost` is charged always; `repair_cost` only when a repair happens.

**Change plan.** Done. The old test asserted a direction that was an artefact of the bug; it now pins the
**window**: no repair → dies of damage (1314 steps), a reasonable price → lives (4000, the horizon), an
unaffordable price → dies faster than with none (343).

**Still open (see Q7):** whether "maintenance" and "repair" should be two named parameters in the config
rather than one renamed. The current fix keeps the name `repair_cost` and changes its meaning; a rename is a
breaking change for every stored config.

---

### R6. Genome inheritance at growth is not defined

**Remark (review 3).** A cell grown by the rule gets the genome that was pre-assigned to its position; the
parent's genome is not copied. So growth is *activation of a pre-existing field*, not inheritance.

**Check.** `self.genome = torch.randn((1, k, n, n)) * 0.1` is created for **every** grid position, empty or
not. `_sync_state_to_world` gives a new cell energy, age and damage, and inherits the **type** A/B, but not
the genome. `Pond.bud` does copy and mutate the genome.

**Verdict: CONFIRMED.** Two inheritance models in one world, and the difference was not written down.

**Change plan.**
- Done: the two paths are documented in `_sync_state_to_world`, and every artifact now records
  `grown_genome = "field"`.
- **Open (Q4):** should growth inherit from the parent? That is a change of world, not a bug fix, and it needs
  a series with an anchor.

---

### R7. The unit of reproduction and the unit of selection do not coincide

**Remark (review 3).** With `budding_unit = "colony"` the parent is the whole connected component, and the
child's genome is the **mean** of the component's genomes. Two lineages that touch become one parent with a
synthetic genome.

**Check.** `find_buds` returns connected components; `run_pond` averages `self.genome[0][:, p_idx]` over the
component.

**Verdict: CONFIRMED.**

**Change plan.**
- Add `budding_unit` to the artifact (done: it was already in the curated block).
- **Open (Q3):** which units should exist, and what "group genome" means. The review proposes four modes
  (cell-clonal, lineage-clonal, colony-mean, colony-heritable). Choosing among them is a design decision for
  the owner.

---

### R8. `splits` counts the rise in component count, not division events

**Remark (reviews 3 and 4).**

**Check.** `if prev_n is not None and n > prev_n: splits += n - prev_n`.

**Verdict: CONFIRMED.** A split plus a merge in one sampling interval counts as zero; one split into three
counts as two.

**Change plan.**
- Rename the field to `component_count_delta` (honest name) **and** add real event tracking:
  `split_events`, `merge_events`, `birth_events`, `death_events`, by matching components between consecutive
  snapshots on spatial overlap.
- **Cost:** a new observer in `field_track.py`; must be inert when off (anchor bit-for-bit).
- **Open (Q8):** what overlap threshold defines "the same component", and whether a merge should be an event
  of its own or a death plus a birth.

---

### R9. Boundary conditions are a hidden part of the world's ontology

**Remark (review 3).**

**Check.** `field_lab.py` uses `torch.roll` (periodic) and `% h` in the component walk. `pond.py` pads with
zeros (`torch.zeros((n + 2, n + 2))`) and checks `0 <= ny < h` (absorbing). Neither is in the config.

**Verdict: CONFIRMED.**

**Change plan.** Add `boundary: "periodic" | "reflective" | "absorbing"` to both configs, default to the
current behaviour, record it in the artifact, and add a test that the two worlds report different values.
**Open (Q9):** whether the two worlds should be allowed to differ at all if results are to be compared.

---

### R10. `config_block` saved 37 of 133 fields

**Remark (review 3).**

**Check.** Measured: 37 keys for 133 fields; the missing ones included `grid`, `budding_cost`,
`budding_mass`, `damage_rate`, `income_mode`.

**Verdict: CONFIRMED, then FIXED.** 138 keys for 133 fields, JSON-serialisable.

**Change plan.** Done. Guard: `scripts/check_config_completeness.py`, with
`scripts/config_gate_selftest.py` proving it can fail.

---

### R11. `git_dirty` is not enough to reconstruct a run

**Remark (review 3).** A run on a modified `pond.py` records `dirty=true` but not which files or their
hashes.

**Check.** The manifest records `git_dirty` as a boolean.

**Verdict: CONFIRMED.**

**Change plan.** Record `dirty_files: [{path, sha256}]` in the manifest when the tree is dirty. **Open (Q10):**
whether to record the full diff (larger, complete) or the hashes (smaller, verifiable).

---

### R12. `PondConfig` has 133 fields mixing fourteen subsystems

**Remark (review 3).**

**Check.** 133 dataclass fields, spanning resource ecology, energetics, reproduction, inheritance, mutation,
migration, learning, signalling, memory, membranes, frequency dependence, invasion, population caps and
external forcing.

**Verdict: CONFIRMED.**

**Change plan.** Split into a **core world** (state, local resource, energy, damage, death, base update) and
**optional mechanisms** (reproduction, inheritance, mutation, mobility, signalling, adaptation, niche
construction), with an **experiment profile** that names the combination. This is the largest change in the
plan; see Part 5.

---

## Part 2. The field line (`scripts/field_lab.py`, `field_track.py`)

### R13. `Dw = 0.32` at `dt = 1` is numerically unstable

**Remark (review 4).** For the explicit scheme with the 4-neighbour Laplacian, the high-frequency
amplification factor is `1 - 8*D*dt`, and stability requires `D*dt <= 0.25`.

**Check.**

| coefficient | `D*dt` | amplification | verdict |
|---|---|---|---|
| `Du = 0.16` | 0.160 | −0.280 | stable |
| `Dv = 0.08` | 0.080 | +0.360 | stable |
| **`Dw = 0.32`** | **0.320** | **−1.560** | **UNSTABLE** |

**Verdict: CONFIRMED.** The optional third field (`--second-species`) runs an unstable diffusion at the
default `dt`.

**Change plan.** Either lower the default `Dw` to ≤ 0.25, or lower `dt` when the third field is on, or use an
implicit scheme. **Open (Q5):** which of the three, because each changes what the third field means.

---

### R14. `clamp` may be doing the integrator's job

**Remark (review 4).** `u = clamp(u + dt*du, 0, 1)` can hold a trajectory in range while the numerical
correction becomes part of the mechanism.

**Check.** The clamp is in the loop; the amount clipped is not recorded.

**Verdict: CONFIRMED as a risk, not measured.**

**Change plan.** Record the clipped mass per step (`clipped_total`) and fail a run whose clipped mass exceeds
a threshold. **Open (Q6):** what the threshold should be.

---

### R15. The initial blob is not periodic although the dynamics are

**Remark (review 4).** The seed disc is built with Euclidean distance, so near the edge it is cut rather than
wrapped: radius 2 gives 13 nodes inside the field but 6 at a corner.

**Check.** The seed mask uses `((xx - c)**2 + (yy - c)**2) <= r0*r0` with no wrap; the Laplacian uses
`torch.roll`.

**Verdict: CONFIRMED.**

**Change plan.** Either wrap the seed distance, or record the initial mass as a factor. **Open (Q11):** which,
because a wrapped seed changes the initial condition of every past run.

---

### R16. `field_inherit` computes `F_eff` from `s_ref` but the artifact text says `s̄`

**Remark (review 3).**

**Check.** The code uses `args.s_ref`; the description written into the result JSON states
`F_eff = F(1 + eps(s − s̄))`.

**Verdict: CONFIRMED.**

**Change plan.** Generate the model description from the parameters rather than writing it twice. **Open
(Q12):** whether the artifact text should be generated, or the model changed to use the mean.

---

## Part 3. The bench itself (`lab/`, `scripts/`)

### R17. The reviewer role does not require reading the code

**Remark.** Not in any review; found by comparing them.

**Check.** The four reviews: two did not open the repository, and one of those gave 9/10.

**Verdict: CONFIRMED.**

**Change plan.** `lab/reviews/README.md` gains a rule: every finding must name a file and a line. A review
whose findings name no file is recorded as "concept-level" and cannot close a defect.

---

### R18. Series taken before 08.11 are not comparable with series taken after

**Remark.** Consequence of R1–R5.

**Check.** The world's energy budget, death rule and repair cost all changed.

**Verdict: CONFIRMED.**

**Change plan.** A `world_version` field in the manifest, bumped to `2` for the current world, and a rule in
`docs/eliminations.md` that series of version 1 are not pooled with series of version 2.

---

### R19. The librarian works only when asked

**Remark.** The owner asked for this to be improved.

**Check.** `lab/notices.md` carries requests; the librarian answers when a message arrives. Nothing triggers
a search automatically.

**Verdict: CONFIRMED.**

**Change plan.** A trigger file `lab/lit-queue.json` already exists; the missing part is **automatic
enqueueing**: when a gate fails, when a manifest is written with `sensitivity: unknown`, or when a report
contains the phrase "we do not know", an entry is added with `question`, `why`, `target`, `deliverable`.
**Open (Q13):** which events should enqueue, and how to avoid a queue that fills with noise.

---

### R20. The bench has no single command that answers "is the world still the world I think it is?"

**Remark.** Not in any review; a gap found while fixing R1–R5.

**Check.** The gates check the repository (links, indices, manifests, policy). None checks the **world's
invariants** as a set.

**Verdict: CONFIRMED.**

**Change plan.** `scripts/world_invariants.py`: energy conservation across every event type, no death by
age, repair charged only on repair, config completeness, and the numerical stability of every diffusion
coefficient. This is the gate the four defects would have tripped.

---

## Part 4. What the reviews got wrong or overstated

| remark | review | verdict |
|---|---|---|
| "9/10, a reference, revolutionary" | 1 | **WRONG as an assessment**: the same review did not open the code, and four defects were live |
| "the bench publishes no conclusions, only the conditions" | 2 | **PARTLY WRONG**: the bench publishes conclusions (articles 001–037) and marks their type; what it does not do is claim more than the type allows |
| "the frozen rule is hidden" | 1 | **WRONG**: `train_rule.py` and `docs/spec/` describe it; the README links them |
| "612 tests" | 1 | **WRONG number**: the suite is 83 test files; 612 was the count of test functions in an older snapshot |
| "the seeds gave one world copied five times" | 1 | **CONFIRMED for that series**, and already fixed with `--init-jitter` |
| "no meta-analysis" | 1 | **CONFIRMED**: there is no aggregator across experiments; see R21 |

### R21. No meta-analysis across experiments

**Remark (review 1).**

**Check.** `reports/` has 583 files and `docs/world-design.md` 242 sections; there is no script that asks "in
what fraction of series did mechanism X help?".

**Verdict: CONFIRMED.**

**Change plan.** After the corpus audit's finding (300 of 320 artifacts record the cell's own measures), a
`scripts/meta_analysis.py` that groups artifacts by mechanism and reports, per mechanism, the paired
difference in the cell's own measures. **Open (Q14):** what counts as "the same mechanism" across series.

---

## Part 5. The change plan, in order

| # | change | why | size | risk |
|---|---|---|---|---|
| 1 | **`scripts/world_invariants.py`** — one gate for the world's invariants | the four defects would have tripped it | small | none |
| 2 | **`world_version` in the manifest** + a rule that versions are not pooled | series before and after 08.11 are not comparable | small | none |
| 3 | **`dirty_files` with hashes** in the manifest | a dirty run is not reconstructible | small | none |
| 4 | **boundary condition in the config** | it is a hidden part of the ontology | small | low |
| 5 | **rename `splits`** and add real split/merge events | the counter measures the wrong thing | medium | low |
| 6 | **fix `Dw`** (or `dt`) and record clipped mass | an unstable default in an optional branch | medium | medium |
| 7 | **generated model text** for `field_inherit` | code and description disagree | small | none |
| 8 | **review rule: name a file and a line** | two of four reviews could not find a defect | tiny | none |
| 9 | **automatic literature enqueueing** | the librarian works only when asked | medium | low |
| 10 | **`meta_analysis.py`** | no aggregator exists | medium | low |
| 11 | **split `PondConfig` into core + mechanisms + profile** | 133 fields mixing fourteen subsystems | **large** | **high** |
| 12 | **decide the two inheritance paths** (Q4) | growth is activation, budding is inheritance | **large** | **high** |
| 13 | **decide the unit of reproduction** (Q3) | colony-mean genomes are not clonal | **large** | **high** |

**Order.** 1–8 are safe and can be done now. 9–10 are safe and need a design decision each. 11–13 change the
world and need the owner's decision, a series with an anchor, and a version bump.

---

## Part 6. What this audit does not establish

1. **It checks the code, not the science.** A world with correct energy accounting can still be an
   uninteresting world.
2. **The numerical claims are analytic**, not measured: the amplification factor is computed from the scheme,
   and no run was made at `Dw = 0.32` to watch it diverge.
3. **The reviews' claims about the literature are not checked here**; they are in `docs/open-questions.md`.
4. **The four defects that were fixed change every number the bench has produced.** Nothing in this document
   says what the new numbers are.

---

## Part 7. What the literature said, and what it changes

Ten of the fourteen open questions were answered by search on 08.11 (the answers are in
`docs/open-questions.md`). Four are owner decisions and remain open. **Three of the answers change something
this audit already did**, and one of them says a claim in manifesto 037 is false.

### A1. Q2 — P3 of manifesto 037 is false in general, and must be restated

**What the search found.** Three independent passes agree: a within-unit variance decomposition is **not**
automatically immune to between-unit manipulation. The counterexample is decisive. Let the behaviour be
`y = (1 + B_i)·S + R`, with `S` the situation, `R` the record, and a bonus `B_i` that is constant **inside**
the unit but changes the **sensitivity** to the situation. The share explained by the situation is
`(1+B_i)²/[(1+B_i)²+1]`: 1/2 at `B_i = 0`, 4/5 at `B_i = 1`. Centring removes nothing, because the bonus
multiplies rather than shifts.

**What survives.** An **additive** manipulation, constant inside the unit, leaves the centred deviations
unchanged. That is exactly the case the rewritten `k_readouts.py` tests, and it holds (a bonus moves the
measure by 0.0000). It is one case out of six.

**What changes.**
- **Manifesto 037, P3:** "the measure cannot be moved by a bonus" becomes "the measure is invariant to
  additive within-unit shifts and is **not** invariant to manipulations that change the within-unit variance,
  the responsiveness, or the measurement noise". The claim narrows; it does not disappear.
- **`scripts/k_readouts.py --self-test`:** must cover six cases, not one — additive bonus, multiplicative
  bonus, situation-dependent bonus, between-unit-only change, within-unit-only change, and a change of
  measurement noise. Only the first is currently tested.
- **This is the second time P3 has been refuted.** The first was the implementation (a between-cell bonus
  moved the measure by 0.31); this is the claim itself. Both are now recorded.

### A2. Q3 — `budding_unit = "colony"` is blending inheritance and must not be called clonal

**What the search found.** The criterion for a collective to be a unit of selection is heritable variation in
fitness **at its own level**, and Godfrey-Smith locates it on three axes: bottleneck size (B), germ–soma
specialisation (G), integration (I). A colony whose genome is the **mean** of its members' genomes has **no
bottleneck and no lineage**: two lineages that touch produce a synthetic genome that is the clone of neither
parent.

**What changes.**
- **The mode must be renamed.** The word "clonal" cannot apply to it. Candidate names: `colony-mean` (what it
  computes) or `blending` (what it is).
- **Every reproduction mode must record the three axes** (B, G, I) in the artifact, so a reader can see at once
  whether a mode is a Darwinian unit.
- **A group genome, if wanted, needs its own transmission operator defined** — the mean vector is a
  **phenotype**, not a genome.

### A3. Q5 — lowering `Dw` changed the model, and that must be declared

**What the search found.** All four passes give the same stability condition, `D·dt/h² ≤ 1/4`, and all four
add the same caveat: **the right fix depends on what the field means**. If `Dw` is a physical diffusion
coefficient, the fix is to lower `dt` (or use an implicit scheme) and **keep `Dw`**; lowering `Dw` changes the
speed at which the field spreads. If `Dw` is a free modelling parameter, lowering it is legitimate but is a
**change of model**.

**What changes.**
- The correction to 0.24 is an **interim** fix and is now labelled as one.
- **The model parameter and the integrator parameter must be separated** in the config: `Dw` (what the field
  diffuses at) and `dt` (how finely we integrate). A stability gate then checks the combination, not a
  hard-coded number.
- **`world_invariants.py` W5** already checks the combination; it should check it for **whatever** `Dw` and
  `dt` the config carries, not for the two literals it has now.

### A4. Q6, Q8, Q9, Q11, Q14 — what is already done and what is still owed

| question | what the search settled | what is done | what is still owed |
|---|---|---|---|
| **Q6** clipping | no acceptable fraction exists; the criterion is whether the correction vanishes under refinement | nothing | record `clipped_mass` and `clip_fraction` per step |
| **Q8** component matching | 0.5 is not canonical; the choice has measurable consequences | the counter now uses a **relative** threshold | a sensitivity sweep over 0.2 / 0.3 / 0.5 |
| **Q9** boundaries | a boundary is part of the model unless the domain is the large-system limit | `boundary` is in the config and the artifact | show that a difference between worlds is not explained by the boundary alone |
| **Q11** initial condition | in a periodic world the seed must use the minimum-image distance | nothing | build the seed with toroidal distance, or record the initial mass as a factor |
| **Q14** mechanism identity | a mechanism is individuated by its phenomenon and causal organisation, not by a parameter name | the meta-analysis groups by config field (a first approximation) | group by mutual manipulability, and record `same` / `related` / `unresolved` |

### A5. Q4 — activation and reproduction are distinguished in the literature, and we now record which one ran

Avida separates `Inject`, `h-alloc`, `h-copy` and `h-divide`: copying and division are different operations and
injection is not a parent. Growing NCA uses one rule for all cells, so a new active cell is not a genetic
offspring at all. **Our `grown_genome = "field"` is the right record**, and the next step is a per-cell
`birth_mode` (`activation` / `reproduction` / `injection`) with the inheritance analysis stratified by it.

### A6. The four questions that remain open

Q7 (maintenance versus repair naming), Q10 (diff or hashes), Q12 (generated text or changed model) and Q13
(automatic triggers) are **owner decisions**; no search can settle them. They are marked as such in
`docs/open-questions.md` and in Part 5 of this audit.

