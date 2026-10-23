"""cNCA: правило, модулированное геномом (организм для среды «пруд»).

Зачем: в среде нужны организмы с **наследуемым правилом**. Один общий набор весов
на всё поле + геном в каждой клетке даёт это дёшево: компонент (тело) несёт почти
однородный геном, потомок получает его копию с мутацией, а правило остаётся общим.

Схема шага:

    perception = conv3x3(state)                 # локальное восприятие, каналы состояния
    scale, bias = film(genome)                  # MLP: K -> 2 * channels
    hidden = relu(scale * perception + bias)
    update = conv1x1(hidden)                    # куда двигать состояние
    state' = (state + update) * alive_gate      # мёртвые клетки не обновляются

Геном (`genome`) — тензор (K, H, W): у каждой клетки свой вектор. Внутри одного
организма он почти одинаков (различие только от мутаций), поэтому «геном линии» —
это медиана по компоненту.

Что здесь НЕ делается: обучение. Правило не оптимизируется градиентом — его
носители отбираются средой по выживаемости. Обучение появится отдельно, если
понадобится «выучить правило до среды».
"""
from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class CNCAConfig:
    channels: int = 16
    genome_dim: int = 32
    hidden: int = 32
    alive_channel: int = 1
    alive_threshold: float = 0.5
    mutation_sigma: float = 0.05
    kernel: int = 3
    init_scale: float = 0.1           # ненулевая инициализация правила: гены должны иметь эффект
    mask_alive: bool = False          # гасить неживые клетки внутри правила (в пруду это делает мир)


class CNCA(nn.Module):
    """Общее правило с FiLM-модуляцией от генома."""

    def __init__(self, cfg: CNCAConfig | None = None) -> None:
        super().__init__()
        self.cfg = cfg or CNCAConfig()
        c = self.cfg.channels
        self.perception = nn.Conv2d(c, c, self.cfg.kernel, padding=self.cfg.kernel // 2)
        self.film = nn.Sequential(
            nn.Linear(self.cfg.genome_dim, self.cfg.hidden),
            nn.Tanh(),
            nn.Linear(self.cfg.hidden, 2 * c),
        )
        self.update = nn.Conv2d(c, c, 1)
        # ненулевая инициализация: если правило нулевое, все геномы ведут себя одинаково
        nn.init.normal_(self.update.weight, std=self.cfg.init_scale)
        nn.init.zeros_(self.update.bias)

    def alive_mask(self, state: torch.Tensor) -> torch.Tensor:
        """Маска живого по каналу живости (порог sigmoid)."""
        alpha = torch.sigmoid(state[:, self.cfg.alive_channel : self.cfg.alive_channel + 1])
        return (alpha > self.cfg.alive_threshold).to(state.dtype)

    def forward(self, state: torch.Tensor, genome: torch.Tensor) -> torch.Tensor:
        """Один шаг правила. state: (B, C, H, W); genome: (B, K, H, W)."""
        if state.dim() != 4 or genome.dim() != 4:
            raise ValueError("ожидались state (B,C,H,W) и genome (B,K,H,W)")
        b, _c, h, w = state.shape
        # FiLM: геном каждой клетки -> масштаб и сдвиг для каналов
        g = genome.permute(0, 2, 3, 1).reshape(-1, genome.shape[1])
        film = self.film(g).reshape(b, h, w, 2 * self.cfg.channels).permute(0, 3, 1, 2)
        scale, bias = film[:, : self.cfg.channels], film[:, self.cfg.channels :]
        perception = self.perception(state)
        hidden = F.relu(perception * (1.0 + scale) + bias)
        update = self.update(hidden)
        new_state = state + update
        if self.cfg.mask_alive:
            # опционально: гасить неживые клетки (в пруду за это отвечает мир)
            return new_state * self.alive_mask(new_state)
        return new_state

    @torch.no_grad()
    def mutate(self, genome: torch.Tensor, sigma: float | None = None,
               generator: torch.Generator | None = None) -> torch.Tensor:
        """Мутация генома: гауссов шум; σ задаёт среда, а не организм."""
        s = self.cfg.mutation_sigma if sigma is None else float(sigma)
        noise = torch.randn(genome.shape, generator=generator, device=genome.device)
        return genome + s * noise
