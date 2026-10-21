---
pretty_name: E02b Morphospace Census — neural cellular automata checkpoints and runs
license: cc-by-4.0
language:
  - en
tags:
  - neural-cellular-automata
  - morphogenesis
  - attractor
  - cellular-automata
  - reproducibility
  - developmental-systems
task_categories:
  - other
size_categories:
  - n<1K
---

# Dataset Card — E02b Morphospace Census (v0, draft)

> **Status: DRAFT — not published, not uploaded.** This card describes an artifact set
> that is being assembled for possible release. Creating or editing this file does not
> publish anything. Release is blocked on (a) the portable export (`dist/e02b-portable`,
> produced by a separate task), (b) real checksums for the lite checkpoints, (c) owner
> sign-off on the licence, and (d) an explicit owner decision to publish. Nothing here may
> be read as a claim that a dataset is live at some URL.
>
> **Licence note.** `cc-by-4.0` in the front matter is the *proposed* licence for our own
> artifacts (weights we trained, measurements we produced). It is not a licence to
> redistribute third-party material, and it takes effect only at release.

## Dataset description

`E02b_morphospace` was a census of **what morphologies a trained neural cellular
automaton (NCA) holds when no target image is requested**. Twelve canonical checkpoints
(five `H-A0`, five `R-9`, one `R-11`, one `H-P1` positive control) plus one untrained
runtime control of the same architecture were rolled out from 64 deterministic noise
seeds for 2000 steps with frozen weights and no gradient: **832 rollouts** (704 learned,
128 control). Final states were described with 18 descriptors, z-normalised and clustered
(Ward, `k=5`, silhouette 0.8545; DBSCAN agreement ARI 0.9137). The released artifact set
is the numeric trace of that census plus the weights needed to reproduce it — the
consumers are the benchmark spec (`docs/benchmark/BENCHMARK_v0.md`) and the replication
work an outside group could do without training anything.

What the census found is documented in the repository report, not here: five classes,
two of them structured, one of the two (`struct_2`) reproducing from all 64 starts of a
single checkpoint and appearing in none of the 768 rollouts of the other eleven models.
Those are **properties of a frozen model under a fixed protocol**, not a claim about
organisms. See "Limitations" and "Ethics" below before using the word attractor in a
paper.

### Lineage of the method

