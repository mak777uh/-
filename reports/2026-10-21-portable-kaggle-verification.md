# Portable/Kaggle-проверка E02b: что именно проверено и чем это не является

- **Дата:** 2026-10-21
- **Предмет:** portable inference-пакет E02b (`dist/e02b-portable`, в git не едет),
  Kaggle Dataset версии 2 и Kaggle Kernel версии 2
- **Связанные документы:** [`AGENTS.md`](../AGENTS.md) §5a (диск/веса),
  [`kaggle/README.md`](../kaggle/README.md) (как собирать и пушить),
  [`docs/dataset/DATASET_CARD.md`](../docs/dataset/DATASET_CARD.md) (карточка датасета),
  [`reports/2026-10-20-e02b-results.md`](2026-10-20-e02b-results.md) (сама перепись)
- **Артефакты:** `portable_manifest.json` внутри пакета (30 файлов + сам манифест),
  `verify_report.json` (CPU, Kaggle), `verify_report.local.json` (CUDA, локально);
  оба отчёта лежат в `dist/` и в git не попадают

## Что собрано

| Параметр | Значение |
| --- | --- |
| Коммит-источник | `b8ed0d0be97882e8decd5a8e08d6d2c77bfae435` (в момент сборки в дереве было 2 чужих несохранённых файла — `git_dirty: true`, это записано в манифесте) |
| Файлов | 30 (+ `portable_manifest.json`) |
| Объём | 17 961 042 байт (17.1 МиБ) |
| Чекпоинтов | 12 (lite: 152 602 байта каждый против 539 495 742 байт полного `nca_final.pt`) |
| Данные | `census.json` (832 развёртки, 15.0 МБ), `class_centroids_frozen.json` (k=5), `wp4_ablations.json` |
| Санитизация census | 25 абсолютных путей автора переписаны в относительные, неразрешённых 0; числа, классы и дескрипторы не менялись |
| Хеши census | пакетный `01a68fb039a05b37…`, канонический исходник `e81678b603ddc4de…` (оба в манифесте) |

Санитизация сделана **на экспорте**, а не правкой канона: канонический
`census.json` остаётся байт-в-байт тем же, а публикуемая копия отличается только
строками-путями. Экспорт падает, если после замены остался абсолютный путь вне
корня репозитория.

## Проверки

| Где | Устройство | Прогон | Итог |
| --- | --- | --- | --- |
| Локально (RTX 3070 Laptop) | CUDA, torch 2.6.0+cu124 | `verify_portable.py --mode smoke`: 3 семейства × 16 стартов × 2000 шагов = 48 развёрток | **PASS**, 48/48 классов, 0 расхождений |
| Kaggle Kernel v2 | CPU, образ Kaggle | тот же smoke на датасете версии 2 | **PASS**, 48/48 классов, 0 расхождений, 712.6 с, 14.8 с на старт |

Проверяемые семейства в smoke: `WP4_R-9_s2000_seed42`, `WP4_R-9_s2000_seed101`,
`untrained_current_arch` — по 16/16 совпадений класса в каждом.

Расхождение чисел при этом остаётся и не скрывается:
`max_abs_descriptor_diff = 125.0` на `n_pixels`. Разные устройства и версии
torch дают разные дескрипторы; совпадает **класс**, а не побитовое значение.

## Чем это является и чем это не является

**Является:**
- независимой по стеку проверкой переписи E02b: другой процессор, другая версия
  torch, другой образ, без доступа к репозиторию (в датасете только пакет);
- проверкой того, что lite-чекпоинт (152 КБ) несёт ту же функцию, что полный
  (539 МБ): forward lite побитово равен полному на CPU (это отдельный тест
  `morphogenesis/tests/test_portable_export.py`);
- проверкой, что публикуемый артефакт не содержит путей и секретов автора.

**Не является:**
- независимым воспроизведением **обучения** (серии E02c и повтор сида 42 шли на
  той же машине; для гейта подачи нужен другой стек и другая машина);
- доказательством побитовой эквивалентности между устройствами: совпадает класс,
  а `n_pixels` расходится на 125;
- публикацией: dataset и kernel остаются **private** до решения владельца (D4/D5).

## Как воспроизвести проверку

```bash
# из корня репозитория
python scripts/export_portable.py --out dist/e02b-portable
cd dist/e02b-portable && python verify_portable.py --mode smoke --device cpu
```

Kaggle-сторона (нужен свой токен; slug владельца — Kaggle username):

```bash
python scripts/pack_kaggle_dataset.py --package dist/e02b-portable --out dist/kaggle-dataset
kaggle datasets version -p dist/kaggle-dataset -m "E02b portable $(git rev-parse --short HEAD)"
kaggle kernels push -p kaggle
kaggle kernels status mak777777uh/morphogenesis-e02b-portable-verify
```

Грабли: `kernels_push` читает `kernel-metadata.json` **из переданного каталога**;
устаревшая копия в `dist/` с другим id даёт `409 Conflict`. Синхронизируй каталог
с `kaggle/kernel-metadata.json` перед пушем.
