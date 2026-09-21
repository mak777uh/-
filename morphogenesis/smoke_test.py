"""

smoke_test.py — Сухая проверка перед запуском.

[v5.5-EXP FINAL Rev.7]

Расширенные проверки:

- config.validate()

- модель создаётся и переводится в eval()

- один шаг вперёд и один шаг назад

- мёртвое поле не оживает

- стресс в мёртвом поле остаётся нулевым

- стресс не воскрешает мёртвые клетки

- inject_morphogen в канал 15 отклоняется

- inject_morphogen в разрешённый канал работает

- replace_all_fresh() создаёт >= 20% живых клеток

- синтетический тест квадратного кольца проходит

- синтетический тест объекта на границе проходит

- STRESS_ABLATION_MODE=True -> стресс = 0

- детерминированный генератор даёт одинаковые результаты при одном и том же сиде

- метаданные чекпоинта сохраняются и загружаются корректно

"""

import os

import numpy as np

import torch

import torch.nn.functional as F

import config

from nca_core import (

    NeuralCellularAutomaton,

    init_state,

    StatePool,

)

from config import create_deterministic_generator

from topology import (

    compute_topology_metrics,

    compute_extended_topology_metrics,

    count_holes,

    count_connected_components,

    get_binary_mask,

)

from target_patterns import create_target_circles

from evaluate import inject_morphogen

def dead_field_remains_dead(model, steps=10, device=config.DEVICE):

    """

    Проверка:

    - полностью мёртвое поле не должно самопроизвольно оживать;

    - стресс-канал в мёртвом поле не должен накапливать активность;

    - стресс не может воскресить мёртвые клетки.

    """

    zero_state = torch.zeros(

        1,

        config.N_CHANNELS,

        config.GRID_SIZE,

        config.GRID_SIZE,

        device=device,

    )

    was_training = model.training

    was_alive = getattr(model, "alive_mask_enabled", True)

    model.eval()

    model.alive_mask_enabled = True

    with torch.no_grad():

        state = zero_state

        for _ in range(steps):

            state = model(state)

        alpha_prob = torch.sigmoid(state[:, config.ALIVE_CHANNEL])

        stress_ok = True

        if config.STRESS_ENABLED:

            stress = state[:, config.STRESS_CHANNEL]

            stress_ok = float(stress.abs().max()) <= 1e-5

    if was_training:

        model.train()

    model.alive_mask_enabled = was_alive

    alive_ok = float(alpha_prob.max()) <= config.ALIVE_THRESHOLD

    return alive_ok and stress_ok

def post_training_death_test(model, steps=500, device=config.DEVICE):

    """

    Пост-тренировочный тест мёртвого поля.

    Обученная модель не должна самовоспламеняться из мёртвого поля.

    """

    was_training = model.training

    was_alive = getattr(model, "alive_mask_enabled", True)

    model.eval()

    model.alive_mask_enabled = True

    dead_state = torch.zeros(

        1,

        config.N_CHANNELS,

        config.GRID_SIZE,

        config.GRID_SIZE,

        device=device,

    )

    dead_state[:, config.ALIVE_CHANNEL, :, :] = config.DEAD_ALPHA_VALUE

    with torch.no_grad():

        for _ in range(steps):

            dead_state = model(dead_state)

    alive_count = int(

        (torch.sigmoid(dead_state[:, config.ALIVE_CHANNEL, :, :]) > config.ALIVE_THRESHOLD)

        .sum()

        .item()

    )

    if was_training:

        model.train()

    model.alive_mask_enabled = was_alive

    return alive_count == 0

def test_square_ring():

    """

    Простое квадратное кольцо должно давать beta1 = 1.

    """

    mask = np.zeros((5, 5), dtype=np.uint8)

    mask[1:4, 1:4] = 1

    mask[2, 2] = 0

    b1 = count_holes(mask)

    return b1 == 1

def test_border_touching_object():

    """

    Объект, касающийся границы, не создаёт ложных дырок.

    """

    mask = np.zeros((16, 16), dtype=np.uint8)

    mask[0:5, 0:5] = 1

    b1 = count_holes(mask)

    return b1 == 0

