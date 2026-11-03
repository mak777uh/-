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

**A manipulation that deletes the pattern reports the pattern's own peak (02.11, X96).** The second-species pilot showed every w-on
setting differing from the control by max|dv| = 0.4325 — identical to six digits across three diffusion lengths and two couplings.
The reason was not a bug: the w-on fields were empty, so the difference *was* the control. The number that looked like a strong effect
was the strongest possible evidence that the manipulated field no longer existed.

Rules. (1) A field-level manipulation reports max|dv| **next to** the manipulated field's own mean and maximum, never alone. (2) If
max|dv| equals the reference's maximum, the manipulated field is gone and the run is void by liveness, not a result. (3) Couplings
that enter a reaction term are checked in the regime they create: a factor 1/(1+gamma*w) is 1/(1+gamma) wherever a structure sits,
so gamma = 0.5 is a 33 % cut in the autocatalysis, not a perturbation. (4) The liveness floor is registered before the run and is
part of the refusal rule.
Report: 
eports/2026-11-02-x96-void-regime.md.

**Mark a queue item running only after its runner holds the lock (02.11, third time).** Three series in one evening (X105, X110, X112c) were
marked `running` in `lab/queue.json` before their runner had taken a lock or written an artifact, and `queue-audit` — correctly — reported
"running without a lock, without fresh artifacts, without a process". One of those states reached CI and turned it red on the exact commit
that started the series.

Rules. (1) The runner claims its lock **first**, heartbeats after every run, and releases in a `finally` block; the queue status follows the
runner, not the other way round. (2) If the status must change from a separate agent, it changes *after* the lock file exists — one `ls
lab/locks/` costs nothing and prevents a red gate. (3) A `running` item with no lock, no artifact and no process is an error, not a warning:
the audit is right and the bookkeeping is wrong. (4) When a runner's release does not match the lock it claimed (the run id is chosen by
`lab.py claim`, not by the caller), the lock outlives the series and the snapshot gate flags it — release by run id in that case.
Reports: `reports/2026-11-02-x110-gamma-cell.md`, `reports/2026-11-02-x112b-cuts.md`.

**Check `git ls-files` before deleting a glob (03.11).** A disk cleanup deleted nineteen *tracked* artifacts —
`morphogenesis/experiments/L1_field/x96*_*.json` — because the ignore rules were added **after** those runs were committed, so the files were
both in git and matched the "dense logs are not committed" pattern I was reasoning with. `git status` caught it as nineteen deletions and
`git checkout` restored them, but the ledger had already recorded them as freed.

Rules. (1) A deletion driven by a pattern first runs `git ls-files` over that pattern and refuses if any path is tracked. (2) An ignore rule
added after the fact does **not** untrack what is already committed — the two states coexist, and only `git rm --cached` separates them. (3) A
retention ledger entry for a restored path is corrected by a new entry, never by editing the old one, and `freed_bytes` goes down by exactly
what came back.

**Before deleting a derived artifact, check that its committed projection exists (03.11).** The same cleanup that removed nineteen tracked files also
removed the **full dense logs of the X108 series** — fifty megabytes that had never been compacted and never committed. The aggregates were in git, so
no claim was lost, but every re-analysis of the evening's chain (X109, X113, X113c, X114) suddenly needed data that no longer existed anywhere: the
series had to be re-run from its seeds, and only determinism makes that a repair rather than a loss.

Rules. (1) A deletion of derived data names the committed artifact that stands in for it — for this line, the `.compact.json` projection or the
aggregate. (2) If no projection exists, the projection is written **before** the deletion, not after. (3) "It is in the aggregate" is enough only for
claims; any analysis that might be re-read needs the projection. (4) A regenerated series is checked against the aggregate it was supposed to
reproduce, and the check is recorded — determinism is the only reason a re-run can replace deleted raw data.

**Matching on the exposure deletes the effect by construction (03.11, X117).** X117 matched sister pairs on the number of daughters *and on area*, found the
survival advantage collapse to nothing, and the registered rule fired "fully arithmetic". The rule was wrong to fire: area **is** the exposure — "the larger
sister" means the one with the larger area — so matching on it compares sisters of equal size and can only produce a null. X116's match on the number of
daughters was a mediator test and halved the effect; X117's match on area removed the question.

