"""«Пруд» — минимальная среда, в которой явлению есть где проявиться.

Зачем: в текущем стенде NCA рисует картинку на замкнутом поле: нет среды, цены,
размножения и отбора. Здесь добавляется ровно то, без чего организация не может
быть процессом:

- **ресурс** `resource` — возобновляемое поле (солнце/питание);
- **энергия** `energy` — тратится на обновление клетки, при нуле клетка гаснет;
- **масса** — сколько живых клеток в компоненте (тело);
- **размножение** — компонент с достаточной массой и энергией отделяет «почку»;
- **смерть** — при нуле энергии или при превышении возраста.

Правило обновления состояния сюда не входит: оно передаётся снаружи
(`rule_fn`), чтобы этот модуль можно было тестировать без GPU и без обучения.
Среда отвечает только за бюджет: кто тратит, кто получает, кто умирает, кто
делится.

Инварианты (проверяются тестами):
1. энергия не появляется из ниоткуда — только из ресурса, который регенерирует
   с ограниченной скоростью;
2. мёртвая клетка не тратит и не отдаёт энергию;
3. почка появляется только если у родителя хватает массы и энергии, и её
   появление списывает энергию у родителя.
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
    budding_mass: float = 64          # сколько живых клеток нужно для почки
    budding_cost: float = 8.0         # энергия, которую платит родитель
    max_age: int = 4000
    noise: float = 0.002              # шум в поле ресурса (чтобы среда не была статичной)


@dataclass
class PondState:
    """Состояние мира: ресурс, энергия, возраст, маска живого."""

    resource: torch.Tensor            # (H, W)
    energy: torch.Tensor              # (H, W)
    age: torch.Tensor                 # (H, W) int64
    alive: torch.Tensor               # (H, W) bool
    step: int = 0
    born: int = 0
    died: int = 0
    history: list[dict] = field(default_factory=list)


class Pond:
    """Среда: ресурс, энергия, смерть, размножение. Без правила обновления."""

    def __init__(self, config: PondConfig | None = None, device: str | torch.device = "cpu",
                 seed: int = 0) -> None:
        self.cfg = config or PondConfig()
        self.device = torch.device(device)
        self.gen = torch.Generator(device=self.device).manual_seed(int(seed))
        n = self.cfg.grid
        self.state = PondState(
            resource=torch.full((n, n), self.cfg.resource_max * 0.5, device=self.device),
            energy=torch.zeros((n, n), device=self.device),
            age=torch.zeros((n, n), dtype=torch.int64, device=self.device),
            alive=torch.zeros((n, n), dtype=torch.bool, device=self.device),
        )

    # ---------- ресурс ----------
    def regenerate(self) -> None:
        """Ресурс прибывает с ограниченной скоростью и не превышает максимум."""
        noise = torch.randn(
            (self.cfg.grid, self.cfg.grid), generator=self.gen, device=self.device
        ) * self.cfg.noise
        self.state.resource = torch.clamp(
            self.state.resource + self.cfg.resource_regen + noise, 0.0, self.cfg.resource_max
        )

    # ---------- жизнь клеток ----------
    def seed_life(self, mask: torch.Tensor, energy: float = 5.0) -> None:
        """Поселить жизнь в маске: энергия появляется только вместе с зарядом."""
        mask = mask.to(self.device).bool()
        self.state.alive |= mask
        self.state.energy = torch.where(mask, torch.full_like(self.state.energy, energy), self.state.energy)
        self.state.age = torch.where(mask, torch.zeros_like(self.state.age), self.state.age)

    def step_cells(self) -> dict:
        """Один шаг бюджета: доход из ресурса, плата за обновление, смерть."""
        s = self.state
        alive = s.alive
        # доход: живая клетка забирает из ресурса, но не больше того, что есть
        income = torch.minimum(s.resource, torch.full_like(s.resource, self.cfg.baseline_income))
        s.resource = torch.where(alive, s.resource - income, s.resource)
        s.energy = torch.where(alive, s.energy + income, s.energy)
        # плата за обновление
        s.energy = torch.where(alive, s.energy - self.cfg.update_cost, s.energy)
        s.age = torch.where(alive, s.age + 1, s.age)
        # смерть: нет энергии или пережил максимальный возраст
        dies = alive & ((s.energy <= 0.0) | (s.age > self.cfg.max_age))
        died_now = int(dies.sum())
        s.energy = torch.where(dies, torch.zeros_like(s.energy), s.energy)
        s.alive = alive & ~dies
        s.died += died_now
        s.step += 1
        return {"died": died_now, "alive": int(s.alive.sum())}

    # ---------- размножение ----------
    def find_buds(self) -> list[torch.Tensor]:
        """Компоненты, у которых достаточно массы и энергии для почки."""
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

    def bud(self, parent_mask: torch.Tensor) -> torch.Tensor:
        """Отделить почку: списать энергию у родителя, вернуть маску потомка.

        Потомок получает энергию от родителя (не из воздуха), поэтому бюджет мира
        не растёт. Геном копируется снаружи — среда отвечает только за бюджет.
        """
        s = self.state
        idx = parent_mask.nonzero(as_tuple=False)
        # берём клетку на краю компонента как точку старта почки
        start = idx[0]
        y, x = int(start[0]), int(start[1])
        child = torch.zeros_like(s.alive)
        child[y, x] = True
        # списываем у родителя
        s.energy[parent_mask] -= self.cfg.budding_cost / max(int(parent_mask.sum()), 1)
        # переносим заряд в потомка (сколько осталось после списания)
        transfer = min(self.cfg.budding_cost, float(s.energy[parent_mask].sum()))
        s.energy[child] = max(transfer, 1.0)
        s.alive |= child
        s.age[child] = 0
        s.born += 1
        return child

    # ---------- служебное ----------
    @staticmethod
    def _components(mask: torch.Tensor) -> tuple[dict[int, int], torch.Tensor]:
        """4-связные компоненты без scipy: итеративное распространение меток."""
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
            "born": int(s.born),
            "died": int(s.died),
        }
