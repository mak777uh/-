# Index of every script

**Generated file — do not edit by hand.** Regenerate with `python scripts/make_scripts_index.py --write`; the gate `check_script_index.py` fails when this file is stale.

The curated page — what matters and why — is [`scripts.md`](scripts.md). This file is the complete list, so that every command behind a number in the record can be found.

Scripts: **198**.

## Гейты и проверки (42)

| script | what it does (first line of its docstring) |
| --- | --- |
| `check_agents_size.py` | check_agents_size.py — контракт обязан влезать в бюджет загрузки. |
| `check_aggregate_claims.py` | check_aggregate_claims.py — каждый агрегат обязан говорить, чего он НЕ утверждает. |
| `check_aggregate_coverage.py` | check_aggregate_coverage.py — каждый научный артефакт обязан входить хотя бы в один агрегат. |
| `check_aggregates_fresh.py` | check_aggregates_fresh.py — агрегаты в git обязаны совпадать с пересборкой. |
| `check_article_numbers.py` | check_article_numbers.py — числа статьи 028 обязаны воспроизводиться из агрегатов. |
| `check_commit_claims.py` | check_commit_claims.py — сообщение коммита не должно утверждать того, чего нет в диффе. |
| `check_cross_audit.py` | check_cross_audit.py — аудиты обязаны быть помечены как внешние утверждения. |
| `check_design.py` | check_design.py — пять проверок дизайна ДО серии. Гейт против нашего главного провала. |
| `check_determinism.py` | check_determinism.py — эталон для новой ветки кода: два прогона с одним конфигом и сидом. |
| `check_draft_numbers.py` | check_draft_numbers.py — числа в тексте статьи обязаны совпадать с агрегатами. |
| `check_empty_aggregates.py` | check_empty_aggregates.py — агрегат с нулём строк при живых данных — ошибка, а не результат. |
| `check_environment_assumptions.py` | check_environment_assumptions.py — гейты не должны зависеть от календаря и концов строк. |
| `check_external_content.py` | check_external_content.py — секреты и попытки инъекции во внешнем контенте, попавшем в репозиторий. |
| `check_hourly_refs.py` | check_hourly_refs.py — audits references to `_hourly/` artifacts, and says which no longer exist. |
| `check_lean_integrity.py` | check_lean_integrity.py — целостность формальных артефактов без запуска Lean. |
| `check_links.py` | Проверить относительные ссылки в markdown-файлах репозитория. |
| `check_metric_definitions.py` | check_metric_definitions.py — реализация метрики обязана совпадать с её определением. |
| `check_mutual_information.py` | check_mutual_information.py — калибровка оценки взаимной информации на данных с ИЗВЕСТНЫМ ответом. |
| `check_plan_split.py` | check_plan_split.py — план разложен по файлам без потерь и без дублей. |
| `check_readme_commands.py` | check_readme_commands.py — команды из README должны запускаться в CI, а не только существовать. |
| `check_readme_fresh.py` | check_readme_fresh.py — витрина не должна отставать от результатов. |
| `check_references.py` | Проверить, что каждая ссылка из References рукописи есть в индексе библиотеки. |
| `check_reports_index.py` | Проверить, что каждый отчёт попал в индекс `reports/README.md`. |
| `check_reviews.py` | check_reviews.py — ревью рецензента обязаны быть проверками, а не мнениями. |
| `check_script_index.py` | check_script_index.py — индекс всех скриптов обязан быть полным и свежим. |
| `check_scripts.py` | P2: какие скрипты никто не вызывает — профилактика мёртвого кода. |
| `check_section_refs.py` | Проверить внутренние ссылки на разделы (`§4.7`, `§5.6`) в рукописи. |
| `check_seed_dispersion.py` | check_seed_dispersion.py — если разброс по сидам велик, агрегат обязан это признать. |
| `check_series_followthrough.py` | check_series_followthrough.py — серия закончилась, а агрегат не собран? |
| `check_series_homogeneity.py` | Гейт: серия должна быть снята одним кодом. |
| `check_single_spec.py` | check_single_spec.py — не должно быть двух документов, объявляющих одну версию требований. |
| `check_snapshots.py` | check_snapshots.py — снимки лабораторного состояния обязаны совпадать с диском. |
| `check_wilson_consistency.py` | check_wilson_consistency.py — все реализации интервала Уилсона должны давать одно и то же. |
| `claims_lint.py` | Линтер матрицы утверждений (manuscript/CLAIMS.md). |
| `lean_check.py` | Проверка формальных гипотез: компилирует formal/*.lean и ведёт инвентарь. |
| `validate_runs.py` | Валидатор машиночитаемых артефактов прогонов (схемы v1.1.0). |
| `verify_e02c_numbers.py` | Пересчёт опубликованных чисел E02c из артефактов, лежащих в репозитории. |
| `verify_manuscript_numbers.py` | Сверить числа §4.12–§4.14 рукописи с артефактами. |
| `verify_portable.py` | verify_portable.py — проверка portable-пакета E02b (smoke \| full). |
| `verify_portable_package.py` | Проверка целостности портативного пакета E02b против его манифеста. |
| `verify_references.py` | verify_references.py — проверить ссылку по названию, не доверяя памяти и не имея веб-поиска. |
| `verify_sections_numbers.py` | verify_sections_numbers.py — числа в рукописи обязаны воспроизводиться из агрегатов. |

## Лабораторный контур (18)

| script | what it does (first line of its docstring) |
| --- | --- |
| `ci_canary_pond.py` | Канарейка для GitHub Actions: маленький прогон пруда на чужой машине (CPU). |
| `ci_receipt.py` | Квитанция воспроизведения: чем именно проверялся репозиторий. |
| `cycle.py` | Один экран состояния цикла: вместо чтения девяти файлов руками. |
| `cycle_audit.py` | Проверка, что цикл движется всеми тремя ногами, а не только прогонами. |
| `export_portable.py` | export_portable.py — собрать portable inference-пакет E02b без обучения. |
| `export_train_repro.py` | export_train_repro.py — собрать пакет для независимого воспроизведения обучения E02c. |
| `insight.py` | Инсайт → действие: учёт того, что прочитанное сразу встроено в работу. |
| `lab.py` | lab.py — машинный control plane лаборатории Morphogenesis. |
| `lab_health.py` | lab_health.py — одна команда, которая отвечает: «лаборатория здорова? что делать сейчас?» |
| `notices_status.py` | Статус запросов в lab/notices.md: что отправлено, что висит, что закрыто. |
| `pool.py` | Пул отложенного: идеи, снятые с плана, но не выброшенные. |
| `preflight.py` | preflight.py — предполётная проверка перед запуском серии. |
| `queue_runner.py` | queue_runner.py — очередь экспериментов как конвейер: порядок по импакту, запуск по готовности. |
| `retention_sweep.py` | Уборка локальных весов по правилу AGENTS §5a. |
| `triage_queue.py` | Триаж очереди: оставить работающее, остальное — в пул с условием возврата. |
| `wake_plan.py` | Когда будить ведущего: вместо «каждый час» — по состоянию работы. |
| `zenodo_link.py` | zenodo_link.py — вставить DOI депозита во все места репозитория одной командой. |
| `zenodo_upload.py` | zenodo_upload.py — депозит новой версии в Zenodo одной командой (без ручной загрузки в браузере). |

## Библиотека и литература (13)

| script | what it does (first line of its docstring) |
| --- | --- |
| `lib_cycle.py` | Цикл библиотеки: состояние, выбор следующей полезной работы, учёт. |
| `library_brief.py` | Задание библиотекарю: собирается из текущего состояния работы, а не пишется руками. |
| `library_cycle_log.py` | Лог работы библиотекаря по циклу волны. |
| `library_digest.py` | Дайджест библиотеки: что прочитано, что цитируется, что лежит мёртвым грузом. |
| `library_inbox.py` | Входящие библиотеки: что появилось и что я ещё не прочитал. |
| `library_wake.py` | Пробуждение библиотекаря по событию, а не только по календарю. |
| `lit_audit.py` | Аудит DOI в библиотеке: резолвятся ли и совпадает ли название. |
| `lit_board.py` | Доска литературы: замечания к текущей работе. |
| `lit_check.py` | Очередь проверок литературы: срабатывает на «нам нужен параметр/механизм X». |
| `lit_duty.py` | Обязательный шаг литературы в каждом цикле. |
| `lit_index.py` | lit_index.py — локальный поисковик по полным текстам статей. |
| `lit_pressure.py` | Литдавление: нужен ли литературный слот прямо сейчас (триггер вместо календаря). |
| `lit_search.py` | Поиск свежих публикаций по открытым вопросам библиотеки. |

## Линия поля (11)

| script | what it does (first line of its docstring) |
| --- | --- |
| `adequacy_mi.py` | adequacy_mi.py — адекватность: числа статьи 028 §4b из артефактов, с названной командой. |
| `field_eas.py` | field_eas.py — две дороги сразу: дифференциал отбора (X37) и накопление новизны (X39). |
| `field_inherit.py` | field_inherit.py — L3 в поле: наследуемый состав, который влияет на рост. |
| `field_lab.py` | field_lab.py — непрерывное поле вместо клеток: пятна, которые делятся сами (Грей–Скотт). |
| `field_lifetimes.py` | field_lifetimes.py — времена жизни структур: числа статьи 028 §4.9 из артефактов. |
| `field_track.py` | field_track.py — L3 в поле: отслеживание компонент и наследование состава. |
| `field_types.py` | field_types.py — два типа структур и скорость роста редкого (правильный прибор для сосуществования). |
| `ghost_control.py` | ghost_control.py — X50: блокирует ли «призрак» предиктивную зависимость. |
| `individuality.py` | Информационная индивидуальность: I(S(t); S(t+1)) с контролем на тривиальность. |
| `individuation.py` | individuation.py — критерий индивидуации из `reports/2026-10-29-individuation-criterion-plan.md`. |
| `te_anticipation.py` | te_anticipation.py — упреждение через УСЛОВНУЮ передачу энтропии, а не через разности. |

## Пруд и W1 (32)

| script | what it does (first line of its docstring) |
| --- | --- |
| `census_curve.py` | Кривая «класс от длины роллаута» для одного или нескольких чекпоинтов. |
| `colony_matrix.py` | Собрать colony_type_matrix.json из артефактов дизайна 3 (инвазия новой колонии). |
| `fisher_meta.py` | fisher_meta.py — критерий на среднем по Фишеру для серии one-bud (H-ALIVE-53). |
| `generation_matrix.py` | generation_matrix.py — длина поколения на плечах, где измерен полураспад наследия. |
| `idh_diversity.py` | idh_diversity.py — реанализ катастрофической серии на разнообразие (IDH). |
| `invader_death_matrix.py` | invader_death_matrix.py — режим гибели инвайдера: рывком или постепенно. |
| `invader_dose_matrix.py` | invader_dose_matrix.py — агрегат серии D (доза основателя, B-037/H73). |
| `kill_keep_matrix.py` | kill_keep_matrix.py — агрегат достаточности условия C (kill-and-keep против clean). |
| `kill_keep_probe.py` | kill_keep_probe.py — достаточность условия C: kill-and-keep против kill-and-clean. |
| `map_metrics.py` | map_metrics.py — метрики формы по финальной карте живого (Betti, rugosity, плотность). |
| `metrics_registry.py` | metrics_registry.py — величины агрегатов обязаны быть объявлены с формулой и знаменателем. |
| `morphometry.py` | Морфометрия маски живости: периметр, размерность границы, случайная маска. |
| `mspd.py` | MSPD: расхождение локальных законов перехода в разных временных окнах. |
| `mutation_matrix.py` | mutation_matrix.py — агрегат серии B (мутация метки линии, условие B). |
| `phase_matrix.py` | phase_matrix.py — фазовая развёртка majority: сколько шагов живёт инвайдер до переписывания. |
| `placement_matrix.py` | placement_matrix.py — V1c: гарантированная подсадка (H-ALIVE-37). |
| `pond_probe_adequacy.py` | pond_probe_adequacy.py — X33: несёт ли состояние организма информацию о БУДУЩЕМ среды. |
| `pond_series_matrix.py` | pond_series_matrix.py — агрегаты серий пруда (habitable, adequacy) с корректными путями. |
| `r1_matrix.py` | r1_matrix.py — агрегат мира `R1` (репликаторы без тела, H-ALIVE-50). |
| `rhythmicity.py` | Ритмичность β и доминирующий период по логу активности пруда. |
| `run_seed_grid_censuses.py` | Запустить переписи второй волны H-E02C-6 и собрать сетку. |
| `selection_matrix.py` | selection_matrix.py — условие E: отбор по наследуемому признаку. |
| `signature_curve.py` | Кривая подписи: (компоненты, полости, плотность) как функция горизонта обучения. |
| `simple_world.py` | simple_world.py — минимальный мир БЕЗ NCA: проверка, свойство ли это среды или нашей клетки. |
| `trait_metrics.py` | trait_metrics.py — метрики условия B по артефактам серии (производственный путь). |
| `w1niche_free_matrix.py` | w1niche_free_matrix.py — агрегат серии «наследование вне плотной зоны» (H-ALIVE-52). |
| `w1niche_matrix.py` | w1niche_matrix.py — W1-niche: наследование среды или зона смерти (H-ALIVE-46). |
| `w2bud_killwinner_matrix.py` | w2bud_killwinner_matrix.py — агрегат серий kill-the-winner (H-ALIVE-54/55). |
| `w2bud_lines_matrix.py` | Агрегат серии пилотов `w2bud_lines` — поиск маневра, дающего ≥12 линий с данными. |
| `w2bud_matrix.py` | w2bud_matrix.py — агрегат W2-bud (клеточное почкование) против W1 (колониальное). |
| `w2bud_metric_variants.py` | w2bud_metric_variants.py — инвариантность эффекта к устройству метрики. |
| `w2bud_quota_matrix.py` | w2bud_quota_matrix.py — агрегат серии с квотой (H-ALIVE-53). |

## Сборка отчётов и таблиц (13)

| script | what it does (first line of its docstring) |
| --- | --- |
| `aggregate_check.py` | aggregate_check.py — сверка агрегатов с артефактами и внутренняя согласованность. |
| `make_artifact_table.py` | Собрать приложение-таблицу артефактов с хешами (manuscript/SUPPLEMENT.md). |
| `make_arxiv_figures.py` | make_arxiv_figures.py — четыре фигуры для черновика (26.10). |
| `make_carrier_figures.py` | Собрать два рисунка по закрытиям carriers/кластеров из сырых артефактов. |
| `make_day2_picture.py` | make_day2_picture.py — картинка «что мы изучаем и как оно себя ведёт», простым языком. |
| `make_day_poster.py` | Постер «сутки лаборатории» для владельца (версия 2, после ночных серий). |
| `make_ledger.py` | make_ledger.py — журнал экспериментов в README: id и статусы генерируются, не правятся руками. |
| `make_logs_bundle.py` | make_logs_bundle.py — собрать «логи вместе со статьёй» в один проверяемый архив. |
| `make_periodic_stream.py` | make_periodic_stream.py — ряд притока с предсказуемым периодом (X41: мир, который предъявляет требования). |
| `make_schedule_stream.py` | make_schedule_stream.py — кодирует расписание темпа в значения потока. |
| `make_scripts_index.py` | make_scripts_index.py — автогенерируемый индекс всех скриптов. |
| `make_seed_grid_figure.py` | Собрать Figure 4 рукописи: сетка «инициализация × порядок данных» (§4.13). |
| `make_simple_poster.py` | Простой постер для владельца: что мы узнали, без терминов. |

## Прочее (69)

| script | what it does (first line of its docstring) |
| --- | --- |
| `additivity_interaction.py` | additivity_interaction.py — взаимодействие двух механизмов на парных сидах. |
| `analyse_e3.py` | analyse_e3.py — сходятся ли три пути после того, как история закончилась. |
| `analyse_e3_state.py` | analyse_e3_state.py — сравнение по СОСТОЯНИЮ, а не по времени. |
| `analysis_task.py` | analysis_task.py — ферма CPU-задач на GitHub Actions: берёт задачу из очереди и считает. |
| `analyze_grid_failures.py` | Какие шумовые старты не дают доминирующий класс в клетках сетки H-E02C-6. |
| `backfill_not_claimed.py` | backfill_not_claimed.py — дописать `not_claimed` в старые агрегаты. |
| `cadence_match.py` | cadence_match.py — is the `dt` dependence of the contrast a snapshot-cadence artefact? |
| `calibrate_thresholds.py` | Откалибровать и заморозить пороги OOD и тривиальности (протокол v1.2 §6b, §7). |
| `capture_stream.py` | capture_stream.py — запись настоящего потока из мира в артефакт. |
| `claim_audit.py` | Проверить пакеты доказательств в library/claims-evidence.md. |
| `claim_comparator.py` | claim_comparator.py — независимый аудит утверждения против его Setup (перенос идеи LongTails). |
| `coexistence_metrics.py` | coexistence_metrics.py — метрики сосуществования линий из СУЩЕСТВУЮЩИХ артефактов (0 GPU). |
| `compare.py` | Второй фильтр сравнения: не одно число, а распределение по сидам (B-008, I-014). |
| `contrast_stationarity.py` | contrast_stationarity.py — стационарен ли контраст «неоднородность минус однородность». |
| `corpus_manifest.py` | corpus_manifest.py — манифест корпуса: что в нём, зачем и насколько прочитано. |
| `e02c_seed_grid.py` | Собрать 2×2-сетку «инициализация × порядок данных» и применить критерий H-E02C-6. |
| `e6p_analyse.py` | e6p_analyse.py — three selection regimes: does the survival channel drift, and does frequency dependence hold diversity? |
| `e6p_series.py` | e6p_series.py — E6p: three selection regimes in the field, artifacts inside git. |
| `e6q_analyse.py` | e6q_analyse.py — did removing the niches collapse coexistence? |
| `e6q_series.py` | e6q_series.py — E6q: turn the niches off. |
| `entrainment.py` | entrainment.py — захватывает ли мир ритм входного потока (энтрейнмент), и связано ли это с «энергией». |
| `farm_reader.py` | farm_reader.py — читать результаты фермы GitHub Actions. |
| `founding_matrix.py` | founding_matrix.py — агрегат серии «порог основания» (H-ALIVE-23 / V10). |
| `index_report.py` | index_report.py — add a report row to reports/README.md, or check which reports lack one. |
| `l1_field_matrix.py` | l1_field_matrix.py — агрегат линии поля: медианы, разброс и интервалы по плечам. |
| `lean_axioms.py` | lean_axioms.py — независимая проверка теорем Lean на «чистоту аксиом» и неизменность формулировок. |
| `literature_harvest.py` | literature_harvest.py — собрать настоящие работы по теме, с аннотациями и ссылками на полные тексты. |
| `log_signal_scan.py` | log_signal_scan.py — майнер логов прогонов (LDD): какие сбои повторяются. |
| `metric_variants.py` | metric_variants.py — инвариантность вывода к устройству метрики (H-ALIVE-39). |
| `neutral_yardstick.py` | neutral_yardstick.py — нейтральная линейка для наших миров. |
| `paired_compare.py` | paired_compare.py — парное сравнение двух плеч по сидам, без «средних по плечу». |
| `periodicity.py` | periodicity.py — есть ли у мира СВОЙ ритм, и синхронизирован ли он с петлёй. |
| `predictions.py` | predictions.py — реестр предсказаний: что мы обещали до данных и что вышло. |
| `probe_invasion_state.py` | probe_invasion_state.py — проба пути инъекции: где и когда исчезает инвайдер (§10at.1). |
| `reciprocity.py` | reciprocity.py — двусторонняя связь потока и мира: считается ОБА направления передачи. |
| `response_independent.py` | Отклик признака, проверенный величиной, независимой от `w`. |
| `result_scan.py` | Сканер результатов: переходы берутся из данных, а не из таймера. |
| `rotate_notices.py` | Ротация доски notices.md: текущее — на доске, история — в архив. |
| `run_replicator.py` | replicator.py — мир `R1`: репликаторы БЕЗ тела (H-ALIVE-50). |
| `runs_chain.py` | runs_chain.py — печать целостности манифестов прогонов (наш аналог аттестации TEE). |
| `safe_commit.py` | safe_commit.py — коммит только при зелёном verify. |
| `self_review.py` | Дневной самоаудит библиотеки: что сработало, что нет, что поправить. |
| `size_resolved_contrast.py` | size_resolved_contrast.py — what size are the structures that make the contrast? |
| `slim_checkpoint.py` | Облегчить чекпоинт для инференса: только веса правила + метаданные. |
| `smc_interval.py` | smc_interval.py — интервалы вместо счёта «N из M». |
| `split_world_design.py` | split_world_design.py — разложить план линии по файлам, оставив индекс. |
| `stream_profile.py` | stream_profile.py — измеряет профиль живых источников, а не угадывает «какой лучше». |
| `stream_sources.py` | stream_sources.py — источники живого сигнала извне для цифрового мира. |
| `test_lib_tools.py` | Регрессионные тесты инструментов библиотеки. |
| `v8_matrix.py` | v8_matrix.py — агрегат серии V8 (размещение инокулята × правило слияния). |
| `verify.py` | Единый гейт перед отправкой: `python scripts/verify.py` (или `make verify`). |
| `x56_matrix.py` | x56_matrix.py — сходимость по шагу: контраст при dt = 1.0, 0.5, 2.0. |
| `x58_analyse.py` | x58_analyse.py — the same measurement on a 128 grid: β₀, β₁, wavelength, normalised count. |
| `x58_series.py` | x60_series.py — X60: the twenty field runs that keep their snapshots. |
| `x59_analyse.py` | x59_analyse.py — amplitude dose-response: does transmission fall as the inflow smooths? |
| `x59_series.py` | x59_series.py — X59: is transmission a dose-response in the inflow amplitude? |
| `x60_analyse.py` | x60_analyse.py — what the kept fields say: β₀, β₁, wavelength, normalised count. |
| `x60_series.py` | x60_series.py — X60: the twenty field runs that keep their snapshots. |
| `x61l_analyse.py` | x61l_analyse.py — four snapshots of a longer world: does the concentration grow? |
| `x61l_series.py` | x61l_series.py — X61-long: is the late concentration selection starting, or a drift? |
| `x62_analyse.py` | x62_analyse.py — correlation length against turnover. |
| `x62_series.py` | x62_series.py — X62: does the correlation length of the inflow control turnover? |
| `x63_analyse.py` | x63_analyse.py — the correlation-length profile: is there an interior maximum? |
| `x63_series.py` | x63_series.py — X63: four more correlation lengths, to turn X62's three points into a profile. |
| `x64_analyse.py` | x64_analyse.py — did the refinement preserve the physical wavelength? |
| `x64_series.py` | x64_series.py — X64: a real refinement (grid 144, dt 0.5, Du scaled by 1/dx^2 AND dt scaled with it). |
| `x65_analyse.py` | x65_analyse.py — the grid-120 bracket: does the heterogeneous arm select at 15 cells per period? |
| `x65_series.py` | x65_series.py — X65: bracket the grid transition at 120 cells (15 cells per pattern period). |
| `x66_series.py` | x66_series.py — X66: the grid map with the time step held fixed. |
