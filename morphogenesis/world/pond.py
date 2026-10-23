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

    # ---------- жизнь клеток ----------
    def seed_life(self, mask: torch.Tensor, energy: float = 5.0) -> None:
        """Поселить жизнь: энергия появляется только вместе с зарядом."""
        mask = mask.to(self.device).bool()
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

    def step_cells(self) -> dict:
        """Один шаг бюджета: доход, плата, ремонт, повреждения, смерть."""
        cfg = self.cfg
        s = self.state
        alive = s.alive

        if cfg.income_mode == "proportional":
            # доход пропорционален доступному ресурсу: бедная зона реально голодает
            income = torch.minimum(
                s.resource, cfg.baseline_income * s.resource * 4.0
            )
        else:
            income = torch.minimum(s.resource, torch.full_like(s.resource, cfg.baseline_income))
        if cfg.membrane_gated:
            # обмен возможен только там, где есть мембрана: её производит организм
            gate = (s.membrane >= cfg.membrane_threshold).to(income.dtype)
            income = income * gate
        income = torch.where(alive, income, torch.zeros_like(income))
        s.resource = s.resource - income
        s.energy = s.energy + income
        self.state.consumed_total += float(income.sum())

        spent = cfg.update_cost + cfg.repair_cost
        s.energy = torch.where(alive, s.energy - spent, s.energy)

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
        # зоны по ресурсу в момент решения: где именно умирают клетки
        if cfg.resource_max > 0 and died_now:
            rich = s.resource > cfg.resource_max * 2 / 3
            poor = s.resource < cfg.resource_max / 3
            mid = ~rich & ~poor
            for name, zone in (("poor", poor), ("mid", mid), ("rich", rich)):
                s.deaths_by_zone[name] += int((dies & zone).sum())
        s.energy = torch.where(dies, torch.zeros_like(s.energy), s.energy)
        s.alive = alive & ~dies
        s.died += died_now
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

    def apply_organism_moves(self, moves: list[tuple[int, int, int, int]]) -> None:
        """Перенести клетку целиком на новую позицию, списав цену шага."""
        if not moves:
            return
        s = self.state
        cost = float(self.cfg.organism_mobility_cost)
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

    def _perceived_resource(self) -> torch.Tensor:
        """Что родитель *видит* как ресурс: истинное поле плюс шум восприятия (σ).

        Истинный `state.resource` не меняется: доход и смерть считаются по нему,
        шум живёт только в решении, куда поставить спору (I-012).
        """
        sigma = float(self.cfg.sense_noise)
        if sigma <= 0.0:
            return self.state.resource
        n = self.cfg.grid
        noise = torch.randn((n, n), generator=self.gen, device=self.device)
        return torch.clamp(
            self.state.resource * (1.0 + sigma * noise), min=0.0, max=self.cfg.resource_max
        )

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

    def bud(self, parent_mask: torch.Tensor) -> torch.Tensor | None:
        """Выпустить спору: `spore_cells` свободных клеток рядом с родителем.

        Потомок стартует с одной-нескольких клеток в СВОБОДНЫХ соседних клетках
        (не поверх родителя), и родитель платит энергией. Возвращает маску споры
        или None, если свободных клеток нет.
        """
        cfg = self.cfg
        s = self.state
        parent = parent_mask.to(self.device).bool()
        free = self._free_neighbours(parent)
        if free.shape[0] == 0:
            # все соседние клетки заняты: потомка нет, родитель копит энергию.
            # Это создаёт давление на территориальность.
            s.spores_blocked += 1
            return None
        take = min(int(cfg.spore_cells), int(free.shape[0]))
        perceived = self._perceived_resource()  # шум восприятия (σ=0 -> истинный ресурс)
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

    def snapshot(self) -> dict:
        s = self.state
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
