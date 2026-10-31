# Plan of the line: index

This file is the **index** of the working plan. The plan itself lives in [`plan/`](plan/), split by identifier
range so that it can be read, reviewed and edited without opening eight thousand lines.

Why it is split: on 31.10 this file reached **8080 lines and 102 sections** and stopped being readable. The
sections were not rewritten, only moved; each one keeps its identifier, so every reference of the form
«§10dc» still resolves through the table below.

## Where the sections live

| file | covers | what is inside |
| --- | --- | --- |
| [`plan/00-pond-specification.md`](plan/00-pond-specification.md) | specification (1870 lines) | the pond world: what the medium is, why designed so, which alternatives were rejected |
| [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) | §10aa–§10az (26) | Pond: how organisation and a line appeared (24–25.10, §10aa–§10az) |
| [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) | §10ba–§10bz (26) | Pond: selection, the price of a trait, coexistence (25–28.10, §10ba–§10bz) |
| [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) | §10ca–§10cz (26) | Field: heterogeneity of inflow and its dose (30.10, §10ca–§10cz) |
| [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) | §10da–§10dl (12) | Field: what the counter measures, lifetime, percolation, form (30–31.10, §10da–§10dl) |
| [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) | §10dm–§10du (9) | Habitability, the self-model, channels and memory (31.10, §10dm–§10du) |

## Full table: section → file

