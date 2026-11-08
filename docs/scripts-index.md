# Index of every script

**Generated file — do not edit by hand.** Regenerate with `python scripts/make_scripts_index.py --write`; the gate `check_script_index.py` fails when this file is stale.

The curated page — what matters and why — is [`scripts.md`](scripts.md). This file is the complete list, so that every command behind a number in the record can be found.

Scripts: **505**.

## Гейты и проверки (65)

| script | what it does (first line of its docstring) |
| --- | --- |
| `check_agents_size.py` | check_agents_size.py — контракт обязан влезать в бюджет загрузки. |
| `check_aggregate_claims.py` | check_aggregate_claims.py — каждый агрегат обязан говорить, чего он НЕ утверждает. |
| `check_aggregate_coverage.py` | check_aggregate_coverage.py — каждый научный артефакт обязан входить хотя бы в один агрегат. |
| `check_aggregates_fresh.py` | check_aggregates_fresh.py — агрегаты в git обязаны совпадать с пересборкой. |
| `check_article_029_numbers.py` | check_article_029_numbers.py — every number printed in article 029 must trace to an aggregate. |
| `check_article_030_numbers.py` | check_article_030_numbers.py — every number printed in article 030 must trace to an aggregate. |
| `check_article_031_numbers.py` | check_article_031_numbers.py — every headline number in article 031 must trace to an artifact. |
| `check_article_032_numbers.py` | Verify the headline numbers of article 032 against the committed artifacts. |
| `check_article_033_numbers.py` | Verify the headline numbers of article 033 v3.0 against the committed artifacts. |
| `check_article_034_numbers.py` | Verify the headline numbers of article 034 against the committed artifact. |
| `check_article_035_numbers.py` | Verify the headline numbers of article 035 against the committed artifact. |
| `check_article_036_numbers.py` | Number gate for article 036: every number in the text is produced by a command that must succeed. |
| `check_article_037_numbers.py` | Number gate for article 037: every count in the manifesto is produced by a command. |
| `check_article_numbers.py` | check_article_numbers.py — числа статьи 028 обязаны воспроизводиться из агрегатов. |
| `check_autonomy.py` | check_autonomy.py — the autonomy policy has to be machine-readable, and its protected paths have to be enforced. |
| `check_claim_artifacts.py` | check_claim_artifacts.py — an artifact cited by a claim must exist in git. |
| `check_commit_claims.py` | check_commit_claims.py — сообщение коммита не должно утверждать того, чего нет в диффе. |
| `check_config_completeness.py` | Gate: the artifact must be able to reconstruct the world. |
| `check_cross_audit.py` | check_cross_audit.py — аудиты обязаны быть помечены как внешние утверждения. |
| `check_design.py` | check_design.py — пять проверок дизайна ДО серии. Гейт против нашего главного провала. |
| `check_determinism.py` | check_determinism.py — эталон для новой ветки кода: два прогона с одним конфигом и сидом. |
| `check_draft_numbers.py` | check_draft_numbers.py — числа в тексте статьи обязаны совпадать с агрегатами. |
| `check_empty_aggregates.py` | check_empty_aggregates.py — агрегат с нулём строк при живых данных — ошибка, а не результат. |
| `check_environment_assumptions.py` | check_environment_assumptions.py — гейты не должны зависеть от календаря и концов строк. |
| `check_experiment_manifest.py` | Gate: an experiment may not run without a manifest that passes the standing rules. |
| `check_external_content.py` | check_external_content.py — секреты и попытки инъекции во внешнем контенте, попавшем в репозиторий. |
| `check_field_analyses.py` | check_field_analyses.py — the field line's aggregates must re-derive from the stored artifacts. |
| `check_hourly_refs.py` | check_hourly_refs.py — audits references to `_hourly/` artifacts, and says which no longer exist. |
| `check_lean_integrity.py` | check_lean_integrity.py — целостность формальных артефактов без запуска Lean. |
| `check_links.py` | Проверить относительные ссылки в markdown-файлах репозитория. |
| `check_metric_definitions.py` | check_metric_definitions.py — реализация метрики обязана совпадать с её определением. |
| `check_mutual_information.py` | check_mutual_information.py — калибровка оценки взаимной информации на данных с ИЗВЕСТНЫМ ответом. |
| `check_plan_split.py` | check_plan_split.py — план разложен по файлам без потерь и без дублей. |
| `check_protected_staged.py` | Gate: a protected path may not change without a decision-log entry. |
| `check_readme_commands.py` | check_readme_commands.py — команды из README должны запускаться в CI, а не только существовать. |
| `check_readme_fresh.py` | check_readme_fresh.py — витрина не должна отставать от результатов. |
| `check_references.py` | Проверить, что каждая ссылка из References рукописи есть в индексе библиотеки. |
| `check_report_style.py` | Gate: a report written after 08.11 must be an observation, not an argument. |
| `check_reports_index.py` | Проверить, что каждый отчёт попал в индекс `reports/README.md`. |
| `check_result_map_coverage.py` | Which experiment artifacts are NOT covered by any claim in library/result-map.json? |
| `check_reviews.py` | check_reviews.py — ревью рецензента обязаны быть проверками, а не мнениями. |
| `check_run_manifest_gate.py` | Gate: every run manifest must carry a policy_gate record. |
| `check_script_index.py` | check_script_index.py — индекс всех скриптов обязан быть полным и свежим. |
| `check_scripts.py` | P2: какие скрипты никто не вызывает — профилактика мёртвого кода. |
| `check_section_refs.py` | Проверить внутренние ссылки на разделы (`§4.7`, `§5.6`) в рукописи. |
| `check_seed_dispersion.py` | check_seed_dispersion.py — если разброс по сидам велик, агрегат обязан это признать. |
| `check_seed_replication.py` | check_seed_replication.py — a seed is replication only if it changes the world. |
| `check_series_followthrough.py` | check_series_followthrough.py — серия закончилась, а агрегат не собран? |
| `check_series_homogeneity.py` | Гейт: серия должна быть снята одним кодом. |
| `check_single_running.py` | Gate: at most one queue item may be marked running. |
| `check_single_spec.py` | check_single_spec.py — не должно быть двух документов, объявляющих одну версию требований. |
| `check_snapshots.py` | check_snapshots.py — снимки лабораторного состояния обязаны совпадать с диском. |
| `check_stability.py` | Gate: the integrator must be stable for the parameters the run actually uses. |
| `check_uid_rule.py` | check_uid_rule.py — the identity rule of the field tracker, pinned as a data check. |
| `check_weights_ignored.py` | Gate: weights files must be ignored by git. |
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

