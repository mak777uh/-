# Рецензия на черновик arXiv (`_hourly/grants/arxiv-draft-EN.md`, v0.1, 3465 слов)

Проверял по своим правилам: числа — из агрегатов, ссылки — по Crossref, утверждения — против
`CLAIMS.md` §4j и `docs/world-design.md` §10ay. Ниже: что блокирует отправку, что поправить, что
подтверждаю.

## Вердикт

**Структура и тон — годные.** Четыре условия, каждое с критерием до данных, контролем и границей;
раздел «Truth versus strength» — сильнейший; ограничения названы честно. **Но есть одно утверждение,
которое сейчас сильнее данных**, и одна ссылка с неверным названием. До их исправления отправлять
нельзя: это ровно те дефекты, которые мы сами ловим у других.

## 1. Блокирует отправку

### 1.1. Абстракт и §4.4: «остаток исчез» — это больше не вердикт

**В черновике** (Abstract и §4.4): «0.862 vs 0.841 under an exact-neighbour control, 3 seeds»;
«the remainder disappears (1 seed of 3)».

**Данные сейчас** (`5ab192e`, docs §10ay, серия на **10** сидах): `legacy > adjacency_exact` в **5 из 9
пригодных**, медиана разницы **+0.014**, `legacy` 0.860 против `adjacency_exact` 0.847, знаковый тест
**p = 0.38**, порог пре-регистрации **≥ 7/10 не достигнут** → вердикт «специфики точки смерти нет»
**не заявляется**.

**Почему это критично именно для arXiv:** «остаток исчез» — утверждение об отсутствии эффекта. По
нашим же правилам (§3.3 п. 4) серия, которая не дотянулась до порога, отчитывается как **«на границе»**,
а не как отсутствие. Рецензент поймает это первым: в §6 Limitations у вас написано «we therefore write
"agrees with", not "proved"» — и тут же в абстракте «disappears».

**Замена (предлагаю дословно):**
> Environmental inheritance does not exist: the apparent advantage of a dying cell's
> neighbourhood is explained by the number of living neighbours (0.862 → 0.847 once the
> neighbour count is matched, i.e. the remainder falls from +0.12 to +0.014); the exact-control
> criterion (≥7/10 seeds) was not met (5/9, p = 0.38), so we do not claim that the death site
> carries no specificity at all.

И в §4.4 таблицу — строкой «exactly the same neighbour count | 0.847 vs 0.860 | remainder falls from
+0.12 to +0.014; criterion not met (5/9, p = 0.38)».

### 1.2. Абстракт: «persists in 7–10 runs out of 10» смешивает две раскладки

Диапазон склеивает uniform (**7/10**) и patches (**10/10**). В §4.3 таблица честная, в абстракте —
неоднозначность. Заменить на «7/10 (free gaps) and 10/10 (dense patches)».

## 2. Ссылки: проверено по Crossref

| черновик | что есть на самом деле |
|---|---|
| Waples 2020, *Evolution* (verify volume/pages) | **Evolution 74(9): 1942–1953**, DOI `10.1111/evo.14061` ✓ название верное |
| Waples & Reed 2023, «Nonequilibrium evolution of population size and opportunity for selection» | **название неверное**. Верно: «**Null Models for the Opportunity for Selection**», *The American Naturalist* **201(6): 779–793**, DOI `10.1086/723889` |
| Crow 1958, Human Biology 30(1):1–13 | верно; DOI в Crossref нет — так и оставить, без DOI |
| Bedau 2000, Langton 1989, Szathmáry & Smith 1995, Fontana & Buss 1994, Lenski 2003, Yaeger 1994, Maturana & Varela 1980, Kauffman 1993, Prigogine & Nicolis 1977 | выглядят верно; у старых книг DOI нет — ок |

**Стоит добавить** (прямо поддерживает нашу осторожность с I):
Reed, Visser & Waples 2022, «The opportunity for selection: A slippery concept in ecology and
evolution», *J. Anim. Ecol.*, DOI `10.1111/1365-2656.13841`.

**Zenodo-ссылки проверил — резолвятся все три:** `10.5281/zenodo.23648667` (6 файлов),
концепт `10.5281/zenodo.23571609`, чекпоинты `10.5281/zenodo.23654174` (18 файлов).

