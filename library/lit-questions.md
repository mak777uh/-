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
| Q10 | Two-pool resource switching versus frequency dependence: distinguishing experiments | open | — | switching vs fd (H54) |

## Как пополнять

- Вопрос формулируем на английском (научные термины), в таблицу можно по-русски.
- Один вопрос = 1–2 запроса; если ничего не подошло — `searched-0` с пояснением.
- Взяли работу — заводим запись в `hypotheses/` и `searched-1` со ссылкой на P-номер.
