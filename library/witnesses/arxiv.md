# Witness-таблица: arXiv draft v1.2 — Morphogenesis

Утверждение -> поле агрегата -> что доказывает -> что НЕ доказывает. Таблица перегенерируется, поэтому не стареет молча.

| id | утверждение | поле | значение | сходится | что доказывает | чего НЕ доказывает |
|---|---|---|---|---|---|---|
| W1 | I_obs = 0.5614 (клеточное почкование) | `morphogenesis/experiments/E09_pond/w2bud3_matrix.json` :: `by_arm.1.crow_I_median_all` | `0.5614` | да | медиана I по 10 сидам воспроизводится из агрегата | критерий I>null записан после данных, а не пре-регистрирован |
| W2 | нуль-модель 95 % = 0.0621 | `morphogenesis/experiments/E09_pond/w2bud3_matrix.json` :: `by_arm.1.I_null_95_median` | `0.0621` | да | значение нуля при rate = sum/sum | чувствительность к выбору нуль-модели (mean-rate даёт другое) |
| W3 | колониальное почкование: I = 0 | `morphogenesis/experiments/E09_pond/w2bud3_matrix.json` :: `by_arm.0.crow_I_median_all` | `0.0` | да | в контроле вариативность между линиями отсутствует | «отбора нет»: линия одна по построению |
| W4 | цена: медиана rho_partial = -0.374 (kill-the-winner, 30 прогонов) | `morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm_matrix.json` :: `by_arm.cellkw05.rho_median` | `-0.374` | да | медиана частной ранговой корреляции по 30 прогонам | величину <= 0.3: верхняя граница ДИ -0.266 порог не берёт |
| W5 | цена отсутствует в канале частоты обновления: медиана +0.055 | `morphogenesis/experiments/E09_pond/w2bud_trait_update_matrix.json` :: `by_arm.cellupd.rho_median` | `0.055` | да | в этом канале медиана около нуля при узком ДИ | общий закон «цена принадлежит каналу» — только для этих двух конструкций |
| W6 | инвазия uniform: keep 7/10, majority 0/10 | `morphogenesis/experiments/E09_pond/placement_matrix.json` :: `by_arm.0.survived_k` | `7` | да | число выживших линий к концу в плече keep | «появляется»: присутствие по a_share<1 даёт 10/10 |
| W7 | инвазия patches: keep 10/10, majority 0/10 | `morphogenesis/experiments/E09_pond/placement_patches_matrix.json` :: `by_arm.0.survived_k` | `10` | да | выжившие в плече keep на раскладке patches | механизм: majority стирает в шаге подсадки, это не конкуренция |
| W8 | горизонт: плато 1/Sum p^2 = 8.80 (комбинация) против 1.30 (контроль) | `morphogenesis/experiments/E09_pond/w2bud_horizon_matrix.json` :: `by_arm.horizonboth.effective_lineages_median` | `8.8` | да | величина на 1800 шагах из одной истории прогона | плато окончательно: 1800 не бесконечность |

## Как воспроизвести

```
python library/tools/paper_witness.py --spec library/witnesses/arxiv.json
```

Таблица генерируется этим запуском: значение в столбце «значение» — прочитано из артефакта сейчас, а не взято из текста статьи.