## 3. Числа: что подтверждаю (и одно место с третьим знаком)

| утверждение черновика | агрегат | итог |
|---|---|---|
| 0.5614 / 0.0621 / 12.16 / 10/10 | `w2bud_matrix` | ✓ |
| colony 0/10 | W1-контроль | ✓ |
| репликация 9/10 и 10/10, отношения 14.23 и 9.47 | `w2bud_rep_uniform/patches` | ✓ (в uniform один сид без данных — потому 9/10) |
| one bud: 7.5 / 8/10 / −0.478 | `w2bud_onebud_matrix` | ✓ |
| `N=3`: 6.5 / 10/10 / −0.219 и 4.0 / 4/10 / −0.690 | `w2budd2_matrix`, `w2budd2_rep_matrix` | ✓ |
| uniform 7/10 и 0/10; patches 10/10 и 0/10; доза 5: 2/10 | placement/mergekeep (n = 10) | ✓ |
| legacy 0.858, foreign 0.844 | `w1niche5_legacy` 0.860; `w1niche4_foreign` **0.844** | ✓ (в третьем знаке) |
| density 0.704 vs 0.710 | `density_matched` 0.712 / `prepared` 0.711 | Δ 0.008 — **указать подвыборку** |
| «time to disappearance 4–9 steps, exactly the period» | период 5 шагов | лучше «one period (5 steps), observed 4–9» |
| environmental memory 1.3–2.4 generations | `generation_length` 9–10 | ✓ |

**Важно про «9/10»:** в `w2bud_rep_uniform` один сид не имеет ≥2 линий с данными, поэтому 9/10 — это
не «провал», а «исключён». В тексте лучше: «9 of 10 usable seeds (one excluded for insufficient
lineages)».

## 4. Структура: что советую

1. **§5 оставить отдельным разделом.** Это самый цитируемый кусок и главный тезис («исход решает
   правило и размер, а не качество»). Но название «Truth versus strength» звучит как философское
   заявление; безопаснее: «**5. The outcome is set by the rule and by size, not by quality**» — и
   первая же фраза с числом.
2. **«Organisation» определить операционально, одним предложением.** Рецензент спросит первым. Вариант:
   «organisation — коллектив, чьи компоненты заменяются быстрее, чем распадается сам коллектив»
   (проверяемо через `generation_length` против времени потери доли).
3. **Добавить таблицу «пре-регистрированный порог → исход»** по четырём условиям (у нас она уже есть в
   `library/claims-evidence.md`): это сильнейший аргумент методологической части и снимает половину
   вопросов рецензента.
4. **Figures:** спец 1–3 готовы по данным. **Спец 4 надо менять**: «occupancy vs neighbours with
   exact-neighbour control» — после исправления это не «коллапс», а распределение разниц с линией
   порога ≥7/10; иначе фигура будет утверждать больше текста.
5. **§6 Limitations** пункт 5 («one exact control has three seeds») обновить: теперь **10 сидов, 9
   пригодных**, и вывод «не дотянулись до порога» — это сильнее и честнее, чем «три сида».

## 5. Ответы на ваш чек-лист

1. **Числа** — сверил все, кроме §4.5 (там только диапазон поколений, совпадает). Блокирует только
   §1.1 (остаток) и §1.2 (7–10 в абстракте).
2. **Ссылки** — Waples 2023 с неверным названием, Waples 2020 теперь с полными данными; см. §2 выше.
   Рекомендую добавить Reed–Visser–Waples 2022.
3. **§5** — оставить разделом, переименовать.
4. **Фигуры** — 1–3 по спекам, 4 переделать под «на границе».
5. **CLAIMS §4j** — сверено: **в текущем виде абстракт сильнее §4j** ровно в пункте про остаток
   (в §4j: «сокращается с +0.12 до +0.014 … и не заявляется как отсутствующая»). После замены из §1.1
   черновик будет соответствовать.

## 6. Что понравилось (чтобы не потерять при правках)

- «Each condition is stated as a pre-registered criterion and compared against a null model, **not
  against zero**» — это лучшая фраза черновика, оставить в абстракте.
- §3.3 правила доказательности — редкая вещь в ALife-статьях.
- §6 п. 3 (история с `rho_partial`) — честно и повышает доверие, не понижает.
