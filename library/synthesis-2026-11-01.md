# The elephant after one night: what the field line now says about conditions for life

1 November 2026, 08:40. Written between two runs, after four campaigns in one night (20 + 30 + 20 + 10 + 15 + 5 runs).
This is not a report of results — each of those has its own page — but the shape they make together, which changed twice
during the night and is now stable enough to state.

---

## 1. What was actually established

| finding | evidence | status |
|---|---|---|
| Heterogeneous inflow **delays wavelength selection at 96 cells** | homogeneous selects q = 8, λ = 12 units (45 % of low-q power); heterogeneous stays broadband on 96, entropy 2.19–2.25 | **holds on peak position across four grids** (96, 108, 120, 144 at `dt = 0.5`): the homogeneous arm peaks at 12 units wherever it patterns; the heterogeneous arm never does — it concentrates on the box scale. An earlier withdrawal based on concentration was itself withdrawn — see §10el |
| The advantage in component count is an **advantage in small, short-lived pieces** | contrast +3.57 falls to +1.36 at 32 cells, +0.07 at 128 cells | free re-analysis, 10 seeds |
| Heterogeneity produces a **transient perforated web** | β₁ +9.0 (10/10 seeds), survives matched occupancy (+5.5, 10/10) and every threshold tested | transient only; gone by t = 6000 |
| **Transmission follows geometry** | divisions 308 → 79 → 21 as inflow amplitude falls 0.5 → 0.25 → 0.1 (14.7×, 5/5 seeds), spectra sharpening in the same order | dose-response, five seeds |
| **Selection is easy, coexistence environmental** | survival channel drifts +0.48 (10/10) and +0.84 (9/10); without frequency dependence 9/10 seeds fixate into one structure | 10 seeds, artifacts in git |
| Heritability we measured is **mechanical** | Spearman(divisions, r) = +0.79; more division, higher fidelity | 24 runs |
| Niches **amplify** selection rather than enable it | drift +0.204 without niches against +0.835 with | one series, secondary endpoint |
| The seed reaches the field **only through the trait channel** | `beta = 0` arms give byte-identical component series across ten seeds | structural property |

Three of these were corrections of our own claims made hours earlier (the spectral reading, the heritability story, the
"environment decides diversity" sentence). That is the normal rate of error in this line, and the reason every claim above
names its window, its ruler and its seed count.

## 2. The sentence the night produced

> **In this medium, heterogeneity buys turnover at the cost of organisation.** A field with a heterogeneous inflow never
> selects a pattern wavelength; it fragments into small pieces, those pieces divide fifteen times more often than in a
> smooth world, and division is the only channel through which composition is inherited. So the same condition that
> destroys spatial regularity multiplies the events in which lineages could exist — and those lineages are, so far,
> copied rather than selected.

That is a statement about a digital medium, not about a counter, and it is the first one in this project that speaks to
the actual question: what does an environment have to be like for something life-like to have a foothold?

## 3. What it implies for "conditions for life"

Reading the results together, a candidate condition needs three things, and the medium supplies them unevenly:

| requirement | does heterogeneous inflow supply it? | evidence |
|---|---|---|
| **turnover** — structures appear and disappear fast enough for lineages to matter | **yes, strongly** | 308 divisions against 17.5; 18× |
| **heritable variation** — something is transmitted | **yes, but mechanically** | r = 0.97, imposed by the copy rule, not emergent |
| **coexistence** — diversity persists instead of one winner | **weakly** | frequency dependence keeps 2.5 structures against a control's 36 |
| durability of organisation | **no** | durable structures 1.3 against 1.2; large components indistinguishable |

So heterogeneity is a **turnover generator, not an organisation generator**. If life-like organisation requires structures
that persist long enough to accumulate change, an environment that only fragments is hostile to it — the very condition
that creates the events removes the objects that could carry a history.

That is a negative result of the useful kind: it says which environmental knob to turn next (something that slows turnover
without removing variation), and it says the trait channel alone will not do it.

## 4. What we now know about our own instruments

Three lessons that outlive the numbers:

1. **Every effect we have is a property of a window.** The count contrast, the hole excess, the wavelength selection — all
   are transients that decay. A claim without a window is a claim about an average that hides its own history.
