# Литература под тему — 2026-11-03

Темы: Единица отбора и единица размножения (клеточное почкование) (next), Цена признака зависит от механизма: цена принадлежит каналу (next), Сосуществование через скорость роста при инвазии (invasion growth rate) (next), Конечный размер и уточнение сетки: когда эффект — свойство дискретизации (next), Память среды: величина против формы, предпочитаемый масштаб, симметрия (next), Мощность и число прогонов: когда 10 миров занижают контраст, а 30 разрешают (current)

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

## Конечный размер и уточнение сетки: когда эффект — свойство дискретизации  `finite-size-refinement` (next)
где у нас: `docs/world-design.md`, `library/claims-evidence.md`, `library/lit-elephant-fulltexts.md`
- не нашлось работ выше порога; отброшено (старый: 11, без абстракта: 2, домен: 3, повтор: 2)
**К чему обязывает:** Проверить, что наш эффект неоднородности не артефакт 11-модовой box-модели: нужны работы по finite-size scaling и continuum limit, и правило записи трёх исходов.

## Память среды: величина против формы, предпочитаемый масштаб, симметрия  `medium-memory-scales` (next)
где у нас: `docs/world-design.md`, `library/lit-elephant-fulltexts.md`, `reports/`
- **, Reichl None**,  — «Symmetry Breaking and Pattern Selection in Models of Visual Development»  
  DOI `10.53846/goediss-2930`; статья; релевантность 5; абстракт: Response properties of neurons in the visual cortex form spatial representations called maps of several stimulus features such as orientation preference (OP) or ocular dominance (OD). This thesis studies macroscopic models for the development of such visual cortical maps described by the time evolut…
**К чему обязывает:** Проверить, есть ли в литературе различение «среда хранит величину, а не форму» и зависимость памяти от числа предпочитаемых масштабов — иначе это наша формулировка без основания.

## Мощность и число прогонов: когда 10 миров занижают контраст, а 30 разрешают  `power-and-replicates` (current)
где у нас: `docs/world-design.md`, `library/reviews/igr-methods.md`
- **Zweifach 2025**,  — «Bonferroni’s correction, not Tukey’s, should be used to control the total number of false positives »  
  DOI `10.1101/2025.05.01.651705`; препринт; релевантность 4; абстракт: Statistical tests can be used to help determine whether experimental manipulations produce effects. In tests of means, when more than two groups are compared the total number of Type 1 errors (false positive results) increases unless a correction is used. Tukey's method is thought to offer good cont…
**К чему обязывает:** Проверить канон: сколько прогонов нужно, чтобы контраст разрешался, и как отличать псевдорепликацию (один мир, много сидов) от настоящих миров — прямо к X132.

## Комментарий главному (черновик)
Сформулировать: (1) что из найденного меняет наш следующий шаг, (2) что подтверждает, но менять не надо, (3) какая оговорка обязательна в тексте. Проверка DOI и отбор — за библиотекарем.
