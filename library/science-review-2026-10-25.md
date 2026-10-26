# Научный дайджест за 2026-10-25

Коммитов за сутки: **203**. Изменённых агрегатов: **18**.

## Что сделано (по коммитам)
- `d826ebe` library: §4h patches — 'keep 10/10 выживших' это присутствие; агрегат даёт survived_k 7/10 (final_cells>0); см
- `488a9bd` manuscript: §4h — вторая раскладка (patches) подтверждает направление по инвазии: keep 10/10 против majority 0
- `5b30e63` experiments+docs: инвазия на patches — направление сохраняется и усиливается (§10at.4)
- `d70e0cc` library: V1e (patches) — гейт постановки и invade_at=201 приняты; порог '5/10 против 1/10' не значим (Fisher p
- `6de5aee` docs: §10at.3 — четыре оговорки к результату V1c (Уилсон, одна раскладка, majority=период, keep=до слияния)
- `06baff5` reports+lab: пре-регистрация инвазии на patches (V1e) — вопрос «а на другой раскладке?»
- `a54116e` manuscript: §4h — решающая серия по инвазии, подсадка починена (20/20 годных), keep 7/10 против majority 0/10,
- `d70b75a` world+experiments+docs: V1c — гарантированная подсадка, 20/20 полных, вопрос о режиме гибели задан (§10at.3)
- `d1b0d1f` library: расхождение §4i объяснилось ddof (0 -> 0.4284, 1 -> 0.5614), R18 — ddof часть определения величины; м
- `4ab49eb` manuscript: §4i приведён к ddof-согласованным числам (I_obs 0.5614, запас 12.16/9.04, диапазон 3.68-104.34 по 
- `f0d86f4` docs+scripts+claims: ddof согласован, один агрегат инвариантности, проба как скрипт, V8 по своему контролю
- `c9c96d6` notices: первое мета-ревью рецензента — 4 из 4 пунктов подтверждены пересчётом, роль остаётся
- `bda76fc` manuscript: правки по первому проходу рецензента — запас как медиана отношений (6.90 рядом), диапазон по основ
- `6af8e9f` library: самоаудит 25.10 — поправка «тесты не зависят от живого состояния»: lit_pressure-тест требовал долг в 
- `330d986` reviewer: контракт роли, формат lab/reviews, гейт check_reviews (в verify и CI), мета-ревью ведущим раз в цикл
- `18a4a26` queue: --audit (running без замка, planned с готовыми артефактами) в CI — последний класс «забыл обновить стат
- `bee19ff` library: гейт «done только со ссылкой на существующий артефакт» + контракт 3b-1 «входящие по расписанию» (тайм
- `2b31392` library: исправлены преждевременные закрытия — viability kernel реально внесён в docs/optimality.md, Уилсон/MI
- `5d2381e` library: разобраны все 36 замечаний (33 закрыто, 17 отложено с условием, 0 без решения); гейт «принято, но не 
- `e2edf34` queue: закрыты принятые пункты (V1b §10at, фазовая развёртка §10at.2, v4 §10as) — состояния очереди приведены 
- `2812bb7` docs+reports+lab: цена vs отклик разделены, пост-хок порог убран, пре-регистрации replication и threshold3
- `8b102b0` manuscript: §4i — цена инвариантна к метрике, но вердикт требует порога >=3, зафиксированного заранее (v3.31);
- `a28e6e7` experiments+docs: инвариантность метрики — S и знак цены держатся во всех 18 вариантах (§10au)
- `4d0b028` experiments+docs: фазовая развёртка — период объясняет типичный случай, слияние — хвост (§10at.2)
- `b123fb5` analysis: проверка на устройство метрики (18 комбинаций) — S инвариантна 10/10 во всех, R меняет знак; §4i v3.

## Что изменилось в числах (агрегаты)
- **ci_p_invasion_keep_uniform**: без criteria
- **whale_w2bud3**: без criteria
- **founding_matrix**: threshold_between_1_and_20=False, founding_from_one_cell=True, no_founding_up_to_20=False, monotone_survival=True
- **invader_death_matrix**: keep_abrupt_7_of_10=False, majority_gradual_7_of_10=False, mode_depends_on_merge=False, invalid_by_data=True
- **kill_keep2_matrix**: positive_in_4_of_5=False, median_diff_positive=False, resource_lower_in_keep=True, c_sufficient=False
- **kill_keep3_matrix**: positive_in_4_of_5=False, median_diff_positive=False, resource_lower_in_keep=True, c_sufficient=False
- **kill_keep_matrix**: positive_in_4_of_5=False, median_diff_positive=False, resource_lower_in_keep=True, c_sufficient=False
- **merge_keep_matrix**: placement_works=False, merge_works_resident=False, merge_works_gap=False, merge_works=False
- **phase_matrix**: structure_period_le5_all_phases=False, any_phase_gt5_in_3=False, note=структурное свойство: time_to_rewrite <= 5 в >= 9/10 каждой фазы => режим гибели в majority неопределим по построению (период enforce = 5 шагов); иначе нужен мир с enforce_every = 1 (пул D-48)
- **placement_matrix**: placement_series_valid=True, note=серия годна по постановке, если в каждом плече rejected <= 1/10 И state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится
- **placement_patches_matrix**: placement_series_valid=True, note=серия годна по постановке, если в каждом плече rejected <= 1/10 И state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится
- **selection_matrix**: manipulation_ok=False, opportunity_for_selection=False, e_confirmed=False, control_neutral=True
- **w2bud2_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud3_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud4s_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_rep_patches_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_rep_uniform_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False

## Рекомендации (из чисел, не из прозы)
- **починить постановку серии по invader_death_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка invader_death_matrix: criteria.invalid_by_data = true
- **починить постановку серии по invader_death_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_placement = True`; цена: 1 цикл; проверка: повторный прогон/пересборка invader_death_matrix: criteria.invalid_by_placement = true
- **починить постановку серии по w2bud2_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2bud2_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2bud2_matrix/colony: валидных 0/10**  
  основание: `valid_n=0 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **добрать линии/сиды для w2bud2_matrix/cell: валидных 4/10**  
  основание: `valid_n=4 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **починить постановку серии по w2bud3_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2bud3_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2bud3_matrix/colony: валидных 0/10**  
  основание: `valid_n=0 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **добрать линии/сиды для w2bud3_matrix/cell: валидных 4/10**  
  основание: `valid_n=4 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **починить постановку серии по w2bud4s_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2bud4s_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2bud4s_matrix/cell: валидных 4/10**  
  основание: `valid_n=4 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **добрать линии/сиды для w2bud_matrix/colony: валидных 0/10**  
  основание: `valid_n=0 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **добрать линии/сиды для w2bud_matrix/cell: валидных 2/10**  
  основание: `valid_n=2 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **починить постановку серии по w2bud_rep_patches_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2bud_rep_patches_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2bud_rep_patches_matrix/cell: валидных 4/10**  
  основание: `valid_n=4 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **починить постановку серии по w2bud_rep_uniform_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2bud_rep_uniform_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2bud_rep_uniform_matrix/colony: валидных 0/10**  
  основание: `valid_n=0 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **добрать линии/сиды для w2bud_rep_uniform_matrix/cell: валидных 1/10**  
  основание: `valid_n=1 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **проверить, что принятые пункты реализованы (не только приняты)**  
  основание: `принято 6 за сутки`; цена: 15 мин; проверка: гейт «принято, но не сделано» зелёный

## Доска и литература
- новых замечаний: 20; решено: 45 (принято 6, отклонено 0)
- литдавление: 2 (порог 3)
  открытые вопросы: 0 []
  открытые lit-пункты очереди: 0 []
