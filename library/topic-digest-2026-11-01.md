# Литература под тему — 2026-11-01

Темы: Единица отбора и единица размножения (клеточное почкование) (next), Цена признака зависит от механизма: цена принадлежит каналу (next), Сосуществование через скорость роста при инвазии (invasion growth rate) (next), Конечный размер и уточнение сетки: когда эффект — свойство дискретизации (current)

## Единица отбора и единица размножения (клеточное почкование)  `unit-of-selection` (next)
где у нас: `docs/world-design.md#10ao`, `library/conditions.md#условие-e`
- не нашлось работ выше порога; отброшено (артефакт: 4, старый: 3, без абстракта: 5, домен: 5, релевантность: 3, повтор: 4)
**К чему обязывает:** Проверить, совпадает ли у нас единица изменчивости с единицей размножения; иначе ρ не определён.

## Цена признака зависит от механизма: цена принадлежит каналу  `trait-cost-channel` (next)
где у нас: `docs/world-design.md#10bj`, `library/claims-evidence.md`
- не нашлось работ выше порога; отброшено (артефакт: 8, старый: 3, релевантность: 1)
**К чему обязывает:** Проверить, что 'цена' названа вместе с каналом: инвестирование против частоты обновления; иначе утверждение недоопределено.

## Сосуществование через скорость роста при инвазии (invasion growth rate)  `coexistence-grw` (next)
где у нас: `reports/2026-10-29-deeper-than-cells.md`, `library/hypotheses/alife-lineage.md#C2`, `docs/world-design.md`
- не нашлось работ выше порога; отброшено (артефакт: 3, старый: 1, без абстракта: 4, домен: 1, релевантность: 1, повтор: 2)
**К чему обязывает:** Проверить, что 'сосуществование' у нас = invasion growth rate > 0 у редкого, а не присутствие; иначе слово не заработано (E11).

## Конечный размер и уточнение сетки: когда эффект — свойство дискретизации  `finite-size-refinement` (current)
где у нас: `docs/world-design.md`, `library/claims-evidence.md`, `library/lit-elephant-fulltexts.md`
- **Xu, Puente, Stapelfeldt 2021**, AIAA Scitech 2021 Forum — «Validation of Three-Dimensional Grid Refinement for Lattice Boltzmann Methods»  
  DOI `10.2514/6.2021-2006`; статья; релевантность 6; абстракт: View Video Presentation: https://doi.org/10.2514/6.2021-2006.vid The lattice Boltzmann method (LBM) is a method for modeling fluid dynamics which is based on discrete kinetic theory. It discretizes the continuous Boltzmann equation in velocity, spatial and temporal space and solves a transport equat…
- ** 2019**, Classical Field Theory — «Classical Integrability: Continuum Limit of Discrete, Lattice, and Spin Systems»  
  DOI `10.1017/9781108569392.012`; статья; релевантность 4; абстракт: We describe the notion of integrability in classical physics and the possible existence of a Lax pair. As examples of integrable systems, we describe Toda and Calogero–Moser systems and Toda field theory. Field theories are also obtained from discrete systems – for instance, spin systems. The Heisen…
**К чему обязывает:** Проверить, что наш эффект неоднородности не артефакт 11-модовой box-модели: нужны работы по finite-size scaling и continuum limit, и правило записи трёх исходов.

## Комментарий главному (черновик)
Сформулировать: (1) что из найденного меняет наш следующий шаг, (2) что подтверждает, но менять не надо, (3) какая оговорка обязательна в тексте. Проверка DOI и отбор — за библиотекарем.
