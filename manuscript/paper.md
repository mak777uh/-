# What Morphologies Does a Neural Cellular Automaton Hold? A Census and a Negative Result

**Status:** DRAFT v0.2 (2026-10-21) — not submitted, not peer-reviewed, do not cite. **Publication gate:** E02c is closed and the portable package passed an independent CPU reproduction; external submission remains a decision of the owner. No claim about life, consciousness or intelligence; only observable behavioural classes and their boundaries ([AGENTS.md](../AGENTS.md) §3).

<!-- TODO: freeze a submission tag and run the independent-reproduction pass before any external submission. -->

## Abstract

Neural cellular automata are usually trained to grow a prescribed pattern. What morphologies does such a system hold when the target is removed? We census twelve frozen checkpoints (five H-A0, five R-9, one R-11, one H-P1) plus an untrained control: 64 deterministic noise starts per model, 2000 steps, frozen weights, 18 descriptors and Ward clustering at k = 5. Of 704 learned rollouts, 573 (81.4%) end in death or in a uniform field; two structured classes remain. `struct_1` is reproduced by the untrained architecture, so its repair does not require learning. `struct_2` appears only in R-9 seed42, is absent from all controls and from 768 rollouts of other models, and returns to its class after 20% amputation. An earlier ring target had failed: the ring was neither reached from noise nor held. A pre-registered replication then trained R-9 on three new seeds (142/242/342) and repeated the 64-start census: **none** produced `struct_2` (seed142 → `struct_1`, seed242/342 → `uniform_dark`), while the seed42 control reproduced it 64/64. The learned candidate is therefore a single-seed case study on the 2000-step horizon, not a property of the recipe. We describe the map as sparse, the repair as class-level rather than bitwise, and make no claim that either class is alive.

## 1. Introduction

Can a local learnable rule hold more than the one pattern it was optimised for? The first target was explicit: a ring, trained as a coverage objective and probed for reach and hold. E02 closed negatively — the ring was not an attractor of the learned dynamics ([E02 report](../reports/2026-10-20-e02-pattern.md), [article 002](../articles/002-pochemu-kolco-ne-stalo-attraktorom.md)). That failure motivated a different question: not whether one prescribed form can be grown, but **which morphologies the existing frozen checkpoints already hold when asked nothing specific**.

E02b answered by census rather than training: it froze every canonical checkpoint, started each model from 64 deterministic noise states, ran 2000 steps without gradient, described each final state with 18 descriptors and clustered the results ([E02b results](../reports/2026-10-20-e02b-results.md)). This manuscript assembles that census, the E02 negative result, and four follow-up probes into one cumulative text.

The contribution is deliberately narrow: a sparse census of what twelve frozen checkpoints hold; a description of repair as recovery of a **class** of texture, not of a bitwise pattern; a pre-registered replication showing that the only learned candidate does **not** survive a change of training seed; and an explicit account of what the measurements cannot show. The scope is equally narrow: one architecture, one recipe family, one training seed for the only learned candidate, and no claim about adaptation, goals, information or agency.

## 2. Related work

The conceptual frame is the literature on morphogenesis as computation and on "agential materials" — a tissue can solve a shape problem rather than execute a fixed plan (Levin; reading map in [`library/levin/README.md`](../library/levin/README.md)). This frame motivates the question but is not a result: our data can say that a class of texture returns after amputation; they cannot say that the tissue "remembers a plan".

The technical lineage is the neural cellular automaton: a differentiable local rule trained to grow and regenerate a target (Mordvintsev et al., 2020, and the works in [`library/hypotheses/nca-lineage.md`](../library/hypotheses/nca-lineage.md)). Our contribution is not a new architecture but a pre-registered census of what trained rules hold, including the negative ring result that preceded it. No source is restated or reprinted; records and our notes are in the library ([index](../library/publications/README.md), [Levin map](../library/levin/README.md), [NCA lineage](../library/hypotheses/nca-lineage.md)).

<!-- TODO: replace narrative citations with verified records (authors, year, venue, DOI/link) from library/publications/README.md. -->

## 3. Methods

### 3.1. Model and checkpoints

The automaton is a 64×64 grid with 16 channels: channel 0 visible, channel 1 alive mask, channel 15 stress ([E02 report](../reports/2026-10-20-e02-pattern.md)). We use the twelve canonical `nca_final.pt` checkpoints of E02b — H-A0 ×5 (seeds 42/101/202/303/404), R-9 ×5, R-11 ×1, H-P1 ×1 (positive control whose training pool starts from the target) — plus an untrained model of the same architecture as a runtime control without weights.

