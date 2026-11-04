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
