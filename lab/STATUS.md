# STATUS — canonical flow of attention

One file, one place that says what is actually in work. Machine state lives in `lab/state.json`, the log in
`_hourly/log.md`, numbers in artifacts. The Russian sections below the line are **history** and are not rewritten; the top
part is kept current (new text in English — decision of 31.10).

**Updated:** 2026-11-02, 08:15 MSK.

## Running now

- **X82** (since 08:12): the transfer function from prescribed to realised spectral share — five cells (prescribed power ratio
  0 / 1 / 4 / 16 at q = 11, and 4 at q = 14), five worlds each, ~40 minutes. Registered in
  `reports/2026-11-02-x82-reach-plan.md` before the run.
- Why it exists: three pilots showed the channel **saturates** (prescribed 1 → realised 0.19, 4 → 0.31, 16 → 0.28), which voids
  X80 (its three cells are spectrally near-identical) and would have voided X81 as registered. X81 is superseded by X82.
- Closed since the previous update: **X74** (half-life follows the inflow non-monotonically: 1.47 / 0.73 / 1.61 at 0.030 /
  0.035 / 0.040 — the multistable band remembers least), **X76** (the 0.033 cell is ordinary at ten worlds, so the five cells
  fall into two levels), **X77** (patch control has no power: a daughter's patch mean predicts her at 0.01, which excludes the
  common-environment reading by measurement), **X78** (void: the matched-scale arm collapsed to one component), **X78b** (an
  imposed second scale shortens the half-life 1.47 → 1.03 while lag-1 stays 0.498), **X79** (the mix sweep was confounded by
  its own construction: variance `(1−w)² + w²` is minimal at `w = 0.5`), **X80** (see below).

## Closed on 01.11 (field line)

| what | verdict | where |
|---|---|---|
| X58-lite grid 128 | **withdrawn**: the code has no `dx`, so 96→128 at `dt = 0.5` changed the domain, not the resolution | §10ed, `reports/2026-11-01-x58-lite-grid128-result.md` |
| X59 amplitude dose | divisions 308 → 79 → 21 at amp 0.5 / 0.25 / 0.1, factor 14.7, 5/5 worlds | §10ef |
| X60 field topology | β₁ excess +9.0 (10/10) at t = 2000, gone by 6000 | §10ea |
| X61l long horizon | the excess fades, no persistent selection | §10eg |
| X62 / X63 / X64 / X65 / X66 / X67 | correlation length, scale sweep, refinement, grid-120 bracket, full grid map, doubled box | §10eh–§10em |
| X68 identity rules | **replicated** on five real worlds: lifetime reversal 5/5 at loose overlap, 4/5 at medium, **5/5 the other way at strict** | §10en, `reports/2026-11-01-x68-identity-replicated.md` |
| X70 size heredity | **real, pair-specific, partial**: 0.42–0.57 over five real worlds, nearest-distance surrogate −0.003, partial 0.545 | §10ep, `reports/2026-11-01-x70-spatial-control-result.md` |
| method | a seed replicates nothing if the world ignores it (β = 0 geometry is seed-independent); gate `check_seed_replication.py` | `docs/design-checks.md` |
| hygiene | board 94/94 closed, CI green, three Linux-only gate defects fixed | `_hourly/log.md` |

## Closed on 02.11 (field line)

| what | verdict | where |
|---|---|---|
| X74 rate | half-life depends on the inflow **non-monotonically**: 1.47 / 0.73 / 1.61 at `F = 0.030 / 0.035 / 0.040`, lag-1 flat at 0.475–0.507 | §10ey |
| X75 edges | inconclusive by the registered rule: 0.037 shallow (0.56), 0.033 out of its control band | §10ez |
| X76 replication | the 0.033 cell is ordinary at ten worlds (ρ₁ 0.447), so the five cells are **two levels** | §10fa |
| X77 patch control | **void as a discriminator**: patch mean predicts a daughter at 0.01 (median patch = 2 structures) — the common-environment reading is excluded *by measurement* | §10fb |
| X78 causal | **void**: the matched-scale arm has one component per world, so the manipulation changed the regime, not the scale | §10fc |
| X78b two scales | imposed second scale shortens memory 1.47 → 1.03 (1.43×) while lag-1 stays 0.498; right direction, third of the band effect | §10fd |
| X79 mix sweep | confounded **by construction**: `Var(G) = (1−w)² + w²` is minimal at `w = 0.5`, so weight and amplitude moved together | §10fe |
| X80 dip test | **void by manipulation reach**: the registered rule fired slope, but measured as a power share all three cells carry a second peak of 0.18–0.34, so the sweep compared three near-identical spectra (the 0/5 two-peak figure was a local-maximum artefact and is withdrawn) | §10ff, `reports/2026-11-02-x80-correction-two-peak.md` |
| the ruler | **half-life is aggregation-dependent**: pooled and per-world median disagree in *sign* on X80 (0.86/1.18/1.25 against 1.04/0.52/1.16), and the band contrast is 2.01×/2.58× pooled but 1.37×/1.91× per-world median; at `F = 0.033` only 7 of 10 worlds are fittable | §10ff, claims 296–298 |

