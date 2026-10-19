"""
wp4_ablations.py — дешёвые дискриминанты коллапса E02 (план WP4, гипотезы H-A…H-D).

Все прогоны КОРОТКИЕ (по умолчанию 200 шагов) и идут с выключенным
предохранителем: нам нужна вся траектория alive_fraction, а не досрочная
остановка на первом признаке смерти. Каждый arm — это одна изменённая настройка
относительно базлайна, поэтому arm'ы сравнимы между собой (тот же сид, тот же
целевой паттерн, та же последовательность шумовых ключей).

Запуск:  python wp4_ablations.py [--steps 200] [--seeds 42] [--arms H-A1,H-A2]
        python wp4_ablations.py --steps 400 --arms H-I1,H-I2 --reparse
Режим --reparse ничего не обучает: он перечитывает логи config.LOG_DIR и
пересчитывает производные метрики — им и добивались поля grad_norm/unroll/
coverage у волн, запущенных до соответствующей правки train.py.
Результат: experiments/E02_pattern/wp4_ablations.json
"""

import argparse

import json

import os

# §9.2: config раньше torch.

import config

from utils.logging import final_run_rows

DEFAULT_ARMS = [
    "H-A0",
    "H-A3",
    "H-E",
    "H-F",
    "H-G",
    "H-H",
    "H-D3",
]

# Третья волна: после того как вторая волна (400 шагов) показала, что коллапс
# имеет ДВА разных тайминга, а не один (см. H-I* ниже).
WAVE3_ARMS = ["H-I1", "H-I2", "H-I3", "H-J1"]

# Четвёртая волна: проверка поглощающей смерти (§5.2) как трещотки коллапса.
WAVE4_ARMS = ["H-K1", "H-K2"]

# Пятая волна: «учится ли цель вообще» на горизонте, где warmup заканчивается.
# Запускать со --steps 4000, а не с 200/400.
WAVE5_ARMS = ["H-N1", "H-M2", "H-M1"]

# Шестая волна: тест ёмкости (пул из цели), а не роста из шума.
WAVE6_ARMS = ["H-P1"]

# Седьмая волна (WP4b): retention roll-out в лоссе (§14.2). Горизонт — 4000+,
# иначе проверяем то же, что уже опровергнуто: на 400 шагах warmup LR не
# заканчивается (§12.1.5, NEG-08).
# R-6 в этом списке записан, но НЕ ПРОГОНЯЛСЯ: после NEG-19 вопрос сместился с
# «где пол alpha» на «есть ли пари», и R-6 (margin 0.4, мн. 3.0) проверяет то,
# что R-7/R-8 уже закрыли с другой стороны. Требование плана — не молчать о
# пропущенном arm'е: он superseded (снят как вопрос), а не «забыт»; запись об
# этом в memory/negative_results.md (NEG-20, следующий шаг) и в отчёте.
WAVE7_ARMS = ["R-1", "R-2", "R-3", "R-4", "R-5", "R-6", "R-7", "R-8"]

# Девятая волна (WP4b): парный quiet-член на ТОЙ ЖЕ автономной развёртке
# (убирает «живо всё» из R-8, NEG-20). Веса калиброваны по градиенту, не наугад.
WAVE9_ARMS = ["R-9", "R-10", "R-11"]

