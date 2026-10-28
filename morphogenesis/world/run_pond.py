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
import random
import json
import sys as _sys


def _safe_print(*pargs, **pkwargs):
    """26.10: печать не должна убивать прогон — запись в закрытый пайп на Windows даёт
    OSError [Errno 22], и раньше это падало ПОСЛЕ расчёта, но ДО записи артефакта."""
    try:
        print(*pargs, **pkwargs)
    except OSError:
        pass
import os
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

import torch

# запуск возможен и как python world/run_pond.py, и как python -m world.run_pond
_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _MORPH not in sys.path:
    sys.path.insert(0, _MORPH)

from world.cnca import CNCA, CNCAConfig
from world.pond import Pond, PondConfig


def git_provenance() -> dict:
    """Провенанс кода на СТАРТЕ прогона: хеш коммита и был ли рабочий каталог грязным.

    Зачем: за сутки два инцидента «смешанное состояние кода» (правка `pond.py` посреди
    серии D; CUDA-генератор в серии B). Раньше чистота серии проверялась вручную
    повторным прогоном на якоре. С этими полями агрегат проверяет однородность
    механически: разные `git_commit` в одной серии — ошибка (данные получены разным
    кодом), а `git_dirty = true` — предупреждение (в дереве были несохранённые файлы,
    в том числе артефакты предыдущих прогонов серии).

    `None` — git недоступен (например, прогон из архива): это не ошибка, а «нет данных».
    """
    root = Path(__file__).resolve().parents[2]
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
        status = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"],
            stderr=subprocess.DEVNULL, text=True)
        # идентичность КОДА, а не HEAD: последний коммит, тронувший мир или config.py
        code_commit = subprocess.check_output(
            ["git", "-C", str(root), "log", "-1", "--format=%h", "--",
             "morphogenesis/world", "morphogenesis/config.py"],
            stderr=subprocess.DEVNULL, text=True).strip()
        return {"git_commit": commit or None, "git_dirty": bool(status.strip()),
                "git_code_commit": code_commit or None}
    except (OSError, subprocess.CalledProcessError):
        return {"git_commit": None, "git_dirty": None, "git_code_commit": None}


def file_sha256(path: str | None) -> str | None:
    """sha256 файла весов: код может быть тем же, а правило другим — тогда мир другой."""
    if not path:
        return None
    try:
        import hashlib
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def config_block(cfg) -> dict:
    """Конфигурация прогона в `summary["config"]`.

    Зачем: артефакт должен читаться сам, без sweep-скрипта вне git. До этого
    `freq_dep` не попадал в `summary` вообще, и плечо восстанавливалось только из
    командной строки, которой в артефакте нет.

    `invade_at` здесь — **запрошенный** шаг инвазии; фактический шаг лежит в
    `summary["invade_at"]` (он сдвигается, если колония ещё меньше `invade_min_cells`).
    """
    return {
        "freq_dep": getattr(cfg, "freq_dep", None),
        "freq_dep_range": "0..1 (непрерывный множитель: 0 — обратной связи нет, "
                          "1 — максимальная; метки fd0/fd05/fd10 = 0.0/0.5/1.0)",
        "type_mode": getattr(cfg, "type_mode", None),
        "type_level": getattr(cfg, "type_level", None),
        "type_inherit": getattr(cfg, "type_inherit", None),
        "invade_at": getattr(cfg, "invade_at", 0),
        "invade_share": getattr(cfg, "invade_share", None),
        "invade_type": getattr(cfg, "invade_type", None),
        "invade_min_cells": getattr(cfg, "invade_min_cells", None),
        "invader_cells": getattr(cfg, "invader_cells", 1),
        "invade_placement": getattr(cfg, "invade_placement", "random"),
        "merge_rule": getattr(cfg, "merge_rule", "majority"),
        "trait_effect": getattr(cfg, "trait_effect", 0.0),
        "budding_unit": getattr(cfg, "budding_unit", "colony"),

        "require_placement": getattr(cfg, "require_placement", 0),
        "buds_per_component": getattr(cfg, "buds_per_component", 1),
        "niche_free_min": getattr(cfg, "niche_free_min", 0),
        "pair_mode": getattr(cfg, "pair_mode", "same_tag"),
        "death_return": getattr(cfg, "death_return", 0.0),
        "death_return_mode": getattr(cfg, "death_return_mode", "legacy"),
        "one_bud_per_lineage": bool(getattr(cfg, "one_bud_per_lineage", False)),
        "quota_share": float(getattr(cfg, "quota_share", 1.0)),
        "bud_refractory": int(getattr(cfg, "bud_refractory", 0)),
        "kill_winner": float(getattr(cfg, "kill_winner", 0.0)),
        "trait_effect_mode": str(getattr(cfg, "trait_effect_mode", "invest")),
        "inflow_coupling": float(getattr(cfg, "inflow_coupling", 0.0)),
        "inflow_stream_mode": str(getattr(cfg, "inflow_stream_mode", "")),
        "invade_on_empty": bool(getattr(cfg, "invade_on_empty", False)),
        "start_cells": int(getattr(cfg, "start_cells", 4)),
        "ignition_gate": bool(getattr(cfg, "ignition_gate", False)),
        "mutation_rate": getattr(cfg, "mutation_rate", 0.0),
        "mutation_trait_sigma": getattr(cfg, "mutation_trait_sigma", 0.0),
        "layout": getattr(cfg, "resource_layout", None),
        "resource_regen": float(getattr(cfg, "resource_regen", 0.02)),
        "income": getattr(cfg, "baseline_income", None),
        "update_cost": getattr(cfg, "update_cost", None),
        "repair_cost": getattr(cfg, "repair_cost", None),
    }