Rules. (1) A matched design names, for every variable it matches on, whether that variable is a **confounder** (associated with exposure and outcome, not on
the causal path), a **mediator** (on the path), or the **exposure**. (2) Matching on a confounder tests the effect; on a mediator it measures the share the
mediator carries; on the exposure it deletes the effect and cannot be reported as a null. (3) A control that verifies the match worked ("the ratio falls from
1.57 to ≤ 1.10") is not evidence that the match was the right one. (4) When a registered rule fires a verdict that the design cannot support, the report
says so and the verdict is withdrawn — a fired rule is not a licence to publish the sentence it was written for.
Report: `reports/2026-11-03-x117-area-matched-void.md`.

**A constant predictor must fail before the model runs (03.11, X121).** X121's person-period table gave every `daughters` coefficient as 0.0 with interval
[0.0, 0.0] — the signature of a column with no variance, not a measured zero effect. The join that was supposed to count daughters matched nothing, and the
model reported the consequence as a clean result.

Rules. (1) Every model prints, before the coefficients, the **count, mean, standard deviation and share of non-zero values** of each predictor. (2) A predictor
with zero variance aborts the run: a coefficient for a constant is not an estimate, and returning 0.0 with a tight interval is worse than failing, because it
looks like a finding. (3) The same check covers coverage: the share of rows where a joined quantity was found. (4) An event-rate model also prints the event
rate against its registered band before anything else, because a rate outside the band makes every coefficient uninterpretable regardless of variance.
Report: `reports/2026-11-03-x121-hazard-void.md`.

**An identity convention is part of every survival readout (03.11, X122).** With `--split-new-uid` a structure's uid ends **exactly when it divides**: uid 1 is
present at steps 1-210 and its children appear at 220, uid 2 at 220-330 with children at 340, uid 5 at 340-490 with children at 500. So "the structure has
daughters" and "the structure is present at the end" are mutually exclusive states, and X119's regression of presence on a daughter count produced −0.429 that
is nothing but that exclusivity. The claim was withdrawn as an artefact.

Rules. (1) Every survival readout names which of the three quantities it measures: **uid present at the end** (undivided and alive), **subtree alive at the end**
(the lineage continues), or **generations reached** (depth). (2) A model that predicts a uid's presence must not carry a count of its own divisions as a
predictor — the two are the same event with opposite signs. (3) Lineage statistics (X93, X97, X113-X116) use the subtree and are unaffected; a reader must be
told when a number uses the uid instead. (4) When a tracker's identity rule can retire a parent at a split, the rule is stated next to every survival number it
touches.
Report: `reports/2026-11-03-x122-identity-artefact.md`.

**One quantity, one definition, stated with every number (03.11, X124).** A coherence audit of the block's consequence work found the line using the same word
for different things. "Rate" meant `depth / generation time × 1000` per uid in X113c and the same formula per sister pair in X124 — the two contrasts differ by an
order of magnitude (6.06 against 36.6). "Generation time" appears both as a raw difference (X124: the larger sister's is **shorter** by 412 steps, CI −518…−310)
and as a share of the pair's mean (X93: the larger sister's is **longer** by 0.05-0.08), and the two disagree in sign.

Rules. (1) An aggregate names the **unit of aggregation** (uid, pair, world, cell) next to every coefficient, because a mean over uids and a mean over pairs are
different quantities even when the formula is the same. (2) A "share" and a "raw difference" are different readouts: a claim that says "the larger sister lives
longer" must say which one it used, and the two must not be quoted interchangeably. (3) When an audit finds two definitions under one word, the affected numbers
are marked with their definition and the claims cite **directions** until one definition is fixed and the numbers recomputed. (4) A coherence audit that voids is
still an audit: the void is the finding.
Report: `reports/2026-11-03-x124-coherence-void.md`.

**An undeclared sample rule is not a definition (03.11, X125-X125c).** Three times in one night a published pair statistic differed from its recomputation
only by a sample rule nobody had printed. X113c kept a sister pair only when **both** generation times were at least 50 steps, and that filter - not any unit of
aggregation - is what turned a rate of 36.6 into 6.06: 185 short-lived pairs out of 1 142. X93 skipped pairs whose generation times were **equal**, and that tie
rule is what turned a fraction of 0.409 into 0.526: 22 % of pairs. X125 averaged the ratio `g_big / g_small` over pairs (12.0), a mean of ratios whose
denominator approaches zero for short-lived uids, where a ratio of means belonged. In each case the recomputation was right and the published sentence was
unqualified, and in each case the *first* diagnosis was wrong: X124 blamed the unit of aggregation for a gap that a filter produced.

Rules. (1) A filtered statistic names its filter and its **denominator** in the same sentence as the number - "+18.96 on 638 of 1 195 pairs", not "18.96".
(2) Ties are a sample rule: a proportion with ties excluded and a proportion with ties counted are two statistics, and swapping one for the other is not a
correction, it is a substitution. (3) A ratio of two paired quantities is published as a **ratio of means** or a **median of ratios**, never as a mean of ratios.
(4) A filter can only change a published number through the pairs it removes, so the removed count is printed next to the filtered result. (5) For a
definitional audit the sensitivity condition is the **interval width**, not a count of pairs: X125b voided at 638 pairs whose rate interval was +/-22 %, which
was ample for the question it asked - a floor carried over from another design is not a power calculation. (6) When a majority statement and a magnitude
statement disagree in sign, both are printed with their statistic named and the discrepancy is decomposed (mean of the positive part, mean of the negative part,
share beyond a stated bound) instead of being resolved by choosing one. (7) A control that reproduces another experiment's number must name that number's unit
**and** filter; if the plan cannot name them, the control is not ready to run - X125's control asked a uid-level statistic to reproduce a pair-level one.
Reports: `reports/2026-11-03-x125-definitions-void.md`, `-x125b-statistics-void.md`, `-x125c-ties.md`.

**A refusal rule must contain a "neither" branch (03.11, X127).** X127's pre-registration offered two outcomes - "the maze is homogenising" (absorbed share rises
by more than 0.10) and "the maze is lethal" (that rise does not happen and vanishing dominates) - and the world answered a third thing: absorption *falls* by
0.089 while vanishing rises to 16.5 %, far from a majority. The code's `elif` chain fell through to the second label, and the first printed verdict said "the maze
is lethal" although the second clause of that branch was false. Nothing was published from it, and the numbers never changed, but the failure mode is general: a
two-sided rule does not become exhaustive because the author thinks the pair is exhaustive.

