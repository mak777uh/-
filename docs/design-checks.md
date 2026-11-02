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

**A seed is replication only if it changes the world (01.11).** The laboratory default reading of a series is «five
seeds», and for most arms that is true: nine distinct `series` rows for nine seeds. In the neutral world it is false by
construction. With `beta = 0` and `eps = 0` the field has no trait feedback, the initial blob is fixed, and the seed is
consumed only by the trait channel — so the geometry is identical for every seed and the run is *one* world with five
different inert trait noises. Measured on 01.11: `uid_pairs`, `areas` and `peaks` identical across seeds, only `s`
differs, and X70 925 division events turned out to be 185 events copied five times. Everything said about geometry in
those arms — «5/5 seeds», «10/10 seeds», seed-averaged spreads — was one observation quoted five times, and a null
calibrated on five copies is too tight by roughly a factor of the square root of five.

Rules that follow. (1) A registration must name **which channel the seed feeds**; if the answer is "the trait channel
only", the seed is not replication for a geometry claim. (2) A neutral world gets an explicit initial-condition knob
(`--init-jitter`: seed-derived offset and plus-minus 20 percent radius of the starting blob, inert when off — anchor
bit-for-bit on seed 171). (3) The claim is checked, not assumed: `python scripts/check_seed_replication.py` hashes every
family series rows with the trait columns removed, writes `morphogenesis/experiments/E09_pond/seed_replication.json`, and
`verify` fails if the committed table disagrees with the artifacts. (4) When a family collapses to one world, the report
says so in the first paragraph and the numbers are restated per world, not per seed. Blast radius on 01.11 — the defect is
exactly the `beta = 0` geometry arms (`x70*`, `x68_ov0*`, `x56_dt2.0`, `e6p_ctrl`, `e6q_ctrl_h`); the amplitude dose,
correlation length, scale sweep, grid map, bigger box and transmission ratio all have genuinely distinct worlds behind
them.

