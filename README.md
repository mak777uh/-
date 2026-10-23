# Project Morphogenesis

Научный стенд для поиска «геометрии жизни» в цифровой среде: нейронные клеточные
автоматы, топология и карта аттракторов. Это не продукт и не заявка на создание
жизни — воспроизводимый стенд и публичный лабораторный журнал: мы проверяем, есть
ли у цифровой материи собственные устойчивые морфологии и можно ли операционально
отличить живое поведение от навязанного извне.

Проект прошёл четыре поворота, и все они сохранены в репозитории как путь, а не
выброшены: **цель** (кольцо не стало аттрактором) → **карта** (перепись того, что
система порождает сама) → **репликация** (класс не воспроизводится на новых сидах
и меняется от арифметики) → **фаза** (класс зависит от горизонта обучения: один
прогон проходит `uniform_dark` → `struct_2` → `struct_1` → `death`). Полное
описание пути, включая ошибки и уроки — [`docs/path.md`](docs/path.md).

Из этого следует нынешнее направление: если класс — фаза, то искать надо не форму,
а **условия, в которых организация поддерживается**. Поэтому строится среда, где
поддержание стоит энергии, есть повреждения, размножение и отбор через дефицит —
[`docs/world-design.md`](docs/world-design.md), [`docs/open-ended-program.md`](docs/open-ended-program.md).

> **Статус:** working paper / laboratory notebook, не рецензировано. Внешняя
> публикация (arXiv, датасет, benchmark) закрыта гейтом: сначала репликация
> обучения R-9 (E02c) и независимое воспроизведение, потом заявления. Репозиторий
> публичен как журнал, а не как опубликованная статья. Будущая статья собирается
> постепенно в [`manuscript/`](manuscript/README.md).

**Обновлено:** 2026-10-23. Источник истины — [`lab/registry.json`](lab/registry.json),
канонический журнал [`morphogenesis/logs/journal.jsonl`](morphogenesis/logs/journal.jsonl)
и сырые артефакты. [`lab/state.json`](lab/state.json) — пересобираемый снимок, а не
ручная правка. Правила измерения — [`docs/protocol.md`](docs/protocol.md) (v1.2),
где мы сейчас — [`docs/research-map.md`](docs/research-map.md).

## Журнал экспериментов

Одна строка на эксперимент; детали, числа и протоколы — в отчётах и статьях.
Правила ведения — [`AGENTS.md` §6a](AGENTS.md).

