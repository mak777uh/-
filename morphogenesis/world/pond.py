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
    step: int = 0
    born: int = 0
    died: int = 0
    spores_blocked: int = 0
    consumed_total: float = 0.0
    history: list[dict] = field(default_factory=list)


class Pond:
    """Среда: ресурс, энергия, повреждения, смерть, споры, катастрофы."""

    def __init__(self, config: PondConfig | None = None, device: str | torch.device = "cpu",
                 seed: int = 0) -> None:
        self.cfg = config or PondConfig()
        self.device = torch.device(device)
        self.gen = torch.Generator(device=self.device).manual_seed(int(seed))
        n = self.cfg.grid
        self._catastrophe_left = 0
        self._catastrophe_next = self._sample_gap()
        self.state = PondState(
            resource=torch.full((n, n), self.cfg.resource_max * 0.5, device=self.device),
            energy=torch.zeros((n, n), device=self.device),
            damage=torch.zeros((n, n), dtype=torch.int64, device=self.device),
            membrane=torch.zeros((n, n), device=self.device),
            age=torch.zeros((n, n), dtype=torch.int64, device=self.device),
            alive=torch.zeros((n, n), dtype=torch.bool, device=self.device),
        )

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
            rows = torch.arange(cfg.grid, device=self.device, dtype=torch.float32)
            ceiling = ceiling * (0.2 + 0.8 * (1.0 - rows / max(cfg.grid - 1, 1)))[:, None]
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
        s.energy = torch.where(dies, torch.zeros_like(s.energy), s.energy)
        s.alive = alive & ~dies
        s.died += died_now
        s.step += 1
        return {"died": died_now, "alive": int(s.alive.sum()), "catastrophe": self.in_catastrophe()}

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
        order = torch.randperm(free.shape[0], generator=self.gen, device=self.device)[:take]
        spots = free[order]

        child = torch.zeros_like(s.alive)
        child[spots[:, 0], spots[:, 1]] = True

        # родитель платит, потомок получает перенос (бюджет не растёт)
        pay = min(float(cfg.budding_cost), float(s.energy[parent].sum()))
        s.energy[parent] -= pay / max(int(parent.sum()), 1)
        s.energy[child] = max(pay * 0.5, 1.0)
        s.alive |= child
        s.age[child] = 0
        s.damage[child] = 0
        s.born += 1
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
