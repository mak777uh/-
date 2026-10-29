<!-- Крестовый аудит: внешнее мнение, не приговор.
     Автор: ведущий научной лаборатории (агент deepseek), дата 2026-10-29.
     Репозиторий: mak777uh/flowguard-spec — спецификация продукта FlowGuard (замыкание и единственная контрольная точка).
     Прочитать за 30 секунд: раздел «Пять пунктов» в конце.
-->

# Внешний аудит `flowguard-spec`

Репозиторий: `C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\_cross_audit\flowguard-spec`
Состояние: один коммит `c06d28b` (2026-10-29 21:06 +03:00), `git rev-list --count HEAD` = 1.
Аудит — только чтение и запуск; ничего в репозитории не менял.

## Что проверено и как

1. **Все 11 шагов `guards.yml` прогнаны локально** (`python`/`bash` из Git for Windows, CPython 3.13.11). Восемь зелёных, три красных: `lab/check-artifact-refs.py` (2 висячие ссылки), `lab/check-metric-digests.py --cards` (99 нерешённых дайджестов), `lab/selftest-guards.sh` (1 из 11 контролей). `lab/check-secrets.sh` — `RESULT: clean`.
2. **Негативные контроли отдельно**: `bash lab/selftest-guards.sh` → `controls passed: 10 failed: 1`, падает контроль `line-endings`.
3. **Схемы против артефактов**: `python tools/fg_schema_check.py --claim|--inventory` по всем 20 файлам в `fixtures/attack/`, `fixtures/verify-probe/`, `fixtures/schema-check/`. Нашёл 3 расхождения (ниже M10, а также намеренные `a2-inv.json`, `c1-claim.json`).
4. **Верификатор вручную**: `python tools/fg_verify.py` на `k-proven.json`/`a6-inv.json`, на синтетических claim'ах (проверка `not_claimed` по уровням, подмена `declared_control_point` с префиксом и без).
5. **Инструменты, которые сами себя объявляют источником чисел**: `tools/fg_status.py --check`, `tools/fg_readiness.py`, `tools/fg_audit.py`, `tools/fg_bundle.py verify --bundle fixtures/sample-bundle`, `lab/claims-map.py`, `lab/cross-family-due.py`, `lab/e-m36-run.py`, `lab/e-m42-run.py`, `lab/e-m12-run.py`, `lab/check-interop.py`.
6. **Пересчёт дайджестов вручную**: `sha256(bundle.json)` = `6e09060c…` (5087 байт), адрес из `manifest.sha256` = `5336c02a…`, `sha256(nc_vocabulary.text)` = `bdc36c88…` — совпал и с `docs/NOT-CLAIMED.md`, и с полем в бандле.
7. **Свой сканер ссылок по всем `*.md`** (не только по трём каталогам, которые смотрит `lab/check-links.py`): 152 ссылки, 11 битых.
8. **Проверка якорей коммитов**: 67 карточек `lab/experiments/*.md` → 34 различных `base_commit`; `git cat-file -e <sha>^{commit}` → **0** резолвится.
9. **Поиск протухающих констант**: `date.today|datetime.now|utcnow` в `tools/` и `lab/` — только два места (`tools/merge_inventory.py:248`, `lab/cross-family-due.py:56`), тесты от настенных часов не зависят; жёстко зашитые даты — только как `target_lock`-пины (`flowguard-sample@2026-10-27`, `ironclaw@2026-10-28`).

## Находки

### Сломает результат