2. **Two kinds of numerical dependence.** Dependence on the *scheme* (dt, grid, boundary conditions) must be declared as
   part of the regime. Dependence on the *ruler* (threshold, size floor, cadence, identity rule) must be shown as a curve.
   We spent a week learning to separate them; the distinction now appears in every report.
3. **A control with no seed variance is one sample.** The field world has no seed-dependent start, so `beta = 0` arms are
   deterministic. Stating this turned three "10 seeds" claims into "one field, ten trait realisations", which is what they
   always were.

## 5. What is genuinely open

- **Does the late concentration become selection?** Running now: 24 000 steps of the same world, four field snapshots.
- **Can turnover be slowed without losing variation?** The obvious knob is the inflow correlation length; the dose
  experiment says amplitude controls turnover monotonically, so a length sweep is the natural next axis.
- **Is there any channel where a trait pays without a matching cost?** Growth had a cost, survival did not; what else is
  there in this world — dispersal, adhesion, decay threshold — is an open design question.
- **Does anything here transfer to the pond line?** Both lines now say diversity comes from the environment; neither has
  shown a case where it comes from the organisms.

---

*Sources: the nine reports of 1 November in `reports/`, the plan sections §10ea–§10ef, and the aggregates under
`morphogenesis/experiments/E09_pond/`. Every number above is reproducible from a file in this repository — that was not
true yesterday for half of them.*

## Correction, 11:00 — the spectral claim is about the grid

The refinement run of 11:00 (X64) changed one row of the table above and, with it, the shape of the argument. The
heterogeneous world does not *prevent* wavelength selection; at 96 cells the pattern has only twelve cells per period and
the inflow modulation, which has the same period, destroys it. At 144 cells — same physical domain, diffusion rescaled
correctly — the heterogeneous arm selects a mode as the homogeneous one does.

This is the **non-Platonic** effect Davis describes, now measured in our own world: a pattern that exists at one
discretisation and not at another. The practical consequence is a rule for every spectral sentence in this project:
**name the grid**, or the sentence is about the instrument.

