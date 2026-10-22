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
                 seed: int = 0, device: str = "cpu") -> None:
        self.world_cfg = world_cfg or PondConfig()
        self.rule_cfg = rule_cfg or CNCAConfig(
            channels=self.world_cfg.channels if hasattr(self.world_cfg, "channels") else 16,
            genome_dim=self.world_cfg.genome_dim,
        )
        self.device = torch.device(device)
        self.gen = torch.Generator(device=self.device).manual_seed(int(seed))
        self.pond = Pond(self.world_cfg, device=self.device, seed=seed)
        self.rule = CNCA(self.rule_cfg).to(self.device)
        n = self.world_cfg.grid
        c = self.rule_cfg.channels
        k = self.rule_cfg.genome_dim
        self.state = torch.zeros((1, c, n, n), device=self.device)
        self.genome = torch.randn((1, k, n, n), generator=self.gen, device=self.device) * 0.1
        self.log: list[dict] = []

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
    def _apply_alive(self, mask: torch.Tensor) -> None:
        """Привести канал живости в состоянии к маске мира."""
        ch = self.rule_cfg.alive_channel
        with torch.no_grad():
            self.state[0, ch] = torch.where(
                mask, torch.full_like(self.state[0, ch], 10.0),
                torch.full_like(self.state[0, ch], -20.0),
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
                self.state[0, ch] = torch.where(
                    alive, self.state[0, ch], torch.full_like(self.state[0, ch], -20.0)
                ) if ch != self.rule_cfg.alive_channel else self.state[0, ch]

    # ---------- шаг ----------
    def step(self) -> dict:
        with torch.no_grad():
            self.state = self.rule(self.state, self.genome)
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

        snap = self.pond.snapshot()
        snap["births_this_step"] = births
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
    args = ap.parse_args(argv)

    world = PondConfig(grid=args.grid)
    run = PondRun(world_cfg=world, seed=args.seed, device=args.device)
    run.seed(cells=4, energy=8.0)
    summary = run.run(args.steps, log_every=max(1, args.steps // 10))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "log": run.log}, fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
