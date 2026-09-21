"""

train.py — Основной цикл обучения с Truncated BPTT.

[v5.5-EXP FINAL Rev.7]

Ключевые требования:

- обучение по MSE + L1;

- супервизия альфа-канала;

- пул состояний возвращает (state, index);

- state.detach() после каждого прогона;

- model.alive_mask_enabled = iteration >= ALIVE_WARMUP_ITERS;

- pool.replace_all_fresh() при iteration == ALIVE_WARMUP_ITERS;

- NaN-гард;

- OOM-гард;

- атомарное сохранение чекпоинтов с метаданными;

- восстановление optimizer, scheduler, pool, best_loss при resume;

- логирование топологии, стресса, симметричного Chamfer как мониторинг;

- pool.maybe_reset(sim_step) — привязка к sim_step;

- использование детерминированного torch.Generator для всех стохастических операций;

- сохранение метаданных чекпоинта при каждом сохранении.

"""

import json

import os

import tempfile

import time

import numpy as np

import torch

import torch.nn.functional as F

import torch.optim as optim

from torch.optim.lr_scheduler import CosineAnnealingLR

from torch.utils.tensorboard import SummaryWriter

import config

import evaluate

from nca_core import (

    NeuralCellularAutomaton,

    run_steps,

    init_state,

    StatePool,

    create_deterministic_generator,

)

from topology import compute_topology_metrics, get_binary_mask

from target_patterns import create_target_circles

from evaluate import compute_symmetric_chamfer_error

def check_memory():

    if torch.cuda.is_available():

        allocated = torch.cuda.memory_allocated() / 1e9

        reserved = torch.cuda.memory_reserved() / 1e9

        if allocated > config.MAX_VRAM_GB - 1.0 or reserved > config.MAX_VRAM_GB - 1.0:

            torch.cuda.empty_cache()

            return True

    return False

def get_current_unroll(iteration):

    for i in range(len(config.UNROLL_CURRICULUM_AT) - 1, -1, -1):

        if iteration >= config.UNROLL_CURRICULUM_AT[i]:

            return config.UNROLL_CURRICULUM[i]

    return config.UNROLL_CURRICULUM[0]

def compute_loss(state, target, model, l1_weight=config.L1_REG_WEIGHT):

    """

    Только pattern_loss + L1.

    Delta считается С ГРАДИЕНТАМИ.

    [v5.5-EXP FINAL Rev.7]:

    - Супервизия альфа-канала.

    - MSE считается по всей сетке, включая мёртвые зоны.

    """

    # Видимый канал.

    image = model.visible_image(state)

    target_expanded = target.expand(image.shape[0], -1, -1, -1)

    pattern_loss = F.mse_loss(image, target_expanded)

    # Альфа-канал.

    alpha = torch.sigmoid(state[:, config.ALIVE_CHANNEL:config.ALIVE_CHANNEL + 1])

    target_alpha = (target_expanded > 0).float()

    alpha_loss = F.mse_loss(alpha, target_alpha)

    # L1 регуляризация.

    delta = model.get_delta(state)

    l1_reg = torch.mean(torch.abs(delta))

    total_loss = pattern_loss + alpha_loss + l1_weight * l1_reg

    loss_dict = {

        "total": total_loss.item(),

        "pattern": pattern_loss.item(),

        "alpha": alpha_loss.item(),

        "l1_reg": l1_reg.item(),

    }

    return total_loss, loss_dict

def atomic_save(obj, path):

    dir_name = os.path.dirname(path) or "."

    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")

    try:

        with os.fdopen(fd, "wb") as f:

            torch.save(obj, f)

        os.replace(tmp_path, path)

    except BaseException:

        if os.path.exists(tmp_path):

            os.remove(tmp_path)

        raise

def append_to_log(log_path, entry):

    with open(log_path, "a", encoding="utf-8") as f:

        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def _compute_symmetric_chamfer_for_state(model, state, target):

    """

    Симметричный Chamfer как мониторинг (не лосс).

    """

    pred_mask = get_binary_mask(state)

    target_mask = (target[0, 0].detach().cpu().numpy() > 0.5).astype(np.uint8)

    return compute_symmetric_chamfer_error(pred_mask, target_mask)

