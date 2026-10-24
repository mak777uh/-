# Вопросы литературы (очередь обязательного шага)

Каждый проход дежурства берёт первый `open` и ищет по нему. Статусы: `open`, `searched-0`, `searched-1`, `done`.

| id | вопрос | статус | дата | заметка |
| --- | --- | --- | --- | --- |
| Q1 | Does niche construction pay off only above an energy-surplus threshold? | searched-1 | 2026-10-24 | P43/P44 (NC3: construction/choice/conformance); запрос через OpenAlex |
| Q2 | How is differentiable logic gate discretization validated against the discrete model? | searched-1 | 2026-10-24 | P42: Miotti 2025 (DiffLogic CA) |
| Q3 | How to separate affordance from adaptation operationally in embodied agents? | searched-0 | 2026-10-24 | литература про восприятие аффордансов (Ferretti 2021; Roessling & Fajen 2020) и роботов; операционального различения affordance/adaptation для нашей задачи нет — покрыто NC3 (P43) и action-space shaping |
| Q4 | Neutral marker fixation times in growing spatial cellular automata | searched-1 | 2026-10-24 | P45 Hallatschek 2008 (gene surfing), P46 Ferretti 2023 (время фиксации ∝ энтропии) |
| Q5 | Differential mortality versus disturbance in removing priority effects | searched-1 | 2026-10-24 | P47 Song 2020 (структура возмущения), P48 Laloux 2026 (response diversity) |
| Q6 | Measuring ecological inheritance half-life after organism removal | open | — | три метрики нишевого конструирования |
| Q7 | How are negative results reported in artificial life venues and formats? | open | — | C-путь развилки |
| Q8 | Generalist versus specialist performance across heterogeneous environments | open | — | L0-генералист (B-025/H56) |
| Q9 | Experiments separating "plasticity does not pay" from "plasticity assimilated" | open | — | Baldwin/ассимиляция (Baldwin 1896; Crispo 2007) |
| Q10 | Two-pool resource switching versus frequency dependence: distinguishing experiments | open | — | switching vs fd (H54) |

## Как пополнять

- Вопрос формулируем на английском (научные термины), в таблицу можно по-русски.
- Один вопрос = 1–2 запроса; если ничего не подошло — `searched-0` с пояснением.
- Взяли работу — заводим запись в `hypotheses/` и `searched-1` со ссылкой на P-номер.
