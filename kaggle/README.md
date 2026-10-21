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
| `kernel-metadata.json` | метаданные kernel `mak777777uh/morphogenesis-e02b-portable-verify`: GPU включён, интернет выключен, датасет подключён как source. |
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

Отчёт Kaggle лежит в `dist/kaggle-report/e02b-portable/verify_report.json`
(`dist/` в git не едет). Воспроизводится **класс**, а не побитовое совпадение
дескрипторов: `max_abs_descriptor_diff = 125.0` на `n_pixels` — разные
устройства и версии torch дают разные числа, но тот же класс.

Отдельно: пакетная копия `census.json` санитизирована при экспорте (25
абсолютных путей автора → относительные), канонический файл не переписан. В
манифесте — оба sha: `datasets.census.sha256` (пакетный) и
`datasets.census.source_sha256` (канонический `e81678b6…`).


## Границы

- Пакет воспроизводит **закрытую** перепись E02b, а не открывает новую серию:
  ни обучения, ни новых гипотез, ни переписывания census.
- `struct_1` — архитектурный конфаунд, `struct_2` — кандидат на выученную
  морфологию. Формулировки «жизнь», «сознание», «интеллект» запрещены
  (AGENTS.md §3).
- Полные 514.5-МБ чекпоинты не публикуются: в датасете lite-версии, а sha256
  исходных файлов зафиксированы в `portable_manifest.json`.
