"""

determinism.py — слой 0: полный контроль энтропии (§9.2, §23 «Базовые»).

[v5.6-EXP FINAL] Rev.11-IMPLEMENTATION-READY

Правила спеки, реализованные здесь:

- CUBLAS_WORKSPACE_CONFIG ставится ДО импорта torch (см. config.py, начало файла);

- torch.use_deterministic_algorithms(True), cudnn.deterministic=True,

  cudnn.benchmark=False;

- все стохастические операции используют локальные генераторы, а не глобальный

  ГПСЧ;

- если детерминистический режим падает на конкретной операции — операция

  пишется в лог и для неё разрешается CPU-fallback (§9.2).

"""

import os

import random

import numpy as np

import torch

import config

# Операции, на которых torch.use_deterministic_algorithms бросает
# "numpy.random" / "non-deterministic" исключения. Список пополняется по мере
# обнаружения и ОБЯЗАТЕНО фиксироваться в memory/decisions_log.jsonl (§0.3).
CPU_FALLBACK_ALLOWED_OPS = set()


def cublas_workspace_configured():
    """Проверка, что переменная действительно стоит и задана до импорта torch."""
    return os.environ.get("CUBLAS_WORKSPACE_CONFIG") == config.CUBLAS_WORKSPACE_CONFIG and bool(
        getattr(config, "CUBLAS_CONFIG_SET_BEFORE_TORCH_IMPORT", True)
    )


def init_determinism(seed=None, strict=None):
    """

    Инициализация детерминизма. Возвращает отчёт (dict) для записи в логи/чекпоинты.

    strict=True — torch.use_deterministic_algorithms(True) без warn_only.

    Если torch отказывается на неизвестной операции, делаем одну повторную

    попытку в warn_only-режиме и фиксируем деградацию в отчёте (не молча).

    """

    if seed is None:
        seed = config.SEED
    if strict is None:
        strict = bool(getattr(config, "DETERMINISTIC_MODE", True))

    seed = int(seed)

    random.seed(seed)
    np.random.seed(seed)

    torch.manual_seed(seed)
    # config.CUDA_USABLE, а не torch.cuda.is_available(): при пустом
    # CUDA_VISIBLE_DEVICES is_available() возвращает True при device_count()==0
    # (замерено на torch 2.6.0+cu124), и отчёт об окружении начал бы врать.
    cuda_available = bool(config.CUDA_USABLE)
    if cuda_available:
        torch.cuda.manual_seed_all(seed)

    env_set_before_torch = bool(
        getattr(config, "CUBLAS_CONFIG_SET_BEFORE_TORCH_IMPORT", True)
    )
    report = {
        "seed": seed,
        "strict": strict,
        "cuda_available": cuda_available,
        "cuda_device_count": int(getattr(config, "CUDA_DEVICE_COUNT", 0)),
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "cublas_env_value_present": os.environ.get("CUBLAS_WORKSPACE_CONFIG")
        == config.CUBLAS_WORKSPACE_CONFIG,
        "cublas_set_before_torch": env_set_before_torch,
        "cuda_initialized": bool(cuda_available and torch.cuda.is_initialized()),
        "use_deterministic_algorithms": None,
        "warn_only": None,
        "cudnn_deterministic": None,
        "cudnn_benchmark": None,
        "degradations": [],
    }

    # §9.2: CUBLAS_WORKSPACE_CONFIG обязан быть выставлен до импорта torch.
    # Если модуль torch уже был в sys.modules — предупреждаем НЕ молча.
    if not env_set_before_torch:
        msg = (
            "config импортирован ПОСЛЕ torch: CUBLAS_WORKSPACE_CONFIG выставлен "
            "поздно, CUDA-детерминизм может не гарантироваться (§9.2). Исправление: "
            "в точке входа делайте `import config` первым (см. train.py/smoke_test.py)."
        )
        report["degradations"].append(msg)
        if cuda_available:
            print(f"⚠️  {msg}")

    if strict:
        try:
            torch.use_deterministic_algorithms(True)
            report["use_deterministic_algorithms"] = True
            report["warn_only"] = False
        except Exception as exc:  # noqa: BLE001 - фиксируем любую деградацию
            torch.use_deterministic_algorithms(True, warn_only=True)
            report["use_deterministic_algorithms"] = True
            report["warn_only"] = True
            report["degradations"].append(f"use_deterministic_algorithms strict failed: {exc!r}")

    torch.backends.cudnn.deterministic = True
    # §9.2 требует benchmark=False; CUDNN_BENCHMARK=True разрешён только как
    # явного экспериментального исключения через decisions_log.
    torch.backends.cudnn.benchmark = bool(getattr(config, "CUDNN_BENCHMARK", False))
    if torch.backends.cudnn.benchmark:
        report["degradations"].append(
            "CUDNN_BENCHMARK=True в config — против §9.2; cudnn.benchmark оставлен True"
        )

    # TF32 — разрешённая по умолчанию точность свёрток на Ampere и новее
    # (torch.backends.cudnn.allow_tf32=True). На Turing (T4) TF32 нет вообще,
    # поэтому «тот же рецепт» считает свёртки с разной точностью. Переменная
    # MORPH_TF32=0 выключает TF32, не меняя дефолтов config: нужно для опыта
    # «точность против класса» (H-REPRO-4). По умолчанию поведение прежнее.
    tf32_env = os.environ.get("MORPH_TF32")
    tf32_enabled = True if tf32_env is None else tf32_env.strip() not in {"0", "false", "False", "no"}
    if tf32_enabled:
        report["tf32_cudnn"] = bool(torch.backends.cudnn.allow_tf32)
        report["tf32_matmul"] = bool(torch.backends.cuda.matmul.allow_tf32)
        report["tf32_forced_off"] = False
    else:
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cuda.matmul.allow_tf32 = False
        if hasattr(torch.backends.cuda.matmul, "allow_fp16_reduced_precision_reduction"):
            torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = False
        report["tf32_cudnn"] = bool(torch.backends.cudnn.allow_tf32)
        report["tf32_matmul"] = bool(torch.backends.cuda.matmul.allow_tf32)
        report["tf32_forced_off"] = True
        report["tf32_env"] = tf32_env

    report["cudnn_deterministic"] = bool(torch.backends.cudnn.deterministic)
    report["cudnn_benchmark"] = bool(torch.backends.cudnn.benchmark)

    return report