def train(resume_from=None, experiment_id="E02", seed=None):

    print("=" * 60)

    print("PROJECT MORPHOGENESIS: Запуск обучения")

    print("=" * 60)

    config.validate()

    if seed is None:

        seed = config.SEED

    config.set_seed(seed)

    # Детерминированный генератор для всех стохастических операций.

    generator = create_deterministic_generator(seed)

    for d in [

        config.CHECKPOINT_DIR,

        config.LOG_DIR,

        config.OUTPUT_DIR,

        config.FRAMES_DIR,

        config.EVAL_DIR,

    ]:

        os.makedirs(d, exist_ok=True)

    log_dir = os.path.join(config.LOG_DIR, experiment_id)

    os.makedirs(log_dir, exist_ok=True)

    device = torch.device(config.DEVICE)

    print(f"Устройство: {device}")

    model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)

    model.set_generator(generator)

    optimizer = optim.AdamW(

        model.parameters(),

        lr=config.LEARNING_RATE,

        weight_decay=config.WEIGHT_DECAY,

    )

    target = create_target_circles(

        grid_size=config.GRID_SIZE,

        n_circles=config.TARGET_COMPONENTS,

        device=device,

    )

    pool = StatePool(size=config.STATE_POOL_SIZE, device=device, generator=generator)

    start_iteration = 1

    best_loss = float("inf")

    scheduler = None

    checkpoint = None

    if resume_from and os.path.exists(resume_from):

        checkpoint = torch.load(

            resume_from,

            map_location=device,

            weights_only=False,

        )

        if "grid_size" in checkpoint and checkpoint["grid_size"] != config.GRID_SIZE:

            raise ValueError(

                f"Несовместимый чекпоинт: grid_size={checkpoint['grid_size']}, "

                f"конфиг={config.GRID_SIZE}"

            )

        if "n_channels" in checkpoint and checkpoint["n_channels"] != config.N_CHANNELS:

            raise ValueError(

                f"Несовместимый чекпоинт: n_channels={checkpoint['n_channels']}, "

                f"конфиг={config.N_CHANNELS}"

            )

        # Загрузка с метаданными.

        if "metadata" in checkpoint:

            metadata = checkpoint["metadata"]

            if metadata.get("spec_version") != config.SPEC_VERSION:

                print(

                    f"⚠️ Предупреждение: чекпоинт имеет версию "

                    f"{metadata.get('spec_version')}, "

                    f"ожидалась {config.SPEC_VERSION}"

                )

        model.load_state_dict(checkpoint["model_state_dict"])

        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        if "pool_state_dict" in checkpoint:

            pool.load_state_dict(checkpoint["pool_state_dict"])

        start_iteration = checkpoint.get("iteration", 0) + 1

        best_loss = checkpoint.get("loss", float("inf"))

        print(f"Возобновление из {resume_from}, итерация {start_iteration}")

    if start_iteration > config.TOTAL_TRAIN_ITERS:

        print(

            f"Обучение уже завершено "

            f"(итерация {start_iteration} > {config.TOTAL_TRAIN_ITERS})"

        )

        if checkpoint is not None:

            return model, checkpoint.get("state", init_state(device=device, generator=generator))

        return model, init_state(device=device, generator=generator)

    if config.LR_SCHEDULER == "cosine":

        scheduler = CosineAnnealingLR(optimizer, T_max=config.TOTAL_TRAIN_ITERS)

        if checkpoint is not None:

            if checkpoint.get("scheduler_state_dict") is not None:

                scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    writer = SummaryWriter(log_dir=log_dir)

    event_log_path = os.path.join(config.LOG_DIR, f"{experiment_id}_log.jsonl")

    print("\nПараметры:")

    print(f"  Версия: {config.SPEC_VERSION}")

    print(f"  Ревизия: {config.SPEC_REVISION}")

    print(f"  Сетка: {config.GRID_SIZE}x{config.GRID_SIZE}")

    print(f"  Пул: {config.STATE_POOL_SIZE}")

    print(f"  Итераций: {config.TOTAL_TRAIN_ITERS}")

    print(f"  Curriculum: {config.UNROLL_CURRICULUM}")

    print(f"  Stress enabled: {config.STRESS_ENABLED}")

    print(f"  Stress channel: {config.STRESS_CHANNEL}")

    print(f"  Seed: {seed}")

    print()

    nan_count = 0

    model.train()

    for iteration in range(start_iteration, config.TOTAL_TRAIN_ITERS + 1):

        t_start = time.time()

        unroll = get_current_unroll(iteration)

        if config.ALIVE_WARMUP_ITERS > 0 and iteration == config.ALIVE_WARMUP_ITERS:

            pool.replace_all_fresh()

            print(

                f"[{iteration:5d}] ♻️ Сброс пула: "

                f"включение alive-маски после warmup"

            )

        model.alive_mask_enabled = iteration >= config.ALIVE_WARMUP_ITERS

        state, pool_idx = pool.sample()

        try:

            state = run_steps(model, state, steps=unroll)

            total_loss, loss_dict = compute_loss(state, target, model)

        except RuntimeError as e:

            if "out of memory" in str(e):

                print(f"⚠️ OOM на итерации {iteration}. Заменяю состояние.")

                if torch.cuda.is_available():

                    torch.cuda.empty_cache()

                pool.replace_with_fresh(pool_idx)

                continue

            raise

        if not torch.isfinite(total_loss):

            nan_count += 1

            print(f"⚠️ NaN/Inf (подряд: {nan_count})")

            if nan_count >= 3:

                ckpt_path = os.path.join(config.CHECKPOINT_DIR, "nca_best.pt")

                if os.path.exists(ckpt_path):

                    ckpt = torch.load(

                        ckpt_path,

                        map_location=device,

                        weights_only=False,

                    )

                    model.load_state_dict(ckpt["model_state_dict"])

                    optimizer.load_state_dict(ckpt["optimizer_state_dict"])

                    if scheduler is not None and ckpt.get("scheduler_state_dict") is not None:

                        scheduler.load_state_dict(ckpt["scheduler_state_dict"])

                    print(f"Откат к {ckpt_path}")

                nan_count = 0

            pool.replace_with_fresh(pool_idx)

            continue

        else:

            nan_count = 0

        optimizer.zero_grad()

        total_loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), config.GRAD_CLIP)

        optimizer.step()

        if scheduler is not None:

            scheduler.step()

        state = state.detach()

        pool.update(state, pool_idx)

        pool.maybe_reset(iteration)

        check_memory()

        if iteration % config.LOG_EVERY == 0:

            visible = model.visible_image(state)

            topo_metrics = compute_topology_metrics(state)

            current_lr = optimizer.param_groups[0]["lr"]

            if config.STRESS_ENABLED:

                stress_mean = float(state[:, config.STRESS_CHANNEL].mean().item())

                stress_max = float(state[:, config.STRESS_CHANNEL].max().item())

            else:

                stress_mean = 0.0

                stress_max = 0.0

            # Симметричный Chamfer как мониторинг.

            sym_chamfer = _compute_symmetric_chamfer_for_state(model, state, target)

            print(

                f"[{iteration:5d}/{config.TOTAL_TRAIN_ITERS}] "

                f"loss={loss_dict['total']:.4f} "

                f"(pattern={loss_dict['pattern']:.4f}, "

                f"alpha={loss_dict['alpha']:.4f}, "

                f"l1={loss_dict['l1_reg']:.6f}) "

                f"| β₀={topo_metrics['b0']} β₁={topo_metrics['b1']} "

                f"| stress={stress_mean:.3f} "

                f"| chamfer={sym_chamfer:.3f} "

                f"| lr={current_lr:.2e} | unroll={unroll} "

                f"| {time.time() - t_start:.2f}s"

            )

            writer.add_scalar("Loss/total", loss_dict["total"], iteration)

            writer.add_scalar("Loss/pattern", loss_dict["pattern"], iteration)

            writer.add_scalar("Loss/alpha", loss_dict["alpha"], iteration)

            writer.add_scalar("Topology/beta_0", topo_metrics["b0"], iteration)

            writer.add_scalar("Topology/beta_1", topo_metrics["b1"], iteration)

            writer.add_scalar("Topology/density", topo_metrics["density"], iteration)

            writer.add_scalar("Stress/mean", stress_mean, iteration)

            writer.add_scalar("Stress/max", stress_max, iteration)

            writer.add_scalar("Chamfer/symmetric", sym_chamfer, iteration)

            writer.add_scalar("LR/current", current_lr, iteration)

            append_to_log(

                event_log_path,

                {

                    "iteration": iteration,

                    "spec_version": config.SPEC_VERSION,

                    "revision": config.SPEC_REVISION,

                    "loss": loss_dict,

                    "topology": topo_metrics,

                    "stress_mean": stress_mean,

                    "stress_max": stress_max,

                    "symmetric_chamfer_error": sym_chamfer,

                    "lr": current_lr,

                    "unroll": unroll,

                    "alive_mask_enabled": bool(model.alive_mask_enabled),

                },

            )

        if iteration % config.VISUALIZE_EVERY == 0:

            evaluate.save_frame(

                model,

                state,

                iteration,

                save_dir=config.FRAMES_DIR,

            )

        # Метаданные чекпоинта.

        checkpoint_metadata = config.get_checkpoint_metadata(

            seed=seed,

            experiment_id=experiment_id,

            iteration=iteration,

            best_loss=best_loss,

        )

        if iteration % config.SAVE_EVERY == 0:

            atomic_save(

                {

                    "iteration": iteration,

                    "model_state_dict": model.state_dict(),

                    "optimizer_state_dict": optimizer.state_dict(),

                    "scheduler_state_dict": scheduler.state_dict() if scheduler else None,

                    "pool_state_dict": pool.state_dict(),

                    "state": state,

                    "loss": loss_dict["total"],

                    "seed": seed,

                    "grid_size": config.GRID_SIZE,

                    "n_channels": config.N_CHANNELS,

                    "spec_version": config.SPEC_VERSION,

                    "revision": config.SPEC_REVISION,

                    "stress_enabled": config.STRESS_ENABLED,

                    "stress_channel": config.STRESS_CHANNEL,

                    "metadata": checkpoint_metadata,

                },

                os.path.join(config.CHECKPOINT_DIR, f"nca_iter_{iteration}.pt"),

            )

        if loss_dict["total"] < best_loss:

            best_loss = loss_dict["total"]

            checkpoint_metadata["best_loss"] = best_loss

            atomic_save(

                {

                    "iteration": iteration,

                    "model_state_dict": model.state_dict(),

                    "optimizer_state_dict": optimizer.state_dict(),

                    "scheduler_state_dict": scheduler.state_dict() if scheduler else None,

                    "pool_state_dict": pool.state_dict(),

                    "state": state,

                    "loss": best_loss,

                    "seed": seed,

                    "grid_size": config.GRID_SIZE,

                    "n_channels": config.N_CHANNELS,

                    "spec_version": config.SPEC_VERSION,

                    "revision": config.SPEC_REVISION,

                    "stress_enabled": config.STRESS_ENABLED,

                    "stress_channel": config.STRESS_CHANNEL,

                    "metadata": checkpoint_metadata,

                },

                os.path.join(config.CHECKPOINT_DIR, "nca_best.pt"),

            )

        time.sleep(0.05)

    final_path = os.path.join(config.CHECKPOINT_DIR, "nca_final.pt")

    final_metadata = config.get_checkpoint_metadata(

        seed=seed,

        experiment_id=experiment_id,

        iteration=config.TOTAL_TRAIN_ITERS,

        best_loss=best_loss,

    )

    atomic_save(

        {

            "iteration": config.TOTAL_TRAIN_ITERS,

            "model_state_dict": model.state_dict(),

            "optimizer_state_dict": optimizer.state_dict(),

            "scheduler_state_dict": scheduler.state_dict() if scheduler else None,

            "pool_state_dict": pool.state_dict(),

            "state": state,

            "loss": best_loss,

            "seed": seed,

            "grid_size": config.GRID_SIZE,

            "n_channels": config.N_CHANNELS,

            "spec_version": config.SPEC_VERSION,

            "revision": config.SPEC_REVISION,

            "stress_enabled": config.STRESS_ENABLED,

            "stress_channel": config.STRESS_CHANNEL,

            "metadata": final_metadata,

        },

        final_path,

    )

    writer.flush()

    writer.close()

    print(f"\nОбучение завершено. Лучший лосс: {best_loss:.4f}")

    return model, state

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--resume", type=str, default=None)

    parser.add_argument("--experiment", type=str, default="E02")

    parser.add_argument("--seed", type=int, default=config.SEED)

    args = parser.parse_args()

    train(resume_from=args.resume, experiment_id=args.experiment, seed=args.seed)
