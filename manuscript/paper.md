# What Morphologies Does a Neural Cellular Automaton Hold? A Census and a Negative Result

**Status:** DRAFT v0.4 (2026-10-21) — not submitted, not peer-reviewed, do not cite. **Publication gate:** E02c is closed, the seed42 run repeats bitwise and returns the class 64/64 (§4.6), and the portable package passed an independent CPU reproduction of the E02b census; none of these is an independent reproduction of the E02c series, and external submission remains a decision of the owner. No claim about life, consciousness or intelligence; only observable behavioural classes and their boundaries ([AGENTS.md](../AGENTS.md) §3).

<!-- TODO: freeze a submission tag and run the independent-reproduction pass before any external submission. -->

## Abstract

Neural cellular automata are usually trained to grow a prescribed pattern. What morphologies does such a system hold when the target is removed? We census twelve frozen checkpoints (five H-A0, five R-9, one R-11, one H-P1) plus an untrained control: 64 deterministic noise starts per model, 2000 steps, frozen weights, 18 descriptors and Ward clustering at k = 5. Of 704 learned rollouts, 573 (81.4%) end in death or in a uniform field; two structured classes remain. `struct_1` is reproduced by the untrained architecture, so its repair does not require learning. `struct_2` appears only in R-9 seed42, is absent from all controls and from 768 rollouts of other models, and returns to its class after 20% amputation. An earlier ring target had failed: the ring was neither reached from noise nor held. A pre-registered replication then trained R-9 on three new seeds (142/242/342) and repeated the 64-start census: **none** produced `struct_2` (seed142 → `struct_1`, seed242/342 → `uniform_dark`), while the seed42 control reproduced it 64/64. A repeat of the seed42 run with frozen code reproduced all seven weight tensors bitwise and the class 64/64, so the run behind the observation is stable and the candidate is tied to its training seed rather than to the recipe. It is therefore a single-seed case study on the 2000-step horizon. We describe the map as sparse, the repair as class-level rather than bitwise, and make no claim that either class is alive.

## 1. Introduction

Can a local learnable rule hold more than the one pattern it was optimised for? The first target was explicit: a ring, trained as a coverage objective and probed for reach and hold. E02 closed negatively — the ring was not an attractor of the learned dynamics ([E02 report](../reports/2026-10-20-e02-pattern.md), [article 002](../articles/002-pochemu-kolco-ne-stalo-attraktorom.md)). That failure motivated a different question: not whether one prescribed form can be grown, but **which morphologies the existing frozen checkpoints already hold when asked nothing specific**.

E02b answered by census rather than training: it froze every canonical checkpoint, started each model from 64 deterministic noise states, ran 2000 steps without gradient, described each final state with 18 descriptors and clustered the results ([E02b results](../reports/2026-10-20-e02b-results.md)). This manuscript assembles that census, the E02 negative result, and the exploratory follow-up probes into one cumulative text.

The contribution is deliberately narrow: a sparse census of what twelve frozen checkpoints hold; a description of repair as recovery of a **class** of texture, not of a bitwise pattern; a pre-registered replication showing that the only learned candidate does **not** survive a change of training seed, while the same seed repeats bitwise on the same hardware; and an explicit account of what the measurements cannot show. The scope is equally narrow: one architecture, one recipe family, one training seed for the only learned candidate, and no claim about adaptation, goals, information or agency.

## 2. Related work

The conceptual frame is the literature on morphogenesis as computation and on "agential materials" — a tissue can solve a shape problem rather than execute a fixed plan (Levin; reading map in [`library/levin/README.md`](../library/levin/README.md)). This frame motivates the question but is not a result: our data can say that a class of texture returns after amputation; they cannot say that the tissue "remembers a plan".

The technical lineage is the neural cellular automaton: a differentiable local rule trained to grow and regenerate a target (Mordvintsev et al., 2020, and the works in [`library/hypotheses/nca-lineage.md`](../library/hypotheses/nca-lineage.md)). Our contribution is not a new architecture but a pre-registered census of what trained rules hold, including the negative ring result that preceded it. No source is restated or reprinted; records and our notes are in the library ([index](../library/publications/README.md), [Levin map](../library/levin/README.md), [NCA lineage](../library/hypotheses/nca-lineage.md)).

The records behind these citations are fixed in the library index, whose metadata were verified against Crossref/arXiv (index date 2026-10-21), and we take method and caution from them, never evidence about our own model. The computational line is the differentiable local rule trained against a target (Mordvintsev et al., 2020), its 3D extension that grows volumetric artefacts and functional machines (Sudhakaran et al., 2021), and the continuous-state precursor whose catalogue of localised patterns is a descriptive vocabulary rather than a claim about organisms (Chan, 2019). Three works bound what a shape can be asked to do: a form that classifies itself through local agreement (Randazzo et al., 2020), a soft-robot body whose shape is regrown while locomotion recovers only partially (Horibe et al., 2021), and physical NCA modules that classify global shape and detect damage without a centre (Moreno et al., 2026). Two set expectations for a map like ours: whether local interactions can hold an ordered phase at all is fixed by the interaction graph rather than by rule details (Sacco et al., 2026), and the corpus review lists collapse into trivial attractors and limited capacity as standing limitations of the method (Hartl, Levin & Pio-Lopez, 2026) — our sparse map is consistent with that list but is not a test of it. Two further works supply vocabulary we use only operationally: autotelic reinforcement learning that finds and holds structures with small interventions (Cvjetko et al., 2026) and a computable measure of goal-directedness (MacDermott et al., 2024). The frame itself (Levin, 2022, 2023) motivates the question and is not a result here: our data can say that a class of texture returns after amputation; they cannot say that anything pursues a goal. Full bibliographic records, with DOI or publisher URL as held in the index, are in the References.

## 3. Methods

### 3.1. Model and checkpoints