Rules. (1) Every refusal rule lists, besides its substantive outcomes, at least one branch for "none of the above" - and that branch is **reported as a result**,
not as a bug. (2) A branch whose condition has several clauses prints which clauses held, so a fall-through cannot borrow a label it did not earn. (3) When the
registered dichotomy is the wrong question, the report says so in the verdict's own words, because "the question was wrong" is a finding and choosing a side is
not. (4) Any classification with a residual band (here 7-9 % of deaths between the two thresholds) publishes the band next to the shares; a split of 84.5 / 8.4
without its 7.1 is a two-category claim in disguise.
Report: `reports/2026-11-03-x127-absorption.md`.

**The unit of the budget must be the unit of the claim (03.11, X128).** X127 and X128 classified a structure's disappearance with a **world-level** area budget:
absorbed if the total area of all surviving structures grew by at least half the dead structure's area. In a world of twenty isolated spots that is satisfied by
growth *elsewhere*, so the lattice's "84.5 % absorbed" described the world's net growth and not a transfer into a neighbour. The local rebuild (survivors within
r_dead + r_survivor + 2 cells) moved that cell to 55.3 % and produced a category the world-level version could not express - deaths with no live neighbour at all,
31.3 % of the lattice's endings.

Rules. (1) A budget argument names the **set over which it is summed**, and that set must be the one the claim is about (a neighbour, a patch, a body, a world).
(2) If the same statistic changes by more than 0.20 when the summation set is narrowed to the claim's own unit, the wide version was measuring something else and is
withdrawn, not qualified. (3) Any classification by threshold publishes its **residual band** next to the shares; a residual that shrinks from 7-9 % to 1-3 % when
the instrument is fixed is evidence that the wide version was absorbing real cases. (4) A category that exists only in one habitat ("isolated") is a finding about the
world and must be a category of the instrument, not a residual of it.
Report: `reports/2026-11-03-x128b-local.md`.