| id | title | file |
| --- | --- | --- |
| §10aa | A-gate: мягкий суррогат пруда не воспроизводит hard (24.10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ab | Тип у колонии: редкая линия не удерживается (24.10, task-11 / H-ALIVE-10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ac | Доза основателя: линию убивает правило слияния и размещение, а не размер (24.10, B-037/H73) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ad | Условие B: новизна появляется — измеримо выше m = 0.05 (24.10, H-ALIVE-20) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ae | Размещение и слияние: линия не удерживается даже с форой (24.10, H-ALIVE-21 / V8) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10af | Порог основания: одна клетка основывает колонию (24.10, H-ALIVE-23 / V10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ag | Условие E: серия остановлена как невалидная по конструкции (25.10, H-ALIVE-24) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ah | Достаточность условия C: тест не чувствителен, наследие не проверено (24.10, H-ALIVE-25 / V12) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ai | Слияние «без переписывания»: направление есть, мощность мала (25.10, H-ALIVE-28) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10aj | Логгер родословной: бухгалтерия исправлена, картина не изменилась (25.10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ak | Ресурс в трёх зонах на шаге инвазии: три сида, и вывод изменился (25.10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10am | H-ALIVE-29: «богатое поле» через приток не создаётся — стоп до серии (25.10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10an | Контроль `freq_dep = 0`: поле в 42 раза богаче, инвайдер всё равно гибнет (25.10) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ao | W2-bud: линия стала единицей отбора, но отбор ещё не измерим (25.10, H-ALIVE-30) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ap | W2-bud v2: структура устойчива, гейт манипуляции не пройден (25.10, H-ALIVE-31) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10aq | W2-bud v3: структура выше нуля, цена признака видна, отклик не заявлен (25.10, H-ALIVE-32) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ar | Контроль на энергию: «бедность» отвергнута, «цена» при контроле не подтверждена (25.10, H-ALIVE-33) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10as | W2-bud v4: метрика по времени меняет знак энергии; серия невалидна по данным (25.10, H-ALIVE-34) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10at | V1b: подсадка не встаёт в 60 % прогонов — отказ постановки, а не режим гибели (25.10, H-ALIVE-35) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10au | Инвариантность к устройству метрики: S и знак C держатся во всех 18 вариантах (25.10, H-ALIVE-39) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10au-b | W2-bud-d2: до N бутонов на компоненту — цена и отклик впервые стали вердиктом (26.10, H-ALIVE-36) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10av | Воспроизведение на новых сидах: направление держится, величина — не свойство выборки (26.10, H-ALIVE-40) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10aw | Репликация `W2-bud-d2`: механизм воспроизвёлся, вердикт по цене — нет (26.10, H-ALIVE-44) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ax | `--one-bud-per-lineage`: шестая конструкция дотянулась — цена стала вердиктом (26.10, H-ALIVE-45) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ay | Наследование среды в `W1`: эффект есть, но он не про родство, не про плотность и лишь частично про соседство (26.10, H-ALIVE-46) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10az | Третья единица размножения — бутон-пара: не промежуточная, а колониальная (26.10, H-ALIVE-48) | [`plan/10a-pond-organization.md`](plan/10a-pond-organization.md) |
| §10ba | Проверка механизма пары: родство внутри единицы ни при чём — решает размер (26.10, H-ALIVE-49) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bb | Мир без тела (`R1`): направление переносится, величина — нет (26.10, H-ALIVE-50) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bc | Ограничение роста в `R1`: объяснение «геометрия усиливает отбор» НЕ подтвердилось (26.10, H-ALIVE-51) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bd | Цена признака: конструкция `W2-bud` не даёт нужного числа линий (26.10, EXPLORATORY) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10be | Наследование среды вне плотной зоны: остаток исчезает — ноль при чистых параметрах (26.10/27.10, H-ALIVE-52) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bf | Квота на долю мира: рычаг не работает и меняет знак цены (27.10, H-ALIVE-53) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bg | Вердикт по величине цены статистикой: критерий не выполнен при 20 прогонах (27.10, H-ALIVE-53/п.2) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bh | Kill-the-winner: первый механизм, который даёт линии, не ломая знак цены (27.10, H-ALIVE-54) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bi | Подтверждающая серия: величина цены −0.37, но порог 0.3 не установлен (28.10, H-ALIVE-55) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bj | Цена принадлежит каналу: признак через обновление не имеет цены (28.10, H-ALIVE-56) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bk | Асинхронность обновления — самостоятельный механизм сосуществования (28.10, H-ALIVE-57) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bl | Асинхронность и смертность усиливают друг друга, а не насыщаются (28.10, H-ALIVE-58) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bm | Живой вход из мира: канал важнее факта связи (28.10, H-ALIVE-59/60) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bn | Горизонт 1800 шагов: плато есть, но у трёх режимов оно на трёх уровнях (28–29.10, H-ALIVE-60) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bo | K3: живой вход через ритм — это СРЕДНИЙ ТЕМП, а не временная структура (29.10) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bp | K2: инвазионный пилот — сигнала нет, дизайн не разрешает вопрос (29.10) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bq | Инвазия с равными когортами: преимущества у редкой линии нет (29.10, K2b) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10br | «Светить в площадку»: жизнь не притягивается (29.10, H-ALIVE-73A/74) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bs | Критерий индивидуации: пятна поля проходят, колонии пруда — нет (29.10, E1) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bt | Абляция объекта: главный вывод переживает смену носителя (29.10, E2) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bu | Гистерезис: состояние достаточно, история на макроуровне не видна (29.10, E3) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bv | Градиент чувствительности: связь меняет путь, а не пункт назначения (29.10, E4) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bw | Наследование в поле: пассивная примесь не наследуется (29.10, E6b) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bx | Отслеживание компонент: наследование есть, отбора нет (30.10, E6c) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10by | Отбор в поле через выживание: работает и ведёт к фиксации (30.10, E6d) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10bz | Частотная зависимость: фиксация остановлена (30.10, E6e) | [`plan/10b-pond-selection.md`](plan/10b-pond-selection.md) |
| §10ca | Неоднородность среды против дрожащей неоднородности (30.10, E7) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cb | Доза неоднородности: максимум около amp = 0.5 (30.10, E8) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cc | Масштаб зерна: медленная смена узора лучше застывшего (30.10, E9) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cd | Медленная огибающая: сигнал восстанавливает разнообразие, но не превосходит статику (30.10, E10) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10ce | Пересчёт всей линии устойчивой метрикой: что выжило, что отменяется (30.10) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cf | Прибор для «скорости роста редкого»: первая попытка негодна (30.10, E11) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cg | Буфер «кто был, тот и выигрывает» уничтожает сосуществование (30.10, E12) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10ch | Число компонент измеряет заполнение, а не разнообразие (30.10, E12c → пересмотр линии) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10ci | Цвет шума: при трёх сидах различия нет, спор не разрешён (30.10, E13) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cj | Зеркало в пруду не встало: пища там не ограничивает (30.10, M1) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10ck | Пруд в рабочем режиме слишком разрешающий, чтобы мерить сосуществование (30.10, M2) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cl | Найден режим, где инвазия проваливается: плотность заполнения (30.10, M3) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cm | Пятно в режиме исключения: перенос не состоялся (30.10, M4) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cn | Неоднородность притока в пруду: направление есть, но конфаунд по занятости (30.10, M5) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10co | Выровненная занятость: направление сохранилось, значимости нет (30.10, M6) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cp | Живая петля: контур замкнулся, но канал насытился (30.10, E5, попытка 1) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cq | Живая петля замкнута, но мир себя в ней не видит (30.10, E5, попытка 2) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cr | Три метрики разнообразия: порядок устойчив, но «структур» меньше, чем кажется (30.10, X10) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cs | Живая петля: сильная корреляция оказалась общей формой (30.10, E5, попытка 3) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10ct | Гейт разброса: три уточнения, и граница его применимости (30.10, X12) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cu | Ампутация: пруд восстанавливается мгновенно, тяжесть удара не влияет (30.10, X13/B-038) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cv | Двадцать сидов отменяют главный вывод линии: статика не лучше изменчивости (30.10) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cw | Что устояло: неоднородность против гомогенности (30.10, X15) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cx | Сетка 128: направление воспроизвелось, значимость на грани (30.10, X16) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cy | Устойчиво ли это: 12 000 шагов вместо 6 000 (30.10, X17) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10cz | Амплитуда: эффект есть при всех трёх, значим при 0.5 и 0.8 (30.10, H-L1-1) | [`plan/10c-field-heterogeneity.md`](plan/10c-field-heterogeneity.md) |
| §10da | Случайность против неоднородности: дрожит всё поле или разные его части (30.10, X18) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10db | Из чего сделаны «шесть компонент»: доминант плюс мерцающая кайма (30.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dc | Время жизни: неоднородность дробит, а не создаёт тела (31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dd | Что дал внешний обзор: терминология, эквивалентность, перколяция (31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10de | Порог решает: оба мира — один перколяционный кластер (X26, 31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10df | Пилот адекватности (X33): зонд работает, но валюта не еда (31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dg | Признак в среде (X32): наследование становится автоматическим (31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dh | Форма не переносится: у структур нет переносимой идентичности (31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10di | Отбор сам себя прекращает: сильная связь даёт монополию (X37, 31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dj | Адекватности нет ни при какой цене ошибки (X33, 31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dk | Разнообразие и отбор — строгий компромисс, окна нет (X40, 31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dl | Мир, предъявляющий требования: канал не тот, требования не создаются (X41, 31.10) | [`plan/10d-field-metrics-and-form.md`](plan/10d-field-metrics-and-form.md) |
| §10dm | Пруд необитаем по цене: жить дороже, чем earns (31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10dn | Обитаемый режим найден: дело было в коэффициенте дохода (X43, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10do | Адекватность оказалась самомоделью, а не моделью мира (X44, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10dp | Канал внешнего: реализация есть, серия невалидна по двум причинам (X45, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10dq | Канал с задержкой: сигнал был, но органа не появилось (X46, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10dr | Сенсор невозможен без памяти: четвёртый раз в одно место (X47, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10ds | Контроль «призрак»: самомодель подтверждена интервенцией (X50, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10dt | Память сигнала: первый валидный опыт и отрицательный результат (X48, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10du | Пропущенное событие в поле: опыт нечувствителен по конструкции (X49, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
| §10dv | Сходимость по шагу: контраст ослаб втрое, знак удержался (X56, 31.10) | [`plan/10e-habitability-and-channels.md`](plan/10e-habitability-and-channels.md) |
