# Переходы из данных: журнал (append-only)

Каждый `result_scan` с `переходов > 0` оставляет здесь строку: что за переход, и **что с ним сделано** —
мини-обзор (`library/reviews/transition-*.md`) или строка «не влияет, потому что …».

Формат строки (одна строка на переход, поля через ` | `):

`ДАТА | claim/плечо | вид перехода | статус (review:<файл> / не влияет: <причина> / pending)`

Проверка: `python library/tools/transition_gate.py` — краснеет, если есть `pending`.

---

2026-11-03 | X145 lone radius-3 disc split clock | опровергнут простой механизм гонки (§10hh) | review:library/reviews/transition-x145.md
2026-11-03 | X142 gap rule for whole coalescence curve | подтверждение правила на всей кривой | не влияет: уточняет уже записанное правило, новых утверждений не вводит
2026-11-03 | X138 mixing length = surface gap of nine cells | новый замер (масштаб), не смена вывода | не влияет: масштабная величина, выводы §10hc не меняет
2026-11-04 | X166 contact band real, 'same at every size' withdrawn | отозвано утверждение о постоянстве зазора | review:library/reviews/transition-x166.md
2026-11-04 | X160 mortality buffer does not hold diversity | третье независимое отрицание по storage effect | не влияет: подтверждает уже записанное (E12/E12b), новых утверждений не вводит
2026-11-04 | X171-X176 corridor per-contact fraction: narrowed to band 0.37-0.52 with two inputs | сужение утверждения: один фактор оказался смесью двух | review:library/reviews/transition-x171-x176.md
2026-11-04 | X161 nothing discrete crosses a division | новое отрицание (нет ratchet по линии) | не влияет: отрицание уже поддержано нулями перестановок, мини-обзор не требуется
2026-11-05 | gradpos sanity (e00d1eb0c): regression vs B1/B1b, tumble-like 0.594 CI 0.491 | регрессия кода/метрики, не смена научного вывода | ЗАКРЫТО 06.11: bisect (ba44f365a) показал не регрессию кода, а зависимость от бэкенда — см. library/reviews/transition-s4-backend.md
2026-11-06 | S4 bisect: B1/B1b 'stable gradpos' not CPU-verified, plastic runs backend-dependent | смена типа свидетельства: аппаратно-зависимый результат | review:library/reviews/transition-s4-backend.md
2026-11-06 | G4/G6/G7 (d99cc1696): 'adaptation trap' is a trap of inaction | смена вывода: фиксированная норма не лечит, платит подвижность | review:library/reviews/transition-g7-inaction.md
2026-11-07 | E3 niche construction (5e8a4da91 -> a97af411e): 0.734 artefact, NULL with free-rider mechanism | отзыв сильного положительного в тот же день | review:library/reviews/transition-e3-niche.md
2026-11-07 | E1 report: 'agrees with Liang & Brinkman 2022 (~20%)' withdrawn (99bb5fb5c) | отозвано сравнение величин с разными определениями | не влияет: отзыв сделан по моей находке, новых утверждений не вводит — записано в library/search-log.md (07.11 09:15)
2026-11-07 | E7g-E7h: 'no selection in rich zone' REFUTED, strength not presence (b21519c8c) | смена объяснения при сохранении факта | не влияет: рамка 'среда задаёт силу отбора' есть в библиотеке (Lande & Arnold 1983, B-059) — записано в notices 10:10
2026-11-07 | E8f-E8g (9338d9e51): 1-seed signal result failed at 10 seeds | третье неподтверждение на 10 сидах за день | не влияет: правило '10 сидов' подтверждено трижды, механизм (близость важнее сигнала) записан в review

2026-11-07 | E10 (057627221): predictive vs coinciding signal, +0.013, 8/10 | первый воспроизведённый результат о сигналах — но числа не сходятся | review:library/reviews/transition-e10-signal.md
2026-11-07 | E14b+E15 (aebdc9266): rule-signal strongest, no selection without cost | подтверждение + расхождение в деталях E15 | review:library/reviews/transition-e14b-e15.md
2026-11-08 | closure_probe.json: 5 сценариев, caught 5, recovered 5, holes 0 | новый артефакт (new_mode), не смена утверждения | не влияет: артефакт подтверждает заявленное в 036 (closure измерена), но гейт чисел краснеет из-за дефекта пробы на Windows — записано в notices 09:35
2026-11-08 | E19 (ee0f98a7c): prediction 'record kills' not confirmed, -0.05 = 0.32 SE | пре-регистрированное предсказание не подтвердилось, правило интерпретации сработало | review:library/reviews/transition-e19.md
