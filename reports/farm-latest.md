# Ферма CPU-задач: последние результаты

Обновлено: 2026-10-26 00:40 UTC. Источник — `morphogenesis/experiments/E09_pond/analysis/`.

| задача | вид | вердикт | ключевые числа | провенанс |
|---|---|---|---|---|
| `ci_p_invasion_dose5` | proportion | — | p=0.2, wilson95=[0.0567, 0.5098], bootstrap95=[0.0, 0.5], n=10 | b0e96d0 |
| `ci_p_invasion_keep_patches` | proportion | — | p=1.0, wilson95=[0.7225, 1.0], bootstrap95=[1.0, 1.0], n=10 | b0e96d0 |
| `ci_p_invasion_keep_uniform` | proportion | — | p=0.7, wilson95=[0.3968, 0.8922], bootstrap95=[0.4, 1.0], n=10 | нет |
| `ci_p_invasion_majority` | proportion | — | p=0.0, wilson95=[0.0, 0.2775], bootstrap95=[0.0, 0.0], n=10 | b0e96d0 |
| `ci_p_selection_replication` | proportion | — | p=0.9, wilson95=[0.5958, 0.9821], bootstrap95=[0.7, 1.0], n=10 | b0e96d0 |
| `recompute_i_w2bud3` | recompute_i | — | I_obs_median=0.5614, I_null_95_median=0.0623, I_ratio_median=12.346, above_null_k=10 | b0e96d0 |
| `recompute_i_w2budd2` | recompute_i | — | I_obs_median=1.151, I_null_95_median=0.015, I_ratio_median=57.138, above_null_k=10 | b0e96d0 |
| `whale_w2bud3` | rho_drop_whale | связь держится на крупнейшей линии: ρ +0.500 → +0.000 без неё (|ρ| < 0.2) — это не популяционная статистика | median_rho_full=0.5, median_rho_without_whale=0.0, verdict=связь держится на крупнейшей линии: ρ +0.500 → +0.000 без неё (|ρ| < 0.2) — это не популяционная статистика | нет (dirty) |

## Проблемы

- ci_p_invasion_keep_uniform.json: нет script_commit — результат старого формата, связь с кодом только по карте
- whale_w2bud3.json: посчитано изменённым скриптом (script_dirty) — провенанс неполный
- whale_w2bud3.json: нет script_commit — результат старого формата, связь с кодом только по карте
- прогон 40248968075 завершился «skipped» — смотреть https://github.com/mak777uh/-/actions/runs/40248968075
- в очереди pending без результата: power_lines_price
