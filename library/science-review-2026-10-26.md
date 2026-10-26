# Научный дайджест за 2026-10-26

Коммитов за сутки: **90**. Изменённых агрегатов: **23**.

## Что сделано (по коммитам)
- `9242d74` library: слот 13:30 — C6 переписан явными дробями с знаменателями (uniform 7/10 и 0/10; patches 10/10 и 0/10; 
- `5d75ed4` SUPPLEMENT: пересобран после правки агрегатов инвазии (таблица читает HEAD, поэтому обновляется только на след
- `d3fbca1` мета-ревью (цикл 12:15): проверка утверждения об инвазии по сырью — placement uniform 7/10, patches 10/10, maj
- `a07a447` library: глубокий проход 26.10 — исправлен устаревший счётчик (было 70, фактически 134 записи/93 G-строки); до
- `d19a60d` library: слот 09:30 — очередь пуста, проверены три агрегата через check_claim (placement uniform 7, patches 10
- `0d1b368` мета-ревью (цикл 09:15) нашло устаревшее число в CLAIMS: строка про W2-bud v4 всё ещё ссылалась на -0.700 из г
- `db0c7a0` SUPPLEMENT: режим --check + блокирующий гейт в health и CI. Причина повторяющегося красного: любой пересчёт аг
- `d726956` CI-задача дня: check_aggregate_coverage.py — каждый артефакт прогона обязан входить в агрегат (331 агрегат, 58
- `e225079` library: тематическая литература 26.10 — Oszoli & Zachar 2024 (10.1371/journal.pcbi.1012107): агрегативная мно
- `b31d8df` SUPPLEMENT: служебные файлы фермы (farm-status.json, provenance-legacy.json) исключены из таблицы артефактов. 
- `996b7a6` health: устаревание красного CI определяется по коммиту, а не по времени — ночной прогон на d11d7de (до починк
- `8b47ebf` health: отсев упавших workflow по name: из YAML, а не по имени файла — удалённый ci-status.yml продолжал висет
- `324d900` reports: пункт 5 сводки — контроль «без резидента» провалился как свойство мира, а не как ошибка серии
- `e4f2fba` docs+reports: цена — медиана с n и квартилями, «запас 0.03» убран как неверная формулировка
- `62c8115` агрегат семейства w1niche канонизирован (43 строки: 4 плеча x 10 сидов + adjacency_exact 3) — шаблон имени зна
- `43bdc32` reports: черновик итога суток для владельца — подтверждено / опровергнуто / открыто
- `ec20ce2` SUPPLEMENT воспроизводим из коммита: хеши и размеры берутся из blob HEAD (пакетно, один git cat-file --batch),
- `46f0dee` CI красный на обеих ОС из-за SUPPLEMENT: он собирался до пересборки агрегатов под стандартную метрику и не сод
- `8ac43ec` lab+reports: пункт пула W1-niche-adjacency-exact закрыт (контроль выполнен), строка в индексе отчётов
- `c7e3053` docs: §10ay — остаток объяснён числом живых соседей (adjacency_exact), специфики точки смерти нет
- `984454a` world+reports: точный контроль соседства adjacency_exact (уровни n4 = 0..4) и поправка к пре-регистрации
- `32390c3` world+experiments+docs: W1-niche — наследования по линии нет; эффект зоны не объясняется плотностью (§10ay)
- `75861c4` reports: поправка к анализу W1-niche ДО конца серии — стратификация по размеру мира, порог underpowered, ожида
- `57282eb` lab: строка о запуске серии W1_niche_v5 (4 плеча x 10 сидов)
- `d11d7de` analysis-farm: результаты 03:53Z [skip ci]

## Что изменилось в числах (агрегаты)
- **ci_p_invasion_dose5**: без criteria
- **ci_p_invasion_keep_patches**: без criteria
- **ci_p_invasion_keep_uniform**: без criteria
- **ci_p_invasion_majority**: без criteria
- **ci_p_selection_replication**: без criteria
- **power_lines_price**: без criteria
- **recompute_i_w2bud3**: без criteria
- **recompute_i_w2budd2**: без criteria
- **whale_w2bud3**: без criteria
- **placement_matrix**: placement_series_valid=True, note=серия годна по постановке, если в каждом плече rejected <= 1/10 И state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится
- **placement_patches_matrix**: placement_series_valid=True, note=серия годна по постановке, если в каждом плече rejected <= 1/10 И state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится
- **w1niche5_matrix**: not_lineage=9, note=вердикт — прямое парное сравнение долей; ожидание не используется
- **w1niche_matrix**: not_lineage=9, note=вердикт — прямое парное сравнение долей; ожидание не используется
- **w2bud2_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud3_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud4s_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_onebud_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=True
- **w2bud_rep_patches_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_rep_uniform_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2budd2_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=True
- **w2budd2_rep_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2budd2_rep_n1_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False

## Рекомендации (из чисел, не из прозы)
- **починить постановку серии по w2bud_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2bud_matrix: criteria.invalid_by_data = true
- **починить постановку серии по w2budd2_rep_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2budd2_rep_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2budd2_rep_matrix/cell: валидных 4/10**  
  основание: `valid_n=4 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5
- **починить постановку серии по w2budd2_rep_n1_matrix, вердикт не выносить**  
  основание: `criteria.invalid_by_data = True`; цена: 1 цикл; проверка: повторный прогон/пересборка w2budd2_rep_n1_matrix: criteria.invalid_by_data = true
- **добрать линии/сиды для w2budd2_rep_n1_matrix/cell: валидных 1/10**  
  основание: `valid_n=1 из runs=10 (порог 0.5)`; цена: 1 серия; проверка: valid_n/runs >= 0.5

## Отдача литературы (7 дней)
- DOI в добавленных/правленых строках `hypotheses/` за неделю: **175**; из них упомянуты ВНЕ индексов (answers/conditions/claims/reviews): **37** (отдача 21%)
  *читается так:* это доля источников, которые дошли до рабочего текста, а не только до индекса. Ниже 30 % две недели подряд — снижать частоту литслота, а не наращивать объём.

## Доска и литература
- новых замечаний: 1; решено: 2 (принято 0, отклонено 1)
- литдавление: 2 (порог 3)
  открытые вопросы: 0 []
  открытые lit-пункты очереди: 0 []