**A proxy must move with what it stands for (20:00, X72).** A readout that replaces the measured quantity with a cheaper
stand-in needs its own positive control, and "both classes are populated" is not one. X72 wanted a branch class (which of
X71's two wavelengths a structure sits on) from a component log that has centroids but no spectrum, so it used the distance
to the nearest neighbour as a stand-in for the local wavelength. The classes were populated (59 % wide), the pre-registered
control passed, and the numbers looked like a clean null: parent–daughter branch concordance 0.517 against chance 0.50,
surrogate 0.904. The stand-in was measuring packing density, not size: median spacing stayed at 11.0–11.5 cells while the
global wavelength moved between 12.0 cells and a labyrinth, correlation −0.18, spread 0.7 cells against a 3.3-cell
difference to resolve. The report is a void, not a negative, and that is the cheaper outcome by far.

Rules. (1) Every proxy readout names the quantity it stands for and the control that would move it — in the
preregistration, next to the class criterion. (2) The control is a correlation or a monotone response, not the existence of
variation: "the proxy must track the quantity across the range where the quantity is known to change". (3) A void is
reported as a void: the numbers are recorded, the verdict says "instrument failure", and no claim is made in either
direction. (4) A surrogate that is measured at the same instant and in the same patch as the target is a measure of spatial
autocorrelation; it cannot be compared with a control measured one snapshot earlier.

**The manipulation check must be the same number the claim uses (02.11, X80).** X80's check asked whether the radial profile had a
strict local maximum in one window and another in a second window. Two failures hid behind that sentence: a **count passes on a tie**
(the rule said "the middle cell must be the most two-peaked", the middle cell tied with a wing, 5/5 against 5/5, and the rule accepted
it), and a **count fails on a shoulder** (at the third weight the second family sat one bin lower, scored 0/5, while as a power share
the same field carried 0.27-0.34 — the opposite reading). The claim then spoke about "equal parts" while the check had counted peaks.

Rules. (1) The manipulation is verified by the **same function** that the claim quantifies: if the claim says a share, the check
returns a share. (2) The tolerance is **numeric and written before the run** ("the realised share must land within 0.15 of the
prescribed one"), never qualitative ("most X"). (3) A peak count may be reported as a description, never used as a gate. (4) When the
positive control can fail, the refusal rule says what happens then — X80's control failed (a wing at 0.86 against the required 1.0)
and the rule did not encode the consequence, so the series closed with a verdict instead of a void.

Consequence for the field line: the transfer function from prescribed to realised spectral share is now measured **before** the design
(X82), because a design built on a channel that saturates at a third would have measured its own ceiling rather than the world.
Reports: `reports/2026-11-02-x80-correction-two-peak.md`, `reports/2026-11-02-x82-reach-plan.md`.

**Logging frequency is a physical parameter (02.11, X85).** In `field_track.py` the trait mutations are drawn **at every sampled
step** (`rng.normal(args.s_ref, args.mutation)` for newborn components, `rng.normal(0, args.mutation)` for daughters), and the trait
feeds back into the field. So `--sample-every` does not only decide how often we look: it decides how many mutation events a world
experiences. X71 ran at 1000 (six events over 6000 steps), X73–X85 at 50 (a hundred and twenty).

Verified: seed 191, `F = 0.035`, identical flags except `--sample-every` — the fields differ by up to **0.365** in v. Two series at
different logging density are therefore **not the same cell measured twice**, and a control band taken from one regime does not apply
to the other. X85 voided itself exactly that way.

Rules. (1) Any cross-series comparison states the logging density of both sides. (2) A control band is measured **in the regime of the
experiment**, never borrowed from an older series. (3) When a series needs both dense genealogies and a cheap run, decide the logging
density in advance and keep it identical across every cell of every series that will be compared. (4) The recipe for a probe that
draws randomness is the same as for a probe that modifies the field: it needs an anchor on both settings.
Report: `reports/2026-11-02-x85-symmetry-memory-void.md`.

**A label is only comparable inside its own frame (02.11, X102).** `basins()` numbers the basins of one snapshot; the numbers mean
nothing across snapshots, and nothing in the function's type says so. X102's first degeneracy check compared the parent's basin label
in the snapshot where the parent peaks with the daughter's label in the snapshot where the daughter peaks, and reported that the parent
sat inside the daughter's basin **no more often than a stranger** (0.13 against 0.07). Recomputed as same-frame containment, the parent
is inside the daughter's basin 2.3-3.0 times as often as the stranger (0.398 against 0.132 at `F = 0.030`, 0.187 against 0.081 at
0.040) — the opposite reading, and the one the report now carries.

Rules. (1) A topological or component **label** (`basin id`, `uid`) may be compared with another label only when both were produced from
the same frame; anything else compares numbering schemes, and the result is noise that looks like a negative. (2) Aggregators that keep
labels expose them together with the frame they came from (`label`, `step`), so the mistake is visible at the call site. (3) Any
comparison of a quantity computed per frame across frames is done on a **scalar** (area, count, position), never on an identifier.

**A collapse needs a degeneracy check before it is interpreted (02.11, X102).** X102 found that the specificity of size heredity
(X91's parent-versus-stranger gap) falls from 0.312 / 0.215 to 0.017 / -0.010 when the size definition is weakened. Two readings were
possible: the medium stops being specific, or the weaker readout cannot separate the candidates by construction (every stranger sits in
the same basin as the daughter). The containment table above decided it — the basin readout had room, so the collapse is real.

Rules. (1) Every null or collapse that could be mechanical carries a **degeneracy table**: how often the control falls in the same
structure as the subject, next to how often the true ancestor does. (2) The table is printed for every cell, not just once. (3) If the
control is nearly always inside, the series is a void **by construction** and is registered as such — never as a negative result.
Report: `reports/2026-11-02-x102-specificity-ladder.md`.

**A coverage gate names its denominator (02.11, X103).** X103 registered "basin coverage at least 60 % of the pairs" and came back
at **0.599** for `F = 0.040` — a void by a thousandth. The gate was counting every ancestor-daughter pair in the logs, including
**622 of 1 761 (35 %)** whose ancestor or daughter was never logged at all: at that inflow the median lifetime is 89 steps against
a 50-step logging interval, so a structure that is born and divides between two samples is invisible by construction. Among pairs
whose peaks do exist, the instrument was available for **0.973 and 0.925**.

Rules. (1) A coverage floor states which pairs the denominator contains: all pairs, pairs with both peaks logged, or pairs with a
usable instrument — the same run reads 0.599 or 0.925 depending on the choice. (2) Structural loss (the world never showed the
object) is reported as a **selection fact** with its own count, never folded into an instrument-availability gate. (3) When a gate
fails, the diagnosis is part of the void: the numbers are recorded, the reason is named, and the rule that follows is written down
before the re-registration. A report that only says "void by coverage" loses the one thing the run produced.
Report: `reports/2026-11-02-x103-basin-position-void.md`.