<!-- ledger:start -->
| id | Статус | Период | Вопрос | Итог | Доказательства |
| --- | --- | --- | --- | --- | --- |
| E01_criticality | закрыто | 18.10 | критичность и «первичный бульон» | историческая серия; в текущую программу не входит | [results.json](morphogenesis/experiments/E01_criticality/results.json) |
| E02_pattern | закрыто | 20.10 | кольцо как цель | **отрицательно:** кольцо не аттрактор; гейт слоя 1 — 0/5; достижение и удержание — разные режимы | [отчёт](reports/2026-10-20-e02-pattern.md) · [статья 002](articles/002-pochemu-kolco-ne-stalo-attraktorom.md) |
| WP4_R9 | закрыто | 20.10 | 5 сидов R-9, зонд reach/hold | sweep закрыт, гейт WP4 не пройден (`journal_pairs_13_3`); Wilcoxon на 5 парах даёт p ≥ 0.0625 | [статус](reports/2026-10-20-wp4-status.md) |
| E02b_morphospace | закрыто | 20–21.10 | перепись морфопространства | **rich_map:** 832 развёртки, 573/704 — смерть/однородность; `struct_2` — выученный кандидат, `struct_1` — архитектурный конфаунд; H1/H2/H-GE-1/H-NU-1/H-AB-1/H-AB-3 поддержаны, H3/H-CH-1/H-BI-1 опровергнуты; H4 не проверялась | [результаты](reports/2026-10-20-e02b-results.md) · [статья 005](articles/005-chto-perepis-nashla-v-morfoprostranstve.md) |
| E02c_replication | закрыто | 21.10 | репликация R-9 на сидах 142/242/342 | **отрицательно:** 0/3 новых сидов дают `struct_2`; seed142 → `struct_1`, seed242/342 → `uniform_dark`; контроль seed42 — `struct_2` 64/64; H-E02C-1 отвергнута, H-R3 подтверждён | [результаты](reports/2026-10-21-e02c-results.md) · [статья 006](articles/006-replikaciya-r9-struct2-ne-vosproizvelsya.md) · [summary](morphogenesis/experiments/E02c_replication/summary_e02c.json) |
| E02c_seed42_repro | закрыто | 21.10 | повтор обучения сида 42 замороженным кодом | **reproduced:** веса побитово равны каноническому прогону, перепись повтора — `struct_2` 64/64 (устойчивость 58/64); класс воспроизводится из сида, но не из рецепта (E02c 0/3 в силе) | [результаты](reports/2026-10-21-e02c-seed42-repro-results.md) · [статья 007](articles/007-struct2-vosproizvoditsya-iz-sida-no-ne-iz-recepta.md) · [summary](morphogenesis/experiments/E02c_replication/summary_e02c_seed42repro.json) |
| E02b_closures | закрыто | 21.10 | каналы, тело, асимметрия (inference-only) | **смешанный:** H-CH-3 и H-AB-2 подтверждены (ориентация возвращается 12/12; асимметрия лево/право −0.225 при выровненной массе), H-CH-2 и H-CH-4 опровергнуты (избыточность скрытых каналов; alive-канал сам несёт тело) | [результаты](reports/2026-10-21-e02b-closures-results.md) · [статья 008](articles/008-izbytochnost-kanalov-telo-i-strukturnaya-asimmetriya.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/closures_exploratory.json) |
| E02c_seed_decomposition | закрыто | 22.10 | декомпозиция сида: инициализация весов против порядка данных | **не разделено:** нужны оба фактора — A (init 42 / data 101) дал `uniform_dark` 64/64, B (init 101 / data 42) — `struct_1` 64/64; `struct_2` ноль в обоих, порог 52/64 не выполнен | [результаты](reports/2026-10-22-e02c-seed-decomposition-results.md) · [статья 009](articles/009-odin-seed-eto-dva-faktora.md) |
| E02b_alive_open | закрыто | 22.10 | открытый гейт живости (inference-only) | **refuted:** тело возвращается 12/12 (IoU 0.821 против 0.864) — текстура восстанавливает тело; вместе с H-CH-4 носители взаимны; асимметрия растёт с повреждением (ρ = −0.71) | [результаты](reports/2026-10-22-alive-open-results.md) · [статья 010](articles/010-telo-i-tekstura-vosstanavlivayut-drug-druga.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/alive_open_exploratory.json) |
| E02b_carriers2 | закрыто | 22.10 | носитель формы и дозу-ответ асимметрии (inference-only) | **смешанный:** H-CH-7 опровергнута (без visible тело возвращается 12/12, IoU 0.809; untrained теряет тело), H-AB-5 не подтверждена (знак −1 12/12, но медиана −0.354 против предсказанных ≤ −0.60 — горб около q≈0.5–0.63) | [результаты](reports/2026-10-22-carriers2-results.md) · [статья 011](articles/011-formu-neset-skrytoe-sostoyanie.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/carriers2_exploratory.json) |
| E02b_clusters3 | закрыто | 22.10 | избыточность скрытых каналов и кривая асимметрии | **смешанный:** H-CH-8 подтверждена (любая половина скрытых каналов восстанавливает тело 12/12, IoU 0.784/0.805; untrained 0/12), H-AB-6 не подтверждена (max|d| 0.551 против 0.63±0.05; при одинаковых срезах разброс 0.125 — величина не функция q) | [результаты](reports/2026-10-22-clusters3-results.md) · [статья 012](articles/012-izbytochnost-i-nestabilnaya-asimmetriya.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/clusters3_exploratory.json) |
| E02c_colab_repro | закрыто | 22.10 | независимое воспроизведение: обучение seed42 на другом стеке (Colab T4) | **не воспроизведено:** T4 дал `uniform_dark` 64/64 вместо `struct_2` 64/64 (untrained-контроль на месте — `struct_1` 64/64); сработала ветка плана «классы расходятся», карта «сид → класс» условна по стеку; механизм не установлен, сырые артефакты внешние | [результаты](reports/2026-10-22-colab-t4-repro-results.md) · [статья 013](articles/013-odin-sid-raznye-steki-raznye-klassy.md) · [план](reports/2026-10-22-colab-reproduction-plan.md) |
| E02c_seed_grid | закрыто | 22.10 | сетка «инициализация × порядок данных»: что держит `struct_2` | **опровергнута (в пользу класса):** H-E02C-6 не подтвердилась — init=101 не фиксирует `struct_1` (`death` 47/64 и `uniform_dark` 64/64), а при init=42 `struct_2` даёт 63/64 и 60/64 с разными данными; класс держит бассейн инициализации 42, данные решают удержание, ломает только data=101 | [результаты](reports/2026-10-22-e02c-seed-grid-results.md) · [статья 014](articles/014-inicializaciya-42-derzhit-strukturu.md) · [сетка](morphogenesis/experiments/E02c_replication/seed_grid.json) |
| E02b_lesion_minimal | закрыто | 22.10 | минимальный носитель и дисперсия асимметрии при фиксированном срезе | **смешанный:** H-CH-9 подтверждена — тело возвращается из **одного** канала `{14}` 12/12 (IoU 0.721), но `{6,7,8}` 0/12: избыточность не равномерная (информативны 2–4 и 10–14); H-AB-7 опровергнута — `std(d)` 0.167 и 0.114 при фиксированной геометрии, знак 24/24 | [результаты](reports/2026-10-22-lesion-minimal-results.md) · [статья 015](articles/015-odin-kanal-i-shum-asimmetrii.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/lesion_minimal_exploratory.json) |
| E02b_lesion_necessity | закрыто | 22.10 | необходимость информативных каналов | **H-CH-10 подтверждена:** `informative_only` {2,3,4,10–14} даёт тело 12/12 (IoU 0.826), `inert_only` {5–9} — 3/12 (0.395) при контроле 12/12; критерий разницы ≥ 8/12 выполнен (9/12) | [результаты](reports/2026-10-22-lesion-necessity-results.md) · [статья 016](articles/016-nositel-eto-podmnozhestvo-kanalov.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/lesion_necessity_exploratory.json) |
| E02b_lesion_core | закрыто | 22.10 | ядро внутри информативного набора каналов | **опровергнута:** удаление любого одного канала из {2,3,4,10–14} не стоит ничего — все 7 условий тело 12/12 (IoU 0.808–0.846 при контроле 0.823); ни один канал внутри набора не необходим, необходим весь набор (H-CH-10) | [результаты](reports/2026-10-22-lesion-core-results.md) · [статья 017](articles/017-vnutri-nositelya-polnaia-vzaimozameniaemost.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/lesion_core_exploratory.json) |
| E02b_asymmetry_variance | закрыто | 22.10 | источник разброса величины асимметрии | **inconclusive:** порог тела достигается на первом снимке, `dt` = +25 у всех 12 пар — измерение вырождено; побочно `std(d)` = 0.208 (у H-AB-7 — 0.167), разброс реален | [результаты](reports/2026-10-22-asymmetry-variance-results.md) · [пере-дизайн](reports/2026-10-22-asymmetry-variance-retry-plan.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/asymmetry_variance_exploratory.json) |
| E02b_asymmetry_variance_retry | закрыто | 22.10 | откуда разброс величины асимметрии (пере-дизайн) | **опровергнута:** ρ(d, t_plateau) = +0.434 при пороге 0.5, `std(dt)` 531.8 — скорость не объясняет величину; побочно на трёх наборах: правая сторона стабильна (`std` 0.010–0.025), левая — нет (0.104–0.203) | [результаты](reports/2026-10-22-asymmetry-variance-retry-results.md) · [статья 018](articles/018-pravaia-polovina-determinirovana.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/asymmetry_variance_retry_exploratory.json) |
| E02b_asymmetry_sides | закрыто | 22.10 | детерминизм сторон при срезе половины | **H-AB-9 подтверждена:** правая половина IoU 0.613–0.745 (`std` 0.036), левая 0.139–0.770 (`std` 0.154) — в 4.3 раза шире; `struct_2` 24/24 в обе стороны, разброс величины — левая половина | [результаты](reports/2026-10-22-asymmetry-sides-results.md) · [статья 019](articles/019-pravaia-vosstanavlivaetsia-vosproizvodimo.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/asymmetry_sides_exploratory.json) |
| E02b_left_outcomes | закрыто | 22.10 | форма левых исходов восстановления | **H-AB-10 опровергнута:** левая сторона — континуум (IoU 0.127–0.722, `std` 0.151, пик ≈ 0.2), правая — узкий пик (0.657–0.746, `std` 0.023); класс `struct_2` у обеих, метка не видит степени восстановления | [результаты](reports/2026-10-22-left-outcomes-results.md) · [статья 020](articles/020-levaia-storona-kontinuum.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/left_outcomes_exploratory.json) |
| E02b_carrier_pairs | закрыто | 22.10 | достаточна ли любая пара каналов внутри носителя | **H-CH-12 опровергнута:** 11 пар из 28 не дают тело (9 — 0/12), все 6 пар с каналом 3 — 12/12; `{14}` один достаточен, а `{2,14}` — 0/12, то есть достаточность немонотонна | [результаты](reports/2026-10-22-carrier-pairs-results.md) · [статья 021](articles/021-nositel-eto-kombinacii.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/carrier_pairs_exploratory.json) |
| E02b_carrier_ch13 | закрыто | 22.10 | достаточен ли канал {3} один | **подтверждена:** `{3}` один даёт тело 12/12 (IoU 0.839, `struct_2` 12/12) — якорь, объясняющий все пары с 3; второй достаточный в одиночку канал после `{14}` | [результаты](reports/2026-10-22-carrier-ch13-results.md) · [статья 021](articles/021-nositel-eto-kombinacii.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/carrier_ch13_exploratory.json) |
| E02b_carrier_ch15 | закрыто | 22.10 | каналы 3 и 14 как двойной якорь | **опровергнута:** шесть каналов без `{3,14}` дают тело 12/12 (IoU 0.831) — 3 и 14 достаточны по отдельности, но совместно не необходимы; у носителя нет якорной пары и малого ядра | [результаты](reports/2026-10-22-carrier-ch15-results.md) · [статья 021](articles/021-nositel-eto-kombinacii.md) · [артефакт](morphogenesis/experiments/E02b_morphospace/carrier_ch15_exploratory.json) |
| E03_injury, E04_topology, E05_aging, E06_narration, E07_control_ablation | не запускался | — | травма, топология, старение, нарратив, абляция | исторические entrypoint'ы; в текущую программу не входят | [registry](lab/registry.json) |
| E08_precision_horizon | идёт | 22–23.10 | режим точности и горизонт обучения: когда класс существует | класс — фаза траектории: TF32 даёт `uniform_dark` → `struct_2` → `struct_1` → `death` на 1000/2000/3000/4000 шагах, FP32 — `uniform_dark` → `struct_1` ×3; класс не зависит от длины роллаута | [карта](docs/research-map.md) · [протокол](docs/protocol.md) |