**R1. Вердикт: спецификация и код описывают два разных словаря, и ни один документ их не отображает.**
`docs/FLOWGUARD-MASTER-v2.md:42-49` задаёт лестницу `PROVEN(R)` / `ENFORCED_TESTED(R)` / `INCONCLUSIVE` / `INVALID`. `tools/fg_verify.py:22` содержит `LEVELS = ["CONSISTENT_DECLARED", "SCOPED_ASSURANCE", "PROVEN"]` (+ `INVALID`). Слово `ENFORCED_TESTED` не порождает ни один кодовый путь: `grep` находит его в 18 документах и в одном файле кода — `lab/check-claims.py:20`, где оно перечислено как зарезервированное слово; `README.md:104` разрешает его при типе `proof`/`test`, но вердикта с таким именем получить не из чего. Реализованная лестница словами определена только в `docs/36-ROUND7-SYNTHESIS.md:54` — то есть в синтезе ревью, а не в мастер-документе и не в спеке. Проверка: `python tools/fg_verify.py --claim fixtures/attack/k-proven.json --inventory fixtures/attack/a6-inv.json` → `"verdict": "CONSISTENT_DECLARED"`, ни одного `(R)`, ни `detector`, ни `recall` в выводе. Мастер-документ — это ровно тот файл, который `README.md:52` предлагает «вставить целиком во внешнее ревью»; внешний ревьюер проверит не тот продукт.

**R2. «Замыкание» — центральный объект продукта — отсутствует в схеме и в коде.**
`README.md:6` обещает «inside a declared closure no value can move past the single control point». В `schemas/claim-0.1.json:7-14` обязательные поля — `claim_id, target_lock, declared_control_point, declared_level, claimed_coverage, not_claimed`; поля `closure` нет. В `tools/fg_verify.py` слово `closure` встречается один раз — как имя кода ошибки `E_NO_INDEPENDENT_CLOSURE` (`:636`). Блок `closure: {declared_paths, excluded, unknown_behavior}` из `docs/SPEC-v0.1.md:103-108` не читает ни один инструмент. То есть замыкание существует в трёх прозах и в нуле проверок; фактически его роль играют `inventory.paths` + `excluded[]`, но это нигде не сказано.

**R3. Синтаксис `declared_control_point` не определён, а именно он решает, попадёт путь в ядро или нет.**
Определение — только словами: «EnforcementPoint M (the single decision point)» (`docs/FLOWGUARD-MASTER-v2.md:34`), поле — просто `string` (`schemas/claim-0.1.json:40`). При этом энумераторы пишут `function:` / `table:` / `role:` (`enumerators/grants-pg/fg_enum_grants.py:43`), а `docs/38-INVENTORY-DESIGN.md:50` показывает третью форму — `procedure:transfer()`, которой не производит никто. Проверено вживую: с `"declared_control_point": "function:bank.transfer"` на `fixtures/attack/a6-inv.json` → `core_paths: 8`; с `"bank.transfer"` (без префикса) → `core_paths: 0`, `computed_coverage: 0.0`, вердикт `CONSISTENT_DECLARED`. Опечатка в недокументированном префиксе тихо обнуляет покрытие — и никто не отличит это от «путей нет».

**R4. `recall 0.71 (corpus 20)` опубликован 12 раз, корпуса не существует, интервала нет.**
Вхождения: `docs/FLOWGUARD-MASTER-v2.md:75`, `articles/2026-10-what-proven-means.md:32`, `articles/2026-10-verifiable-ai-typed-claims.md:52`, `PACKET-ROUND6.md:52`, `docs/14-ROUND6-QUESTIONS.md:92`, `docs/32-ROUND6-SYNTHESIS.md:18`, `docs/34-OPEN-QUESTIONS.md:35` и др. При этом `docs/CLAIMS.md:68` прямо требует: «Every published recall figure must carry its interval and the corpus, or it is decoration» — и ни одно из 12 вхождений интервала не несёт. В `docs/METRICS.md` строки с recall нет вообще; артефакт claim'а C-03 — `lab/experiments/E-M11-grant-enumeration.md`, где измерено 8/8 на 8 посаженных обходов, то есть другое число. Детектор в примере — `slither+cast+manual`, инструменты Solidity: продукт после пивота проверяет Postgres. Число кочует из мастер-документа в опубликованные статьи как измеренное.

