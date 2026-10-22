# Colab: независимое воспроизведение E02b (сценарий A)

Здесь лежит ноутбук, исполняющий
[`reports/2026-10-22-colab-reproduction-plan.md`](../reports/2026-10-22-colab-reproduction-plan.md):
перепись E02b на портативном пакете (18 МБ) на **другом железе** (Tesla T4) и
**другой версии torch**. Это шаг к гейту публикации: до сих пор всё, кроме
Kaggle-CPU-прогона, шло на одной машине.

## Зачем Colab, а не Kaggle

Для Kaggle GPU нужна верификация телефона, которая не прошла; Colab даёт
бесплатный T4 без неё. Kaggle-проверка (CPU, 48/48 классов) остаётся в силе и
лежит в [`../kaggle/README.md`](../kaggle/README.md).

## Что проверяет сценарий A

- lite-чекпоинты (152 602 байта на модель) переносятся и воспроизводят **те же
  классы** переписи E02b на T4;
- отчёт содержит стек (`torch.__version__`, имя устройства) и `status`;
- **не** проверяет обучение и **не** считает частоту `struct_2`: разные железные
  ансамбли не смешиваются.

## Как запустить (один раз)

1. Runtime → Change runtime type → **T4 GPU**.
2. Положить `dist/kaggle-dataset/e02b-portable.zip` на свой Google Drive в папку
   `MyDrive/morphogenesis/`. Папку создать, если её нет.
3. Открыть [`verify_e02b_t4.ipynb`](verify_e02b_t4.ipynb) в Colab
   (File → Upload notebook) и выполнить ячейки по порядку.
4. Забрать `MyDrive/morphogenesis/verify_report.colab.json`.

Отчёт кладётся в репозиторий как
`dist/kaggle-report/colab/verify_report.json` (в git не едет — `dist/`
игнорируется), а выводы — в отчёт проекта со ссылкой на стек.

## Сценарий B (по решению владельца)

Полная перепись известных сидов (`E02c_R-9_s2000_seed42`,
`WP4_R-9_s2000_seed101`, `WP4_R-9_s2000_seed142`) на тех же весах, но на T4:
проверка переноса **карты «сид → класс»** между железом. Ожидания: seed42 →
`struct_2` 64/64, seed101 и seed142 → `struct_1`. Нужны 3 чекпоинта по 540 МБ на
Drive; ячейка 5 в ноутбуке включается флагом `RUN_FULL = True`.

## Границы

- Colab не заменяет независимое воспроизведение **обучения**: там нужен прогон
  тренировки на другом стеке (`repro_independent`, пакет
  `scripts/export_train_repro.py` готов).
- Классы сравниваются с локальной переписью; расхождение дескрипторов
  записывается как есть, а не подгоняется.
- Формулировки о жизни/сознании/интеллекте запрещены (AGENTS §3).

## Карточка прогона: что именно приезжает в git

`verify_report.colab.json` лежит в `dist/` и в git не едет — значит после
прогона в репозитории не остаётся ни окружения, ни привязки к коммиту кода.
Для этого есть [`morphogenesis/colab_run_card.py`](../morphogenesis/colab_run_card.py):
он собирает маленькую карточку (единицы килобайт) и её **можно и нужно**
коммитить.

Формат каталога:

```
colab/<YYYY-MM-DD>_<slug>/
├── run.ipynb          # исполненный ноутбук — рецепт прогона
└── run_card.json      # окружение, коммит кода, дизайн, результат, sha256
```

В ноутбуке:

```python
import sys; sys.path.insert(0, "/content/repo/morphogenesis")
from colab_run_card import build_card
card = build_card(
    summary_path="/content/summary_colab_seed42.json",
    experiment="E02c_colab_repro_seed42",
    design={"family": "E02c_R-9_s2000_seed42", "seeds": "0-63", "steps": 2000},
    repo_dir="/content/repo",
    repo_url="https://github.com/mak777uh/-",
    census_path="/content/census_colab_seed42.json",
    out_path="/content/run_card.json",
)
```

В карточке: `gpu`, `torch`, `cuda`, `python`, `repo.commit`, дизайн, `stats`,
контроли, вердикт, sha256 сводки и census. Этого достаточно, чтобы потом
воспроизвести прогон и доказать, на каком коде и железе он сделан.

Доставка в git — два пути, оба без весов:

1. **Безопасный:** скачать `run_card.json` (и `.ipynb`) из Colab, положить в
   локальный `colab/<дата>_<slug>/`, коммит делает агент. Токенов нигде нет.
2. **Прямой push (опционально):** `GH_TOKEN` в секретах Colab (fine-grained PAT,
   только `contents:write`), пуш в ветку `colab/<slug>` — агент вливает. Токен в
   ноутбук и в git не попадает.

Не коммитить: `*.pt`, `census_*.json`, вывод `!pip`, TensorBoard.
