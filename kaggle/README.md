# Kaggle assets — E02b portable verification

Здесь лежат только **ассеты публикации**, а не сам пакет. Пакет собирается
локально и в git не попадает (`.gitignore`: `dist/`):

```bash
python scripts/export_portable.py --out dist/e02b-portable
```

## Что где

| Файл | Смысл |
| --- | --- |
| `dataset-metadata.json` | метаданные датасета `mak777777uh/morphogenesis-e02b-portable` (MIT, lite-чекпоинты + census). |
| `kernel-metadata.json` | метаданные kernel `mak777777uh/morphogenesis-e02b-portable-verify`: **GPU выключен** (проверенный прогон v2 — CPU; GPU-режим не проверялся), интернет выключен, датасет подключён как source. |
| Статус | dataset (версия 2) и kernel (версия 2) **private** до решения владельца (D4/D5). Санитизация census выполнена; для public остаётся решение владельца и review. |
| `verify_e02b.ipynb` | notebook: находит датасет, копирует пакет в `/kaggle/working`, запускает `verify_portable.py --mode smoke`, печатает версии и PASS/FAIL. |

Notebook ничего не устанавливает: `torch`/`numpy`/`scipy` уже есть в образе
Kaggle, репозиторий не клонируется, секретов и абсолютных путей автора нет.
`/kaggle/input` и `/kaggle/working` — стандартные точки монтирования платформы.

## Публикация (вручную, после review)

Kaggle Dataset хранит файлы плоско, а portable-пакет — дерево каталогов,
поэтому пакет уезжает **одним архивом** `e02b-portable.zip`; notebook
распаковывает его в `/kaggle/working`.

```bash
python scripts/export_portable.py --out dist/e02b-portable
python scripts/pack_kaggle_dataset.py \
  --package dist/e02b-portable --out dist/kaggle-dataset
kaggle datasets create -p dist/kaggle-dataset          # первый раз (private по умолчанию)
kaggle datasets version -p dist/kaggle-dataset -m "E02b portable $(git rev-parse --short HEAD)"
```

Kernel пушится из этого каталога (в нём метаданные и notebook):

```bash
kaggle kernels push -p kaggle
kaggle kernels status mak777777uh/morphogenesis-e02b-portable-verify
```

Slug владельца — **Kaggle username**, а не GitHub username: `mak777777uh`.

**Грабли (проверено на ошибке).** `kernels_push` читает метаданные из **того**
каталога, который ему дали. Копия в `dist/kaggle-kernel-private/` отстала от
`kaggle/kernel-metadata.json` (в ней был старый id без `portable`), и push падал с
`409 Conflict: Your kernel title does not resolve to the specified id`. Перед
пушем синхронизируй каталог с `kaggle/kernel-metadata.json`, а не правь метаданные
в `dist/`.

## Проверки

| Где | Что | Итог |
| --- | --- | --- |
| Локально (RTX 3070, CUDA) | `verify_portable.py --mode smoke` на собранном `dist/e02b-portable`, 3 семейства × 16 стартов × 2000 шагов | **PASS**: 48/48 классов, 0 расхождений, 367 с |
| Kaggle (kernel v2, CPU) | тот же smoke на датасете версии 2, собранном из коммита `b8ed0d0` | **PASS**: 48/48 классов, 0 расхождений, 713 с, sha пакетной переписи `01a68fb0…` |
| Целостность пакета | `scripts/verify_portable_package.py` на `dist/e02b-portable` (2026-10-22) | **PASS**: 29 записей `files[]` совпали по sha256 и размеру, census `01a68fb0…` ≠ канонический `e81678b6…` (не переписан), абсолютных путей в 16 текстовых файлах нет |

**GPU-режим kernel не проверялся.** В `kernel-metadata.json` стоит
`enable_gpu: false`, потому что проверенный прогон v2 — CPU; если включать GPU,
нужен новый прогон и новый PASS, иначе опубликованный kernel будет обещать
конфигурацию, которой нет в отчёте.

Отчёт Kaggle лежит в `dist/kaggle-report/e02b-portable/verify_report.json`
(`dist/` в git не едет). Воспроизводится **класс**, а не побитовое совпадение
дескрипторов: `max_abs_descriptor_diff = 125.0` на `n_pixels` — разные
устройства и версии torch дают разные числа, но тот же класс.

Отдельно: пакетная копия `census.json` санитизирована при экспорте (25
абсолютных путей автора → относительные), канонический файл не переписан. В
манифесте — оба sha: `datasets.census.sha256` (пакетный) и
`datasets.census.source_sha256` (канонический `e81678b6…`).

## Второй пакет: воспроизведение обучения (Gate 3)

Инференс-пакет отвечает на вопрос «те же веса на другом стеке дают тот же класс».
Обучение — другая ось: меняется траектория, из которой выросли веса. Для неё есть
отдельный пакет:

```bash
python scripts/export_train_repro.py --out dist/e02c-train-repro
```

Внутри — код обучения и переписи байт-в-байт, рецепт `ARMS["R-9"]`, замороженные
центроиды E02b и `reference.json` с эталоном канонического прогона
(`best_loss` 1.104736089706421, `alive_fraction_final` 0.34686279296875,
sha256 весов, перепись 64/64). Пакет самодостаточен: `pip install -r
requirements-train.txt`, дальше две команды из его `README.md`.

Критерий и правила запуска заморожены в
[`reports/2026-10-21-repro-independent-plan.md`](../reports/2026-10-21-repro-independent-plan.md):
класс `struct_2 ≥ 52/64` при устойчивости `≥ 0.80`, побитовое совпадение весов
**не** требуется. Датасет для Kaggle собирается тем же
`scripts/pack_kaggle_dataset.py --package dist/e02c-train-repro`, но отдельным
slug — смешивать train-repro и inference-пакет в одном датасете нельзя.
Smoke проверен локально на CPU: 5 шагов дают чекпоинт и пару `start`/`finish` в
`logs/journal.jsonl` (полный пакет — 21 файл, 16 МБ, из них 15.5 МБ — `census.json`).


## Границы

- Пакет воспроизводит **закрытую** перепись E02b, а не открывает новую серию:
  ни обучения, ни новых гипотез, ни переписывания census.
- `struct_1` — архитектурный конфаунд, `struct_2` — кандидат на выученную
  морфологию. Формулировки «жизнь», «сознание», «интеллект» запрещены
  (AGENTS.md §3).
- Полные 514.5-МБ чекпоинты не публикуются: в датасете lite-версии, а sha256
  исходных файлов зафиксированы в `portable_manifest.json`.