**R5. Контракт «у каждого числа есть лог» не выполнен для 99 из 103 строк `METRICS.md`.**
`python lab/check-metric-digests.py --cards` → `metric rows: 103 … unresolved digests: 130` (99 строк). В `lab/logs/` 34 файла, последний — `e-m42`; логов для E-M45…E-M76 нет. Один и тот же дайджест `2ad5b2c63a4c…` стоит у ~60 разных строк (`docs/METRICS.md:108-148`) — то есть один файл объявлен логом шестидесяти разных команд. Строка 63 (`docs/METRICS.md:108`) при этом утверждает «**0 unresolved** (was 14 across 8 rows)» и сама ссылается на этот же дайджест. Проверка слабее, чем звучит: `lab/check-metric-digests.py:41-47` принимает дайджест, если он совпал с sha256 **любого** файла в `lab/logs/` (не того, что относится к строке), а строка без дайджеста (`-`, строка 7) проходит молча. Правило из `docs/METRICS.md:9-10` («the sha256 of the log it was extracted from») не выполняется ни для одной строки после E-M44.

### Сломает доверие

**T1. CI на HEAD не может быть зелёным, а опубликованная статья утверждает «Green here».**
Красные шаги `guards.yml`: `:45` `lab/check-artifact-refs.py` → `dangling: 2` (`tools/_tmp` в `lab/experiments/E-M43-hostile-doc-review.md` и `E-M76-external-audit.md`); `:43` `check-metric-digests.py --cards` → 99 нерешённых; `:53` `selftest-guards.sh` → 1 провал. При этом `articles/2026-10-verifiable-ai-typed-claims.md:95` пишет «Three instruments that run in CI on every push … **Green here**: [workflow runs]» со ссылкой на страницу прогонов, `README.md:45` — «Both run automatically on every push and pull request», а `lab/experiments/E-M76-external-audit.md:61` честно признаёт: «no GitHub Actions run was observed». Локальный ритуал `lab/round-check.sh` включает все три упавших шага (`:42`, `:65`, `:44`), то есть и он красный. Это не «работа идёт», это «работа забыта»: ни один зелёный сигнал не существует.

**T2. `docs/21-FINAL-ASSESSMENT.md` устарел целиком, под фразой «каждое число — из инструмента».**
`:3` — «Every number below comes from a tool in this repository; the command is named beside it». Дальше: `:40` «readiness, engine half **100%**» (живой `tools/fg_readiness.py` → 83%); `:44` «guard self-tests **8 controls**» (сейчас 11, из них 1 падает); `:45` «experiment cards **49** (46 supports, 3 refutes)» (сейчас 67 = 60 + 7); `:46` «metric rows **79**» (сейчас 103). В шапке нет ни генератора, ни даты, в отличие от `STATUS-v0.md:3`; `tools/fg_audit.py` этот файл не сверяет (его 12/12 — про другие файлы), поэтому числа не пересчитываются ничем.

**T3. `READINESS.md` объявляет T2 достигнутым; его собственный инструмент говорит T0.**
`docs/READINESS.md:40` — заголовок «What can be applied **today** (tier T2)»; `:79` — «**T2 reached** — ✅». `python tools/fg_readiness.py` печатает `tier: T0 — nothing runs`, `next tier T1 … blocked by: E1`, `E1 … 0/10` (`secrets/links/claims/negative-controls: 3/4 green`). По таблице самого документа (`:16-17`) T2 требует E1, а E1 не взят. Причина E1 — тот же проваленный контроль `line-endings`. `README.md:14` («The readiness tier T2 claims an outsider can install and reproduce») стоит на этом же неверном основании. Негативный результат опубликован в `STATUS-v0.md:13-14`, но не доехал до страницы, которую читают первой.

**T4. `STATUS-v0.md` теряет строку M4, печатает 7/7, и `--check` этого не видит; коммит в шапке не существует.**
`tools/fg_status.py:44` разбирает строку регуляркой с `\s{2,}` перед состоянием. Метка M4 — `M4 eliminations with revival conditions` — длиной 39 символов не влезает в колонку `:38`, поэтому `check-interop` печатает её через **один** пробел — и строка отбрасывается. В `docs/STATUS-v0.md:31` стоит «**7/7**», а в таблице `:35-40` шесть строк: M1, M2, M3, M5, M6, M7 — M4 («eliminations with revival conditions») отсутствует. `python tools/fg_status.py --check` → «STATUS-v0.md is current». Плюс `:3` называет коммит `a1e2a4c`, которого в репозитории нет (`git cat-file -t a1e2a4c` → fatal), потому что `fg_status.py:193` намеренно исключает штамп из сравнения. Страница, чей смысл — «генерируется, а не правится», генерируется с потерянной строкой и несуществующим происхождением.

