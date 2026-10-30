# Литература под тему — 2026-10-30

Темы: Единица отбора и единица размножения (клеточное почкование) (current), Гомогенность серий: провенанс вычислений и воспроизводимость (next), Цена признака зависит от механизма: цена принадлежит каналу (next), Сосуществование через скорость роста при инвазии (invasion growth rate) (current)

## Единица отбора и единица размножения (клеточное почкование)  `unit-of-selection` (current)
где у нас: `docs/world-design.md#10ao`, `library/conditions.md#условие-e`
- не нашлось работ выше порога; отброшено (артефакт: 4, старый: 3, без абстракта: 5, домен: 5, релевантность: 3, повтор: 4)
**К чему обязывает:** Проверить, совпадает ли у нас единица изменчивости с единицей размножения; иначе ρ не определён.

## Гомогенность серий: провенанс вычислений и воспроизводимость  `series-homogeneity` (next)
где у нас: `lab/homogeneity.json`, `scripts/check_series_homogeneity.py`, `library/hypotheses/reproducibility.md`
- не нашлось работ выше порога; отброшено (без абстракта: 3, релевантность: 8, повтор: 1)
**К чему обязывает:** Проверить, что для каждой цифры известен коммит кода, которым снят артефакт; иначе парное сравнение недействительно.

## Цена признака зависит от механизма: цена принадлежит каналу  `trait-cost-channel` (next)
где у нас: `docs/world-design.md#10bj`, `library/claims-evidence.md`
- не нашлось работ выше порога; отброшено (артефакт: 8, старый: 3, релевантность: 1)
**К чему обязывает:** Проверить, что 'цена' названа вместе с каналом: инвестирование против частоты обновления; иначе утверждение недоопределено.

## Сосуществование через скорость роста при инвазии (invasion growth rate)  `coexistence-grw` (current)
где у нас: `reports/2026-10-29-deeper-than-cells.md`, `library/hypotheses/alife-lineage.md#C2`, `docs/world-design.md`
- **Schreiber 2025**, Journal of Mathematical Biology — «Coexistence and extinction in flow-kick systems: An invasion growth rate approach»  
  DOI `10.1007/s00285-025-02283-0`; статья; релевантность 7; абстракт: Natural populations experience a complex interplay of continuous and discrete processes: continuous growth and interactions are punctuated by discrete reproduction events, dispersal, and external disturbances. These dynamics can be modeled by impulsive or flow-kick systems, where continuous flows al…
**К чему обязывает:** Проверить, что 'сосуществование' у нас = invasion growth rate > 0 у редкого, а не присутствие; иначе слово не заработано (E11).

## Комментарий главному (черновик)
Сформулировать: (1) что из найденного меняет наш следующий шаг, (2) что подтверждает, но менять не надо, (3) какая оговорка обязательна в тексте. Проверка DOI и отбор — за библиотекарем.
