# Научный дайджест за 2026-10-26

Коммитов за сутки: **171**. Изменённых агрегатов: **31**.

## Что сделано (по коммитам)
- `ab2a4bb` рукопись+CLAIMS: цена — ограничение конструкции, а не выборки. Арифметика до опытов (порог -0.3 выходит за ДИ 
- `b53bb12` experiments+docs: 14 пилотов по числу линий — конструкция W2-bud не даёт >=12 линий (§10bd, exploratory)
- `c3e5579` мета-ревью invasion-0of10: пересчитал претензию — подтверждается (gap: [0,0,0,0,5,10,15,20,40,50], медиана 7.5
- `fde5792` SUPPLEMENT: в таблицу артефактов вошёл pilot_start100 (файл был в индексе, но таблица собрана раньше) — гейт а
- `277f364` SUPPLEMENT: пересобран после правки §4
- `08f94f5` гейт §чисел: verify_sections_numbers теперь ловит устаревшие значения (-0.700, -0.558) без пометки контекста —
- `3ddeeb0` рукопись: ссылка на разделы world-design переписана без § (гейт section_refs читал §10bb как раздел рукописи)
- `6d62e2a` рукопись §7: «что дальше» переписано — второй субстрат перенесён в «сделано» (R1: одна против многих, монотонн
- `dddb018` рукопись: убрано устаревшее -0.700 из сводной таблицы (§4, база) — заменено на -0.219 (rho_partial_energy_medi
- `69b798d` рукопись: указатель в начале раздела цены — текущие числа в блоке «Итог по цене (26.10)» (-0.478, знак 8/8), а
- `527a1dc` док: §6 incidents — ноль и «нечего считать» неотличимы (пустой список линий от несоединившихся ключей даёт Non
- `36cc942` правило §3c: любая корреляция подписывается коэффициентом, фильтром линий и знаменателем — без подписи число н
- `791a2fe` reports: точные имена ключей для воспроизведения отклика + сверка с независимым пересчётом
- `7ce87a1` reports: подписан метод расчёта отклика и зафиксировано расхождение с независимым пересчётом
- `2243d0f` claims: отклик — опровергнут независимой величиной (было «открыто: данные невалидны»)
- `a380d43` docs+reports: отклик признака не подтверждается независимой величиной — вопрос закрыт (0 GPU)
- `ec61025` цена: знак и величина разделены — знаковый тест 8/8 (p=0.0039) твёрд, медиана -0.478 при 95% ДИ [-0.797, -0.17
- `49258f4` рукопись: вставлены готовые блоки §4i (бутон-пара и пара любых меток, четыре конструкции со статусами, правило
- `c8eecad` reports: готовые блоки рукописи для §4i — пара и пара «любых меток» (моя часть сборки)
- `999153a` health.md: обновлён после закрытия дня
- `ed86816` docs+reports: закрыт вопрос о величине (механизм не установлен) и обновлён итог суток
- `28c7af9` инструкция: блок про выпуск v1.1 препринта (New version в Zenodo, concept DOI сохраняется, changelog в описани
- `0a3980a` v1.1: черновик §4.6 (перенос вне тел — «одна против многих»), ограничение и вывод обновлены; LaTeX-исходник с 
- `bfbbaae` scripts: check_draft_numbers сканирует весь morphogenesis/experiments, а не только линию пруда
- `f630353` experiments+docs: exploratory-сетка N_cap 10/20/40 — интерпретация «лимит выравнивает размеры линий» выдержала

## Что изменилось в числах (агрегаты)
- **ci_p_invasion_dose5**: без criteria
- **ci_p_invasion_keep_patches**: без criteria
- **ci_p_invasion_keep_uniform**: без criteria
- **ci_p_invasion_majority**: без criteria
- **ci_p_pair_any_tag**: без criteria
- **ci_p_pair_same_tag**: без criteria
- **ci_p_selection_replication**: без criteria
- **power_lines_price**: без criteria
- **recompute_i_onebud**: без criteria
- **recompute_i_pairany**: без criteria
- **recompute_i_w2bud3**: без criteria
- **recompute_i_w2budd2**: без criteria
- **whale_w2bud3**: без criteria
- **placement_matrix**: placement_series_valid=True, note=серия годна по постановке, если в каждом плече rejected <= 1/10 И state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится
- **placement_patches_matrix**: placement_series_valid=True, note=серия годна по постановке, если в каждом плече rejected <= 1/10 И state >= 15 в >= 9/10; иначе вопрос о режиме гибели не ставится
- **w1niche5_matrix**: not_lineage=9, note=вердикт — прямое парное сравнение долей; ожидание не используется
- **w1niche_matrix**: not_lineage=9, note=вердикт — прямое парное сравнение долей; ожидание не используется
- **w2bud2_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud3_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud4s_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_onebud_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=True
- **w2bud_pair_matrix**: I_above_null=False, I_above_null_7_of_10=False, I_positive_all_7_of_10=False, I_positive_valid_7_of_10=False
- **w2bud_pairany_matrix**: I_above_null=False, I_above_null_7_of_10=False, I_positive_all_7_of_10=False, I_positive_valid_7_of_10=False
- **w2bud_rep_patches_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2bud_rep_uniform_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2budd2_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=True
- **w2budd2_rep_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **w2budd2_rep_n1_matrix**: I_above_null=True, I_above_null_7_of_10=True, I_positive_all_7_of_10=True, I_positive_valid_7_of_10=False
- **r1_matrix**: monotone_prediction=I_ratio(k=1) > I_ratio(k=2) > I_ratio(k=8), pilot_note=пилот: 1 сид на плечо; серия — 10 сидов после проверки режима
- **r1cap_matrix**: monotone_prediction=I_ratio(k=1) > I_ratio(k=2) > I_ratio(k=8), pilot_note=пилот: 1 сид на плечо; серия — 10 сидов после проверки режима

## Рекомендации (из чисел, не из прозы)
- новых рекомендаций нет (все уже выдавались и не закрыты)

## Отдача литературы (7 дней)
- DOI в добавленных/правленых строках `hypotheses/` за неделю: **175**; из них упомянуты ВНЕ индексов (answers/conditions/claims/reviews): **37** (отдача 21%)
  *читается так:* это доля источников, которые дошли до рабочего текста, а не только до индекса. Ниже 30 % две недели подряд — снижать частоту литслота, а не наращивать объём.

## Доска и литература
- новых замечаний: 2; решено: 2 (принято 0, отклонено 1)
- литдавление: 2 (порог 3)
  открытые вопросы: 0 []
  открытые lit-пункты очереди: 0 []
