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
        self.organism_moves_total: int = 0
        self.plastic_moves_total: int = 0
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

    def _organism_mobility(self) -> int:
        """Шаг организма по жизни: двигаем всё состояние клетки и её геном (I-023).

        Ссылка на канал живости пересчитается из маски мира в `_flow_energy_to_state`,
        а остальные каналы переносятся как есть, чтобы не терять «тело» организма.
        """
        cfg = self.world_cfg
        every = int(getattr(cfg, "organism_mobility_every", 0) or 0)
        if every <= 0 or float(getattr(cfg, "organism_mobility_cost", 0.0)) <= 0.0:
            return 0
        if int(self.pond.state.step) % every != 0:
            return 0
        moves = self.pond.find_organism_moves()
        if not moves:
            return 0
        with torch.no_grad():
            for sy, sx, dy, dx in moves:
                self.state[0, :, dy, dx] = self.state[0, :, sy, sx]
                self.state[0, :, sy, sx] = 0.0
                self.genome[0, :, dy, dx] = self.genome[0, :, sy, sx]
                self.genome[0, :, sy, sx] = 0.0
        self.pond.apply_organism_moves(moves)
        self.organism_moves_total += len(moves)
        return len(moves)

    def _plastic_mobility(self) -> int:
        """L2: шаг клетки по ошибке предсказания ресурса (двигаем состояние и геном)."""
        cfg = self.world_cfg
        if float(getattr(cfg, "plastic_eta", 0.0)) <= 0.0:
            return 0
        self.pond.update_plasticity()
        moves = self.pond.plastic_moves()
        if not moves:
            return 0
        with torch.no_grad():
            for sy, sx, dy, dx in moves:
                self.state[0, :, dy, dx] = self.state[0, :, sy, sx]
                self.state[0, :, sy, sx] = 0.0
                self.genome[0, :, dy, dx] = self.genome[0, :, sy, sx]
                self.genome[0, :, sy, sx] = 0.0
        self.pond.apply_organism_moves(moves, cost=float(cfg.plastic_move_cost))
        self.plastic_moves_total += len(moves)
        return len(moves)

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
            if s.cell_type is not None:
                self._inherit_grown_types(old_alive, newly, labels)
        else:
            s.alive = alive_now
        return births

    def _inherit_grown_types(self, old_alive: torch.Tensor, newly: torch.Tensor,
                             labels: torch.Tensor | None = None) -> None:
        """Тип A/B для клеток, выросших правилом (два режима, I-033/task-10).

        `neighbours` — клетка копирует тип ближайших типизированных соседей: это
        voter-процесс, смесь фиксируется за ~100 шагов.
        `parent` — тип идёт по линии: новая клетка наследует тип СВОЕГО тела
        (компоненты), поэтому образуются клональные пятна и voter-смешивания нет.
        Для нового тела без старой части падаем на ближайших соседей, затем на
        тип большинства колонии.
        """
        s = self.pond.state
        ct = s.cell_type
        n = self.world_cfg.grid
        global_type = 1.0 if float((ct[old_alive] == 1).float().mean()) > 0.5 else 0.0
        mode = getattr(self.world_cfg, "type_inherit", "neighbours")
        if mode == "parent" and labels is not None:
            body_type: dict[int, float] = {}
            for lab in set(labels[newly].tolist()):
                body = old_alive & (labels == lab)
                body_type[int(lab)] = float(ct[body].float().mean()) if bool(body.any()) else -1.0
            fallback = 1.0 + global_type
            for y, x in newly.nonzero(as_tuple=False).tolist():
                code = body_type.get(int(labels[y, x]), -1.0)
                ct[y, x] = int(round(code)) if code >= 0.0 else int(fallback - 1.0)
            return
        # neighbours: локальное копирование (voter)
        code = torch.where(old_alive & (ct == 0),
                           torch.ones_like(ct, dtype=torch.float32),
                           torch.zeros_like(ct, dtype=torch.float32))
        code = torch.where(old_alive & (ct == 1), torch.full_like(code, 2.0), code)
        padded = torch.zeros((n + 2, n + 2), device=self.device)
        padded[1:-1, 1:-1] = code
        acc = torch.zeros_like(code)
        cnt = torch.zeros_like(code)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                nb = padded[1 + dy:1 + dy + n, 1 + dx:1 + dx + n]
                acc += nb
                cnt += (nb > 0).to(code.dtype)
        fallback = torch.full_like(acc, 1.0 + global_type)
        mean_code = torch.where(cnt > 0, acc / cnt.clamp_min(1), fallback)
        ct[newly] = (mean_code[newly] > 1.5).to(ct.dtype)

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
        self._organism_mobility()
        self._plastic_mobility()
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
    ap.add_argument("--catastrophe-rate", type=float, default=0.0,
                    help="пуассоновские катастрофы: событий на шаг (0 = выкл)")
    ap.add_argument("--catastrophe-mode", default="shift", choices=["shift", "drop"],
                    help="shift: ресурс переезжает (сброс в половине поля), drop: ресурс падает везде")
    ap.add_argument("--catastrophe-duration", type=int, default=50,
                    help="длительность катастрофы в шагах")
    ap.add_argument("--flip-at", type=int, default=0,
                    help="перевернуть градиент ресурса на этом шаге (0 = не переворачивать)")
    ap.add_argument("--drift-at", type=int, default=0,
                    help="шаг, с которого градиент переворачивается постепенно (0 = выкл)")
    ap.add_argument("--drift-steps", type=int, default=0,
                    help="за сколько шагов плавный дрейф переворачивает верх и низ")
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
    ap.add_argument("--mobility-steps", type=int, default=0,
                    help="сколько шагов спора может пройти при расселении (0 = выкл)")
    ap.add_argument("--mobility-cost", type=float, default=0.0,
                    help="энергия за шаг споры (0 = бесплатно)")
    ap.add_argument("--organism-mobility-cost", type=float, default=0.0,
                    help="энергия за шаг организма по жизни (0 = выкл, I-023)")
    ap.add_argument("--plastic-eta", type=float, default=0.0,
                    help="L2: скорость обновления предсказания ресурса (0 = выкл)")
    ap.add_argument("--invest-rate", type=float, default=0.0,
                    help="B2: энергия на подъём ресурса в своей клетке (0 = выкл)")
    ap.add_argument("--invest-efficiency", type=float, default=2.0)
    ap.add_argument("--invest-mode", default="fixed", choices=["fixed", "learn", "surplus", "none"])
    ap.add_argument("--invest-threshold", type=float, default=0.3)
    ap.add_argument("--invest-placebo", action="store_true",
                    help="контроль: тратить энергию без подъёма ресурса")
    ap.add_argument("--abiotic", action="store_true",
                    help="контроль: без организмов (только среда)")
    ap.add_argument("--plastic-gate", default="pred", choices=["pred", "random"])
    ap.add_argument("--plastic-prob", type=float, default=0.5)
    ap.add_argument("--plastic-nomove", action="store_true")
    ap.add_argument("--plastic-move-cost", type=float, default=0.05,
                    help="L2: цена шага по ошибке предсказания")
    ap.add_argument("--organism-mobility-every", type=int, default=10,
                    help="раз в сколько шагов организм пробует шаг по жизни")
    ap.add_argument("--freq-dep", type=float, default=0.0,
                    help="сила отрицательной частотной зависимости ресурса (0 = выкл, I-030)")
    ap.add_argument("--invade-at", type=int, default=0,
                    help="шаг инвазии редкого типа (0 = нет)")
    ap.add_argument("--invade-share", type=float, default=0.05,
                    help="доля живых клеток, которым подменяют тип при инвазии")
    ap.add_argument("--invade-type", type=int, default=1, choices=[0, 1],
                    help="какой тип подсаживаем: 0 = A, 1 = B")
    ap.add_argument("--type-inherit", default="neighbours", choices=["neighbours", "parent"],
                    help="как наследуется тип при росте: voter-соседи или линия (компонента)")
    ap.add_argument("--type-start", default="a", choices=["a", "b", "mixed"],
                    help="тип стартовых клеток: все A или смешанный")
    ap.add_argument("--type-mode", default="fixed", choices=["fixed", "mixfixed", "random", "learn"],
                    help="как наследуется тип A/B: fixed | random | learn")
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
    world.mobility_steps = args.mobility_steps
    world.mobility_cost = args.mobility_cost
    world.organism_mobility_cost = args.organism_mobility_cost
    world.organism_mobility_every = args.organism_mobility_every
    world.plastic_eta = args.plastic_eta
    world.plastic_move_cost = args.plastic_move_cost
    world.plastic_gate = args.plastic_gate
    world.plastic_prob = args.plastic_prob
    world.plastic_nomove = args.plastic_nomove
    world.invest_rate = args.invest_rate
    world.invest_efficiency = args.invest_efficiency
    world.invest_mode = args.invest_mode
    world.invest_threshold = args.invest_threshold
    world.invest_placebo = args.invest_placebo
    world.freq_dep = args.freq_dep
    world.type_mode = args.type_mode
    world.type_start = args.type_start
    world.type_inherit = args.type_inherit
    world.invade_at = args.invade_at
    world.invade_share = args.invade_share
    world.invade_type = args.invade_type
    world.w_rich = args.w_rich
    world.learn_w = args.learn_w
    world.learn_rate = args.learn_rate
    world.learn_delay = args.learn_delay
    world.learn_mode = args.learn_mode
    world.learn_noise = args.learn_noise
    world.learn_pair_noise = args.learn_pair_noise
    world.learn_window = getattr(args, "learn_window", 30)
    world.catastrophe_rate = args.catastrophe_rate
    world.catastrophe_duration = args.catastrophe_duration
    world.catastrophe_mode = args.catastrophe_mode
    world.flip_at = args.flip_at
    world.drift_at = args.drift_at
    world.drift_steps = args.drift_steps
    world.income_mode = args.income_mode
    world.init_resource_fill = args.init_resource_fill
    run = PondRun(world_cfg=world, seed=args.seed, device=args.device,
                  rule_checkpoint=args.rule_checkpoint)
    run.snapshot_every = args.snapshot_every
    run.update_probability = args.update_probability
    if not args.abiotic:
        run.seed(cells=4, energy=8.0)
    else:
        run.run.__self__ if False else None
    summary = run.run(args.steps, log_every=max(1, args.steps // 10))
    summary["clonal_attached"] = run.clonal_attached
    summary["clonal_separate"] = run.clonal_separate
    total = run.clonal_attached + run.clonal_separate
    summary["clonal_fraction"] = (run.clonal_attached / total) if total else None
    summary["deaths_by_zone"] = dict(run.pond.state.deaths_by_zone)
    summary["pop_time"] = int(getattr(run, "pop_time", 0))
    summary["learn_updates"] = int(run.pond.learn_updates)
    summary["learn_useless"] = int(getattr(run.pond, "learn_useless", 0))
    summary["mobility_moves"] = int(getattr(run.pond, "mobility_moves", 0))
    summary["mobility_mean_shift"] = round(
        float(getattr(run.pond, "mobility_shift", 0.0)) / max(int(run.pond.state.born), 1), 4
    )
    summary["organism_moves"] = int(run.organism_moves_total)
    summary["plastic_moves"] = int(run.plastic_moves_total)
    summary["plastic_updates"] = int(getattr(run.pond, "plastic_updates", 0))
    summary["invested_energy"] = round(float(getattr(run.pond, "invested_energy", 0.0)), 3)
    summary["invest_updates"] = int(getattr(run.pond, "invest_updates", 0))
    im, inc = getattr(run.pond, "invest_map", None), getattr(run.pond, "income_map", None)
    if im is not None and inc is not None:
        m = im > 1e-6
        if bool(m.any()):
            x = im[m].float()
            y = inc[m].float()
            xc, yc = x - x.mean(), y - y.mean()
            denom = float((xc.pow(2).sum() * yc.pow(2).sum()) ** 0.5)
            summary["feedback_r"] = round(float((xc * yc).sum()) / denom, 4) if denom > 1e-9 else None
            summary["invested_cells"] = int(m.sum())
    summary["resource_mean"] = round(float(run.pond.state.resource.mean()), 5)
    if getattr(run.pond.state, "alive", None) is not None and bool(run.pond.state.alive.any()):
        a = run.pond.state.alive
        summary["resource_alive_mean"] = round(float(run.pond.state.resource[a].mean()), 5)
        summary["resource_empty_mean"] = round(
            float(run.pond.state.resource[~a].mean()) if bool((~a).any()) else 0.0, 5)
    if getattr(run.pond.state, "pred", None) is not None and run.pond.state.alive.any():
        summary["pred_mean_alive"] = round(
            float(run.pond.state.pred[run.pond.state.alive].mean()), 4
        )
    summary["organism_moves_per_step"] = round(
        float(run.organism_moves_total) / max(int(run.pond.state.step), 1), 3
    )
    series = getattr(run.pond, "type_share_series", [])
    if series:
        summary["a_share_final"] = series[-1]
        summary["a_share_min"] = round(min(series), 4)
        summary["a_share_max"] = round(max(series), 4)
        summary["a_share_series"] = series
    summary["invade_at"] = int(getattr(run.pond, "invasion_step", 0))
    summary["invader_share_after"] = getattr(run.pond, "invasion_share_after", None)
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