Provenance was audited before any class was read: byte hashes match the index, seeds and metadata match their families, iteration is 2000 for all, SHA-256 over `model_state_dict` is pairwise distinct 12/12, and four H-A0 files share a final loss to the last bit while having distinct weights — the same loss on a dead field, not duplicate files ([E02b results](../reports/2026-10-20-e02b-results.md), "Происхождение канонических чекпоинтов").

### 3.2. Training recipes

All checkpoints were trained for 2000 steps against a ring with density p = 0.15234375 and signature b0 = 1, b1 = 1, chi = 0. H-A0 is the baseline; R-9 adds a quiet-background term of weight 1.0 on top of R-8; R-11 adds the same term on top of R-7 without the strengthened alive-policy; H-P1 is the positive control whose pool starts from the target ([E02 report](../reports/2026-10-20-e02-pattern.md), [WP4 status](../reports/2026-10-20-wp4-status.md), [negative-results log](../morphogenesis/memory/negative_results.md)). The arms differ in loss composition, not architecture — which is why the census can compare five R-9 seeds that share a recipe but differ in training seed.

<!-- TODO: add exact loss terms and weights from the frozen training config; do not infer them from memory. -->

### 3.3. Census protocol

For every checkpoint we ran 64 deterministic initial states (seeds 0–63) from `init_state` for 2000 steps with frozen weights and no gradient, snapshotting every 50 steps. With 13 families (12 checkpoints plus untrained) this gives 832 rollouts, 704 learned and 128 control. The protocol ran on CUDA in 5070.2 s; families took 365.4–423.9 s. All 64 seeds enter the denominator ([E02b results](../reports/2026-10-20-e02b-results.md)).

Controls are projected onto learned centroids and do not participate in fitting. Class semantics are fixed: `death` when alive_fraction < 0.01, `uniform_dark` when binary_fraction < 0.01, `uniform_bright` when binary_fraction > 0.95, else `structured`.

### 3.4. Descriptors and clustering

Each final state gets 18 features: alive fraction, binary and bright density, mean soft intensity, entropy, components and holes (b0, b1), Euler characteristic, bounding-box fill, largest-component fraction, radial profile and variance, rotational and reflection symmetry, autocorrelations (lags 1, 4; 2 and 8 in follow-ups) and edge fraction ([E02b results](../reports/2026-10-20-e02b-results.md)). Features are z-normalised; Ward clustering builds classes with k chosen by silhouette and minimum class size 5; DBSCAN is an agreement check, not the source of classes. The solution is k = 5, silhouette 0.8545; DBSCAN gives 7 clusters, 4/704 noise (0.57%), ARI 0.9137. The taxonomy is descriptive: bootstrap over k selects k = 5 in 52%, while `struct_2` survives intact for k = 3–8.

### 3.5. Perturbations

For each structural class three prototypes were chosen by distance to the centroid. Three prototypes per class × six perturbations × five repeats gave 180 rollouts: 10% and 20% amputation, noise σ = 0.1, a cut of half the field, a patch transplant into a dead field, and a dead-field control. Runs lasted 500 steps with snapshots every 25; recovery means the final state is assigned to the prototype's class again ([E02b results](../reports/2026-10-20-e02b-results.md), "Возмущения"). Two deviations are recorded, not hidden: amputation zeroes all 16 channels (stronger than the literal protocol), and the protocol transplant was degenerate (bounding box = whole field), so the growth claim rests on exploratory patches (§4.3).

### 3.6. Determinism and compute

Runs follow the specification's determinism contract ([spec §9.2](../docs/spec/MORPHOGENESIS_v5.6_Rev11.md)): `CUBLAS_WORKSPACE_CONFIG` set before CUDA init, `torch.use_deterministic_algorithms(True)`, deterministic cuDNN with benchmark off, fixed seeds. Census used CUDA on an RTX 3070 Laptop; the canonical prototype path reproduces bit-identically within and across processes ([E02b results](../reports/2026-10-20-e02b-results.md)). Cross-hardware determinism was not tested.

<!-- TODO: record exact torch/CUDA versions and the manifest run id in a data-availability paragraph. -->

## 4. Results

