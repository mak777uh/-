# Литература под тему — 2026-10-29

Темы: Наследие среды: полураспад и нормировка на поколение (next), Единица отбора и единица размножения (клеточное почкование) (current), Гомогенность серий: провенанс вычислений и воспроизводимость (current), Цена признака зависит от механизма: цена принадлежит каналу (current), Суррогатные данные: как проверять «сигнал против темпа» (current)

## Наследие среды: полураспад и нормировка на поколение  `legacy-half-life` (next)
где у нас: `library/conditions.md#условие-c`, `library/reviews/legacy-prior-art.md`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить единицы (шаги против поколений) и не выдаётся ли «переживание поколения» за выгоду для следующей когорты.

## Единица отбора и единица размножения (клеточное почкование)  `unit-of-selection` (current)
где у нас: `docs/world-design.md#10ao`, `library/conditions.md#условие-e`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить, совпадает ли у нас единица изменчивости с единицей размножения; иначе ρ не определён.

## Гомогенность серий: провенанс вычислений и воспроизводимость  `series-homogeneity` (current)
где у нас: `lab/homogeneity.json`, `scripts/check_series_homogeneity.py`, `library/hypotheses/reproducibility.md`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить, что для каждой цифры известен коммит кода, которым снят артефакт; иначе парное сравнение недействительно.

## Цена признака зависит от механизма: цена принадлежит каналу  `trait-cost-channel` (current)
где у нас: `docs/world-design.md#10bj`, `library/claims-evidence.md`
- не нашлось работ выше порога: отброшены артефакты, препринты дублей, нет абстракта, не прошёл доменный фильтр или релевантность < порога
**К чему обязывает:** Проверить, что 'цена' названа вместе с каналом: инвестирование против частоты обновления; иначе утверждение недоопределено.

## Суррогатные данные: как проверять «сигнал против темпа»  `surrogate-data` (current)
где у нас: `docs/world-design.md#10bm`, `library/claims-evidence.md`
- **Theiler, Prichard 2006**, Nonlinear Dynamics and Time Series — «Using "Surrogate Surrogate Data" to calibrate the actual rate of false positives in tests for nonlin»  
  DOI `10.1090/fic/011/07`; статья; релевантность 8; абстракт: (абстракт недоступен — проверить по Crossref/полю, не цитировать вслепую)…
- **Palus, Hoyer 1998**, IEEE Engineering in Medicine and Biology Magazine — «Detecting nonlinearity and phase synchronization with surrogate data»  
  DOI `10.1109/51.731319`; статья; релевантность 6; абстракт: Methods for detecting nonlinearity in univariate and multivariate time series and methods for identification of phase synchronization in bivariate time series are presented. Both techniques utilize the technique of surrogate data. The detection of nonlinearity is based on rejecting a null hypothesis…
- **Hinich, Mendes, Stone 2005**, Studies in Nonlinear Dynamics &amp; Econometrics — «Detecting Nonlinearity in Time Series: Surrogate and Bootstrap Approaches»  
  DOI `10.2202/1558-3708.1268`; статья; релевантность 7; абстракт: Detecting nonlinearity in financial time series is a key point when the main interest is to understand the generating process. One of the main tests for testing linearity in time series is the Hinich Bispectrum Nonlinearity Test (HINBIN). Although this test has been succesfully applied to a vast num…
**К чему обязывает:** Проверить, что канон суррогатных методов назван: иначе наш K3 выглядит как самодельный контроль, хотя у него есть литературная основа.

## Комментарий главному (черновик)
Сформулировать: (1) что из найденного меняет наш следующий шаг, (2) что подтверждает, но менять не надо, (3) какая оговорка обязательна в тексте. Проверка DOI и отбор — за библиотекарем.
