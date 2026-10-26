# Литература под тему — 2026-10-26

Темы: Инвазия: укоренение редкой линии в занятом поле (current), Наследие среды: полураспад и нормировка на поколение (current), Возможность отбора: I Кроу и нуль-модели (current), Единица отбора и единица размножения (клеточное почкование) (next), Частичная информация: измерение выигрыша при шуме и задержке (next)

## Инвазия: укоренение редкой линии в занятом поле  `invasion-establishment` (current)
где у нас: `docs/world-design.md#10at`, `docs/world-design.md#10at.4`, `reports/2026-10-25-invasion-patches-plan.md`
- **MacDonald, Leroux, Purchase 2024**, Ecosphere — «Landscape, demographic, and dispersal parameters influence the spread and establishment of an aquati»  
  DOI `10.1002/ecs2.4967`; статья; релевантность 4; абстракт: Abstract Human‐mediated species introductions are contributing to the biotic homogenization of global flora and fauna. Despite extensive research, we lack simple methods of predicting how and where an introduced species will spread and establish, particularly in species with complex life histories i…
**К чему обязывает:** Проверить, разделены ли у нас «появление», «укоренение» и «распространение», и не смешаны ли они в одном числе выживания.

## Наследие среды: полураспад и нормировка на поколение  `legacy-half-life` (current)
где у нас: `library/conditions.md#условие-c`, `library/reviews/legacy-prior-art.md`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить единицы (шаги против поколений) и не выдаётся ли «переживание поколения» за выгоду для следующей когорты.

## Возможность отбора: I Кроу и нуль-модели  `selection-opportunity` (current)
где у нас: `docs/world-design.md#10aq`, `library/reviews/w8-metrics-canon.md`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить, что критерий — I_obs > I_null(95%), и что знаменатель/df/ddof зафиксированы до прогона.

## Единица отбора и единица размножения (клеточное почкование)  `unit-of-selection` (next)
где у нас: `docs/world-design.md#10ao`, `library/conditions.md#условие-e`
- **Ackermann, Osmond 2023**,  — «The role of the unicellular bottleneck and organism size in mediating cooperation and conflict among»  
  DOI `10.1101/2023.07.17.549265`; препринт; релевантность 4; абстракт: Abstract Evolutionary transitions in individuality introduce new levels of selection and thus enable discordant selection, threatening the stability of the transition. Cheating is such a problem for multicellularity. So why have so many transitions to multicellularity persisted? One possibility is t…
**К чему обязывает:** Проверить, совпадает ли у нас единица изменчивости с единицей размножения; иначе ρ не определён.

## Частичная информация: измерение выигрыша при шуме и задержке  `partial-information` (next)
где у нас: `library/conditions.md#досье-a`, `library/reviews/w12-partial-info-canon.md`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить, есть ли контроль «та же статистика действий без информации» (yoked), иначе выигрыш неотличим от везения.

## Комментарий главному (черновик)
Сформулировать: (1) что из найденного меняет наш следующий шаг, (2) что подтверждает, но менять не надо, (3) какая оговорка обязательна в тексте. Проверка DOI и отбор — за библиотекарем.
