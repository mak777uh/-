# Лог поиска публикаций

Каждая строка — запрос и что из него вышло. Нужен, чтобы не искать одно и то же дважды
и чтобы «обзор» был видимым, а не обещанным.

| дата | запрос | кандидатов | взято | куда |
| --- | --- | --- | --- | --- |
| 2026-10-24 | negative frequency-dependent selection recognition | 6 | 2 | P35, P36 |
| 2026-10-24 | differentiable cellular automata gradient | 6 | 1 | tools-survey (PyTorchFire) |
| 2026-10-24 | switching prey choice stability | 8 | 0 | не подошли (частотные модели, не switching) |
| 2026-10-24 | priority effects coexistence theory | 8 | 0 | уже был P20/P31 |
| 2026-10-24 | intermediate disturbance hypothesis test | 8 | 1 | P34 (Blanchette & Menge) |
| 2026-10-24 | neutral theory microbial community drift | 8 | 1 | P33 (Morrow) |
| 2026-10-24 | meta-learning generalization new tasks | 8 | 0 | не подошли (частные приложения) |
| 2026-10-24 | resource pulses consumers dynamics | 8 | 1 | P27 (Ostfeld & Keesing) |

## Как вести

- Один проход = 1–2 запроса по открытым пунктам доски/answers/пула.
- Кандидатов берём только с `type:journal-article` и годом ≥ 2023 (старое — через обычную запись).
- Авторов и год — **только из Crossref**, не по памяти (уже ошибались дважды).
- Взяли 1–2 — запись в `pond-lineage.md` (раздел H) или `tools-survey.md`, строка сюда.
- Не взяли — тоже строка: чтобы через неделю не искать то же.