The construction being exercised is the one introduced by
[Mordvintsev et al., 2020, *Growing Neural Cellular Automata*](https://doi.org/10.23915/distill.00023)
(the NCA trained to grow and repair a target pattern); the 3D extension is
[Sudhakaran et al., 2021](https://doi.org/10.1162/isal_a_00451) and the hypernetwork
variation is [Najarro et al., 2022](https://arxiv.org/abs/2204.11674). Continuous-state
precursors are [Chan, 2019, Lenia](https://doi.org/10.25088/ComplexSystems.28.3.251) and
[Plantec et al., Flow-Lenia](https://arxiv.org/abs/2212.07906). None of these works report
this census; the dataset is our own measurement, not a replication of theirs.

## Files

| Path | What | Size | SHA-256 |
| --- | --- | --- | --- |
| `census.json` | 832 rollouts: per-run final descriptor vector, 40-snapshot trajectory, dynamics class, cluster/class label, stability | 15.5 MB | `e81678b603ddc4def4b3c736a4ca0d9b99b2b0b234f666ef620bcae60cad0775` |
| `class_centroids_frozen.json` | frozen z-space centroids (5 × 18), scaler mean/std, class names, semantics, sizes; projection self-check | 7,310 B | `ef71d679a939a089cce6d550b5ea731861ede18161f1cf363972a955e892672d` |
| `perturbations.json` | 6 prototypes × 6 perturbations × 5 repeats = 180 outcomes; H3 verdict | 1.9 MB | `64a685acd3ea880b6a21a96518d2c5c6a27105b85177ce284c18d809b0b4125b` |
| `checkpoints/<family>/nca_final.pt` (lite) | 12 canonical checkpoints, inference-lite (model state dict + metadata + scalars) | ~0.145 MB each, ~1.7 MB total | **TBD** — filled at export time; full-file hashes below |
| `portable_manifest.json` | source commit, full and lite hashes, file list, license | TBD | TBD |

Checksums above were computed on the repository working tree on 2026-10-21. The lite
checkpoint hashes are deliberately left as `TBD`: they must be computed **by the export
step** and verified against the full-file hashes, not typed in by hand.

### Canonical full checkpoints (reference, not shipped)

The 12 canonical files are ~539 MB each and are **not** part of the release (weights are
not committed in the source repository either). They are listed so a third party can
verify that a lite file corresponds to the canonical full model:

| Family | Training seed | Steps | Full SHA-256 |
| --- | ---: | ---: | --- |
| `WP4_H-A0_s2000_seed42` | 42 | 2000 | `9a3983dd1c79…` |
| `WP4_H-A0_s2000_seed101` | 101 | 2000 | `65e88ee44136…` |
| `WP4_H-A0_s2000_seed202` | 202 | 2000 | `b0183298b1ee…` |
| `WP4_H-A0_s2000_seed303` | 303 | 2000 | `d08ab4534f85…` |
| `WP4_H-A0_s2000_seed404` | 404 | 2000 | `41ffaef86320…` |
| `WP4_R-9_s2000_seed42` | 42 | 2000 | `0aaba35763fb…` |
| `WP4_R-9_s2000_seed101` | 101 | 2000 | `f584511b54f8…` |
| `WP4_R-9_s2000_seed202` | 202 | 2000 | `6496bee63506…` |
| `WP4_R-9_s2000_seed303` | 303 | 2000 | `8770a423db1d…` |
| `WP4_R-9_s2000_seed404` | 404 | 2000 | `2b1ecfc01a21…` |
| `WP4_R-11_s2000_seed42` | 42 | 2000 | `28eaa7b7291e…` |
| `WP4_H-P1_s2000_seed42` | 42 | 2000 | `dc2c186ae1b0…` |

Truncated hashes are shown for readability; `lab/checkpoints.json` holds the full values.
Provenance of these files was audited separately: byte hash matches the index 12/12, the
`seed` inside each checkpoint matches its family 12/12, and the twelve weight sets are
pairwise distinct 12/12.

## Provenance

| Field | Value |
| --- | --- |
| Source repository | `Morphogenesis` lab stand (this repo) |
| Source commit at card draft | `cf16b068a0a07b4059508d357f9e57b0bda0f0bf` (the census closed earlier; use the run manifest below for the exact run) |
| Protocol document | `reports/2026-10-20-e02b-plan.md` |
| Protocol SHA-256 | `30c4312f6a34a5d062b3cb1c3ad6a066393036f6acc5e5d6226286a9947866a9` |
| Protocol frozen at commit | `24aefe4` |
| Protocol frozen on | 2026-10-20 (before the census run) |
| Run manifest | `lab/runs/20261020T195942Z-E02b_morphospace_census.json` |
| Seeds used | `0–63` inclusive, per checkpoint, all in the denominator |
| Steps / snapshot interval | 2000 / 50 |
| Device | CUDA; `total_seconds = 5070.2` (84 min 30 s) |
| Hypothesis pre-registration | H1–H4 in the protocol; H4 never run |
| Independent verifiers | `e02b_verify.py` and `e02b_verify_exploratory.py` re-derive the summary fields from per-run rows (0 errors, 0 warnings) |

Seeds `64–127` were used later in an **exploratory** held-out check (64/64 for both
structured classes) and are therefore *not* pristine for benchmarking. Seeds `128–191`
have never been run by this lab and are reserved as the hidden evaluation range in the
benchmark spec.

## Intended use

- **Replication without training.** Re-run the census protocol on the released lite
  checkpoints and compare per-run class labels against `census.json` through the frozen
  centroids. No GPU training is involved; the protocol is forward-only.
- **Benchmark baseline material.** The published numbers (per-class counts, recovery
  fractions, transplant outcomes) are the v0 baselines of
  `docs/benchmark/BENCHMARK_v0.md`.
- **Methodological study of class definitions.** The 18 descriptors, the `k=5` choice,
  the frozen centroids and the stability checks are all in the data, so a third party can
  test how much of the five-class taxonomy is an artifact of clustering choices. Our own
  sweep says `struct_2` survives `k = 3…8`, jackknife and 10 % feature noise, while the
  `death`/`uniform_dark` boundary does not survive dropping `alive_fraction` or
  `soft_mean`.
- **Teaching.** A small, fully documented example of pre-registered exploratory analysis
  including a case where the authors found and reported their own tooling bug.

## Limitations

Read these as part of the data, not as a disclaimer at the end.

1. **One training seed per class.** `struct_2` exists only at `R-9 seed42`; `struct_1`
   only at `R-9 seed101`. The census cannot separate "a property of the trained dynamics"
   from "a lucky trajectory of one training seed". Held-out noise seeds (64–127) remove
   the noise-seed objection but **not** the training-seed objection.
2. **`struct_1` is an architectural confound.** An untrained network of the same
   architecture lands in `struct_1` in 64/64 rollouts, three seeded untrained
   initialisations give 64/64, and the untrained model "repairs" after 20 % amputation in
   45/45 repeats. Any claim that learning produced `struct_1` is not supported by this
   dataset.
3. **H4 was never tested.** The secondary hypothesis (variance across local-rule variants
   exceeds variance across seeds) requires a separate grid of rule variants. `status =
   not_run`; this census does not substitute for it.
4. **WP5 was never opened.** Stress-as-uncertainty, agency and lifelong-learning
   questions are outside this dataset entirely. No field here supports them.
5. **A class label is not a vital sign.** The recovery metric is class identity over 18
   descriptors, not restoration of a cell configuration. Binary IoU between regrown and
   prototype patterns is 0.15–0.47, i.e. the global picture does **not** come back.
   A field with 1 live cell out of 4096 was labelled `struct_2`; verdicts that concern
   liveness use `alive_fraction ≥ 0.05` instead of the label.
6. **The five-class taxonomy is descriptive.** Bootstrap over the choice of `k` selects
   `k=5` in only 52 % of resamples. The stable object is `struct_2`, not the partition.
7. **Horizon is 2000 steps**, with one 6000-step check on 16 starts of a single
   checkpoint (16/16 stayed `struct_2`). Asymptotic stability is not established.
8. **One exploratory artifact carries a known tooling bug, and its corrected rerun now
   exists.** The 12-repeat geometric ablation was first run with the prototype built from
   a zeroed `stress_ema` (inverted "trained" flag in the model list), which changes the
   attractor instance: the binary masks differ on 2070 of 4096 cells. Its absolute IoU
   values are therefore **not** comparable with the earlier 3-repeat ablation; only
   within-run paired sign tests are valid. The corrected canonical run (H-AB-1, 216
   rollouts) was executed on 2026-10-21: left/right Δ = −0.336 (12/12) and top/bottom
   Δ = +0.184 (12/12), controls < 0.01. The old artifact is kept as history, not as the
   current result.
9. **Two other exploratory runs share the same flag bug** (channel memory, nucleogenesis).
   Channel-memory *comparisons between conditions within the run* are valid, but its
   absolute IoU is not comparable with canonical runs; the clean rerun is queued.
   Nucleogenesis *verdicts about wake-up* are robust; its "same picture" verdict, which
   depends on the non-canonical prototype, is not.
10. **`census.json` carries the author's absolute Windows checkpoint paths** (12 in
    `checkpoints[].path`, 12 in `timings[].path`, one `perturbations_path`). The verifier
    does not read them and they contain no credentials. **Resolved at export time
    (2026-10-21):** the canonical file is not rewritten; `scripts/export_portable.py`
    rewrites only path strings inside the repository to relative form (25 strings) and
    fails the build if any absolute path outside the repository remains. Numbers, class
    labels and descriptor vectors are untouched. `portable_manifest.json` records both
    hashes — `datasets.census.sha256` (packaged, sanitized) and
    `datasets.census.source_sha256` (canonical, `e81678b6…`) — plus
    `sanitized.absolute_paths_rewritten`. The Kaggle dataset remains private/draft.
11. **Protocol deviations are part of the record.** Amputation zeroes all 16 channels
    rather than only `alive` and `visible` (stronger than the protocol, making H3
    conservative). The protocol's patch-transplant test was degenerate (bounding box of
    both classes is the whole field), so growth claims rest on exploratory patches only.

## Ethics and scope

- **No biological material.** The released artifacts are synthetic model weights and
  numeric measurements. Nothing here involves animals, human tissue, or wet-lab work.
- **No claims of life, consciousness or intelligence.** The dataset reports a class of
  behaviour that a frozen model holds, and the boundary of that claim. Words such as
  "attractor" are used operationally (a basin of initial conditions and perturbations
  returning to the same descriptor class), never as a claim about organisms. Do not
  restate these results as evidence that a cellular automaton is alive, sentient or
  intelligent; the data cannot support it and the authors do not assert it.
- **Rehabilitation of a negative result.** The predecessor experiment (E02, the ring
  pattern) closed negatively and stays negative in this record. The dataset does not
  retroactively rescue it.
- **Known-bug transparency.** Artifacts produced with a known tooling bug are shipped
  with explicit caveats rather than removed, so that downstream users can reproduce the
  error and the correction.
- **No personal data.** Family names appear only as authors of cited literature.

## Citation

The dataset is not published; cite the repository report and this card as drafts.
Replace `morphogenesis-e02b-census-v0` and the version placeholder only at release time.

```bibtex
@misc{morphogenesis-e02b-census-v0,
  title        = {E02b Morphospace Census: neural cellular automata checkpoints and
                  rollouts (v0, draft)},
  author       = {{Morphogenesis Lab}},
  year         = {2026},
  howpublished = {Draft dataset card, Morphogenesis repository},
  note         = {Not published. Protocol SHA-256
                  30c4312f6a34a5d062b3cb1c3ad6a066393036f6acc5e5d6226286a9947866a9;
                  source commit cf16b06. License CC BY 4.0.}
}
```

Method citation for the NCA construction itself (independent of this dataset):

```bibtex
@article{mordvintsev2020growing,
  title   = {Growing Neural Cellular Automata},
  author  = {Mordvintsev, Alexander and Randazzo, Ettore and Niklasson, Eyvind
             and Levin, Michael},
  journal = {Distill},
  year    = {2020},
  volume  = {5},
  number  = {2},
  doi     = {10.23915/distill.00023}
}
```

## Maintenance

- Generated from the repository state at commit `cf16b06`; the census is closed and its
  protocol is frozen. Do not edit numbers in this card to match a new run — add a new
  version of the card and a new dataset version instead.
- Any change to the file list, hashes or license is a new version, not an edit.
- If the export step changes the lite format, the manifest hash changes and this card's
  `TBD` values must be filled from the export log, never from memory.

## Кратко по-русски

- **Что это.** Черновик карточки датасета по закрытой переписи E02b: 12 канонических
  NCA-чекпоинтов (inference-lite), `census.json` на 832 развёртки,
  `class_centroids_frozen.json` (5 × 18 замороженных центроидов), `perturbations.json`
  (180 исходов), манифест с коммитом и хешами.
- **Что не заявляется.** Ни «жизнь», ни «сознание», ни «интеллект». «Аттрактор» —
  операциональный термин: бассейн начальных условий и возмущений, возвращающийся в
  тот же класс дескрипторов.
- **Главные ограничения.** Один тренировочный сид на класс; `struct_1` — архитектурный
  конфаунд (необученная сеть даёт его 64/64 и «ремонтирует» 45/45); H4 не проверялась;
  WP5 не открывался; метка класса — не признак жизни; горизонт 2000 шагов.
- **Честность.** Один exploratory-артефакт собран с ошибкой инструмента (обнулённая
  `stress_ema`) и включён с оговоркой, а не удалён.
- **Статус.** Не опубликовано и не загружено. Хеши lite-чекпоинтов — `TBD` до экспорта;
  релиз — только по решению владельца.