## Лабораторный контур (19)

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
| `zenodo_deposit_030.py` | zenodo_deposit_030.py — deposit the article 030 archive on Zenodo through the records API. |
| `zenodo_link.py` | zenodo_link.py — вставить DOI депозита во все места репозитория одной командой. |
| `zenodo_upload.py` | zenodo_upload.py — депозит новой версии в Zenodo одной командой (без ручной загрузки в браузере). |

## Библиотека и литература (14)

| script | what it does (first line of its docstring) |
| --- | --- |
| `lib_cycle.py` | Цикл библиотеки: состояние, выбор следующей полезной работы, учёт. |
| `library_brief.py` | Задание библиотекарю: собирается из текущего состояния работы, а не пишется руками. |
| `library_cycle_log.py` | Лог работы библиотекаря по циклу волны. |
| `library_digest.py` | Дайджест библиотеки: что прочитано, что цитируется, что лежит мёртвым грузом. |
| `library_inbox.py` | Входящие библиотеки: что появилось и что я ещё не прочитал. |
| `library_wake.py` | Пробуждение библиотекаря по событию, а не только по календарю. |
| `lit_audit.py` | Аудит DOI в библиотеке: резолвятся ли и совпадает ли название. |
| `lit_autoqueue.py` | Automatic literature enqueueing: the librarian should not wait to be asked. |
| `lit_board.py` | Доска литературы: замечания к текущей работе. |
| `lit_check.py` | Очередь проверок литературы: срабатывает на «нам нужен параметр/механизм X». |
| `lit_duty.py` | Обязательный шаг литературы в каждом цикле. |
| `lit_index.py` | lit_index.py — локальный поисковик по полным текстам статей. |
| `lit_pressure.py` | Литдавление: нужен ли литературный слот прямо сейчас (триггер вместо календаря). |
| `lit_search.py` | Поиск свежих публикаций по открытым вопросам библиотеки. |

## Линия поля (12)

| script | what it does (first line of its docstring) |
| --- | --- |
| `adequacy_mi.py` | adequacy_mi.py — адекватность: числа статьи 028 §4b из артефактов, с названной командой. |
| `field_eas.py` | field_eas.py — две дороги сразу: дифференциал отбора (X37) и накопление новизны (X39). |
| `field_inherit.py` | field_inherit.py — L3 в поле: наследуемый состав, который влияет на рост. |
| `field_lab.py` | field_lab.py — непрерывное поле вместо клеток: пятна, которые делятся сами (Грей–Скотт). |
| `field_lifetimes.py` | field_lifetimes.py — времена жизни структур: числа статьи 028 §4.9 из артефактов. |
| `field_metrics.py` | field_metrics.py — the measurement code the field line's analyses share. |
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

## Сборка отчётов и таблиц (40)

| script | what it does (first line of its docstring) |
| --- | --- |
| `aggregate_check.py` | aggregate_check.py — сверка агрегатов с артефактами и внутренняя согласованность. |
| `build_article_029_package.py` | build_article_029_package.py — assemble the deposit package for article 029. |
| `build_article_030_package.py` | build_article_030_package.py — assemble the deposit package for article 030. |
| `build_article_031_package.py` | build_article_031_package.py — assemble the deposit package for article 031. |
| `build_article_032_package.py` | Build the deposit package for article 032. |
| `build_article_033_package.py` | build_article_033_package.py — assemble the deposit package for article 033. |
| `build_article_034_package.py` | build_article_034_package.py — assemble the deposit package for article 034. |
| `build_article_035_package.py` | build_article_035_package.py — assemble the deposit package for article 035. |
| `build_article_036_package.py` | build_article_036_package.py — assemble the deposit package for article 036. |
| `build_article_037_package.py` | build_article_037_package.py — assemble the deposit package for article 037. |
| `build_x160_memory_matrix.py` | Build x160_memory_matrix.json from the x160_memory series (63 artifacts, 3 arms x 20 seeds). |
| `make_article_029_figures.py` | make_article_029_figures.py — figures and derived tables for article 029 (v2, plain-language edition). |
| `make_article_029_pdf.py` | make_article_029_pdf.py — render article 029 as a self-contained PDF for the deposit. |
| `make_article_030_figures.py` | make_article_030_figures.py — figures for articles/030 (the gap between surfaces switches fusion). |
| `make_article_030_pdf.py` | make_article_030_pdf.py — render article 030 as a self-contained PDF for the deposit. |
| `make_article_031_figures.py` | Build the figures of article 031 from committed artifacts only. |
| `make_article_031_pdf.py` | make_article_031_pdf.py — render article 031 as a self-contained PDF for the deposit. |
| `make_article_032_pdf.py` | Build the PDF for article 032 by reusing the article-031 renderer. |
| `make_article_033_figures.py` | make_article_033_figures.py — the figure of article 033, built from the artifacts only. |
| `make_article_033_pdf.py` | Build the PDF for article 032 by reusing the article-031 renderer. |
| `make_article_034_figures.py` | make_article_034_figures.py — the figure of article 034, built from the artifact only. |
| `make_article_034_pdf.py` | Build the PDF for article 032 by reusing the article-031 renderer. |
| `make_article_035_figures.py` | make_article_035_figures.py — the figure of article 035, built from the artifact only. |
| `make_article_035_pdf.py` | Build the PDF for article 032 by reusing the article-031 renderer. |
| `make_article_036_figures.py` | Figures for article 036: the layer diagram and the defect-attribution table. |
| `make_article_036_pdf.py` | Build the PDF for article 036 by reusing the article-031 renderer. |
| `make_article_037_figures.py` | Figures for article 037: the three claims and the four constraints. |
| `make_article_037_pdf.py` | Build the PDF for article 037 by reusing the article-031 renderer. |
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

