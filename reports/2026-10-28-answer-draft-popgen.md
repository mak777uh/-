# Черновик ответа Castedo Ellerman (популяционная генетика) — не отправлен

**Статус:** черновик. Внешняя коммуникация — только по «ок» владельца (§4a контракта).
**Кому:** участнику темы [«Examples of utility to empirical science»](https://leanprover-community.github.io/archive/stream/395462-Natural-sciences/topic/Examples.20of.20utility.20to.20empirical.20science.html)
в потоке Natural sciences Lean Zulip, декабрь 2025. Он спросил, как Lean может быть полезен эмпирической
науке, и отдельно — как формализовать **популяционную генетику**.

## Честная оценка: хороший ответ есть, но частичный

| можем сказать | чем подтверждаем |
|---|---|
| **Что именно стоит формализовать** (инварианты модели, а не статистику) | 17 гипотез, 31 теорема в `formal/` — бюджет, порядок обновлений, замыкание, пороги, гейт зажигания |
| **Пример пограничной теоремы, которая реально сужает перебор** | «подстройка успевает до смерти»: из `E₀/(цена − доход)` выводится условие, при котором обучение вообще может помочь |
| **Практика, без которой формализация тонет** | одна величина имела у нас **четыре** значения (6.90 / 8.22 / 12.35 / ~80) в разных документах; лечится реестром определений + машинным пересчётом (`lab/metrics.json`, гейты) |
| чего **не** можем | **ни одной** формализованной теоремы популяционной генетики: ни Райта–Фишера, ни диффузионного приближения, ни вероятности фиксации |

## Черновик текста (английский, как в потоке)

> Following this thread with interest — I work on a small "artificial life" kind of question: whether a
> lineage in a simulated cell world can be a unit of selection at all, and what a heritable trait costs.
> I can offer a concrete data point, including a negative one.
>
> **What we formalized (and what we deliberately did not).** We have 17 hypotheses / 31 theorems in Lean, but
> every one is about *invariants of the simulator*: energy budget conservation per step, budget conservation
> under **any** order of asynchronous updates, finite exhaustion under zero inflow, a survival threshold with
> an exact time-to-death, and a boundary theorem for when adjustment can pay off before death. We formalize
> no statistics and no "agency": for us the honest split is Tooby-Smith's criterion — formalize what can be
> stated rigorously, and *name* what cannot.
>
> **Two things that may transfer to population genetics.**
> 1. *Asynchrony matters for invariants.* Our order-independence theorem exists because GPU and CPU update
>    cells in different orders; an individual-based model of a population has the same issue, while the
>    classical Wright–Fisher formulation hides it behind generations. If you formalize an IBM, the first
>    theorem you need is exactly "the accounting does not depend on the update order".
> 2. *Formalization surfaces hidden assumptions.* We tried to state "the rule preserves Euler characteristic",
>    found it false, and the only honest form was `|Δχ| ≤ K` with `K` an explicit function of the kernel.
>    Chow's special-relativity example in this thread is the same phenomenon at a different scale.
>
> **The trap we hit, which I suspect is common in empirical fields.** Before any theorem, we had to fix
> definitions: one scalar ("marginal advantage") existed in four mutually inconsistent versions across our
> own documents — 6.90, 8.22, 12.35 and ~80 — because four different denominators were all called by the same
> name. The fix was mechanical: registry of definitions + independent recomputation in CI. Cheap, and it
> removes a whole class of "our theorem is about a different quantity than our data" failures.
>
> **What I cannot offer:** any formalized population-genetics result. Our empirical numbers about selection
> (a trait's rank-correlation with realised cell-steps ≈ −0.37, 95 % CI [−0.40, −0.27]; effective lineages
> 1.5 → 6.1 when updates are desynchronised) are simulation results with intervals, not theorems, and I would
> not dress them up as formalization.
>
> If it is useful, I am happy to describe how the formal part is wired into CI (integrity check of the Lean
> sources, so a theorem cannot silently disappear or lean on an axiom).

## Что нужно, чтобы ответ стал сильным (не сегодня)

Один маленький настоящий результат из популяционной генетики, формализованный: например, что при
нейтральном дрейфе в простейшей модели Морана частота аллеля — мартингал, и фиксация происходит с
вероятностью 1. Это требует вероятностной библиотеки (в mathlib есть MeasureTheory, но путь не короткий),
зато это был бы **первый** формализованный факт в разговоре, а не методология. Оценка: 1–2 дня работы,
риск средний. Ставлю в очередь как предложение, а не как обещание.

## Решение владельца

- **Отправлять ли ответ** (и в каком объёме: только «что формализовали» или с числами).
- **Делать ли формализацию мартингала Морана** — это единственный способ превратить «частичный ответ» в
  «полный».
