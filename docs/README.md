# Документы: что читать и в каком порядке

Индекс документации. Правило: один вопрос — один документ; числа живут в
артефактах (`morphogenesis/experiments/`, `lab/`), а не в прозе.

## Сначала — путь

| Документ | Зачем |
|---|---|
| [`path.md`](path.md) | **История мысли**: четыре поворота (цель → карта → репликация → фаза → среда), что нашли, что признали ошибкой, что сохраняем. Начинать с него. |

## Где мы сейчас

| Документ | Зачем |
|---|---|
| [`research-map.md`](research-map.md) | Вопросы → эксперименты → артефакты, лестница по цене, сценарии чтения результатов, слепое пятно. |
| [`plan-alive.md`](plan-alive.md) | **Текущая программа**: цель «увидеть живое», фазы P0–P4, математика вместо перебора, критерии успеха. |
| [`prior-art-alive.md`](prior-art-alive.md) | **Что уже проверено до нас**: таблица «вопрос → известно → что не делаем → что проверяем → ожидание». |
| [`pool-deferred.md`](pool-deferred.md) | **Пул отложенного**: снятые с плана идеи с условием возврата (машинная версия — `lab/pool.json`). |
| [`protocol.md`](protocol.md) | Правила измерения v1.2: три координаты класса, пять контролей, OOD, тривиальность по трём осям, габитуация по трём критериям. Обязателен. |
| [`world-design.md`](world-design.md) | Спецификация среды «пруд»: энергия, повреждения, споры, катастрофы, контроли, критерии успеха. |
| [`open-ended-program.md`](open-ended-program.md) | Зачем менять постановку: пять отсутствующих ингредиентов и три шага к среде, где явлению есть где быть. |

## Контракт и инфраструктура

| Документ | Зачем |
|---|---|
| [`../AGENTS.md`](../AGENTS.md) | Контракт для агентов: цикл из восьми стадий, след эксперимента, роли, запреты. |
| [`artifact-contract-plan.md`](artifact-contract-plan.md) | План слоёв артефактов v1.1 (манифест → карточка → индекс), CI-гейты, теги. |
| [`agents-transformation-plan.md`](agents-transformation-plan.md) | Как менять работу агентов, не ломая слои: интерфейсы, фазы, риски. |
| [`vk-cloud-gpu-quickstart.md`](vk-cloud-gpu-quickstart.md) | Внешний GPU: пошаговая инструкция (когда понадобится второй стек). |

## Спецификации и упаковка

| Документ | Зачем |
|---|---|
| [`spec/MORPHOGENESIS_v5.6_Rev11.md`](spec/MORPHOGENESIS_v5.6_Rev11.md) | Техническая спецификация стенда (архитектура, каналы, инварианты). |
| [`spec/archived/`](spec/archived/) | Старые ревизии спецификации, сохранены как история. |
| [`benchmark/BENCHMARK_v0.md`](benchmark/BENCHMARK_v0.md) | Черновик бенчмарка (не опубликован). |
| [`dataset/DATASET_CARD.md`](dataset/DATASET_CARD.md) | Карточка датасета для будущего депозита (не опубликован). |

## Чего здесь нет

Отчётов и статей: они живут в [`reports/`](../reports/README.md) и
[`articles/`](../articles/README.md). Рукопись — в
[`manuscript/`](../manuscript/README.md).

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

## Проверки текста

```bash
python scripts/check_links.py               # относительные ссылки публичных документов
python scripts/check_links.py --all         # весь репозиторий
python scripts/check_section_refs.py        # ссылки «§4.7» внутри рукописи
python scripts/check_references.py          # каждая ссылка References есть в индексе библиотеки
python scripts/check_reports_index.py       # каждый отчёт имеет строку в reports/README.md
python scripts/verify_portable_package.py   # целостность dist/e02b-portable (если собран)
python scripts/verify_manuscript_numbers.py # числа §4.12–§4.14 против артефактов
```