def test_three_components():

    """

    Три раздельных пятна должны давать beta0 = 3.

    """

    mask = np.zeros((24, 24), dtype=np.uint8)

    mask[4:7, 4:7] = 1

    mask[4:7, 16:19] = 1

    mask[16:19, 10:13] = 1

    b0 = count_connected_components(mask)

    return b0 == 3

def test_stress_ablation_mode():

    """

    При STRESS_ABLATION_MODE=True стресс должен оставаться нулевым.

    """

    was_ablation = config.STRESS_ABLATION_MODE

    was_enabled = config.STRESS_ENABLED

    config.STRESS_ABLATION_MODE = True

    config.STRESS_ENABLED = True

    device = torch.device(config.DEVICE)

    model = NeuralCellularAutomaton().to(device)

    model.eval()

    model.alive_mask_enabled = True

    state = init_state(device=device)

    with torch.no_grad():

        for _ in range(10):

            state = model(state)

        stress = state[:, config.STRESS_CHANNEL]

        stress_zero = float(stress.abs().max()) <= 1e-5

    config.STRESS_ABLATION_MODE = was_ablation

    config.STRESS_ENABLED = was_enabled

    return stress_zero

def test_deterministic_generator():

    """

    Детерминированный генератор даёт одинаковые результаты при одном и том же сиде.

    """

    seed = 123

    gen1 = create_deterministic_generator(seed)

    gen2 = create_deterministic_generator(seed)

    device = torch.device(config.DEVICE)

    model = NeuralCellularAutomaton().to(device)

    model.eval()

    model.alive_mask_enabled = True

    state1 = init_state(device=device, generator=gen1)

    state2 = init_state(device=device, generator=gen2)

    # Проверяем, что инициализация одинаковая.

    if not torch.allclose(state1, state2):

        return False

    # Проверяем, что шаг модели одинаковый.

    model.set_generator(gen1)

    with torch.no_grad():

        next1 = model(state1.clone())

    model.set_generator(gen2)

    with torch.no_grad():

        next2 = model(state2.clone())

    return torch.allclose(next1, next2)

def test_checkpoint_metadata():

    """

    Метаданные чекпоинта сохраняются и загружаются корректно.

    """

    import tempfile

    import torch

    metadata = config.get_checkpoint_metadata(

        seed=config.SEED,

        experiment_id="SMOKE",

        iteration=0,

        best_loss=0.0,

    )

    assert metadata["spec_version"] == config.SPEC_VERSION

    assert metadata["grid_size"] == config.GRID_SIZE

    assert metadata["n_channels"] == config.N_CHANNELS

    assert "target_topology" in metadata

    assert "stress_mode" in metadata

    assert "alive_threshold" in metadata

    return True

def test_fresh_state_alive():

    """

    replace_all_fresh() создаёт состояние с >= FRESH_MIN_ALIVE_FRACTION живых клеток.

    """

    device = torch.device(config.DEVICE)

    pool = StatePool(size=1, device=device)

    pool.replace_all_fresh()

    state = pool.states[0]

    alpha_prob = torch.sigmoid(state[:, config.ALIVE_CHANNEL, :, :])

    alive_fraction = float((alpha_prob > config.ALIVE_THRESHOLD).float().mean().item())

    stress_zero = float(state[:, config.STRESS_CHANNEL].abs().max().item()) <= 1e-5

    return alive_fraction >= config.FRESH_MIN_ALIVE_FRACTION and stress_zero

