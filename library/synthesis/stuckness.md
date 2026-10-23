# Синтез: почему системы застревают

Готовые абзацы для рукописи (английский — как в `paper.md`), с русскими пометками о том,
на что опирается каждое утверждение и где граница. Источники — блоки A1–A5, B1–B4, C1 из
[`../hypotheses/alife-lineage.md`](../hypotheses/alife-lineage.md).

## §5.x. Why systems stall — and what that implies for the pond

### Абзац 1. Насыщение, а не деградация

> Digital evolution systems do not fail by collapsing; they fail by settling. In Tierra,
> diversity grows as recombination of an already present replication mechanism, while
> parasites and cheaters appear early and persist (A1). In Avida, a complex function is
> assembled only when the intermediate steps are themselves rewarded; when only the final
> function counts, it is not found at all (A2). In Polyworld, the maximal Lyapunov
> exponent rises during behavioural adaptation and then plateaus, with the passive control
> overtaking the driven runs (A5). The common pattern is a reversal of selection after
> adaptation: stability is preferred to further structure. Our own numbers sit at one such
> plateau — 601, 594 and 532 are three strategies on the same level, not three mechanisms.

**Пометки.** A1, A5 — `[К]`; A2 — `[К]`. Числа 601/594/532 — наши, из отчётов пруда, не
из литературы. Утверждение «stability is preferred» — формулировка авторов A5 (MLE/OOC),
перенос на наш стенд — наша интерпретация, в тексте это надо разделить.

### Абзац 2. Инновация дешёвая, неограниченность дорогая

> Open-endedness has two separate requirements: unboundedness, i.e. trajectories that do
> not repeat within the return time of the isolated system, and innovation, i.e. states
> absent from every isolated control run. Empirically, innovation is cheap (more than 99 %
> of runs in the relevant variants) while unboundedness is rare (below 5 %), and only laws
> that read the system's own state deliver both (B1). The distinction matters for
> measurement: a plateau in a diversity metric is therefore not evidence of a lack of
> novelty, but of return. What separates drift from innovation is the time of return, not
> the count of distinct configurations.

**Пометки.** B1 — `[К]`. Проценты — из работы, не наши. Для нас это ограничение на
формулировку: «новизна есть, возврат в пределах окна есть» вместо «эволюция открытая».

### Абзац 3. Застревание снимается сменой задачи, а не мощностью

> POET does not optimise harder on a fixed problem: it co-evolves environments and their
> solutions and admits a new environment only if a solution for it exists, transferring
> solutions between environments. The ablation is decisive — without transfer no
> environment of maximal difficulty is solved and coverage of the environment space drops
> significantly (Mann–Whitney, p < 2.2e-16 over 3000 sampled environments), while direct
> optimisation with twice the budget stalls in the local optimum of "freeze before the
> obstacle" (B3). Darwin Gödel Machine adds the complementary lesson: an archive of
> intermediate variants that are worse than the current best beats greedy ascent, because
> the best lineage passes through nodes with a temporary dip in quality (B4).

**Пометки.** B3 — `[К]`, B4 — `[К]`. Числа и p — из работ. Перенос на «пруд»: наши
601/594/532 могут быть вариациями одной статичной задачи, поэтому минимальный решающий
тест — плечо с наследуемой средой против контроля «перенос выключен» (инсайт I-011).

## Таблица утверждений

| Утверждение | Доказательство | Что можно писать | Чего нельзя |
| --- | --- | --- | --- |
| Цифровые системы застревают на насыщении | A1, A2, A5 | «после адаптации тренд разворачивается к стабильности» | «система деградирует» |
| Инновация не равна открытости | B1, B2 | «новизна дешевле неограниченности» | «мы получили открытую эволюцию» |
| Застревание снимается сменой задачи | B3, B4 | «нужен механизм смены задачи/архив ступенек» | «нужно больше вычислений» |
| Наши три числа — один уровень | наши отчёты | «три стратегии у одного плато» | «три разных режима» |
| Индивидуальность требует контроля | D1 | «метрика — тройка A*/A/nC» | «MI = индивидуальность» |

## Чего не хватает для статьи

1. **Прямого измерения времени возврата** на наших артефактах: без него абзац 2 —
   литературная рамка, а не наш результат.
2. **Плеча с наследуемой средой** (I-011): без него абзац 3 остаётся чужим результатом.
3. **Согласованной метрики режима** (H39): развёртка по цене поддержания не запускалась.
4. **Сверки чисел** 601/594/532 с конкретными отчётами и конфигами — в тексте они должны
   иметь ссылку на артефакт, а не на переписку.

## История

- 2026-10-23 — создано по разбору ALife-списка (`alife-lineage.md`).