The automaton is a 64×64 grid with 16 channels: channel 0 visible, channel 1 alive mask, channel 15 stress ([E02 report](../reports/2026-10-20-e02-pattern.md)). We use the twelve canonical `nca_final.pt` checkpoints of E02b — H-A0 ×5 (seeds 42/101/202/303/404), R-9 ×5, R-11 ×1, H-P1 ×1 (positive control whose training pool starts from the target) — plus an untrained model of the same architecture as a runtime control without weights.

Provenance was audited before any class was read: byte hashes match the index, seeds and metadata match their families, iteration is 2000 for all, SHA-256 over `model_state_dict` is pairwise distinct 12/12, and four H-A0 files share a final loss to the last bit while having distinct weights — the same loss on a dead field, not duplicate files ([E02b results](../reports/2026-10-20-e02b-results.md), "Происхождение канонических чекпоинтов").

### 3.2. Training recipes

All checkpoints were trained for 2000 steps against a ring with density p = 0.15234375 and signature b0 = 1, b1 = 1, chi = 0. H-A0 is the baseline; R-9 adds a quiet-background term of weight 1.0 on top of R-8; R-11 adds the same term on top of R-7 without the strengthened alive-policy; H-P1 is the positive control whose pool starts from the target ([E02 report](../reports/2026-10-20-e02-pattern.md), [WP4 status](../reports/2026-10-20-wp4-status.md), [negative-results log](../morphogenesis/memory/negative_results.md)). The arms differ in loss composition, not architecture — which is why the census can compare five R-9 seeds that share a recipe but differ in training seed.

#### Loss composition of the R-9 arm

The arm definition is frozen in code and mirrored in the data, so the values below are read, not recalled. `ARMS["R-9"]` in [`morphogenesis/wp4_ablations.py`](../morphogenesis/wp4_ablations.py) sets, on top of the defaults: `RETENTION_ENABLED = true`, a retention rollout of 16 steps (`RETENTION_ROLLOUT_STEPS = 16`), survival mode `level` with alive margin 0.1 (`RETENTION_SURVIVAL_MODE = "level"`, `RETENTION_ALIVE_MARGIN = 0.1`), survival weight 10.0 (`RETENTION_SURVIVAL_WEIGHT = 10.0`), quiet weight 1.0 (`RETENTION_QUIET_WEIGHT = 1.0`), loss weights `{"retention": 1.0, "alive_policy": 2.0}`, and a flat BPTT curriculum `TRAIN_BPTT_CURRICULUM = [16, 16, 16]`. The same values are written into [`census.json`](../morphogenesis/experiments/E02b_morphospace/census.json) → `checkpoints[]` → `overrides` with `overrides_source: "wp4_ablations.json"`, which makes the arm auditable without the training log.

| Term | Weight in R-9 | Source |
| --- | ---: | --- |
| `retention` | 1.0 (default 0.0) | `ARMS["R-9"]` → `LOSS_WEIGHTS` |
| `alive_policy` | 2.0 (default 0.5) | `ARMS["R-9"]` → `LOSS_WEIGHTS` |
| `visible_mse` | 1.0 | `config.LOSS_WEIGHTS` |
| `hidden_regularization` | 0.05 | `config.LOSS_WEIGHTS` |
| `stress_proxy` | 0.1 | `config.LOSS_WEIGHTS` |
| `topo_proxy` | 0.1 | `config.LOSS_WEIGHTS` |
| `attractor_divergence` | 0.2 | `config.LOSS_WEIGHTS`, phase 3 only |

The retention term is `1.0 × (retention_mse + 10.0 × retention_survival + 1.0 × retention_quiet)` ([`morphogenesis/train.py`](../morphogenesis/train.py)); the other terms enter as `weight × term`. Batch size is 8 (`TRAIN_BATCH_SIZE`, and `batch_size` in the training manifest `lab/runs/20261019T201445Z-WP4_R-9_s2000_seed42.json`). `attractor_divergence` is added only in phase 3, i.e. after `PHASE1_STEPS = 10000` (`train.py` → `resolve_phase`), so a 2000-step run does not reach it.

Two limits are part of the statement. The arm record stores weights and modes, not the algebraic definition of each term: the shape of `retention_survival` and `retention_quiet` is defined by `train.py` (`retention_rollout_loss`), not by `wp4_ablations.json`. And R-11 differs in composition — the same quiet term without the strengthened alive policy — which is why the arms are described here by composition rather than called identical.

### 3.3. Census protocol

For every checkpoint we ran 64 deterministic initial states (seeds 0–63) from `init_state` for 2000 steps with frozen weights and no gradient, snapshotting every 50 steps. With 13 families (12 checkpoints plus untrained) this gives 832 rollouts, 704 learned and 128 control. The protocol ran on CUDA in 5070.2 s; families took 365.4–423.9 s. All 64 seeds enter the denominator ([E02b results](../reports/2026-10-20-e02b-results.md)).

Controls are projected onto learned centroids and do not participate in fitting. Class semantics are fixed: `death` when alive_fraction < 0.01, `uniform_dark` when binary_fraction < 0.01, `uniform_bright` when binary_fraction > 0.95, else `structured`.

### 3.4. Descriptors and clustering

Each final state gets 18 features: alive fraction, binary and bright density, mean soft intensity, entropy, components and holes (b0, b1), Euler characteristic, bounding-box fill, largest-component fraction, radial profile and variance, rotational and reflection symmetry, autocorrelations (lags 1, 4; 2 and 8 in follow-ups) and edge fraction ([E02b results](../reports/2026-10-20-e02b-results.md)). Features are z-normalised; Ward clustering builds classes with k chosen by silhouette and minimum class size 5; DBSCAN is an agreement check, not the source of classes. The solution is k = 5, silhouette 0.8545; DBSCAN gives 7 clusters, 4/704 noise (0.57%), ARI 0.9137. The taxonomy is descriptive: bootstrap over k selects k = 5 in 52%, while `struct_2` survives intact for k = 3–8.