### 4.1. The ring target was not an attractor

E02 asked whether a ring is reachable from noise and stable from the target; it is neither. The layer-1 gate (5 seeds × 800 steps) failed all four conditions — no collapse 0/5, Chamfer improvement 0/5, coverage above threshold 0/5, retention 0/5 — and every run was stopped by `collapse_fuse` with visible MSE 0.2498–0.2499, the dead-field plateau ([E02 report](../reports/2026-10-20-e02-pattern.md), [WP4 status](../reports/2026-10-20-wp4-status.md)). With the structural ceiling 2p/(1+p) = 0.2644 and the gate 0.3144, the best family-R f1 was 0.2419 at iteration 650 (R-9), 0.0225 below the ceiling and 0.0725 below the gate. Reach maxima were 0.2755–0.2793 at precision 0.15–0.17 ("almost everything bright", not a ring); the only holder, H-P1, decayed with horizon (0.9495 → 0.3959 → 0.2069). The WP4 artefact gate is formally unpassed (`journal_pairs_13_3 = false`): `met = true` means fields and runs exist, not that the science succeeded.

<!-- TODO: explain why the ring remained a calibration target rather than a negative control for "form" in general. -->

### 4.2. A sparse map with two structural classes

Ward at k = 5 gives class sizes [67, 320, 189, 64, 64] over learned runs: `struct_1`, `death`, `uniform_dark`, `uniform_bright`, `struct_2` ([E02b results](../reports/2026-10-20-e02b-results.md)). Of 704 learned rollouts, 573 end in death or a uniform field — 81.4% (death_or_uniform_fraction = 0.8139) — and 131 (18.6%) are structural. The formal outcome is `rich_map`, but the map is sparse: four of five learned runs show no structure.

The two structural classes are not equivalent. **`struct_1`** (67 learned, 93 control rollouts) is a fine speckle: alive median 0.7959, binary median 0.2561, b0 ≈ 382, b1 ≈ 2; it is reproduced 64/64 by the untrained architecture and appears in 29/64 H-P1 rollouts, so it is an architectural confound, not evidence of learned morphology. **`struct_2`** (64 learned, 0 control) is a connected tissue with many holes: alive median 0.5310, binary median 0.5310, b0 ≈ 1, b1 ≈ 1844.5, entropy median 0.2535; R-9 seed42 produces it from all 64 noise starts, no control produces it, and it is absent even transiently from the 768 rollouts of other models.

