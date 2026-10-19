"""
wp4_delta_profile.py — дискриминатор H-C из WP4: использует ли CellBrain
локальную структуру вообще, или он выдаёт почти постоянную дельту.

Формулировка проверки. Модель §12.2.2 получает окрестность Мура (9·C=144
канала) и обязана реагировать на ГРАНИЦУ паттерна сильнее, чем на однородный
фон: если |delta| в клетках с неоднородной окрестностью статистически не
отличается от |delta| в однородных клетках, ёмкость/веса роли не играют —
сеть выучила константу, и никакой hidden_dim ей не поможет. Это более
сильное и более дешёвое утверждение, чем «гистограмма край-vs-центр», которую
план предлагал изначально: она отделяет геометрию паттерна от границы грида
(reflect-pad), а нас интересует именно реакция на структуру.

Замер делается для свежей модели (до обучения) и для чекпоинтов
сколлапсировавших гейтных прогонов.

Запуск:  python wp4_delta_profile.py [--seeds 42,101]
"""

import argparse

import json

import os

# §9.2: config раньше torch.

import config

import torch


def _structure_masks(state):
    """
    (edge, uniform): клетки, у которых в окрестности Мура есть перепад
    видимого канала, против клеток с однородной окрестностью.
    """
    visible = state[:, config.VISIBLE_CHANNEL : config.VISIBLE_CHANNEL + 1, :, :]
    padded = torch.nn.functional.pad(visible, (1, 1, 1, 1), mode="reflect")
    neigh_max = torch.zeros_like(visible)
    neigh_min = torch.zeros_like(visible)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            window = padded[:, :, dy : dy + visible.shape[2], dx : dx + visible.shape[3]]
            neigh_max = torch.maximum(neigh_max, window)
            neigh_min = torch.minimum(neigh_min, window)
    spread = (neigh_max - neigh_min).squeeze(1)  # (B, H, W) — ровно как magnitude
    edge = spread > 1e-3
    return edge, ~edge


def profile(model, structured, own_state, label):
    """
    Ответ модели на СТРУКТУРИРОВАННЫЙ живой вход (собранное кольцо) и на её
    собственный финальный state.

    Структурированный вход нужен специально: на мёртвом однородном поле
    перепада соседей нет физически, и edge/uniform там совпадают по построению.
    Вопрос H-C — «различает ли сеть границу паттерна», — имеет смысл только
    тогда, когда граница на входе есть.
    """
    from nca_core import run_steps_no_grad

    with torch.no_grad():
        delta = model.get_delta(structured)
        rolled = run_steps_no_grad(model, structured.clone(), config.TRAIN_BPTT_CURRICULUM[0])
        own_alive = float(
            (torch.sigmoid(own_state[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD).float().mean().item()
        )
    magnitude = delta.abs().mean(dim=1)  # (B, H, W)
    edge, uniform = _structure_masks(structured)
    out = {
        "weights": label,
        "abs_delta_mean": float(magnitude.mean().item()),
        "abs_delta_at_edge": float(magnitude[edge].mean().item()) if bool(edge.any()) else None,
        "abs_delta_at_uniform": float(magnitude[uniform].mean().item()) if bool(uniform.any()) else None,
        "edge_share": float(edge.float().mean().item()),
        "alive_fraction_own_state": own_alive,
        # Сколько шагов развёртки ткань остаётся живой: если живость гаснет за
        # TRAIN_BPTT шагов, лосс считается на мёртвом состоянии и разговор о
        # ёмкости бессмыслен.
        "alive_fraction_after_rollout": float(
            (torch.sigmoid(rolled[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD).float().mean().item()
        ),
    }
    ratio = None
    if out["abs_delta_at_edge"] is not None and out["abs_delta_at_uniform"] is not None:
        ratio = out["abs_delta_at_edge"] / max(out["abs_delta_at_uniform"], 1e-9)
    out["edge_over_uniform"] = ratio
    return out


def main(seeds):
    from nca_core import NeuralCellularAutomaton
    from target_patterns import create_target

    target = create_target(device=config.DEVICE)
    batch = config.TRAIN_BATCH_SIZE
    rows = []

    # Структурированный живой вход: канал 0 уверенно рисует цель (sigmoid(±5)),
    # alive-канал открыт везде, остальные нули — «ткань здорова и видит форму».
    structured = torch.zeros(
        batch, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE, device=config.DEVICE
    )
    structured[:, config.VISIBLE_CHANNEL : config.VISIBLE_CHANNEL + 1] = 5.0 * (
        2.0 * target.expand(batch, -1, -1, -1) - 1.0
    )
    structured[:, config.ALIVE_CHANNEL] = 5.0
    dead_own = torch.zeros_like(structured)

    torch.manual_seed(42)
    fresh = NeuralCellularAutomaton().to(config.DEVICE)
    fresh.eval()
    rows.append(profile(fresh, structured, dead_own, "fresh"))

    for seed in seeds:
        path = os.path.join(config.CHECKPOINT_DIR, f"gate_layer1_seed{seed}", "nca_final.pt")
        if not os.path.exists(path):
            continue
        payload = torch.load(path, map_location=config.DEVICE, weights_only=False)
        model = NeuralCellularAutomaton().to(config.DEVICE)
        model.load_state_dict(payload["model_state_dict"])
        model.eval()
        own = payload["state"]
        if own.shape[0] >= batch:
            own = own[:batch]
        rows.append(profile(model, structured, own, f"gate_seed{seed}"))

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))

    out_dir = os.path.join("experiments", "E02_pattern")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "delta_profile.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "spec_version": config.SPEC_VERSION,
                "revision": config.SPEC_REVISION,
                "hidden_dim": int(config.CELL_BRAIN_HIDDEN_DIM),
                "input_channels": int(config.CELL_BRAIN_INPUT_CHANNELS),
                "runs": rows,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
    print(f"[h-c] записано: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=str, default="42,101")
    args = parser.parse_args()
    main(seeds=[int(s) for s in args.seeds.split(",")])