Note on X80's three numbers: they were measured on cells whose *realised* spectra differ by less than the noise (shares 0.27–0.31,
0.18–0.23, 0.27–0.34), so they are a statement about the composite at three weights, not a graded trend.

The estimator note is the one with teeth: every half-life we published (X74, X76, X78b, X79) is **pooled**, and pooling is a
choice that was never declared. The direction of the band survives it; the size does not.


## Waiting for the owner — only two items, both small

1. **X54, canonical weights:** the snapshot is honest now (`ready 1 / missing 11`, `weights_tracked: false`), but the choice
   remains: (a) restore the 12 `nca_final.pt` from Zenodo `10.5281/zenodo.23654174` (6.47 GB), or (b) record the local
   absence in `docs/deposit.md` and drop the 12-file requirement. Option (b) costs 15 minutes and unblocks the retention
   policy; option (a) is only needed if E02b is to be reproduced locally.
2. **v1.7 of article 028:** v1.6 was **published** on 31.10 at 23:45 (DOI `10.5281/zenodo.23844978`), so "inserts before
   upload" no longer exists as a category. Two things remain: the published files still call themselves v1.5.1 and link
   `23839898` (a two-line header fix), and the two prepared inserts (the count is a count of *small* components; lifetimes
   belong to the trait channel) would go into v1.7. Publication is outward-facing, so it is the owner's call; ~60 minutes.

## Queued compute, not waiting on anyone