| E09_pond | план | 23.10 | среда с ценой, повреждениями, спорами и отбором: организация как процесс | ядро мира готово и покрыто 14 тестами (энергия, повреждения, споры, катастрофы-перемещения); цена ремонта откалибрована (0.02 → тело живёт ~500 шагов) | [дизайн](docs/world-design.md) · [программа](docs/open-ended-program.md) |

| E10_formal | идёт | 23.10 | формальные гипотезы (Lean): инварианты бюджета и порядка обновлений | доказано 10 теорем без зависимостей: сохранение бюджета на любой последовательности шагов и независимость от порядка асинхронных обновлений (F-BUDGET-1..3, F-ORDER-1) | [метод](docs/formal-method.md) · [инвентарь](lab/formal.json) |

<!-- ledger:end -->

**E02c — не новый вопрос, а проверка предыдущего.** Перепись нашла `struct_2`
на одном тренировочном сиде; репликация на сидах 142/242/342 проверяла, свойство
ли это рецепта R-9. Ответ отрицательный: **0/3** новых сидов дают `struct_2`
(seed142 → `struct_1`, seed242/342 → `uniform_dark`), контроль seed42 — 64/64.
H-E02C-1 отвергнута, H-R3 подтверждён: на горизонте 2000 `struct_2` привязан к
seed42. Это проверенное ограничение E02b, а не сбой переписи; H4 не открывается.