def torch_generator(seed=None, device=None):
    """Локальный torch.Generator (ПРАВИЛО: не глобальный ГПСЧ)."""
    if seed is None:
        seed = config.SEED
    gen = torch.Generator(device=device) if device is not None else torch.Generator()
    gen.manual_seed(int(seed))
    return gen


def numpy_generator(seed=None):
    """Локальный numpy Generator (numpy.random.default_rng), без глобального состояния."""
    if seed is None:
        seed = config.SEED
    return np.random.default_rng(int(seed))


def numpy_rng_from(generator):
    """

    numpy-Generator, выведенный из torch.Generator: один источник энтропии на прогон.

    Нужен, чтобы выбор (например, кластер для травмы) был детерминирован сидом и

    при этом не зависел от глобального np.random (§9.2, ПРАВИЛО локальных ГПСЧ).

    """
    if generator is None:
        return numpy_generator()
    with torch.no_grad():
        draw = torch.randint(
            0,
            2**62 - 1,
            (1,),
            generator=generator,
            dtype=torch.int64,
        )
    return numpy_generator(int(draw.item()))



def rand_tensor(shape, generator=None, device=None, dtype=torch.float32):
    """torch.rand с обязательным локальным генератором."""
    if generator is None:
        raise ValueError("rand_tensor требует локальный torch.Generator (§4.3).")
    return rand(shape, generator=generator, device=device, dtype=dtype)


def _device_draw(generator, op, *args, device, dtype):
    """
    Рисование через op с учётом привязки Generator к устройству (§9.2).

    Generator в PyTorch принадлежит устройству: torch.rand(..., generator=cpu_gen,
    device='cuda') бросает RuntimeError. Поскольку проект сознательно держит
    ЕДИНЫЙ CPU-генератор на прогон (одинаковая энтропия на CPU и GPU — прогоны
    сравнимы между машинами), значения рисуются на устройстве генератора и
    переносятся на устройство тензора.
    """
    tensor_device = torch.device(device) if device is not None else None
    if generator is None:
        if tensor_device is None:
            return op(*args, dtype=dtype)
        return op(*args, device=tensor_device, dtype=dtype)
    gen_device = torch.device(generator.device)
    if tensor_device is None or gen_device.type == tensor_device.type:
        return op(*args, generator=generator, device=gen_device, dtype=dtype)
    return op(*args, generator=generator, device=gen_device, dtype=dtype).to(
        device=tensor_device
    )


def rand(shape, generator=None, device=None, dtype=torch.float32):
    """torch.rand(shape), устроенный по §9.2 (локальный ГПСЧ + перенос на устройство)."""
    return _device_draw(generator, torch.rand, tuple(shape), device=device, dtype=dtype)


def randn(shape, generator=None, device=None, dtype=torch.float32):
    """torch.randn(shape) в том же устройство-адаптивном режиме."""
    return _device_draw(generator, torch.randn, tuple(shape), device=device, dtype=dtype)


def randperm(n, generator=None, device=None):
    """torch.randperm(n) в том же устройство-адаптивном режиме."""
    return _device_draw(generator, torch.randperm, int(n), device=device, dtype=torch.int64)



def assert_deterministic_ready(report=None):
    """
    Предзапусковый гейт (§23 «Базовые»). Бросает RuntimeError, если окружение
    не удовлетворяет §9.2. report — результат init_determinism().
    """
    problems = []
    if not torch.backends.cudnn.deterministic:
        problems.append("cudnn.deterministic=False")
    if torch.backends.cudnn.benchmark:
        problems.append("cudnn.benchmark=True")
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") != config.CUBLAS_WORKSPACE_CONFIG:
        problems.append(
            "CUBLAS_WORKSPACE_CONFIG != "
            f"{config.CUBLAS_WORKSPACE_CONFIG} (должен быть задан через config)"
        )
    if not getattr(config, "CUBLAS_CONFIG_SET_BEFORE_TORCH_IMPORT", True):
        problems.append(
            "config импортирован после torch — переменная окружения задана поздно (§9.2)"
        )
    if config.CUDA_USABLE and not torch.are_deterministic_algorithms_enabled():
        problems.append("use_deterministic_algorithms(False) при доступном CUDA")
    if report is not None and report.get("warn_only"):
        problems.append("use_deterministic_algorithms работает в warn_only (деградация)")
    if problems:
        raise RuntimeError("Детерминизм §9.2 не обеспечен: " + "; ".join(problems))