- **the mixedness channel that actually reaches** (the open problem after X82): inflow modulation admits an imposed second scale
  only as a shoulder of about a third, so "two preferred scales of comparable strength" is not reachable through `hetero_G`. The
  candidates are (a) impose the second scale in the initial condition rather than in the inflow, (b) a second species with its own
  diffusion length, (c) a spatially varying `F` (X52's design) instead of a temporal-spectral one. Decide after X82's transfer
  function is in hand; do not build a heredity design on a channel with a 0.3 ceiling.
- **X58 at grid 192** (the real refinement): `Du = 0.64`, `Dv = 0.32`, `dt = 0.375` (stability `dt·Du = 0.24 ≤ 0.25`),
  16 000 steps, 10 runs, ~2 GPU-hours. Criterion: peak position at 12 units.
- **X57 stationarity:** one 30 000-unit arm at `dt = 1.0`, 10 seeds, ~2 GPU-hours.
- **X31 equivalence:** the rule is implemented in `claim_comparator.py`; the 60-seed series is missing, ~1 GPU-hour.
- **X29:** `scripts/field_eas.py` (Flow-Lenia meter) has never been run; the `x37_sel`/`x37_null` data are on disk. No GPU.
- **X35:** six published claim rows sit at `наблюдение` only because nobody matched their numbers to aggregates that already
  exist (`v8_matrix.json`, `frequency_start_control.json`, five `w2bud_*` manifests). One hour, no GPU.
- **X3:** the claims gate checks that an artifact exists, not that its value matches; add the expected-value column.
- **X69:** 15-seed dose confirmation, registered, paused (`reports/2026-11-01-x69-dose-15-seeds-plan.md`).

## No longer waiting (stale entries removed)

- **A (`freq_dep > 0`)** — the quota arm was approved, run and closed negative on 27.10 (§10bf: lineages with data 4.0 → 5.0 →
  4.0 against a target of ≥12, sign of the price flipped); the price magnitude was closed by §10bg/§10bh. Nothing waits.
- **Preprint v1.1/v1.2** — v1.2 has been live since 28.10 (`10.5281/zenodo.23733719`); only the optional arXiv endorsement
  step remains, and `_hourly/grants/ИНСТРУКЦИЯ-ОТПРАВКА.md` is out of date rather than blocking.
- **Provenance gaps** — of the 93 references to lost `_hourly/` artifacts, **66 exist one directory up** (the gate scans
  `repo/_hourly` only), 13 can be re-pointed to committed aggregates, 3 are filename drift, 11 are gone for good.

## Deliberately not doing (unchanged)

- New pilots on the same price construction (14 manoeuvres gave the answer: at most 9 lineages).
- A third explanation of the price magnitude (two were tested and withdrawn).
- Rewriting old series for cosmetics; re-running insensitive tests under new names.
- Editing `world/` or `config.py` while a series runs.
- Publishing anything outward without the owner's explicit "ok".

## Lessons that still bind (pointers)

| # | class | rule |
|---|---|---|
| 7 | a series taken across four code commits | the indicator is `git_code_commit`, not `git_dirty`; `check_series_homogeneity.py` |
| 8 | `print` into a closed pipe killed a run | the artifact is written **before** printing; the fix is checked by deliberately breaking it |
| 9 | a series mixed by parameters invisible in `config` | parameters come from the preregistration, not from the previous script |
| 10 | 01.11 | a seed is replication only if it changes the world — `docs/design-checks.md` |

## How to check the state

```bash
python scripts/lab.py validate      # contract
python scripts/claims_lint.py       # claims matrix: basis kind, assumptions, artifacts
make verify                         # everything, with per-step time budgets
python scripts/lab_health.py --full --github   # single entry point: gates, CI, queues, series, disk
```

---

# История (не переписывается)

## Что закрыто за ночь 26→27.10

1. **Единица размножения — четыре конструкции** (§4i, §10az/§10ba): колония **0/10**, пара «своей» метки **2/10**, пара
   «любых» меток **1/10**, клетка **10/10**. В первых трёх линия с данными одна, поэтому они помечены **«не оценивается»**,
   а не «отбора нет». Утверждение сузилось до **«ровно одна клетка»**; объяснение «порог в родстве внутри единицы»
   опровергнуто нашими же данными.
2. **Цена признака** (§4i, §10bd): знак устойчив (**8/8**, p = 0.0039), величина **не определена** (медиана −0.478, ДИ
   [−0.797, −0.177], порог −0.3 внутри). Причина — **ограничение конструкции**: 14 маневров дают максимум **9 линий**
   против нужных ≥12 (доминирующая линия занимает 69–90 %). Серия не запускалась — это записано как свойство мира.
3. **Отклик закрыт двумя величинами** (§10ax): независимая от `w` величина даёт медиану **0.018** (5/10), `ρ(признак, w)` —
   **+0.518** (8/10), знак совпадает в **3/10** ⇒ кажущийся отклик — свойство определения `w`.
4. **Наследование среды закрыто механизмом** (§4j, §10be): пересъёмка 20 прогонов **одним `git_code_commit`**
   (`248e01d`), фильтр «свободная компонента ≥15»: `legacy > adjacency_exact` в **5/10**, медиана **−0.0092**, p = 0.62.
   Остаток +0.12 → +0.014 → **−0.0092** исчез; место занимает тот, у кого больше живых 4-соседей (0.744 → 0.881).
   **Уточнение:** память среды при этом есть — избыток живёт 2–4 поколения; опровергнуто наследование **по линии**, а не
   память среды вообще.
5. **Перенос вне тел** (§4j.1, §10bb/§10bc): `k = 1 > k = 2` в **10/10** (p = 0.001), `k = 2` против `k = 8` — **6/10**,
   величина 1.765 против 12–50. Объяснение «геометрия усиливает отбор» проверено и **снято**.
6. **Препринт опубликован** (Zenodo, v1.0 `23669738`, v1.1 `23694918`, v1.2 `23733719`); статья 028 v1.6 —
   `23844978`.

## Уроки ночи (разборы — `docs/incidents.md` §7–9, правило — `AGENTS.md` §3c)

| # | класс | правило |
|---|---|---|
| 7 | серия снята на четырёх коммитах кода | индикатор — `git_code_commit`, а не `git_dirty`; гейт `check_series_homogeneity.py` + реестр `lab/homogeneity.json` |
| 8 | `print` в закрытый пайп убивал прогон (и PowerShell `*>>` — тоже пайп) | артефакт пишется **до** печати, `_safe_print` везде, фикс проверять **намеренной поломкой** |
| 9 | серия смешана по параметрам, невидимым в `config` | параметры берутся из **пре-регистрации исполнителя**, а не из прошлого скрипта; сверка на одном сиде до серии |

Плюс два собственных промаха ведущего, записанных явно: предсказание «+0.005…+0.02» для просторной зоны **не
подтвердилось** (−0.0092), потому что опиралось на отозванную серию; и 17 прогонов были запущены скопированным старым
`POND_ARGS` (три флага отсутствовали, а в `config` они не видны).

## Красное, которое оставлено осознанно (26.10)

- **Гейт «замечания библиотеки»: 1 замечание new висит больше дня.** Библиотекарь написал **58 новых разделов**
  (`library/answers.md`), из них прочитаны и разобраны три ключевых (§37, §38, §39). `library_inbox --ack` отказывается
  закрывать без `--force`, а ставить `--force`, не прочитав 55 разделов, — ровно то «зелёное, которое врёт», с чем мы
  воюем. *(На 01.11 доска 94/94 закрыта; строка оставлена как история правила.)*

## 29.10 — вечер: итог дня

**Закрыто:** E1, E1b (критерий индивидуации — пруд не проходит), E2 (абляция объекта — вывод устоял с границей), E3
(гистерезиса нет), E4 (связь даёт скорость, не прирост), E6a (критерий был неустойчив к сетке), E6b (пассивная примесь не
наследуется), X5 (вердикт E1 не зависит от фона).

**Не выжили три вывода:** преимущество инвазии, гистерезис, оптимум чувствительности.

**Два правила метода:** сравнивать на срезе 600 (CV 0.3), контраст против локального кольца.

**Осторожно:** срез 300 хаотичен (CV до 0.80). Любое число, взятое до 600 шагов, публиковать только с CV.