## Что это значит

- **Кольцо — калибровка, не жизнь.** Из шума оно не собирается, из цели
  распадается; обучение упирается в мёртвое поле. Гейт слоя 1 — 0/5, лучший
  gated f1 ниже потолка бесструктурного поля.
- **Морфопространство разрежено, но не пусто.** Два структурных класса
  воспроизводятся 64/64, однако 81% финальных состояний — смерть или однородность.
  `struct_1` совпадает с необученной архитектурой, поэтому выученным кандидатом
  остаётся только `struct_2`.
- **Ремонт — на уровне класса, а не побитовый.** Патчи вырастают в свой класс,
  но не восстанавливают исходный рисунок; у формы нет «памяти в скрытых каналах»,
  а прочность тела — порог, а не доза.
- **«Один живой аттрактор» ≠ «одна живая форма со структурой».** На 1296
  пересадках ни у одной из 12 моделей нет двух устойчивых живых форм одновременно;
  `struct_2` — единственная форма с собственной геометрией и ориентацией.
- **Мы не утверждаем жизнь, сознание или интеллект.** Допустимая формулировка —
  наблюдаемый класс поведения и его границы. H4 не проверялась; E02c не закрыт.

## Рукопись

[`manuscript/`](manuscript/README.md) — отдельное место для будущей научной
статьи. Она не переписывает статьи об отдельных экспериментах: `articles/` —
связный текст об одном эксперименте, `manuscript/paper.md` — накопительный
черновик публикации (v0.1, не подан).