**A variable the instrument fixes cannot be used to match (03.11, X129).** X129 tested the deflationary explanation of the kinship result - "the absorber is a
sibling only because siblings are born adjacent" - by matching absorptions on contact distance, the normalised distance between the two centroids. The match
degenerated: **100 % of partnered absorptions fell inside the contact band**, because the neighbourhood that produced the partners had itself been defined as
contact plus two cells. A control built on a variable that the instrument's definition already fixes cannot fail, and therefore cannot test anything.

Rules. (1) Before matching, name the variable's range **in the sample** and, if the instrument defines that range, do not call the comparison matched - say it is
fixed and use the invariance as the statement instead. (2) When a match degenerates, report it as part of the result: "every absorption is a contact event" is
itself a finding about the medium and it carries the inference that a distance explanation is unavailable rather than refuted. (3) The stronger claim is the one
that survives the invariance: at the same geometry, the genealogy of the neighbour differs by 49.6 points between habitats. (4) A design that needs a matched
population must build the matching variable **outside** the instrument's own filter (an independent measurement), otherwise the plan is void by construction and
should be refused at §3d, not discovered after the run.
Report: `reports/2026-11-03-x129-geometry.md`.

**The pair's ordering must be applied in every block that uses the pair (03.11, X130).** X130's survival readout was copied from X126 but computed on the daughters in
**birth order** instead of the larger/smaller ordering that defines the claim. Within a pair the two orderings differ on half the pairs, so the differences cancelled:
the script printed **0.0219** where X126 says **0.2496**, and the end-survival control caught it before the run was read. A second defect in the same script printed a
median with an interval bootstrapped from the **mean** (median 80, interval [127, 211] - an interval that does not contain its own point estimate).

Rules. (1) When a statistic is a difference inside a pair, the ordering rule is applied in **every** block that touches the pair, not only where it is defined; a helper
that returns the ordered pair, used everywhere, is cheaper than the bug. (2) An interval belongs to the statistic it is printed with: a bootstrap of a cousin is a
different claim, not a conservative version of this one. (3) A re-derivation prints the source number it is supposed to reproduce **next to** the recomputed one, so a
cancellation of the kind above cannot look like a real effect of size 0.02. (4) When two published shares of the same event differ, check the denominators before the
finding: "18 % of sister pairs re-merge" and "64 % of absorptions take a sibling" are both true and neither explains the other away.
Report: `reports/2026-11-03-x130-remerge.md`.

**Cells that share seeds are compared paired (03.11, X131).** X131 tested whether the habitat differences survive resampling worlds. Its registered rule compared
the **marginal** world-level intervals and called a difference world-level when they did not overlap. The three cells use the same seeds 301-310, so the design is
paired and the marginal test throws that away: for the absorbed share and for the depth contrast the marginal intervals overlap while the **per-seed difference**
excludes zero. Both results were printed; the paired one is quoted.

Rules. (1) When two arms share seeds, units or pairs by construction, the test of their difference is the **paired difference**, bootstrapped over those units - the
overlap of two marginal intervals is a weaker test of the same hypothesis and must never be reported as *the* test. (2) A pair-level interval is **within-world
precision**: quoting it as a statement about habitats is the same error as quoting a filtered statistic without its filter. (3) Before a cross-habitat claim, compute
the power from the observed per-world spread: X131 puts 30-40 worlds at the price of the survival contrast, which is worth knowing before the claim is written.
(4) When a test is replaced by a more powerful one, both results are printed and the replacement is stated in the report - not because the new test is more
favourable, but because it is the test the design implies.
Report: `reports/2026-11-03-x131-worlds.md`.

**Порог классификации нельзя сравнивать с самой манипуляцией.** Если класс решается допуском на расстояние, а свип
двигает это расстояние на одну клетку за точку, то рано или поздно решает допуск. 03.11 так появилось «третье
состояние» у X139: при зазоре 5 клеток «поглощение» требовало, чтобы партнёр был в пределах `r_dead + r_other + 2`
клеток — при разделении 10 порог был 10.8, при разделении 11 — 10.1, и одна и та же динамика (два тела стали одним
под новым uid) получила два разных имени. Правило: до публикации границы класса показать, что запас между измеряемой
величиной и порогом больше шага свипа, и определить класс так, чтобы он вообще не зависел от допуска.


## Проверка манипуляции обязана читать состояние, а не запрос

