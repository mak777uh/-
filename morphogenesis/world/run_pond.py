"""Цикл эволюции в «пруду»: cNCA + ресурс + энергия + споры.

Связка двух слоёв: мир (`pond.py`) отвечает за бюджет, организм (`cnca.py`) — за
правило и геном. Здесь они соединяются: состояние клеток двигает правило, мир
решает, кто тратит и кто умирает, а появление споры копирует геном с мутацией.

Правила синхронизации (важно, иначе слои разъедутся):

1. `pond.alive` — истина о том, кто жив; канал живости в состоянии подстраивается
   под неё (мёртвые клетки не обновляются и не светятся);
2. смерть в мире гасит клетку в состоянии (канал живости → −20);
3. спора появляется в свободных соседних клетках и получает геном родителя с
   мутацией, σ задаёт мир;
4. никакой функции приспособленности нет: только дефицит.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import torch

# запуск возможен и как python world/run_pond.py, и как python -m world.run_pond
_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)

from world.cnca import CNCA, CNCAConfig
from world.pond import Pond, PondConfig


class PondRun:
    """Один мир: правило, геном на клетку, бюджет и цикл шагов."""

    def __init__(self, world_cfg: PondConfig | None = None, rule_cfg: CNCAConfig | None = None,
                 seed: int = 0, device: str = "cpu", rule_checkpoint: str | None = None) -> None:
        self.world_cfg = world_cfg or PondConfig()
        self.rule_cfg = rule_cfg or CNCAConfig(
            channels=self.world_cfg.channels if hasattr(self.world_cfg, "channels") else 16,
            genome_dim=self.world_cfg.genome_dim,
        )
        self.device = torch.device(device)
        self.gen = torch.Generator(device=self.device).manual_seed(int(seed))
        self.pond = Pond(self.world_cfg, device=self.device, seed=seed)
        self.rule = CNCA(self.rule_cfg).to(self.device)
        if rule_checkpoint:
            payload = torch.load(rule_checkpoint, map_location=self.device, weights_only=False)
            state_dict = payload.get("model_state_dict", payload)
            self.rule.load_state_dict(state_dict)
            print(f"[pond] правило загружено: {rule_checkpoint}")
        n = self.world_cfg.grid
        c = self.rule_cfg.channels
        k = self.rule_cfg.genome_dim
        self.state = torch.zeros((1, c, n, n), device=self.device)
        self.genome = torch.randn((1, k, n, n), generator=self.gen, device=self.device) * 0.1
        self.log: list[dict] = []
        self.snapshots: list[dict] = []
        self.snapshot_every: int = 0
        self.clonal_attached: int = 0
        self.clonal_separate: int = 0
        self.update_probability: float = 1.0

    # ---------- инициализация ----------
    def seed(self, cells: int = 4, energy: float = 8.0) -> None:
        """Поселить несколько клеток в центре: им даётся заряд и геном."""
        n = self.world_cfg.grid
        mid = n // 2
        mask = torch.zeros((n, n), dtype=torch.bool, device=self.device)
        mask[mid - 1 : mid + 1, mid - 1 : mid + 1] = True
        if cells > 4:
            mask[mid - 1 : mid + 1, mid - 1 : mid + 1] = True
        self.pond.seed_life(mask, energy=energy)
        self._apply_alive(mask.to(self.device))
        self._apply_genome(mask, self.genome[0, :, mask])

    # ---------- синхронизация ----------
    ALIVE_VALUE = 0.5      # sigmoid(0.5) > 0.5 — живая клетка
    DEAD_VALUE = -0.5      # sigmoid(-0.5) < 0.5 — мёртвая

    def _apply_alive(self, mask: torch.Tensor) -> None:
        """Привести канал живости в состоянии к маске мира (диапазон обучения)."""
        ch = self.rule_cfg.alive_channel
        with torch.no_grad():
            self.state[0, ch] = torch.where(
                mask, torch.full_like(self.state[0, ch], self.ALIVE_VALUE),
                torch.full_like(self.state[0, ch], self.DEAD_VALUE),
            )

    def _apply_genome(self, mask: torch.Tensor, values: torch.Tensor | None = None) -> None:
        if values is None:
            return
        self.genome[0][:, mask] = values

    def _flow_energy_to_state(self) -> None:
        """Мир решил, кто выжил — гасим остальных в состоянии."""
        alive = self.pond.state.alive
        self._apply_alive(alive)
        # погашенные клетки теряют видимый сигнал, чтобы не «светиться» мёртвыми
        with torch.no_grad():
            for ch in range(self.rule_cfg.channels):
                if ch == self.rule_cfg.alive_channel:
                    continue
                # мёртвые клетки обнуляются, как в обучении (не -20: это вне диапазона)
                self.state[0, ch] = torch.where(
                    alive, self.state[0, ch], torch.zeros_like(self.state[0, ch])
                )

    # ---------- шаг ----------
    def _sync_state_to_world(self, birth_energy: float = 0.5) -> int:
        """Перенести живость из состояния в мир: новые клетки получают стартовый заряд."""
        s = self.pond.state
        with torch.no_grad():
            alive_now = torch.sigmoid(self.state[0, self.rule_cfg.alive_channel]) > 0.5
        newly = alive_now & ~s.alive
        births = int(newly.sum())
        if births:
            # клональность: приросла ли новая клетка к старому телу или начала свой компонент
            old_alive = s.alive.clone()
            s.alive = alive_now
            _, labels = self.pond._components(alive_now)
            new_idx = newly.nonzero(as_tuple=False)
            attached = 0
            for y, x in new_idx.tolist():
                label = int(labels[y, x])
                same = old_alive & (labels == label)
                if bool(same.any()):
                    attached += 1
            self.clonal_attached += attached
            self.clonal_separate += births - attached
            s.energy = torch.where(newly, torch.full_like(s.energy, birth_energy), s.energy)
            s.age = torch.where(newly, torch.zeros_like(s.age), s.age)
            s.damage = torch.where(newly, torch.zeros_like(s.damage), s.damage)
        else:
            s.alive = alive_now
        return births

    def _accumulate(self, alive_now: int) -> None:
        """Накопить «площадь жизни»: сумма живых по шагам."""
        self.pop_time = getattr(self, "pop_time", 0) + int(alive_now)

    def step(self) -> dict:
        with torch.no_grad():
            if self.update_probability >= 1.0:
                self.state = self.rule(self.state, self.genome)
            else:
                # абляция: часть клеток пропускает обновление (шум в динамике)
                new_state = self.rule(self.state, self.genome)
                keep = torch.rand(
                    (1, 1, self.world_cfg.grid, self.world_cfg.grid), device=self.device
                ) < self.update_probability
                self.state = torch.where(keep, new_state, self.state)
        grown = self._sync_state_to_world()
        self.pond.regenerate()
        cell_stats = self.pond.step_cells()
        self._flow_energy_to_state()

        births = 0
        for parent in self.pond.find_buds():
            child = self.pond.bud(parent)
            if child is None:
                continue
            # геном: берём медиану родителя и мутируем
            parent_genome = self.genome[0][:, parent].mean(dim=1, keepdim=True)
            child_genome = self.rule.mutate(
                parent_genome.unsqueeze(0).unsqueeze(-1).unsqueeze(-1), generator=self.gen
            ).reshape(-1, 1)
            self.genome[0][:, child] = child_genome
            self.state[0][:, child] = self.state[0][:, parent].mean(dim=1, keepdim=True)
            births += 1
        self._apply_alive(self.pond.state.alive)

        if self.snapshot_every and self.pond.state.step % self.snapshot_every == 0:
            self.snapshots.append({
                "step": int(self.pond.state.step),
                "alive": self.pond.state.alive.detach().cpu().numpy().copy(),
                "energy": self.pond.state.energy.detach().cpu().numpy().copy(),
            })

        self._accumulate(int(self.pond.state.alive.sum()))
        snap = self.pond.snapshot()
        snap["births_this_step"] = births
        snap["grown_cells"] = grown
        self.log.append(snap)
        return snap

    def run(self, steps: int, log_every: int = 50) -> dict:
        t0 = time.perf_counter()
        for _ in range(steps):
            self.step()
            if len(self.log) % log_every == 0:
                last = self.log[-1]
                print(
                    f"шаг {last['step']:5d} | живых {last['alive_cells']:5d} | "
                    f"родилось {last['born']:3d} | умерло {last['died']:4d} | "
                    f"спор заблокировано {last['spores_blocked']:3d}",
                    flush=True,
                )
        elapsed = time.perf_counter() - t0
        return {"steps": steps, "wall_seconds": round(elapsed, 2), "final": self.log[-1] if self.log else {}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="запуск эволюции в «пруду»")
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--rule-checkpoint", default=None,
                    help="обученное базовое правило (v0.1a); без него правило случайное")
    ap.add_argument("--income", type=float, default=None, help="приток ресурса на клетку за шаг")
    ap.add_argument("--update-cost", type=float, default=None, help="цена обновления клетки")
    ap.add_argument("--repair-cost", type=float, default=None, help="цена ремонта клетки")
    ap.add_argument("--budding-mass", type=float, default=None, help="масса для споры")
    ap.add_argument("--budding-cost", type=float, default=None, help="энергия на спору")
    ap.add_argument("--init-resource-fill", type=float, default=0.0,
                    help="доля потолка, до которой поле заполнено ресурсом на старте")
    ap.add_argument("--income-mode", default="cap", choices=["cap", "proportional"],
                    help="как считается доход: cap (текущий) или proportional (доход*ресурс)")
    ap.add_argument("--flip-at", type=int, default=0,
                    help="перевернуть градиент ресурса на этом шаге (0 = не переворачивать)")
    ap.add_argument("--update-probability", type=float, default=1.0,
                    help="вероятность обновления клетки за шаг (1.0 = детерминированно)")
    ap.add_argument("--snapshot-every", type=int, default=0,
                    help="сохранять снимок состояния каждые N шагов (0 = не сохранять)")
    ap.add_argument("--snapshots-out", default=None, help="куда сохранить снимки (.npz)")
    ap.add_argument("--w-rich", type=float, default=0.5, help="вес ресурса в score (1-w — скученность)")
    ap.add_argument("--learn-w", action="store_true", help="учить вес политики по судьбе потомства")
    ap.add_argument("--learn-rate", type=float, default=0.1)
    ap.add_argument("--learn-delay", type=int, default=10)
    ap.add_argument("--learn-mode", default="outcome", choices=["outcome", "bandit", "colony", "paired"])
    ap.add_argument("--learn-noise", type=float, default=0.05)
    ap.add_argument("--learn-pair-noise", type=float, default=0.2,
                    help="δ парного режима: вторая спора идёт по w' = w ± δ")
    ap.add_argument("--learn-window", type=int, default=30)
    ap.add_argument("--spore-bias", default="random",
                    choices=["random", "rich", "score", "ifd", "matching"],
                    help="куда выпускать спору: случайно, к богатому, score, IFD или matching")
    ap.add_argument("--matching-temperature", type=float, default=1.0,
                    help="температура политики matching: 1 = пропорционально payoff, <1 ближе к argmax")
    ap.add_argument("--sense-noise", type=float, default=0.0,
                    help="σ шума восприятия ресурса: родитель видит resource*(1+σ*N(0,1)), "
                         "доход и смерть считаются по истинному ресурсу")
    ap.add_argument("--layout", default="uniform",
                    choices=["uniform", "gradient", "patches"], help="структура ресурса")
    args = ap.parse_args(argv)
    if args.learn_w and args.learn_mode == "paired" and args.spore_bias != "score":
        ap.error("--learn-mode paired работает только со --spore-bias score: "
                 "парный сигнал сравнивает два веса одной политики")

    world = PondConfig(grid=args.grid)
    if args.income is not None:
        world.baseline_income = args.income
    if args.update_cost is not None:
        world.update_cost = args.update_cost
    if args.repair_cost is not None:
        world.repair_cost = args.repair_cost
    if args.budding_mass is not None:
        world.budding_mass = args.budding_mass
    if args.budding_cost is not None:
        world.budding_cost = args.budding_cost
    world.resource_layout = args.layout
    world.spore_bias = args.spore_bias
    world.matching_temp = args.matching_temperature
    world.sense_noise = args.sense_noise
    world.w_rich = args.w_rich
    world.learn_w = args.learn_w
    world.learn_rate = args.learn_rate
    world.learn_delay = args.learn_delay
    world.learn_mode = args.learn_mode
    world.learn_noise = args.learn_noise
    world.learn_pair_noise = args.learn_pair_noise
    world.learn_window = getattr(args, "learn_window", 30)
    world.flip_at = args.flip_at
    world.income_mode = args.income_mode
    world.init_resource_fill = args.init_resource_fill
    run = PondRun(world_cfg=world, seed=args.seed, device=args.device,
                  rule_checkpoint=args.rule_checkpoint)
    run.snapshot_every = args.snapshot_every
    run.update_probability = args.update_probability
    run.seed(cells=4, energy=8.0)
    summary = run.run(args.steps, log_every=max(1, args.steps // 10))
    summary["clonal_attached"] = run.clonal_attached
    summary["clonal_separate"] = run.clonal_separate
    total = run.clonal_attached + run.clonal_separate
    summary["clonal_fraction"] = (run.clonal_attached / total) if total else None
    summary["deaths_by_zone"] = dict(run.pond.state.deaths_by_zone)
    summary["pop_time"] = int(getattr(run, "pop_time", 0))
    summary["learn_updates"] = int(run.pond.learn_updates)
    summary["learn_useless"] = int(getattr(run.pond, "learn_useless", 0))
    summary["w_final"] = float(run.pond.w)
    if getattr(run.pond.state, "w_cell", None) is not None and run.pond.state.alive.any():
        wcel = run.pond.state.w_cell[run.pond.state.alive]
        summary["w_cell_mean"] = float(wcel.mean())
        summary["w_cell_std"] = float(wcel.std())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.snapshots_out and run.snapshots:
        import numpy as _np
        _np.savez_compressed(
            args.snapshots_out,
            steps=_np.array([s["step"] for s in run.snapshots]),
            alive=_np.array([s["alive"] for s in run.snapshots]),
            energy=_np.array([s["energy"] for s in run.snapshots]),
        )
        print(f"[pond] снимков сохранено: {len(run.snapshots)} -> {args.snapshots_out}")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "log": run.log}, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
