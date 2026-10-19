"""

topo_proxy.py — дифференцируемый топологический прокси (§2.10, §12.4).

Зачем: нормированный symmetric Chamfer не видит «тонкие разрывы» —

1–2 пикселя в кольце дают вклад ~0.01 в Chamfer при полном разрушении

топологии (β₁ теряет дыру). Поэтому в лосс добавляется отдельный член,

который ДИФФЕРЕНЦИРУЕМ по видимому каналу.

Жёсткие правила спеки, которые этот файл соблюдает:

- §2.4: запрещано утверждать дифференцируемость β₀/β₁ и тем более брать

  градиент через ``scipy.ndimage.label``. Дискретная топология остаётся

  ИСТОЧНИКОМ ИСТИНЫ для отчётов и считается отдельно (topology.py);

- §2.10.2: прокси НЕ обязан быть точным топологическим инвариантом —

  он обязан быть дифференцируемым и проходить тест градиента;

- §2.10.4: при деградации (ноль градиента / NaN в течение

  TOPO_PROXY_GRACE_STEPS) прокси обязан сам отключиться, а событие —

  быть записанным в memory/negative_results.md.

Реализация ``soft_topological_proxy`` (два члена, оба дифференцируемы):

1) мягкая эйлерова характеристика χ = β₀ − β₁ по локальным 2×2-паттернам

   (классическая формула цифровой топологии, записанная через произведения

   сдвигов маски, поэтому дифференцируема);

2) штраф за тонкий разрыв: пиксель, который выключен, но его противоположные

   соседи включены (разрыв толщиной 1 клетку вдоль линии/кольца).

"""

import math

import torch

import torch.nn.functional as F

import config


def _shift(x, dy, dx):

    """Сдвиг на (dy, dx) с нулями за краем (тот же constant-pad, что и в §12.2.2)."""

    b, c, h, w = x.shape

    if dy == 0 and dx == 0:

        return x

    pad_top = max(dy, 0)

    pad_bottom = max(-dy, 0)

    pad_left = max(dx, 0)

    pad_right = max(-dx, 0)

    padded = F.pad(x, (pad_left, pad_right, pad_top, pad_bottom), mode="constant", value=0)

    return padded[:, :, :h, :w]


def soft_chi(mask):

    """

    Мягкая эйлерова характеристика (β₀ − β₁) для маски формы (B,1,H,W).

    На бинарной входе совпадает с дискретной χ с точностью до соглашений

    цифровой топологии (проверяется тестом против topology.py).

    Формула через 2×2-паттерны: χ = (N3 − N1 + 2·ND) / 4, где

    N3 — окна ровно с одной активной клеткой, N1 — окна с тремя,

    ND — окна с двумя диагональными активными клетками.

    Для мягкой маски индикаторы окон заменяются произведениями

    (m или 1−m) — дифференцируемость сохраняется везде.

    """

    m = _as_single_channel(mask, mask)

    inv = 1.0 - m

    # 2×2 окно: a=(0,0), b=(0,1), c=(1,0), d=(1,1).

    a = m

    b = _shift(m, 0, 1)

    c = _shift(m, 1, 0)

    d = _shift(m, 1, 1)

    ai, bi, ci, di = inv, _shift(inv, 0, 1), _shift(inv, 1, 0), _shift(inv, 1, 1)

    # Ровно одна активная клетка.

    n3 = a * bi * ci * di + ai * b * ci * di + ai * bi * c * di + ai * bi * ci * d

    # Ровно три активные клетки.

    n1 = a * b * c * di + a * b * d * ci + a * c * d * bi + b * c * d * ai

    # Две диагональные активные клетки (разрыв топологии «наискосок»).

    nd = a * d * bi * ci + b * c * ai * di

    return (n3 - n1 + 2.0 * nd).mean(dim=(1, 2, 3)) / 4.0


