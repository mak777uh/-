# Вопросы литературы (очередь обязательного шага)

Каждый проход дежурства берёт первый `open` и ищет по нему. Статусы: `open`, `searched-0`, `searched-1`, `done`.

| id | вопрос | статус | дата | заметка |
| --- | --- | --- | --- | --- |
| Q1 | Does niche construction pay off only above an energy-surplus threshold? | searched-1 | 2026-10-24 | P43/P44 (NC3: construction/choice/conformance); запрос через OpenAlex |
| Q2 | How is differentiable logic gate discretization validated against the discrete model? | searched-1 | 2026-10-24 | P42: Miotti 2025 (DiffLogic CA) |
| Q3 | How to separate affordance from adaptation operationally in embodied agents? | searched-0 | 2026-10-24 | литература про восприятие аффордансов (Ferretti 2021; Roessling & Fajen 2020) и роботов; операционального различения affordance/adaptation для нашей задачи нет — покрыто NC3 (P43) и action-space shaping |
| Q4 | Neutral marker fixation times in growing spatial cellular automata | searched-1 | 2026-10-24 | P45 Hallatschek 2008 (gene surfing), P46 Ferretti 2023 (время фиксации ∝ энтропии) |
| Q5 | Differential mortality versus disturbance in removing priority effects | searched-1 | 2026-10-24 | P47 Song 2020 (структура возмущения), P48 Laloux 2026 (response diversity) |
| Q6 | Measuring ecological inheritance half-life after organism removal | searched-1 | 2026-10-24 | P49 Harris & Byers 2026 (legacy vs live), P50 Grove 2015 (persistence after removal) |
| Q7 | How are negative results reported in artificial life venues and formats? | searched-1 | 2026-10-24 | отдельного ALife-трека нет; форматы: ALIFE/ArtLife, ReScience C, registered reports, workshops (audit/publishing-practice.md) |
| Q8 | Generalist versus specialist performance across heterogeneous environments | searched-1 | 2026-10-24 | P51 Hughes 2023 (генералист/специалист: 2 vs 4 среды); mapping NC3 исправлен (L2 = choice) |
| Q9 | Experiments separating "plasticity does not pay" from "plasticity assimilated" | searched-1 | 2026-10-24 | P52 Fragata 2015 (пластичность сохраняется в стабильной среде), P53 Walasek 2025 (обратимая пластичность в стабильной среде) |
| Q10 | Two-pool resource switching versus frequency dependence: distinguishing experiments | searched-0 | 2026-10-24 | различающий эксперимент конструируем сами: компоненты уже есть (P25/P26 switching, P15/P16 fd); свежих работ именно про two-pool vs fd не нашлось |
| Q11 | How is niche conformance operationalized in minimal models? | searched-1 | 2026-10-24 | P54 Riyahi 2024: conformance = изменение фенотипа на месте; P43 — определение |
| Q12 | What minimal in-silico experiments show construction benefit with a placebo control? | searched-1 | 2026-10-24 | P55 Han 2006: строительство держит полиморфизм при наследовании+пространстве; placebo-контроля в моделях нет — наш вклад |
| Q13 | How to detect bistability and bimodality in small-sample ALife runs? | searched-1 | 2026-10-24 | P56 Hartigan 1985 (dip test), P57 Silverman 1981 (kernel modes); при 3–5 сидах тест не применять |
| Q14 | How do ALife papers justify generalisation across substrates? | searched-1 | 2026-10-24 | P58 Aguilar 2014: ALife как общая биология, но кросс-субстратных тестов мало — W2 закрывает пробел |

| Q15 | How is lineage inheritance implemented in digital organisms (tags, genomes)? | open | — | task-11: тип на уровне линии |
| Q16 | What are minimal criteria for a unit of selection in digital systems? | open | — | I-020: деление/смерть как условие отбора |
| Q17 | How to measure robustness vs performance trade-offs in ALife? | open | — | B2: 1/3 коллапсов vs медиана |
| Q18 | What counts as a pre-registered ALife experiment? | open | — | наш §3a и registered reports |

## Как пополнять

- Вопрос формулируем на английском (научные термины), в таблицу можно по-русски.
- Один вопрос = 1–2 запроса; если ничего не подошло — `searched-0` с пояснением.
- Взяли работу — заводим запись в `hypotheses/` и `searched-1` со ссылкой на P-номер.