Правило круга: **эксперимент → отчёт → статья → строка в README → кусочек в
рукопись → новая гипотеза.** Каждый закрытый результат обязан оставить в
рукописи абзац или подраздел, запись в [`CHANGELOG.md`](manuscript/CHANGELOG.md)
и строку в карте [`README.md`](manuscript/README.md); утверждения сверяются с
доказательствами в [`CLAIMS.md`](manuscript/CLAIMS.md). Проверка —
`python scripts/lab.py validate`.

## Что мы ищем

Вдохновение — работы Майкла Левина о теле как вычислительной среде и
целенаправленности без центрального планера. Мы не воспроизводим его
эксперименты и не переносим выводы на цифровую среду автоматически.

| Свойство | Что значит | Как проверяем |
| --- | --- | --- |
| Самоподдержание | состояние остаётся в жизнеспособной области без внешнего драйва | автономная развёртка без обучения и градиента |
| Ремонт | после повреждения система возвращается в тот же класс | ампутация, разрез, шум; возврат за 500 шагов |
| Адаптация | поведение меняется под возмущением, идентичность сохраняется | батарея возмущений, переключение классов |
| Граница и цель | система отличает себя от среды и держит setpoint | alive-маска, стресс-канал, гомеостаз |
| Цена поддержания | форма держится, только если её поддержание дешевле притока энергии | среда «пруд»: энергия, ремонт, смерть при нуле |
| Открытость | разнообразие не упирается в потолок, появляются новые стратегии | критерии §9 в [`docs/world-design.md`](docs/world-design.md), зафиксированы заранее |

Это чек-лист экспериментов, а не определение жизни. Утверждения разделены на три
уровня: **данные** (числа, артефакты, сиды — источник в `morphogenesis/experiments/`
и журнале), **гипотезы** (формулируются до запуска и могут быть опровергнуты) и
**метафора** (язык Левина задаёт вопросы, но не является доказательством).