def soft_break_penalty(mask, target):

    """

    Штраф за тонкие разрывы внутри цели (§2.10): клетка выключена, но её

    противоположные соседи включены — разрыв толщиной в одну клетку.

    Chamfer за такое платит ~0, а β₁ теряет дыру целиком.

    Нормировка — на число клеток цели, а не на площадь сетки: один разрыв

    кольца должен стоить одинаково при любом размере фона.

    """

    m = _as_single_channel(mask, mask)

    target = _as_single_channel(target, m)

    gap_lr = (1.0 - m) * _shift(m, 0, -1) * _shift(m, 0, 1)

    gap_ud = (1.0 - m) * _shift(m, -1, 0) * _shift(m, 1, 0)

    gaps = gap_lr + gap_ud

    inside_target = (target > 0.5).to(m.dtype)

    per_sample = (gaps * inside_target).sum(dim=(1, 2, 3))

    target_cells = inside_target.sum(dim=(1, 2, 3)).clamp(min=1.0)

    return per_sample / target_cells


def _as_single_channel(x, reference):

    """Приводит вход прокси к (B, 1, H, W) в dtype/device опорного тензора."""

    x = x.to(device=reference.device, dtype=reference.dtype) if isinstance(reference, torch.Tensor) else x

    if x.dim() == 3:

        x = x.unsqueeze(1)

    if x.dim() != 4:

        raise ValueError(f"видимый канал должен иметь форму (B, 1, H, W), получено {tuple(x.shape)}")

    if x.shape[1] != 1:

        x = x[:, :1]

    return x


