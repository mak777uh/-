# Design checks before a series — the five rules, and why they exist

Introduced 31.10.2026, after five invalid designs of the field line in one day and about **110 runs** spent on them.
Rule `§3c` of the contract already demanded the sensitivity arithmetic; it did not cover the dominant cause: **the
manipulated variable never reached the dynamics.**

This page is the full text. The contract keeps the rule and a pointer.

---

## The five checks

### 1. Connectivity — the manipulation changes the world, not a label

Two runs, identical in everything except the manipulation, must produce **different dynamics**.

```
python scripts/check_design.py --pair on.json off.json --key "series[].components"
```

If the hashes are equal, the arms are the same experiment. *This is not hypothetical:* `X46` ran `lead0`, `lead20`
and `lead40` as three arms, and all three had the hash `efd3ee56dc8e`, because the sensor coupling was zero and the
lead only changed a recorded field. Forty runs produced a comparison between three copies of one world.

### 2. Positive control fires

The arm in which the effect **must** be strong has to show it, with the observed size written down.

*Counter-example:* `X49` fired pulses in its `periodic` arm and the phase still differed from the non-phase by
`0.00` components and `0.00` divisions. The whole omission design was a null by construction — and the series had
already been run.

### 3. The readout exists and varies

The behaviour being measured must be recorded per slice and must not be constant.

```
python scripts/check_design.py --readout run.json --key "series[].splits"
```

*Counter-example:* `X49` had no behavioural variable at all — `splits` was `None` in every slice. Later, in the pond,
`born` turned out to be zero in a run with 1469 living cells, because growth happens by cells appearing and moving
rather than dividing. Both times the readout looked present in the plan and was absent in the data.

### 4. Sensitivity arithmetic before the criterion

| quantity | why it matters |
|---|---|
| baseline median | what the effect is measured against |
| sd between seeds | the noise the effect must clear |
| effect worth detecting | in absolute and relative terms |
| seeds needed at α = 0.05, power 0.8 | whether the design is affordable |
| CV of the baseline | above 0.3 the readout is inadmissible without pairing or a stronger effect |

*Worked example (`X53`):* growth has median 436, sd 145, **CV 0.333**. A 10 % effect would need **174 seeds** per arm
unpaired; a 30 % effect, 20 seeds. Hence the design became **paired** (same seed with and without the tide), and the
paired spread is left unassumed until a pilot measures it.

### 5. Refusal rule written in advance

Name the outcomes under which the experiment will be declared **worthless** rather than negative:

1. the manipulation does not change the readout;
2. the paired spread is as large as the unpaired one (pairing failed);
3. the window contains too few would-be events;
4. the population dies before the window;
5. the effect is global rather than local (nothing to anticipate).

Written before the data, these cannot be discovered afterwards as an excuse.

---

## Routine

1. Copy [`preregistration-template.md`](preregistration-template.md).
2. Fill the five sections; run `check_design.py --prereg <file> --ci` — it refuses while any box is unticked.
3. Run the two artifact checks (`--pair`, `--readout`).
4. Only then run the series.
5. If a check fails after the fact, the record says **insensitive by construction**, with the failing item named —
   not "no effect".

## What the gate cannot do

It cannot judge whether the question is worth asking, whether the readout is the right behaviour, or whether the
effect size matters scientifically. It only refuses the specific failures that cost us a hundred runs: arms that are
the same run, controls that never fire, readouts that are not recorded, and designs whose arithmetic cannot produce a
difference.

---

## Правила §3c (перенесено из AGENTS.md)

**Монотонное по построению — не свидетельство.** Величина, связанная с изучаемым фактором формулой
реализации, помечается в агрегате как `derived_by_construction: true`; в тексте она называется проверкой
**реализации механизма**, и рядом обязателен независимый контроль либо честное «конфаундер не отделён».
Проверка на тавтологию: подставить предсказанную формулу вместо наблюдаемой — если ρ не меняется,
величина по построению. Примеры — [`incidents.md`](incidents.md) §5.

**Нормировка может инвертировать вывод — проверяй обе.** Утверждение, опирающееся на отношение,
перепроверяется на альтернативной нормировке **до** записи в рукопись; в пре-регистрации указываются обе
и основная; расхождение знаков публикуется как «вывод зависит от нормировки». Пример — `docs/incidents.md` §6.

**Знаменатель — часть определения величины.** Любая величина, считаемая по подмножеству прогонов
(«только валидные», «только с данными», «только завершившиеся»), обязана: (1) нести суффикс в имени
поля — `*_all` или `*_valid`; (2) иметь явный знаменатель в `metric` агрегата; (3) не называться так
же, как величина по всем прогонам. Основание: 25.10 агрегатор W2-bud считал `I > 0` только по валидным
прогонам (2 из 10), а критерий пре-регистрации требовал ≥7/10 по всем — агрегат «опроверг» выполненный
критерий, и это всплыло только при попытке автоматизировать сверку. Тогда же переименованы поля
`founding_matrix.by_n`: `n` = доза, и рядом `runs`/`valid_runs` — читалось как «n прогонов».
Проверка: `python scripts/verify_sections_numbers.py` (в CI) сверяет числа разделов рукописи с
агрегатами и падает при расхождении.

**Отбор строк — часть определения агрегата.** Агрегат обязан либо содержать строки, либо объяснить,
почему их ноль. Шаблон имени файла — тоже часть контракта: 26.10 шаблон `w2bud[a-z0-9]*_` не пропускал
подчёркивания, файлы `w2budd2_rep_n3_cell_seed101.json` молча выпадали, и агрегат выдавал
`invalid_by_data: true` — то есть **«эффекта нет» вместо «данных не видно»**. Тот же шаблон нашёлся
вторым экземпляром в другом скрипте. Правило: (1) агрегатор печатает число отобранных строк и число
отброшенных; (2) гейт `scripts/check_empty_aggregates.py` падает, если строк ноль, а в каталоге-источнике
есть файлы; (3) при чтении агрегата с нулём строк всегда проверяйте, не пуст ли источник.

**Реализация должна совпадать с определением.** Метрика объявлена словами («частная корреляция
Спирмена») — значит и считать надо ровно это. 26.10 нашлось расхождение: `rho_partial` считалась как
«исключить `z` из сырых значений, потом ранжировать остатки» — ни частный Спирмен, ни частный Пирсон;
числа расходились с определением на 0.2–0.5, и вердикт держался на них. Правило: (1) в `lab/metrics.json`
формула записывается текстом; (2) гейт `scripts/check_metric_definitions.py` (проверяется в `make health` **и** `make verify`) пересчитывает величину
независимой реализацией из сырья и падает при расхождении > 0.05; (3) если нужен вариант реализации —
он публикуется отдельным полем с именем (`*_hybrid`), а не подменяет основной.

**Проверка пост-фактум:** в отчёте и в §-разделе линии пруда пишется строка «чувствительность:
`own*` = …, поле = …, вывод — чувствительно/нечувствительно». Нечувствительный результат
публикуется как «тест не дотянулся», а не как «эффекта нет».
