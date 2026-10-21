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
| Статус | dataset и kernel **private** до решения владельца о публикации (D4/D5); public — только после review и санитизации census. |
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


## Границы

- Пакет воспроизводит **закрытую** перепись E02b, а не открывает новую серию:
  ни обучения, ни новых гипотез, ни переписывания census.
- `struct_1` — архитектурный конфаунд, `struct_2` — кандидат на выученную
  морфологию. Формулировки «жизнь», «сознание», «интеллект» запрещены
  (AGENTS.md §3).
- Полные 514.5-МБ чекпоинты не публикуются: в датасете lite-версии, а sha256
  исходных файлов зафиксированы в `portable_manifest.json`.