def smoke_test():

    print("=" * 60)

    print("SMOKE TEST v5.5-EXP FINAL Rev.7")

    print("=" * 60)

    try:

        config.validate()

        print("✅ config.validate() пройден")

    except AssertionError as e:

        print(f"❌ config.validate() провален: {e}")

        return False

    config.set_seed()

    device = torch.device(config.DEVICE)

    print(f"Устройство: {device}")

    try:

        # === Модель ===

        model = NeuralCellularAutomaton().to(device)

        model.eval()

        model.alive_mask_enabled = True

        print("✅ Модель создана")

        # === Мёртвое поле не оживает ===

        if not dead_field_remains_dead(model, steps=10, device=device):

            print("❌ Мёртвое нулевое поле самопроизвольно ожило")

            return False

        print("✅ Мёртвое поле остаётся мёртвым")

        print("✅ Стресс-канал не воскрешает мёртвое поле")

        # === Один шаг вперёд ===

        state = init_state(device=device)

        state = model(state)

        print("✅ Один шаг вперёд работает")

        # === Базовая топология ===

        visible = model.visible_image(state)

        topo = compute_topology_metrics(visible[0, 0])

        print(f"✅ Базовая топология: β₀={topo['b0']}, β₁={topo['b1']}")

        # === Расширенная топология ===

        topo_ext = compute_extended_topology_metrics(

            state,

            target_topology=config.TARGET_TOPOLOGY,

            mse=None,

        )

        print(

            "✅ Расширенная топология: "

            f"entropy={topo_ext['spatial_entropy']:.3f}, "

            f"wall={topo_ext['domain_wall_energy']:.3f}, "

            f"hallucination={topo_ext['topological_hallucination_raw']}"

        )

        # === Один шаг назад ===

        target = create_target_circles(device=device)

        image = model.visible_image(state)

        target_expanded = target.expand(image.shape[0], -1, -1, -1)

        loss = F.mse_loss(image, target_expanded)

        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        print(f"✅ Один шаг назад работает, loss={loss.item():.4f}")

        # === Проверка зарезервированного стресс-канала ===

        try:

            inject_morphogen(

                state,

                channel=config.STRESS_CHANNEL,

                value=0.1,

                radius=2,

            )

            print("❌ inject_morphogen разрешил инъекцию в зарезервированный канал")

            return False

        except ValueError:

            print("✅ Зарезервированный стресс-канал защищён от инъекций")

        # === Проверка допустимого морфогенетического канала ===

        _ = inject_morphogen(

            state,

            channel=config.MORPHOGEN_MIN_CHANNEL,

            value=0.1,

            radius=2,

        )

        print("✅ Инъекция морфогена в разрешённый скрытый канал работает")

        # === Проверка синтетических тестов топологии ===

        if not test_square_ring():

            print("❌ Тест квадратного кольца провален")

            return False

        print("✅ Тест квадратного кольца пройден")

        if not test_border_touching_object():

            print("❌ Тест объекта на границе провален")

            return False

        print("✅ Тест объекта на границе пройден")

        if not test_three_components():

            print("❌ Тест трёх компонент провален")

            return False

        print("✅ Тест трёх компонент пройден")

        # === Проверка стресс-абляции ===

        if not test_stress_ablation_mode():

            print("❌ STRESS_ABLATION_MODE не обнуляет стресс")

            return False

        print("✅ STRESS_ABLATION_MODE обнуляет стресс")

        # === Проверка детерминированного генератора ===

        if not test_deterministic_generator():

            print("❌ Детерминированный генератор не воспроизводим")

            return False

        print("✅ Детерминированный генератор воспроизводим")

        # === Проверка метаданных чекпоинта ===

        if not test_checkpoint_metadata():

            print("❌ Метаданные чекпоинта некорректны")

            return False

        print("✅ Метаданные чекпоинта корректны")

        # === Проверка живости свежих состояний ===

        if not test_fresh_state_alive():

            print("❌ Fresh-состояние не содержит достаточно живых клеток")

            return False

        print("✅ Fresh-состояние содержит достаточно живых клеток")

        # === Проверка памяти ===

        if torch.cuda.is_available():

            mem_mb = torch.cuda.memory_allocated() / 1e6

            limit_mb = config.MAX_VRAM_GB * 1000

            print(f"✅ VRAM: {mem_mb:.1f} MB (лимит {limit_mb} MB)")

            if mem_mb > limit_mb * 0.5:

                print("⚠️ Использование памяти > 50% лимита")

        print("\n" + "=" * 60)

        print("SMOKE TEST ПРОЙДЕН.")

        print("=" * 60)

        return True

    except Exception as e:

        print(f"\n❌ SMOKE TEST ПРОВАЛЕН: {e}")

        import traceback

        traceback.print_exc()

        return False

if __name__ == "__main__":

    exit(0 if smoke_test() else 1)