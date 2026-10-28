# Готовый текст ответа Castedo Ellerman — можно отправлять

**Куда писать** (тот же поток, тот же тред — ответ на его вопрос):
<https://leanprover-community.github.io/archive/stream/395462-Natural-sciences/topic/Examples.20of.20utility.20to.20empirical.20science.html>

Через веб-интерфейс Zulip это тред **Natural sciences → Examples of utility to empirical science**.
Прямая ссылка для отправки (вход в Zulip потребуется):
<https://leanprover.zulipchat.com/#narrow/stream/395462-Natural-sciences/topic/Examples.20of.20utility.20to.20empirical.20science>

**Проверено:** репозиторий публичный (`mak777uh/-`, ветка `main`), все файлы по ссылкам ниже доступны
без входа (проверил через API GitHub).

---

## Текст (английский, копировать целиком)

> Hi Castedo — I have been asking myself a very similar question, from a different corner: I study a small
> simulated "cell world", and the empirical question is whether a lineage can be a unit of selection at all
> and what a heritable trait costs. I do not have population-genetics results in Lean, but I do have a few
> years of "what actually paid off" on a closely related problem, so here is the honest version.
>
> **What we do.** We run a simulation (a pond of cells, rules on a 32×32 grid) and we have two separate
> toolchains that must agree: the *simulation*, which gives numbers with error bars, and *Lean*, which proves
> statements about the simulator's accounting. Every Lean theorem we have is about the model's own
> invariants, never about the biology. The whole repo is public:
> <https://github.com/mak777uh/->
>
> **The rule we settled on for "what is worth formalizing"** is Joseph Tooby-Smith's criterion from this
> thread, applied strictly: formalize what can be *stated* rigorously, and *write down by name* what cannot.
> Our own list of "we do not formalize" is in the repo, with reasons:
> <https://github.com/mak777uh/-/blob/main/docs/formal-method.md>
> It includes things that would be tempting in your field too: statistics over empirical data, and any
> property of a trained network.
>
> **Three concrete things that paid off**, in decreasing order of how much I would expect them to transfer.
>
> 1. *A formal statement replaced a brute-force search.* We were about to find the "lethal cost" by running
>    dozens of simulations. But the model has a closed form: with income `i` and cost `c`, energy changes by
>    `i − c` per step, so time-to-death is exactly `E₀/(c − i)`. From that, a small theorem gives the
>    condition under which an organism can adapt before it dies — i.e. when learning can pay off at all.
>    That turned a parameter sweep into an inequality, and the inequality is what we cite now:
>    <https://github.com/mak777uh/-/blob/main/formal/Survival.lean>
>    (Adapt.lean next to it is the "can adaptation finish before death" boundary.)
>
> 2. *Order-independence is the theorem you need the moment you leave the generation model.* Our GPU and CPU
>    update cells in different orders, so we had to prove that the energy accounting does not depend on the
>    update order: <https://github.com/mak777uh/-/blob/main/formal/Order.lean>
>    Classical Wright–Fisher hides this behind synchronous generations. The moment you formalize an
>    individual-based model — where individuals update asynchronously, exactly like our cells — this is the
>    first lemma you will need, and it is the kind of thing that is silently false in hand-written proofs.
>
> 3. *Formalization surfaced a hidden assumption.* We tried to prove "the update rule preserves topology".
>    It is false: convolution plus threshold both merges components and creates holes. The only honest form
>    was `|Δχ| ≤ K`, with `K` an explicit function of the kernel. Chow's special-relativity example in this
>    thread (scale invariance has to be assumed explicitly, or you get a nonstandard theory) is the same
>    phenomenon at a different scale. In my experience this is the most *reliable* benefit of formalization:
>    not that it proves what you hoped, but that it tells you precisely what you were silently assuming.
>
> **The trap I would warn you about before any theorem.** We had one scalar — "marginal advantage" — living
> in four mutually inconsistent versions across our own documents (6.90, 8.22, 12.35, ~80), because four
> different denominators were all called by the same name. Population genetics has exactly this failure mode
> with *fitness*, *selection coefficient* and *effective population size*. We fixed it mechanically: a
> registry of definitions, where every quantity must declare its formula, its denominator and where it is
> computed, plus a CI job that recomputes each value independently from raw artifacts:
> <https://github.com/mak777uh/-/blob/main/lab/metrics.json>
> This is unglamorous and it removes an entire class of "my theorem is about a different quantity than my
> data" failures. If I were starting a formalization of population genetics, I would do this registry first
> and only then write the first theorem.
>
> **Now the honest part, and it is the part you should weigh most.** I have **no formalized result from
> population genetics**. Not Wright–Fisher, not a diffusion limit, not a fixation probability. My numbers
> about selection (a trait's rank correlation with realised cell-steps ≈ −0.37, 95 % CI [−0.40, −0.27];
> effective lineages 1.5 → 6.1 when updates are desynchronised) are simulation results with intervals, not
> theorems, and I would not dress them up as formalization. So what I can offer you is a method and a
> boundary rule, not a precedent.
>
> What *would* be a real precedent, and what I am considering doing next, is the smallest genuine fact I can
> think of: in the neutral Moran model the allele frequency is a martingale and fixation happens with
> probability 1. It needs a probability library and some patience, but it would be a *fact from your field*,
> not a methodology. If you (or anyone here) already knows a Lean-ready path to it — or thinks it is the
> wrong first target — I would genuinely like to know before I spend the time.
>
> Either way: good luck with it. My impression from this thread is that the honest state of the art is
> "formalize the accounting, not the biology", and that this is still worth doing.

---

## Что в тексте намеренно сделано

1. **Никаких заявлений о «жизни» или интеллекте** — только «unit of selection» и «модель», как требует §3
   контракта.
2. **Числа с интервалами и с оговоркой «это симуляция, не теорема»** — то есть ровно то, что мы требуем
   от себя.
3. **Честное признание в конце** — «формализованного результата из популяционной генетики у меня нет».
   Это ключевая часть: она делает предложение проверяемым, а не рекламным.
4. **Вопрос в конце, а не утверждение** — приглашение к разговору, а не поза эксперта.
5. Ссылки: 4 на файлы репозитория + корень репозитория. Все проверены на доступность без входа.
