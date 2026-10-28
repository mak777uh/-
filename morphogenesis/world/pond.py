"""«Пруд» — минимальная среда, в которой явлению есть где проявиться.

Зачем: в текущем стенде NCA рисует картинку на замкнутом поле: нет среды, цены,
размножения и отбора. Здесь добавляется ровно то, без чего организация не может
быть процессом:

- **ресурс** `resource` — возобновляемое поле (свет/питание), с катастрофами;
- **энергия** `energy` — доход из ресурса, плата за обновление и за ремонт, ноль →
  смерть;
- **повреждения** `damage` — накапливаются с шумом, ремонтируются за энергию; при
  переполнении клетка гибнет. Возраст — только диагностика, не причина смерти;
- **размножение** — компонент с достаточной массой и энергией выпускает **спору**
  (1–4 клетки в свободных соседних клетках), а не копию тела: потомок должен
  вырасти сам, и на это есть давление;
- **катастрофы** — периодическое падение ресурса, которое вымывает доминирующие
  линии и освобождает ниши.

Правило обновления состояния сюда не входит: оно передаётся снаружи (`rule_fn`),
чтобы мир тестировался без GPU и без обучения. Мир отвечает только за бюджет.

Инварианты (проверяются тестами):
1. энергия не появляется из ниоткуда — только из ресурса;
2. мёртвая клетка не тратит и не отдаёт энергию;
3. спора не занимает клетку родителя и появляется только при достаточной массе и
   энергии, причём энергия списывается у родителя;
4. повреждения накапливаются и убивают без участия возраста.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import torch


@dataclass
class PondConfig:
    """Параметры среды. Значения — стартовые, не «истина»."""

    grid: int = 64
    resource_max: float = 1.0
    resource_regen: float = 0.02      # сколько ресурса прибывает за шаг на клетку
    update_cost: float = 0.01         # цена одного обновления живой клетки
    baseline_income: float = 0.002    # доход клетки из ресурса за шаг
    budding_mass: float = 64          # сколько живых клеток нужно для споры
    budding_cost: float = 8.0         # энергия, которую платит родитель
    spore_cells: int = 2              # из скольких клеток стартует потомок
    damage_max: int = 50              # сколько повреждений выдерживает клетка
    damage_rate: float = 0.02         # вероятность получить повреждение за шаг
    repair_cost: float = 0.02         # энергия на ремонт (калибровка: 0.02 -> тело живёт ~500 шагов без роста)
    repair_rate: float = 0.5          # вероятность ремонта за шаг (если есть чем платить)
    max_age: int = 100_000            # диагностический предел, не причина смерти
    noise: float = 0.002              # шум в поле ресурса
    catastrophe_period: int = 0       # 0 — катастроф выключены
    catastrophe_duration: int = 50
    catastrophe_strength: float = 0.9
    catastrophe_mode: str = "shift"   # "shift" — ресурс переезжает, "drop" — падает везде
    catastrophe_rate: float = 0.0     # если > 0: катастрофы пуассоновские (событий на шаг)
    genome_dim: int = 32              # размер генома (для cNCA)
    resource_layout: str = "uniform"  # uniform | gradient | patches
    flip_at: int = 0                  # если > 0: на этом шаге градиент переворачивается
    drift_at: int = 0                  # если > 0: с этого шага градиент дрейфует
    drift_steps: int = 0               # за сколько шагов дрейф переворачивает верх и низ
    income_mode: str = "cap"           # cap (min(ресурс, доход)) | proportional (доход*ресурс)
    spore_bias: str = "random"         # random | rich | score | ifd | matching
    w_rich: float = 0.5                # вес ресурса в score (1-w — вес скученности)
    learn_w: bool = False              # учить w по судьбе потомства
    learn_rate: float = 0.1            # шаг обучения
    learn_delay: int = 10              # через сколько шагов проверять судьбу потомка
    learn_mode: str = "outcome"        # outcome | bandit | colony | paired
    learn_noise: float = 0.05          # разброс пробного веса потомка
    learn_pair_noise: float = 0.2      # δ в парном режиме: w' = w ± δ
    matching_temp: float = 1.0         # температура политики matching (1 = без неё)
    sense_noise: float = 0.0           # σ шума восприятия ресурса при выборе клетки
    mobility_cost: float = 0.0         # цена шага споры при расселении (0 = бесплатно)
    mobility_steps: int = 0            # сколько шагов спора может пройти (0 = подвижность выкл)
    organism_mobility_cost: float = 0.0    # цена шага организма по жизни (0 = выкл)
    organism_mobility_every: int = 10      # раз в сколько шагов организм пробует шаг
    plastic_eta: float = 0.0           # L2: скорость обновления предсказания ресурса
    plastic_move_cost: float = 0.05    # L2: цена шага по ошибке предсказания
    plastic_gate: str = "pred"         # pred | random: чем гейтится шаг
    plastic_prob: float = 0.5          # доля клеток за шаг при gate=random
    plastic_nomove: bool = False       # ablation: предсказание без перемещений
    invest_rate: float = 0.0           # B2: энергия на подъём ресурса в своей клетке
    invest_efficiency: float = 2.0     # B2: сколько ресурса даёт единица энергии
    invest_mode: str = "fixed"         # fixed | learn | none
    invest_threshold: float = 0.3      # порог ресурса для режима learn
    invest_eta: float = 0.02           # скорость адаптации порога у клетки
    invest_placebo: bool = False       # контроль: тратить энергию, но НЕ поднимать ресурс
    freq_dep: float = 0.0              # сила отрицательной частотной зависимости (0 = выкл)
    type_mode: str = "fixed"           # fixed | mixfixed | random | learn — тип A/B
    type_start: str = "a"              # a | b | mixed — тип стартовых клеток
    type_inherit: str = "neighbours"   # neighbours (voter) | parent (клональные пятна)
    type_level: str = "cell"           # cell | colony: тип у клетки или у всей колонии
    invade_at: int = 0                 # шаг инвазии редкого типа (0 = нет, I-032)
    invade_share: float = 0.05         # доля живых клеток, которым подменяют тип
    invade_type: int = 1               # какой тип подсаживаем: 0 = A, 1 = B
    invade_min_cells: int = 30         # ждать, пока колония не вырастет до N клеток
    invader_cells: int = 1             # доза основателя: сколько клеток ставит инъекция (colony)
    mutation_rate: float = 0.0         # 0..1: новый tag (метка линии) при рождении (условие B)
    ignition_gate: bool = False        # запретить правилу зажигать без живого 4-соседа (пропагул)
    trait_effect: float = 0.0          # eps: насколько tag_trait меняет интенсивность инвестирования (E)
    budding_unit: str = "colony"       # colony (W1) | cell (W2-bud): кто почкуется — колония или клетка
    niche_free_min: int = 0           # H-ALIVE-52: фильтр «свободная компонента >= N» (0 = без фильтра)
    pair_mode: str = "same_tag"        # H-ALIVE-49: same_tag (пара одной метки) | any_tag (любой сосед)
    death_return: float = 0.0          # W1-niche: доля взятого за жизнь ресурса, возвращаемая при смерти
    death_return_mode: str = "legacy"  # legacy (туда, где умерла) | prepared (в случайные СВОБОДНЫЕ) | depleted
    buds_per_component: int = 1        # W2-bud-d2: до N бутонов на компоненту (1 = W2-bud бит-в-бит)
    one_bud_per_lineage: bool = False  # не больше одного бутона на линию в компоненте
    quota_share: float = 1.0           # H-ALIVE-53: линия не может держать больше q живых клеток
                                       # (1.0 = выключено, бит-в-бит со старым миром)
    bud_refractory: int = 0            # H-ALIVE-54: линия не почкуется чаще, чем раз в K шагов
                                       # (0 = выключено, бит-в-бит со старым миром)
    kill_winner: float = 0.0            # H-ALIVE-54: смертность ∝ превышению доли линии над средней
                                        # (0 = выключено, бит-в-бит со старым миром)
    trait_effect_mode: str = "invest"   # H-ALIVE-56: invest (по умолчанию, бит-в-бит) | update
    inflow_coupling: float = 0.0        # H-ALIVE-59: сила связи с внешним потоком (0 = выключено)
    inflow_stream_mode: str = ""        # H-ALIVE-59: global | spatial
    require_placement: int = 0         # 0 = старая ветка бит-в-бит; >0 = гарантировать столько клеток
    placement_attempts: int = 5        # сколько раз перерисовывать точку, если пятно не встало
    mutation_trait_sigma: float = 0.01  # сдвиг признака линии при мутации (масштаб признака ~1)
    invade_placement: str = "random"   # random | gap: куда садится инокулят (V8)
    merge_rule: str = "majority"       # majority | mass_weighted: правило слияния компонент (V8)
    invade_on_empty: bool = False      # разрешить подсадку без резидента (плечо resident_free)
    learn_window: int = 30             # окно оценки для обучения колонии
    init_resource_fill: float = 0.0     # 0..1: доля потолка, до которой поле заполнено на старте
    membrane_gated: bool = False      # обмен гейтируется мембраной (замыкание)
    membrane_decay: float = 0.05      # распад мембраны за шаг
    membrane_rebuild: float = 0.10    # скорость восстановления мембраны
    membrane_rebuild_cost: float = 0.01  # энергия на единицу восстановления
    membrane_threshold: float = 0.2   # ниже этого порога притока нет


@dataclass
class PondState:
    """Состояние мира: ресурс, энергия, повреждения, возраст, маска живого."""

    resource: torch.Tensor            # (H, W)
    energy: torch.Tensor              # (H, W)
    damage: torch.Tensor              # (H, W) int64
    membrane: torch.Tensor            # (H, W) float, 0..1
    age: torch.Tensor                 # (H, W) int64
    alive: torch.Tensor               # (H, W) bool
    resource_b: torch.Tensor | None = None  # (H, W) ресурс второго типа (I-030)
    cell_type: torch.Tensor | None = None   # (H, W) int64: 0 = A, 1 = B
    tag: torch.Tensor | None = None         # (H, W) int64: метка линии (наследуемая)
    tag_trait: torch.Tensor | None = None   # (H, W) float: признак линии (наследуемый)
    pred: torch.Tensor | None = None    # (H, W) L2: предсказание локального ресурса
    w_cell: torch.Tensor | None = None  # (H, W) локальный вес политики (учится)
    step: int = 0
    born: int = 0
    died: int = 0
    spores_blocked: int = 0
    consumed_total: float = 0.0
    history: list[dict] = field(default_factory=list)
    deaths_by_zone: dict = field(default_factory=lambda: {"poor": 0, "mid": 0, "rich": 0})


class Pond:
    """Среда: ресурс, энергия, повреждения, смерть, споры, катастрофы."""

    def __init__(self, config: PondConfig | None = None, device: str | torch.device = "cpu",
                 seed: int = 0) -> None:
        self.cfg = config or PondConfig()
        self.device = torch.device(device)
        self.gen = torch.Generator(device=self.device).manual_seed(int(seed))
        # выборки в политиках (рулетка matching) идут с CPU-генератора: многоместный
        # multinomial на CUDA недетерминирован (atomic-суммы), из-за чего один и тот
        # же сид давал разные траектории (protocol §18a, I-017).
        self.gen_sel = torch.Generator(device="cpu").manual_seed(int(seed) * 7919 + 13)
        n = self.cfg.grid
        self._catastrophe_left = 0
        self.w = float(self.cfg.w_rich)
        self._pending: list[dict] = []
        self.learn_updates = 0
        self.learn_useless = 0   # парные уроки без сигнала (обе споры с одинаковой судьбой)
        self._pair_trials = 0    # номер парного испытания: чередуем знак w' = w ± δ
        self.mobility_moves = 0   # сколько шагов сделали споры (диагностика)
        self.mobility_shift = 0.0  # суммарное смещение спор от клетки выбора (шагов сетки)
        self.organism_moves = 0    # сколько шагов сделали организмы по жизни (I-023)
        self.plastic_shift = 0.0   # L2: сдвиг предсказания после переключения среды
        self.plastic_updates = 0
        self.invested_energy = 0.0
        self.invest_map: torch.Tensor | None = None
        self.thr_e: torch.Tensor | None = None
        self.invest_updates = 0
        self.thr_series: list[float] = []
        self.income_map: torch.Tensor | None = None
        self.income_scale: torch.Tensor | None = None   # H-ALIVE-59: множитель притока
        self.thr: torch.Tensor | None = None
        self.learn_history: list[float] = []
        self._colony_alive_prev = 0
        self._colony_dir = 1.0
        self._catastrophe_next = self._sample_gap()
        self.state = PondState(
            resource=torch.full((n, n), self.cfg.resource_max * 0.5, device=self.device),
            energy=torch.zeros((n, n), device=self.device),
            damage=torch.zeros((n, n), dtype=torch.int64, device=self.device),
            membrane=torch.zeros((n, n), device=self.device),
            age=torch.zeros((n, n), dtype=torch.int64, device=self.device),
            alive=torch.zeros((n, n), dtype=torch.bool, device=self.device),
        )
        if self.state.w_cell is None:
            self.state.w_cell = torch.full(
                (self.cfg.grid, self.cfg.grid), float(self.cfg.w_rich), device=self.device
            )
        if self.cfg.init_resource_fill > 0:
            fill = torch.full(
                (n, n),
                self.cfg.resource_max * self.cfg.init_resource_fill,
                device=self.device,
            )
            if self.cfg.resource_layout == "gradient":
                rows = torch.arange(n, device=self.device, dtype=torch.float32)
                position = 1.0 - rows / max(n - 1, 1)
                fill = fill * (0.2 + 0.8 * position)[:, None]
            elif self.cfg.resource_layout == "patches":
                third = n // 3
                rich = self.cfg.resource_max * self.cfg.init_resource_fill
                fill = fill * 0.2
                fill[third // 2 : third // 2 + third // 2, third // 2 : third // 2 + third // 2] = rich
                fill[n - third : n - third // 2, n - third : n - third // 2] = rich
                fill[third // 2 : third // 2 + third // 2, n - third : n - third // 2] = rich
            self.state.resource = fill

        # два типа ресурса и частотная зависимость (I-030)
        if self.cfg.plastic_eta > 0.0:
            self.state.pred = self.state.resource.clone()
        if self.cfg.freq_dep > 0.0 or self.cfg.type_mode != "fixed":
            self.state.resource_b = self.state.resource.clone()
            self.state.cell_type = torch.zeros((n, n), dtype=torch.int64, device=self.device)
        self.consumed_a = 0.0
        self.consumed_b = 0.0
        self.type_share_series: list[float] = []
        self.invasion_step = 0
        self.invasion_share_after = None
        self.colony_cells_at_invasion = 0
        self.injection_invalid = False
        self.injection_share_actual = None
        self.invader_cells_requested = 0   # запрошенная доза основателя (0 = не применимо)
        self.invader_cells_actual = 0      # сколько клеток реально подсажено (0 = нет инвазии)
        # время «родитель → деление» по каждому почкованию (в шагах): возраст родителя
        # на момент деления. Нужно, чтобы поколение было ИЗМЕРЕНО, а не оценено косвенно
        # (полураспад наследия 20–41 шаг сравнивается с поколением 125–206 в шагах).
        # Два списка: средний возраст клеток колонии и возраст самой старой клетки —
        # родитель здесь компонента, и одно число её «возраст» не описывает.
        self.division_parent_ages: list[int] = []
        self.division_oldest_ages: list[int] = []
        # метки линий (условие B): tag наследуется, мутация даёт НОВЫЙ tag с признаком
        # tag_trait = признак родителя + шум. Пул A/B и вся динамика от метки не зависят,
        # поэтому m=0 — бит-в-бит прежнее, а новизна (новые метки) измерима при m>0.
        self.state.tag = torch.zeros((n, n), dtype=torch.int64, device=self.device)
        self.state.tag_trait = torch.zeros((n, n), device=self.device)
        self.next_tag = 1
        self.mutation_events = 0
        self.tag_born_at: dict[int, int] = {0: 0}
        self.generation_depth: dict[int, int] = {0: 0}   # сколько делений от основателя
        self.lineage_offspring: dict[int, int] = {0: 0}     # потомков, приписанных линии (tag)
        self.lineage_spores: dict[int, int] = {0: 0}        # СПОР линии (единица размножения, условие E)
        self.lineage_invested: dict[int, float] = {0: 0.0}  # вложенная линией энергия (манипуляционная проверка)
        # сколько РАЗ клетки линии инвестировали (не зависит от энергии): чистая проверка
        # «мир читает признак» — вложение/клетку смешивало накопленное с текущим (§10ap)
        self.lineage_invest_updates: dict[int, int] = {0: 0}
        # клетко-шаги линии: интеграл живых клеток по времени. Нужен, чтобы нормировать
        # НАКОПЛЕННОЕ вложение (оно копится весь прогон) на время жизни линии, а не на
        # число клеток в конце (§10ap: накопленное/текущее — сравнение разного).
        self.lineage_cell_steps: dict[int, int] = {0: 0}
        # V1c: диагностика подсадки (заполняется только при require_placement > 0)
        # W1-niche: возврат ресурса при смерти и статистика «подготовленных» клеток
        self.resource_taken = torch.zeros((self.cfg.grid, self.cfg.grid), device=self.device)
        self.returned_total = 0.0
        self.resource_at_death: list[float] = []
        self.niche_log: list[dict] = []
        self.niche_expected = 0.0
        self.niche_hit_same = 0
        self.niche_hit_any = 0
        self.niche_levels: dict[int, list[int]] = {}   # n4 -> [prepared, hit_same]
        self.death_log: list[tuple[int, int, int]] = []   # (y, x, tag) для плеча foreign
        self.pair_degenerate = 0                          # H-ALIVE-48: пара выродилась в одну клетку
        self.free_cells_at_injection: int | None = None
        self.max_free_component_at_injection: int | None = None
        self.placement_attempts_used: int | None = None
        self.rejected_by_placement: bool = False
        # ЭНЕРГО-ШАГИ линии (H-ALIVE-33): суммарная энергия живых клеток по шагам.
        # Нужно, чтобы отделить «цену признака» от «бедности линии»: вложение клетки =
        # rate(признак)·энергия, поэтому без энергии цена неотличима от бедности (§10aq).
        self.lineage_energy_steps: dict[int, float] = {0: 0.0}
        # energy_per_cell_time (H-ALIVE-34): сумма средних энергий линии по РАВНОМЕРНОЙ сетке
        # времени (каждые 10 шагов) и число сэмплов. Знаменатель — сэмплы, а не клетко-шаги,
        # иначе малоклеточные линии механически получают завышенное среднее (§10ar).
        self.lineage_energy_mean_sum: dict[int, float] = {0: 0.0}
        self.lineage_energy_samples: dict[int, int] = {0: 0}
        self.tag_trait_of: dict[int, float] = {0: 0.0}
        self.births_by_type: dict[str, int] = {}
        self.deaths_by_type: dict[str, int] = {}
        self.type_counts_series: list[dict] = []
        self._logged_births: dict[str, int] = {}
        self._logged_deaths: dict[str, int] = {}
        self._logged_mutations = 0

    # ---------- ресурс и катастрофы ----------
    def _sample_gap(self) -> int:
        """Интервал до следующей катастрофы (пуассоновский режим)."""
        rate = self.cfg.catastrophe_rate
        if rate <= 0.0:
            return 10**9
        import math
        u = max(float(torch.rand((), generator=self.gen, device=self.device)), 1e-9)
        return max(1, int(-math.log(u) / rate))
    def in_catastrophe(self) -> bool:
        cfg = self.cfg
        if cfg.catastrophe_rate > 0.0:
            # пуассоновский режим: длительность задаётся catastrophe_duration,
            # начало события — экспоненциальные интервалы
            return self._catastrophe_left > 0
        if cfg.catastrophe_period <= 0:
            return False
        return (self.state.step % cfg.catastrophe_period) < cfg.catastrophe_duration

    def _invade(self) -> None:
        """Подсадить редкий тип; при маленькой колонии ждём следующего шага."""
        s = self.state
        ct = s.cell_type
        if ct is None:
            return
        if not bool(s.alive.any()):
            # плечо resident_free: поле без резидента, инокулят основывает колонию
            if getattr(self.cfg, "invade_on_empty", False) and \
                    getattr(self.cfg, "type_level", "cell") == "colony":
                self._place_invader_colony()
            return
        cells_now = int(s.alive.sum())
        resident_share = float((ct[s.alive] == int(self.cfg.invade_type)).float().mean())
        if resident_share >= 0.25:
            # «редкий» тип уже не редок: это не инвазия, а смена метки у большинства
            self.injection_invalid = True
            self.colony_cells_at_invasion = cells_now
            self.injection_share_actual = round(resident_share, 4)
            return
        if cells_now < int(self.cfg.invade_min_cells):
            # ещё рано: при крошечной колонии доля одной подсаженной клетки нестабильна
            return
        if (getattr(self.cfg, "type_level", "cell") == "colony"
                and getattr(self.cfg, "type_mode", "") != "random"):
            # инвазия = НОВАЯ редкая колония: `invader_cells` клеток в случайной свободной
            # точке, иначе в одной слипшейся колонии «редкой» колонии просто нет
            # (в серии 24.10 это 1 клетка при колонии 382-700 -> доля 0.14-0.25%).
            # Доза > 1 ставится СВЯЗНЫМ 4-пятном: при типе на компоненте N независимых
            # клеток дали бы N колоний по одной клетке, то есть дозу 1, и параметр
            # ничего бы не измерял (B-037/H73 — эффект основателя).
            spot = self._invader_spot()
            if spot is None:
                return
            # запомнить ФАКТИЧЕСКУЮ точку подсадки для ресурса в трёх зонах (§10ak):
            # именно этот вызов, а не отдельный — иначе лишний вызов _invader_spot()
            # сдвигает ГПСЧ и старый якорь перестаёт совпадать бит-в-бит
            self._last_invasion_spot = spot
            s.alive |= spot
            s.energy = torch.where(spot, torch.full_like(s.energy, 8.0), s.energy)
            s.age = torch.where(spot, torch.zeros_like(s.age), s.age)
            s.damage = torch.where(spot, torch.zeros_like(s.damage), s.damage)
            s.cell_type[spot] = int(self.cfg.invade_type)
            self.invasion_share_after = round(
                float((s.cell_type[s.alive] == int(self.cfg.invade_type)).float().mean()), 4
            )
            self.invasion_step = int(s.step)
            self.colony_cells_at_invasion = int(s.alive.sum())
            self.injection_share_actual = round(
                float((s.cell_type[s.alive] == int(self.cfg.invade_type)).float().mean()), 4
            )
            # V1c: сколько клеток инвайдера реально в СОСТОЯНИИ сразу после подсадки
            self.invader_cells_state_after_injection = int(
                ((s.cell_type == int(self.cfg.invade_type)) & s.alive).sum()
            )
            self.injection_invalid = bool(self.injection_share_actual > 0.25)
            return
        idx = s.alive.nonzero(as_tuple=False)
        k = max(1, int(round(float(self.cfg.invade_share) * idx.shape[0])))
        perm = torch.randperm(idx.shape[0], generator=self.gen_sel)[:k].to(self.device)
        chosen = idx[perm]
        ct[chosen[:, 0], chosen[:, 1]] = int(self.cfg.invade_type)
        self.invasion_share_after = round(
            float((ct[s.alive] == int(self.cfg.invade_type)).float().mean()), 4
        )
        self.invasion_step = int(s.step)
        self.colony_cells_at_invasion = int(s.alive.sum())
        self.injection_share_actual = self.invasion_share_after
        self.injection_invalid = bool(self.injection_share_actual > 0.25)
        # подсадка по доле клеток: доза основателя здесь не применима, но число
        # подсаженных клеток в summary полезно
        self.invader_cells_requested = 0
        self.invader_cells_actual = int(k)

    def _farthest_free_cell(self, alive: torch.Tensor) -> tuple[int, int] | None:
        """Свободная клетка, максимально далёкая от живых (4-расстояние).

        Плечо `into_gap` (V8): при случайной точке инокулят почти всегда ложится вплотную
        к резиденту и переписывается правилом большинства на шаге подсадки (§10ac);
        здесь пятно получает фору по расстоянию. Считается волной от живых клеток —
        сетка 32x32, дороже одной инвазии это не делает.
        """
        s = self.state
        n = int(alive.shape[0])
        free = ~alive
        if not bool(free.any()):
            return None
        if not bool(alive.any()):
            ys, xs = free.nonzero(as_tuple=True)
            pick = int(torch.randint(0, ys.numel(), (), generator=self.gen_sel))
            return int(ys[pick]), int(xs[pick])
        dist = torch.zeros((n, n), dtype=torch.int64, device=self.device)
        reached = alive.clone()
        frontier = alive.clone()
        d = 0
        while bool(frontier.any()) and d < n * 2:
            d += 1
            grow = torch.zeros_like(frontier)
            grow[1:, :] |= frontier[:-1, :]
            grow[:-1, :] |= frontier[1:, :]
            grow[:, 1:] |= frontier[:, :-1]
            grow[:, :-1] |= frontier[:, 1:]
            frontier = grow & ~reached & free
            dist[frontier] = d
            reached |= frontier
        far = free & (dist == dist[free].max()) if bool(free.any()) else None
        if far is None or not bool(far.any()):
            return None
        ys, xs = far.nonzero(as_tuple=True)
        pick = int(torch.randint(0, ys.numel(), (), generator=self.gen_sel))
        return int(ys[pick]), int(xs[pick])

    def _free_component_stats(self) -> tuple[int, int, torch.Tensor, dict[int, int]]:
        """Свободное место при инъекции: (свободно всего, максимальная свободная компонента)."""
        s = self.state
        free = ~s.alive
        free_total = int(free.sum())
        sizes, labels = self._components(free)
        max_comp = max(sizes.values()) if sizes else 0
        return free_total, int(max_comp), labels, sizes

    def _invader_spot_guaranteed(self) -> torch.Tensor | None:
        """Подсадка с гарантией размера (V1c): точка только там, где свободная компонента
        вмещает `require_placement` клеток; до `placement_attempts` перерисовок RNG.

        Старая ветка (`require_placement = 0`) не затрагивается — она остаётся бит-в-бит.
        """
        s = self.state
        want = int(max(1, getattr(self.cfg, "invader_cells", 1)))
        need = int(getattr(self.cfg, "require_placement", 0))
        attempts = int(getattr(self.cfg, "placement_attempts", 5))
        free_total, max_comp, labels, sizes = self._free_component_stats()
        self.free_cells_at_injection = free_total
        self.max_free_component_at_injection = max_comp
        eligible = [cid for cid, size in sizes.items() if size >= max(need, want)]
        self.placement_attempts_used = 0
        if not eligible:
            self.rejected_by_placement = True
            self.invader_cells_actual = 0
            return None
        for attempt in range(1, attempts + 1):
            self.placement_attempts_used = attempt
            cid = eligible[int(torch.randint(0, len(eligible), (), generator=self.gen_sel))]
            cells = (labels == cid).nonzero(as_tuple=False)
            pick = cells[int(torch.randint(0, cells.shape[0], (), generator=self.gen_sel))]
            spot = torch.zeros_like(s.alive)
            spot[int(pick[0]), int(pick[1])] = True
            if want > 1:
                spot = self._grow_invader_blob(spot, s.alive, want)
            if int(spot.sum()) >= need:
                self.invader_cells_actual = int(spot.sum())
                self.rejected_by_placement = False
                return spot
        self.rejected_by_placement = True
        self.invader_cells_actual = 0
        return None

    def _invader_spot(self) -> torch.Tensor | None:
        """Где ставить инокулят: точка по `invade_placement` + связное пятно `invader_cells`."""
        s = self.state
        self.invader_cells_requested = int(max(1, getattr(self.cfg, "invader_cells", 1)))
        if int(getattr(self.cfg, "require_placement", 0)) > 0:
            return self._invader_spot_guaranteed()
        placement = getattr(self.cfg, "invade_placement", "random")
        if placement == "gap":
            cell = self._farthest_free_cell(s.alive)
        else:
            free = (~s.alive).nonzero(as_tuple=False)
            cell = None
            if free.shape[0] > 0:
                pick = free[int(torch.randint(0, free.shape[0], (), generator=self.gen_sel))]
                cell = (int(pick[0]), int(pick[1]))
        if cell is None:
            return None
        y, x = cell
        spot = torch.zeros_like(s.alive)
        spot[y, x] = True
        if self.invader_cells_requested > 1:
            spot = self._grow_invader_blob(spot, s.alive, self.invader_cells_requested)
        self.invader_cells_actual = int(spot.sum())
        return spot

    def _place_invader_colony(self) -> None:
        """Основывать колонию на пустом поле (плечо `resident_free`)."""
        s = self.state
        spot = self._invader_spot()
        if spot is None:
            return
        s.alive |= spot
        s.energy = torch.where(spot, torch.full_like(s.energy, 8.0), s.energy)
        s.age = torch.where(spot, torch.zeros_like(s.age), s.age)
        s.damage = torch.where(spot, torch.zeros_like(s.damage), s.damage)
        s.cell_type[spot] = int(self.cfg.invade_type)
        self.invasion_share_after = 1.0
        self.invasion_step = int(s.step)
        self.colony_cells_at_invasion = int(s.alive.sum())
        self.injection_share_actual = 1.0
        self.injection_invalid = True   # это не инвазия в колонию, а основание своей

    def _grow_invader_blob(self, spot: torch.Tensor, alive: torch.Tensor,
                           want: int) -> torch.Tensor:
        """Дорастить инокулят до `want` клеток, оставаясь одной 4-компонентой.

        Фронт — свободные 4-соседи уже занятых клеток инокулята; следующая клетка
        выбирается случайно (`gen_sel`), поэтому форма пятна случайна, но связность
        гарантирует, что это одна колония (иначе при типе на компоненте N клеток
        распались бы на N колоний по одной клетке). Если свободных клеток меньше,
        пятно получается меньше `want` — фактический размер пишется в
        `invader_cells_actual`.
        """
        n = int(alive.shape[0])
        frontier: list[tuple[int, int]] = []
        queued: set[tuple[int, int]] = set()

        def push_neighbours(y: int, x: int) -> None:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if not (0 <= ny < n and 0 <= nx < n) or (ny, nx) in queued:
                    continue
                if bool(spot[ny, nx]) or bool(alive[ny, nx]):
                    continue
                queued.add((ny, nx))
                frontier.append((ny, nx))

        ys, xs = spot.nonzero(as_tuple=True)
        for y, x in zip(ys.tolist(), xs.tolist()):
            push_neighbours(int(y), int(x))
        total = int(spot.sum())
        while total < want and frontier:
            k = int(torch.randint(0, len(frontier), (), generator=self.gen_sel))
            y, x = frontier[k]
            frontier[k] = frontier[-1]
            frontier.pop()
            queued.discard((y, x))
            spot[y, x] = True
            total += 1
            push_neighbours(y, x)
        return spot

    def _gradient_position(self) -> torch.Tensor:
        """Положение потолка градиента по строкам: 1.0 = верх (богато), 0.0 = низ.

        Три режима, из которых берётся первый подходящий:
        - плавный дрейф (`drift_at`, `drift_steps` > 0): линейная перестановка
          верха и низа за `drift_steps` шагов начиная с `drift_at`;
        - резкий переворот (`flip_at`): верх и низ меняются местами за один шаг;
        - без изменений: верх остаётся верхом.
        """
        cfg = self.cfg
        rows = torch.arange(cfg.grid, device=self.device, dtype=torch.float32)
        up = 1.0 - rows / max(cfg.grid - 1, 1)
        if cfg.drift_at and cfg.drift_steps and cfg.drift_steps > 0:
            progress = (float(self.state.step) - float(cfg.drift_at)) / float(cfg.drift_steps)
            progress = min(1.0, max(0.0, progress))
            return (1.0 - progress) * up + progress * (1.0 - up)
        if cfg.flip_at and self.state.step >= cfg.flip_at:
            return 1.0 - up
        return up

    def regenerate(self) -> None:
        """Ресурс прибывает с ограниченной скоростью; в катастрофу — падает."""
        cfg = self.cfg
        if cfg.catastrophe_rate > 0.0:
            if self._catastrophe_left > 0:
                self._catastrophe_left -= 1
            else:
                self._catastrophe_next -= 1
                if self._catastrophe_next <= 0:
                    self._catastrophe_left = cfg.catastrophe_duration
                    self._catastrophe_next = self._sample_gap()
        if self.in_catastrophe():
            if cfg.catastrophe_mode == "shift":
                # ресурс не исчезает, а переезжает: левая половина гаснет, правая
                # наполняется — давление на миграцию, а не на накопление
                half = cfg.grid // 2
                self.state.resource[:, :half] = 0.0
                self.state.resource[:, half:] = cfg.resource_max
                # второй тип ресурса переезжает так же (task-12)
                if self.state.resource_b is not None:
                    self.state.resource_b[:, :half] = 0.0
                    self.state.resource_b[:, half:] = cfg.resource_max
            else:
                self.state.resource = self.state.resource * (1.0 - cfg.catastrophe_strength)
            return
        noise = torch.randn(
            (cfg.grid, cfg.grid), generator=self.gen, device=self.device
        ) * cfg.noise
        inflow = torch.full((cfg.grid, cfg.grid), cfg.resource_regen, device=self.device)
        if cfg.resource_layout == "gradient":
            # «свет» сверху: верх богат, низ беден
            rows = torch.arange(cfg.grid, device=self.device, dtype=torch.float32)
            inflow = inflow * (0.1 + 0.9 * (1.0 - rows / max(cfg.grid - 1, 1)))[:, None]
        elif cfg.resource_layout == "patches":
            # три источника, остальное бедно
            base = torch.full((cfg.grid, cfg.grid), cfg.resource_regen * 0.1, device=self.device)
            third = cfg.grid // 3
            base[third // 2 : third // 2 + third // 2, third // 2 : third // 2 + third // 2] = cfg.resource_regen * 4
            base[cfg.grid - third : cfg.grid - third // 2, cfg.grid - third : cfg.grid - third // 2] = cfg.resource_regen * 4
            base[third // 2 : third // 2 + third // 2, cfg.grid - third : cfg.grid - third // 2] = cfg.resource_regen * 4
            inflow = base
        # потолок зависит от раскладки: иначе ресурс насыщается везде одинаково
        ceiling = torch.full((cfg.grid, cfg.grid), cfg.resource_max, device=self.device)
        if cfg.resource_layout == "gradient":
            position = self._gradient_position()
            ceiling = ceiling * (0.2 + 0.8 * position)[:, None]
        elif cfg.resource_layout == "patches":
            ceiling = torch.full((cfg.grid, cfg.grid), cfg.resource_max * 0.2, device=self.device)
            third = cfg.grid // 3
            ceiling[third // 2 : third // 2 + third // 2, third // 2 : third // 2 + third // 2] = cfg.resource_max
            ceiling[cfg.grid - third : cfg.grid - third // 2, cfg.grid - third : cfg.grid - third // 2] = cfg.resource_max
            ceiling[third // 2 : third // 2 + third // 2, cfg.grid - third : cfg.grid - third // 2] = cfg.resource_max
        self.state.resource = torch.minimum(
            torch.clamp(self.state.resource + inflow + noise, min=0.0), ceiling
        )
        # второй тип ресурса: отрицательная частотная зависимость (I-030).
        # Тип, который едят больше, восстанавливается медленнее; недоедаемый — быстрее.
        if self.state.resource_b is not None:
            total = self.consumed_a + self.consumed_b
            share_a = self.consumed_a / total if total > 1e-9 else 0.5
            share_b = 1.0 - share_a
            fd = float(cfg.freq_dep)
            fa = min(1.0 + fd, max(0.0, 1.0 - fd * (2.0 * share_a - 1.0)))
            fb = min(1.0 + fd, max(0.0, 1.0 - fd * (2.0 * share_b - 1.0)))
            noise_b = torch.randn(
                (cfg.grid, cfg.grid), generator=self.gen, device=self.device
            ) * cfg.noise
            self.state.resource_b = torch.minimum(
                torch.clamp(self.state.resource_b + inflow * fb + noise_b, min=0.0), ceiling
            )
            self.state.resource = torch.minimum(
                torch.clamp(self.state.resource + inflow * (fa - 1.0), min=0.0), ceiling
            )

    # ---------- жизнь клеток ----------
    def seed_life(self, mask: torch.Tensor, energy: float = 5.0) -> None:
        """Поселить жизнь: энергия появляется только вместе с зарядом."""
        mask = mask.to(self.device).bool()
        if self.state.cell_type is not None:
            if self.cfg.type_start == "mixed":
                draw = torch.randint(0, 2, (int(mask.sum()),), generator=self.gen_sel)
                self.state.cell_type[mask] = draw.to(self.device)
            elif self.cfg.type_start == "b":
                self.state.cell_type[mask] = 1
        self.state.alive |= mask
        self.state.energy = torch.where(
            mask, torch.full_like(self.state.energy, energy), self.state.energy
        )
        self.state.age = torch.where(mask, torch.zeros_like(self.state.age), self.state.age)
        self.state.damage = torch.where(
            mask, torch.zeros_like(self.state.damage), self.state.damage
        )
        self.state.membrane = torch.where(
            mask, torch.ones_like(self.state.membrane), self.state.membrane
        )

    def _kill_winner_step(self) -> None:
        """H-ALIVE-54: смертность пропорциональна превышению доли линии над средней.

        Зачем именно так, а не квотой: два предыдущих рычага (`quota_share`, `bud_refractory`)
        блокировали ПОЧКОВАНИЕ, а новые метки рождаются только на бутоне, поэтому оба УМЕНЬШАЛИ
        число линий (5 → 1). Здесь размножение не трогается: штрафуется только доля, то есть
        «победитель». При `kill_winner = 0` — ранний выход без обращения к генератору, поэтому
        старый мир остаётся бит-в-бит.
        """
        k = float(getattr(self.cfg, "kill_winner", 0.0) or 0.0)
        if k <= 0.0:
            return
        s = self.state
        if s.tag is None:
            return
        alive = s.alive
        n = int(alive.sum())
        if n <= 0:
            return
        tags = s.tag[alive]
        uniq, cnt = torch.unique(tags, return_counts=True)
        n_lines = int(uniq.numel())
        if n_lines < 2:
            return
        mean_share = 1.0 / float(n_lines)
        killed = 0
        for val, c in zip(uniq.tolist(), cnt.tolist()):
            share = float(c) / float(n)
            excess = share - mean_share
            if excess <= 0:
                continue
            want = int(k * excess * float(n))
            if want <= 0:
                continue
            mask = alive & (s.tag == int(val))
            idx = mask.nonzero(as_tuple=False)
            if idx.shape[0] == 0:
                continue
            take = min(want, int(idx.shape[0]))
            perm = torch.randperm(idx.shape[0], generator=self.gen_sel)[:take]
            pick = idx[perm]
            kill_mask = torch.zeros_like(alive)
            kill_mask[pick[:, 0], pick[:, 1]] = True
            s.energy = torch.where(kill_mask, torch.zeros_like(s.energy), s.energy)
            s.alive = s.alive & ~kill_mask
            killed += take
        if killed:
            self.killed_by_kill_winner = int(getattr(self, "killed_by_kill_winner", 0)) + killed
            s.died += killed

    def step_cells(self) -> dict:
        """Один шаг бюджета: доход, плата, ремонт, повреждения, смерть."""
        cfg = self.cfg
        s = self.state
        alive = s.alive

        # клетка ест ресурс СВОЕГО типа (I-030); без двух типов — единственное поле
        if s.resource_b is not None and s.cell_type is not None:
            is_b = s.cell_type == 1
            own = torch.where(is_b, s.resource_b, s.resource)
        else:
            is_b = None
            own = s.resource
        if getattr(s, "income_scale", None) is not None:
            # H-ALIVE-59: внешний поток масштабирует приток ПО КЛЕТКАМ; при множителе 1.0
            # умножение на единицу не меняет ни одного бита (якорь проверяется отдельно).
            own = own * s.income_scale
        if cfg.income_mode == "proportional":
            # доход пропорционален доступному ресурсу: бедная зона реально голодает
            income = torch.minimum(
                own, cfg.baseline_income * own * 4.0
            )
        else:
            income = torch.minimum(own, torch.full_like(own, cfg.baseline_income))
        if cfg.membrane_gated:
            # обмен возможен только там, где есть мембрана: её производит организм
            gate = (s.membrane >= cfg.membrane_threshold).to(income.dtype)
            income = income * gate
        income = torch.where(alive, income, torch.zeros_like(income))
        if is_b is None:
            s.resource = s.resource - income
        else:
            s.resource = s.resource - torch.where(is_b, torch.zeros_like(income), income)
            s.resource_b = s.resource_b - torch.where(is_b, income, torch.zeros_like(income))
            # мгновенное потребление по типам со сглаживанием (EMA): кумулятивный
            # итог давал медленную обратную связь, и доля уезжала к одному типу
            eat_a = float(torch.where(is_b, torch.zeros_like(income), income).sum())
            eat_b = float(torch.where(is_b, income, torch.zeros_like(income)).sum())
            beta = 0.1
            self.consumed_a = (1.0 - beta) * self.consumed_a + beta * eat_a
            self.consumed_b = (1.0 - beta) * self.consumed_b + beta * eat_b
        s.energy = s.energy + income
        self.state.consumed_total += float(income.sum())
        if self.cfg.death_return > 0:
            # W1-niche: сколько ресурса клетка взяла за жизнь — это и возвращается при смерти
            # (остаточную ЭНЕРГИЮ возвращать нельзя: клетка умирает при energy <= 0)
            self.resource_taken = self.resource_taken + income

        spent = cfg.update_cost + cfg.repair_cost
        s.energy = torch.where(alive, s.energy - spent, s.energy)
        if s.tag is not None and bool(alive.any()):
            uniq_a, inv_a = torch.unique(s.tag[alive], return_inverse=True)
            cnt = torch.zeros(uniq_a.numel(), device=self.device, dtype=torch.long)
            cnt.index_add_(0, inv_a.view(-1), torch.ones_like(inv_a, dtype=torch.long).view(-1))
            esum = torch.zeros(uniq_a.numel(), device=self.device, dtype=torch.float32)
            esum.index_add_(0, inv_a.view(-1), s.energy[alive].float().view(-1))
            for tag_val, c, e in zip(uniq_a.tolist(), cnt.tolist(), esum.tolist()):
                self.lineage_cell_steps[int(tag_val)] = (
                    self.lineage_cell_steps.get(int(tag_val), 0) + int(c))
                self.lineage_energy_steps[int(tag_val)] = (
                    self.lineage_energy_steps.get(int(tag_val), 0.0) + float(e))
            # сэмпл «средняя энергия клетки линии» на равномерной сетке (каждые 10 шагов)
            if int(s.step) % 10 == 0:
                emean = torch.zeros(uniq_a.numel(), device=self.device, dtype=torch.float32)
                emean.index_add_(0, inv_a.view(-1), s.energy[alive].float().view(-1))
                cnt_f = cnt.float().clamp_min(1.0)
                emean = emean / cnt_f
                for tag_val, m in zip(uniq_a.tolist(), emean.tolist()):
                    self.lineage_energy_mean_sum[int(tag_val)] = (
                        self.lineage_energy_mean_sum.get(int(tag_val), 0.0) + float(m))
                    self.lineage_energy_samples[int(tag_val)] = (
                        self.lineage_energy_samples.get(int(tag_val), 0) + 1)

        # B2: ниша — клетка поднимает ресурс в СВОЕЙ клетке за энергию
        if cfg.invest_rate > 0.0:
            if self.thr is None:
                self.thr = s.resource.clone()
            self.thr = self.thr + cfg.invest_eta * (s.resource - self.thr)
            if self.thr_e is None:
                self.thr_e = s.energy.clone()
            self.thr_e = self.thr_e + cfg.invest_eta * (s.energy - self.thr_e)
            if cfg.invest_mode == "surplus":
                # кандидат в обучение: инвестировать только при излишке энергии
                want = alive & (s.energy > self.thr_e)
            elif cfg.invest_mode == "fixed":
                want = alive
            elif cfg.invest_mode == "learn":
                want = alive & (s.resource < self.thr * 0.8)
            else:
                want = torch.zeros_like(alive)
            rate = torch.full_like(s.energy, float(cfg.invest_rate))
            eps = float(getattr(cfg, "trait_effect", 0.0))
            mode = str(getattr(cfg, "trait_effect_mode", "invest"))
            if eps != 0.0 and mode == "update":
                # H-ALIVE-56: в этом режиме признак читается в асинхронности (run_pond.step),
                # а инвестирование остаётся ровным — иначе каналы смешались бы.
                eps = 0.0
            if eps != 0.0 and s.tag_trait is not None:
                # E: признак линии читается миром — интенсивность инвестирования масштабируется
                # (выше признак → больше поднимает потолок, но и больше тратит: trade-off)
                mean_trait = float(s.tag_trait[alive].mean()) if bool(alive.any()) else 0.0
                factor = torch.clamp(1.0 + eps * (s.tag_trait - mean_trait), 0.5, 2.0)
                rate = rate * factor
            spend = torch.where(want, torch.minimum(s.energy.clamp_min(0.0), rate),
                                torch.zeros_like(s.energy))
            if s.tag is not None and float(spend.sum()) > 0.0:
                # манипуляционная проверка: сколько вложила каждая линия
                uniq, inverse = torch.unique(s.tag, return_inverse=True)
                sums = torch.zeros(uniq.numel(), device=self.device, dtype=spend.dtype)
                sums.index_add_(0, inverse.view(-1), spend.view(-1))
                for tag_val, total in zip(uniq.tolist(), sums.tolist()):
                    if total > 0.0:
                        self.lineage_invested[int(tag_val)] = (
                            self.lineage_invested.get(int(tag_val), 0.0) + float(total))
                # число инвестиционных событий по линиям (энергонезависимая проверка)
                events = torch.zeros(uniq.numel(), device=self.device, dtype=torch.long)
                events.index_add_(0, inverse.view(-1), (spend > 1e-9).long().view(-1))
                for tag_val, cnt in zip(uniq.tolist(), events.tolist()):
                    if cnt > 0:
                        self.lineage_invest_updates[int(tag_val)] = (
                            self.lineage_invest_updates.get(int(tag_val), 0) + int(cnt))
            s.energy = s.energy - spend
            if self.invest_map is None or self.invest_map.shape != spend.shape:
                self.invest_map = torch.zeros_like(spend)
                self.income_map = torch.zeros_like(spend)
            self.invest_map = self.invest_map + spend
            self.income_map = self.income_map + income
            gain = spend * cfg.invest_efficiency
            if cfg.invest_placebo:
                gain = torch.zeros_like(gain)
            s.resource = torch.minimum(s.resource + gain, torch.full_like(s.resource, cfg.resource_max))
            self.invested_energy += float(spend.sum())
            self.invest_updates += int((spend > 1e-9).sum())
            if int(s.step) % 20 == 0 and bool(alive.any()):
                self.thr_series.append(round(float(self.thr_e[alive].mean()), 4))

        # мембрана: распад и восстановление за энергию — только в режиме замыкания
        if cfg.membrane_gated:
          s.membrane = torch.clamp(s.membrane - cfg.membrane_decay, 0.0, 1.0)
          if cfg.membrane_rebuild > 0.0:
            need = torch.clamp(1.0 - s.membrane, 0.0, 1.0) * cfg.membrane_rebuild
            cost = need * cfg.membrane_rebuild_cost
            afford = (s.energy > cost) & alive
            s.energy = torch.where(afford, s.energy - cost, s.energy)
            s.membrane = torch.where(afford, torch.clamp(s.membrane + need, 0.0, 1.0), s.membrane)

        # повреждения: шум попадает с вероятностью damage_rate, ремонт их гасит
        hits = (torch.rand((cfg.grid, cfg.grid), generator=self.gen, device=self.device)
                < cfg.damage_rate) & alive
        s.damage = s.damage + hits.to(s.damage.dtype)
        repair_roll = torch.rand((cfg.grid, cfg.grid), generator=self.gen, device=self.device)
        repaired = (
            alive
            & (s.damage > 0)
            & (cfg.repair_cost > 0.0)
            & (s.energy > spent)
            & (repair_roll < cfg.repair_rate)
        )
        s.damage = torch.where(repaired, s.damage - 1, s.damage)

        s.age = torch.where(alive, s.age + 1, s.age)
        dies = alive & ((s.energy <= 0.0) | (s.damage >= cfg.damage_max) | (s.age > cfg.max_age))
        died_now = int(dies.sum())
        if s.tag is not None and died_now and bool(dies.any()):
            uniq, counts = torch.unique(s.tag[dies], return_counts=True)
            for val, cnt in zip(uniq.tolist(), counts.tolist()):
                key = f"T{int(val)}"
                self.deaths_by_type[key] = self.deaths_by_type.get(key, 0) + int(cnt)
        # зоны по ресурсу в момент решения: где именно умирают клетки
        if cfg.resource_max > 0 and died_now:
            rich = s.resource > cfg.resource_max * 2 / 3
            poor = s.resource < cfg.resource_max / 3
            mid = ~rich & ~poor
            for name, zone in (("poor", poor), ("mid", mid), ("rich", rich)):
                s.deaths_by_zone[name] += int((dies & zone).sum())
        if cfg.death_return > 0 and died_now:
            self._return_on_death(dies)
        s.energy = torch.where(dies, torch.zeros_like(s.energy), s.energy)
        s.alive = alive & ~dies
        s.died += died_now
        self._kill_winner_step()
        if cfg.learn_w and self._pending:
            still = []
            for entry in self._pending:
                if s.step - entry["born_step"] < cfg.learn_delay:
                    still.append(entry)
                    continue
                if entry.get("pair"):
                    # относительный сигнал: сравниваем две споры одного рождения.
                    # Если судьба одинаковая (обе живы/обе мертвы) — сигнала нет,
                    # такой урок не тратится на сдвиг веса (иначе это шум).
                    alive_a = bool((s.alive & entry["mask_a"]).any())
                    alive_b = bool((s.alive & entry["mask_b"]).any())
                    if alive_a != alive_b:
                        winner = entry["w_a"] if alive_a else entry["w_b"]
                        self.w = min(1.0, max(0.0, self.w + cfg.learn_rate * (winner - self.w)))
                        if s.w_cell is not None:
                            s.w_cell = torch.full_like(s.w_cell, self.w)
                        self.learn_updates += 1
                        self.learn_history.append(float(self.w))
                    else:
                        self.learn_useless += 1
                    continue
                survived = bool((s.alive & entry["mask"]).any())
                if cfg.learn_mode == "bandit":
                    direction = 1.0 if survived else -1.0
                    if s.w_cell is not None and "parent" in entry:
                        target = float(entry.get("child_w", self.w))
                        s.w_cell = torch.where(
                            entry["parent"],
                            torch.clamp(s.w_cell + direction * cfg.learn_rate * (target - s.w_cell), 0.0, 1.0),
                            s.w_cell,
                        )
                    if s.w_cell is not None:
                        self.w = float(s.w_cell.mean())
                elif survived:
                    self.w = min(1.0, self.w + cfg.learn_rate * (1.0 - self.w))
                    if s.w_cell is not None and "parent" in entry:
                        s.w_cell = torch.where(
                            entry["parent"],
                            torch.clamp(s.w_cell + cfg.learn_rate * (1.0 - s.w_cell), 0.0, 1.0),
                            s.w_cell,
                        )
                else:
                    self.w = max(0.0, self.w - cfg.learn_rate * self.w)
                    if s.w_cell is not None and "parent" in entry:
                        s.w_cell = torch.where(
                            entry["parent"],
                            torch.clamp(s.w_cell - cfg.learn_rate * s.w_cell, 0.0, 1.0),
                            s.w_cell,
                        )
                self.learn_updates += 1
                self.learn_history.append(float(self.w))
            self._pending = still

        if cfg.learn_w and cfg.learn_mode == "colony" and s.step and s.step % cfg.learn_window == 0:
            alive_now = int(s.alive.sum())
            gained = alive_now - self._colony_alive_prev
            if gained >= 0:
                # направление сработало — продолжаем в ту же сторону
                self.w = min(1.0, max(0.0, self.w + self._colony_dir * cfg.learn_rate))
            else:
                # стало хуже — разворачиваемся
                self._colony_dir = -self._colony_dir
                self.w = min(1.0, max(0.0, self.w + self._colony_dir * cfg.learn_rate))
            if s.w_cell is not None:
                s.w_cell = torch.full_like(s.w_cell, self.w)
            self.learn_updates += 1
            self.learn_history.append(float(self.w))
            self._colony_alive_prev = alive_now

        s.step += 1
        if s.cell_type is not None and cfg.invade_at and int(s.step) == int(cfg.invade_at):
            self._invade()
        if s.cell_type is not None and int(s.step) % 5 == 0 and bool(s.alive.any()):
            self.type_share_series.append(
                round(float((s.cell_type[s.alive] == 0).float().mean()), 4)
            )
        return {"died": died_now, "alive": int(s.alive.sum()), "catastrophe": self.in_catastrophe()}

    # ---------- подвижность споры при расселении (I-022) ----------
    def _walk_spots(self, spots: torch.Tensor,
                    perceived: torch.Tensor) -> tuple[torch.Tensor, float]:
        """Спора может пройти до `mobility_steps` шагов по свободным клеткам.

        Это подвижность СТАДИИ РАССЕЛЕНИЯ, а не обратимость выбора организма:
        решение, куда поставить спору, принимается один раз, но внутри него
        разрешено несколько шагов к более богатому соседу. Каждый шаг стоит
        `mobility_cost` (0 = бесплатно), платит его спора из своего заряда.
        Возвращает новые позиции и сумму, которую спора потратила на ходы.
        """
        cfg = self.cfg
        steps = int(cfg.mobility_steps)
        if steps <= 0 or spots.numel() == 0:
            return spots, 0.0
        s = self.state
        n = cfg.grid
        cost = float(cfg.mobility_cost)
        # столько получит спора при рождении (как в bud: max(pay/2, 1.0))
        budget = max(float(cfg.budding_cost) * 0.5, 1.0)
        claimed: set[tuple[int, int]] = set()
        out: list[tuple[int, int]] = []
        spent = 0.0
        moved_total = 0
        for y, x in spots.tolist():
            cy, cx = int(y), int(x)
            start = (cy, cx)
            for _ in range(steps):
                if cost > 0.0 and budget <= cost:
                    break
                best, best_res = None, float(perceived[cy, cx])
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if not (0 <= ny < n and 0 <= nx < n):
                        continue
                    if bool(s.alive[ny, nx]) or (ny, nx) in claimed:
                        continue
                    res = float(perceived[ny, nx])
                    if res > best_res:
                        best, best_res = (ny, nx), res
                if best is None:
                    break
                cy, cx = best
                budget -= cost
                spent += cost
                moved_total += 1
            claimed.add((cy, cx))
            self.mobility_shift += abs(cy - start[0]) + abs(cx - start[1])
            out.append((cy, cx))
        if not out:
            return spots, 0.0
        self.mobility_moves += moved_total
        new_spots = torch.tensor(out, device=spots.device, dtype=spots.dtype)
        return new_spots, spent
    def enforce_colony_types(self) -> None:
        """Тип у всей колонии-компоненты один (task-11): voter-смешивания нет.

        При слиянии двух компонент побеждает тип той, чьих клеток больше (тип
        компоненты = округлённое среднее; при ровно 50/50 округление даёт A).
        Рост внутри компоненты тип не меняет, потому что после шага все клетки
        компоненты приводятся к одному типу.
        """
        s = self.state
        if s.cell_type is None or not bool(s.alive.any()):
            return
        if getattr(self.cfg, "type_level", "cell") != "colony":
            return
        mass, labels = self._components(s.alive)
        rule = getattr(self.cfg, "merge_rule", "majority")
        if rule == "keep":
            # H-ALIVE-28: при слиянии клетки СОХРАНЯЮТ свой тип; тип снова живёт на клетке
            # (третья семантика типа после cell-voter и colony-majority)
            return
        for lab in mass:
            m = labels == lab
            vals = s.cell_type[m]
            if int(vals.min()) == int(vals.max()):
                continue
            if rule == "mass_weighted":
                # V8: тип компоненты — лотерея с вероятностью, пропорциональной массе.
                # Меньшинство сохраняет шанс, равный своей доле (3% массы — 3% шанс).
                p1 = float(vals.float().mean())
                u = float(torch.rand((), generator=self.gen_sel))
                t = 1 if u < p1 else 0
            else:
                t = int(round(float(vals.float().mean())))
            s.cell_type[m] = t

    # ---------- обратимость организма (I-023) ----------
    def find_organism_moves(self) -> list[tuple[int, int, int, int]]:
        """Кто из организмов уходит из плохой клетки: (sy, sx, dy, dx).

        Клетка с энергией ниже средней по колонии может сделать шаг в соседнюю
        СВОБОДНУЮ клетку, если ресурс там больше, и если она может заплатить
        `organism_mobility_cost`. Ошибка размещения перестаёт быть смертельной:
        организм исправляет её во время жизни (в отличие от подвижности споры,
        где решение только растягивается).
        """
        cfg = self.cfg
        s = self.state
        if cfg.organism_mobility_cost <= 0.0 or not bool(s.alive.any()):
            return []
        mean_energy = float(s.energy[s.alive].mean())
        poor = s.alive & (s.energy < mean_energy)
        if not bool(poor.any()):
            return []
        n = cfg.grid
        candidates = poor.nonzero(as_tuple=False)
        order = torch.randperm(candidates.shape[0], generator=self.gen_sel)
        taken = torch.zeros_like(s.alive)
        moves: list[tuple[int, int, int, int]] = []
        for k in order.tolist():
            y, x = int(candidates[k, 0]), int(candidates[k, 1])
            if not bool(s.alive[y, x]) or bool(taken[y, x]):
                continue
            if float(s.energy[y, x]) <= cfg.organism_mobility_cost:
                continue
            cur = float(s.resource[y, x])
            best, best_res = None, cur
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if not (0 <= ny < n and 0 <= nx < n):
                    continue
                if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                    continue
                res = float(s.resource[ny, nx])
                if res > best_res:
                    best, best_res = (ny, nx), res
            if best is None:
                continue
            taken[best[0], best[1]] = True
            moves.append((y, x, best[0], best[1]))
        return moves

    def apply_organism_moves(self, moves: list[tuple[int, int, int, int]],
                             cost: float | None = None) -> None:
        """Перенести клетку целиком на новую позицию, списав цену шага."""
        if not moves:
            return
        s = self.state
        cost = float(self.cfg.organism_mobility_cost) if cost is None else float(cost)
        for sy, sx, dy, dx in moves:
            s.alive[dy, dx] = True
            s.alive[sy, sx] = False
            s.energy[dy, dx] = s.energy[sy, sx] - cost
            s.energy[sy, sx] = 0.0
            s.damage[dy, dx] = s.damage[sy, sx]
            s.damage[sy, sx] = 0
            s.age[dy, dx] = s.age[sy, sx]
            s.age[sy, sx] = 0
            s.membrane[dy, dx] = s.membrane[sy, sx]
            s.membrane[sy, sx] = 0.0
        self.organism_moves += len(moves)

    # ---------- L2: пластичность в течение жизни ----------
    def update_plasticity(self) -> None:
        """Локальное правило без градиента: предсказание ресурса по ошибке.

        У каждой клетки есть предсказание `pred` локального ресурса; оно
        подтягивается к фактическому ресурсу с шагом `plastic_eta`. Это не
        обучение веса политики (там сигнал не работал, §10n), а адаптация
        внутреннего состояния клетки, одинаковая во всех средах.
        """
        cfg = self.cfg
        s = self.state
        if cfg.plastic_eta <= 0.0 or s.pred is None:
            return
        s.pred = s.pred + cfg.plastic_eta * (s.resource - s.pred)
        self.plastic_updates += 1

    def plastic_moves(self) -> list[tuple[int, int, int, int]]:
        """Клетки, у которых ресурс ХУЖЕ предсказания, пробуют шаг к соседу."""
        cfg = self.cfg
        s = self.state
        if cfg.plastic_eta <= 0.0 or s.pred is None or not bool(s.alive.any()):
            return []
        if cfg.plastic_nomove:
            return []
        if cfg.plastic_gate == "random":
            roll = torch.rand((cfg.grid, cfg.grid), generator=self.gen_sel).to(self.device)
            poor = s.alive & (roll < float(cfg.plastic_prob))
        else:
            err = s.resource - s.pred
            poor = s.alive & (err < 0.0)
        poor = poor & (s.energy > cfg.plastic_move_cost)
        if not bool(poor.any()):
            return []
        n = cfg.grid
        candidates = poor.nonzero(as_tuple=False)
        order = torch.randperm(candidates.shape[0], generator=self.gen_sel)
        taken = torch.zeros_like(s.alive)
        moves: list[tuple[int, int, int, int]] = []
        for k in order.tolist():
            y, x = int(candidates[k, 0]), int(candidates[k, 1])
            if not bool(s.alive[y, x]) or bool(taken[y, x]):
                continue
            best, best_res = None, float(s.resource[y, x])
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if not (0 <= ny < n and 0 <= nx < n):
                    continue
                if bool(s.alive[ny, nx]) or bool(taken[ny, nx]):
                    continue
                res = float(s.resource[ny, nx])
                if res > best_res:
                    best, best_res = (ny, nx), res
            if best is None:
                continue
            taken[best[0], best[1]] = True
            moves.append((y, x, best[0], best[1]))
        return moves

    # ---------- размножение ----------
    def find_buds(self) -> list[torch.Tensor]:
        """Компоненты, у которых хватает массы и энергии на спору."""
        if not self.state.alive.any():
            return []
        mass, labels = self._components(self.state.alive)
        buds = []
        for comp_id, size in mass.items():
            if size < self.cfg.budding_mass:
                continue
            mask = labels == comp_id
            if float(self.state.energy[mask].mean()) >= self.cfg.budding_cost:
                buds.append(mask)
        return buds

    def _perceived_resource(self, field: torch.Tensor | None = None) -> torch.Tensor:
        """Что родитель *видит* как ресурс: истинное поле плюс шум восприятия (σ).

        Истинный `state.resource` не меняется: доход и смерть считаются по нему,
        шум живёт только в решении, куда поставить спору (I-012).
        """
        base = self.state.resource if field is None else field
        sigma = float(self.cfg.sense_noise)
        if sigma <= 0.0:
            return base
        n = self.cfg.grid
        noise = torch.randn((n, n), generator=self.gen, device=self.device)
        return torch.clamp(
            base * (1.0 + sigma * noise), min=0.0, max=self.cfg.resource_max
        )

    def _parent_field(self, parent: torch.Tensor) -> torch.Tensor:
        """Поле ресурса, которое видит родитель: своего типа (I-030)."""
        s = self.state
        if s.cell_type is None or s.resource_b is None:
            return s.resource
        ptype = int(round(float(s.cell_type[parent].float().mean())))
        return s.resource_b if ptype == 1 else s.resource

    def _assign_child_type(self, parent: torch.Tensor, child: torch.Tensor) -> None:
        """Тип потомка: fixed (все A) | random | learn (наследуй, пока не голодно)."""
        s = self.state
        if s.cell_type is None:
            return
        mode = self.cfg.type_mode
        if mode == "fixed":
            t = 0 if self.cfg.type_start != "b" else 1
        elif mode == "mixfixed":
            # 50/50 на старте, но без переключения: потомок наследует тип родителя.
            # Контроль: разнообразие БЕЗ переключения (решает ли переключение или
            # просто присутствие двух типов).
            t = int(round(float(s.cell_type[parent].float().mean())))
        elif mode == "random":
            t = int(torch.randint(0, 2, (), generator=self.gen_sel))
        else:
            ptype = int(round(float(s.cell_type[parent].float().mean())))
            own = s.resource_b if ptype == 1 else s.resource
            local = float(own[parent].mean())
            global_mean = float(own.mean())
            # родитель в хорошей зоне — передаёт тип; в плохой — переключает
            t = ptype if local >= global_mean else 1 - ptype
        s.cell_type[child] = t

    def _score_values(self, free: torch.Tensor,
                      resource: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        """Для свободных клеток: нормированный ресурс и скученность в окрестности 3x3."""
        s = self.state
        cfg = self.cfg
        field = self._perceived_resource() if resource is None else resource
        ys, xs = free[:, 0], free[:, 1]
        res_norm = field[ys, xs] / max(cfg.resource_max, 1e-9)
        padded = torch.zeros((cfg.grid + 2, cfg.grid + 2), device=self.device)
        padded[1:-1, 1:-1] = s.alive.float()
        crowd = torch.zeros(free.shape[0], device=self.device)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                crowd += padded[1 + ys + dy, 1 + xs + dx]
        return res_norm, crowd / 8.0

    def budding_parent(self, parent_mask: torch.Tensor) -> torch.Tensor:
        """Кто почкуется: вся компонента (W1) или ОДНА клетка (W2-bud).

        W2-bud: единица размножения — клетка, а не колония. Родитель выбирается тем же
        критерием, что и спора (`spore_bias`): по `score` — самая «богатая» клетка тела
        (ресурс минус теснота), иначе — случайная живая клетка тела. Это единственное
        изменение мира: спора и её метка принадлежат клетке, а не компоненте.
        """
        if getattr(self.cfg, "budding_unit", "colony") != "cell":
            return parent_mask
        s = self.state
        body = parent_mask & s.alive
        if not bool(body.any()):
            return parent_mask
        idx = body.nonzero(as_tuple=False)
        if self.cfg.spore_bias == "score":
            own = s.resource
            crowd = torch.zeros_like(own)
            crowd[1:, :] += body[:-1, :].float()
            crowd[:-1, :] += body[1:, :].float()
            crowd[:, 1:] += body[:, :-1].float()
            crowd[:, :-1] += body[:, 1:].float()
            score = own - 0.1 * crowd
            vals = score[idx[:, 0], idx[:, 1]]
            pick = idx[int(torch.argmax(vals))]
        else:
            draw = int(torch.randint(0, idx.shape[0], (1,), generator=self.gen_sel))
            pick = idx[draw]
        single = torch.zeros_like(body)
        single[int(pick[0]), int(pick[1])] = True
        return single

    def budding_parents(self, body: torch.Tensor) -> list[torch.Tensor]:
        """Список родителей от одной компоненты: W2-bud-d2 (до N бутонов).

        При `buds_per_component = 1` возвращается ровно один родитель — тем же вызовом, что раньше,
        поэтому старый мир остаётся бит-в-бит. При N > 1 берутся до N разных клеток компоненты по
        тому же `score` (ресурс минус теснота); `one_bud_per_lineage` запрещает два бутона одной
        линии, чтобы N не усиливал предка, а давал шанс мутанту.
        """
        if getattr(self.cfg, "budding_unit", "colony") == "pair":
            return [self.budding_parent_pair(body)]
        n_buds = int(getattr(self.cfg, "buds_per_component", 1))
        quota = float(getattr(self.cfg, "quota_share", 1.0) or 1.0)
        # При quota >= 1.0 старый путь сохраняется бит-в-бит (одна ветка, без лишних вычислений).
        if (quota >= 1.0 and int(getattr(self.cfg, "bud_refractory", 0) or 0) <= 0
                and (getattr(self.cfg, "budding_unit", "colony") != "cell" or n_buds <= 1)):
            return [self.budding_parent(body)]
        s = self.state
        alive_body = body & s.alive
        if not bool(alive_body.any()):
            return [self.budding_parent(body)]
        idx = alive_body.nonzero(as_tuple=False)
        if self.cfg.spore_bias == "score":
            own = s.resource
            crowd = torch.zeros_like(own)
            crowd[1:, :] += alive_body[:-1, :].float()
            crowd[:-1, :] += alive_body[1:, :].float()
            crowd[:, 1:] += alive_body[:, :-1].float()
            crowd[:, :-1] += alive_body[:, 1:].float()
            score = own - 0.1 * crowd
            vals = score[idx[:, 0], idx[:, 1]]
            order = torch.argsort(vals, descending=True)
        else:
            order = torch.randperm(idx.shape[0], generator=self.gen_sel)
        parents: list[torch.Tensor] = []
        used_tags: set[int] = set()
        # H-ALIVE-53: доля каждой линии среди живых клеток — считается один раз на компоненту.
        share_of: dict[int, float] = {}
        blocked = 0
        refractory = int(getattr(self.cfg, "bud_refractory", 0) or 0)
        blocked_ref = 0
        if quota < 1.0 and s.tag is not None:
            live_tags = s.tag[s.alive]
            total_alive = int(live_tags.numel())
            if total_alive > 0:
                uniq, cnt = torch.unique(live_tags, return_counts=True)
                share_of = {int(u): float(c) / float(total_alive)
                            for u, c in zip(uniq.tolist(), cnt.tolist())}
        for pos in order.tolist():
            if len(parents) >= n_buds:
                break
            y, x = int(idx[pos][0]), int(idx[pos][1])
            if getattr(self.cfg, "one_bud_per_lineage", False) and s.tag is not None:
                tag_val = int(s.tag[y, x])
                if tag_val in used_tags:
                    continue
                used_tags.add(tag_val)
            if share_of:
                tag_here = int(s.tag[y, x])
                if share_of.get(tag_here, 0.0) >= quota:
                    blocked += 1
                    continue
            if refractory > 0 and s.tag is not None:
                tag_ref = int(s.tag[y, x])
                last = int((getattr(self, "lineage_last_bud", {}) or {}).get(tag_ref, -10**9))
                if int(s.step) - last < refractory:
                    blocked_ref += 1
                    continue
            single = torch.zeros_like(alive_body)
            single[y, x] = True
            parents.append(single)
        if quota < 1.0 or refractory > 0:
            # Квота или рефрактерный период включены: пустой список — законный исход.
            self.buds_blocked_by_quota = int(getattr(self, "buds_blocked_by_quota", 0)) + blocked
            self.buds_blocked_by_refractory = int(getattr(self, "buds_blocked_by_refractory", 0)) + blocked_ref
            if refractory > 0 and s.tag is not None and parents:
                log_map = getattr(self, "lineage_last_bud", None)
                if log_map is None:
                    self.lineage_last_bud = log_map = {}
                for mask in parents:
                    coords = mask.nonzero(as_tuple=False)
                    if coords.shape[0]:
                        log_map[int(s.tag[int(coords[0, 0]), int(coords[0, 1])])] = int(s.step)
            return parents
        return parents or [self.budding_parent(body)]

    def budding_parent_pair(self, body: torch.Tensor) -> torch.Tensor:
        """Единица размножения — ПАРА клеток: случайная живая клетка + живой 4-сосед той же метки.

        Промежуточная единица между клеткой и колонией (H-ALIVE-48). Если соседа той же метки нет,
        единица вырождается в одну клетку — это считается в `pair_degenerate`.
        """
        s = self.state
        alive_body = body & s.alive
        idx = alive_body.nonzero(as_tuple=False)
        if idx.shape[0] == 0:
            return self.budding_parent(body)
        pick = idx[int(torch.randint(0, idx.shape[0], (), generator=self.gen_sel))]
        y, x = int(pick[0]), int(pick[1])
        mask = torch.zeros_like(alive_body)
        mask[y, x] = True
        n = int(alive_body.shape[0])
        tag_here = int(s.tag[y, x]) if s.tag is not None else -1
        any_tag = str(getattr(self.cfg, "pair_mode", "same_tag")) == "any_tag"
        cand = []
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < n and 0 <= nx < n):
                continue
            if not bool(alive_body[ny, nx]):
                continue
            if not any_tag and s.tag is not None and int(s.tag[ny, nx]) != tag_here:
                continue
            cand.append((ny, nx))
        if not cand and any_tag:
            # 8-связность, затем любая живая клетка компоненты
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if (dy, dx) == (0, 0) or not (0 <= ny < n and 0 <= nx < n):
                        continue
                    if bool(alive_body[ny, nx]):
                        cand.append((ny, nx))
            if not cand:
                others = alive_body.nonzero(as_tuple=False)
                if others.shape[0] > 1:
                    o = others[int(torch.randint(0, others.shape[0], (), generator=self.gen_sel))]
                    cand.append((int(o[0]), int(o[1])))
        if cand:
            ny, nx = cand[int(torch.randint(0, len(cand), (), generator=self.gen_sel))]
            mask[ny, nx] = True
        else:
            self.pair_degenerate += 1
        return mask

    def bud(self, parent_mask: torch.Tensor) -> torch.Tensor | None:
        """Выпустить спору: `spore_cells` свободных клеток рядом с родителем.

        Потомок стартует с одной-нескольких клеток в СВОБОДНЫХ соседних клетках
        (не поверх родителя), и родитель платит энергией. Возвращает маску споры
        или None, если свободных клеток нет.
        """
        cfg = self.cfg
        s = self.state
        parent = parent_mask.to(self.device).bool()
        # поколение: возраст родителя снимается В НАЧАЛЕ деления, потому что перенос
        # внутри bud (подвижность споры) обнуляет возраст у перемещённых клеток и
        # исказил бы метрику. Учитывается только почкование: у роста правила родителя нет.
        # Родитель здесь — ВСЯ компонента (find_buds отдаёт маску колонии), поэтому
        # пара «средний / самый старый возраст» честнее одного числа: делится
        # компонента, а не отдельная клетка.
        parent_age = (int(round(float(s.age[parent].float().mean())))
                      if bool(parent.any()) else None)
        parent_age_oldest = (int(s.age[parent].max())
                             if bool(parent.any()) else None)
        free = self._free_neighbours(parent)
        if free.shape[0] == 0:
            # все соседние клетки заняты: потомка нет, родитель копит энергию.
            # Это создаёт давление на территориальность.
            s.spores_blocked += 1
            return None
        take = min(int(cfg.spore_cells), int(free.shape[0]))
        perceived = self._perceived_resource(self._parent_field(parent))  # тип родителя + шум
        paired = None
        if cfg.learn_w and cfg.learn_mode == "paired" and cfg.spore_bias == "score":
            # (1+1)-ES на парных образцах: тот же родитель, тот же шаг, две клетки —
            # одна по весу w, вторая по w' = w ± δ (знак чередуется). Экология не
            # меняется: spore_cells=2 и так даёт две клетки за рождение; меняется
            # только правило выбора для второй из них.
            w_a = float(self.w)
            sign = 1.0 if self._pair_trials % 2 == 0 else -1.0
            self._pair_trials += 1
            w_b = min(1.0, max(0.0, w_a + sign * float(cfg.learn_pair_noise)))
            res_norm, crowd = self._score_values(free, perceived)
            score_a = w_a * res_norm - (1.0 - w_a) * crowd
            score_b = w_b * res_norm - (1.0 - w_b) * crowd
            idx_a = int(torch.argmax(score_a))
            if int(free.shape[0]) >= 2 and abs(w_b - w_a) > 1e-9:
                score_b = score_b.clone()
                score_b[idx_a] = float("-inf")
                idx_b = int(torch.argmax(score_b))
                order = torch.tensor([idx_a, idx_b], device=free.device)
                paired = {"w_a": w_a, "w_b": w_b}
            else:
                # второй клетки нет или δ=0: обычный выбор, урок не записывается
                order = torch.argsort(score_a, descending=True)[:take]
        elif cfg.spore_bias == "ifd":
            # идеальное свободное распределение: подушевая отдача в окрестности 3x3
            ys, xs = free[:, 0], free[:, 1]
            padded_res = torch.zeros((cfg.grid + 2, cfg.grid + 2), device=self.device)
            padded_res[1:-1, 1:-1] = perceived
            padded_alive = torch.zeros((cfg.grid + 2, cfg.grid + 2), device=self.device)
            padded_alive[1:-1, 1:-1] = s.alive.float()
            res_local = torch.zeros(free.shape[0], device=self.device)
            crowd = torch.zeros(free.shape[0], device=self.device)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    res_local += padded_res[1 + ys + dy, 1 + xs + dx]
                    crowd += padded_alive[1 + ys + dy, 1 + xs + dx]
            payoff = res_local / 9.0 / (1.0 + crowd)
            order = torch.argsort(payoff, descending=True)[:take]
        elif cfg.spore_bias == "matching":
            # matching law вместо melioration: поведение распределяется ПРОПОРЦИОНАЛЬНО
            # подушевой отдаче, а не отдаётся лучшей клетке (argmax). Жадный argmax
            # локально оптимален и глобально субоптимален (Herrnstein & Vaughan).
            ys, xs = free[:, 0], free[:, 1]
            padded_res = torch.zeros((cfg.grid + 2, cfg.grid + 2), device=self.device)
            padded_res[1:-1, 1:-1] = perceived
            padded_alive = torch.zeros((cfg.grid + 2, cfg.grid + 2), device=self.device)
            padded_alive[1:-1, 1:-1] = s.alive.float()
            res_local = torch.zeros(free.shape[0], device=self.device)
            crowd = torch.zeros(free.shape[0], device=self.device)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    res_local += padded_res[1 + ys + dy, 1 + xs + dx]
                    crowd += padded_alive[1 + ys + dy, 1 + xs + dx]
            payoff = res_local / 9.0 / (1.0 + crowd)
            temp = max(float(cfg.matching_temp), 1e-6)
            # нормируем на максимум, иначе payoff**100 уходит в ноль во float32
            # и рулетка вырождается в равномерную
            top = float(payoff.max()) if payoff.numel() else 0.0
            if top <= 0.0:
                order = torch.randperm(
                    free.shape[0], generator=self.gen_sel
                ).to(free.device)[:take]
            else:
                weights = (payoff / top).clamp_min(0.0) ** (1.0 / temp) + 1e-12
                # рулетка без возвращения: несколько клеток за одно рождение не совпадают.
                # Считаем на CPU с явным генератором — иначе прогон невоспроизводим.
                order = torch.multinomial(
                    weights.detach().float().cpu(),
                    num_samples=min(take, int(free.shape[0])),
                    replacement=False,
                    generator=self.gen_sel,
                ).to(free.device)
        elif cfg.spore_bias == "score":
            # торг: ресурс против скученности (доля живых в окрестности 3x3)
            res_norm, crowd = self._score_values(free, perceived)
            parent_w = float(self.state.w_cell[parent].mean()) if self.state.w_cell is not None else self.w
            score = parent_w * res_norm - (1.0 - parent_w) * crowd
            order = torch.argsort(score, descending=True)[:take]
        elif cfg.spore_bias == "rich":
            # поведение: потомок идёт в свободную клетку с наибольшим ресурсом
            values = perceived[free[:, 0], free[:, 1]]
            order = torch.argsort(values, descending=True)[:take]
        else:
            order = torch.randperm(free.shape[0], generator=self.gen, device=self.device)[:take]
        spots = free[order]
        spots, mobility_spent = self._walk_spots(spots, perceived)

        child = torch.zeros_like(s.alive)
        child[spots[:, 0], spots[:, 1]] = True

        # родитель платит, потомок получает перенос (бюджет не растёт)
        pay = min(float(cfg.budding_cost), float(s.energy[parent].sum()))
        s.energy[parent] -= pay / max(int(parent.sum()), 1)
        s.energy[child] = max(max(pay * 0.5, 1.0) - mobility_spent, 0.0)
        s.alive |= child
        s.age[child] = 0
        s.damage[child] = 0
        s.born += 1
        if parent_age is not None:
            n_children = int(spots.shape[0])
            self.division_parent_ages.extend([parent_age] * n_children)
            self.division_oldest_ages.extend([parent_age_oldest] * n_children)
        self._assign_child_type(parent, child)
        self.register_births(child, parent, is_spore=True)
        if cfg.learn_w:
            if cfg.learn_mode == "paired":
                # урок ставится только когда есть вторая спора с другим весом
                if paired is not None:
                    halves = []
                    for row in spots[:2]:
                        one = torch.zeros_like(s.alive)
                        one[int(row[0]), int(row[1])] = True
                        halves.append(one)
                    self._pending.append({
                        "pair": True,
                        "mask_a": halves[0],
                        "mask_b": halves[1],
                        "parent": parent.clone(),
                        "born_step": int(s.step),
                        "w_a": paired["w_a"],
                        "w_b": paired["w_b"],
                    })
                    s.w_cell = torch.full_like(s.w_cell, float(self.w))
                return child
            probe_w = float(self.w)
            if s.w_cell is not None:
                parent_w = float(s.w_cell[parent].mean())
                if cfg.learn_mode == "bandit":
                    import random as _random
                    _rng = _random.Random(int(s.step) * 7919 + 13)
                    probe_w = min(1.0, max(0.0, parent_w + cfg.learn_noise * _rng.gauss(0.0, 1.0)))
                else:
                    probe_w = parent_w
                s.w_cell = torch.where(
                    child, torch.full_like(s.w_cell, probe_w), s.w_cell
                )
            self._pending.append({
                "mask": child.clone(),
                "parent": parent.clone(),
                "born_step": int(s.step),
                "w": float(self.w),
                "child_w": float(probe_w),
            })
        return child

    def _return_on_death(self, dies: torch.Tensor) -> None:
        """W1-niche: возврат взятого за жизнь ресурса (f * resource_taken).

        `legacy`  — туда, где клетка умерла (освободившаяся клетка);
        `prepared` — то же СУММАРНОЕ количество, но в случайные СВОБОДНЫЕ клетки (контроль на
                     «просто больше ресурса»; попадание в свободные обязательно, иначе сравнивается
                     доступность, а не наследование);
        `depleted` — ничего (базовый уровень).
        """
        s = self.state
        f = float(self.cfg.death_return)
        idx = dies.nonzero(as_tuple=False)
        amounts = (f * self.resource_taken[idx[:, 0], idx[:, 1]]).tolist()
        total = float(sum(amounts))
        if total <= 0:
            return
        mode = str(getattr(self.cfg, "death_return_mode", "legacy"))
        tags = s.tag
        if mode in ("adjacent_matched", "adjacency_exact"):
            exact = (mode == "adjacency_exact")
            # контроль СОСЕДСТВА: пустая клетка с тем же числом живых 4-соседей, что у точки
            # смерти (+-1), но не точка смерти. Проверяет гипотезу «доступность/соседство».
            ker = torch.tensor([[0., 1., 0.], [1., 0., 1.], [0., 1., 0.]], device=self.device)
            n4 = torch.nn.functional.conv2d(
                s.alive.float().view(1, 1, *s.alive.shape),
                ker.view(1, 1, 3, 3), padding=1).view(s.alive.shape)
            free_all = (~s.alive).nonzero(as_tuple=False)
            targets = []
            for (dy, dx) in idx.tolist():
                if free_all.shape[0] == 0:
                    return
                want = float(n4[dy, dx])
                dv = n4[free_all[:, 0], free_all[:, 1]]
                ok = (dv == want) if exact else ((dv - want).abs() <= 1.0)
                same_cell = (free_all[:, 0] == dy) & (free_all[:, 1] == dx)
                ok = ok & ~same_cell
                cand = free_all[ok]
                if cand.shape[0] == 0 and exact:
                    ok = ((dv - want).abs() <= 1.0) & ~same_cell
                    cand = free_all[ok]
                if cand.shape[0] == 0:
                    ok2 = dv >= min(2.0, want)
                    cand = free_all[ok2 & ~same_cell]
                if cand.shape[0] == 0:
                    cand = free_all
                pick = cand[int(torch.randint(0, cand.shape[0], (), generator=self.gen_sel))]
                targets.append((int(pick[0]), int(pick[1])))
            targets = torch.tensor(targets, device=self.device)
            for (dy, dx) in idx.tolist():
                if tags is not None:
                    self.death_log.append((int(dy), int(dx), int(tags[dy, dx])))
        elif mode == "density_matched":
            # контроль плотности: пустая клетка с ТОЙ ЖЕ локальной плотностью (окно 5x5, +-1),
            # но не точка смерти. Проверяет, объясняется ли эффект зоны плотностью.
            dens = torch.nn.functional.conv2d(
                s.alive.float().view(1, 1, *s.alive.shape),
                torch.ones((1, 1, 5, 5), device=self.device), padding=2).view(-1)
            dens = dens.view(s.alive.shape)
            free_all = (~s.alive).nonzero(as_tuple=False)
            targets = []
            for (dy, dx) in idx.tolist():
                d_here = float(dens[dy, dx])
                if free_all.shape[0] == 0:
                    return
                dv = dens[free_all[:, 0], free_all[:, 1]]
                ok = (dv - d_here).abs() <= 1.0
                same_cell = (free_all[:, 0] == dy) & (free_all[:, 1] == dx)
                ok = ok & ~same_cell
                cand = free_all[ok]
                if cand.shape[0] == 0:
                    cand = free_all
                pick = cand[int(torch.randint(0, cand.shape[0], (), generator=self.gen_sel))]
                targets.append((int(pick[0]), int(pick[1])))
            targets = torch.tensor(targets, device=self.device)
            for (dy, dx) in idx.tolist():
                if tags is not None:
                    self.death_log.append((int(dy), int(dx), int(tags[dy, dx])))
        elif mode == "foreign":
            # подготовка в клетках, где умерла клетка ДРУГОЙ линии (контроль на «свою зону»)
            targets = []
            for (dy, dx) in idx.tolist():
                tag_here = int(tags[dy, dx]) if tags is not None else -1
                cand = [(y, x) for (y, x, tg) in self.death_log if tg != tag_here]
                if cand:
                    pick = cand[int(torch.randint(0, len(cand), (), generator=self.gen_sel))]
                    targets.append(pick)
                else:
                    free0 = (~s.alive).nonzero(as_tuple=False)
                    if free0.shape[0] == 0:
                        return
                    p0 = free0[int(torch.randint(0, free0.shape[0], (), generator=self.gen_sel))]
                    targets.append((int(p0[0]), int(p0[1])))
            targets = torch.tensor(targets, device=self.device)
            for (dy, dx) in idx.tolist():
                if tags is not None:
                    self.death_log.append((int(dy), int(dx), int(tags[dy, dx])))
        elif mode == "prepared":
            free = (~s.alive).nonzero(as_tuple=False)
            if free.shape[0] == 0:
                return
            perm = torch.randperm(free.shape[0], generator=self.gen_sel)[: len(amounts)]
            targets = free[perm]
        else:
            targets = idx
            for (dy, dx) in idx.tolist():
                if tags is not None:
                    self.death_log.append((int(dy), int(dx), int(tags[dy, dx])))
        for (ty, tx), amount in zip(targets.tolist(), amounts):
            s.resource[ty, tx] = min(
                float(s.resource[ty, tx]) + float(amount), float(self.cfg.resource_max))
            self.returned_total += float(amount)
            self.resource_at_death.append(float(s.resource[ty, tx]))
        # журнал «подготовленных» клеток для статистики наследования
        for k, ((dy, dx), amount) in enumerate(zip(idx.tolist(), amounts)):
            ty, tx = (targets[k].tolist()
                      if mode in ("prepared", "foreign", "density_matched",
                                  "adjacent_matched") else (dy, dx))
            tag_val = int(tags[dy, dx]) if tags is not None else -1
            lvl = -1
            if mode in ("adjacent_matched", "adjacency_exact"):
                ker2 = torch.tensor([[0., 1., 0.], [1., 0., 1.], [0., 1., 0.]], device=self.device)
                n4m = torch.nn.functional.conv2d(
                    s.alive.float().view(1, 1, *s.alive.shape),
                    ker2.view(1, 1, 3, 3), padding=1).view(s.alive.shape)
                lvl = int(n4m[dy, dx])
            self.niche_log.append({
                "step": int(s.step), "y": int(ty), "x": int(tx), "n4": lvl,
                "tag": tag_val, "amount": float(amount), "hit_same": False, "hit_any": False,
                "free_comp": self._free_component_size(int(ty), int(tx)),
            })
            if lvl >= 0:
                slot = self.niche_levels.setdefault(lvl, [0, 0])
                slot[0] += 1
            if tags is not None and bool(s.alive.any()):
                same = int(((tags == tag_val) & s.alive).sum())
                free_n = int((~s.alive).sum())
                self.niche_expected += (same / free_n) if free_n > 0 else 0.0

    def _free_component_size(self, y: int, x: int) -> int:
        """H-ALIVE-52: размер 4-связной компоненты МЁРТВЫХ клеток, содержащей (y, x)."""
        s = self.state
        n = self.cfg.grid
        if not (0 <= y < n and 0 <= x < n):
            return 0
        # ВАЖНО: в момент смерти клетка ещё помечена живой (маска обновляется позже),
        # поэтому стартовую клетку считаем свободной принудительно — иначе размер всегда 0.
        seen = torch.zeros_like(s.alive, dtype=torch.bool)
        stack = [(y, x)]
        seen[y, x] = True
        size = 0
        while stack:
            cy, cx = stack.pop()
            size += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if not (0 <= ny < n and 0 <= nx < n) or bool(seen[ny, nx]):
                    continue
                if bool(s.alive[ny, nx]) and (ny, nx) != (y, x):
                    continue
                seen[ny, nx] = True
                stack.append((ny, nx))
        return size

    def _niche_update(self) -> None:
        """W1-niche: занял ли кто-то подготовленную клетку — и потомок ли это той же линии."""
        if not self.niche_log:
            return
        s = self.state
        tags = s.tag
        for entry in self.niche_log:
            if entry["hit_same"]:
                continue
            y, x = entry["y"], entry["x"]
            if not bool(s.alive[y, x]):
                continue
            if not entry["hit_any"]:
                entry["hit_any"] = True
                self.niche_hit_any += 1
            if tags is not None and int(tags[y, x]) == entry["tag"]:
                entry["hit_same"] = True
                self.niche_hit_same += 1
                lvl = int(entry.get("n4", -1))
                if lvl >= 0 and lvl in self.niche_levels:
                    self.niche_levels[lvl][1] += 1

    def _free_neighbours(self, mask: torch.Tensor) -> torch.Tensor:
        """Свободные (не живые) клетки, соседние с маской (4-связность)."""
        n = self.cfg.grid
        padded = torch.zeros((n + 2, n + 2), dtype=torch.bool, device=self.device)
        padded[1:-1, 1:-1] = mask
        neigh = torch.zeros_like(mask)
        neigh |= padded[:-2, 1:-1]
        neigh |= padded[2:, 1:-1]
        neigh |= padded[1:-1, :-2]
        neigh |= padded[1:-1, 2:]
        free = neigh & ~self.state.alive
        return free.nonzero(as_tuple=False)

    # ---------- служебное ----------
    @staticmethod
    def _components(mask: torch.Tensor) -> tuple[dict[int, int], torch.Tensor]:
        """4-связные компоненты: итеративное распространение меток (без scipy)."""
        h, w = mask.shape
        labels = torch.zeros((h, w), dtype=torch.int64, device=mask.device)
        current = 0
        for y in range(h):
            for x in range(w):
                if not bool(mask[y, x]) or int(labels[y, x]) != 0:
                    continue
                current += 1
                labels[y, x] = current
                stack = [(y, x)]
                while stack:
                    cy, cx = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and bool(mask[ny, nx]) and int(labels[ny, nx]) == 0:
                            labels[ny, nx] = current
                            stack.append((ny, nx))
        sizes = {i: int((labels == i).sum()) for i in range(1, current + 1)}
        return sizes, labels

    def register_births(self, newly: torch.Tensor, parent_mask: torch.Tensor,
                        labels: torch.Tensor | None = None, is_spore: bool = False) -> int:
        """Записать рождения: метка линии потомка, родословная, мутации и счётчики.

        `tag` — наследуемая единица (метка линии), `tag_trait` — её числовой признак,
        `generation_depth` — сколько делений от основателя, `lineage_offspring` — сколько
        потомков приписано линии (единица отбора «линия», без переделки движка).

        Потомок наследует tag и trait родителя, а с вероятностью `mutation_rate`
        получает **новый** tag с `tag_trait` = признак родителя + шум
        (`mutation_trait_sigma`). Так новизна измерима: по спецификации
        (`library/metrics-spec.md`) это «типы, появившиеся и прожившие ≥ 50 шагов», а
        флип A↔B новых типов не создаёт.

        `labels` (компоненты) необязательны, но важны для честной родословной: тогда
        потомок приписывается линии большинства СВОЕЙ колонии, а не всей карты.

        Экологический тип A/B не трогается. При `m = 0` ни одного вызова RNG не
        добавляется, поэтому прежние прогоны воспроизводятся бит-в-бит.
        """
        s = self.state
        # защита от CPU-масок (как в bud()): маски приходят из разных слоёв
        newly = newly.to(self.device).bool()
        parent_mask = parent_mask.to(self.device).bool()
        if labels is not None:
            labels = labels.to(self.device)
        if s.tag is None or not bool(newly.any()):
            return 0

        def ancestor_of(y: int, x: int) -> tuple[int, float] | None:
            """Метка ПРЕДКА: клетка, выросшая по правилу, наследует метку того живого
            4-соседа, из которого выросла (большинство среди соседей-родителей).

            Прежнее правило брало большинство по всему телу компоненты, из-за чего все
            клетки роста доставались предковой линии, а мутантные оставались одиночками
            (§10ag.2: 1-2 метки с >=2 клетками против 18-23 у нейтральной модели).
            Это только бухгалтерия: мир от меток не зависит (m = 0 -> поведение бит-в-бит).
            """
            n = int(parent_mask.shape[0])
            cand: list[int] = []
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < n and 0 <= nx < n and bool(parent_mask[ny, nx]):
                    cand.append(int(s.tag[ny, nx]))
            if not cand:
                return None
            uniq, counts = torch.unique(torch.tensor(cand, device=self.device), return_counts=True)
            tag = int(uniq[int(torch.argmax(counts))])
            same = parent_mask & (s.tag == tag)
            trait = float(s.tag_trait[same].mean()) if bool(same.any()) else 0.0
            return tag, trait

        def base_of(mask: torch.Tensor) -> tuple[int, float]:
            if not bool(mask.any()):
                return 0, 0.0
            vals = s.tag[mask]
            uniq, counts = torch.unique(vals, return_counts=True)
            tag = int(uniq[int(torch.argmax(counts))])
            same = mask & (s.tag == tag)
            trait = float(s.tag_trait[same].mean()) if bool(same.any()) else 0.0
            return tag, trait

        if labels is None:
            base_tag, base_trait = base_of(parent_mask)
            s.tag[newly] = base_tag
            s.tag_trait[newly] = base_trait
            self.lineage_offspring[base_tag] = self.lineage_offspring.get(base_tag, 0) + int(newly.sum())
            if is_spore:
                self.lineage_spores[base_tag] = self.lineage_spores.get(base_tag, 0) + int(newly.sum())
            base_depth = int(self.generation_depth.get(base_tag, 0))
        else:
            base_depth = 0
            for y, x in newly.nonzero(as_tuple=False).tolist():
                anc = ancestor_of(y, x)
                if anc is not None:
                    tag, trait = anc
                else:
                    # новое тело без живого соседа (зажигание/спора) — прежний путь
                    body = parent_mask & (labels == int(labels[y, x]))
                    tag, trait = base_of(body)
                s.tag[y, x] = tag
                s.tag_trait[y, x] = trait
                self.lineage_offspring[tag] = self.lineage_offspring.get(tag, 0) + 1
                base_depth = max(base_depth, int(self.generation_depth.get(tag, 0)))

        mutated = 0
        m = float(self.cfg.mutation_rate)
        if m > 0.0:
            # `gen_sel` — CPU-генератор (как и при выборе спор: многоместные выборки на
            # CUDA недетерминированы). Поэтому тянем на CPU и переносим на устройство,
            # иначе на cuda: RuntimeError: Expected a 'cuda' device type for generator.
            roll = torch.rand(tuple(newly.shape), generator=self.gen_sel).to(self.device)
            flip = newly & (roll < m)
            mutated = int(flip.sum())
            if mutated:
                sigma = float(getattr(self.cfg, "mutation_trait_sigma", 0.0))
                noise = torch.randn(tuple(flip.shape), generator=self.gen_sel).to(self.device) * sigma
                for y, x in flip.nonzero(as_tuple=False).tolist():
                    parent_tag = int(s.tag[y, x])
                    parent_trait = float(s.tag_trait[y, x])
                    tag = self.next_tag
                    self.next_tag += 1
                    s.tag[y, x] = tag
                    s.tag_trait[y, x] = parent_trait + float(noise[y, x])
                    self.tag_born_at[tag] = int(s.step)
                    self.tag_trait_of[tag] = parent_trait + float(noise[y, x])
                    self.generation_depth[tag] = int(self.generation_depth.get(parent_tag, 0)) + 1
                    self.lineage_offspring[tag] = 0
                self.mutation_events += mutated
        uniq, counts = torch.unique(s.tag[newly], return_counts=True)
        for val, cnt in zip(uniq.tolist(), counts.tolist()):
            key = f"T{int(val)}"
            self.births_by_type[key] = self.births_by_type.get(key, 0) + int(cnt)
        return mutated

    def snapshot(self) -> dict:
        s = self.state
        a_share = None
        if s.cell_type is not None and bool(s.alive.any()):
            a_share = round(float((s.cell_type[s.alive] == 0).float().mean()), 4)
        metrics: dict = {}
        if s.tag is not None and bool(s.alive.any()):
            uniq, counts = torch.unique(s.tag[s.alive], return_counts=True)
            births_step = {
                k: v - self._logged_births.get(k, 0) for k, v in self.births_by_type.items()
            }
            deaths_step = {
                k: v - self._logged_deaths.get(k, 0) for k, v in self.deaths_by_type.items()
            }
            self._logged_births = dict(self.births_by_type)
            self._logged_deaths = dict(self.deaths_by_type)
            mutated = self.mutation_events - self._logged_mutations
            self._logged_mutations = self.mutation_events
            # в лог — только скаляры: поштучные счётчики по меткам кладутся в summary
            # каждые 5 шагов (`type_counts_series`), иначе артефакт пухнет вдвое
            metrics = {
                "types_alive": int(uniq.numel()),
                "births_step": int(sum(births_step.values())),
                "deaths_step": int(sum(deaths_step.values())),
                "mutation_events": int(mutated),
            }
        return {
            "step": int(s.step),
            "alive_cells": int(s.alive.sum()),
            "energy_total": float(s.energy.sum()),
            "resource_total": float(s.resource.sum()),
            "consumed_total": float(s.consumed_total),
            "damage_mean": float(s.damage[s.alive].float().mean()) if s.alive.any() else 0.0,
            "membrane_mean": float(s.membrane[s.alive].float().mean()) if s.alive.any() else 0.0,
            "born": int(s.born),
            "died": int(s.died),
            "spores_blocked": int(s.spores_blocked),
            "catastrophe": self.in_catastrophe(),
            "a_share": a_share,
            **metrics,
        }


def survival_probe(repair_cost: float, steps: int = 4000, grid: int = 32,
                   body: int = 6, income: float = 0.02, update_cost: float = 0.01,
                   damage_rate: float = 0.05, seed: int = 0) -> int:
    """Сколько шагов живёт тело при данной цене ремонта (калибровка р- vs К-стратегий).

    Тело не растёт и не делится: это чистая проверка бюджета, нужная до запуска
    эволюции, чтобы ремонт не был ни бесплатным, ни запретительным.
    """
    cfg = PondConfig(
        grid=grid,
        resource_regen=0.05,
        baseline_income=income,
        update_cost=update_cost,
        repair_cost=repair_cost,
        damage_rate=damage_rate,
        damage_max=50,
        noise=0.0,
    )
    pond = Pond(cfg, seed=seed)
    mask = torch.zeros((grid, grid), dtype=torch.bool)
    start = grid // 2 - body // 2
    mask[start:start + body, start:start + body] = True
    pond.seed_life(mask, energy=5.0)
    for step in range(steps):
        pond.regenerate()
        pond.step_cells()
        if not pond.state.alive.any():
            return step + 1
    return steps
