# Corpus audit — one question for 578 reports

<!-- report-format: observation -->
<!-- report-kind: audit -->

**Why this audit.** The reading says: throw out the tradition and find out whether these mechanisms actually
helped (P122); a result that contradicts the design is a finding about the design (P123); a null is a fact
about the world, not a failure of a mechanism (P105); and the file is an argument that reaches only the
conscious mind (P294). So the audit asks **one question of every experiment we ever ran**: **did it help the
cell, in the cell's own terms** — energy, survival, offspring — not "did it produce a difference".

**What this audit is not.** It is not a re-run. It reads the artifacts we already have and reports what they
say. Where an artifact does not carry the measure needed, the audit says so rather than estimating.

## 1. What we looked at

Every artifact in `morphogenesis/experiments/E09_pond/*.json` that contains per-arm results, and every report
in `reports/` that describes one. The question: **for each mechanism, did the arm that had it do better than
the arm that did not, in the cell's own measures?**

## 2. What we saw

<!-- audit:start -->

**Artifacts scanned:** 788

| category | count | what it means |
|---|---|---|
| A. record the cell's own measures | **300** | the audit can answer "did it help the cell" |
| B. record only the ranking metric | **0** | the audit CANNOT answer it — a ranking is blind to order |
| C. record neither | 20 | nothing to audit |

### A. Artifacts that can answer the question

| artifact | kind | rows |
|---|---|---|
| `adequacy_matrix.json` | adequacy_matrix | 15 |
| `catastrophe_diversity.json` | idh_reanalysis | 54 |
| `catastrophe_matrix.json` | None | 54 |
| `drift_matrix.json` | None | 18 |
| `founding_maps.json` | map_metrics | 50 |
| `founding_matrix.json` | founding_runs | 50 |
| `frequency_matrix.json` | None | 54 |
| `frequency_matrix_v2.json` | None | 60 |
| `frequency_start_control.json` | None | 20 |
| `generation_matrix.json` | generation_runs | 9 |
| `habitable_matrix.json` | habitable_matrix | 10 |
| `invader_death_matrix.json` | invader_death_runs | 20 |
| `invasion_matrix.json` | None | 12 |
| `kill_keep2_matrix.json` | kill_keep_runs | 10 |
| `kill_keep3_matrix.json` | kill_keep_runs | 10 |
| `kill_keep_matrix.json` | kill_keep_runs | 10 |
| `l2_matrix.json` | None | 30 |
| `merge_keep_matrix.json` | v8_placement_merge | 20 |
| `mobility_matrix.json` | None | 36 |
| `mutation_matrix.json` | mutation_runs | 15 |
| `organism_mobility_matrix.json` | None | 27 |
| `p0_baseline_long.json` | p0_flip_behavior_metric | 3 |
| `p0_cal1.json` | p0_flip_behavior_metric | 1 |
| `p0_cal10.json` | p0_flip_behavior_metric | 1 |
| `p0_cal11.json` | p0_flip_behavior_metric | 1 |
| `p0_cal12.json` | p0_flip_behavior_metric | 1 |
| `p0_cal2.json` | p0_flip_behavior_metric | 1 |
| `p0_cal3.json` | p0_flip_behavior_metric | 1 |
| `p0_cal4.json` | p0_flip_behavior_metric | 1 |
| `p0_cal5.json` | p0_flip_behavior_metric | 1 |
| `p0_cal6.json` | p0_flip_behavior_metric | 1 |
| `p0_cal8.json` | p0_flip_behavior_metric | 1 |
| `p0_cal8b.json` | p0_flip_behavior_metric | 3 |
| `p0_cal9.json` | p0_flip_behavior_metric | 1 |
| `p0_cal_0.046_0.046_b.json` | p0_flip_behavior_metric | 1 |
| `p0_cal_0.048_0.048_b.json` | p0_flip_behavior_metric | 1 |
| `p0_cal_0.048_0.052_b.json` | p0_flip_behavior_metric | 1 |
| `p0_cal_0.052_0.05_b.json` | p0_flip_behavior_metric | 1 |
| `p0_cal_0.05_0.048_b.json` | p0_flip_behavior_metric | 1 |
| `p0_cx_0.075_0.058.json` | p0_flip_behavior_metric | 1 |
| … and 260 more | | |

### B. Artifacts that cannot — they ranked cells and never measured a cell

0 artifacts carry only the favourable share or a trait mean. **Every conclusion drawn from them is a conclusion about a ranking, not about a cell.** That is the corpus-level version of P66 and P102.

<!-- audit:end -->

*(filled by `scripts/audit_corpus.py` — the table below is generated, not written by hand)*

## 3. What it means

**320 artifacts were classified and 471 were not read at all.** The 471 are matrices, Betti numbers, summaries
and configuration dumps: they have no `rows` array, so the scanner skips them silently. That is a defect of this
audit and it is stated here rather than hidden: **the corpus is 791 files and this audit speaks about 320 of
them.** A file that cannot be read is not evidence for or against anything, and counting it as "neither" would
have been worse than counting it as unread.

## 4. What we do not know

**The 20 artifacts in category C are not failures; they are the wrong shape.** They are matrices and
probes (`b2_matrix.json`, `colony_type_matrix.json`, `invader_dose_matrix.json`, `l1_field_betti.json` and
similar): they record a structure — a matrix, a Betti number, a state — and not a per-cell trajectory. The
question "did this help the cell" cannot be asked of them, because they do not contain cells. **They are useful
for a different question** (does the field have a topology at all), and mixing the two questions is what made the
first version of this audit look like a verdict on the corpus when it was a verdict on a file format.

## 5. What this changes in the next experiment

**What this audit does not establish.** It does not say that any mechanism helped. It says that **300
artifacts contain the cell's own measures**, which is the necessary condition for asking the question. The
sufficient condition — that the same mechanism was run with and without, on the same seeds, and the cell's own
measures differ — has not been checked for a single mechanism yet. **The next step is not another count; it is one
mechanism, two arms, the cell's own measures, and a paired comparison.**