**T5. `fixtures/sample-bundle/README.md` противоречит артефакту, который описывает, в четырёх местах.**
Это страница, по которой «два независимых реализатора воспроизвели бандл» (`:6`), то есть самый нагруженный документ репозитория.
- `:140` — код `REPORT_BUNDLE_INCONSISTENT` выдаётся, когда «`bundle_version` is not `fg-bundle/1`»; артефакт — `fg-bundle/2` (`fixtures/sample-bundle/bundle.json:2`), и `:8` той же страницы требует v2. Реализатор по нормативной таблице `:138-150` обязан отвергнуть поставляемый бандл.
- `:123` — пример `"signature_binding": { "demo": "role", "owner": "role" }`; фактический вывод `tools/fg_bundle.py verify` — `"demo": "v2", "owner": "v2"`, а код умеет только `v2` / `v1-role` / `v1-address` (`tools/fg_bundle.py:341,351,353`). Значений `role`/`address` не существует.
- `:40` — «Hashing the pretty-printed file bytes gives a different value (`7358bb44…` here)». `sha256` файла = `6e09060c36617ef7…` (5087 байт, проверил `Get-FileHash` и `[SHA256]::ComputeHash`); `7358bb44` не воспроизводится.
- `:218-220` — «The artifact carries only the identifiers; the closed vocabulary is defined in the issuing repository». В бандле лежит `nc_vocabulary.text_included: true` и полный текст `docs/NOT-CLAIMED.md` (`bundle.json:60-64`), sha256 `bdc36c88…` совпадает с документом побайтно. Раздел «что бандл не даёт» прячет то, что бандл как раз даёт.

**T6. `check-links` зелёный потому, что смотрит три каталога из десяти; битых ссылок 11.**
`lab/check-links.py:12` обходит только корень, `docs/*.md` и `articles/*.md`. Мой прогон по всем `*.md` (152 ссылки) даёт 11 битых, в том числе в несущих артефактах: `interop/2026-10-28-flowguard-to-lexspec-1.md:30` → `37-REFUSAL-CODES.md` (нужно `../docs/…`), `lab/experiments/E-M76-external-audit.md:21` и `:25` → `../docs/28-CORRESPONDENCE.md` (из `lab/experiments/` это `lab/docs/…`), `docs/interop/README.md:4` → `../interop/REVIEW-EXCHANGE.md` (двойной `interop`), `interop/reviews/2026-10-28-flowguard-r1.md:9` → `../../REVIEW-EXCHANGE.md`. `README.md:41` обещает «every relative link between documents resolves» — обещание шире проверки.

**T7. Гейт контроля переводов строк не видит ровно тот случай, ради которого написан, и его негативный контроль красный.**
`lab/check-line-endings.py:29` перечисляет файлы через `git ls-files`, то есть только отслеживаемые. `lab/selftest-guards.sh:130` сажает `lab/_negative_crlf.sh` как **неотслеживаемый** файл — контроль падает (`FAIL line-endings: a CRLF shell script was NOT caught`). Собственный docstring (`:4-7`) описывает сценарий «скрипт, записанный Windows-инструментом», то есть новый файл — именно его гейт не видит. Следствие: новый CRLF-скрипт проходит CI до коммита, а после коммита ломает bash. Это единственная причина, по которой E1 = 0/10 и tier = T0 (T3).

**T8. Канонический `README.md` повреждён escape-последовательностями в четырёх местах.**
`:17` — `` `\x08ash `` (байт 0x08 вместо `` `b ``), поэтому блок «Install and run it once» не открывается валидным забором, а закрывается одиночным `` ` `` на `:21`. `:27` — литеральный `\thin` вместо «thin». `:89` — строка кончается ``…LEDGER.md) |`n| Assessment |…``: строка Assessment склеена с Exchange литеральным `n`, ячейка таблицы разрушена. `:94` — `| Process | \x08ash lab/round-check.sh`. Проверено перебором кодов символов (`ord(c) < 32`). Ни `check-line-endings` (ищет только CRLF), ни `check-links` (ссылки целы) этого не ловят; ничего не валидирует markdown как разметку. Первая страница репозитория — и команда установки в ней не рендерится.