class TopologicalProxy:

    """

    §12.4: вычисляет дифференцируемый лосс топологии.

    Бэкенды: ``soft_topological_proxy`` (дефолт MVP), ``torch-topological``

    (персистентная гомология, только после теста градиента), ``disabled``.

    """

    def __init__(

        self,

        target_pattern,

        backend=None,

        weight=None,

        stride=None,

    ):

        self.target_pattern = target_pattern

        self.backend = str(config.TOPO_PROXY_BACKEND if backend is None else backend)

        self.weight = float(config.TOPO_PROXY_WEIGHT if weight is None else weight)

        self.stride = int(config.TOPO_PROXY_STEP_STRIDE if stride is None else stride)

        self.grace_steps = int(config.TOPO_PROXY_GRACE_STEPS)

        # Целевая χ считается один раз по бинарной цели (дискретная величина —

        # она не «всплывает» вместе с шумом видимого канала).

        with torch.no_grad():

            target = _as_single_channel(

                self.target_pattern.float()

                if isinstance(self.target_pattern, torch.Tensor)

                else torch.as_tensor(self.target_pattern, dtype=torch.float32),

                self.target_pattern,

            )

            self.target_chi = float(soft_chi((target > 0.5).float()).mean().item())

        # Счётчики деградации (§2.10.4).

        self.steps_without_gradient = 0

        self.nan_count = 0

        self.degraded = False

        self.degradation_reason = None

    # ------------------------------------------------------------------ loss

    def compute_loss(self, visible_channel):

        """

        visible_channel: (B, 1, H, W) в диапазоне [0, 1].

        Возвращает скалярный лосс (torch.Tensor) либо 0.0 для disabled.

        """

        if self.backend == "disabled":

            return 0.0

        if self.backend == "soft_topological_proxy":

            return self.soft_proxy_loss(visible_channel)

        if self.backend == "torch-topological":

            return self.persistent_loss(visible_channel)

        raise ValueError(f"Unknown topo proxy backend: {self.backend!r}")

    def soft_proxy_loss(self, visible_channel):
        """
        Мягкий прокси β₀/β₁ (§2.10.2). Обязательно дифференцируем.

        Масштаб: нарушение χ делим на число клеток цели, поэтому член
        измерается в «единицах нарушения χ на клетку цели» и сопоставим по
        порядку с MSE видимого канала и со штрафом за разрыв. Без нормировки
        на случайном инициализации Δχ ~ 10² единиц, и topo-член перекрывал бы
        основной сигнальный член на два порядка (проверено прогоном).
        """
        m = _as_single_channel(visible_channel, visible_channel)
        target = _as_single_channel(self.target_pattern, m)
        area = float(m.shape[2] * m.shape[3])
        # soft_chi возвращает χ, делённый на число клеток — умножаем обратно.
        chi_now = soft_chi(m) * area
        chi_target = soft_chi((target > 0.5).to(m.dtype)) * area
        target_cells = max(1.0, float((target > 0.5).to(m.dtype).sum().item()))
        chi_term = ((chi_now - chi_target).abs() / target_cells).mean()
        break_term = soft_break_penalty(m, target).mean()
        return chi_term + break_term

    def persistent_loss(self, visible_channel):

        """

        Персистентная гомология через torch-topological (§2.10.3).

        Вызывается только если прошёл тест градиента. Библиотека не входит в

        обязательные зависимости MVP: при её отсутствии бэкенд честно

        деградирует в ``disabled`` (иначе «персистентный лосс» молча стал бы

        нулевым членом лосса).

        """

        try:

            import torch_topological  # noqa: F401

        except ImportError as exc:

            self._degrade(f"torch-topological недоступен: {exc!r}")

            return 0.0

        raise NotImplementedError(

            "Персистентный бэкенд требует подтверждённой дифференцируемости "

            "(§2.10.3) и не входит в MVP слоя 1; используй soft_topological_proxy."

        )

    # -------------------------------------------------------------- gradient

    def _grad_probes(self, device):
        """
        Зонды для градиентного чекпоинта (§2.10.1).

        Важно: сама бинарная цель — ОПТИМУМ прокси (её лосс равен нулю), и
        проверка градиента в нуле лосса дала бы ложный отказ. Поэтому зонды
        берутся ЗАВЕДОМО вне цели: размытая цель, заполненный диск вместо
        кольца, мягкий шум.
        """
        with torch.no_grad():
            target = _as_single_channel(
                self.target_pattern.float(), self.target_pattern
            ).to(device)
            hard = (target > 0.5).float()
            kernel = torch.ones(1, 1, 3, 3, device=device, dtype=hard.dtype) / 9.0
            blurred = F.conv2d(F.pad(hard, (1, 1, 1, 1), mode="replicate"), kernel)
            h, w = hard.shape[2], hard.shape[3]
            yy = torch.arange(h, device=device, dtype=hard.dtype).view(1, 1, h, 1)
            xx = torch.arange(w, device=device, dtype=hard.dtype).view(1, 1, 1, w)
            dist = ((yy - h / 2) ** 2 + (xx - w / 2) ** 2).sqrt()
            disk = (dist <= 0.35 * min(h, w)).to(hard.dtype)
            gen = torch.Generator(device="cpu").manual_seed(int(config.SEED))
            noise = (
                torch.rand(tuple(hard.shape), generator=gen).to(device=device, dtype=hard.dtype)
                * 0.6
                + 0.2
            )
        return {
            "blurred_target": blurred,
            "disk": disk,
            "soft_noise": noise,
        }

    def grad_test(self, device=None):

        """

        Обязательная проверка (§2.10.1, §12.1.13): градиент прокси по видимому

        каналу существует, ненулевой и без NaN. Возвращает dict с результатом —

        вызывающий код обязан его залогировать, а не проигнорировать.

        """

        if self.backend == "disabled":
            return {
                "backend": self.backend,
                "passed": False,
                "grad_norm": 0.0,
                "note": "бэкенд отключён",
            }

        if device is None:
            device = self.target_pattern.device if isinstance(self.target_pattern, torch.Tensor) else "cpu"

        results = {}
        best = None
        for name, probe_template in self._grad_probes(device).items():
            probe = probe_template.clone().detach()
            probe.requires_grad_(True)
            loss = self.compute_loss(probe)
            if not torch.is_tensor(loss):
                results[name] = {"passed": False, "grad_norm": 0.0, "loss": None}
                continue
            loss.backward()
            grad = probe.grad
            finite = grad is not None and bool(torch.isfinite(grad).all())
            norm = float(grad.abs().sum().item()) if grad is not None else 0.0
            passed = bool(finite and norm > 0.0)
            results[name] = {
                "passed": passed,
                "grad_norm": norm,
                "loss": float(loss.item()),
                "nan": bool(grad is not None and not finite),
            }
            if passed and (best is None or norm > results[best]["grad_norm"]):
                best = name

        report = {
            "backend": self.backend,
            "passed": best is not None,
            "probe": best,
            "grad_norm": results[best]["grad_norm"] if best else 0.0,
            "loss": results[best]["loss"] if best else None,
            "probes": results,
        }
        return report

    # ------------------------------------------------------------ degradation

    def _degrade(self, reason):

        """§2.10.4: перевод в disabled с причиной. Возвращает событие для NEG."""

        self.backend = "disabled"

        self.degraded = True

        self.degradation_reason = reason

        return {

            "reason": reason,

            "steps_without_gradient": self.steps_without_gradient,

            "nan_count": self.nan_count,

            "backend": "disabled",

        }

    def observe(self, loss_value, grad_norm, step):

        """

        Мониторинг здоровья прокси (§2.10.4).

        Вызывается из train-цикла на каждом шаге, где прокси участвовал в лоссе.

        Возвращает dict-событие деградации (или None, если всё в порядке) —

        запись в negative_results.md делает вызывающий код, потому что только

        он знает идентификатор эксперимента.

        """

        if self.backend == "disabled":

            return None

        loss_nan = False

        if loss_value is None:

            loss_nan = True

        elif torch.is_tensor(loss_value):

            loss_nan = not bool(torch.isfinite(loss_value).all())

        else:

            try:

                loss_nan = not math.isfinite(float(loss_value))

            except (TypeError, ValueError):

                loss_nan = True

        grad_nan = grad_norm is not None and not math.isfinite(float(grad_norm))

        if loss_nan or grad_nan:

            self.nan_count += 1

        else:

            self.nan_count = 0

            if float(grad_norm or 0.0) <= 0.0:

                self.steps_without_gradient += 1

            else:

                self.steps_without_gradient = 0

        if self.nan_count >= 3:

            # §2.10.4: три NaN подряд — это деградация, а не «шум в мониторинге».

            return self._degrade(f"лосс/градиент прокси содержит NaN ({self.nan_count} раз подряд)")

        if self.steps_without_gradient >= self.grace_steps:

            return self._degrade(

                f"{self.steps_without_gradient} шагов подряд с нулевым градиентом "

                f"(последний шаг {step})"

            )

        return None

    # ------------------------------------------------------------------- misc

    def next_step_ok(self, iteration):

        """§2.10.3: прокси считается не каждый шаг, а каждые STRIDE шагов."""

        if self.backend == "disabled" or not config.TOPO_PROXY_ENABLED:

            return False

        return int(iteration) % max(1, self.stride) == 0