H1 (a non-trivial reproducible class) and H2 (R-11's structure is transient: 61/64 finals non-structural, `struct_1` on some snapshot 64/64) were supported; H3 was refuted (§4.3); H4 — whether the rule variant matters more than the seed — was not run.

<!-- TODO: add the PCA figure and class table once figure numbering is fixed; link reports/figures/e02b_morphospace_pca.png. -->

### 4.3. Repair at the level of a class, not a pattern

After 20% amputation of live cells (zeroing all 16 channels), both structural classes returned to their own class in 15/15 repeats, median return at the first snapshot (25 steps) ([E02b results](../reports/2026-10-20-e02b-results.md)). This refutes H3, which expected no recovery above 50%. For `struct_1` learning is not required: three seeded untrained initialisations give 64/64 `struct_1` and 45/45 returns after the same amputation.

Recovery is class-level, not bitwise. Patches of 8×8, 16×16 and 32×32 transplanted into a zero field (2 classes × 3 sizes × 5 positions = 30) all grew into their class within 500 steps, but the global pattern did not return: IoU with the prototype was 0.15–0.47, and `struct_1` agreement was at the random-field level. Small seeds organise more slowly (25 steps for 32×32, 225 for 8×8, 275 for 16×16 in `struct_2`), and convergence is not observed even at 2000 steps.

The transplant matrix says the same from the other side. A 12×12 matrix (144 transplants) found six killers (H-A0 ×5 and H-P1), five single-live-attractor models, one diagonally unstable model (R-11) and zero multi-basin candidates: no model holds two stable live forms. A repeat with nine samples per pair (1296 transplants) reproduced the verdicts; R-9 seed42 pulled all 54 foreign live states into `struct_2` with death share exactly 0.000. The reverse transplant is equally model-specific: `struct_2` into R-9 seed101 ends in death 16/16, while seeds 202 and 303 return to their own classes 16/16.

<!-- TODO: state whether the 25-step return time is an upper bound set by snapshot resolution. -->

### 4.4. Exploratory probes: channels, strength, asymmetry

Four follow-up probes were run after the census with rules written before each run; they do not change the pre-registered verdicts.

**Where the form lives (H-CH-1).** In 144 rollouts (3 models × 4 conditions × 12), `struct_2` reproduced the same pattern 12/12 intact, with visible texture zeroed, with hidden channels zeroed, and with hidden channels shuffled; median IoU 0.786–0.825 ([channel-memory report](../reports/2026-10-21-e02b-channel-memory.md)). "Form is held in hidden channels" is rejected in its strong form: `memory_in_hidden_channels = false`. The prototype was non-canonical (alive 2200/3240 vs canonical 2174/3263), so absolute IoU is not comparable with canonical runs; a clean provenance repeat is required before publication.

**Strength of the body (H-BI-1).** In 252 rollouts (3 models × 7 fractions × 12), `struct_2` survived 12/12 at every fraction from 0 to 0.9 and 0/12 at 1.0 — a threshold, not a dose-response ([body-integrity report](../reports/2026-10-21-e02b-body-integrity.md)). T is 0.90 for both learned models and 0.50 for the untrained network; the verdict is `mixed` because `struct_2` is not more tolerant than `struct_1`. What it adds is a connected body: median alive_b0 = 1 at T, against about 22 islands for `struct_1`.

**Asymmetry (H-AB-1).** On the canonical prototype, 216 rollouts (3 models × 6 lesions × 12) gave, for `struct_2`, cut_left 0.473 vs cut_right 0.792 (Δ = −0.336, sign 12/12) and cut_top 0.806 vs cut_bottom 0.659 (Δ = +0.184, sign 12/12). Both axes pass the pre-registered rule (sign in ≥11/12 and |Δ| ≥ 0.05); `struct_1` and untrained stay below 0.01. The class was retained in all 216 rollouts; central lesions healed with IoU 0.841 (16×16) and 0.745 (32×32) ([asymmetry report](../reports/2026-10-21-e02b-asymmetry-canonical.md)). Prototype mass is balanced (1078/1122 horizontally, 1082/1118 vertically), so the effect is not explained by more tissue on one side; whether it is structural is left to H-AB-2, not yet run.

**Instrument bug found on the way.** The first 12-repeat asymmetry run built the learned prototype with a zeroed stress-EMA because of an inverted `is_trained` flag; 2070 of 4096 cells differed from the canonical prototype. The corrupted artefact is kept as documented history of the error; its absolute IoU is not comparable with canonical runs.

<!-- TODO: merge the probes into one table when figure numbering is fixed; keep their exploratory status visible. -->

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

On this horizon, `struct_2` is a single-seed case study. The E02b findings about its geometry, repair, orientation and basin remain properties of that frozen model; they are not promoted to a property of the R-9 recipe.

## 5. Discussion

### 5.1. A class label is not a criterion of life

The census labels final states; it does not measure life. A field with one live cell out of 4096 (alive 0.00024) was labelled `struct_2` by the nearest centroid ([E02b results](../reports/2026-10-20-e02b-results.md), limitation 14; [article 005](../articles/005-chto-perepis-nashla-v-morfoprostranstve.md)). Verdicts are therefore decided by alive_fraction (threshold 0.05), not by the label, and such rows are flagged `class_alive_conflict`. A label describes visible morphology; it does not certify a body. Hence "structured class", "morphological attractor in the operational sense", "class-level repair" — never "alive" or "the tissue remembers" ([AGENTS.md](../AGENTS.md) §3; [articles/README](../articles/README.md), rule 5).

### 5.2. One live attractor is not one structured live form

Three of five R-9 models (seeds 202, 303, 404) have exactly one live attractor, but it is a uniform field (chi = 1.0 or 0.0 at alive_fraction = 1.000): alive, structureless. Only seed42 holds a structured form, and it is the only model that neither kills nor homogenises a foreign live state — 54/54 transplants end in `struct_2`. "One live attractor" is not "one live form", and "does not die" is not "holds a morphology". Conversely, `struct_1` appears without training at all: its stability is architectural, not learned.

### 5.3. Measurement traps

1. **Class is not identity.** Recovery is measured by 18 descriptors; IoU 0.15–0.47 shows the global pattern is not restored. High class recovery can coexist with no memory.
2. **A single maximum is not retention.** Reach and hold use different decision points; hold from the target is 1.0 by construction, and `met = true` means fields exist, not that the hypothesis succeeded ([article 004](../articles/004-lovushki-izmereniya-v-nca.md)).
3. **The instrument can be the bug.** The non-canonical stress-EMA prototype produced plausible but incomparable IoU values; only a provenance audit and a reproducibility check exposed it. Corrupted artefacts are kept, not deleted.

<!-- TODO: explain how a reader reproduces class assignment from census.json and frozen centroids. -->

## 6. Limitations

- **`struct_2` is a single-seed case study**: E02c tested three new training seeds and found it in 0/3 (seed142 → `struct_1`, seed242/342 → `uniform_dark`); the seed42 control reproduced it 64/64. A 0/3 result is compatible with a frequency up to about 63%, so the claim is "not reproduced on the 2000-step horizon", not "impossible".
- **`struct_1` is an architectural confound**: untrained reaches it 64/64 and repairs 45/45; H-P1 reaches it in 29/64.
- **H4 was never run**: whether the rule variant matters more than the seed has no data.
- **One architecture**: 64×64×16, fixed channels, one loss family; no claim about NCA in general.
- **Exploratory probes are small**: one prototype per model, 12 repeats, 2000 steps; the channel-memory prototype is non-canonical, and the untrained network is bit-identical across repeats, so its 12 repeats are not independent samples.
- **Determinism is local**: §9.2 was enforced on one CUDA device; cross-hardware reproducibility was not tested.
- **Taxonomy is descriptive**: k = 5 in 52/100 bootstraps, the `death`/`uniform_dark` boundary is least stable, though `struct_2` survives k = 3–8, jackknife and 10% feature noise.
- **Journal gap**: six exploratory runs of 2026-10-21 (channel memory, body integrity, transient analysis, geometry of form, H-AB-1 lesion repeat, E02c census) have manifests and stdout but no start/finish pair in the canonical journal; recorded, not backfilled. A second census process aborted after one minute and left only an `aborted` manifest.
- **Independent reproduction is class-level, not bitwise**: the portable 18-MB package reproduced 48/48 classes of the E02b census on Kaggle CPU; `n_pixels` and other threshold descriptors drifted, and a GPU run was not available (phone verification). This is enough for the class-level claim, not for numerical identity.

<!-- TODO: add a data-availability statement linking census.json, perturbations.json and archived manifests. -->

## 7. Conclusion

A frozen NCA trained on a ring does not hold the ring, but one of twelve checkpoints holds a structured, self-repairing class of texture that no control reproduces. The map is sparse: four of five learned rollouts end in death or uniformity, and the second structural class is an architectural confound. Repair is real at class level and absent at pattern level. The one learned candidate, `struct_2`, does not survive a pre-registered change of training seed: 0/3 new R-9 seeds reproduce it, while the seed42 control does so 64/64. What remains is a measured single-seed morphology and its boundary — a negative replication, not a recipe-level law, and nothing about life.

## References

<!-- TODO: replace every placeholder with a verified record (authors, year, title, venue, DOI or stable URL) from library/publications/README.md; do not invent DOIs. -->

- **[Placeholder — NCA]** Mordvintsev et al., *Growing Neural Cellular Automata* (2020). Record and notes: [`library/hypotheses/nca-lineage.md`](../library/hypotheses/nca-lineage.md).
- **[Placeholder — Levin]** M. Levin, work on agential materials and morphological memory. Records: [`library/levin/README.md`](../library/levin/README.md).
- **[Placeholder — measurement]** Laboratory note on measurement traps in NCA: [article 004](../articles/004-lovushki-izmereniya-v-nca.md).
- **Primary sources index:** [`library/publications/README.md`](../library/publications/README.md) (source → hypothesis → experiment, status per row).

---

**Verification:** numbers were checked against [E02](../reports/2026-10-20-e02-pattern.md), [E02b](../reports/2026-10-20-e02b-results.md), [channel memory](../reports/2026-10-21-e02b-channel-memory.md), [body integrity](../reports/2026-10-21-e02b-body-integrity.md), [asymmetry](../reports/2026-10-21-e02b-asymmetry-canonical.md) and [E02c](../reports/2026-10-21-e02c-results.md). Independent reproduction passed at class level (48/48) on Kaggle CPU. **Do not cite without owner approval.**
