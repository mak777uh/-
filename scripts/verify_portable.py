"""verify_portable.py — проверка portable-пакета E02b (smoke | full).

Скрипт лежит в корне portable-пакета и работает без репозитория: он находит
`morphogenesis/` рядом с собой, импортирует тот же код, что и каноническая
перепись, и сравнивает получившиеся классы с `census.json`.

Режимы:
  * `--mode smoke` (по умолчанию) — 2 обученные модели (R-9 seed42, R-9 seed101)
    и необученная архитектура × 16 сидов (0–15) × 2000 шагов. Каждый финальный
    дескриптор проецируется на замороженные центроиды
    (`class_centroids_frozen.json`), класс сравнивается с census. Это проверка
    целостности пакета, а не новый эксперимент.
  * `--mode full` — все 13 семейств × 64 сида × 2000 шагов, Ward + ARI против
    census. Долгий прогон (~85 минут на RTX 3070), запускать только по явному
    решению.

Результат — `verify_report.json` (версии, sha256, расхождения, время, device).

Почему smoke идёт через функции, а не через `e02b_morphospace.main`: `main`
включает `_preflight` полного протокола (12 файлов, ≥2 ГБ диска) и пишет
`census.json` поверх канонического. Для проверки пакета это лишнее и опасно.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

# Пакет — артефакт, а не рабочая копия: проверка не должна оставлять в нём
# __pycache__ (иначе sha256 манифеста и содержимое каталога расходятся).
sys.dont_write_bytecode = True

MANIFEST_NAME = "portable_manifest.json"
EXPERIMENT_ID = "E02b_morphospace"
SMOKE_FAMILIES = ("WP4_R-9_s2000_seed42", "WP4_R-9_s2000_seed101")
CONTROL_FAMILY = "untrained_current_arch"
SMOKE_SEEDS = tuple(range(16))
FULL_SEEDS = tuple(range(64))
CENSUS_STEPS = 2000
CENSUS_EVERY = 50
REPORT_SCHEMA_VERSION = 1

# Lite-контракт: ровно эти ключи и никаких optimizer/scheduler/pool/state.
LITE_KEYS = (
    "model_state_dict",
    "iteration",
    "seed",
    "grid_size",
    "n_channels",
    "spec_version",
    "revision",
    "stress_enabled",
    "stress_channel",
    "metadata",
)
FORBIDDEN_KEYS = (
    "optimizer_state_dict",
    "scheduler_state_dict",
    "pool_state_dict",
    "state",
)


def find_root(start: str | os.PathLike[str] | None = None) -> Path:
    """Ближайший предок, где есть `morphogenesis/e02b_morphospace.py`.

    Так один и тот же файл работает и в portable-пакете, и в репозитории
    (`scripts/verify_portable.py`), не зная абсолютных путей заранее.
    """
    here = Path(start or __file__).resolve()
    if here.is_file():
        here = here.parent
    for cand in (here, *here.parents):
        if (cand / "morphogenesis" / "e02b_morphospace.py").is_file():
            return cand
    raise SystemExit(
        "[verify] не найден morphogenesis/e02b_morphospace.py рядом с "
        f"{here}; ожидается portable-пакет или корень репозитория"
    )


ROOT = find_root()
MORPH_ROOT = ROOT / "morphogenesis"
# §9.2: config обязан импортироваться раньше torch, а все относительные пути
# config.py (checkpoints/, logs/, ...) резолвятся от cwd — как в проде.
if str(MORPH_ROOT) not in sys.path:
    sys.path.insert(0, str(MORPH_ROOT))
os.chdir(MORPH_ROOT)

import config  # noqa: E402
import numpy as np  # noqa: E402
import scipy  # noqa: E402
import torch  # noqa: E402

import e02b_morphospace as e02b  # noqa: E402


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def resolve_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device(config.DEVICE)
    device = torch.device(name)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("[verify] запрошен CUDA, но torch.cuda.is_available() == False")
    return device


def versions(device: torch.device) -> dict:
    gpu = None
    if device.type == "cuda":
        gpu = torch.cuda.get_device_name(device)
    return {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "device": str(device),
        "gpu": gpu,
        "spec_version": config.SPEC_VERSION,
        "revision": config.SPEC_REVISION,
    }


def load_census() -> tuple[dict, dict[tuple[str, int], dict]]:
    path = MORPH_ROOT / "experiments" / EXPERIMENT_ID / "census.json"
    if not path.is_file():
        raise SystemExit(f"[verify] нет census.json в пакете: {path}")
    census = load_json(path)
    rows = {(run["family"], int(run["seed"])): run for run in census.get("runs", [])}
    return census, rows


def load_frozen() -> dict:
    path = MORPH_ROOT / "experiments" / EXPERIMENT_ID / "class_centroids_frozen.json"
    if not path.is_file():
        raise SystemExit(f"[verify] нет class_centroids_frozen.json в пакете: {path}")
    frozen = load_json(path)
    for key in ("features", "scaler_mean", "scaler_std", "centroids_z", "labels_valid",
                "class_names"):
        if key not in frozen:
            raise SystemExit(f"[verify] в центроидах нет ключа {key!r}")
    return frozen


def frozen_assign(desc: dict, frozen: dict) -> tuple[int, str, float]:
    """Класс по замороженным центроидам — канонической функцией e02b.

    z-нормировка берётся из census (scaler_mean/std), а не пересчитывается на
    подмножестве: иначе классы «поедут» относительно опубликованных.
    """
    mean = np.asarray(frozen["scaler_mean"], dtype=np.float64)
    std = np.asarray(frozen["scaler_std"], dtype=np.float64)
    centroids = np.asarray(frozen["centroids_z"], dtype=np.float64)
    labels = list(frozen["labels_valid"])
    vec = e02b.descriptor_vector(desc).reshape(1, -1)
    label = int(e02b.assign_to_clusters(vec, mean, std, centroids, labels)[0])
    z = (vec - mean) / std
    sqdist = ((z - centroids) ** 2).sum(axis=1)
    class_name = frozen["class_names"][labels.index(label)]
    return label, str(class_name), float(sqdist.min())


def descriptor_max_abs_diff(got: dict, expected: dict) -> tuple[float, list[str]]:
    """Максимальное расхождение по скалярным полям дескриптора."""
    worst = 0.0
    fields: list[str] = []
    for key, value in expected.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        if key not in got or not isinstance(got[key], (int, float)):
            continue
        diff = abs(float(got[key]) - float(value))
        if diff > worst:
            worst = diff
            fields = [key]
        elif diff == worst and diff > 0:
            fields.append(key)
    return float(worst), sorted(set(fields))


def check_lite_checkpoint(family: str, manifest: dict) -> dict:
    """Проверить, что в пакете лежит lite, а не что-то другое."""
    info = (manifest.get("checkpoints") or {}).get(family)
    if not info:
        return {"family": family, "ok": False, "reason": "нет записи в манифесте"}
    rel = info["path"]
    path = ROOT / rel
    if not path.is_file():
        return {"family": family, "ok": False, "reason": f"нет файла {rel}"}
    size = path.stat().st_size
    sha = sha256_file(path)
    problems: list[str] = []
    if size != int(info["lite_bytes"]):
        problems.append(f"размер {size} != манифест {info['lite_bytes']}")
    if sha != info["lite_sha256"]:
        problems.append("sha256 не совпадает с манифестом")
    ck = torch.load(str(path), map_location="cpu", weights_only=False)
    keys = set(ck)
    extra = sorted(keys - set(LITE_KEYS))
    missing = sorted(set(LITE_KEYS) - keys)
    forbidden = sorted(keys & set(FORBIDDEN_KEYS))
    if extra:
        problems.append(f"лишние ключи: {extra}")
    if missing:
        problems.append(f"нет ключей: {missing}")
    if forbidden:
        problems.append(f"запрещённые ключи: {forbidden}")
    metadata = ck.get("metadata") or {}
    if metadata.get("spec_version") != config.SPEC_VERSION:
        problems.append(
            f"metadata.spec_version={metadata.get('spec_version')!r} != {config.SPEC_VERSION}"
        )
    if int(ck.get("grid_size", -1)) != config.GRID_SIZE:
        problems.append(f"grid_size={ck.get('grid_size')} != {config.GRID_SIZE}")
    if int(ck.get("n_channels", -1)) != config.N_CHANNELS:
        problems.append(f"n_channels={ck.get('n_channels')} != {config.N_CHANNELS}")
    declared_keys = info.get("lite_keys")
    if declared_keys and list(declared_keys) != list(LITE_KEYS):
        problems.append("контракт ключей в манифесте расходится с LITE_KEYS")
    return {
        "family": family,
        "path": rel,
        "size_bytes": size,
        "sha256": sha,
        "full_sha256": info.get("full_sha256"),
        "keys": sorted(keys),
        "ok": not problems,
        "problems": problems,
    }


def run_smoke(device: torch.device, steps: int, seeds: tuple[int, ...], frozen: dict,
              census_rows: dict, manifest: dict) -> dict:
    families = [*SMOKE_FAMILIES, CONTROL_FAMILY]
    specs = e02b.load_checkpoint_specs(
        families=families, include_untrained=True, allow_missing=False
    )
    print(
        f"[verify] smoke: семейств={len(specs)} сидов={len(seeds)} шагов={steps} "
        f"device={device}"
    )
    rows: list[dict] = []
    started = time.time()
    for spec in specs:
        model, _ck = e02b.build_model(spec, device)
        e02b.remember_stress_ema_start(model)
        family_start = time.time()
        family_rows: list[dict] = []
        for seed in seeds:
            run = e02b.run_seed(model, spec, seed, steps, CENSUS_EVERY, device)
            got = run["final"]
            label, class_name, margin = frozen_assign(got, frozen)
            expected = census_rows.get((spec.family, int(seed)))
            if expected is None:
                row = {
                    "family": spec.family,
                    "seed": int(seed),
                    "assigned_class": class_name,
                    "expected_class": None,
                    "class_match": False,
                    "reason": "нет строки в census.json",
                    "wall_seconds": float(run["wall_seconds"]),
                }
                rows.append(row)
                family_rows.append(row)
                continue
            diff, fields = descriptor_max_abs_diff(got, expected["final"])
            row = {
                "family": spec.family,
                "arm": spec.arm,
                "seed": int(seed),
                "steps": int(steps),
                "alive_mask_enabled": bool(spec.alive_mask_enabled),
                "overrides_source": spec.overrides_source,
                "assigned_label": int(label),
                "assigned_class": class_name,
                "assigned_margin_sqdist": round(margin, 6),
                "expected_label": int(expected["cluster"]),
                "expected_class": str(expected["class_name"]),
                "class_match": bool(class_name == expected["class_name"]),
                "descriptor_max_abs_diff": diff,
                "descriptor_diff_fields": fields,
                "wall_seconds": float(run["wall_seconds"]),
            }
            rows.append(row)
            family_rows.append(row)
        matched = sum(1 for row in family_rows if row["class_match"])
        print(
            f"[verify] {spec.family}: {matched}/{len(family_rows)} классов совпало, "
            f"{time.time() - family_start:.1f} с"
        )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    elapsed = time.time() - started
    # Целостность проверяем у ВСЕХ lite-файлов пакета, а не только у тех двух,
    # которые участвуют в rollout: 12 × 152 КБ — дешёво, а публикуемый пакет
    # не должен выглядеть проверенным там, где проверены только 2 из 12.
    checks = [
        check_lite_checkpoint(family, manifest)
        for family in manifest["package"]["families"]
    ]
    mismatches = [
        {
            "family": row["family"],
            "seed": row["seed"],
            "expected_class": row.get("expected_class"),
            "assigned_class": row["assigned_class"],
            "descriptor_max_abs_diff": row.get("descriptor_max_abs_diff"),
            "reason": row.get("reason"),
        }
        for row in rows
        if not row["class_match"]
    ]
    comparable = steps == CENSUS_STEPS and all(
        (family, int(seed)) in census_rows
        for family in (*SMOKE_FAMILIES, CONTROL_FAMILY)
        for seed in seeds
    )
    checks_ok = all(item["ok"] for item in checks)
    if not comparable:
        status = "INCONCLUSIVE"
    elif checks_ok and not mismatches:
        status = "PASS"
    else:
        status = "FAIL"
    diffs = [row["descriptor_max_abs_diff"] for row in rows if "descriptor_max_abs_diff" in row]
    return {
        "status": status,
        "families": families,
        "seeds": list(seeds),
        "steps": int(steps),
        "snapshot_every": CENSUS_EVERY,
        "comparable_to_census": bool(comparable),
        "numeric_identity_expected": False,
        "checks": checks,
        "checks_ok": bool(checks_ok),
        "runs": rows,
        "mismatches": mismatches,
        "summary": {
            "n_runs": len(rows),
            "n_class_matches": sum(1 for row in rows if row["class_match"]),
            "n_mismatches": len(mismatches),
            "n_learned": sum(1 for row in rows if row["family"] in SMOKE_FAMILIES),
            "n_control": sum(1 for row in rows if row["family"] == CONTROL_FAMILY),
            "max_abs_descriptor_diff": max(diffs) if diffs else None,
            "total_rollout_seconds": round(elapsed, 2),
            "mean_seed_seconds": round(
                sum(row["wall_seconds"] for row in rows) / max(len(rows), 1), 3
            ),
        },
        "notes": [
            "критерий PASS — совпадение классов с census по всем прогонам "
            "и целостность всех lite-файлов пакета",
            "классы ожидаются совпадающими между CPU и CUDA, но побитовость "
            "не гарантируется: n_pixels/alive-порог чувствителен к округлению, "
            "поэтому max_abs_descriptor_diff может быть O(10^2) при 0 mismatch",
            "числовая идентичность дескрипторов не является критерием; "
            "сравниваются классы, а расхождение показывается явно",
        ],
    }


def _run_key(run: dict) -> tuple[str, int]:
    return str(run["family"]), int(run["seed"])


def run_full(device: torch.device, seeds: tuple[int, ...]) -> tuple[dict, dict]:
    specs = e02b.load_checkpoint_specs(include_untrained=True, allow_missing=False)
    # Тот же предполётный гейт, что и у канонического прогона: 12 файлов, sha256,
    # ≥2 ГБ диска. Пакет не должен «пройти» там, где репозиторий бы отказал.
    e02b._preflight(specs, full_protocol=True, allow_missing=False)
    print(
        f"[verify] full: семейств={len(specs)} сидов={len(seeds)} шагов={CENSUS_STEPS} "
        f"device={device}"
    )
    started = time.time()
    payload, clustering = e02b.run_census(
        specs, list(seeds), CENSUS_STEPS, CENSUS_EVERY, device, pilot=False
    )
    elapsed = time.time() - started

    census, census_rows = load_census()
    payload_rows = {_run_key(run): run for run in payload.get("runs", [])}
    common = sorted(set(census_rows) & set(payload_rows))
    missing = sorted(set(census_rows) - set(payload_rows))
    extra = sorted(set(payload_rows) - set(census_rows))

    # ARI считается по выученным прогонам: контроли проецируются, а не фитятся.
    learned = [key for key in common if not census_rows[key].get("is_control")]
    labels_new = np.asarray([int(payload_rows[key]["cluster"]) for key in learned])
    labels_old = np.asarray([int(census_rows[key]["cluster"]) for key in learned])
    ari_learned = float(e02b._adjusted_rand(labels_new, labels_old))

    # Ward перенумеровывает классы: сопоставляем по большинству, а не по номеру.
    mapping: dict[int, str] = {}
    for label in sorted(set(int(v) for v in labels_new if int(v) >= 0)):
        members = [key for key in learned if int(payload_rows[key]["cluster"]) == label]
        if not members:
            continue
        names = [str(census_rows[key]["class_name"]) for key in members]
        mapping[label] = max(sorted(set(names)), key=names.count)
    rows = []
    mismatches = []
    for key in common:
        run = payload_rows[key]
        predicted = mapping.get(int(run["cluster"]), "outlier")
        expected = str(census_rows[key]["class_name"])
        match = predicted == expected
        rows.append(
            {
                "family": key[0],
                "seed": key[1],
                "ward_label": int(run["cluster"]),
                "mapped_class": predicted,
                "expected_class": expected,
                "class_match": bool(match),
                "is_control": bool(run.get("is_control")),
            }
        )
        if not match:
            mismatches.append(
                {
                    "family": key[0],
                    "seed": key[1],
                    "expected_class": expected,
                    "mapped_class": predicted,
                    "ward_label": int(run["cluster"]),
                }
            )
    accuracy = (
        sum(1 for row in rows if row["class_match"]) / len(rows) if rows else 0.0
    )

    new_clustering = payload.get("clustering") or {}
    old_clustering = census.get("clustering") or {}
    old_labels = [int(v) for v in (old_clustering.get("labels_valid") or [])]
    old_names = [str(v) for v in (old_clustering.get("class_names") or [])]
    structural_new = sorted(
        mapping.get(int(label), "outlier") for label in payload.get("structural_labels", [])
    )
    structural_old = sorted(
        old_names[old_labels.index(int(label))]
        for label in census.get("structural_labels", [])
        if int(label) in old_labels
    )
    status = "PASS" if (ari_learned >= 0.999 and accuracy >= 0.999 and not missing) else "FAIL"
    if not rows:
        status = "INCONCLUSIVE"
    result = {
        "status": status,
        "families": [spec.family for spec in specs],
        "seeds": list(seeds),
        "steps": CENSUS_STEPS,
        "snapshot_every": CENSUS_EVERY,
        "ward": {
            "k": new_clustering.get("k"),
            "silhouette": new_clustering.get("silhouette"),
            "class_sizes": new_clustering.get("sizes"),
            "class_names": new_clustering.get("class_names"),
            "structural_labels": payload.get("structural_labels"),
        },
        "census_ward": {
            "k": old_clustering.get("k"),
            "silhouette": old_clustering.get("silhouette"),
            "class_sizes": old_clustering.get("sizes"),
            "class_names": old_clustering.get("class_names"),
            "structural_labels": census.get("structural_labels"),
        },
        "ari_learned": ari_learned,
        "class_mapping": {str(key): value for key, value in mapping.items()},
        "class_mapping_accuracy": float(accuracy),
        "structural_class_names": {"new": structural_new, "census": structural_old},
        "runs": rows,
        "mismatches": mismatches,
        "missing_runs": [{"family": key[0], "seed": key[1]} for key in missing],
        "unexpected_runs": [{"family": key[0], "seed": key[1]} for key in extra],
        "outcome": payload.get("outcome"),
        "census_outcome": census.get("outcome"),
        "summary": {
            "n_runs_compared": len(rows),
            "n_mismatches": len(mismatches),
            "n_learned": len(learned),
            "total_seconds": round(elapsed, 2),
            "seconds_per_seed": round(elapsed / max(len(payload.get("runs", [])), 1), 3),
        },
        "notes": [
            "PASS — ARI ≥ 0.999 и совпадение классов после сопоставления меток Ward",
            "пересчитанная перепись сохраняется только с --save-census",
        ],
    }
    return result, payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--device", default="auto", help="auto|cuda|cpu")
    parser.add_argument("--seeds", default=None, help="smoke: 0-15 (по умолчанию); full: 0-63")
    parser.add_argument("--steps", type=int, default=None, help="smoke: 2000 (для сравнения)")
    parser.add_argument("--out", default=None, help="путь verify_report.json")
    parser.add_argument(
        "--save-census",
        action="store_true",
        help="full: сохранить пересчитанную перепись рядом с отчётом",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    device = resolve_device(args.device)
    started_at = utc_now()
    t_start = time.time()

    manifest_path = ROOT / MANIFEST_NAME
    if manifest_path.is_file():
        manifest = load_json(manifest_path)
        manifest_sha = sha256_file(manifest_path)
    else:
        manifest = {}
        manifest_sha = None
        print(f"[verify] ВНИМАНИЕ: {MANIFEST_NAME} не найден в {ROOT}")

    census, census_rows = load_census()
    frozen = load_frozen()

    if args.mode == "smoke":
        seeds = tuple(e02b._parse_seeds(args.seeds)) if args.seeds else SMOKE_SEEDS
        steps = int(args.steps or CENSUS_STEPS)
        if device.type == "cpu":
            print(
                "[verify] smoke на CPU: ~1 минута на сид; полный набор 48 прогонов "
                "может занять час. Для проверки класса лучше CUDA."
            )
        result = run_smoke(device, steps, seeds, frozen, census_rows, manifest)
    else:
        seeds = tuple(e02b._parse_seeds(args.seeds)) if args.seeds else FULL_SEEDS
        print(
            f"[verify] full — это {len(seeds) * 13} развёрток по {CENSUS_STEPS} шагов; "
            "на RTX 3070 ~85 минут. Не прерывайте прогон: census не перезаписывается."
        )
        result, payload = run_full(device, seeds)
        if args.save_census:
            if args.out:
                base = Path(args.out)
                out_dir = (base if base.is_absolute() else ROOT / base).parent
            else:
                out_dir = ROOT
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / "verify_census.json"
            with path.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            print(f"[verify] перепись сохранена: {path}")

    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "experiment": EXPERIMENT_ID,
        "mode": args.mode,
        "started_at": started_at,
        "finished_at": utc_now(),
        "wall_seconds": round(time.time() - t_start, 2),
        "device": str(device),
        "versions": versions(device),
        "package": {
            "root": ROOT.name,
            "manifest_sha256": manifest_sha,
            "git_commit": (manifest.get("source") or {}).get("git_commit"),
            "git_dirty": (manifest.get("source") or {}).get("git_dirty"),
            "spec_version": (manifest.get("package") or {}).get("spec_version"),
            "n_families": len((manifest.get("package") or {}).get("families") or []),
        },
        "census": {
            "sha256": sha256_file(MORPH_ROOT / "experiments" / EXPERIMENT_ID / "census.json"),
            "n_runs": len(census.get("runs", [])),
            "device": census.get("device"),
            "steps": census.get("steps"),
            "snapshot_every": census.get("snapshot_every"),
        },
        "frozen_centroids": {
            "sha256": sha256_file(
                MORPH_ROOT / "experiments" / EXPERIMENT_ID / "class_centroids_frozen.json"
            ),
            "k": frozen.get("k"),
            "class_names": frozen.get("class_names"),
        },
        "config": {
            "grid_size": config.GRID_SIZE,
            "n_channels": config.N_CHANNELS,
        },
        **result,
    }
    # Относительный --out считается от корня пакета, а не от cwd: скрипт уже
    # сделал chdir в morphogenesis/, и «verify_report.json» иначе уедет внутрь.
    if args.out:
        out_arg = Path(args.out)
        out_path = out_arg if out_arg.is_absolute() else ROOT / out_arg
    else:
        out_path = ROOT / "verify_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    summary = report.get("summary") or {}
    print(
        f"[verify] {report['status']}: {report['mode']}, device={device}, "
        f"runs={summary.get('n_runs', summary.get('n_runs_compared'))}, "
        f"mismatches={summary.get('n_mismatches')}, "
        f"{report['wall_seconds']:.1f} с"
    )
    print(f"[verify] отчёт: {out_path}")
    return 0 if report["status"] in ("PASS", "INCONCLUSIVE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