## Как устроен стенд

```
┌──────────────────────────────────────────────────────────┐
│  Когнитивный контур (cognition/) — инструмент, не цель    │
│  protocol → agent_backends → action_validator → bridge    │
│        ▲                                        │         │
│        │ метрики / отчёты                        │ действия │
│        │                                        ▼         │
│  Ядро NCA (nca_core.py) ── stress, alive-mask, morphogens │
└──────────────────────────────────────────────────────────┘
```

- **`nca_core.py`** — ядро автомата: perception-layer, стресс с EMA, alive-маска
  из pre-update состояния, инъекции морфогенов.
- **`topology.py` / `topo_proxy.py`** — топологические инварианты, симметричный
  Chamfer, topo-proxy для градиента.
- **`train.py`** — обучение с truncated BPTT, пул состояний, NaN/OOM-гарды,
  атомарные чекпоинты с метаданными.
- **`experiment_manager.py`** — историческая серия E01–E07; текущая программа
  работает с E02/WP4, E02b и E02c.
- **`e02b_morphospace.py` / `e02c_replication.py`** — перепись и репликация;
  диагностика — `gate_layer1.py`, `wp4_*.py`.
- **`cognition/`** — протокол решений, эвристический агент, валидатор действий,
  мост к симулятору; это инструмент наблюдения, а не научный вопрос.

Детерминизм (порядок импортов, локальные `torch.Generator`, предзапусковый гейт)
описан в [`AGENTS.md`](AGENTS.md) и спецификации §9.2. Единственный источник
истины по механике стенда — [`docs/spec/MORPHOGENESIS_v5.6_Rev11.md`](docs/spec/MORPHOGENESIS_v5.6_Rev11.md).

## Структура репозитория

```
.
├── README.md                   # эта карта
├── AGENTS.md                   # контракт агентов: чтение, запуск, границы, цикл
├── manuscript/                 # будущая научная статья, собирается постепенно
│   ├── paper.md                # живой черновик (англ.)
│   ├── CHANGELOG.md            # вклады: дата, эксперимент, раздел
│   └── CLAIMS.md               # утверждение → доказательство → раздел
├── morphogenesis/
│   ├── config.py               # все гиперпараметры
│   ├── nca_core.py             # ядро NCA
│   ├── train.py                # цикл обучения
│   ├── e02b_morphospace.py     # перепись E02b
│   ├── e02c_replication.py     # репликация E02c
│   ├── e02c_census.py          # перепись E02c
│   ├── gate_layer1.py / wp4_*.py
│   ├── cognition/              # когнитивный контур
│   ├── tests/                  # pytest (полный набор — в CI)
│   ├── memory/                 # гипотезы, negative_results, decisions_log
│   ├── experiments/            # E01, E02, E02b, E02c — сырые артефакты
│   ├── checkpoints/            # веса (в git не попадают)
│   └── logs/                   # journal.jsonl — в git; остальное — нет
├── lab/                        # машинный control plane: registry, state, runs
├── scripts/                    # lab.py, export_portable.py, verify_portable.py,
│                               # контроль: check_links.py, check_section_refs.py,
│                               # verify_portable_package.py, retention_sweep.py,
│                               # сетка H-E02C-6: e02c_seed_grid.py, run_seed_grid_censuses.py
├── docs/
│   ├── spec/                   # активная спецификация; archived/ — только аудит
│   ├── benchmark/              # BENCHMARK_v0.md (draft, не опубликован)
│   └── dataset/                # DATASET_CARD.md (draft, не опубликован)
├── reports/                    # лабораторный журнал: карточки экспериментов
├── articles/                   # длинные статьи об отдельных экспериментах
├── library/                    # источники: publications, levin, hypotheses
├── kaggle/                     # ассеты Kaggle dataset/kernel (private)
├── colab/                      # ноутбук независимой проверки на T4 (сценарий A)
├── requirements.txt            # CPU-ядро
├── requirements-cuda.txt       # CUDA-сборка torch для RTX 3070
├── run_tests.py                # локальный CI: pytest + smoke_test
└── LICENSE
```