## Прочее (323)

| script | what it does (first line of its docstring) |
| --- | --- |
| `a1_corpus_survey.py` | A1: survey the whole artifact corpus - what do we actually have? |
| `a2_invalid_in_reports.py` | A2: did any INVALID run reach a report? |
| `a3_anomalies.py` | A3: find ANOMALIES in the corpus - series whose results depart from their peers. |
| `additivity_interaction.py` | additivity_interaction.py — взаимодействие двух механизмов на парных сидах. |
| `analyse_e3.py` | analyse_e3.py — сходятся ли три пути после того, как история закончилась. |
| `analyse_e3_state.py` | analyse_e3_state.py — сравнение по СОСТОЯНИЮ, а не по времени. |
| `analysis_task.py` | analysis_task.py — ферма CPU-задач на GitHub Actions: берёт задачу из очереди и считает. |
| `analyze_grid_failures.py` | Какие шумовые старты не дают доминирующий класс в клетках сетки H-E02C-6. |
| `attention.py` | attention.py — one page that answers "what needs a human, right now". |
| `audit_corpus.py` | Audit the whole corpus with one question: did each mechanism help the cell, in the cell's own terms? |
| `backfill_not_claimed.py` | backfill_not_claimed.py — дописать `not_claimed` в старые агрегаты. |
| `cadence_match.py` | cadence_match.py — is the `dt` dependence of the contrast a snapshot-cadence artefact? |
| `calibrate_thresholds.py` | Откалибровать и заморозить пороги OOD и тривиальности (протокол v1.2 §6b, §7). |
| `capture_stream.py` | capture_stream.py — запись настоящего потока из мира в артефакт. |
| `claim_audit.py` | Проверить пакеты доказательств в library/claims-evidence.md. |
| `claim_comparator.py` | claim_comparator.py — независимый аудит утверждения против его Setup (перенос идеи LongTails). |
| `closure_probe.py` | Closure probes: does the machinery actually catch a planted defect, and does it recover? |
| `coexistence_metrics.py` | coexistence_metrics.py — метрики сосуществования линий из СУЩЕСТВУЮЩИХ артефактов (0 GPU). |
| `compact_field_series.py` | compact_field_series.py — keep the derivable part of a dense-logging series in git. |
| `compact_world.py` | Helpers for reading the committed `.compact.json` projections of the dense series. |
| `compare.py` | Второй фильтр сравнения: не одно число, а распределение по сидам (B-008, I-014). |
| `config_gate_selftest.py` | Prove the config gate can fail: plant a field that config_block does not save. |
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
| `gate_refusal_selftest.py` | Does the live gate actually refuse? Plant a disagreement and check that no run starts. |
| `github_intake.py` | github_intake.py — GitHub issues as a task source, with an author allowlist. |
| `index_report.py` | index_report.py — add a report row to reports/README.md, or check which reports lack one. |
| `k_readouts.py` | The within-cell readouts: does a cell's behaviour follow its situation or its own record? |
| `l1_field_matrix.py` | l1_field_matrix.py — агрегат линии поля: медианы, разброс и интервалы по плечам. |
| `lean_axioms.py` | lean_axioms.py — независимая проверка теорем Lean на «чистоту аксиом» и неизменность формулировок. |
| `literature_harvest.py` | literature_harvest.py — собрать настоящие работы по теме, с аннотациями и ссылками на полные тексты. |
| `log_signal_scan.py` | log_signal_scan.py — майнер логов прогонов (LDD): какие сбои повторяются. |
| `meta_analysis.py` | Meta-analysis: across all series, did mechanism X help the cell? |
| `metric_variants.py` | metric_variants.py — инвариантность вывода к устройству метрики (H-ALIVE-39). |
| `neutral_yardstick.py` | neutral_yardstick.py — нейтральная линейка для наших миров. |
| `paired_compare.py` | paired_compare.py — парное сравнение двух плеч по сидам, без «средних по плечу». |
| `pdf_to_text_k.py` | Convert the Krishnamurti PDF into plain text so the whole book can be read at once. |
| `periodicity.py` | periodicity.py — есть ли у мира СВОЙ ритм, и синхронизирован ли он с петлёй. |
| `policy_bridge.py` | Bridge: the policy FILE and the policy MODEL must agree. |
| `policy_diff.py` | Three implementations of the same policy decision must agree. |
| `policy_mediator.py` | The mediator that the harness calls: Python rule plus a cross-check against the Rust mediator. |
| `policy_mediator_selftest.py` | Self-test for the live mediator: does the cross-check actually happen, and does it actually refuse? |
| `predictions.py` | predictions.py — реестр предсказаний: что мы обещали до данных и что вышло. |
| `probe_invasion_state.py` | probe_invasion_state.py — проба пути инъекции: где и когда исчезает инвайдер (§10at.1). |
| `recheck_partial_rho.py` | Independent recount of the C series in `metric_variants.json` (partial rho, trait against cell steps at fixed energy). |
| `reciprocity.py` | reciprocity.py — двусторонняя связь потока и мира: считается ОБА направления передачи. |
| `register_check.py` | Tell me where a NEW artifact has to be registered. |
| `response_independent.py` | Отклик признака, проверенный величиной, независимой от `w`. |
| `result_scan.py` | Сканер результатов: переходы берутся из данных, а не из таймера. |
| `rotate_notices.py` | Ротация доски notices.md: текущее — на доске, история — в архив. |
| `run_replicator.py` | replicator.py — мир `R1`: репликаторы БЕЗ тела (H-ALIVE-50). |
| `runs_chain.py` | runs_chain.py — печать целостности манифестов прогонов (наш аналог аттестации TEE). |
| `safe_commit.py` | safe_commit.py — коммит только при зелёном verify. |
| `seed_selftest.py` | Prove the seed is toroidal: the same disc must have the same mass wherever it is placed. |
| `self_review.py` | Дневной самоаудит библиотеки: что сработало, что нет, что поправить. |
| `size_resolved_contrast.py` | size_resolved_contrast.py — what size are the structures that make the contrast? |
| `slim_checkpoint.py` | Облегчить чекпоинт для инференса: только веса правила + метаданные. |
| `smc_interval.py` | smc_interval.py — интервалы вместо счёта «N из M». |
| `split_merge_selftest.py` | Prove the new split/merge counter sees events the old delta counter could not. |
| `split_world_design.py` | split_world_design.py — разложить план линии по файлам, оставив индекс. |
| `stream_profile.py` | stream_profile.py — измеряет профиль живых источников, а не угадывает «какой лучше». |
| `stream_sources.py` | stream_sources.py — источники живого сигнала извне для цифрового мира. |
| `test_lib_tools.py` | Регрессионные тесты инструментов библиотеки. |
| `v8_matrix.py` | v8_matrix.py — агрегат серии V8 (размещение инокулята × правило слияния). |
| `verify.py` | Единый гейт перед отправкой: `python scripts/verify.py` (или `make verify`). |
| `world_invariants.py` | Gate: the world's invariants, as one command. |
| `write_zenodo_032.py` | Write the zenodo.json metadata file for article 032 (and, generically, for others). |
| `x100_analyse.py` | x100_analyse.py — does the heredity of size survive a definition that needs no excursion cut? |
| `x100_series.py` | x100_series.py — heredity with a size that needs no excursion cut (X100). |
| `x101_analyse.py` | x101_analyse.py — basins by steepest ascent: a structure size with no level set at all. |
| `x102_analyse.py` | x102_analyse.py — does the SPECIFICITY of inheritance (parent beats neighbour) survive a weaker size definition? |
| `x103_analyse.py` | x103_analyse.py — X103: is heredity topographic?  Where in the mother's basin, not how big it is. |
| `x105_analyse.py` | x105_analyse.py — X105: does the maternal-decay term survive dense logging? |
| `x105_series.py` | x105_series.py — dense logging for the maze cell (X105). |
| `x106_analyse.py` | x106_analyse.py — X106: what is the crowding term?  A property of places, of growth, or of persistence. |
| `x107_analyse.py` | x107_analyse.py — X107: how much of the parent-daughter correlation is a shared room? |
| `x108_series.py` | x108_series.py — the same twenty worlds as X105, with a field at every logged step (X108). |
| `x110_analyse.py` | x110_analyse.py — X110: gamma_cell, the largest autocatalysis cut a cell survives, as a bracket. |
| `x110_series.py` | x110_series.py — X110: gamma_cell by bisection. How large an autocatalysis cut does each cell survive? |
| `x110b_analyse.py` | x110b_analyse.py — X110b: gamma_cell with a liveness test that can tell a pattern from a speckle. |
| `x111_analyse.py` | x111_analyse.py — X111: does the sign of rho(peak area, lifetime) survive a nine-times finer lifetime? |
| `x112_analyse.py` | x112_analyse.py — X112: the ladder and the specificity at three excursion cuts, on the same genealogies and frames. |
| `x112b_analyse.py` | x112b_analyse.py — X112b: the ladder and the specificity at cuts 0.15 and 0.25, on X108's worlds. |
| `x112b_series.py` | x112b_series.py — X112b: the same worlds at thresholds 0.15 and 0.25, next to X108's 0.20 reference. |
| `x112c_analyse.py` | x112c_analyse.py — X112c: the ladder and the specificity at cuts 0.15 and 0.25, on X108's worlds. |
| `x112c_series.py` | x112c_series.py — X112c: the same cut sweep in the maze cell (F = 0.040), next to X108's 0.20 reference. |
| `x113_analyse.py` | x113_analyse.py — X113: does size buy generations? |
| `x113b_analyse.py` | x113c_analyse.py — X113c: faster propagation or more division events? |
| `x113c_analyse.py` | x113c_analyse.py — X113c: faster propagation or more division events? |
| `x114_analyse.py` | x114_analyse.py — X114: is the generation-rate advantage an artefact of the horizon? |
| `x115_analyse.py` | x115_analyse.py — X115: does the faster line persist? Survival to the horizon, paired within sister pairs. |
| `x116_analyse.py` | x116_analyse.py — X116: is the survival advantage mechanical? |
| `x117_analyse.py` | x117_analyse.py — X117: match on area as well as on daughters. Does any survival advantage remain? |
| `x118_analyse.py` | x118_analyse.py — X118: at fixed size, does the number of daughters matter? |
| `x119_analyse.py` | x119_analyse.py — X119: does the daughter count predict survival with size held statistically? |
| `x120_analyse.py` | x120_analyse.py — X120: cost of division or time to divide? Daughters counted in a fixed early window. |
| `x121_analyse.py` | x121_analyse.py — X121: discrete-time hazard of disappearing, given age and daughters. |
| `x124_analyse.py` | x124_analyse.py — X124: do the generation-time and generation-rate results agree? |
| `x125_analyse.py` | x125_analyse.py — X125: one definition per quantity, all five readouts, both weightings. |
| `x125b_analyse.py` | x125b_analyse.py — X125b: the filter printed with the number, four statistics of one paired difference. |
| `x125c_analyse.py` | x125c_analyse.py — X125c: is X93's tie-excluded fraction bare once ties are counted? |
| `x126_analyse.py` | x126_analyse.py — X126: the third cell, three cells under one code path. |
| `x126_series.py` | x126_series.py — the third cell: ten worlds at F = 0.035, the identical protocol of X108. |
| `x127_analyse.py` | x127_analyse.py — X127: does a lineage end by vanishing, or by being absorbed into a neighbour? |
| `x128_analyse.py` | x128_analyse.py — X128: when a lineage loses its name, do its cells go to kin? |
| `x128b_analyse.py` | x128b_analyse.py — X128b: the local budget, then the kinship of whoever took the cells. |
| `x129_analyse.py` | x129_analyse.py — X129: is the kin advantage only geometry? Who lives next door at the same distance. |
| `x130_analyse.py` | x130_analyse.py — X130: do sisters merge back, and how long does it take? |
| `x131_analyse.py` | x131_analyse.py — X131: per-world values, then a bootstrap over WORLDS rather than over pairs. |
| `x132_analyse.py` | x132_analyse.py — X132: thirty worlds per cell, the paired per-seed test the power calculation asked for. |
| `x132_series.py` | x132_series.py — X132: twenty new worlds per cell at the two extreme inflows, seeds 311-330. |
| `x134_analyse.py` | x134_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages. |
| `x134_series.py` | x134_series.py — X134: two structures seeded at a controlled separation, swept. |
| `x134b_analyse.py` | x134b_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages. |
| `x134b_series.py` | x134_series.py — X134b: the X134 sweep re-run with a seed-dependent placement. |
| `x135_analyse.py` | x135_analyse.py — X135: the mixing length in the percolating cell, plus the single-disc control. |
| `x135_series.py` | x135_series.py — X135: the X134 sweep at F = 0.040, plus the single-disc control (SEP = 0). |
| `x136_analyse.py` | x136_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages. |
| `x136_series.py` | x134_series.py — X136: the wall to the cell - separations 14, 16, 17; 12, 15, 18 are reused from X134b. |
| `x138_analyse.py` | x138_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages. |
| `x138_series.py` | x134_series.py — X138: does the mixing length scale with the structure or with the wavelength? Radius 6, separations 16/24/32/40. |
| `x139_analyse.py` | x139_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages. |
| `x139_series.py` | x134_series.py — X139: the slowing curve - separations 7, 8, 10, 11 at radius 3; 12/14/15/16 are reused from X136. |
| `x140_analyse.py` | x140_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages. |
| `x140_series.py` | x134_series.py — X140: the gap rule's prediction - radius 4.5 must cross at 18 cells (2*4.5 + 9). |
| `x142_analyse.py` | x142_analyse.py — X142: how far out does mutual coalescence reach? |
| `x142_series.py` | x142_series.py — X142: the annihilation band - radius 3 gaps 3 and 7, radius 4.5 gaps 4, 5 and 6. |
| `x145_analyse.py` | x145_analyse.py — X145: when does a lone disc first split, at each radius? |
| `x145_series.py` | x145_series.py — X145: one radius-3 disc and nothing else (`--init-spots 3:0`). |
| `x147_analyse.py` | x147_analyse.py — X147: is the coalescence boundary at the same surface gap for two radii? |
| `x147_series.py` | x147_series.py — X147: radius 4.5 at surface gap 8 (separation 17), five seeds. |
| `x150_analyse.py` | x150_analyse.py — X150: a third radius (6.0) against the two already measured. |
| `x150_series.py` | x150_series.py — X150: a third radius (6.0) at surface gaps 6, 7 and 8. |
| `x151_analyse.py` | x151_analyse.py — X151: is the stop of the boundary a threshold or a plateau? |
| `x151_series.py` | x151_series.py — X151: radius 5.25 at surface gaps 7 and 8 (separations 17.5 and 18.5). |
| `x153_analyse.py` | x153_analyse.py — X153: is the boundary a whole-cell step or does it creep within a cell? |
| `x153_series.py` | x153_series.py — X153: radius 6.0 at separation 19.5, i.e. a surface gap of 7.5 cells. |
| `x154_analyse.py` | x154_analyse.py — X154: is the width in the time measurable, or is it noise of ten seeds? |
| `x154_series.py` | x154_series.py — X154: the mixing curve at radius 6, ten seeds per arm. |
| `x155_ablation.py` | x155_ablation.py — the mutation-off arm of X155, plus its anchor. |
| `x155_analyse.py` | x155_analyse.py — heredity of the field's trait: is it the medium's or the copying rule's? |
| `x156_analyse.py` | x156_analyse.py — is a shape measured from the field itself inherited? |
| `x156_series.py` | x156_series.py — X156: twenty runs with the field-measured shape observer. |
| `x157_gap_geometry.py` | x157_gap_geometry.py — where does fusion actually happen, in the geometry the bodies have at that moment? |
| `x157_quantum.py` | x157_quantum.py — is the 1.9-cell contact gap a threshold, or a logging artefact? |
| `x158_analyse.py` | x158_analyse.py — X158: turn the X157 band into a measured crossing. |
| `x158_series.py` | x158_series.py — X158: the missing arms that turn the X157 band into a measured crossing. |
| `x160_analyse.py` | x160_analyse.py — X160: does a mortality buffer on an external signal hold diversity? |
| `x160_series.py` | X160: does an external signal hold diversity through a mortality buffer? |
| `x161_discrete.py` | x161_discrete.py — is a DISCRETE trait inherited? Division order, fertility and lifespan from the lineage trees. |
| `x162_local_scale.py` | X162: is the local scale inherited? Parent-daughter reconstruction from the X156 compact logs, with area and shape |
| `x162b_neighbour_decay.py` | x162b_neighbour_decay.py — how far does the medium remember? |
| `x164_analyse.py` | x164_analyse.py — X164: does the fusion crossing depend on the size RATIO? |
| `x164_series.py` | x164_series.py — X164: does the fusion crossing depend on the size RATIO? |
| `x165_analyse.py` | x165_analyse.py — X165: does the pairwise crossing survive many-body contact? |
| `x165_series.py` | x165_series.py — X165: three bodies in a row, at gaps 8, 10 and 12. |
| `x166_analyse.py` | x166_analyse.py — X166: the contact threshold at one-step resolution. |
| `x166_series.py` | x166_series.py — X166: the contact threshold at one-step resolution. |
| `x167_fusion_reversibility.py` | x167_fusion_reversibility.py — is a merged body a new object, or the old pair that can come apart? |
| `x167b_analyse.py` | x167b_analyse.py — X167b: does a merge preserve anything? |
| `x167b_series.py` | x167b_series.py — arm (b) of X167b: single bodies, for the matched comparison with merged ones. |
| `x168_analyse.py` | x168_analyse.py — X168: does the crossing move with the inflow rate? |
| `x168_series.py` | x168_series.py — X168: does the fusion crossing move with the inflow rate F? |
| `x168b_analyse.py` | x168b_analyse.py — X168b: fusion share per (inflow, gap) cell, the crossing per rate, and the matched baseline. |
| `x168b_series.py` | x168b_series.py — X168b: the inflow matrix on one seed set and one run length. |
| `x168c_analyse.py` | x168c_analyse.py — the inflow test with the gap converted correctly. |
| `x168c_series.py` | X168c: the inflow test again, with the gap converted to a centre separation correctly. |
| `x168d_analyse.py` | x168d_analyse.py — X168d: ten seeds per cell at surface gaps 11 and 8, three inflow rates. |
| `x168d_series.py` | x168d_series.py — X168d: ten seeds at gap 11 (and a gap-8 control) at three inflow rates. |
| `x169_seam.py` | x169_seam.py — X169: sample the field around a fusing pair, to look for a seam. |
| `x169_seam_analyse.py` | x169_seam_analyse.py — X169: is there a seam in the field after a fusion? |
| `x170_corridor.py` | x170_corridor.py — X170: the field between two bodies at contact, at three inflow rates. |
| `x170_corridor_analyse.py` | x170_corridor_analyse.py — X170: the corridor concentration at contact, at three inflow rates. |
| `x171_corridor_sizes.py` | x171_corridor_sizes.py — X171: the corridor at contact at three body sizes, reference rate. |
| `x171_corridor_sizes_analyse.py` | x171_corridor_sizes_analyse.py — X171: is the corridor at contact the same at every body size? |
| `x172_forecast.py` | x172_forecast.py — X172: an unrun rate, F = 0.033, against two registered predictions. |
| `x172_forecast_analyse.py` | x172_forecast_analyse.py — X172: did the two registered predictions at F = 0.033 land? |
| `x173_bridge.py` | x173_bridge.py — X173: does the maximum the bridge reaches separate the runs that fuse from those that do not? |
| `x173_bridge_analyse.py` | x173_bridge_analyse.py — X173: does the bridge's maximum separate the runs that fuse from those that do not? |
| `x174_gap_corridor.py` | x174_gap_corridor.py — X174: the corridor at contact at three surface gaps, one size, one rate. |
| `x174_gap_corridor_analyse.py` | x174_gap_corridor_analyse.py — X174: corridor at contact across three gaps, one size, one rate. |
| `x174b_curve.py` | Extend X174's aggregate with the relation the three gaps suggest: the corridor at contact is monotone in the arm's fusion |
| `x175_interior.py` | x175_interior.py — X175: radius 4.5 at surface gap 9, F = 0.030 — an interior point of X174's curve. |
| `x175_interior_analyse.py` | x175_interior_analyse.py — X175: does the arm land where X174's curve said it would? |
| `x176_past_crossing.py` | x176_past_crossing.py — X176: radius 6 at surface gap 10, F = 0.030 — past that size's crossing (9). |
| `x176_past_crossing_analyse.py` | x176_past_crossing_analyse.py — X176: radius 6 at gap 10, past that size's crossing. |
| `x177_edge.py` | x177_edge.py — X177: radius 4.5 at surface gap 11, F = 0.030 — one cell past that size's crossing (10). |
| `x177_edge_analyse.py` | x177_edge_analyse.py — X177: the band's upper edge, radius 4.5 at gap 11. |
| `x178_cliff.py` | x178_cliff.py — X178: radius 6 at surface gap 9, F = 0.030 — thirty seeds on the cell that decides plateau or cliff. |
| `x178_cliff_analyse.py` | x178_cliff_analyse.py — X178: is the crossing a plateau or a cliff? Radius 6, gap 9, thirty seeds. |
| `x179_crossing_table.py` | x179_crossing_table.py — X179: every two-body cell this line has run, with intervals, from the committed projections. |
| `x180_dispersion.py` | x180_dispersion.py — X180: is the between-family dispersion the fixed spatial pattern's phase at the seeded site? |
| `x181_worst_cell.py` | x181_worst_cell.py — X181: radius 3 at surface gap 10, F = 0.030 — thirty fresh seeds on X179's worst-heterogeneity cell. |
| `x181_worst_cell_analyse.py` | x181_worst_cell_analyse.py — X181: X179's worst-heterogeneity cell (radius 3, gap 10, F = 0.030) on thirty fresh seeds. |
| `x182_local_inflow.py` | x182_local_inflow.py — X182: the same arm run at five chosen levels of the seeded site's local inflow. |
| `x182_local_inflow_analyse.py` | x182_local_inflow_analyse.py — X182: five chosen levels of the seeded site's local inflow, same arm. |
| `x183_local_collapse.py` | x183_local_collapse.py — X183: does the crossing collapse when the rate is read locally instead of nominally? |
| `x184_cold_body.py` | x184_cold_body.py — X184: the same arm run at five chosen levels of the local inflow at the colder body. |
| `x184_cold_body_analyse.py` | x184_cold_body_analyse.py — X184: five chosen levels of the local inflow at the colder body, same arm. |
| `x185_one_law.py` | x185_one_law.py — X185: do X182 (midpoint control) and X184 (colder-body control) read one law? |
| `x186_table_local.py` | x186_table_local.py — X186: re-read the 57-cell crossing table in the local inflow. |
| `x187_large_radius.py` | x187_large_radius.py — X187: why do the largest bodies read the opposite sign? |
| `x187_nucleation_analyse.py` | x187_nucleation_analyse.py — X187: why do the largest bodies read the opposite sign? |
| `x188_nucleation_identity.py` | x188_nucleation_identity.py — X188: are there bodies besides the pair, by spatial continuation rather than by uid? |
| `x189_bridge.py` | x189_bridge.py — X189: is the bridge between the bodies weaker when the site is warm? |
| `x189_bridge_analyse.py` | x189_bridge_analyse.py — X189: the bridge between two bodies, by local inflow and size. |
| `x190_bridge_sites.py` | x190_bridge_sites.py — X190: the bridge with the sample made of SITES, not seeds. |
| `x190_bridge_sites_analyse.py` | x190_bridge_sites_analyse.py — X190: the bridge measured over five distinct SITES per level. |
| `x191_site_sweep.py` | x191_site_sweep.py — X191: the bridge as a dose-response in the local inflow, five sites per level, one seed per site. |
| `x191_site_sweep_analyse.py` | x191_site_sweep_analyse.py — X191: the bridge as a dose-response in the local inflow. |
| `x192_phase_census.py` | x192_phase_census.py — X192: one world per phase class, the whole population at radius 6 gap 9. |
| `x192_phase_census_analyse.py` | x192_phase_census_analyse.py — X192: the phase census at radius 6 gap 9. |
| `x193_phase_census_r3.py` | x193_phase_census_r3.py — X193: the phase census at radius 3 gap 10, the smaller-body arm. |
| `x193_phase_census_r3_analyse.py` | x193_phase_census_r3_analyse.py — X193: the phase census at radius 3 gap 10. |
| `x194_phase_clusters.py` | x194_phase_clusters.py — X194: how many worlds do the line's published pools actually contain? |
| `x195_sign_sweep.py` | x195_sign_sweep.py — X195: the phase census at two intermediate radii, to locate the change of sign. |
| `x195_sign_sweep_analyse.py` | x195_sign_sweep_analyse.py — X195: the sign of the inflow-outcome relation at four body sizes. |
| `x196_gap_or_size.py` | x196_gap_or_size.py — X196: is the fusion window set by the body size or by the gap? |
| `x196_gap_or_size_analyse.py` | x196_gap_or_size_analyse.py — X196: is the fusion window set by the body size or by the gap? |
| `x197_deviance_worlds.py` | x197_deviance_worlds.py — X197: does X186's published deviance drop survive counting worlds instead of runs? |
| `x198_gap_curve.py` | X196 answered the either-or: the gap switches fusion, the size shifts it. It did so with three arms and a five-row table whose two |
| `x198_gap_curve_analyse.py` | x198_gap_curve_analyse.py — X198: the fusion share as a function of the surface-to-surface gap. |
| `x199_mixed_model.py` | x199_mixed_model.py — X199: does the local-inflow association survive a random intercept per world / per phase class? |
| `x200_clone_pairs.py` | x200_clone_pairs.py — X200: is the "world" of X199 a cluster? Clone pairs at one (cell, phase). |
| `x201_edge_intervention.py` | X201 — edge-distance intervention (pre-registration: reports/2026-11-05-x201-edge-intervention-plan.md). |
| `x202_clone_repro.py` | X202 — reproduce sensitive X200 clone-pairs and test clean clones (fixed phase + fixed edge). |
| `x203_clean_clone.py` | X203 — larger-n clean clones at fixed (geometry, phase, edge) on verified non-zero-baseline strata. |
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
| `x66_analyse.py` | x66_analyse.py — the four-point grid map, all at dt = 0.5. |
| `x66_series.py` | x66_series.py — X66: the grid map with the time step held fixed. |
| `x67_analyse.py` | x67_analyse.py — the box doubled: which scale does the heterogeneous field peak on? |
| `x67_series.py` | x67_series.py — X67: the box doubled, the cell size fixed. |
| `x68_analyse.py` | x68_analyse.py — does the lifetime contrast survive a different identity rule? |
| `x68_series.py` | x68_series.py — X68: the lifetime contrast under two other identity rules. |
| `x68r_analyse.py` | x68r_analyse.py — X68 lifetimes on five genuinely different neutral worlds per identity rule. |
| `x68r_series.py` | x68r_series.py — X68 with five genuinely different neutral worlds per rule. |
| `x70_analyse.py` | x70_analyse.py — size heredity: does a daughter's peak area follow its parent's? |
| `x70_series.py` | x70_series.py — X70: size heredity in the neutral world. |
| `x70_spatial_null.py` | x70_spatial_null.py — the control the four answers asked for: is the size signal just neighbours sharing a place? |
| `x70_spatial_strata.py` | x70_spatial_strata.py — the spatial control for X70 done over all events, stratified instead of matched. |
| `x70d_series.py` | x70d_series.py — X70 re-run with dense component logging, for the stratified spatial control. |
| `x70r_series.py` | x70r_series.py — X70 with genuinely independent neutral worlds. |
| `x71_analyse.py` | x71_analyse.py — is the selected wavelength single-valued across worlds, or do two branches coexist? |
| `x71_series.py` | x71_series.py — does one inflow support two morphologies? (preregistered in reports/2026-11-01-x71-multistability-plan.md) |
| `x71b_analyse.py` | x71b_analyse.py — is the two-branch coexistence of X71 stable or a transient? |
| `x71b_series.py` | x71b_series.py — does the two-branch coexistence of X71 survive 24 000 steps? |
| `x71c_analyse.py` | x71c_analyse.py — how wide is the multistable band? Measured, not assumed from the sweep step. |
| `x71c_series.py` | x71c_series.py — how wide is the multistable band? Two half-steps around F = 0.035 at 24 000 steps. |
| `x72_analyse.py` | x72_analyse.py — at the multistable boundary, does a daughter take her parent's branch? |
| `x72b_analyse.py` | x72b_analyse.py — branch concordance at the multistability boundary, read from local spectra. |
| `x72b_series.py` | x72b_series.py — the branch-heredity series, with fields every 50 steps. |
| `x72c_analyse.py` | x72c_analyse.py — branch heredity with band powers: does a daughter's mixture follow her parent's? |
| `x72c_regions.py` | x72c_regions.py — is the mixture a property of regions? (follow-up to X72c, no new runs) |
| `x72c_series.py` | x72c_series.py — third attempt at branch heredity: ten worlds, band powers instead of a class. |
| `x72c_size_contrast.py` | x72c_size_contrast.py — the same events, two readouts: size versus mixture. |
| `x73_depth.py` | x73_depth.py — how deep is the size memory? Ancestor–descendant correlation over genealogical distance. |
| `x74_analyse.py` | x74_analyse.py — does the half-life of the size memory depend on the inflow? |
| `x74_series.py` | x74_series.py — two more inflow cells for the memory-decay rate (X74). |
| `x75_analyse.py` | x75_analyse.py — depth curves at the multistable band edges. |
| `x75_series.py` | x75_series.py — depth curves at the multistable band edges (X75). |
| `x76_analyse.py` | x76_analyse.py — ten worlds at F = 0.033: sampling accident or a genuinely weak initial memory? |
| `x76_series.py` | x76_series.py — ten worlds at F = 0.033 to replicate the weak-memory cell (X76). |
| `x77_patch_control.py` | x77_patch_control.py — is the size memory parental, or just the local patch? |
| `x78_analyse.py` | x78_analyse.py — causal test: does memory depth follow the number of preferred scales, or the inflow? |
| `x78_series.py` | x78_series.py — causal test: matched vs mismatched prescribed scale at F = 0.040 (X78). |
| `x78b_analyse.py` | x78b_analyse.py — does an imposed second scale shorten memory at a long-memory inflow? |
| `x78b_series.py` | x78b_series.py — composite two-scale pattern at F = 0.030 (X78b). |
| `x79_analyse.py` | x79_analyse.py — does memory shorten gradually with the weight of an imposed second scale? |
| `x79_series.py` | x79_series.py — mix sweep of the composite pattern at F = 0.030 (X79). |
| `x80_analyse.py` | x80_analyse.py — with amplitude fixed, does memory dip where the mixture is richest? |
| `x80_series.py` | x80_series.py — amplitude-normalised mix sweep at F = 0.030 (X80). |
| `x81_series.py` | x81_series.py — prescribed spectrum: share of a second peak at fixed dominant (X81). |
| `x82_analyse.py` | x82_analyse.py — prescribed vs realised spectral share: how far does inflow modulation reach? |
| `x82_series.py` | x82_series.py — the reach of inflow modulation: prescribed vs realised spectral share (X82). |
| `x84_analyse.py` | x84_analyse.py — separate the forcing line from the morphology, and re-read X71's branches. |
| `x85_analyse.py` | x85_analyse.py — does the symmetry of the pattern carry the size memory? |
| `x85_series.py` | x85_series.py — does the symmetry of the pattern carry the size memory? (X85) |
| `x86_analyse.py` | x86_analyse.py — place the symmetry curve, then read the memory against it. |
| `x86_series.py` | x86_series.py — place the symmetry curve with twenty worlds per inflow (X86). |
| `x87_analyse.py` | x87_analyse.py — memory against symmetry on twenty worlds per inflow (X85's eight + X87's twelve). |
| `x87_series.py` | x87_series.py — memory against symmetry, twelve more worlds per cell (X87). |
| `x88_analyse.py` | x88_analyse.py — the percolating arm: does memory rise again above the band, or keep declining? |
| `x88_series.py` | x88_series.py — the high-inflow (percolating) arm at twenty worlds per cell (X88). |
| `x89_analyse.py` | x89_analyse.py — where do the lineages vanish between F = 0.045 and 0.050? |
| `x89_series.py` | x89_series.py — four half-steps between 0.045 and 0.050, to locate where lineages vanish (X89). |
| `x90_analyse.py` | x90_analyse.py — does the lineage trickle stop, or does it only slow down? |
| `x90_series.py` | x90_series.py — does the trickle stop or only slow? 12 000 steps at the fading edge (X90). |
| `x91_analyse.py` | x91_analyse.py — is the memory at the band's shoulders lineage memory or regional resemblance? |
| `x92_analyse.py` | x92_analyse.py — does size pay? Peak area against lifetime and against the number of daughters. |
| `x93_analyse.py` | x93_analyse.py — do sisters pay for size? Within-family contrast with lifetime as the outcome. |
| `x96_analyse.py` | x96_analyse.py — X96 pilot: does a second diffusive species move the pattern's scale? |
| `x96_pilot.py` | x96_pilot.py — X96: the second diffusive species (owner-approved 02.11). |
| `x96d_analyse.py` | x96d_analyse.py — X96d: does the second species move the orientation, and does it replicate? |
| `x96d_series.py` | x96d_series.py — X96d: does the second species move the orientation? Three seeds, two cells, four diffusion lengths. |
| `x97_analyse.py` | x97_analyse.py — X97: does the sister advantage reach the second generation? |
| `x97b_analyse.py` | x97b_analyse.py — X97b: is the second-generation sister advantage branching arithmetic or a lineage effect? |
| `x98_analyse.py` | x98_analyse.py — is the angular map a property of the world or of the excursion cut? |
| `x99_analyse.py` | x99_analyse.py — is the memory map a property of the world or of the excursion cut? |
| `x99_series.py` | x99_series.py — the memory map at two other excursion cuts (X99). |