ARMS = {
    # Базлайн: то, что уже провалило гейт слоя 1 (для парности сравнения).
    "H-A0": ("базлайн: supervised_mse, ALPHA_SUPERVISION_WEIGHT=1.0", {}),
    # H-A: снимает только supervised-давление на alive-канал, всё остальное как в
    # базлайне. Если ткань выживает — причина в члене alive_policy, а не в LR.
    "H-A1": ("supervised_mse, ALPHA_SUPERVISION_WEIGHT=0", {"ALPHA_SUPERVISION_WEIGHT": 0.0}),
    # H-A-лечение: тот же вес, но односторонний штраф за смерть в области цели.
    "H-A2": ("death_penalty: карается только смерть в цели", {"ALIVE_POLICY_MODE": "death_penalty"}),
    # H-B: L1 по дельте выключен — проверяет «заморозку динамики».
    "H-B": ("hidden_regularization=0 (L1 по delta выключен)", {"LOSS_WEIGHTS": {"hidden_regularization": 0.0}}),
    # H-D: LR-свип.
    "H-D1": ("TRAIN_LR=3e-4", {"TRAIN_LR": 3e-4}),
    "H-D2": ("TRAIN_LR=1e-4", {"TRAIN_LR": 1e-4}),
    "H-D3": ("TRAIN_LR=3e-5", {"TRAIN_LR": 3e-5}),
    # --- вторая волна: бисекция состава лосса -------------------------------
    # Итог первой волны (seed 42, 200 шагов): H-A0/H-A1/H-A2/H-B/H-D1 умерли
    # (alive_fraction на iter 200 = 0.0014–0.0017), но H-D2 (LR=1e-4) на том же
    # горизонте даёт alive_fraction 0.349 — то есть единственная переменная,
    # которая до сих пор меняла исход, это величина шага, а не состав лосса.
    # Поэтому: (1) снимаем оставшиеся служебные члены по одному, (2) проверяем
    # режим «не убий», (3) удлиняем горизонт у низких LR, чтобы отделить
    # «выживает» от «просто медленнее умирает».
    "H-A3": ("survival: карается переход живой->мёртвая, а не форма поля альфа",
             {"ALIVE_POLICY_MODE": "survival"}),
    "H-E": ("stress_proxy=0 (внутренний сенсор ошибки не учится)", {"LOSS_WEIGHTS": {"stress_proxy": 0.0}}),
    "H-F": ("topo_proxy=0 (топологический член выключен)", {"LOSS_WEIGHTS": {"topo_proxy": 0.0}}),
    "H-G": ("только visible_mse (все служебные члены выключены)",
            {"LOSS_WEIGHTS": {"alive_policy": 0.0, "hidden_regularization": 0.0,
                              "stress_proxy": 0.0, "topo_proxy": 0.0}}),
    "H-H": ("visible_mse + alive_policy (death_penalty), без L1/stress/topo",
            {"ALIVE_POLICY_MODE": "death_penalty",
             "LOSS_WEIGHTS": {"hidden_regularization": 0.0, "stress_proxy": 0.0, "topo_proxy": 0.0}}),
    # --- третья волна: куррикулум BPTT как пусковой механизм -----------------
    # Вторая волна (400 шагов, seed 42, без coverage-логирования — артефакт
    # запуска до правки train.py) дала ДВА разных профиля смерти:
    #   H-A0/H-A3 (LR=1e-3): af 0.48 -> 0.14 (it100) -> 0.065 -> 0.001 (it200),
    #     grad_norm всё время ~0-2, то есть плавная спираль в смерть;
    #   H-D2 (LR=1e-4): af держится 0.50/0.49/0.47 на it 50/100/150, затем ровно
    #     на it=200 grad_norm подскакивает 1.4 -> 21.4 и af падает 0.349 -> 0.149
    #     -> 0.009 -> 0.0014. H-D3 (LR=3e-5) повторяет картину: 0.475 на it200 с
    #     grad_norm 13.
    # It=200 — это TRAIN_BPTT_CURRICULUM_AT: длина раскрутки становится 32 вместо
    # 16. Значит «H-D2 выжил на 200 шагах» был артефактом горизонта: прогон
    # обрывался за шаг до перехода. Ниже — проверка перехода.
    "H-I1": ("LR=1e-4 БЕЗ прыжка unroll (curriculum [16,16,16])",
             {"TRAIN_LR": 1e-4, "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    "H-I2": ("LR=3e-5 БЕЗ прыжка unroll",
             {"TRAIN_LR": 3e-5, "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    "H-I3": ("LR=1e-3 (базлайн) БЕЗ прыжка unroll",
             {"TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    # If the trigger is the size of the shock rather than the transition itself,
    # a tighter clip should blunt it. Reported grad_norm is the PRE-clip total
    # (torch.nn.utils.clip_grad_norm_), so H-D2 really did take a norm-1.0 step.
    "H-J1": ("LR=1e-4, jump есть, но TRAIN_GRAD_CLIP_NORM=0.1",
             {"TRAIN_LR": 1e-4, "TRAIN_GRAD_CLIP_NORM": 0.1}),
    # --- четвёртая волна: поглощающая смерть как трещотка --------------------
    # H-I1 (LR=1e-4, куррикулум [16,16,16]) умер и без перехода: 0.502 -> 0.420
    # (it200) -> 0.302 -> 0.130 -> 0.068, плавно и без скачка grad_norm. Значит
    # переход куррикулума — ускоритель, а не первопричина. Остаётся механизм,
    # который обязывает живость только убывать: §5.2, мёртвая клетка обнуляется
    # ЦЕЛИКОМ (nca_core: enforce_alive_policy + life_support_mask, оба под
    # if self.alive_mask_enabled), а включается маска на ALIVE_WARMUP_ITERS=50 —
    # ровно там, где начинается убывание во всех arm'ах. Если маска никогда не
    # включается, смерть не поглощающая: alive_fraction перестаёт быть
    # монотонно убывающей, и f1 получает шанс вырасти.
    "H-K1": ("alive-маска никогда не включается (ALIVE_WARMUP_ITERS=9999): смерть не поглощающая",
             {"ALIVE_WARMUP_ITERS": 9999}),
    # Тот же выключенный рэтчет, но и без давления alive_policy: разделяет
    # «убивает поглощение» и «убивает член alive_policy».
    "H-K2": ("alive-маска выключена + alive_policy=0",
             {"ALIVE_WARMUP_ITERS": 9999, "LOSS_WEIGHTS": {"alive_policy": 0.0}}),
    # --- пятая волна: а учится ли цель вообще на полноценном горизонте? ------
    # H-K1 (маска выключена, всё остальное как в базлайне) умер по alive_fraction,
    # но его visible_mse дошёл до 0.1397 против 0.2499 у всех mask-on arm'ов —
    # то есть без поглощающей смерти сеть учится заметно лучше, просто выученное
    # поле остаётся ТЕМНЕЕ порога бинаризации 0.5 (f1 0.000, β₀=0). H-K2 (маска и
    # alive_policy выключены) даёт af 0.998 при том же visible_mse 0.1399: альфа
    # без давления живёт, но кольцо из канала 0 всё равно не собирается.
    # Значит короткий горизонт путает два разных вопроса — «ткань умерла» и «цель
    # не выучена». Отделяем: тот же состав лосса, но горизонт за границей warmup
    # (TRAIN_WARMUP_STEPS=500), предохранитель выключен; длина горизонта — в
    # --steps и зашита в experiment_id.
    "H-M1": ("полный контракт (mask on), длинный горизонт, fuse выключен", {}),
    "H-M2": ("mask выключен, длинный горизонт: учится ли кольцо, когда его не убивают",
             {"ALIVE_WARMUP_ITERS": 9999}),
    # H-M2 на it 200-500 стоит ровно на том же 0.1399, что и H-K1, при
    # grad_norm 0.00-0.01: оптимизация встала НЕ из-за смерти ткани, а потому,
    # что сеть сошлась к константной («всё потемнее») задаче, где больше ничего
    # не убывает. H-N1 убирает ВСЕ силы, которые могут удерживать её в этой
    # яме: маска выключена, альфа-супервизия выключена, L1 по дельте (штраф за
    # движение) выключен. Это тест «способна ли вообще архитектура собрать
    # кольцо», отделённый от вопроса «кто убивает ткань».
    "H-N1": ("чистый тест обучаемости: mask off + alive_policy=0 + L1=0",
             {"ALIVE_WARMUP_ITERS": 9999,
              "LOSS_WEIGHTS": {"alive_policy": 0.0, "hidden_regularization": 0.0}}),
    # Шестая волна: отделяем «архитектура не может» от «не успевает вырасти».
    # H-N1 при выключенных маске, альфа-супервизии и L1 всё равно стоит на плато
    # почти-чёрного поля (it 600: visible_mse 0.1368, f1 0.000, grad_norm 0.05,
    # β₀=β₁=0) — значит дело не в членах, которые тянут в яму. H-P1 снимает сам
    # рост из шума: пул наполняется состоянием, где видимый канал УЖЕ равен цели
    # (TRAIN_POOL_INIT_MODE="target"), остаётся только удержать форму — второй
    # критерий §14.2 («форма удерживается без внешнего микроменеджмента»). Если
    # здесь f1 не около 1.0, виновата ёмкость/динамика; если удерживается, блокёр
    # в постановке «вырасти из шума за горизонт BPTT 16-64».
    "H-P1": ("ёмкость и удержание: пул стартует из цели (pool_init_mode=target)",
             {"TRAIN_POOL_INIT_MODE": "target"}),
    # --- седьмая волна (WP4b): удержание как член лосса, §14.2 ----------------
    # Назначение owner'а после NEG-17 (5 из 5 сидов: смерть на итерации 200 при
    # разбросе финального MSE 8.9e-5). Waves H-A..H-P ответили, что блокер НЕ
    # состав лосса и НЕ ёмкость; R-плечи проверяют единственную оставшуюся
    # гипотезу — лосс обязан спрашивать поле через автономные шаги, а не только
    # на входе шага обучения.
    "R-1": ("retention roll-out K=8, вес 0.5, survival 1.0",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 8,
             "LOSS_WEIGHTS": {"retention": 0.5}}),
    "R-2": ("retention K=8, вес 1.0, survival 2.0 (давление на живость сильнее)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 8,
             "RETENTION_SURVIVAL_WEIGHT": 2.0, "LOSS_WEIGHTS": {"retention": 1.0}}),
    # K=16 каждый второй шаг: тот же объём вычислений на шаг обучения, что у
    # R-2, но горизонт автономии вдвое длиннее — проверка, что эффект не от K,
    # а от самого наличия roll-out.
    "R-3": ("retention K=16, вес 1.0, roll-out каждый 2-й шаг",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
             "RETENTION_EVERY": 2, "LOSS_WEIGHTS": {"retention": 1.0}}),
    # --- R-4/R-5: та же постановка «удержание», но survival-член видит смерть --
    # Основание (NEG-18): R-1 повторил коллапс базлайна, а его survival-член дал
    # 1.9e-4…8.5e-4 при visible_mse 0.25. Причина не вес, а форма: мёртвая клетка
    # имеет alpha = sigmoid(0) = 0.5 = ALIVE_THRESHOLD (§5.7–5.8), и
    # transition-штраф relu(alpha_prev − alpha)·alpha_prev на ней ровно 0 — член
    # слеп к поглощающей смерти. level-форма relu(threshold + margin − alpha) по
    # клеткам цели при alpha = 0.5 даёт margin, то есть усилие есть именно там,
    # R-4/R-5 обоснованы как исправление формы, а не как ещё один вес.
    # Замер (wp4_retention_scale, CPU, свежие веса) по норме градиента на
    # параметрах: у level-члена в полосе alpha∈(0.5;0.6) gn=0.043…0.136 против
    # gn(visible_mse)=0.66 — чтобы усилия были одного порядка, множитель должен
    # быть 5…15. R-4 берёт минимальное (1.0: проверяет сам факт влияния), R-5 —
    # 10.0 из середины диапазона и вдвое более длинный автономный горизонт.
    # Ограничение зафиксировано заранее и оно из той же диагностики: на ПОЛНОСТЬЮ
    # мёртвом поле градиент любого survival-члена ровно 0 (AliveSTE обнуляет
    # состояние, §5.2 — смерть поглощающая). Значит R-плечи могут только не
    # дать умереть в первые ~150 итераций; прогон, где ткань уже мертва, член
    # не спасёт, и отрицательный результат надо читать так.
    "R-4": ("retention K=8, вес 1.0, survival level (margin 0.1, множитель 1.0)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 8,
             "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
             "LOSS_WEIGHTS": {"retention": 1.0}}),
    "R-5": ("retention K=16, вес 1.0, survival level (margin 0.1, множитель 10.0)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
             "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
             "RETENTION_SURVIVAL_WEIGHT": 10.0, "LOSS_WEIGHTS": {"retention": 1.0}}),
    # R-6 проверяет НЕ силу, а ПОЛОЖЕНИЕ усилия. Причина, по которой R-4 (level,
    # margin 0.1) умер так же, как R-1: градиент level-члена существует только в
    # полосе alpha ∈ (0.5; 0.6), а клетки проходят её за несколько итераций —
    # дальше член остаётся большим по значению (замер: surv 0.094…0.098 при
    # margin 0.1, то есть почти все клетки цели уже мертвы), но с нулевым
    # градиентом. Пол 0.9 (margin 0.4) оставляет клетку в полосе с градиентом,
    # пока она ещё жива: усилие прилагается ДО перехода, а не после.
    "R-6": ("retention K=8, вес 1.0, survival level (margin 0.4 -> пол alpha=0.9, мн. 3.0)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 8,
             "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.4,
             "RETENTION_SURVIVAL_WEIGHT": 3.0, "LOSS_WEIGHTS": {"retention": 1.0}}),
    # R-7 — из замера R-5, а не из догадки. R-5 (level, margin 0.1, множитель 10,
    # K=16) впервые удержал ткань живой на горизонте, где раньше она была мертва:
    # af=1.000 на it=50…150 и 0.999 на it=200 при visible_mse 0.2625 -> 0.1377.
    # Умер он не от постановки, а ровно на скачке учебной программы unroll
    # 16 -> 32 на итерации 200 (§12.1.13): it=200 af 0.999, it=250 af 0.001 и
    # штраф, насыщенный до margin. Значит удержание подавляет смерть, пока шаг
    # обучения не меняется, и следующий вопрос — выживает ли ткань на
    # flat-программе [16,16,16], где скачка нет (H-I1/H-I3 проверяли flat без
    # retention и умирали; здесь проверяется обратная комбинация).
    # Второй вывод R-5, который этот arm не прячет: при живом поле f1 ПАДАЕТ
    # (0.1886 -> 0.0004 к it=200), то есть удержание само по себе морфогенез не
    # делает — модель выбирает «живое ровное поле» (MSE 0.1377 у пола константы
    # 0.129135). Поэтому R-7 засчитывается только по полному эндпоинту гейта
    # (f1 выше потолка 0.2644 + 0.05), а не по факту выживания.
    "R-7": ("retention K=16, мн. 10 level + flat curriculum [16,16,16] (без скачка unroll)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
             "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
             "RETENTION_SURVIVAL_WEIGHT": 10.0, "LOSS_WEIGHTS": {"retention": 1.0},
             "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    # R-8 — ответ на вторую половину NEG-19: удержание «держите alpha выше пола»
    # оптимизируется тривиально («живо всё», precision 0.025), потому что сети
    # общие и поднять alpha в области цели дешевле, чем сформировать границу.
    # Пари against это — надзор над живостью ФОНА, он в лоссе уже есть
    # (alive_policy, §12.6.3), но с весом 0.5 против retention-множителя 10 его
    # давление перекручено. Отличие от R-7 ровно одно — вес alive_policy 2.0,
    # поэтому сравнение R-7/R-8 изолирует пари по фону, а не состав лосса.
    "R-8": ("R-7 + пари по фону: alive_policy вес 2.0 (живость вне цели карается)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
             "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
             "RETENTION_SURVIVAL_WEIGHT": 10.0,
             "LOSS_WEIGHTS": {"retention": 1.0, "alive_policy": 2.0},
             "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    # Волна 9 — пари к survival-члену на ТОЙ ЖЕ траектории (quiet). Причина —
    # итог R-8 на горизонте 2000 (experiments/E02_pattern/wp4_ablations.json):
    # ткань впервые пережила весь горизонт (alive_min 0.4575 при пороге 0.0762,
    # коллапса нет), но f1_max остался 0.2300 < потолка поля без структуры
    # 0.2644, а precision ~0.15 при плотности цели 0.1523, то есть «живо всё»
    # с шумом. Однокадровое пари (alive_policy) смерть фона не отменило,
    # потому что вырождение живёт в автономном roll-out, где eval-полиса нет.
    # Веса quiet взяты не наугад, а из замера wp4_retention_scale.py на чекпоинте
    # R-8 (сид 42, K=16, level; срез возраста 0 — живой фон, af 0.679):
    #   gn(visible_mse)=1.1509, gn(survival при мн. 1.0)=0.0399, gn(quiet)=0.3441
    # Значит при мн. survival 10.0 его вклад по градиенту ~0.399, и паритет с
    # ним требует quiet~1.16 (R-9, округлённо 1.0), а паритет с самим
    # visible_mse требует ~3.3 (R-10). Две точки вместо одной догадки: если
    # 1.0 не сдвинет форму, а 3.0 убьёт ткань, вывод будет про масштаб, а не
    # про член. R-11 — контроль состава: тот же quiet 1.0 без усиленного
    # однокадрового alive_policy, чтобы отделить «пари в roll-out» от «пари на
    # кадре». Сравнения: R-7↔R-11 изолирует quiet, R-9↔R-11 — alive_policy 2.0,
    # R-8↔R-9 — quiet поверх усиленного полиса.
    "R-9": ("R-8 + quiet-пари в roll-out с весом 1.0 (паритет с survival×10 по замеру)",
            {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
             "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
             "RETENTION_SURVIVAL_WEIGHT": 10.0, "RETENTION_QUIET_WEIGHT": 1.0,
             "LOSS_WEIGHTS": {"retention": 1.0, "alive_policy": 2.0},
             "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    "R-10": ("R-8 + quiet-пари с весом 3.0 (паритет с visible_mse по замеру)",
             {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
              "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
              "RETENTION_SURVIVAL_WEIGHT": 10.0, "RETENTION_QUIET_WEIGHT": 3.0,
              "LOSS_WEIGHTS": {"retention": 1.0, "alive_policy": 2.0},
              "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
    "R-11": ("R-7 + quiet-пари с весом 1.0 (без усиленного alive_policy)",
             {"RETENTION_ENABLED": True, "RETENTION_ROLLOUT_STEPS": 16,
              "RETENTION_SURVIVAL_MODE": "level", "RETENTION_ALIVE_MARGIN": 0.1,
              "RETENTION_SURVIVAL_WEIGHT": 10.0, "RETENTION_QUIET_WEIGHT": 1.0,
              "LOSS_WEIGHTS": {"retention": 1.0},
              "TRAIN_BPTT_CURRICULUM": [16, 16, 16]}),
}


def _apply(overrides):
    """Вернуть функцию отката настроек config после arm'а."""
    saved = {}
    for key, value in overrides.items():
        saved[key] = getattr(config, key)
        if key == "LOSS_WEIGHTS":
            merged = dict(config.LOSS_WEIGHTS)
            merged.update(value)
            setattr(config, key, merged)
        else:
            setattr(config, key, value)

    def restore():
        for key, value in saved.items():
            setattr(config, key, value)

    return restore


def _trajectory(log_path):
    rows = []
    if not os.path.exists(log_path):
        return rows
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "iteration" not in entry or "loss" not in entry:
                continue
            loss = entry["loss"]
            rows.append(
                {
                    "iteration": entry["iteration"],
                    "total": loss["total"],
                    "visible_mse": loss["visible_mse"],
                    "alive_policy": loss["alive_policy"],
                    "hidden_reg": loss["hidden_reg"],
                    "alive_fraction": loss["alive_fraction"],
                    # retention_* появились в логе вместе с членом §14.2 (WP4b);
                    # .get(), а не [] — старые логи волн H-A..H-P их не содержат,
                    # и reparse не имел права на них падать.
                    "retention_mse": loss.get("retention_mse"),
                    "retention_survival": loss.get("retention_survival"),
                    "retention_quiet": loss.get("retention_quiet"),
                    # grad_norm в логе — это НОРМА ДО клиппинга (torch.nn.utils.
                    # clip_grad_norm_ возвращает сумму до масштабирования), то
                    # есть «насколько сильным был посыл» независимо от того, как
                    # сильно его подрезал TRAIN_GRAD_CLIP_NORM.
                    "grad_norm": entry.get("grad_norm"),
                    "lr": entry.get("lr"),
                    "unroll": entry.get("unroll"),
                    "phase": entry.get("phase"),
                    "alive_mask_enabled": entry.get("alive_mask_enabled"),
                    "chamfer": entry.get("symmetric_chamfer_error"),
                    "coverage": entry.get("coverage"),
                    "b0": entry.get("topology", {}).get("b0"),
                    "b1": entry.get("topology", {}).get("b1"),
                    "density": entry.get("topology", {}).get("density"),
                }
            )
    # Лог прогона append-история (§7.7): оставляем только последний прогон,
    # иначе минимум alive_fraction считается по чужим точкам.
    return final_run_rows(rows)


def _summarize(rows, arm, steps, seed, threshold, description, overrides):
    """Вывести метрики из траектории. Отдельно от train-а, чтобы вызывался и из
    --reparse: журнал прогона (§7.7) первичен, а его производные можно
    пересчитать, когда к списку метрик добавляется новое поле."""
    alive = [r["alive_fraction"] for r in rows]
    chamfers = [r["chamfer"] for r in rows if r.get("chamfer") is not None]
    f1s = [
        r["coverage"]["f1"]
        for r in rows
        if isinstance(r.get("coverage"), dict) and r["coverage"].get("f1") is not None
    ]
    # f1 сам по себе не отвечает на вопрос «есть ли форма»: важно ГДЕ достигнут
    # максимум. Замерено в wave 9 (NEG-21): у всех четырёх плеч с удержанием
    # argmax f1 — итерация 50, первая же точка после сброса маски, а дальше f1
    # только падает. Значит f1_max на коротком горизонте измеряет начальное
    # состояние модели, а не результат обучения, и ряд «f1_max выше потолка» без
    # этой колонки читается как verdict по форме там, где вердикта нет.
    f1_points = [
        (r["iteration"], r["coverage"]["f1"])
        for r in rows
        if isinstance(r.get("coverage"), dict) and r["coverage"].get("f1") is not None
    ]
    f1_max_iteration = (
        max(f1_points, key=lambda p: p[1])[0] if f1_points else None
    )
    # Нулевые точки выключенного члена неотличимы от «идеальное удержание»,
    # поэтому ряд берётся только для arm'а с включённым retention: у остальных
    # поля будут None, а не 0.0.
    retention_on = bool(
        overrides.get("RETENTION_ENABLED")
        or float((overrides.get("LOSS_WEIGHTS") or {}).get("retention", 0.0)) > 0.0
    )
    ret_mse = (
        [r["retention_mse"] for r in rows if r.get("retention_mse") is not None]
        if retention_on
        else []
    )
    ret_surv = (
        [r["retention_survival"] for r in rows if r.get("retention_survival") is not None]
        if retention_on
        else []
    )
    ret_quiet = (
        [r["retention_quiet"] for r in rows if r.get("retention_quiet") is not None]
        if retention_on
        else []
    )
    # Пик градиента и момент, когда ткань впервые провалилась под порог, —
    # именно их совпадение (it=200, переход unroll 16->32) превратило «H-D2
    # выжил» в артефакт горизонта.
    grads = [(r["iteration"], r["grad_norm"]) for r in rows if r.get("grad_norm") is not None]
    peak = max(grads, key=lambda t: t[1]) if grads else (None, None)
    collapse_iteration = None
    unroll_at_collapse = None
    for r in rows:
        if r["alive_fraction"] < threshold:
            collapse_iteration = r["iteration"]
            unroll_at_collapse = r.get("unroll")
            break
    # Первый переход куррикулума = первая итерация, на которой длина раскрутки
    # отличается от предыдущей записанной. Ищем по логам, а не по config: в
    # arm'ах H-I* расписание переопределено, и именно это надо увидеть в данных.
    transition_iteration = None
    unroll_before = None
    unroll_after = None
    alive_before_transition = None
    grad_norm_at_transition = None
    grad_norm_median_before = None
    previous = None
    previous_index = -1
    for index, r in enumerate(rows):
        u = r.get("unroll")
        if u is None:
            continue
        if previous is not None and u != previous["unroll"]:
            transition_iteration = r["iteration"]
            unroll_before = previous["unroll"]
            unroll_after = u
            alive_before_transition = previous["alive_fraction"]
            grad_norm_at_transition = r.get("grad_norm")
            before = sorted(
                q["grad_norm"]
                for q in rows[: previous_index + 1]
                if q.get("grad_norm") is not None
            )
            if before:
                mid = len(before) // 2
                grad_norm_median_before = (
                    before[mid]
                    if len(before) % 2
                    else 0.5 * (before[mid - 1] + before[mid])
                )
            break
        previous = r
        previous_index = index
    return {
        "arm": arm,
        "description": description,
        "overrides": overrides,
        "seed": int(seed),
        "steps": int(steps),
        "collapse_threshold": threshold,
        # Прогон мог быть остановлен досрочно (Ctrl-C, OOM, граница фазы). Тогда
        # последняя записанная итерация меньше заявленного горизонта, и запись
        # обязана это показывать: «alive_min» на 700 итерациях — не результат
        # прогона в 4000.
        "logged_final_iteration": rows[-1]["iteration"] if rows else None,
        "truncated": bool(rows and rows[-1]["iteration"] < int(steps)),
        "alive_fraction_min": min(alive) if alive else None,
        "alive_fraction_final": alive[-1] if alive else None,
        "collapse_iteration": collapse_iteration,
        "unroll_at_collapse": unroll_at_collapse,
        "transition_iteration": transition_iteration,
        "unroll_before_transition": unroll_before,
        "unroll_after_transition": unroll_after,
        "alive_fraction_before_transition": alive_before_transition,
        "grad_norm_at_transition": grad_norm_at_transition,
        "grad_norm_median_before_transition": grad_norm_median_before,
        "grad_norm_max": peak[1],
        "grad_norm_at": peak[0],
        "visible_mse_first": rows[0]["visible_mse"] if rows else None,
        "visible_mse_final": rows[-1]["visible_mse"] if rows else None,
        # Члены удержания (§14.2, WP4b). При выключенном retention train пишет
        # 0.0 — это не «удержание не удалось», а «удержание не обучалось»,
        # поэтому рядом лежит retention_enabled_by_overrides.
        "retention_enabled_by_overrides": retention_on,
        # Форма survival-члена меняется вместе с выводом: R-1 (transition) и
        # R-4 (level) имеют одинаковый вес retention=1.0 и разные предсказания,
        # поэтому без mode запись нельзя отличить при чтении results (§13.5).
        "retention_survival_mode": (
            overrides.get("RETENTION_SURVIVAL_MODE")
            if retention_on
            else None
        ),
        "retention_alive_margin": (
            overrides.get("RETENTION_ALIVE_MARGIN") if retention_on else None
        ),
        "retention_mse_first": ret_mse[0] if ret_mse else None,
        "retention_mse_final": ret_mse[-1] if ret_mse else None,
        "retention_survival_final": ret_surv[-1] if ret_surv else None,
        # Вторая половина полосы (§14.2 + NEG-20): без этих полей прогон
        # «survival + quiet» выглядит идентично прогону «только survival», а
        # именно на этой паре решается, есть ли форма или только выживание.
        "retention_quiet_final": ret_quiet[-1] if ret_quiet else None,
        "retention_quiet_weight": (
            overrides.get("RETENTION_QUIET_WEIGHT") if retention_on else None
        ),
        "retention_quiet_margin": (
            overrides.get("RETENTION_QUIET_MARGIN") if retention_on else None
        ),
        "chamfer_first": chamfers[0] if chamfers else None,
        "chamfer_final": chamfers[-1] if chamfers else None,
        "f1_final": f1s[-1] if f1s else None,
        "f1_max": max(f1s) if f1s else None,
        "f1_max_iteration": f1_max_iteration,
        "survived": bool(alive and min(alive) >= threshold),
        "trajectory": rows,
    }


def run_arm(arm, steps, seed, collapse_threshold=None):
    from train import train

    description, overrides = ARMS[arm]
    restore = _apply(overrides)
    # steps в имени обязательны: один и тот же arm на разном горизонте — это
    # разные прогоны, и общий лог/чекпоинт смешал бы их траектории.
    experiment_id = f"WP4_{arm}_s{steps}_seed{seed}"
    original_ckpt = config.CHECKPOINT_DIR
    config.CHECKPOINT_DIR = os.path.join(original_ckpt, experiment_id)
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
    try:
        # stop_on_collapse=False: нужен полный профиль траектории.
        model, state = train(
            experiment_id=experiment_id,
            seed=seed,
            max_steps=steps,
            stop_on_collapse=False,
        )
    finally:
        config.CHECKPOINT_DIR = original_ckpt
        restore()
    rows = _trajectory(os.path.join(config.LOG_DIR, f"{experiment_id}_log.jsonl"))
    threshold = (
        config.COLLAPSE_ALIVE_FRACTION_MIN
        if collapse_threshold is None
        else float(collapse_threshold)
    )
    return _summarize(rows, arm, steps, seed, threshold, description, overrides)


def _log_path(arm, steps, seed):
    """Имя лога прогона. Волна 1 запускалась до того, как горизонт стали шить в
    experiment_id, поэтому у неё старый формат WP4_<arm>_seed<seed> — оба
    формата перебираем, иначе reparse молча потерял бы доказательства первой
    волны (§7.7: потерянный результат хуже неполного)."""
    candidates = (
        f"WP4_{arm}_s{steps}_seed{seed}",
        f"WP4_{arm}_seed{seed}",
    )
    for name in candidates:
        path = os.path.join(config.LOG_DIR, f"{name}_log.jsonl")
        if os.path.exists(path):
            return path
    return os.path.join(config.LOG_DIR, f"{candidates[0]}_log.jsonl")


def reparse(steps, seeds, arms, threshold):
    """Пересчитать записи из существующих логов БЕЗ обучения.

    Нужен потому, что часть волн запускалась до того, как train.py начал писать
    coverage и до того, как сюда добавились grad_norm/unroll. Логи на месте,
    значит производные метрики можно достать задним числом, не тратя GPU.
    """
    out = []
    for arm in arms:
        for seed in seeds:
            path = _log_path(arm, steps, seed)
            if not os.path.exists(path):
                print(f"[reparse] {arm}: нет лога {path} — пропуск")
                continue
            rows = _trajectory(path)
            if not rows:
                print(f"[reparse] {arm}: лог есть, точек обучения нет — пропуск")
                continue
            description, overrides = ARMS.get(arm, (None, None))
            out.append(
                _summarize(
                    rows,
                    arm,
                    steps,
                    seed,
                    threshold,
                    description if description else "восстановлено из лога",
                    overrides if overrides is not None else {},
                )
            )
            r = out[-1]
            alive_min = r["alive_fraction_min"]
            print(
                f"[reparse] {arm:5s} af_min={'нет' if alive_min is None else f'{alive_min:.4f}'} "
                f"survived={r['survived']} coll_it={r['collapse_iteration']} "
                f"unroll@coll={r['unroll_at_collapse']} gn_max={r['grad_norm_max']} "
                f"@{r['grad_norm_at']} f1={r['f1_max']}"
            )
    return out


def main(steps, seeds, arms, do_reparse=False):
    from target_patterns import create_target

    out_dir = os.path.join("experiments", "E02_pattern")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "wp4_ablations.json")

    # Плотность цели — обязательный контекст: у цели ring она 0.1523, и
    # абсолютный порог 0.15 стоит впритык, поэтому вердикт «выжил/умер»
    # считается от относительного порога (config.collapse_alive_fraction_min).
    target = create_target(device="cpu")
    target_density = float((target > 0).float().mean().item())
    threshold = config.collapse_alive_fraction_min(target_density)
    print(f"[wp4] плотность цели={target_density:.4f} порог коллапса={threshold:.4f}")

    # Волны запускаются отдельными командами, файл один. Без слияния вторая
    # волна стёрла бы доказательства первой (§7.7: результаты не перезаписываем,
    # дополняем). Ключ — (arm, seed, steps): перевыпуск той же конфигурации с
    # другим горизонтом остаётся отдельной записью.
    own = []

    def _read_runs():
        """Читает runs из файла; повреждённая/неполная запись — пустой список.

        Файл мог быть прерван посередине json.dump (два процесса пишут в один
        путь), поэтому разбор защищён: потерянные при чтении чужие записи
        достаются из логов через --reparse, но ронять из-за них прогон нельзя.
        """
        if not os.path.exists(out_path):
            return []
        try:
            with open(out_path, "r", encoding="utf-8") as fh:
                return list(json.load(fh).get("runs", []))
        except (json.JSONDecodeError, OSError):
            return []

    def _key(r):
        return (r["arm"], int(r["seed"]), int(r["steps"]))

    def _write():
        # Перечитать ПЕРЕД каждой записью, а не писать стартовый снимок. Волны
        # шли параллельно в разных процессах, и снимок, взятый при старте,
        # оказывался устаревшим: волна 2 на 400 шагах перезаписал файл своим
        # содержимым и стёрла записи волны 4 (H-K1, H-K2), появившиеся позже.
        merged = {_key(r): r for r in _read_runs()}
        for r in own:
            merged[_key(r)] = r
        payload["runs"] = sorted(
            merged.values(), key=lambda r: (int(r["steps"]), str(r["arm"]), int(r["seed"]))
        )
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    # Конфигурации, которые этот процесс перегенерирует, убираем из файла —
    # свежие траектории важнее старых по тому же ключу.
    regenerated = {(a, int(s), int(steps)) for a in arms for s in seeds}
    payload = {
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
        "collapse_threshold": threshold,
        "collapse_threshold_absolute": config.COLLAPSE_ALIVE_FRACTION_MIN,
        "collapse_threshold_ratio": config.COLLAPSE_ALIVE_FRACTION_RATIO,
        "target_pattern": config.TARGET_PATTERN,
        "target_density": target_density,
        "runs": [r for r in _read_runs() if _key(r) not in regenerated],
    }
    _write()

    for arm in arms:
        for seed in seeds:
            if do_reparse:
                # Ничего не обучаем: только перечитать существующий лог и
                # пересчитать производные метрики (см. reparse()).
                fresh = reparse(steps, [seed], [arm], threshold)
                if not fresh:
                    continue
                res = fresh[0]
            else:
                res = run_arm(arm, steps, seed, collapse_threshold=threshold)
            own.append(res)
            alive_min = res["alive_fraction_min"]
            print(
                f"[wp4] {arm:5s} seed={seed} "
                f"alive_min={'нет' if alive_min is None else f'{alive_min:.4f}'} "
                f"survived={res['survived']} vis {res['visible_mse_first']:.4f}->{res['visible_mse_final']:.4f} "
                f"ret={res['retention_mse_final'] if res['retention_enabled_by_overrides'] else 'выкл'} "
                f"| {res['description']}"
            )
            # NEG-21: если argmax f1 совпал с первой же точкой лога, этот прогон
            # ничего не сказал о ФОРМЕ — он измерил начальное состояние модели.
            # Без строки экран на 400 итерациях читается как вердикт по f1, и по
            # нему wave 9 закрыли бы «формы нет», хотя горизонт был негоден для
            # этого вопроса (у R-8 максимум f1 на 1250-й итерации).
            f1max_it = res.get("f1_max_iteration")
            first_it = res["trajectory"][0]["iteration"] if res["trajectory"] else None
            if f1max_it is not None and first_it is not None and f1max_it <= first_it:
                print(
                    f"[wp4] ВНИМАНИЕ {arm}/s{steps}: максимум f1={res['f1_max']:.4f} на it={f1max_it} "
                    f"(первая точка лога) — экран по форме неинформативен, f1 измеряет инициализацию; "
                    f"горизонт нужно увеличивать (ряд сравнения: R-8 argmax на it=1250)"
                )
            # Пишем инкрементально: прогон долгий, терять всё из-за одного arm'а нельзя.
            _write()
    print(f"[wp4] записано: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--seeds", type=str, default="42")
    parser.add_argument("--arms", type=str, default=",".join(DEFAULT_ARMS))
    parser.add_argument(
        "--reparse",
        action="store_true",
        help="не обучать: пересчитать записи из логов, лежащих в config.LOG_DIR",
    )
    args = parser.parse_args()
    main(
        steps=args.steps,
        seeds=[int(s) for s in args.seeds.split(",")],
        arms=[a.strip() for a in args.arms.split(",") if a.strip()],
        do_reparse=args.reparse,
    )