What the night's sentence becomes after this: heterogeneity buys turnover at the cost of organisation — the *turnover*
half is a count and is unaffected (X59's dose-response stands); the *organisation* half is grid-dependent, and the honest
version says so.

**And the topological half at the refined grid (11:15).** The same saved fields give β₁ at 144: the heterogeneous arm has
more loops at every snapshot (median excess +13 at physical time 2000, +12 at 6000) but the sign holds in only 4/5 and 3/5
seeds, against 10/10 at 96, and the occupancy control has not been run there. So the web is a hypothesis supported by two
grids, not a result — and the table row above should be read with that in mind.

## Final correction of the day, 13:10 — twice withdrawn, now restored

The spectral claim was withdrawn at 11:00 and restored at 13:10, and the reason matters more than the outcome: both the
original claim and its withdrawal were judged by **concentration** (share, entropy) while the sentence was always about
**position** (does the peak sit at the medium's wavelength). Once position is the readout, the picture is sharp and stable
across four grids: the homogeneous world picks 12 units wherever it patterns, the heterogeneous world never does.

Two lessons, both about instruments rather than physics:

1. **A summary number is not the claim.** Share and entropy compress a spectrum into one value and can make two very
   different spectra look alike.
2. **The right fix was a criterion, not a rerun.** X66 cost twenty runs, but the map was already there; what was missing was
   the quantity to read off it.

The row above is the corrected form. Everything else in this page — turnover, heritability, coexistence — is untouched by
this sequence.

## Last word on the spectrum, 13:50 — tested against two domain sizes

X67 doubled the domain with the cell size fixed. The homogeneous pattern stayed at twelve units (q = 16), and the
heterogeneous peak stayed at q = 1 — it moved with the box. So the heterogeneous concentration is **the domain**, not a
structure: that world has less organisation, not a different kind of it.

The spectral claim has now been tested against five grids (96, 108, 120, 144, 192 cells in the domain-size run) and two
domain sizes (96 and 192 units), with the time step held fixed where it matters. Its final form:

> Heterogeneous inflow suppresses the medium's twelve-unit pattern. What concentration the heterogeneous field shows is
> the box itself, so it is not alternative organisation but the absence of it.

## Where to go next, and what is deliberately not being done now

The day closed three questions and left three, and the order below is a judgement about cost rather than importance.

**1. Turnover, with a readout that can carry it.** X59's dose-response is the strongest evidence in the line (divisions
308 → 79 → 21 as amplitude falls, 5/5 seeds), and X63 showed why the correlation-length profile could not be resolved: the
count is heavy-tailed, with a tenfold spread between seeds inside one arm. The next experiment is not another scale sweep
but **more seeds at fewer points** — three scales, fifteen to twenty seeds each — with divisions per component per 1000
steps as the readout. That is about two hours of GPU and it would turn a hypothesis into a curve.

**2. Lifetimes and identity.** The weakest link in the published line has not moved all day: the median lifetimes (57
against 4046 steps) rest on the overlap rule, and the tracking literature we read says that rule is a convention, not a
standard. The fix was specified this morning and never executed: one run saving masks, then lifetimes under overlap
0.3 / 0.5 / 0.7, plus a persistence-based definition on the same fields. Until it runs, the lifetime contrast should be
quoted with its rule attached, exactly as the v1.6 text does.

**3. The publication decision.** The v1.6 package is built, checksummed and sitting on disk; the two-sentence insert about
small components is written and costed. That decision is the owner's and it has been open since the small hours.

**What is not being done, and why.** No further grid work on the spectrum: it has been tested against five resolutions and
two domain sizes and the answer stopped changing. No more reading: the corpus is at the point where the next useful text is
an implementation, not an argument. And no new "quick" run at the end of a long day — the two claims that went wrong today
both went wrong through a rushed criterion, not through a rushed measurement.

One rule from today is worth keeping above the rest: **a claim names the quantity it is about.** Twice this line judged a
sentence about *position* by a number that measured *concentration*, and once it judged a sentence about the medium by a
number that measured the box. Each time the measurement was fine and the reading was not.

## Correction, 14:35 — the lifetimes belong to the trait channel, not to the field

X68 varied the overlap cutoff that defines identity, and its own leak check killed the first design within one seed: the
rule cannot be varied in isolation, because composition is **carried per component, inherited with the identity, and paid
for in growth**. Change who inherits and you change the field.

In the neutral world where the rule is separable, the ordering reverses: heterogeneous components live **longer** (5999,
5044, 2607 steps at cutoffs 0.3, 0.5, 0.7) than homogeneous ones (4030, 1565, 1565) — the opposite of the published 57
against 4046, which was measured with the feedback on.

So the sentence is not "structures in a heterogeneous field are short-lived". It is: **a trait carried along lineages and
paying for its carrier's growth fragments the field into short-lived pieces**. The contrast is a property of the
two-channel world, and the field geometry alone produces the other sign.

This is the third claim today to change its object rather than its number, and the pattern is consistent: what looks like a
property of the medium keeps turning out to be a property of the measurement channel attached to it.

## Added 17:30 — the size-heredity question, and a defect the repair found

The afternoon's last experiment asked whether the medium itself carries heredity of form, with no copying rule imposed.
It does, but weakly, and testing it properly cost more than expected.

- **Heredity is real and belongs to the pair, not the place.** Over five genuinely different worlds a daughter's peak
  area correlates with her own parent's at 0.42–0.57 (mean 0.499), each above its own pairing null. The control the
  external answers demanded — a non-parent companion at the same distance — gives −0.003 against the observed 0.582, and
  the partial correlation controlling distance, crowding and two local field statistics is 0.545. So the parent is not
  just a proxy for a rich neighbourhood.
- **It is partial.** Slope 0.38–0.57: roughly half the parent's deviation is erased within one division. That is
  "limited heredity", not a lineage mechanism — enough for a memory of form one generation deep, not enough for
  cumulative evolution.
- **Richness modulates it instead of causing it.** Heredity is 0.18 in the driest third of the field and 0.63 in the
  richest, while the local environment does not predict the area itself. A rich neighbourhood lets the pair similarity
  show; it does not manufacture it.
- **The defect that made the first numbers wrong.** In a world without feedback (`beta = 0`) the seed does not move the
  geometry at all: the start is a fixed blob and the seed only feeds the trait channel. Five "seeds" were one universe
  copied five times, so the morning's 0.334 was a single draw and every "5/5 seeds" sentence about geometry was one
  observation. Fixed with `--init-jitter` (seed-dependent start position and radius, inert when off) and gated by
  `check_seed_replication.py`, which now measures per family whether the seeds actually produced different worlds. Blast
  radius: exactly the `beta = 0` arms; the amplitude dose, correlation length, scale sweep, grid map and transmission ratio
  all have genuinely distinct worlds behind them.

The general lesson, which is the day's most transferable finding: **replication is a property of the world, not of the
seed count.** A world that ignores its seed cannot be replicated by more seeds, and a null calibrated on copies is too
tight by roughly the square root of the number of copies.

**Correction on the lifetimes, 17:30.** The sentence above about the neutral world reversing the ordering at all three
cutoffs was measured in one world per rule: in a `beta = 0` world the seed does not move the geometry, so the five "seeds"
are one universe. Replicated on five real worlds (`--init-jitter`, 30 runs), the reversal is unanimous at the loose cutoff
(5999 against 2846–4030), four of five at the medium one, and **goes back to the published direction at the strict cutoff**
(heterogeneous 712–1417 against homogeneous 1565–3985, 5/5). The identity rule therefore moves the *sign* of the contrast,
not only its size — and the strict-cutoff fragmentation into 35–66 uids is where the rule visibly manufactures entities.

## 02.11, ночь — что среда запоминает и что нет (X71–X77)

Семь экспериментов за ночь сложились в одну фразу, которой раньше не было: **среда несёт память о величине и не несёт памяти
о форме, и глубина памяти зависит от того, одна у неё предпочтительная шкала или две.**

- **Размер наследуется, и это родитель, а не место.** X70 дал 0.42–0.57 по мирам; X72c пересчитал оба прибора на **одних и тех
  же 1 955 событиях**: площадь даёт 0.457 против 0.069 у ближайшего не-родителя, а смешение полос — 0.853, которую сосед
  перебивает. X77 закрыл последнее измеримое возражение: средний размер соседей в радиусе длины волны предсказывает дочь на
  **0.01** (патч из двух структур), то есть «общая среда» в этом мире просто не связана с размером.
- **Память забывается экспоненциально.** X73: 0.475 → 0.204 → 0.072 по трём делениям, фактор ≈ 0.4 за деление, полураспад
  **0.7–0.8 деления**. Правило копирования дало бы плоскую кривую; среда даёт забывание.
- **Глубина памяти — свойство точки плоскости, а не константа.** X74/X75/X76: полураспад **1.47** при `F=0.030`, **0.57** при
  0.033, **0.73** при 0.035, **0.56** при 0.037, **1.61** при 0.040. Не U-образная кривая, а **две ступени**: внутри
  мультистабильной полосы 0.56–0.73, вне её 1.47–1.61, разница в 2.5 раза.
- **Мир, который может быть двумя вещами, помнит меньше.** Механизм не в частоте делений и не в разбросе размеров (оба
  монотонны по `F`, X74) — остаётся то, что есть только у полосы: **два сосуществующих масштаба** (X71: 12.0 и 8.73 клетки,
  устойчиво 24 000 шагов, ширина 0.002–0.005 при пороге 0.2).
- **Форма не наследуется ни в каком приборе.** Три инструмента (расстояние до соседа, класс по argmax, доли мощности) дают один
  ответ: ничего родитель-специфичного не выживает контроля на патч. Смешение оказалось **региональным и историческим**:
  η² = 0.307 внутри мира, 0.004 между мирами — область богата смешением потому, что так сложилась её история, а не потому,
  что так предписано узором.

Практический смысл для вопроса «условия для жизни»: среда даёт состояние с полураспадом меньше поколения — достаточно, чтобы
дочь походила на мать, недостаточно, чтобы линия накапливала. Разрыв с требованием кумулятивного отбора — примерно порядок, и
теперь это число, а не впечатление. И у этого числа есть ручка: место в плоскости параметров, где среда нерешительна, — худшее
место для памяти и лучшее для разнообразия форм.

**02.11, 04:30 — ручку нашли и повернули.** «Два масштаба» перестало быть описанием: в раннер добавлен **составной узор**
(две длины волны в одном `G`, по умолчанию выключен, якорь бит-в-бит), и на клетке `F = 0.030` с длинной памятью (1.47)
навязанная вторая шкала **сократила полураспад до 1.03** — в 1.43 раза, при неизменном начальном сходстве (0.498 против 0.507) и
при том, что 9 из 10 миров действительно несли два спектральных пика.

Величина эффекта меньше, чем у собственной полосы среды (0.56–0.73, то есть в 2.1–2.5 раза), и это честная граница знания:
предписанная шкала — более слабое возмущение, чем два по-настоящему конкурирующих аттрактора, либо мелкость полосы отчасти
про близость к фазовой границе (пятна ↔ лабиринт). Первый опыт (X78) при этом **уничтожил мир** (одна компонента), и именно этот
провал показал, что «навязать масштаб» и «сменить режим» — разные операции; понадобился композит, а не другая длина волны.

**02.11, 07:30 — полминуты на арифметику, которая отменяет два вывода.** Пока шла развёртка по весу, выяснилось, что линейка
сама врёт. Полураспад у нас — **отношение** (λ из ρ₂/ρ₁ и ρ₃/ρ₂), а не уровень: если начальное сходство падает, а затухание
замедляется, полураспад *удлиняется*, хотя память стартует ниже. На одних и тех же данных X80 это дало три разных ответа —
пул пар говорит «наклон» (0.86 / 1.18 / 1.25), медиана по мирам говорит «впадина» (1.04 / 0.52 / 1.16), а ρ₁ говорит «впадина»
(0.509 / 0.391 / 0.499). Пересчёт старых клеток по мирам (без новых прогонов) сохраняет **направление** полосы — 1.26 и 1.82
снаружи против 0.66 и 0.92 внутри — но не её **величину**: 2.0–2.6× при пуле против 1.4–1.9× по медианам, а в клетке F = 0.033
три мира из десяти вообще не поддаются подгонке (лаг-2 или лаг-3 ≤ 0). Значит «два уровня, фактор 2.5» — это число про
*способ усреднения*, и теперь оно так и подписано.

Второе, крупнее: **канал не дотягивается**. Три пилота с предписанным отношением мощности второго пика 1, 4 и 16 дали в поле
0.19, 0.31 и 0.28. Шестнадцатикратная мощность покупает плечо в треть. Среда держит свою длину волны и пускает чужую только
меньшинством — потому и X78 «схлопнулся» в одну компоненту, и веса в X79 двигали почти ничего, и три клетки X80 оказались
спектрально почти одинаковыми (0.27–0.31, 0.18–0.23, 0.27–0.34, если мерить долю, а не считать локальные максимумы).

Для вопроса о жизни это важнее, чем кажется. Среда, которая *не даёт* навязать себе масштаб, — это среда с собственной
устойчивой длиной волны; её разнообразие нельзя раздуть извне притоком, его можно менять только переводя её в другой режим
(полоса, лабиринт, пятна). То есть «условия для жизни» упираются не в то, сколько разнообразия мы подадим, а в то, сколько
среда удержит. Мерить надо её пропускную способность — и это ровно то, что делает X82.

**02.11, 09:20 — прибор показывал не то, что мы думали, и это меняет главный вывод.** Полураспад мы уже пересчитали (см. выше), но
дальше выяснилось хуже. Все спектральные числа линии — моды X71, «два пика» X78b, доли X79/X80 — считались по **радиальному**
профилю, то есть по мощности на кольце |k|. Навязанный узор — шахматка sin(qy)cos(qx), её мощность стоит на четырёх
**диагоналях** (±q,±q): для 12-клеточного узора |k| = 8√2 = 11.3, то есть кольцо 11. А полосатая морфология с периодом 8.7
клетки стоит на (±11,0), |k| = 11.0 — **то же кольцо 11**. Две разные вещи в одном кольце, и одна из них — сам навязанный узор.
Контрольный мир без всякой второй шкалы это и показывает: четыре самых сильных пика — диагонали 11.3 (63 123 и 57 209), а
следующие четыре — оси 8.0 (35 612 и 35 431).

Перечитав поля, которые X71/X71b/X71c уже сохранили (65 снимков, **без единого нового прогона**), разделяем два числа: q' —
осевое волновое число (период) и s — доля мощности на навязанных диагоналях (симметрия). Результат: **период не расщепляется**.
q' принимает 5–9 (10.7–19.2 клетки) во всех 35 мирах и **никогда 11** — того значения, которое нужно для ветви 8.7 клетки. Зато
симметрия идёт гладко: 0.38 при F = 0.025, 0.52 при 0.030, 0.78 при 0.035, 0.92 при 0.040 и дальше плато (ρ = 0.687 по 35 мирам).
Без узора s = 0.02–0.33, и период тот же — значит узор **не задаёт масштаб**, он задаёт **ориентацию**.

Отсюда три следствия, каждое бьёт по уже написанному. «Мультистабильность двух длин волн при 0.035» **опровергнута**: длина одна,
меняется симметрия, и меняется плавно. «Сосуществование устойчиво 24 000 шагов» — это устойчивость навязанной линии, она
устойчива потому, что узор зафиксирован. «Полоса шириной 0.002–0.005» — это ширина плавного перехода: при 0.033 s = 0.663, при
0.037 = 0.901, поэтому любой порог даёт «полосу».

И главное для вопроса о жизни: среда в этом ящике **не даёт сдвинуть свой масштаб**, но **отдаёт ориентацию**. Раньше мы
искали «два предпочитаемых масштаба» и мерили при этом навязанную линию. Теперь ручка одна и она чистая: симметрия от притока.
Следующий вопрос прямой — несёт ли память симметрия, а не масштаб; и прибор для него уже есть на сохранённых полях.

**02.11, 12:00 — день, в котором среда оказалась проще, чем мы думали, а прибор сложнее.** Следующий вопрос был задан сразу же, и ответ
пришёл отрицательный: ориентация память **не несёт** (X87, по двадцать миров на клетку: внутриклеточные коэффициенты −0.05 / −0.26 /
−0.21, частная корреляция с контролем притока −0.10; при двадцати мирах связь сильнее ~0.3 исключена, слабее — нет). То есть
среда задаёт ориентацию узора, но состояние, которое мерит наследование, живёт не в ней. Память принадлежит среде, а не тому, что
она в данный момент показывает.

Заодно выяснилось, что память зависит от притока **U-образно**: 1.82 / 1.16 / 1.07 / 2.08 / 1.60 при 0.025 / 0.030 / 0.035 / 0.040 /
0.045, минимум на краю полосы (X87+X88, по двадцать миров). Дольше всего помнит решётка вдали от полосы, меньше всего — её край,
снова долго — перколирующая мозаика. Направление «двух уровней», которое мы записали вчера, верное; числа — нет: они были пулом пар
на пяти мирах и занижены примерно в полтора раза. И там же нашлось третье, чего мы вообще не искали: **выше 0.049 среда практически
не делится**. При 0.045 — 636 линий, при 0.046 — 13 на мир, при 0.050 — ноль в медианном мире даже за двенадцать тысяч шагов (X89,
X90). И это не смерть мира: все двадцать четыре мира X90 — одна живая компонента с дырками, β₁ > 0; мозаика просто перестаёт
размножаться. То есть у среды есть область, где она **производит новых индивидов**, и область, где уже нет, — и граница между ними
не стена, а транзиент, длительность которого сокращается с притоком.

Что это говорит про «условия для жизни» прямее, чем всё остальное за сутки: наследование — не свойство субстрата вообще, а функция
**места в плоскости параметров**. Есть полоса, где среда нерешительна и память коротка; есть края, где она длинна; и есть область,
где индивидов не возникает, хотя узор жив. Если искать «жизнь» как явление, искать её надо не в правиле и не в масштабе, а в
пересечении двух условий: среда должна **удерживать** состояние дольше поколения и **производить** поколения вообще. Мы научились
мерить оба. Насколько это редкое пересечение — следующий вопрос, и теперь у него есть числа.

Отдельно про прибор, потому что это тоже часть результата: за сутки он трижды ошибался и трижды был пойман — радиальное кольцо
путало навязанную линию с морфологией; пул пар давал другой знак, чем медиана по мирам; частота логирования оказалась физическим
параметром, потому что мутации признака тянутся на каждом шаге. Все три ошибки нашли **контроли**, а не внимательность, — и это
лучший аргумент за то, что мы делаем: среда отвечает не на вопросы, а на измерения, и половина работы — держать измерение честным.
