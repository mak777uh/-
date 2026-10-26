#!/usr/bin/env python
"""replicator.py — мир `R1`: репликаторы БЕЗ тела (H-ALIVE-50).

Конструкция (см. `reports/2026-10-26-r1-substrate-plan.md`):

  * нет сетки и геометрии; есть единицы (units) и общий пул ресурса;
  * единица = `k` репликаторов, которые делятся ВМЕСТЕ;
  * **порог сравнивается с энергией НА РЕПЛИКАТОР**: `E_unit / k >= E*` (иначе крупные единицы
    делятся чаще просто из-за суммы энергии — конфаундер 1);
  * потомок наследует признак **случайного члена** группы (не среднее — иначе при `k > 1` дисперсия
    признака сжимается, и малое `I` получается по построению — конфаундер 2);
  * экспозиция считается как `k × unit_steps` и в `w`, и в нуль-модели (конфаундер 3);
  * линия = метка основателя единицы; потомки наследуют метку.

Запуск (из корня):

    python scripts/run_replicator.py --k 1 --seed 1 --steps 400
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPOSURE_GATE = 50          # репликатор-шагов; см. пре-регистрацию (гейт экспозиции)


@dataclass
class Replicator:
    trait: float
    energy: float


@dataclass
class Unit:
    tag: int
    members: list[Replicator] = field(default_factory=list)

    @property
    def energy(self) -> float:
        return sum(m.energy for m in self.members)

    @property
    def mean_trait(self) -> float:
        return sum(m.trait for m in self.members) / len(self.members)


class World:
    """R1: единицы репликаторов, общий пул ресурса, деление по энергии на репликатор."""

    def __init__(self, k: int = 1, units: int = 60, seed: int = 1, steps: int = 400,
                 split_threshold: float = 4.0, split_cost: float = 0.5,
                 upkeep: float = 0.30, supply_per_replicator: float = 0.30,
                 target_replicators: int = 600,
                 mutation_sigma: float = 0.05, trait_effect: float = 1.0,
                 max_units: int = 4000) -> None:
        self.rng = random.Random(seed)
        self.k = k
        self.steps = steps
        self.e_star = split_threshold        # порог НА РЕПЛИКАТОР
        self.split_cost = split_cost
        self.upkeep = upkeep
        # хемостат: подача на репликатор зависит от плотности (N_target), но НЕ от k.
        # при N = target: доход = upkeep*(1+0.1*trait) => единицы с высоким признаком накапливают,
        # с низким теряют. Это и есть отбор, и он одинаково доступен при любом k.
        self.supply = supply_per_replicator
        self.target = target_replicators
        self.sigma = mutation_sigma
        self.trait_effect = trait_effect
        self.max_units = max_units
        self.next_tag = units
        self.pool = 0.0
        self.units: list[Unit] = []
        self.divisions_by_tag: dict[int, int] = {}
        self.exposure_by_tag: dict[int, float] = {}
        self.above_threshold_steps = 0
        self.unit_steps_total = 0
        for tag in range(units):
            trait = self.rng.gauss(0.0, 1.0)
            self.units.append(Unit(tag, [Replicator(trait, 2.0) for _ in range(k)]))
            self.divisions_by_tag[tag] = 0
            self.exposure_by_tag[tag] = 0.0

    # ---------- шаг ----------
    def step(self) -> None:
        # 1) потребление: подача НА РЕПЛИКАТОР (хемостат), признак даёт множитель
        n_rep = sum(len(u.members) for u in self.units) or 1
        dilution = min(1.0, self.target / n_rep)
        for unit in self.units:
            for m in unit.members:
                m.energy += (self.supply * dilution
                             * max(0.0, 1.0 + self.trait_effect * 0.1 * m.trait))
        # 2) трата
        for unit in self.units:
            for m in unit.members:
                m.energy -= self.upkeep
        self.units = [u for u in self.units if all(m.energy > 0 for m in u.members)]
        # 3) экспозиция и статистика порога
        for unit in self.units:
            self.exposure_by_tag[unit.tag] = (self.exposure_by_tag.get(unit.tag, 0.0)
                                              + len(unit.members))
            self.unit_steps_total += 1
            if unit.energy / len(unit.members) >= self.e_star:
                self.above_threshold_steps += 1
        # 4) деление: энергия НА РЕПЛИКАТОР выше порога
        born: list[Unit] = []
        for unit in self.units:
            if unit.energy / len(unit.members) < self.e_star:
                continue
            if len(self.units) + len(born) >= self.max_units:
                break
            half = (unit.energy / len(unit.members) - self.split_cost) / 2.0
            if half <= 0:
                continue
            for m in unit.members:
                m.energy = half
            # наследование признака — от СЛУЧАЙНОГО члена, не среднее
            parent_member = self.rng.choice(unit.members)
            child_members = []
            for _ in range(len(unit.members)):
                trait = parent_member.trait + self.rng.gauss(0.0, self.sigma)
                child_members.append(Replicator(trait, half))
            born.append(Unit(unit.tag, child_members))
            self.divisions_by_tag[unit.tag] = self.divisions_by_tag.get(unit.tag, 0) + 1
        self.units.extend(born)

    def run(self) -> dict:
        for _ in range(self.steps):
            self.step()
            if not self.units:
                break
        return self.summary()

    # ---------- статистика ----------
    def summary(self) -> dict:
        # гейт экспозиции (аналог «>=5 клеток» в W2-bud): линия входит в I, только если
        # её экспозиция >= EXPOSURE_GATE репликатор-шагов
        tags = [t for t in self.divisions_by_tag
                if self.exposure_by_tag.get(t, 0.0) >= EXPOSURE_GATE]
        w = []
        for t in tags:
            exp = self.exposure_by_tag[t]
            w.append(self.divisions_by_tag[t] / exp if exp > 0 else 0.0)
        live = len(self.units)
        lineages = [t for t in tags if self.divisions_by_tag[t] > 0]
        return {
            "world": "R1 (репликаторы без тела)",
            "k": self.k,
            "steps": self.steps,
            "units_final": live,
            "replicators_target": self.target,
            "replicators_final": sum(len(u.members) for u in self.units),
            "lineages_with_data": len(lineages),
            "lineages_after_gate": len(tags),
            "exposure_gate": EXPOSURE_GATE,
            "tags_total": len(tags),
            "share_above_threshold": round(self.above_threshold_steps / self.unit_steps_total, 4)
            if self.unit_steps_total else None,
            "share_units_divided": round(
                sum(1 for t in self.divisions_by_tag if self.divisions_by_tag[t] > 0)
                / max(1, len(self.divisions_by_tag)), 4),
            "divisions_total": sum(self.divisions_by_tag.values()),
            "exposure_total": round(sum(self.exposure_by_tag.values()), 3),
            "mean_trait_final": round(statistics.mean([u.mean_trait for u in self.units]), 4)
            if self.units else None,
            "w_by_lineage": {str(t): round(self.divisions_by_tag[t] / self.exposure_by_tag[t], 6)
                             for t in tags if self.exposure_by_tag[t] > 0},
        }


def crow_i(w: list[float]) -> float | None:
    if len(w) < 2:
        return 0.0
    mean = statistics.mean(w)
    if mean <= 0:
        return None
    return statistics.variance(w) / (mean * mean)


def null_95(w: list[float], exposures: list[float], draws: int = 2000,
            seed: int = 7) -> float | None:
    """Условная пуассоновская нуль-модель: X_i ~ Poisson(rate · exposure_i)."""
    if len(w) < 2:
        return None
    rate = sum(wi * ei for wi, ei in zip(w, exposures)) / sum(exposures)
    rng = random.Random(seed)

    def poisson(lam: float) -> int:
        """Пуассон (Кнут); для малых lambda быстрый путь."""
        if lam <= 0:
            return 0
        if lam < 30:
            L, k, p = math.exp(-lam), 0, 1.0
            while True:
                k += 1
                p *= rng.random()
                if p <= L:
                    return k - 1
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))

    vals = []
    for _ in range(draws):
        xs = [poisson(rate * ei) for ei in exposures]
        vals.append(crow_i([x / ei for x, ei in zip(xs, exposures)]) or 0.0)
    vals.sort()
    return vals[int(0.95 * (len(vals) - 1))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--units", type=int, default=60)
    ap.add_argument("--split-threshold", type=float, default=4.0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    world = World(k=args.k, units=args.units, seed=args.seed, steps=args.steps,
                  split_threshold=args.split_threshold)
    summary = world.run()
    w = [summary["w_by_lineage"][t] for t in summary["w_by_lineage"]]
    exposures = [world.exposure_by_tag[int(t)] for t in summary["w_by_lineage"]]
    i_obs = crow_i(w)
    i_null = null_95(w, exposures)
    summary["I_obs"] = round(i_obs, 4) if i_obs is not None else None
    summary["I_null_95"] = round(i_null, 4) if i_null is not None else None
    summary["I_ratio"] = (round(i_obs / i_null, 2)
                          if (i_obs is not None and i_null not in (None, 0)) else None)
    if args.out:
        Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
    print(json.dumps({k: summary[k] for k in
                      ("k", "units_final", "lineages_with_data", "tags_total",
                       "share_above_threshold", "divisions_total", "I_obs", "I_null_95",
                       "I_ratio")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