**T9. Ни одна карточка эксперимента не привязана к существующей ревизии.**
67 карточек несут `base_commit:`; 34 различных sha-подобных значения; `git cat-file -e <sha>^{commit}` → **0** резолвится; в репозитории один коммит `c06d28b`. Примеры: `lab/experiments/E-M76-external-audit.md:5` — `base_commit: "885e12f"` (нет), `lab/experiments/E-M66-rust-core.md:5` — `"d2108e6"` (нет); остальные 32 sha-значения — та же картина, ещё 33 карточки пишут `uncommitted tree`. При этом `docs/METRICS.md:10` требует «the commit it was measured at», а колонка «commit» содержит `2026-10-27 tree`, `2026-10-28 Windows` — не идентификаторы. Воспроизвести измерение «на той ревизии» невозможно: ревизии нет.

**T10. `lab/round-check.sh` содержит два шага, которые не могут упасть, — тот самый паттерн, который карточка E-M76 объявляет исправленным.**
`:59` — `stage "differential: Rust core vs Python core" "$PY" lab/e-m66-run.py || true`; `:52` — то же для `cross-family-due.py`. `|| true` применяется к вызову `stage`, поэтому `RC=1` не выставляется никогда: расхождение двух ядер не покраснеет. `lab/experiments/E-M76-external-audit.md:34-37` называет ровно это («a step that could not fail») главной находкой внешнего аудита и починенным в CI — в локальном ритуале паттерн остался.

### Мелочи

**M1. `docs/METRICS.md:3` — «contract in force, 59 rows»; строк 103 (то же в `README.md:61`).** Счётчик в шапке контракта, который сам требует пересчёта, не пересчитан.

**M2. `README.md:74` — «lab/decisions/ — 14 ADRs»; файлов ADR-0001…ADR-0017 — 17** (`docs/STATUS-v0.md:26` уже печатает 17).

**M3. `docs/37-REFUSAL-CODES.md:10` — «There are seventeen, plus RETRY_BUDGET_EXCEEDED».** В таблице `:14-38` ровно 17 строк, включая `RETRY_BUDGET_EXCEEDED`; «plus» даёт 18. Ирония в том, что абзац начинается словами о том, что «число в заголовке — украшение, которое дрейфует».

**M4. `docs/37-REFUSAL-CODES.md:57` документирует `"attempt_budget": {used, max}` в форме ответа; ни один инструмент его не печатает** (`grep attempt_budget` → только код ошибки `RETRY_BUDGET_EXCEEDED`, `tools/fg_verify.py:343`). Правило 5 (`:70`) «The attempt budget is enforced by the verifier, not by the agent's good manners» неверно: бюджет — это аргумент CLI `--attempts` со значением по умолчанию 1 (`tools/fg_verify.py:252`), то есть его сообщает вызывающий.

**M5. `docs/NOT-CLAIMED.md:28-29` перечисляет NC-11 перед NC-10**, а `docs/STATUS-v0.md:57` утверждает «Every verdict carries `NC-01`…`NC-11`» — на деле `CONSISTENT_DECLARED` требует два кода (`docs/NOT-CLAIMED.md:35`), а NC-06…NC-09 не требуются ни одним уровнем (`:35-37`). Фраза в генерируемом файле сильнее таблицы, из которой генерируется.

**M6. `lab/check-refusal-coverage.py` считает «exercised by a test» упоминание в прозе.** 6 из 17 кодов покрыты только текстом карточек (`AMBIGUOUS_ATTRIBUTION`, `EXCLUSION_REASON_UNKNOWN`, `LIABILITY_NOT_A_ROLE`, `RISK_ACCEPTANCE_INCOMPLETE`, `SEPARATION_OF_DUTIES_VIOLATED`, `SIGNATURE_ROLE_UNKNOWN` — вывод `--list`), потому что `:55-57` склеивает весь текст карточек. Настоящие производители этих кодов в список носителей `:24-30` не входят: `tools/fg_bundle.py:136-176` (четыре кода), `tools/fg_verify.py:596` (`AMBIGUOUS_ATTRIBUTION`), `tools/fg_exclusions.py:64` (`EXCLUSION_REASON_UNKNOWN`). Гейт неверен в обе стороны: производители не учтены, проза учтена.

