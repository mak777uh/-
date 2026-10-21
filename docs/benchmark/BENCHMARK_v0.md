# E02b Reproduction Benchmark v0

**Status:** draft specification, internal. No leaderboard exists, no submissions are
being accepted, and nothing here is published. This document defines *what would be
scored* and *how*, so that the protocol can be criticised before anyone runs it.

**Scope in one sentence:** given twelve frozen NCA checkpoints and a frozen class
definer, reproduce and extend the E02b census measurements without training anything,
and report every seed in the denominator.

## 1. Why v0 and not v1

A benchmark earns the name by having participants other than its authors. This one does
not, yet:

| Requirement for v1 | Status |
| --- | --- |
| External baselines (someone else's run, own implementation) | none — all numbers are ours |
| Leaderboard with independent submissions | none |
| Hidden evaluation set actually executed by a third party | seeds `128–191` reserved, never run |
| More than one training seed per class | no: `struct_2` exists at one training seed only |
| Stable, versioned scorer with its own tests | scorer described here, not yet implemented |
| Independent reproduction of the headline numbers | verification exists in-repo, but by the same authors |

So v0 is a **reproducibility contract**, not a competition: it fixes tasks, metrics,
denominators and a submission format so that (a) our own replication work has a target,
and (b) an outside group can produce a comparable artifact without negotiating
definitions. The version bumps to v1 only when an outside run exists and the scorer has
been exercised on a submission it did not produce.

Two related caveats belong up front:

- The census was pre-registered with four hypotheses; **H4 was never run**, and this
  benchmark does not test it. A rule-variant track would be a new experiment requiring
  owner sign-off.
- The predecessor experiment E02 closed **negatively** (the ring pattern was not an
  attractor). Nothing here reopens it.

## 2. What is fixed (and must not be tuned)

These are the constants a submission may not change. If you change one, you are running a
different benchmark and must label it as such.

| Constant | Value | Where it comes from |
| --- | --- | --- |
| Model architecture | the E02b NCA (16 channels, Moore 3×3 perception → 9×16 inputs, 1×1 cell brain, alive masking as in the census) | `census.json` → `runs[*].alive_mask_enabled`; `config.MOORE_NEIGHBOR_OFFSETS` |
| Checkpoints | 12 inference-lite files, `nca_final.pt` per family | dataset card, `docs/dataset/DATASET_CARD.md` |
| Descriptor vector | 18 features in fixed order | `census.json` → `clustering.features` |
| Scaler | frozen `scaler_mean` / `scaler_std` | `class_centroids_frozen.json` |
| Class definer | frozen `centroids_z`, `class_names`, `labels_valid` | `class_centroids_frozen.json` |
| Class semantics | `death` if `alive_fraction < 0.01`; `uniform_dark` if `binary_fraction < 0.01`; `uniform_bright` if `binary_fraction > 0.95`; else `structured` | protocol |
| Liveness threshold for verdicts | `alive_fraction ≥ 0.05` | added after a 1-of-4096 cell field was labelled `struct_2` |
| Rollout horizon | 2000 steps, snapshot every 50 | protocol |
| Reference run | `census.json`, SHA-256 `e81678b6…0775` | dataset card |

**No refitting.** A submission that re-derives centroids with a different `k`, different
features or a different scaler is reported separately as "refit" and is **not**
comparable; that is allowed as research, not as a score.

## 3. Tasks

Five tasks. Each has a fixed denominator; every seed is counted, including failures.
Nothing is dropped for being uninteresting.

### T1 — Census replication

Run the full protocol: 13 families × 64 seeds (`0–63`) × 2000 steps, snapshot every 50.
Assign each final state a class through the frozen centroids and compare with
`census.json`.

- **Primary metric:** per-family agreement rate, i.e. fraction of runs whose assigned
  class equals the reference class. Reported per family, then macro-averaged over the 13
  families (each family weighted equally, not by its size).
- **Secondary metric:** descriptor drift — mean absolute deviation in z-space between
  submitted and reference descriptors, per feature, per family.
- **Denominator:** 832 runs. Always.
- **Reference:** agreement 1.000 by construction; the honest target for an independent
  implementation is "agreement high enough that no family changes its modal class".

### T2 — Reach (from noise to a named class)

For a target class and a checkpoint, measure how often the rollout ends in that class.

- **Primary metric:** `reach_rate = |{seeds: final_class = target}| / 64`.
- **Secondary metric:** `stability_rate` — fraction of seeds where the class matches in
  the last quarter of snapshots as well (`stability_last_quarter ≥ 0.8`).
- **Denominator:** 64 seeds, no exclusions.
- **Baselines:** see §4.

### T3 — Hold (persistence beyond the protocol horizon)

Take 16 seeds, extend to 6000 steps, and ask whether the class is still the same.

- **Primary metric:** `persistence = |{seeds: class(6000) = class(2000)}| / 16`, plus
  `stability_rate` at 6000.
- **Denominator:** 16 seeds.
- **Baseline:** `R-9 seed42` → 16/16 `struct_2` at 2000, 4000 and 6000; last-quarter
  stability 1.00; `alive` median 0.5259.
- **Caveat that must travel with any number here:** 16 starts, one checkpoint, one
  horizon. This is not an asymptotics result.

### T4 — Repair (amputation)

Amputate 20 % of live cells (**all 16 channels zeroed**, as in the census — note this is
stronger than zeroing only `alive` and `visible`), run 500 steps, snapshot every 25,
assign the class.

- **Primary metric:** `recovery_fraction` — fraction of repeats whose final class equals
  the prototype's class.
- **Secondary metrics:** median return step (first snapshot in the matching class);
  binary IoU with the prototype at the final snapshot, reported **with the random
  baseline** `p/(2−p)` for the observed density `p`.
- **Denominator:** 15 repeats per class (3 prototypes × 5), or 12 per condition for the
  12-repeat ablation variant.
- **Mandatory control:** a fully dead field. It must stay exactly zero. If anything
  germinates there, the block is `control_failed` and no repair claim may be made.
- **Baselines:** `struct_1` 15/15, `struct_2` 15/15, median return step 25 (the first
  snapshot — real time is shorter than the protocol can resolve).

The metric pair matters: class recovery is high while pattern IoU is near the random
baseline. A submission that reports only `recovery_fraction` is reporting the weaker half
of the result, and the scorer flags it.

### T5 — Transplant prediction (predict before you run)

This is the only task with a genuine prediction component in v0.

- **Setup:** a source state (final field of model S from a stated seed) is injected as the
  initial condition of model T. Predict the outcome class **before** running.
- **Primary metric:** top-1 accuracy over the declared prediction set, with the outcome
  determined by the protocol: field alive (`alive_fraction ≥ 0.05`) and class equal to the
  predicted class. Non-predictions are counted as wrong, not skipped.
- **Secondary metric:** Brier score over the five class labels, so that "I guessed
  `struct_2` for everything" is visibly worse than a calibrated prediction.
- **Denominator:** every pair in the declared matrix — 144 pairs for the single-state
  matrix, or 144 pairs × 9 samples for the repeated matrix (1296 transplants).
- **Baselines:** `R-9 seed42` pulls **54/54** live transplants into `struct_2` and kills
  none; `R-9 seed101` kills **45/54**; `R-9 seed202` absorbs 47/54; `R-9 seed303` and
  `seed404` absorb 54/54 into a uniform class; `R-11` is unstable on its diagonal
  (structure is a transient phase, not a second attractor).
- **Why this task exists:** it is the one place where a self-reported summary cannot be
  trusted, because the label is a prediction. The scorer checks it against the executed
  outcome in the same submission.

Conceptual framing for T5 comes from regeneration biology — cells keep a memory of tissue
origin ([Kragl et al., 2009](https://doi.org/10.1038/nature08152)) and body boundaries
constrain identity ([Levin, 2021](https://doi.org/10.1016/j.bbrc.2020.10.077)). Those works
motivate the *question*; they are not evidence about this model. On the present stand the
cross-transplant block killed both directions 12/12, which is a negative result for
patch-level identity transfer, not a confirmation of it.

## 4. Baselines

Four baselines, all reproducible without training:

| Baseline | What it is | Where the numbers are |
| --- | --- | --- |
| `R-9 seed42` | the only checkpoint holding a structured class that no control reproduces | `struct_2` 64/64; repair 15/15; transplant 54/54 |
| `R-9 seed101` | structured, but confounded with architecture | `struct_1` 64/64; repair 15/15; kills 45/54 transplants |
| `untrained` | fresh initialisation of the same architecture, no weights loaded | `struct_1` 64/64; "repair" 45/45 — i.e. indistinguishable from seed101 on this metric |
| `H-P1 seed42` | positive control whose pool starts from the target | `death` 35/64, `struct_1` 29/64; kills all live transplants |

The `untrained` row is the most important one in the table: it means T4 cannot
discriminate learning from architecture on `struct_1`. Any submission that reports
`struct_1` repair as a result must also report the untrained baseline next to it.

Baselines are **descriptive**: the census is one training seed per class, so these are not
estimates of a population of training runs.

## 5. Seeds

| Range | Status | Use |
| --- | --- | --- |
| `0–63` | published in the census | T1, T2, T4, T5 (training-time evaluation) |
| `64–127` | used in an exploratory held-out check (64/64 both structured classes) | not pristine; may be used for development, must be declared |
| `128–191` | **never executed by this lab** | reserved as the hidden evaluation range |
| `≥ 192` | unused | free for new work, must be declared |

**Honest statement about the hidden range:** seeds `128–191` are hidden *in the sense that
no result on them exists*. There is no organiser holding a sealed answer key, because
nobody has run them. v1 requires that someone (ideally not the authors) executes the
hidden range once, commits the hash of the resulting artifact, and only then accepts
submissions scored against it. Until that happens, "hidden set" in this document means
"reserved", and no submission may claim a hidden-set score.

## 6. Submission format

One JSON file. Self-reported labels are welcome but are **not** trusted: the scorer
recomputes classes from the submitted descriptor vectors using the frozen centroids and
reports both the declared and the recomputed label.

```json
{
  "schema_version": "e02b-bench-v0",
  "submission_id": "<free-form, unique>",
  "submitted_at": "<ISO-8601 UTC>",
  "task": "T1 | T2 | T3 | T4 | T5",
  "model": {
    "family": "WP4_R-9_s2000_seed42",
    "checkpoint_kind": "lite | full",
    "checkpoint_sha256": "<sha256 of the file actually loaded>",
    "training_seed": 42,
    "steps": 2000,
    "arch_overrides": {}
  },
  "protocol": {
    "nca_implementation_commit": "<git sha of the code that rolled out the field>",
    "steps": 2000,
    "snapshot_every": 50,
    "seed_range": [0, 63],
    "device": "cpu | cuda",
    "dtype": "float32"
  },
  "class_definer": {
    "source": "class_centroids_frozen.json",
    "sha256": "ef71d679a939a089cce6d550b5ea731861ede18161f1cf363972a955e892672d",
    "refit": false
  },
  "runs": [
    {
      "seed": 0,
      "declared_class": "struct_2",
      "alive_fraction": 0.531,
      "binary_fraction": 0.531,
      "stability_last_quarter": 1.0,
      "descriptors": {
        "alive_fraction": 0.531,
        "binary_fraction": 0.531,
        "bright_fraction": 0.531,
        "soft_mean": 0.0,
        "entropy": 0.0,
        "log1p_b0": 0.0,
        "log1p_b1": 0.0,
        "chi": 0.0,
        "bbox_fill": 0.0,
        "largest_component_fraction": 0.0,
        "radial_var": 0.0,
        "radial_peak_bin": 0,
        "radial_center_occupancy": 0.0,
        "symmetry_rot_centered": 0.0,
        "symmetry_reflect_centered": 0.0,
        "autocorr_lag1": 0.0,
        "autocorr_lag4": 0.0,
        "edge_fraction": 0.0
      },
      "class_alive_conflict": false
    }
  ],
  "aggregates": {
    "denominator": 832,
    "learned": 704,
    "controls": 128,
    "counts_by_class_all_runs": {
      "struct_1": 160,
      "death": 355,
      "uniform_dark": 189,
      "uniform_bright": 64,
      "struct_2": 64
    },
    "counts_by_class_learned_only": {
      "struct_1": 67,
      "death": 320,
      "uniform_dark": 189,
      "uniform_bright": 64,
      "struct_2": 64
    }
  },
  "predictions": [
    {
      "source_family": "WP4_R-9_s2000_seed101",
      "source_seed": 0,
      "target_family": "WP4_R-9_s2000_seed42",
      "target_noise_seed": 0,
      "predicted_class": "struct_2",
      "predicted_alive": true
    }
  ],
  "deviations": [
    {
      "what": "snapshot_every raised to 25",
      "why": "finer return-step resolution",
      "scope": "T2 and T4 only"
    }
  ],
  "known_anomalies": [
    {
      "seed": 1234,
      "what": "class label `struct_2` at alive_fraction 0.0002",
      "handled_as": "counted as death"
    }
  ],
  "environment": {
    "python": "<version>",
    "framework": "<name and version>",
    "gpu": "<model or 'none'>",
    "wall_seconds": 0
  }
}
```

Rules for the payload:

- `runs` must contain **one entry per seed in the denominator**. Missing seeds are scored
  as failures, not skipped.
- `descriptors` must contain all 18 features, even for dead fields (zeros are legitimate
  values there).
- `predictions` is required for T5 and must be produced **before** execution; the scorer
  checks the declared prediction against the executed outcome.
- `deviations` is mandatory if any constant in §2 changed. An undeclared deviation
  invalidates the submission for comparability.
- `known_anomalies` is where label-versus-liveness conflicts go; they are counted as
  death and reported, never silently re-labelled.

## 7. Scorer

The scorer is a deterministic script (to be written; this section is its contract).

1. **Validate** the payload against `schema_version` and the required keys. Reject on
   missing denominators.
2. **Recompute labels.** For every run: `z = (descriptor_vector − scaler_mean) /
   scaler_std`, then nearest frozen centroid. Never trust `declared_class`. Report both.
   A mismatch is a finding, not a crash: it usually means a descriptor implementation
   differs, which is exactly what T1 is for.
3. **Check the liveness rule.** Any verdict involving "alive" uses
   `alive_fraction ≥ 0.05`; label-based verdicts are recomputed and any
   `class_alive_conflict` row is counted as death.
4. **Score per task**, with the fixed denominators of §3 and the fixed constants of §2.
5. **Report a `score.json`** with: task, metric values, per-family breakdown, denominators,
   declared-versus-recomputed agreement, list of deviations, and a boolean
   `comparable: true|false` (false if `refit`, undeclared deviation, or missing seeds).
6. **Never aggregate away the classes.** The report always contains per-class counts. A
   summary that has only a single number is an invalid report.

Reference implementation intent: the in-repo verifiers (`e02b_verify.py`,
`e02b_verify_exploratory.py`) already do steps 2–3 for the census and for exploratory
artifacts, without trusting harness summary fields. The benchmark scorer should reuse
that behaviour rather than invent a second definition of "class".

## 8. Rules

1. **All seeds in the denominator.** Every seed that was run or planned is counted. No
   "valid seeds only", no outlier removal without a pre-declared rule.
2. **No cherry-picking.** Reporting the best of N repeats instead of the median/rate is a
   protocol violation; the scorer rejects a submission whose `runs` array is smaller than
   the declared denominator.
3. **Publish classes, not only aggregates.** Per-class counts and per-family breakdown are
   mandatory. "Score 0.87" alone is not a result.
4. **Failures are data.** Dead fields, collapsed runs and negative results are reported.
   Dropping them changes the denominator and therefore the score.
5. **Frozen definer.** Classes come from `class_centroids_frozen.json`. A refit is allowed
   as separate research and flagged `comparable: false`.
6. **Declare deviations before scoring**, with scope. Undeclared deviation = not
   comparable.
7. **Controls travel with results.** T4 without the dead-field control is not a result;
   `struct_1` repair without the untrained baseline is not attributable to learning.
8. **No claims beyond the protocol.** A score here measures reproduction of a census of
   held classes. It says nothing about life, mind, intelligence, agency or adaptation, and
   submissions may not frame it that way.
9. **One submission per implementation.** Re-submitting the same artifact with a different
   `submission_id` does not create a second data point.

## 9. What v0 cannot measure

- **Whether `struct_2` is a property of training or of a lucky seed.** That is
  H-E02C-1 and needs new training runs, which require owner sign-off. No amount of
  inference on frozen checkpoints answers it.
- **Whether local-rule variants matter more than seeds.** That is H4, never run.
- **Anything about stress, goals, agency, lifelong learning.** WP5 is closed; this
  benchmark has no task for it and will not grow one silently.
- **Generalisation across architectures.** One architecture, twelve checkpoints. A
  different NCA would need its own census and its own frozen definer.

## 10. Open questions for v1

1. Who executes the hidden range `128–191` first, and how is the answer key committed so
   that it cannot be regenerated after seeing submissions?
2. Should T2/T3 be merged — "reach and hold" is one question with two horizons — or kept
   separate so that a model can be good at one and bad at the other?
3. Is a rule-variant track (H4) worth adding, given that it requires training and
   therefore an owner decision each time?
4. Should the scorer accept a full re-implementation (different framework) directly, or
   require the reference forward pass bundled with the dataset? Current text assumes the
   latter for comparability, which limits what "independent implementation" means.

## Кратко по-русски

- **Что это.** Черновик спецификации бенчмарка «E02b Reproduction Benchmark v0»: пять
  задач (перепись, достижение класса, удержание, ремонт, предсказание пересадки),
  метрики с фиксированными знаменателями, четыре baseline, скрытый диапазон сидов
  `128–191`, формат submission JSON и контракт скорера.
- **Почему v0.** Нет внешних baseline, нет leaderboard, скрытый диапазон никто не
  запускал, на класс один тренировочный сид, скорер ещё не написан. Это контракт
  воспроизводимости, а не соревнование.
- **Правила.** Все сиды в знаменателе; без cherry-picking; публиковать счётчики по
  классам, а не только агрегат; провалы — тоже данные; классы считаются замороженными
  центроидами, а не самоотчётом; отклонения заявляются до скоринга.
- **Чего бенчмарк не измеряет.** Выученность `struct_2` (нужны новые тренировочные
  серии), H4 (не запускалась), стресс/агентность/lifelong (WP5 закрыт), обобщение на
  другие архитектуры.
- **Ссылки по линии метода:** Growing NCA (Distill 2020), 3D-NCA (ALIFE 2021),
  HyperNCA (2022), Lenia (2019), Flow-Lenia (2022/2023) — см.
  [`library/publications/README.md`](../../library/publications/README.md). Мотив задачи
  T5 — регенерация и память происхождения (Kragl et al., 2009; Levin, 2021), но эти
  работы задают вопрос, а не служат свидетельством о нашей модели.