def tag_metrics_block(pond) -> dict:
    """Метрики условия B по МЕТКАМ ЛИНИЙ (tag), а не по экологическому типу A/B.

    Формат согласован с библиотекарем (`library/conditions-B-criteria.md`):
    `type_counts_series` — список {"step": N, "counts": {tag: клеток}} каждые 5 шагов,
    а не каждый шаг (артефакт иначе пухнет вдвое); `type_counts` — итог на конец;
    `type_traits` — {tag: признак} для меток, у которых были рождения (без признака
    дифференциальное воспроизводство не считается — это «нет данных», а не «нет отбора»).
    """
    import torch as _torch  # локально: модуль должен импортироваться и без тяжёлых путей
    s = pond.state
    block = {
        "type_counts": {},
        "types_alive": 0,
        "births_by_type": dict(getattr(pond, "births_by_type", {})),
        "deaths_by_type": dict(getattr(pond, "deaths_by_type", {})),
        "mutation_events": int(getattr(pond, "mutation_events", 0)),
        "type_counts_series": list(getattr(pond, "type_counts_series", [])),
        "type_traits": {},
        "lineage_generation": dict(getattr(pond, "generation_depth", {})),
        "lineage_fitness": dict(getattr(pond, "lineage_offspring", {})),
        "lineage_spores": dict(getattr(pond, "lineage_spores", {})),
        "lineage_invested": {str(k): round(float(v), 4)
                             for k, v in getattr(pond, "lineage_invested", {}).items()},
        "lineage_invest_updates": {str(k): int(v)
                                   for k, v in getattr(pond, "lineage_invest_updates", {}).items()},
        "lineage_cell_steps": {str(k): int(v)
                               for k, v in getattr(pond, "lineage_cell_steps", {}).items()},
        "lineage_energy_steps": {str(k): round(float(v), 3)
                                 for k, v in getattr(pond, "lineage_energy_steps", {}).items()},
        "lineage_energy_mean_sum": {str(k): round(float(v), 4)
                                    for k, v in getattr(pond, "lineage_energy_mean_sum", {}).items()},
        "lineage_energy_samples": {str(k): int(v)
                                   for k, v in getattr(pond, "lineage_energy_samples", {}).items()},
        "tag_source": "tag: наследуемая метка линии; type A/B — экологический пул",
    }
    if s.tag is None or not bool(s.alive.any()):
        return block
    uniq, counts = _torch.unique(s.tag[s.alive], return_counts=True)
    finals = {f"T{int(u)}": int(c) for u, c in zip(uniq.tolist(), counts.tolist())}
    block["type_counts"] = finals
    block["types_alive"] = len(finals)
    traits = getattr(pond, "tag_trait_of", {})
    for key in block["births_by_type"]:
        tag_id = int(key[1:]) if key.startswith("T") else None
        if tag_id is not None and tag_id in traits:
            block["type_traits"][key] = round(float(traits[tag_id]), 6)
    return block


def resource_zones(pond) -> dict:
    """Ресурс по зонам в финале: всё поле / под живыми / под мёртвыми.

    Нужно, чтобы отличать «клетке не хватает ресурса» от «механику съедает» (§10ai):
    без этих чисел вопрос о конкуренции за ресурс не решается.
    """
    s = pond.state
    alive = s.alive
    res = s.resource
    empty = ~alive
    block = {
        "resource_mean": round(float(res.mean()), 4),
        "resource_alive_mean": round(float(res[alive].mean()), 4) if bool(alive.any()) else None,
        "resource_empty_mean": round(float(res[empty].mean()), 4) if bool(empty.any()) else None,
    }
    rb = getattr(s, "resource_b", None)
    if rb is not None:
        # пул B: в freq_dep-мире он получает inflow*fb, и при доминировании A это до 2x
        block["resource_b_mean"] = round(float(rb.mean()), 4)
        block["resource_b_alive_mean"] = round(float(rb[alive].mean()), 4) if bool(alive.any()) else None
        is_b = s.cell_type == 1 if s.cell_type is not None else None
        if is_b is not None and bool((is_b & alive).any()):
            block["resource_b_under_b_cells"] = round(float(rb[is_b & alive].mean()), 4)
    return block


def invasion_resource_block(pond, log: list[dict]) -> dict:
    """Ресурс в трёх зонах на шаге инвазии: точка подсадки, колония, свободное поле."""
    spot = getattr(pond, "_last_invasion_spot", None)
    if spot is None:
        return {}
    s = pond.state
    alive = s.alive
    coords = torch.as_tensor(spot, dtype=torch.long).flatten()
    if int(coords.numel()) < 2:
        return {}
    y, x = int(coords[0]), int(coords[1])
    free = ~alive
    block = {
        "resource_at_invasion_spot": round(float(s.resource[y, x]), 4),
        "resource_colony_mean": round(float(s.resource[alive].mean()), 4) if bool(alive.any()) else None,
        "resource_free_mean": round(float(s.resource[free].mean()), 4) if bool(free.any()) else None,
    }
    if log and "resource_mean" in log[-1]:
        block["resource_mean_at_invasion"] = log[-1]["resource_mean"]
    rb = getattr(s, "resource_b", None)
    if rb is not None:
        block["resource_b_at_invasion_spot"] = round(float(rb[y, x]), 4)
        block["resource_b_colony_mean"] = (round(float(rb[alive].mean()), 4)
                                           if bool(alive.any()) else None)
    return block