### 3.5. Perturbations

For each structural class three prototypes were chosen by distance to the centroid. Three prototypes per class × six perturbations × five repeats gave 180 rollouts: 10% and 20% amputation, noise σ = 0.1, a cut of half the field, a patch transplant into a dead field, and a dead-field control. Runs lasted 500 steps with snapshots every 25; recovery means the final state is assigned to the prototype's class again ([E02b results](../reports/2026-10-20-e02b-results.md), "Возмущения"). Two deviations are recorded, not hidden: amputation zeroes all 16 channels (stronger than the literal protocol), and the protocol transplant was degenerate (bounding box = whole field), so the growth claim rests on exploratory patches (§4.3).

### 3.6. Determinism and compute

Runs follow the specification's determinism contract ([spec §9.2](../docs/spec/MORPHOGENESIS_v5.6_Rev11.md)): `CUBLAS_WORKSPACE_CONFIG` set before CUDA init, `torch.use_deterministic_algorithms(True)`, deterministic cuDNN with benchmark off, fixed seeds. Census used CUDA on an RTX 3070 Laptop; the canonical prototype path reproduces bit-identically within and across processes ([E02b results](../reports/2026-10-20-e02b-results.md)). A full 2000-step training run is also bitwise repeatable on this device: the seed42 repeat matched all seven weight tensors of the canonical checkpoint (§4.6, [seed42 repeat](../reports/2026-10-21-e02c-seed42-repro-results.md)). Cross-hardware determinism was not tested.

## 4. Results

### 4.1. The ring target was not an attractor

E02 asked whether a ring is reachable from noise and stable from the target; it is neither. The layer-1 gate (5 seeds × 800 steps) failed all four conditions — no collapse 0/5, Chamfer improvement 0/5, coverage above threshold 0/5, retention 0/5 — and every run was stopped by `collapse_fuse` with visible MSE 0.2498–0.2499, the dead-field plateau ([E02 report](../reports/2026-10-20-e02-pattern.md), [WP4 status](../reports/2026-10-20-wp4-status.md)). With the structural ceiling 2p/(1+p) = 0.2644 and the gate 0.3144, the best family-R f1 was 0.2419 at iteration 650 (R-9), 0.0225 below the ceiling and 0.0725 below the gate. Reach maxima were 0.2755–0.2793 at precision 0.15–0.17 ("almost everything bright", not a ring); the only holder, H-P1, decayed with horizon (0.9495 → 0.3959 → 0.2069). The WP4 artefact gate is formally unpassed (`journal_pairs_13_3 = false`): `met = true` means fields and runs exist, not that the science succeeded.

#### Why the ring is a calibration target, not a control for form in general

The ring was the training objective, not a control arm: every E02 arm was trained against the same ring, and the four layer-1 conditions tested reach and hold of that one target, not the capacity to hold any form ([E02 report](../reports/2026-10-20-e02-pattern.md), "Дизайн"). A control in the sense this manuscript uses needs an arm whose expected outcome is fixed independently of the treatment; E02 had none — the untrained architecture and the H-P1 positive control were added only in E02b (§3.1). The failure therefore bounds one optimisation: this architecture, this loss family, this horizon, this target. It does not bound the capacity to hold form, and the census makes the distinction concrete rather than academic: two structural classes appear in the frozen map, one of them from every start of a single checkpoint (§4.2). The E02 report states the same boundary in its own section ("Что НЕ следует из результата": it is not proved that an NCA cannot produce morphogenesis — one architecture, loss, horizon and target were tested). Reading the ring as a negative control for form in general would be the measurement trap of §5.3 applied to a single failure: a single maximum — or a single absence of one — taken as a verdict about a class.

### 4.2. A sparse map with two structural classes

Ward at k = 5 gives class sizes [67, 320, 189, 64, 64] over learned runs: `struct_1`, `death`, `uniform_dark`, `uniform_bright`, `struct_2` ([E02b results](../reports/2026-10-20-e02b-results.md)). Of 704 learned rollouts, 573 end in death or a uniform field — 81.4% (death_or_uniform_fraction = 0.8139) — and 131 (18.6%) are structural. The formal outcome is `rich_map`, but the map is sparse: four of five learned runs show no structure.

The two structural classes are not equivalent. **`struct_1`** (67 learned, 93 control rollouts) is a fine speckle: alive median 0.7959, binary median 0.2561, b0 ≈ 382, b1 ≈ 2; it is reproduced 64/64 by the untrained architecture and appears in 29/64 H-P1 rollouts, so it is an architectural confound, not evidence of learned morphology. **`struct_2`** (64 learned, 0 control) is a connected tissue with many holes: alive median 0.5310, binary median 0.5310, b0 ≈ 1, b1 ≈ 1844.5, entropy median 0.2535; R-9 seed42 produces it from all 64 noise starts, no control produces it, and it is absent even transiently from the 768 rollouts of other models.

**Classes at Ward k = 5** — learned/control counts and medians from [E02b results](../reports/2026-10-20-e02b-results.md), "Классы"; the 128 controls split 93 + 35 and are projected, not fitted:

| Class | Semantics | Learned | Control | alive (median) | binary (median) |
| --- | --- | ---: | ---: | ---: | ---: |
| `struct_1` | structured | 67 | 93 | 0.7959 | 0.2561 |
| `death` | death | 320 | 35 | 0.0000 | 0.0000 |
| `uniform_dark` | uniform_dark | 189 | 0 | 1.0000 | 0.0000 |
| `uniform_bright` | uniform_bright | 64 | 0 | 1.0000 | 1.0000 |
| `struct_2` | structured | 64 | 0 | 0.5310 | 0.5310 |

![PCA of the census morphospace: the 704 learned rollouts coloured by Ward class at k = 5, with the 128 control rollouts projected as open circles](../reports/figures/e02b_morphospace_pca.png)