`dist/` (portable-пакет, lite-веса, Kaggle-архивы) собирается локально и в git
не попадает.

## Два входа

- **Человеческий:** [`reports/`](reports/README.md) — карточки экспериментов;
  [`articles/`](articles/README.md) — длинные тексты; [`library/`](library/README.md)
  — индекс публикаций, родословная NCA, конспекты; [`manuscript/`](manuscript/README.md)
  — будущая публикация.
- **Машинный:** [`AGENTS.md`](AGENTS.md), [`lab/registry.json`](lab/registry.json),
  [`lab/state.json`](lab/state.json), [`lab/runs/`](lab/runs/).

При расхождении README и registry/журнала прав registry/журнал/артефакт; README
исправляется, а не подгоняется.

## Установка

Нужен Python 3.11+ (проверено на 3.13.11); для обучения — CUDA-сборка torch.

```bash
git clone https://github.com/mak777uh/-.git morphogenesis-repo
cd morphogenesis-repo
python -m venv .venv
.venv/Scripts/python.exe -m pip install -U pip
# CPU (тесты и диагностика):
.venv/Scripts/python.exe -m pip install -r requirements.txt
# GPU RTX 3070 8GB (обучение):
.venv/Scripts/python.exe -m pip install --index-url https://download.pytorch.org/whl/cu124 --extra-index-url https://pypi.org/simple -r requirements-cuda.txt
```

`python -m pip` вместо `.venv/Scripts/pip` — чтобы гарантированно попасть в этот
venv. Если `torch.cuda.is_available()` вернул `False`, прилетела CPU-сборка:
детерминизм §9.2 на ней не проверить.

## Быстрый старт

Команды обучения и диагностики — из `morphogenesis/`; команды `scripts/lab.py` —
из корня.

```bash
# из morphogenesis/
python smoke_test.py                  # конфиг, шаг, инварианты стресса
python train.py --experiment E02 --seed 42
python wp4_reach_probe.py --arms R-9 --all-seeds --steps 1000 --every 50
```

Длинные прогоны — только через обёртку, чтобы остался манифест и замок:

```bash
# из корня
python scripts/lab.py run \
  --experiment E02c_R-9_s2000_seed242 --experiment-id E02c --arm R-9 --seed 242 \
  --steps 2000 --owner my-agent -- \
  python e02c_replication.py --seed 242 --steps 2000
python scripts/lab.py status
python scripts/lab.py validate
```

## Тесты и CI

```bash
# из morphogenesis/
python -m pytest tests/ -q
# из корня
python run_tests.py --quick
```

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) проверяет контракт
`lab.py validate --ci` (включая журнал README и карту рукописи), **пересчитывает
канонические артефакты E02b** (`e02b_verify.py`: классы, силуэт, ARI, H1/H3) и
CPU-тесты. Четыре проверки текста можно запускать и руками:

```bash
python scripts/check_links.py            # относительные ссылки публичных документов
python scripts/check_links.py --all      # весь репозиторий
python scripts/check_section_refs.py     # ссылки «§4.7» внутри рукописи
python scripts/check_references.py       # каждая ссылка References есть в индексе библиотеки
python scripts/check_reports_index.py      # каждый отчёт имеет строку в reports/README.md
python scripts/verify_portable_package.py  # целостность dist/e02b-portable (если собран)
python scripts/verify_manuscript_numbers.py  # числа §4.12–§4.14 против артефактов
```

Точное число тестов не дублируется в README: оно живёт в pytest.

## Правила журнала

Число имеет источник; критерии не переписываются после запуска; finish-строки не
дописываются задним числом; `met=true` означает наличие артефакта, а не научный
успех. README — карта, а не журнал: устаревшие строки переписываются, история
остаётся в git и `reports/`. Полный контракт — [`AGENTS.md` §6a](AGENTS.md);
цикл — [`AGENTS.md` §3a](AGENTS.md).

## Лицензия

MIT (см. [`LICENSE`](LICENSE)).

