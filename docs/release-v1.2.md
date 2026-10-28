# Инструкция по публикации v1.2 — для агента-публикатора

> Передать целиком. Всё, что нужно, лежит на диске; ни один файл не надо искать заново.
> **Публиковать только после подтверждения владельца** (§3 контракта и §7 «Запрещено» AGENTS.md:
> внешняя публикация — только по явному «ок»).

## 0. Что публикуем в этот раз

| запись | действие | версия |
|---|---|---|
| **Препринт** (concept DOI `10.5281/zenodo.23669737`) | **новая версия** поверх v1.1 | v1.2, 28.10.2026 |
| **Код, отчёты, журнал** (concept DOI `10.5281/zenodo.23571609`) | **новая версия** поверх v1.0 | v1.1, 28.10.2026 |
| **Канонические веса** (concept DOI `10.5281/zenodo.23654173`) | **не трогаем** — веса не менялись | остаётся v1.1 |
| **Набор данных серий** (новый concept DOI) | **новая запись**, если владелец одобрит | v1.0, 28.10.2026 |

Терминология Zenodo: у каждой записи есть **concept DOI** (всегда указывает на последнюю версию) и DOI
конкретной версии. Новая версия заливается командой «New version» внутри записи — тогда concept DOI
сохраняется, а у версии появляется свой DOI. **Не создавайте новую запись** для препринта и кода: иначе
история цитирования разорвётся.

## 1. Препринт v1.2

### Файлы (готовы)

| файл | путь | размер |
|---|---|---|
| PDF (собирается заново, см. ниже) | `C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\_hourly\grants\arxiv-preprint-v1.2.pdf` | ~0.5 МБ ожидается |
| LaTeX-исходник (архив) | `...\_hourly\grants\arxiv-tex-v1.2.zip` | ~0.35 МБ |
| исходник до сборки | `...\_hourly\grants\arxiv-tex\` (`main.tex`, `refs.bib`, `fig1..4.png`) | — |

### Как собрать PDF (на машине без TeX)

На этой машине **нет** `pdflatex`/`xelatex`/`pandoc` (проверено). Собирать на любой среде с TeX Live:

```bash
cd arxiv-tex
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Требуется `pdflatex` (в `main.tex` стоят `inputenc`/`fontenc` и пакет `newunicodechar` — файл
специально сделан pdflatex-совместимым, **не** переключайте на `xelatex` без нужды).
Проверка после сборки: страниц **13–16** (v1.1 было 13, добавляются подраздел и два абзаца), в логе нет
`! LaTeX Error`, все `\ref`/`\cite` разрешились (нет `??`).

Упаковать исходник:

```bash
cd arxiv-tex && zip -r ../../_hourly/grants/arxiv-tex-v1.2.zip main.tex refs.bib fig1.png fig2.png fig3.png fig4.png
```

### Метаданные записи препринта

- **Title:** `Four conditions for a self-maintaining organisation in a digital medium`
- **Authors:** Ilya Vladimirov (Independent researcher), ORCID `0009-0007-2996-3387`
- **Publication date:** 2026-10-28
- **Version:** `v1.2`
- **Resource type:** Publication → Preprint
- **License:** CC-BY-4.0
- **Language:** English
- **Description (вставлять как есть):**

> Preprint v1.2. Four pre-registered conditions for a self-maintaining organisation in a world of digital
> cells: a reproduction unit smaller than the whole, a price for a heritable trait, a rule for when two types
> meet, and inheritance of the environment. v1.2 adds the measured magnitude of the price (−0.374, 95 % CI
> [−0.396, −0.266]; the pre-registered bar of 0.3 is not reached, so the claim is closed), the finding that
> the price belongs to the investment channel (routing the same trait to update frequency gives +0.001,
> CI [−0.080, +0.082]), and two coexistence mechanisms — mortality proportional to a lineage's excess share
> and desynchronisation of updates — which raise effective lineages from 1.52 to 26.06 together, with a
> log-scale interaction of +0.445 [+0.350, +0.566]. Four pre-registered predictions of the lead failed and
> are reported as failures. Not peer reviewed. Previous versions: v1.1 (10.5281/zenodo.23694918),
> v1.0 (10.5281/zenodo.23669738).

- **Keywords:** digital life; self-maintenance; opportunity for selection; pre-registration; null models;
  cellular worlds; coexistence; negative results
- **Related identifiers:** `isNewVersionOf` → `10.5281/zenodo.23694918`; `isSupplementedBy` → DOI кода
  (запись с кодом) и DOI данных (если будет создана, см. §4).

## 2. Код и отчёты v1.1

- **Что заливать:** архив рабочего дерева `repo/` на коммите, куда указывает тег/HEAD после публикации
  (см. §5), **без** `morphogenesis/experiments/` (артефакты слишком велики — они идут отдельной записью,
  §4), **без** `.venv`, `__pycache__`, весов `.pt`.