**Figure 1.** PCA of the 18 descriptors, fitted on the 704 learned rollouts only; the first two components carry 72.0% of the variance (axes labelled 53.8% and 18.3%, each rounded independently on the figure), and all 832 rollouts are shown — 704 learned, denoted by colour, and 128 controls, drawn as open circles projected onto the learned axes and never used in fitting. Black crosses mark class centroids. `struct_2` (64 learned, 0 control) is an isolated island at the lower right; `death` and `uniform_dark` form a tight pair on the left, `struct_1` a compact group near the origin, and the controls spread along the band between them, sitting inside `struct_1` and `death` rather than forming a class of their own. The figure visualises the partition already obtained and is not an additional test ([map script](../morphogenesis/experiments/E02b_morphospace/scripts/e02b_morphospace_map.py); the figure file is 95 345 bytes).

H1 (a non-trivial reproducible class) and H2 (R-11's structure is transient: 61/64 finals non-structural, `struct_1` on some snapshot 64/64) were supported; H3 was refuted (§4.3); H4 — whether the rule variant matters more than the seed — was not run.

### 4.3. Repair at the level of a class, not a pattern

After 20% amputation of live cells (zeroing all 16 channels), both structural classes returned to their own class in 15/15 repeats, median return at the first snapshot (25 steps) ([E02b results](../reports/2026-10-20-e02b-results.md)). This refutes H3, which expected no recovery above 50%. For `struct_1` learning is not required: three seeded untrained initialisations give 64/64 `struct_1` and 45/45 returns after the same amputation.

Recovery is class-level, not bitwise. Patches of 8×8, 16×16 and 32×32 transplanted into a zero field (2 classes × 3 sizes × 5 positions = 30) all grew into their class within 500 steps, but the global pattern did not return: IoU with the prototype was 0.15–0.47, and `struct_1` agreement was at the random-field level. Small seeds organise more slowly (25 steps for 32×32, 225 for 8×8, 275 for 16×16 in `struct_2`), and convergence is not observed even at 2000 steps.

The transplant matrix says the same from the other side. A 12×12 matrix (144 transplants) found six killers (H-A0 ×5 and H-P1), five single-live-attractor models, one diagonally unstable model (R-11) and zero multi-basin candidates: no model holds two stable live forms. A repeat with nine samples per pair (1296 transplants) reproduced the verdicts; R-9 seed42 pulled all 54 foreign live states into `struct_2` with death share exactly 0.000. The reverse transplant is equally model-specific: `struct_2` into R-9 seed101 ends in death 16/16, while seeds 202 and 303 return to their own classes 16/16.

#### The 25-step return is an upper bound, not a measurement

The number 25 is the resolution of the measurement, not a measured latency. Perturbation runs last 500 steps with a snapshot every 25 (`run_perturbations(..., steps=500, every=25)` in [`morphogenesis/e02b_morphospace.py`](../morphogenesis/e02b_morphospace.py); the same interval is stated in the E02b design), so "return at the first snapshot" means that the first post-lesion snapshot already carries the class. Any return anywhere in the interval (0, 25] is recorded as 25: the true time is **at most** 25 steps and may be shorter. The E02b report records the same reading (limitation 6: "the median of 25 steps is the first snapshot, the real time may be less"). Nothing in the archive resolves sub-25-step timing; this manuscript therefore claims no faster or slower repair than the bound, and a denser snapshot grid would be needed to narrow it.

### 4.4. Exploratory probes: channels, strength, asymmetry, nucleation, transplants

The follow-up probes below were run after the census with rules written before each run; they do not change the pre-registered verdicts.

**Where the form lives (H-CH-1).** In 144 rollouts (3 models × 4 conditions × 12), `struct_2` reproduced the same pattern 12/12 intact, with visible texture zeroed, with hidden channels zeroed, and with hidden channels shuffled; median IoU 0.786–0.825 ([channel-memory report](../reports/2026-10-21-e02b-channel-memory.md)). "Form is held in hidden channels" is rejected in its strong form: `memory_in_hidden_channels = false`. The prototype was non-canonical (alive 2200/3240 vs canonical 2174/3263), so absolute IoU is not comparable with canonical runs; a clean provenance repeat is required before publication.

**Strength of the body (H-BI-1).** In 252 rollouts (3 models × 7 fractions × 12), `struct_2` survived 12/12 at every fraction from 0 to 0.9 and 0/12 at 1.0 — a threshold, not a dose-response ([body-integrity report](../reports/2026-10-21-e02b-body-integrity.md)). T is 0.90 for both learned models and 0.50 for the untrained network; the verdict is `mixed` because `struct_2` is not more tolerant than `struct_1`. What it adds is a connected body: median alive_b0 = 1 at T, against about 22 islands for `struct_1`.

**Asymmetry (H-AB-1).** On the canonical prototype, 216 rollouts (3 models × 6 lesions × 12) gave, for `struct_2`, cut_left 0.473 vs cut_right 0.792 (Δ = −0.336, sign 12/12) and cut_top 0.806 vs cut_bottom 0.659 (Δ = +0.184, sign 12/12). Both axes pass the pre-registered rule (sign in ≥11/12 and |Δ| ≥ 0.05); `struct_1` and untrained stay below 0.01. The class was retained in all 216 rollouts; central lesions healed with IoU 0.841 (16×16) and 0.745 (32×32) ([asymmetry report](../reports/2026-10-21-e02b-asymmetry-canonical.md)). Prototype mass is balanced (1078/1122 horizontally, 1082/1118 vertically), so the effect is not explained by more tissue on one side; whether it is structural is left to H-AB-2, not yet run.

**Instrument bug found on the way.** The first 12-repeat asymmetry run built the learned prototype with a zeroed stress-EMA because of an inverted `is_trained` flag; 2070 of 4096 cells differed from the canonical prototype. The corrupted artefact is kept as documented history of the error; its absolute IoU is not comparable with canonical runs.

#### One table for the exploratory probes

The probes are collected here so that their status travels with their numbers. `exploratory` is part of the result, not a label to be dropped in the abstract: every row is a run outside the pre-registered E02b protocol, on one prototype (or one transplanted state) per model, and none of them is evidence for §4.2–4.3.

| Probe (hypothesis) | Design | Result | Status | Source |
| --- | --- | --- | --- | --- |
| Where the form lives (H-CH-1) | 3 models × 4 conditions × 12 = 144 rollouts, 2000 steps | `struct_2` same pattern 12/12 in all four conditions (`none`, `visible_zeroed`, `hidden_zeroed`, `hidden_shuffled`), median IoU 0.786–0.825; `memory_in_hidden_channels = false`, `rederivable_from_visible = true`, `hidden_layout_matters = false` | exploratory; prototype non-canonical (alive 2200 vs canonical 2174), so absolute IoU is not comparable | [channel-memory report](../reports/2026-10-21-e02b-channel-memory.md) |
| Strength of the body (H-BI-1) | 3 models × 7 fractions × 12 = 252 rollouts, 2000 steps | survival 12/12 at p = 0…0.9 and 0/12 at p = 1.0; T = 0.90 for both learned models, 0.50 for untrained; verdict `mixed`; at T median alive_b0 = 1 (`struct_2`) vs 22 (`struct_1`) | exploratory; hypothesis refuted in its original dose–response form | [body-integrity report](../reports/2026-10-21-e02b-body-integrity.md) |
| Asymmetry (H-AB-1) | 3 models × 6 lesions × 12 = 216 rollouts, 2000 steps | `struct_2`: cut_left 0.473 vs cut_right 0.792 (Δ = −0.336, sign 12/12), cut_top 0.806 vs cut_bottom 0.659 (Δ = +0.184, sign 12/12); controls below 0.01; class retained 216/216 | exploratory; H-AB-1 confirmed on the canonical prototype only | [asymmetry report](../reports/2026-10-21-e02b-asymmetry-canonical.md) |
| Nucleogenesis (H-NU-1) | 5 focus sizes × 2 packings × 12 × 3 models, plus the k = 0 control and a cross-class block; 420 rollouts, 2000 steps | minimal focus 1 cell (`struct_2`, expansion ×2158) and 8 cells (`struct_1` seed101); untrained never wakes; cross-class block dies 12/12 both ways; "same picture" reached only at 128 cells, `scattered` | exploratory; wake-up verdicts robust, "same picture" verdict rests on the non-canonical prototype | [E02b results](../reports/2026-10-20-e02b-results.md), "Нуклеогенез" |
| Transplants and basins | 12×12 matrix, one state per source = 144 transplants, 2000 steps; repeat with 9 samples per pair = 1296 transplants | 144-run matrix: 6 killers, 5 `single_live_attractor`, 1 `diagonal_unstable` (R-11), 0 multi-basin; the 1296-run repeat finds 0 multi-basin again, `struct_2` 54/54 with death share 0.000 | exploratory; descriptive map, not a proof of a basin | [E02b results](../reports/2026-10-20-e02b-results.md), "Матрица переходов" |

Two of these rows carry a known instrument defect and are labelled as such in their reports: the channel-memory and nucleogenesis prototypes were built with a zeroed stress-EMA from an inverted `is_trained` flag (alive 2200 rather than 2174). The H-AB-1 repeat of 2026-10-21 avoided that path and built its prototypes from the checkpoint EMA (alive 0.530762, 2174 cells). A clean provenance repeat of the channel-memory probe on the canonical prototype is queued and is a condition for using its absolute IoU values.

### 4.5. Replication: `struct_2` does not survive a change of training seed

E02c trained the same R-9 recipe on three pre-registered seeds (142/242/342), then repeated the 64-start, 2000-step census with frozen weights; seed42 was the positive control and the untrained architecture the negative control ([E02c results](../reports/2026-10-21-e02c-results.md), [article 006](../articles/006-replikaciya-r9-struct2-ne-vosproizvelsya.md)).

| Family | `struct_2` | Frozen-centroid class | Ward class |
| --- | ---: | --- | --- |
| seed142 | **0/64** | `struct_1` 64 | `struct_1` 64 |
| seed242 | **0/64** | `uniform_dark` 64 | `uniform_dark` 64 |
| seed342 | **0/64** | `uniform_dark` 64 | `uniform_dark` 64 |
| control seed42 | 64/64 | `struct_2` 64 | `struct_2` 64 |
| control untrained | 0/64 | `struct_1` 64 | `struct_1` 64 |

The result is **0/3**: H-R1 and H-R2 are rejected, H-R3 is confirmed, and H-E02C-1 is rejected. The positive control rules out a broken census; the untrained control reproduces the architectural confound. Final training losses of the new seeds (1.119–1.235) overlap seed42 (1.105), and seed342 has the best `best_loss` of all, so the class difference is not a crude under-training artefact. Across the eight R-9 training seeds, `struct_2` is observed in 1/8 (seed42 only), `struct_1` in 2/8 (101, 142), `uniform_dark` in 4/8 and `uniform_bright` in 1/8; this is a descriptive frequency, not a probability estimate (seed42 is the base seed, not a random draw). A 0/3 outcome is compatible with a frequency up to about 63% by the rule of three, so the correct claim is "not reproduced on the 2000-step horizon", not "impossible".

On this horizon, `struct_2` is a single-seed case study. The E02b findings about its geometry, repair, orientation and basin remain properties of that frozen model; they are not promoted to a property of the R-9 recipe. §4.6 closes the remaining alternative — an unstable run: the seed42 run itself repeats bitwise, so the tie is to the seed, not to run noise.

### 4.6. Seed reproducibility: the class returns with its own seed

E02c left one alternative open: perhaps the seed42 run was not repeatable at all, in which case "a single-seed observation" would also mean an unstable run, and the seed-versus-recipe dispute would be premature. A separate protocol was frozen before the run — same seed, same recipe, same code, same hardware, criterion `struct_2 ≥ 52/64` and stability `≥ 0.80` — and the new checkpoint was written to its own family without overwriting the canonical file ([protocol](../reports/2026-10-21-e02c-seed42-repro-plan.md)).

Training repeated bit for bit. All seven tensors of `model_state_dict` are **bitwise equal** to the canonical `WP4_R-9_s2000_seed42`, and `best_loss` 1.104736089706421 and `alive_fraction_final` 0.34686279296875 agree to the last bit; only the file metadata differs ([seed42 repeat](../reports/2026-10-21-e02c-seed42-repro-results.md)).

The census of the repeat returns `struct_2` in **64/64** starts under the frozen E02b centroids, with stability 58/64 = 0.906 over the last quarter of the run. The positive control (canonical seed42) also returns 64/64 with stability 0.906, and the negative control (untrained) returns `struct_1` 64/64. Descriptor vectors of the repeat and of the positive control are bitwise identical on all 64 starts (maximum absolute difference 0.0), so the census itself added no drift. The frozen criterion (52/64 and 0.80) is met and the outcome is `reproduced`; 192 rollouts took 1257 s on CUDA.

Ward clustering does not name classes in this narrow census. Fitted on 192 rollouts of three families it selects k = 2 with silhouette 0.315, and under those conditions the untrained architecture receives the Ward label `struct_2` (64/64) although the frozen projection gives `struct_1`, while start 61 receives different Ward labels in the two families from bitwise identical descriptors. That is an artefact of the clustering, not a physical difference, so the numbers above come from the frozen projection and the Ward split (42/22 for the repeat against 41/23 for the control) is reported descriptively only. Stability is 0.906 against 1.00 in the E02b census for a related reason — the label of the last quarter rides on the same weak split — and the difference is not read as a degradation of the form.

Three boundaries follow. The repeat is **not an independent reproduction**: same machine, same environment, same code, and the publication gate still requires a different stack. It does not make `struct_2` a property of the recipe: E02c's 0/3 stands, and the class is tied to the training seed. And it checks exactly one seed, so "reproducible from this seed" does not become "stable across seeds" (refuted in E02c) or an estimate of the class frequency for the recipe.

## 5. Discussion

### 5.1. A class label is not a criterion of life

The census labels final states; it does not measure life. A field with one live cell out of 4096 (alive 0.00024) was labelled `struct_2` by the nearest centroid ([E02b results](../reports/2026-10-20-e02b-results.md), limitation 14; [article 005](../articles/005-chto-perepis-nashla-v-morfoprostranstve.md)). Verdicts are therefore decided by alive_fraction (threshold 0.05), not by the label, and such rows are flagged `class_alive_conflict`. A label describes visible morphology; it does not certify a body. Hence "structured class", "morphological attractor in the operational sense", "class-level repair" — never "alive" or "the tissue remembers" ([AGENTS.md](../AGENTS.md) §3; [articles/README](../articles/README.md), rule 5).

### 5.2. One live attractor is not one structured live form

Three of five R-9 models (seeds 202, 303, 404) have exactly one live attractor, but it is a uniform field (chi = 1.0 or 0.0 at alive_fraction = 1.000): alive, structureless. Only seed42 holds a structured form, and it is the only model that neither kills nor homogenises a foreign live state — 54/54 transplants end in `struct_2`. "One live attractor" is not "one live form", and "does not die" is not "holds a morphology". Conversely, `struct_1` appears without training at all: its stability is architectural, not learned.

### 5.3. Measurement traps

1. **Class is not identity.** Recovery is measured by 18 descriptors; IoU 0.15–0.47 shows the global pattern is not restored. High class recovery can coexist with no memory.
2. **A single maximum is not retention.** Reach and hold use different decision points; hold from the target is 1.0 by construction, and `met = true` means fields exist, not that the hypothesis succeeded ([article 004](../articles/004-lovushki-izmereniya-v-nca.md)).
3. **The instrument can be the bug.** The non-canonical stress-EMA prototype produced plausible but incomparable IoU values; only a provenance audit and a reproducibility check exposed it. Corrupted artefacts are kept, not deleted.

### 5.4. Recomputing a class label from the archive

A class can be recomputed without retraining and without re-clustering, from two files — `census.json` for the descriptor vectors and `class_centroids_frozen.json` for the projection:

1. **Descriptor vector.** In `census.json` → `runs[]` → `final`, read the 18 fields listed in `class_centroids_frozen.json` → `features`, in that order. The canonical extractor is `descriptor_vector()` in [`morphogenesis/e02b_morphospace.py`](../morphogenesis/e02b_morphospace.py), which keeps exactly the order of the clustering feature list.
2. **z-normalisation.** `z = (descriptor − scaler_mean) / scaler_std`, with the 18 frozen values from `class_centroids_frozen.json`. Recomputing the scaler on a subset would shift the labels relative to the published ones, which is why `scripts/verify_portable.py` takes it from the frozen file.
3. **Nearest centroid.** `label = labels_valid[argmin(sum((z − centroids_z)², axis=1))]` and the class name is `class_names[label]` — the `how_to_project` string stored in the file; the canonical implementation is `assign_to_clusters()`.
4. **Liveness is a separate verdict.** `alive_fraction ≥ 0.05` (§5.1). A label can coexist with an almost dead field, and such rows are flagged `class_alive_conflict`; verdicts about a body are never taken from the label alone.

A working example is [`scripts/verify_portable.py`](../scripts/verify_portable.py) → `frozen_assign()`, which performs steps 1–3 by calling the canonical function; that is the path the Kaggle CPU run used to reproduce 48/48 census classes with 0 disagreements. The frozen file carries its own check: reprojecting every member of the parent census returns each to its own class (67/67, 320/320, 189/189, 64/64, 64/64, `projection_selfcheck.fraction = 1.0`, 128 control projections checked on refit). One caveat stands and is the reason the centroids were frozen separately: `census.json` does not store `centroids_z` or per-run cluster membership in a form intended for external reassignment ([E02b results](../reports/2026-10-20-e02b-results.md), limitation 9).

## 6. Limitations

- **`struct_2` is tied to a training seed**: E02c tested three new training seeds and found it in 0/3 (seed142 → `struct_1`, seed242/342 → `uniform_dark`); the seed42 control reproduced it 64/64. The seed42 run itself repeats bitwise and returns the class 64/64 (§4.6), so the observation is not run instability, but it is still one seed; a 0/3 result is compatible with a frequency up to about 63%, so the claim is "not reproduced on the 2000-step horizon", not "impossible".
- **`struct_1` is an architectural confound**: untrained reaches it 64/64 and repairs 45/45; H-P1 reaches it in 29/64.
- **H4 was never run**: whether the rule variant matters more than the seed has no data.
- **One architecture**: 64×64×16, fixed channels, one loss family; no claim about NCA in general.
- **Exploratory probes are small**: one prototype per model, 12 repeats, 2000 steps; the channel-memory prototype is non-canonical, and the untrained network is bit-identical across repeats, so its 12 repeats are not independent samples.
- **Determinism is local**: §9.2 was enforced on one CUDA device; cross-hardware reproducibility was not tested.
- **The repeat is not independent reproduction**: the seed42 repeat ran on the same machine, environment and code; independent reproduction on a different stack remains a condition of submission, and the Kaggle pass covers the E02b census, not the E02c series.
- **Taxonomy is descriptive**: k = 5 in 52/100 bootstraps, the `death`/`uniform_dark` boundary is least stable, though `struct_2` survives k = 3–8, jackknife and 10% feature noise.
- **Journal gap**: seven exploratory runs of 2026-10-21 (channel memory, body integrity, transient analysis, geometry of form, H-AB-1 lesion repeat, E02c census, seed42-repro census) have manifests and stdout but no start/finish pair in the canonical journal; recorded, not backfilled. A second census process aborted after one minute and left only an `aborted` manifest.
- **Independent reproduction is class-level, not bitwise**: the portable 18-MB package reproduced 48/48 classes of the E02b census on Kaggle CPU; `n_pixels` and other threshold descriptors drifted, and a GPU run was not available (phone verification). This is enough for the class-level claim, not for numerical identity.

## 7. Data and code availability

Everything needed to re-derive the numbers above is in this repository. Nothing is behind a private link except the two Kaggle copies, which are private by decision and are not required for any claim.

**Artifacts (canonical, in-repo).**

- `morphogenesis/experiments/E02b_morphospace/census.json` — all 832 rollouts (704 learned, 128 control): per-run final 18-descriptor vector, 40-snapshot trajectory, class labels and stability. SHA-256 `e81678b603ddc4def4b3c736a4ca0d9b99b2b0b234f666ef620bcae60cad0775`, 15 526 457 bytes. The hash is the one recorded as `source_census.sha256` in the frozen-centroid file and re-checked on disk on 2026-10-21.
- `morphogenesis/experiments/E02b_morphospace/class_centroids_frozen.json` — the frozen k = 5 centroids (5 × 18) with `scaler_mean`/`scaler_std`, class names and semantics, and the projection self-check (§5.4). SHA-256 `ef71d679a939a089cce6d550b5ea731861ede18161f1cf363972a955e892672d`.
- `morphogenesis/experiments/E02b_morphospace/perturbations.json` — the 180 perturbation outcomes (6 prototypes × 6 perturbations × 5 repeats) behind §4.3. SHA-256 `64a685acd3ea880b6a21a96518d2c5c6a27105b85177ce284c18d809b0b4125b`.
- `morphogenesis/logs/journal.jsonl` — the append-only canonical journal of training runs. The census is forward-only and has no start/finish pair there; its record is the run manifest below (§6 records the same gap for the 2026-10-21 exploratory runs).
- `lab/runs/20261020T195942Z-E02b_morphospace_census.json` — the run manifest of the census: command (`e02b_morphospace.py --steps 2000 --seeds 0-63`), working directory, start and finish, `exit_code: 0`, and the environment below. This is the manifest id referenced throughout.
- `lab/checkpoints.json` — the index of the twelve canonical checkpoints with SHA-256 and size (539 495 742 bytes each); weights themselves are not committed.

**Environment of the census run** (from that manifest, not from memory): python 3.13.11, torch 2.6.0+cu124, numpy 2.5.4, platform `Windows-11-10.0.26300-SP0`, device `NVIDIA GeForce RTX 3070 Laptop GPU, 595.79` (CUDA), 5070.2 s total for 832 rollouts.

**Portable inference package (built locally, not in git).** `dist/e02b-portable` is produced by `scripts/export_portable.py` and described by its `portable_manifest.json`: 30 files, 17 961 042 bytes, twelve lite checkpoints of 152 602 bytes each against 539 495 742 bytes for a full `nca_final.pt`, with both hashes recorded per checkpoint. On an independent stack — Kaggle kernel on CPU — the smoke mode reproduced 48/48 census classes for three families with 0 disagreements and `max_abs_descriptor_diff = 125.0` on `n_pixels`, i.e. class-level rather than bitwise agreement ([portable/Kaggle verification](../reports/2026-10-21-portable-kaggle-verification.md), [kaggle/README](../kaggle/README.md)). The Kaggle dataset `mak777777uh/morphogenesis-e02b-portable` and kernel `mak777777uh/morphogenesis-e02b-portable-verify` are **private** pending the owner's decision; the packaged copy of `census.json` rewrites 25 absolute author paths to repository-relative form and leaves the canonical file byte-identical.

**What is not available.** No independent reproduction of the E02c training series exists: the seed42 repeat ran on the same machine, environment and code (§4.6), and the Kaggle pass covers the E02b census only. The corrupted non-canonical artifacts (channel memory, nucleogenesis, the first 12-repeat ablation) are kept as documented history, not withdrawn, and their absolute IoU values are not comparable with canonical runs.

## 8. Conclusion

A frozen NCA trained on a ring does not hold the ring, but one of twelve checkpoints holds a structured, self-repairing class of texture that no control reproduces. The map is sparse: four of five learned rollouts end in death or uniformity, and the second structural class is an architectural confound. Repair is real at class level and absent at pattern level. The one learned candidate, `struct_2`, does not survive a pre-registered change of training seed: 0/3 new R-9 seeds reproduce it, while the seed42 control does so 64/64. Repeating the seed42 run reproduces the weights bitwise and the class 64/64, so the negative replication is not run instability: the class is reproducible from its own seed and not from the recipe. What remains is a measured single-seed morphology and its boundary — a negative replication, not a recipe-level law, and nothing about life.

## References

Every record below was taken from the library index ([`library/publications/README.md`](../library/publications/README.md)) and independently re-checked against the Crossref API on 2026-10-21 (title, container, volume/issue and pages or article number); the DOIs/URLs are reproduced as recorded in the index. Two Levin records carry a publisher URL because the index holds no DOI for them. No work is cited that the text does not use (§2).

- Chan, B. W.-C. (2019). *Lenia: Biology of Artificial Life*. Complex Systems, 28(3), 251–286. https://doi.org/10.25088/ComplexSystems.28.3.251
- Cvjetko, M., Hartl, B., Levin, M., Moulin-Frier, C., & Oudeyer, P.-Y. (2026). *The Artificial Experimentalist: Discovery and Control of Self-Organizing Phenomena with Autotelic Reinforcement Learning*. ALIFE 2026: Proceedings of the 2026 Artificial Life Conference. https://doi.org/10.1162/isal.a.971
- Hartl, B., Levin, M., & Pio-Lopez, L. (2026). *Neural cellular automata: applications to biology and beyond classical AI*. Physics of Life Reviews, 56, 94–108. https://doi.org/10.1016/j.plrev.2025.11.010
- Horibe, K., Walker, K., & Risi, S. (2021). *Regenerating Soft Robots Through Neural Cellular Automata*. Genetic Programming (EuroGP 2021), LNCS, 36–50. https://doi.org/10.1007/978-3-030-72812-0_3
- Levin, M. (2022). *Technological Approach to Mind Everywhere*. Frontiers in Systems Neuroscience. https://www.frontiersin.org/articles/10.3389/fnsys.2022.768201/full
- Levin, M. (2023). *Synthetic morphology with agential materials*. Nature Reviews Bioengineering. https://www.nature.com/articles/s44222-022-00001-9
- MacDermott, M., Fox, J., Belardinelli, F., & Everitt, T. (2024). *Measuring Goal-Directedness*. Advances in Neural Information Processing Systems 37, 11412–11431. https://doi.org/10.52202/079017-0363
- Moreno, R., Faíña, A., Sudhakaran, S., Walker, K., & Risi, S. (2026). *Smart cellular bricks for decentralized shape classification and damage recovery*. Nature Communications, 17, 5932. https://doi.org/10.1038/s41467-026-75166-7
- Mordvintsev, A., Randazzo, E., Niklasson, E., & Levin, M. (2020). *Growing Neural Cellular Automata*. Distill, 5(2). https://doi.org/10.23915/distill.00023
- Randazzo, E., Mordvintsev, A., Niklasson, E., Levin, M., & Greydanus, S. (2020). *Self-classifying MNIST Digits*. Distill, 5(8). https://doi.org/10.23915/distill.00027.002
- Sacco, F., Sakthivadivel, D. A. R., & Levin, M. (2026). *Topological constraints on self-organization in locally interacting systems*. Philosophical Transactions of the Royal Society A, 384(2320). https://doi.org/10.1098/rsta.2025.0011
- Sudhakaran, S., Grbic, D., Li, S., Katona, A., Najarro, E., Glanois, C., & Risi, S. (2021). *Growing 3D Artefacts and Functional Machines with Neural Cellular Automata*. The 2021 Conference on Artificial Life (ALIFE 2021), MIT Press. https://doi.org/10.1162/isal_a_00451

- **Primary sources index:** [`library/publications/README.md`](../library/publications/README.md) (source → hypothesis → experiment, status per row).

---

**Verification:** numbers were checked against [E02](../reports/2026-10-20-e02-pattern.md), [E02b](../reports/2026-10-20-e02b-results.md), [channel memory](../reports/2026-10-21-e02b-channel-memory.md), [body integrity](../reports/2026-10-21-e02b-body-integrity.md), [asymmetry](../reports/2026-10-21-e02b-asymmetry-canonical.md), [E02c](../reports/2026-10-21-e02c-results.md) and the [seed42 repeat](../reports/2026-10-21-e02c-seed42-repro-results.md) (bitwise weight equality, `best_loss` 1.104736089706421, 64/64 and 58/64 = 0.906, Ward k = 2 / silhouette 0.315). Data-availability paths, SHA-256 values, file sizes and environment versions were read from the artifacts and manifests and re-checked on disk on 2026-10-21 (census `e81678b6…0775`, centroids `ef71d679…2672d`, perturbations `64a685ac…125b`, manifest `20261020T195942Z-E02b_morphospace_census`, lite 152 602 B vs full 539 495 742 B). Bibliographic records were taken from the library index and not from memory. Independent reproduction passed at class level (48/48) on Kaggle CPU for the E02b census ([verification report](../reports/2026-10-21-portable-kaggle-verification.md)); the seed42 repeat ran on the same hardware and is not independent. **Do not cite without owner approval.**