def topo_term_cap(raw_loss, cap=None):
    """
    §12.6.8: отдельный потолок влияния топологического члена.

    Это НЕ torch.clamp: жёсткий клиппинг обнуляет градиент выше потолка
    (мёртвая зона — прокси перестает учиться именно там, где топология хуже
    всего). Рациональное насыщение ``x / (1 + |x|/cap)`` монотонно, ограничено
    сверху величиной cap и имеет градиент ``1 / (1 + |x|/cap)²``, который
    остаётся представим в float32 и на x = 1000·cap (tanh там уже дал бы ноль —
    проверено тестом).
    """
    if not torch.is_tensor(raw_loss):
        return raw_loss
    if cap is None:
        cap = float(config.TOPO_PROXY_GRAD_CLIP)
    cap = max(float(cap), 1e-6)
    return raw_loss / (1.0 + raw_loss.abs() / cap)


def gradient_clipped_topo_term(proxy, visible_channel, target_grad_norm=None):
    """
    §12.6.8: для топологического прокси допускается отдельный клиппинг градиента
    (TOPO_PROXY_GRAD_CLIP), чтобы он не перекрывал основной MSE-сигнал.
    """
    loss = proxy.compute_loss(visible_channel)
    if not torch.is_tensor(loss):
        return loss
    return topo_term_cap(loss, target_grad_norm)