**M7. `articles/SUBMIT.md:48` — «заголовок ≤80 символов — сейчас 59»; заголовок в `:8` — 62 символа.** Чек-лист перед публикацией содержит неверный счётчик в единственном месте, где счётчик проверяем.

**M8. `lab/cross-family-due.py` печатает `RESULT: due`** («the files that decide verdicts changed»), а `docs/METRICS.md:127` сообщает «1 run recorded»; в `lab/state/cross-family.json` — `"runs": 2`. Гейт каденции говорит «пора», и его никто не потребляет: в `guards.yml` его нет, в `round-check.sh:52` он заглушён `|| true`.

**M9. Зависимость не объявлена.** `tools/fg_schema_check.py:28` жёстко требует `jsonschema` (иначе `exit 2`), в репозитории нет ни `requirements.txt`, ни `pyproject.toml`, в `guards.yml` нет шага установки, а `README.md:25` обещает «PostgreSQL client tools and Python 3.11+; nothing else». Шаг CI «published schemas accept the artifacts» держится на неустановленном пакете.

**M10. Проба готовности использует inventory, не проходящий опубликованную схему.** `fixtures/verify-probe/inv.json:1` — нет `manifest_version`, у пути нет `kind`, `path_id: "p1"` короче `minLength: 4`; `python tools/fg_schema_check.py --inventory fixtures/verify-probe/inv.json` → 3 ошибки. Это вход проверки E2 (`tools/fg_readiness.py:46-47`), которая засчитывается при `returncode in (0,1,2)` (`:48`) — то есть «executes and refuses» не может провалиться даже если верификатор всё принимает (rc=0).

**M11. `docs/38-INVENTORY-DESIGN.md:64` — «`path_id` is a content hash of `kind + entry + control_point`».** В фикстурах `wp_001…wp_008` (`fixtures/attack/a6-inv.json`), в демо-бандле `wp_demo0000000001`; энумератор считает хеш от четырёх полей, включая `detail` (`enumerators/grants-pg/fg_enum_grants.py:43`). Три разных правила в одном репозитории, и ни одно не нормативно.

**M12. `docs/26-PUTNAM-AGENT.md:55` — «the checker does not test „the claim is vacuous“. That is a rule worth adding».** Правило уже есть: `docs/METRICS.md:137` («vacuity rule in both cores: empty coverage cannot carry a level») и код `tools/fg_verify.py:479` («A ratio over one or two paths is noise»). Документ отстал от собственной карточки.

**M13. `docs/FLOWGUARD-MASTER-v2.md:143` — «Closure Z — 13 elements», но элементов в документе нет**; сказано «Twelve from v1 plus a thirteenth», а v1 (`docs/FLOWGUARD-MASTER.md:149-152`) действительно перечисляет 9 + 3 = 12. Документ заявлен как «self-contained file for external review» (`:3`), но для проверки числа 13 нужно открыть другой файл; «тринадцатый» элемент (shared secrets) при этом пересекается с девятым обязательным v1 («CI/CD and secrets»).

**M14. `docs/36-ROUND7-SYNTHESIS.md:70` — «Refusal taxonomy: six codes»**; в `docs/37-REFUSAL-CODES.md` их 17, и его шапка (`:9-10`) рассказывает, как «six» превратилось в семнадцать. Синтез не обновлён.

**M15. `articles/2026-10-what-proven-means.md:51` и `articles/2026-10-verifiable-ai-typed-claims.md:73` — «fifteen positions» в `eliminations.md`; там 26 записей** (`check-interop` и мой подсчёт заголовков `^#{2,3}`). Опубликованный текст, число протухло.

## Пять пунктов, которые я бы сделал первыми

