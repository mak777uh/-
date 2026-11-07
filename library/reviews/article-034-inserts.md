# Готовые вставки для 034 (08.11.2026)

По запросу главного: 034 в нынешнем виде **не подавать** (ноль ссылок, таксономия «где/когда/что» не наша).
Здесь — **готовый текст**, который можно вписать без переписывания статьи.

## Вставка 1 — список литературы (в конец, перед «Authorship and automation»)

```
## References

[1] Trapanese, G., Meunier, H., Masi, S. (2018). What, where and when: spatial foraging decisions in primates.
    *Biological Reviews* 94(2). DOI: 10.1111/brv.12462.
[2] Mathew, S., Sasidevan, V. (2019). Food Income and the Evolution of Forager Mobility.
    *Scientific Reports* 9: s41598-019-42006-2. DOI: 10.1038/s41598-019-42006-2.
```

## Вставка 2 — абзац в §1 (Design), сразу после «Keywords»

```
**The three classes of signal are not ours.** Distinguishing a signal that tells an animal *what* is available,
*where* it is and *when* it is there is the standard decomposition of spatial foraging research, reviewed for
primates by Trapanese, Meunier and Masi (2018) [1]. What this article adds is not the taxonomy but a
**comparison of their strength** in one world where the cell cannot move, and the finding that the class of the
signal, not its accuracy, sets the size of the gain.
```

## Вставка 3 — абзац в §3 (Why), первым

```
**What this explanation is and is not.** It is a consequence of the design, not a mechanism derived from it: an
immobile cell has no way to act on a map, so the only lever a signal can pull is the cell's own terms. The
measured ordering (rules +0.0512 > place +0.0117 > time +0.0080) is what that design predicts, and the design
is the reason the ordering is not a discovery about signals in general. The cost–benefit frame in which the
value of information is weighed against the cost of acting on it is that of Mathew and Sasidevan (2019) [2];
what is ours is the comparison inside that frame.
```

## Вставка 4 — оговорка в §4 (What this does not show), первым пунктом

```
- It does not show that the trait or the signal is **sustained**: in every arm the heritable quantity falls to
  0.08–0.14 of its starting value, and **none of the twenty seeds** holds it above 0.5 in any arm. "The rule
  signal pays" therefore means "the decline is slower", not "the signal is retained". This is the same
  limitation recorded for the earlier signal experiments.
```

## Вставка 5 — замена названия §3

`## 3. Why` → `## 3. Why this ordering follows from the design`

Причина: §3 объясняет **следствие конструкции** (клетка не двигается ⇒ карта бесполезна), а не механизм.
Название «Why» обещает механизм, которого статья сама не даёт (§4 это признаёт).

## Что НЕ трогать

- **числа** — воспроизвёл по агрегату `s89_e14b_20seeds.json`: rule 0.1445, none 0.0933, Δ +0.0512, 18/20 ✅;
- **ссылку на 033** — она теперь опубликована (v3.0), но **проверить номер версии** перед подачей: если 033
  ещё не в депозите, заменить «article 033» на «the previous article of this series (in preparation)».

## Проверка после вставки

`python scripts/check_article_034_numbers.py` — числа не должны измениться (вставки текстовые).