03.11 (X153). Пре-регистрация требовала, чтобы артефакт фиксировал зазор 7.5, «а не округлённые 7 или 8». Контроль
прошёл: `params.init_spots = 6.0:19.5`. Но параметр — это **запрос**, а не **состояние**: если бы зонд округлил
разделение внутри, параметр всё равно прочитался бы как 19.5, а плечо оказалось бы молчаливым дубликатом зазора 7.

Правило: контроль манипуляции читает **первый залогированный кадр** (площади компонент, занятую долю) и сравнивает его
с соседним плечом. В X153 именно это и обнаружило и что манипуляция дошла (110 клеток на диск против 108 — на одну
клетку больше), и что она дошла **не бесплатно**: полуклетка сдвинула растеризацию, то есть плечо — это зазор плюс ~2 %
площади, и так и написано в отчёте.

Тот же класс, что «реализация расходится с определением», но на уровне входа: проверка на параметре проходит всегда,
потому что параметр записывается из того же запроса.

## A rasterisation bound must be registered on the effective gap, not on raw cells

03.11 (X154). The pre-registration bounded the first-frame disc area at "at most 2 cells per disc across the four arms" —
a check on whether the half-cell separation moved the *disc* as well as the gap. The measured areas were **110 / 108 / 110 /
113** cells per disc: a spread of five, and a 3-cell move into the last arm. The control failed by one cell, in a series whose
verdict was otherwise clean.

The bound was unsatisfiable, not informative. The nominal radius is 6.0 and pi*6^2 is 113, so the last arm is the fully
covered disc and the earlier ones are under-covered; a radius-6 disc placed at half-cell separations can only land on cell
areas 108, 110 or 113, i.e. the *quantisation* of the disc is larger than the bound. Converted to an effective radius
sqrt(A/pi), the realised surface gaps were 6.67 / 7.27 / 7.67 / 8.00 cells — monotone in the nominal gap, so no arm was a
duplicate and none was reordered.

Rules. (1) A manipulation bound on a rasterised quantity is registered in the **physical** unit of the claim (here: the
effective surface gap `separation - 2*sqrt(area/pi)`), with the quantisation step printed next to it; a bound smaller than the
grid's own quantisation is a guaranteed void and cannot detect anything. (2) When such a bound fails, the report converts the
rasterised values to the physical unit and says whether the arms keep their order, rather than voiding on the raw number.
(3) The direction of the confound is stated: a larger disc at a fixed centre separation contacts *earlier*, so it works
against a "the time widens as the gap grows" reading, not for it. (4) A failed control is printed in the report and in the
queue note even when the verdict stands — a control that is quietly re-read is indistinguishable from one that was never
registered.
Report: `reports/2026-11-03-x154-mixing-curve.md`.

## A "near-perfect" criterion must be written for the degenerate case

03.11 (X155). The pre-registration for the heredity ablation said the mutation-off arm counts as near-perfect if `r ≥ 0.99`
and the slope `≥ 0.95`. The arm produced **no coefficient at all**: with `--mutation 0` the trait is constant (`s` = 1.0 in
every component at every step, between-component sd 0.0, 100 % of parent-daughter pairs exactly equal), so both statistics are
undefined — zero variance in the denominator. The strongest form of perfect transmission is a vanished variance, and the
registered rule could not express it.

The arm was read under a fallback written in the plan **after** the data and labelled as such: sd 0 in every run, at least
99 % of pairs exactly equal, and the mutation-on arm's residual within a factor of two of the rule's own `sigma`. All three
held (0.1487 / 0.1495 against 0.15), so the verdict stands — but a criterion amended after the data is weaker evidence, and
the report says so in the controls section.

Rules. (1) A threshold on a correlation, ratio or slope is accompanied by its **degenerate case**: what the arm reports when
the denominator vanishes, and whether that outcome counts for the claim or against it. (2) The degenerate case is registered
as a branch, not as an excuse: "if the variance is zero, the criterion is X" must appear next to the threshold, because a
perfect manipulation is exactly the one that destroys the statistic. (3) An amendment written after the data is dated, marked
post hoc, and quoted in the report's controls section; it may not be folded into the plan as if it had been there.
Report: `reports/2026-11-03-x155-heredity.md`; plan: `reports/2026-11-03-x155-heredity-plan.md` (§Amendment).
