"""

test_determinism.py — слой 0 (§9.2, §19 «Слой 0», §23 «Базовые»).

Гейт спеки: два прогона одного сида дают идентичные метрики. Здесь это

проверяется на том уровне, который реально ломается в NCA-обучении — порядок

обращений к ГПСЧ. Поэтому сравнивается не «средняя величина лосса», а

побитовый отпечаток (sha256) последовательности total_loss, индексов выборки из

пула, весов модели, конечного состояния и alive-маски.

Отдельно проверяется, что torch действительно включил deterministic-режим и что

CUBLAS_WORKSPACE_CONFIG задан до импорта torch (поздняя установка переменной

окружения CUDA-детерминизм не даёт).

"""

import hashlib

import json

import os

import subprocess

import sys

import unittest

import config

import torch


def config_root():

    """Каталог пакета morphogenesis/ — от него резолвятся относительные пути config."""

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _training_fingerprint(seed, iterations=20, unroll=4):

    """

    Мини-версия цикла из train.py (пул → unroll → loss → шаг → обновление пула),

    без чекпоинтов, логов и тяжёлых метрик. Возвращает hex-отпечаток всего, что

    обязано совпасть между двумя прогонами одного сида.

    """

    from utils.determinism import init_determinism, torch_generator

    from nca_core import NeuralCellularAutomaton, StatePool, run_steps

    from target_patterns import create_target_circles

    from train import compute_loss

    report = init_determinism(seed)

    generator = torch_generator(seed)

    device = torch.device(config.DEVICE)

    model = NeuralCellularAutomaton(channels=config.N_CHANNELS).to(device)

    model.set_generator(generator)

    optimizer = torch.optim.AdamW(

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

    model.train()

    h = hashlib.sha256()

    h.update(str(seed).encode("ascii"))

    losses = []

    for _ in range(iterations):

        state, pool_idx = pool.sample()

        state = run_steps(model, state, steps=unroll)

        total_loss, loss_dict = compute_loss(state, target, model)

        losses.append(repr(float(loss_dict["total"])))

        # Индекс выборки из пула тоже часть следа: если порядок обращений к ГПСЧ

        # разъедется, лоссы могут случайно совпасть, а последовательность индексов — нет.

        h.update(int(pool_idx).to_bytes(4, "little", signed=False))

        optimizer.zero_grad()

        total_loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), config.GRAD_CLIP)

        optimizer.step()

        state = state.detach()

        pool.update(state, pool_idx)

    h.update("".join(losses).encode("ascii"))

    final_state, _ = pool.sample()

    h.update(b"params")

    for name, param in sorted(model.named_parameters(), key=lambda kv: kv[0]):

        h.update(name.encode("utf-8"))

        h.update(param.detach().cpu().contiguous().numpy().tobytes())

    h.update(b"state")

    h.update(final_state.detach().cpu().contiguous().numpy().tobytes())

    alive = torch.sigmoid(final_state[:, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD

    h.update(b"alive")

    h.update(alive.cpu().numpy().tobytes())

    return {

        "digest": h.hexdigest(),

        "first_loss": loss_dict["pattern"],

        "losses": [float(x) for x in losses],

        "determinism_report": report,

    }


_SUBPROCESS_SCRIPT = (

    "import json, os, sys;"

    "sys.path.insert(0, {pkg!r}); os.chdir({pkg!r});"

    "import config;"

    "from tests.test_determinism import _training_fingerprint;"

    "print(json.dumps(_training_fingerprint({seed}, iterations={iterations}, "

    "unroll={unroll})['digest']))"

)


class DeterminismEnvironmentTests(unittest.TestCase):

    def test_cublas_env_set_before_torch_import(self):

        """§9.2: переменная обязана появиться до импорта torch в процессе."""

        self.assertEqual(

            os.environ.get("CUBLAS_WORKSPACE_CONFIG"),

            config.CUBLAS_WORKSPACE_CONFIG,

        )

        self.assertTrue(

            config.CUBLAS_CONFIG_SET_BEFORE_TORCH_IMPORT,

            "torch импортирован раньше config: CUDA-детерминизм не гарантирован. "

            "Проверьте, что в точке входа `import config` стоит первым.",

        )

    def test_deterministic_algorithms_actually_enabled(self):

        from utils.determinism import assert_deterministic_ready, init_determinism

        report = init_determinism(config.SEED)

        self.assertTrue(torch.are_deterministic_algorithms_enabled())

        self.assertTrue(torch.backends.cudnn.deterministic)

        self.assertFalse(torch.backends.cudnn.benchmark)

        self.assertEqual(report["degradations"], [])

        # Гейт предзапуска (§23) обязан проходить в собранном окружении.

        assert_deterministic_ready(report)

    def test_entry_modules_import_config_first(self):

        """

        Статическая проверка порядка импортов: если в точке входа torch идёт раньше

        config, §9.2 нарушается молча.

        """

        entry_points = [

            "train.py",

            "smoke_test.py",

            "experiment_manager.py",

            "evaluate.py",

            "nca_core.py",

            "topology.py",

            os.path.join("cognition", "cognitive_loop.py"),

        ]

        for rel in entry_points:

            path = os.path.join(config_root(), rel)

            with open(path, "r", encoding="utf-8") as fh:

                lines = fh.read().splitlines()

            config_line = next(

                (i for i, line in enumerate(lines) if line.strip() == "import config"),

                None,

            )

            torch_line = next(

                (

                    i

                    for i, line in enumerate(lines)

                    if line.strip().startswith(("import torch", "from torch"))

                ),

                None,

            )

            self.assertIsNotNone(config_line, f"{rel}: нет `import config`")

            if torch_line is None:

                continue

            self.assertLess(

                config_line,

                torch_line,

                f"{rel}: torch импортируется до config (строка {torch_line + 1} < "

                f"{config_line + 1}) — нарушает §9.2",

            )


class LocalGeneratorTests(unittest.TestCase):

    def test_local_torch_generator_reproducible(self):

        from utils.determinism import rand_tensor, torch_generator

        a = rand_tensor((8, 8), generator=torch_generator(42))

        b = rand_tensor((8, 8), generator=torch_generator(42))

        c = rand_tensor((8, 8), generator=torch_generator(43))

        self.assertTrue(torch.equal(a, b))

        self.assertFalse(torch.equal(a, c))

    def test_global_rng_disturbance_does_not_change_local_generator(self):

        """

        Ключевой инвариант §9.2: локальный ГПСЧ не должен зависеть от того, что

        кто-то уже потратил случайные числа из глобального.

        """

        from utils.determinism import rand_tensor, torch_generator

        import numpy as np

        first = rand_tensor((4, 4), generator=torch_generator(7))

        torch.rand(1000)

        np.random.rand(1000)

        second = rand_tensor((4, 4), generator=torch_generator(7))

        self.assertTrue(torch.equal(first, second))

    def test_rand_tensor_requires_generator(self):

        from utils.determinism import rand_tensor

        with self.assertRaises(ValueError):

            rand_tensor((2, 2))

    def test_numpy_rng_from_torch_generator_is_deterministic(self):

        from utils.determinism import numpy_rng_from, torch_generator

        def draw(gen_seed):

            return [int(x) for x in numpy_rng_from(torch_generator(gen_seed)).integers(0, 1000, size=8)]

        self.assertEqual(draw(42), draw(42))

        self.assertNotEqual(draw(42), draw(43))


class InjuryRngTests(unittest.TestCase):

    def test_apply_injury_reproducible_by_seed(self):

        """

        Было: np.random.randint в глобальном состоянии (дыра §9.2 — результат

        травмы менялся от порядка тестов/прогонов). Стало: локальный rng.

        """

        import numpy as np

        from utils.determinism import init_determinism, numpy_generator

        from evaluate import apply_injury

        from target_patterns import create_target_circles

        init_determinism(config.SEED)

        target = create_target_circles(

            grid_size=config.GRID_SIZE,

            n_circles=config.TARGET_COMPONENTS,

        )

        state = torch.zeros(1, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE)

        first = apply_injury(state, 16, target_pattern=target, rng=numpy_generator(5))

        # Мусорим в глобальные ГПСЧ: локальный rng обязан это игнорировать.

        np.random.seed(12345)

        np.random.rand(100)

        torch.manual_seed(12345)

        second = apply_injury(state, 16, target_pattern=target, rng=numpy_generator(5))

        self.assertTrue(torch.equal(first, second))

        self.assertGreater(

            int((first[:, config.ALIVE_CHANNEL] == config.DEAD_ALPHA_VALUE).sum()),

            0,

            "травма не оставила мёртвых клеток — тест ничего не проверяет",

        )

    def test_apply_injury_does_not_consume_global_numpy_state(self):

        import numpy as np

        from evaluate import apply_injury

        from target_patterns import create_target_circles

        np.random.seed(0)

        before = np.random.get_state()[1].copy()

        target = create_target_circles(

            grid_size=config.GRID_SIZE,

            n_circles=config.TARGET_COMPONENTS,

        )

        state = torch.zeros(1, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE)

        apply_injury(state, 16, target_pattern=target)  # rng=None → локальный fallback

        after = np.random.get_state()[1]

        self.assertTrue(np.array_equal(before, after))


class ReproducibleTrainingTests(unittest.TestCase):

    """Главный гейт слоя 0: одинаковый сид → побитово одинаковый прогон."""

    def test_same_seed_same_fingerprint_inprocess(self):

        a = _training_fingerprint(seed=42, iterations=20, unroll=4)

        b = _training_fingerprint(seed=42, iterations=20, unroll=4)

        self.assertEqual(a["losses"], b["losses"])

        self.assertEqual(a["digest"], b["digest"])

    def test_different_seed_diverges(self):

        a = _training_fingerprint(seed=42, iterations=8, unroll=4)

        b = _training_fingerprint(seed=43, iterations=8, unroll=4)

        self.assertNotEqual(a["digest"], b["digest"])

    def test_no_silently_nondeterministic_ops(self):

        """

        torch в warn_only-режиме пишет UserWarning про операции без детерминированной

        реализации. Молча принять такой предупреждение = получить «воспроизводимый»

        прогон, который не воспроизводится. Поэтому предупреждения здесь — падения.

        """

        import warnings

        suspects = (

            "does not have a deterministic implementation",

            "no deterministic implementation",

            "Deterministic algorithms are disabled",

            "non-deterministic",

        )

        with warnings.catch_warnings(record=True) as caught:

            warnings.simplefilter("always")

            _training_fingerprint(seed=42, iterations=4, unroll=2)

        bad = [

            f"{w.category.__name__}: {w.message}"

            for w in caught

            if any(s in str(w.message) for s in suspects)

        ]

        self.assertEqual(bad, [])

    def test_same_seed_same_fingerprint_in_fresh_process(self):

        """

        Два независимых процесса: ловит зависимость от состояния, накопленного

        предыдущими тестами (порядок обращений к глобальным ГПСЧ).

        """

        digests = []

        for _ in range(2):

            code = _SUBPROCESS_SCRIPT.format(

                pkg=config_root(),

                seed=42,

                iterations=10,

                unroll=4,

            )

            result = subprocess.run(

                [sys.executable, "-c", code],

                cwd=config_root(),

                capture_output=True,

                text=True,

                timeout=1200,

            )

            self.assertEqual(

                result.returncode,

                0,

                f"подпрогон упал: {result.stderr[-3000:]}",

            )

            digests.append(json.loads(result.stdout.strip().splitlines()[-1]))

        self.assertEqual(digests[0], digests[1])


if __name__ == "__main__":

    unittest.main()