1. **Починить или удалить колонку «log sha256» в `docs/METRICS.md`.** 99 из 103 строк ссылаются на один несуществующий дайджест, а строка 63 врёт про «0 unresolved» — пока это так, весь тезис «у каждого числа есть лог» недоказуем, и любая внешняя проверка начнётся и закончится здесь.
2. **Свести вердикты в одну таблицу «спека → код» и либо реализовать `ENFORCED_TESTED`, либо вычеркнуть его из `README.md:104` и мастер-документа.** Сейчас внешний ревьюер, читающий `FLOWGUARD-MASTER-v2.md`, проверяет продукт с другим выходным словарём, чем тот, что выдаёт `fg_verify`.
3. **Внести `closure` и синтаксис `declared_control_point` в `schemas/claim-0.1.json`.** Недокументированный префикс `function:` переключает `core_paths` с 8 на 0 — это не косметика, это скрытый вход вердикта.
4. **Довести CI до реально зелёного и не публиковать «Green here» до ссылки на прогон.** Три шага красные на HEAD, статья уже утверждает зелёный CI, а карточка E-M76 признаёт, что прогонов не видели — это самая дорогая потеря доверия при самой дешёвой починке.
5. **Перегенерировать `docs/21-FINAL-ASSESSMENT.md`, `docs/READINESS.md` и `fixtures/sample-bundle/README.md` из инструментов и добавить их в `fg_status`/`fg_audit`.** Все три противоречат своим же инструментам (100% против 83%, T2 против T0, `fg-bundle/1` против `/2`), и именно они читаются раньше честного `STATUS-v0.md`.

## Чего я не проверял

- **Всё, что требует PostgreSQL**: `psql` в окружении есть (`C:\Users\Admin\miniconda3\Library\bin\psql.exe`), но свою копию `lab/e-m11-run.py` воспроизвести не удалось: харнесс подключается к `postgres` на `--port` и делает `DROP/CREATE DATABASE fgfix` (`lab/e-m11-run.py:53-55`), а на 127.0.0.1:54329 сервер в момент моего прогона не отвечал (`could not initiate GSSAPI security context`, затем `database "fgfix" does not exist`). Поэтому числа E4/E5 (8/8, 11/12) и E-M13 (2/2, 0/9) я взял из документов; в прогоне `tools/fg_readiness.py` они в тот момент отметились как `OK RESULT: PASS`, но независимо я их не подтвердил. `tools/fg_init.py`, энумераторы `grants-pg`/`pgcalls`/`runtime-pg` и фикстуры `fixtures/pg-bypass/*` по той же причине не запускал.
- **Rust-ядро**: `cargo` не запускал, поэтому E-M66/E-M67/E-M68 (6/6, 15/15, 10/10) и `core-rs/` не проверены; `lab/e-m66-run.py` в `round-check.sh:59` заглушён `|| true`, так что даже при наличии тулчейна сигнал был бы скрыт.
- **Дифференциальные прогоны**: `lab/e-m57-run.py`, `e-m69-run.py`, `e-m70-run.py`, `e-m72-run.py`, `paired-eval.py` не запускал — часть требует внешних бинарников/транскриптов.
- **Внешние ссылки и внешние числа**: `github.com/mak777uh/flowguard-spec`, страница прогонов Actions, цифры DARPA AIxCC в статье (54 млн строк, 18 уязвимостей, $152/задача) — сети не было, проверить не мог; отдельно не устанавливал, запускался ли workflow когда-либо (проверял только, что он не может быть зелёным на HEAD).
- **Содержимое interop-переписки и `docs/20-ROUND2-DECISIONS.md`** (46 КБ) — читал выборочно, по ссылкам и утверждениям, а не целиком; не сверял цитаты из заметок VecDHT/LexSpec с их репозиториями.
- **Семантику SQL-фикстур** (`fixtures/pg-bypass/01-fixture.sql`, `inbox/ironclaw-migrations/*.sql`) — не разбирал, поэтому не сужу, действительно ли там 8 посаженных обходов и 5 файлов миграций.
- **`python3` против `python`**: все прогоны делал `python` (3.13.11); `guards.yml` вызывает `python3`, и на ubuntu-раннере поведение может отличаться (в частности, наличие `jsonschema`, см. M9).