- **Размер:** ~10–12 МБ (v1.0 было 10.3 МБ).
- **Тип:** Software. **Лицензия:** MIT.
- **Версия:** `v1.1`. **Дата:** 2026-10-28.
- **Описание:** взять из `repo/README.md` (раздел «What this repository is»), плюс строка:
  «v1.1 adds the kill-the-winner, trait-update-channel and additivity series, the prediction ledger with four
  recorded failures, and six new CI gates (commit-claim accounting, Lean integrity, paired comparison).»

## 3. Веса — не трогать

`10.5281/zenodo.23654174` (6.03 ГБ, 12 файлов `nca_final.pt` + `world_base_rule.pt`) не менялись.
Ничего не перезаливать.

## 4. Набор данных (новое, если владелец одобрит)

**Что:** ровно четыре серии v1.2, не весь каталог. Всего **120 JSON**, **73.5 МБ**
(посчитано: 19.76 + 20.87 + 9.41 + 23.50 МБ; Zenodo даёт 50 ГБ на запись, запас огромный).

| серия | путь (от `repo/`) | файлов |
|---|---|---|
| kill-the-winner, три плеча | `morphogenesis/experiments/E09_pond/w2bud_killwinner/` | 30 |
| подтверждающая серия | `morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm/` | 30 |
| канал обновления | `morphogenesis/experiments/E09_pond/w2bud_trait_update/` | 20 |
| квадрат 2×2 | `morphogenesis/experiments/E09_pond/w2bud_additivity/` | 40 |
| агрегаты | `..._matrix.json` рядом с каждой серией | 4 |

**Плюс два файла, без которых данные непонятны:**
- `lab/predictions.json` — журнал предсказаний (включая четыре провалившихся);
- `reports/2026-10-28-additivity-plan.md`, `reports/2026-10-28-asynchrony-coexistence-plan.md`,
  `reports/2026-10-27-killwinner-plan.md`, `reports/2026-10-27-killwinner-confirm-plan.md` — пре-регистрации.

**Тип:** Dataset. **Лицензия:** CC-BY-4.0. **Версия:** `v1.0`. **Дата:** 2026-10-28.
**Описание:** «Per-run artifacts for the four v1.2 series: each file contains the full command, seed,
environment and summary of one run; aggregates are rebuilt from them by scripts in the code record.»

**Проверка целостности перед загрузкой** (обязательно, иначе это не данные, а мусор):

```powershell
# из корня repo
Get-ChildItem morphogenesis\experiments\E09_pond\w2bud_killwinner*,w2bud_trait_update,w2bud_additivity -Recurse -Filter *.json |
  Get-FileHash -Algorithm SHA256 | Export-Csv ..\_zenodo\dataset-v1.2.sha256.csv -NoTypeInformation
```

CSV кладётся **в ту же запись** как `CHECKSUMS-v1.2.csv`.

## 5. Порядок действий (строго в этом порядке)

1. Владелец подтверждает публикацию (без этого шага дальше не идти).
2. Собрать PDF (§1) и архив исходника; проверить число страниц и отсутствие `??`.
3. Создать **новую версию** записи препринта (concept `10.5281/zenodo.23669737`), залить PDF + zip,
   заполнить метаданные из §1, опубликовать, записать новый DOI версии.
4. Создать **новую версию** записи кода (concept `10.5281/zenodo.23571609`), залить архив, лицензия MIT,
   опубликовать, записать DOI.
5. Если одобрены данные — создать **новую запись** по §4, опубликовать, записать concept DOI и DOI версии.
6. **Вернуть в репозиторий** полученные DOI — без этого следующий препринт снова будет ссылаться на v1.1:

```powershell
cd C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo
python scripts\zenodo_link.py --weights-doi <тот же> --concept-doi <новый concept кода>
# затем вручную (скрипт этого не умеет): CITATION.cff → preferred-citation.doi = DOI препринта v1.2,
# identifiers → DOI кода v1.1, references → DOI данных; docs\deposit.md → новая строка; README → ссылка «Preprint v1.2».
python scripts\lab.py validate && python scripts\check_links.py --all
```

7. Тег после публикации (не двигать задним числом): `git tag -a v1.2 -m "preprint v1.2 + code v1.1"`.

## 6. Если что-то не сходится

- **PDF собирается с ошибкой** — не «исправляйте» текст препринта: верните лог, правит ведущий.
- **Zenodo отказывает по размеру** — проверьте, что в архив кода не попали `experiments/` и `.pt`
  (главная причина «внезапных 300 МБ»).
- **DOI версии не появился** — запись осталась в состоянии `draft`; публикация не выполнена, повторите шаг.
- **Конфликт с уже существующей версией** — не создавайте вторую запись, используйте «New version»
  внутри существующей.

## 7. Чего делать нельзя

- Менять текст препринта под видом «правки опечаток», если это меняет числа или выводы.
- Публиковать веса заново (6 ГБ без причины).
- Создавать новую concept-запись для препринта или кода.
- Заливать `_hourly/`, `_zenodo/`, токены, `.env`, личные данные.
- Указывать в метаданных «peer reviewed».