def final_map_block(pond) -> dict:
    """Финальная карта живого (патч логгера под IDH/TDA, §10x.1).

    Без карты разнообразие ПАТТЕРНОВ не считается (IDH, Betti, Rugosity): в `log` были
    только скаляры. Формат компактный: `final_alive_map` — строки по 32 символа «0/1»
    через «/», то есть 32×32 бит на прогон (~1 КБ текстом). Старые артефакты не
    переписываются: поле появляется у новых прогонов.
    """
    s = pond.state
    block: dict = {"final_alive_map": None, "alive_map_shape": None,
                   "map_source": "final_alive_map: строки «0/1» через «/», финальный шаг"}
    if not bool(s.alive.any()) and int(s.alive.sum()) == 0:
        block["final_alive_map"] = "/".join(["0" * int(s.alive.shape[1])] * int(s.alive.shape[0]))
        block["alive_map_shape"] = list(s.alive.shape)
        return block
    rows = ["".join("1" if bool(v) else "0" for v in row) for row in s.alive]
    block["final_alive_map"] = "/".join(rows)
    block["alive_map_shape"] = list(s.alive.shape)
    return block


def generation_block(parent_ages: list[int], oldest_ages: list[int] | None = None) -> dict:
    """Длина поколения в шагах по почкованиям: медиана и «средняя», и «самая старая».

    В этой модели делится **компонента**, а не отдельная клетка (`find_buds` отдаёт
    маску всей колонии), поэтому «время от рождения клетки до её деления» одного
    числа не даёт. Пишем два: `generation_length` — медиана среднего возраста клеток
    колонии в момент деления, `generation_length_oldest` — медиана возраста самой
    старой клетки (верхняя оценка возраста линии). Оба — описательные; критерии
    гипотез на них не опираются.

    Меньше 20 делений — `null`, а не оценка: медиана по 3 событиям ничего не значит
    (H71/P64 — при малых n число без интервала не публикуется). Считается только
    почкование: клетки, выросшие по правилу, родителя не имеют.
    """
    ages = [int(a) for a in parent_ages]
    oldest = [int(a) for a in (oldest_ages or [])]
    block = {
        "generation_length": None,
        "generation_length_oldest": None,
        "generation_divisions": len(ages),
        "generation_source": "budding: возраст клеток колонии (средний и самой старой) "
                             "на шаге деления; делится компонента, а не клетка",
    }
    if len(ages) >= 20:
        block["generation_length"] = round(float(statistics.median(ages)), 1)
    if len(oldest) >= 20:
        block["generation_length_oldest"] = round(float(statistics.median(oldest)), 1)
    return block


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
            _safe_print(f"[pond] правило загружено: {rule_checkpoint}")
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
        """Поселить `cells` клеток в центре: им даётся заряд и геном.

        `cells = 0` — **пустое поле**: мир стартует без жизни (плечо `resident_free`:
        проверяем, основывает ли колонию сам инокулят). `cells = 4` — исторический
        старт блоком 2x2, он остаётся бит-в-бит для всех старых серий.
        """
        n = self.world_cfg.grid
        mid = n // 2
        mask = torch.zeros((n, n), dtype=torch.bool, device=self.device)
        cells = int(cells)
        if cells <= 0:
            return
        if cells == 4:
            mask[mid - 1 : mid + 1, mid - 1 : mid + 1] = True
        else:
            # центрированный квадрат, ровно `cells` клеток в порядке строк
            side = max(1, math.isqrt(cells - 1) + 1)
            top = mid - side // 2
            left = mid - side // 2
            coords = [(top + i // side, left + i % side) for i in range(cells)]
            for y, x in coords:
                mask[y % n, x % n] = True
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

    def _gate_ignition(self, alive_now: torch.Tensor) -> torch.Tensor:
        """Оставить только клетки, приросшие к уже живому (4-соседство).

        Пустое поле остаётся пустым: без этого правила «жизнь из ничего» не отличить от
        основания колонии. Уже живые клетки не гасятся — гейт касается только новых.
        """
        s = self.pond.state
        if not bool(alive_now.any()):
            return alive_now
        if not bool(s.alive.any()):
            # поле пустое: зажигать нечему, кроме того, что уже посажено снаружи (seed/bud)
            return alive_now & s.alive
        n = int(alive_now.shape[0])
        grow = torch.zeros_like(s.alive)
        grow[1:, :] |= s.alive[:-1, :]
        grow[:-1, :] |= s.alive[1:, :]
        grow[:, 1:] |= s.alive[:, :-1]
        grow[:, :-1] |= s.alive[:, 1:]
        return s.alive | (alive_now & grow)

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
        if bool(getattr(self.world_cfg, "ignition_gate", False)):
            # гейт зажигания: правило не имеет права зажечь клетку, у которой нет живого
            # 4-соседа. Иначе обученное правило из пустого поля зажигает ВСЁ (1024 из 1024
            # на шаге 1, см. §10ae) и вопрос «основывает ли колонию N клеток» не задаётся.
            alive_now = self._gate_ignition(alive_now)
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
                self.pond.register_births(newly, old_alive, labels)
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
            cfg_ = getattr(self, "world_cfg", None)
            live_src = getattr(cfg_, "inflow_live", None)
            if live_src is not None and getattr(cfg_, "inflow_coupling", 0.0) > 0.0:
                # H-ALIVE-59 (живой режим): значение приходит от источника ПРЯМО СЕЙЧАС
                v = float(live_src.value()) if hasattr(live_src, "value") else 0.5
                rec = getattr(cfg_, "inflow_record", None)
                if isinstance(rec, list):
                    rec.append(round(v, 6))
                c = float(getattr(cfg_, "inflow_coupling", 0.0))
                if str(getattr(cfg_, "inflow_stream_mode", "global") or "global") == "spatial":
                    grid = cfg_.grid
                    self.pond.state.income_scale.copy_((1.0 + c * (2.0 * v - 1.0)))
                else:
                    self.pond.state.income_scale.fill_(1.0 + c * (2.0 * v - 1.0))
            infl_vals = getattr(cfg_, "inflow_values", None)
            if infl_vals and getattr(cfg_, "inflow_coupling", 0.0) > 0.0 and live_src is None:
                n = len(infl_vals)
                total = getattr(self, "total_steps", None) or 600
                cur = len(getattr(self, "log", []) or [])   # журнал растёт на один шаг за вызов
                if getattr(self, "total_steps", None) is None:
                    self.total_steps = total
                pos = int(round(cur / max(1, total - 1) * (n - 1))) if n > 1 else 0
                c = float(getattr(cfg_, "inflow_coupling", 0.0))
                if str(getattr(cfg_, "inflow_stream_mode", "global") or "global") == "spatial":
                    grid = cfg_.grid
                    per_row = [infl_vals[(pos + int(round(row / max(1, grid - 1) * (n - 1)))) % n]
                               for row in range(grid)]
                    col = torch.tensor(per_row, device=self.device).view(-1, 1)
                    self.pond.state.income_scale.copy_((1.0 + c * (2.0 * col - 1.0)).expand(grid, grid))
                else:
                    self.pond.state.income_scale.fill_(1.0 + c * (2.0 * infl_vals[pos] - 1.0))
            if self.update_probability >= 1.0:
                self.state = self.rule(self.state, self.genome)
            else:
                # абляция: часть клеток пропускает обновление (шум в динамике)
                new_state = self.rule(self.state, self.genome)
                base = float(self.update_probability)
                mode = str(getattr(self.pond.cfg, "trait_effect_mode", "invest"))
                eps = float(getattr(self.pond.cfg, "trait_effect", 0.0))
                trait = self.pond.state.tag_trait
                if mode == "update" and eps != 0.0 and trait is not None:
                    # H-ALIVE-56: признак масштабирует ЧАСТОТУ обновления клетки, а не трату.
                    alive = self.pond.state.alive
                    mean_trait = float(trait[alive].mean()) if bool(alive.any()) else 0.0
                    factor = torch.clamp(1.0 + eps * (trait - mean_trait), 0.0, 2.0)
                    keep_p = torch.clamp(base * factor, 0.0, 1.0)
                    draw = torch.rand(
                        (1, 1, self.world_cfg.grid, self.world_cfg.grid),
                        generator=self.gen, device=self.device)
                    keep = draw < keep_p.unsqueeze(0).unsqueeze(0)
                else:
                    keep = torch.rand(
                        (1, 1, self.world_cfg.grid, self.world_cfg.grid),
                        generator=self.gen,
                        device=self.device,
                    ) < base
                self.state = torch.where(keep, new_state, self.state)
        grown = self._sync_state_to_world()
        self.pond.regenerate()
        cell_stats = self.pond.step_cells()
        self._organism_mobility()
        self._plastic_mobility()
        self._flow_energy_to_state()

        births = 0
        for body in self.pond.find_buds():
            # W2-bud: почкуется ОДНА клетка тела; W2-bud-d2: до N клеток на компоненту
            for parent in self.pond.budding_parents(body):
                child = self.pond.bud(parent)
                if child is None:
                    continue
                # геном: медиана родителя и мутация. Считаем по явным координатам, а не
                # маской: родитель может быть ОДНОЙ клеткой, и тогда `[:, mask]` даёт
                # [C, 1], а `mean(dim=1, keepdim=True)` — лишнюю ось (падение 26.10).
                p_idx = parent.nonzero(as_tuple=False)
                c_idx = child.nonzero(as_tuple=False)
                if p_idx.shape[0] == 0 or c_idx.shape[0] == 0:
                    continue
                parent_genome = self.genome[0][:, p_idx[:, 0], p_idx[:, 1]].mean(
                    dim=-1, keepdim=True)
                child_genome = self.rule.mutate(
                    parent_genome.unsqueeze(0).unsqueeze(-1).unsqueeze(-1), generator=self.gen
                ).reshape(-1, 1)
                self.genome[0][:, c_idx[:, 0], c_idx[:, 1]] = child_genome
                state_mean = self.state[0][:, p_idx[:, 0], p_idx[:, 1]].mean(
                    dim=-1, keepdim=True)
                self.state[0][:, c_idx[:, 0], c_idx[:, 1]] = state_mean
                births += 1
        if self.pond.cfg.death_return > 0 and int(self.pond.state.step) % 10 == 0:
            self.pond._niche_update()
        if int(self.pond.state.step) % 5 == 0:
            self.pond.enforce_colony_types()
            # серия меток линий для метрик условия B: каждые 5 шагов, а не каждый
            tag_t = self.pond.state.tag
            if tag_t is not None and bool(self.pond.state.alive.any()):
                uniq, counts = torch.unique(tag_t[self.pond.state.alive], return_counts=True)
                self.pond.type_counts_series.append({
                    "step": int(self.pond.state.step),
                    "counts": {f"T{int(u)}": int(c)
                               for u, c in zip(uniq.tolist(), counts.tolist())},
                })
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
                # 26.10: print не должен убивать прогон. На Windows запись в закрытый
                # пайп даёт OSError [Errno 22] и падение на первом же шаге логирования.
                try:
                    print(
                        f"шаг {last['step']:5d} | живых {last['alive_cells']:5d} | "
                        f"родилось {last['born']:3d} | умерло {last['died']:4d} | "
                        f"спор заблокировано {last['spores_blocked']:3d}",
                        flush=True,
                    )
                except OSError:
                    pass
        elapsed = time.perf_counter() - t0
        return {"steps": steps, "wall_seconds": round(elapsed, 2), "final": self.log[-1] if self.log else {}}


def build_parser() -> argparse.ArgumentParser:
    """Собрать CLI. Отдельно от `main`, чтобы дефолты можно было проверить тестом.

    Дефолт CLI обязан совпадать с дефолтом `PondConfig` (тест
    `test_cli_defaults_match_pond_config`): расхождение делает прогон, запущенный
    без флага, не тем прогоном, который описан в отчёте.
    """
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
    ap.add_argument("--resource-regen", type=float, default=0.02,
                    help="приток ресурса на клетку за шаг (равновесие поля: regen*N = "
                         "потребление); H-ALIVE-29 меняет только это, не доход и не цену")
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
    ap.add_argument("--invade-min-cells", type=int, default=30,
                    help="инъекция валидна только если живых >= N (дефолт = PondConfig)")
    ap.add_argument("--mutation-rate", type=float, default=0.0,
                    help="вероятность НОВОЙ метки линии (tag) при рождении; 0 = мутаций нет")
    ap.add_argument("--mutation-trait-sigma", type=float, default=0.01,
                    help="сдвиг признака линии при мутации (масштаб признака ~1)")
    ap.add_argument("--ignition-gate", action="store_true",
                    help="запретить правилу зажигать клетку без живого 4-соседа "
                         "(пустое поле остаётся пустым, плечо пропагула)")
    ap.add_argument("--start-cells", type=int, default=4,
                    help="сколько клеток засеять на старте (0 = пустое поле, плечо resident_free)")
    ap.add_argument("--invade-placement", default="random", choices=["random", "gap"],
                    help="куда садится инокулят: random (как §10ab) или gap — в самую "
                         "далёкую от резидента свободную клетку (V8)")
    ap.add_argument("--niche-free-min", type=int, default=0,
                    help="H-ALIVE-52: учитывать подготовленные клетки только в свободной компоненте >= N")
    ap.add_argument("--pair-mode", default="same_tag", choices=["same_tag", "any_tag"],
                    help="H-ALIVE-49: пара одной метки (по умолчанию) или с любым соседом")
    ap.add_argument("--death-return", type=float, default=0.0,
                    help="W1-niche: доля взятого за жизнь ресурса, возвращаемая при смерти (0 = старая ветка)")
    ap.add_argument("--death-return-mode", default="legacy",
                    choices=["legacy", "prepared", "foreign", "density_matched",
                             "adjacent_matched", "adjacency_exact", "depleted"],
                    help="legacy: туда, где умерла; prepared: в случайные СВОБОДНЫЕ (контроль объёма)")
    ap.add_argument("--buds-per-component", type=int, default=1,
                    help="W2-bud-d2: до N бутонов на компоненту (1 = W2-bud бит-в-бит)")
    ap.add_argument("--trait-effect-mode", default="invest", choices=["invest", "update"],
                    help="H-ALIVE-56: канал признака — invest (по умолчанию) или update (частота обновления)")
    ap.add_argument("--inflow-stream", default=None,
                    help="H-ALIVE-59: JSON записанного потока (scripts/capture_stream.py), значения 0..1")
    ap.add_argument("--inflow-coupling", type=float, default=0.0,
                    help="сила связи: 0 = выключено, 1 = приток ходит от 0 до 2× базового")
    ap.add_argument("--inflow-live", default=None,
                    choices=["mic", "net", "crypto", "events", "usgs", "system"],
                    help="H-ALIVE-59: живой сигнал в реальном времени (микрофон), а не проигрывание записи")
    ap.add_argument("--inflow-live-rate", type=float, default=20.0,
                    help="частота отсчётов живого сигнала, Гц")
    ap.add_argument("--inflow-live-window", type=float, default=15.0,
                    help="окно нормировки живого сигнала, секунды")
    ap.add_argument("--inflow-live-dump", default=None,
                    help="куда записать то, что услышал мир (для аудита и повторного проигрывания)")
    ap.add_argument("--inflow-stream-mode", default="global", choices=["global", "spatial"],
                    help="global: всё поле; spatial: полосы по Y (мир видит градиент)")
    ap.add_argument("--kill-winner", type=float, default=0.0,
                    help="H-ALIVE-54: смертность пропорциональна превышению доли линии над средней (0 = выкл.)")
    ap.add_argument("--bud-refractory", type=int, default=0,
                    help="H-ALIVE-54: линия почкуется не чаще, чем раз в K шагов (0 = выключено)")
    ap.add_argument("--quota-share", type=float, default=1.0,
                    help="H-ALIVE-53: линия держит не больше q живых клеток (1.0 = выключено)")
    ap.add_argument("--one-bud-per-lineage", action="store_true",
                    help="не больше одного бутона на линию в компоненте")
    ap.add_argument("--require-placement", type=int, default=0,
                    help="гарантировать столько клеток инокулята (0 = старая ветка бит-в-бит)")
    ap.add_argument("--placement-attempts", type=int, default=5,
                    help="сколько раз перерисовывать точку подсадки, если пятно не встало")
    ap.add_argument("--budding-unit", default="colony", choices=["colony", "cell", "pair"],
                    help="кто почкуется: colony (W1, по умолчанию) или cell (W2-bud)")
    ap.add_argument("--trait-effect", type=float, default=0.0,
                    help="eps: насколько tag_trait меняет интенсивность инвестирования "
                         "(0 = признак не читается, условие E)")
    ap.add_argument("--merge-rule", default="majority",
                    choices=["majority", "mass_weighted", "keep"],
                    help="правило слияния компонент: большинство (как §10ab), лотерея по массе "
                         "(V8) или keep — никто не переписывается (H-ALIVE-28)")
    ap.add_argument("--invade-on-empty", action="store_true",
                    help="разрешить подсадку без резидента (плечо resident_free)")
    ap.add_argument("--invader-cells", type=int, default=1,
                    help="доза основателя при --type-level colony: сколько клеток ставит "
                         "инъекция (связное 4-пятно; 1 = как в серии 24.10)")
    ap.add_argument("--invade-type", type=int, default=1, choices=[0, 1],
                    help="какой тип подсаживаем: 0 = A, 1 = B")
    ap.add_argument("--type-level", default="cell", choices=["cell", "colony"],
                    help="тип у клетки или у всей колонии-компоненты (task-11)")
    ap.add_argument("--type-inherit", default="neighbours", choices=["neighbours", "parent"],
                    help="как наследуется тип при росте: voter-соседи или линия (компонента)")
    ap.add_argument("--type-start", default="a", choices=["a", "b", "mixed"],
                    help="тип стартовых клеток: все A или смешанный")
    ap.add_argument("--type-mode", default="fixed", choices=["fixed", "mixfixed", "random", "learn"],
                    help="как наследуется тип A/B: fixed | random | learn")
    ap.add_argument("--layout", default="uniform",
                    choices=["uniform", "gradient", "patches"], help="структура ресурса")
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.learn_w and args.learn_mode == "paired" and args.spore_bias != "score":
        ap.error("--learn-mode paired работает только со --spore-bias score: "
                 "парный сигнал сравнивает два веса одной политики")

    code_provenance = git_provenance()   # снимается на старте, до записи артефакта
    code_provenance["rule_sha256"] = file_sha256(args.rule_checkpoint)
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
    world.type_level = args.type_level
    world.invade_at = args.invade_at
    world.invade_share = args.invade_share
    world.invade_type = args.invade_type
    world.invade_min_cells = args.invade_min_cells
    world.invader_cells = args.invader_cells
    world.invade_placement = args.invade_placement
    world.merge_rule = args.merge_rule
    world.trait_effect = args.trait_effect
    world.budding_unit = args.budding_unit
    world.niche_free_min = args.niche_free_min
    world.pair_mode = args.pair_mode
    world.death_return = args.death_return
    world.death_return_mode = args.death_return_mode
    world.buds_per_component = args.buds_per_component
    world.one_bud_per_lineage = bool(args.one_bud_per_lineage)
    world.quota_share = float(args.quota_share)
    world.bud_refractory = int(args.bud_refractory)
    world.kill_winner = float(args.kill_winner)
    # здесь `world` — это PondConfig, а не объект прогона (проверено ошибкой AttributeError)
    if hasattr(world, "inflow_coupling"):
        world.inflow_coupling = float(args.inflow_coupling)
        world.inflow_stream_mode = str(args.inflow_stream_mode)
    if args.inflow_stream and float(args.inflow_coupling) > 0.0:
        import json as _json
        from pathlib import Path as _Path
        raw = _json.loads(_Path(args.inflow_stream).read_text(encoding="utf-8"))
        values = [float(v) for v in (raw.get("values") or [])]
        if not values:
            raise SystemExit(f"поток пуст: {args.inflow_stream}")
        world.inflow_values = values
        world.inflow_coupling = float(args.inflow_coupling)
        world.inflow_mode = str(args.inflow_stream_mode)
        world.inflow_scale = torch.ones((world.grid, world.grid), device=args.device)
    world.trait_effect_mode = str(args.trait_effect_mode)
    world.require_placement = args.require_placement
    world.placement_attempts = args.placement_attempts
    world.invade_on_empty = bool(args.invade_on_empty)
    world.start_cells = int(args.start_cells)
    world.ignition_gate = bool(args.ignition_gate)
    world.mutation_rate = args.mutation_rate
    world.mutation_trait_sigma = args.mutation_trait_sigma
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
    world.resource_regen = args.resource_regen
    # Воспроизводимость: сеем глобальные ГПСЧ сидом прогона. Без этого часть
    # случайности (например, глобальный torch-ГПСЧ в служебных операциях) шла мимо
    # `self.gen`, и один и тот же сид давал разные pop_time (проверено 24.10).
    torch.manual_seed(int(args.seed))
    random.seed(int(args.seed))
    try:
        import numpy as _np

        _np.random.seed(int(args.seed))
    except ImportError:
        pass

    live = None
    if args.inflow_live:
        import sys as _sys
        _scripts = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "scripts")
        if _scripts not in _sys.path:
            _sys.path.insert(0, _scripts)
        import stream_sources as _ss
        src = _ss.make(args.inflow_live, rate=args.inflow_live_rate,
                       window_s=getattr(args, "inflow_live_window", 15.0)).start()
        live = {"src": src}
        world.inflow_record = []

    run = PondRun(world_cfg=world, seed=args.seed, device=args.device,
                  rule_checkpoint=args.rule_checkpoint)
    if live is not None:
        world.inflow_live = live["src"]
        world.inflow_coupling = float(args.inflow_coupling)
        world.inflow_stream_mode = str(args.inflow_stream_mode)
        world.inflow_scale = torch.ones((world.grid, world.grid), device=args.device)
        run.pond.state.income_scale = world.inflow_scale
        run.pond.cfg.inflow_coupling = float(args.inflow_coupling)
        run.pond.cfg.inflow_stream_mode = str(args.inflow_stream_mode)
    if getattr(world, "inflow_scale", None) is not None:
        run.pond.state.income_scale = world.inflow_scale
    run.snapshot_every = args.snapshot_every
    run.update_probability = args.update_probability
    if args.abiotic:
        # контроль «среда без организмов»: гоняем только бюджет среды, без правила
        # (иначе обученное правило самопроизвольно зажигает клетки из нулевого поля)
        from world.pond import Pond
        pond = Pond(world, device=args.device, seed=args.seed)
        for _ in range(args.steps):
            pond.state.step += 1
            pond.regenerate()
        summary = {
            "steps": args.steps,
            "abiotic": True,
            "resource_mean": round(float(pond.state.resource.mean()), 5),
            "resource_max_field": round(float(pond.state.resource.max()), 5),
            "resource_total": round(float(pond.state.resource.sum()), 3),
            "final": {"alive_cells": 0, "born": 0, "died": 0},
            "pop_time": 0,
        }
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump({"summary": summary, "log": []}, fh, ensure_ascii=False, indent=2)
        _safe_print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    run.seed(cells=int(args.start_cells), energy=8.0)
    summary = run.run(args.steps, log_every=max(1, args.steps // 10))
    summary["clonal_attached"] = run.clonal_attached
    summary["clonal_separate"] = run.clonal_separate
    total = run.clonal_attached + run.clonal_separate
    summary["clonal_fraction"] = (run.clonal_attached / total) if total else None
    summary["deaths_by_zone"] = dict(run.pond.state.deaths_by_zone)
    # ресурс по зонам в финале и на шаге инвазии (§10ai: отличить «не хватает ресурса»
    # от «механика съедает»)
    summary["resource_zones_final"] = resource_zones(run.pond)
    summary.update({("final_" + k): v for k, v in resource_zones(run.pond).items()})
    summary.update(invasion_resource_block(run.pond, run.log))
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
    summary["thr_series"] = getattr(run.pond, "thr_series", [])[:20]
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
    summary["type_level"] = getattr(run.world_cfg, "type_level", "cell")
    summary["invader_share_after"] = getattr(run.pond, "invasion_share_after", None)
    summary["colony_cells_at_invasion"] = int(getattr(run.pond, "colony_cells_at_invasion", 0))
    summary["injection_share_actual"] = getattr(run.pond, "injection_share_actual", None)
    summary["invader_cells"] = int(getattr(run.pond, "invader_cells_requested", 0))
    summary["invader_cells_actual"] = int(getattr(run.pond, "invader_cells_actual", 0))
    # V1c: диагностика подсадки (None в старой ветке)
    if getattr(run.pond, "cfg", None) is not None and run.pond.cfg.death_return > 0:
        vals = sorted(run.pond.resource_at_death)
        n = len(vals)
        summary["death_return"] = float(run.pond.cfg.death_return)
        summary["death_return_mode"] = str(run.pond.cfg.death_return_mode)
        summary["returned_total"] = round(float(run.pond.returned_total), 4)
        summary["resource_at_death_median"] = round(vals[n // 2], 5) if n else None
        summary["resource_at_death_n"] = n
        summary["prepared_cells_total"] = len(run.pond.niche_log)
        summary["offspring_in_prepared_k"] = int(run.pond.niche_hit_same)
        summary["prepared_occupied_any_k"] = int(run.pond.niche_hit_any)
        summary["prepared_expected_hits"] = round(float(run.pond.niche_expected), 3)
        # H-ALIVE-52: та же статистика, но только по подготовленным клеткам в свободной компоненте >= N
    free_min = int(getattr(run.pond.cfg, "niche_free_min", 0) or 0)
    if free_min > 0:
        entries = run.pond.niche_log
        kept = [e for e in entries if int(e.get("free_comp") or 0) >= free_min]
        summary["niche_free_min"] = free_min
        summary["prepared_cells_filtered"] = len(kept)
        summary["prepared_cells_total_all"] = len(entries)
        summary["same_share_filtered"] = (round(sum(1 for e in kept if e["hit_same"]) / len(kept), 4)
                                          if kept else None)
        summary["any_share_filtered"] = (round(sum(1 for e in kept if e["hit_any"]) / len(kept), 4)
                                         if kept else None)
        comps = sorted(int(e.get("free_comp") or 0) for e in entries)
        summary["free_comp_median"] = comps[len(comps) // 2] if comps else None
        summary["free_comp_q90"] = comps[int(0.9 * (len(comps) - 1))] if comps else None
    if getattr(run.pond, "niche_levels", None):
            summary["niche_levels"] = {str(k): v for k, v in sorted(run.pond.niche_levels.items())}
    if getattr(run.pond.cfg, "budding_unit", "") == "pair":
        summary["pair_degenerate_k"] = int(getattr(run.pond, "pair_degenerate", 0))
    if float(getattr(run.pond.cfg, "kill_winner", 0.0) or 0.0) > 0.0:
        killed_kw = int(getattr(run.pond, "killed_by_kill_winner", 0))
        died_all = int(getattr(run.pond.state, "died", 0) or 0)
        summary["kill_winner"] = float(getattr(run.pond.cfg, "kill_winner", 0.0))
        summary["killed_by_kill_winner"] = killed_kw
        summary["died_total"] = died_all
        # доля смертей, созданных механизмом: критерий чувствительности пре-регистрации (0.05–0.5)
        summary["kill_winner_death_share"] = (round(killed_kw / died_all, 4) if died_all else None)
    if int(getattr(run.pond.cfg, "bud_refractory", 0) or 0) > 0:
        summary["bud_refractory"] = int(getattr(run.pond.cfg, "bud_refractory", 0))
        summary["buds_blocked_by_refractory"] = int(getattr(run.pond, "buds_blocked_by_refractory", 0))
    blk = int(getattr(run.pond, "buds_blocked_by_quota", 0))
    if float(getattr(run.pond.cfg, "quota_share", 1.0) or 1.0) < 1.0:
        summary["quota_share"] = float(getattr(run.pond.cfg, "quota_share", 1.0))
        summary["buds_blocked_by_quota"] = blk
        spores_tot = int(sum(int(v) for v in (getattr(run.pond, "lineage_spores", {}) or {}).values()))
        summary["buds_successful"] = spores_tot
        summary["buds_blocked_share"] = (round(blk / (blk + spores_tot), 4)
                                         if blk + spores_tot > 0 else None)
    summary["free_cells_at_injection"] = getattr(run.pond, "free_cells_at_injection", None)
    summary["max_free_component_at_injection"] = getattr(
        run.pond, "max_free_component_at_injection", None)
    summary["placement_attempts_used"] = getattr(run.pond, "placement_attempts_used", None)
    summary["rejected_by_placement"] = bool(getattr(run.pond, "rejected_by_placement", False))
    summary["invader_cells_state_after_injection"] = getattr(
        run.pond, "invader_cells_state_after_injection", None)
    summary["config"] = {**config_block(run.world_cfg), **code_provenance}
    summary.update(generation_block(getattr(run.pond, "division_parent_ages", []),
                                    getattr(run.pond, "division_oldest_ages", [])))
    summary.update(tag_metrics_block(run.pond))
    summary.update(final_map_block(run.pond))
    summary["design"] = 3
    summary["injection_invalid"] = bool(getattr(run.pond, "injection_invalid", False))
    summary["w_final"] = float(run.pond.w)
    if getattr(run.pond.state, "w_cell", None) is not None and run.pond.state.alive.any():
        wcel = run.pond.state.w_cell[run.pond.state.alive]
        summary["w_cell_mean"] = float(wcel.mean())
        summary["w_cell_std"] = float(wcel.std())
    if live is not None:
        info = live["src"].stop()
        rec = list(getattr(world, "inflow_record", []) or [])
        summary.setdefault("live_stream", {}).update(info)
        summary["live_stream"]["values_seen"] = rec[:2000]
        if args.inflow_live_dump:
            try:
                import json as _json2
                from pathlib import Path as _Path2
                _p = _Path2(args.inflow_live_dump)
                _p.parent.mkdir(parents=True, exist_ok=True)
                _p.write_text(_json2.dumps({"source": args.inflow_live, "rate_hz": args.inflow_live_rate,
                                            "coupling": float(args.inflow_coupling),
                                            "values": rec, "raw": info},
                                           ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8", newline="\n")
            except Exception:
                pass
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "log": run.log}, fh, ensure_ascii=False, indent=2)
    _safe_print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.snapshots_out and run.snapshots:
        import numpy as _np
        _np.savez_compressed(
            args.snapshots_out,
            steps=_np.array([s["step"] for s in run.snapshots]),
            alive=_np.array([s["alive"] for s in run.snapshots]),
            energy=_np.array([s["energy"] for s in run.snapshots]),
        )
        _safe_print(f"[pond] снимков сохранено: {len(run.snapshots)} -> {args.snapshots_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
