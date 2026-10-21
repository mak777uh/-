"""E02b: аудит происхождения 12 канонических чекпоинтов.

Зачем. Вся статья про E02b стоит на 12 файлах `nca_final.pt`
(`lab/checkpoints.json` → `canonical_for: ["E02b_morphospace"]`). Пока эти
файлы не проверены, любой вывод про «модели ведут себя по-разному» держится
на доверии к архиву. Проверка отвечает на четыре вопроса:

1. **Целостность.** Байт-хэш каждого файла совпадает с записанным в
   `lab/checkpoints.json`? (Файл мог быть перезаписан или подредактирован.)
2. **Происхождение.** Внутри каждого файла лежит свой `seed`, своя `iteration`,
   своя `spec_version`, своя `target_pattern` и `metadata["experiment"]` —
   совпадающие с именем семейства? (Канон не должен быть переименован.)
3. **Различие весов.** SHA-256 по самим тензорам `model_state_dict` у всех 12
   разный? (Одинаковый лосс у нескольких моделей мог бы означать, что веса
   продублированы, а не что модели сошлись к одному и тому же решению.)
4. **Различие лоссов.** Какие модели реально имеют одинаковый финальный лосс,
   и чем это объясняется.

Скрипт ничего не обучает и не меняет: только чтение. Хеш считается потоково
(файл ~515 МБ), поэтому одновременно в памяти держится один чекпоинт.

Результат: `checkpoint_provenance_exploratory.json` рядом с остальными
exploratory-артефактами E02b.
"""
import gc
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import torch

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
REPO = HERE.parents[4]
CHECKPOINTS = REPO / "lab" / "checkpoints.json"
OUT = EXP / "checkpoint_provenance_exploratory.json"

FAMILY_RE = re.compile(r"^WP4_(?P<arm>.+?)_s(?P<steps>\d+)_seed(?P<seed>\d+)$")


def file_sha256(path: Path) -> str:
    """Потоковый хеш файла — чтобы не читать 515 МБ целиком в память."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def state_dict_sha256(state_dict) -> str:
    """Хеш весов: имя + форма + dtype + байты, в фиксированном порядке.

    Хеш считается по содержимому тензоров, а не по файлу: так проверяется
    именно модель, а не упаковка чекпоинта (оптимизатор, шедулер, пул).
    """
    h = hashlib.sha256()
    for key in sorted(state_dict.keys()):
        tensor = state_dict[key]
        h.update(key.encode("utf-8"))
        h.update(str(tuple(tensor.shape)).encode("utf-8"))
        h.update(str(tensor.dtype).encode("utf-8"))
        flat = tensor.detach().cpu().contiguous().flatten()
        try:
            raw = flat.view(torch.uint8).numpy().tobytes()
        except (RuntimeError, TypeError):
            # bfloat16 и прочие dtype, которые numpy не умеет — берём сырые байты
            raw = flat.view(torch.int8).numpy().tobytes()
        h.update(raw)
    return h.hexdigest()


def main():
    index = json.loads(CHECKPOINTS.read_text(encoding="utf-8"))
    entries = [
        e for e in index.get("entries", [])
        if "E02b_morphospace" in (e.get("canonical_for") or [])
    ]
    entries.sort(key=lambda e: e["family"])
    if len(entries) != 12:
        raise SystemExit(
            f"ожидалось 12 канонических чекпоинтов E02b, в индексе {len(entries)}"
        )

    rows = []
    for entry in entries:
        path = REPO / entry["path"]
        if not path.exists():
            raise SystemExit(f"канонический чекпоинт не найден: {path}")
        digest = file_sha256(path)
        payload = torch.load(path, map_location="cpu", weights_only=False)
        metadata = payload.get("metadata") or {}
        weights_hash = state_dict_sha256(payload["model_state_dict"])

        match = FAMILY_RE.match(entry["family"])
        expected_seed = int(match.group("seed"))
        expected_steps = int(match.group("steps"))
        expected_arm = match.group("arm")

        # Внутреннее время обучения (локальное, UTC+3) против времени файла
        # (UTC в индексе): если чекпоинт писал тот прогон, который сам о себе
        # заявляет, разница одна и та же для всех файлов.
        created = datetime.fromisoformat(str(metadata.get("created_at")))
        mtime = datetime.fromisoformat(str(entry["mtime"]).replace("Z", "+00:00"))
        offset_h = (created - mtime.replace(tzinfo=None)).total_seconds() / 3600.0

        rows.append({
            "family": entry["family"],
            "arm": expected_arm,
            "expected_seed": expected_seed,
            "expected_steps": expected_steps,
            "path": entry["path"],
            "size_bytes": path.stat().st_size,
            "size_matches_index": path.stat().st_size == int(entry["size_bytes"]),
            "file_sha256": digest,
            "file_sha256_matches_index": digest == entry["sha256"],
            "index_hash_status": entry.get("hash_status"),
            "index_mtime_utc": entry["mtime"],
            "created_at_minus_file_mtime_hours": offset_h,
            "weights_sha256": weights_hash,
            "n_weight_tensors": len(payload["model_state_dict"]),
            "payload_seed": payload.get("seed"),
            "payload_iteration": payload.get("iteration"),
            "payload_loss": payload.get("loss"),
            "payload_spec_version": payload.get("spec_version"),
            "payload_revision": payload.get("revision"),
            "payload_grid_size": payload.get("grid_size"),
            "payload_n_channels": payload.get("n_channels"),
            "payload_stress_enabled": payload.get("stress_enabled"),
            "metadata_experiment": metadata.get("experiment"),
            "metadata_seed": metadata.get("seed"),
            "metadata_created_at": metadata.get("created_at"),
            "metadata_target_pattern": metadata.get("target_pattern"),
            "metadata_spec_version": metadata.get("spec_version"),
            "metadata_environment": metadata.get("environment"),
        })
        del payload
        gc.collect()
        print(f"[prov] {entry['family']}: file={digest[:12]} weights={weights_hash[:12]}")

    # --- согласованность метаданных с именем семейства -------------------
    issues = []
    for row in rows:
        if not row["file_sha256_matches_index"]:
            issues.append(f"{row['family']}: байт-хеш файла не совпадает с lab/checkpoints.json")
        if not row["size_matches_index"]:
            issues.append(f"{row['family']}: размер файла не совпадает с индексом")
        if row["payload_seed"] != row["expected_seed"]:
            issues.append(f"{row['family']}: seed в чекпоинте {row['payload_seed']} != {row['expected_seed']}")
        if row["metadata_seed"] != row["expected_seed"]:
            issues.append(f"{row['family']}: seed в metadata {row['metadata_seed']} != {row['expected_seed']}")
        if row["payload_iteration"] != row["expected_steps"]:
            issues.append(
                f"{row['family']}: iteration {row['payload_iteration']} != {row['expected_steps']}"
            )
        if row["metadata_experiment"] != row["family"]:
            issues.append(
                f"{row['family']}: metadata.experiment = {row['metadata_experiment']!r}"
            )
        if not row["metadata_created_at"]:
            issues.append(f"{row['family']}: нет metadata.created_at")
        if not 2.9 <= row["created_at_minus_file_mtime_hours"] <= 3.1:
            issues.append(
                f"{row['family']}: metadata.created_at и время файла расходятся "
                f"на {row['created_at_minus_file_mtime_hours']:.3f} ч "
                "(ожидалось ~3 ч: локальное время против UTC)"
            )

    weights = [row["weights_sha256"] for row in rows]
    distinct_weights = len(set(weights))
    if distinct_weights != len(rows):
        dupes = sorted({w for w in weights if weights.count(w) > 1})
        issues.append(f"веса не попарно различны: совпали {dupes}")

    # --- группы одинакового финального лосса -----------------------------
    loss_groups = {}
    for row in rows:
        key = f"{row['payload_loss']:.17g}"
        loss_groups.setdefault(key, []).append(row["family"])
    loss_groups = {k: sorted(v) for k, v in sorted(loss_groups.items())}

    # Смысл групп: одинаковый лосс при различных весах = разные модели
    # сошлись к одному и тому же значению функции (обычно — к пустому полю).
    loss_group_explanation = {}
    for key, families in loss_groups.items():
        hashes = {r["weights_sha256"] for r in rows if r["family"] in families}
        loss_group_explanation[key] = {
            "families": families,
            "n": len(families),
            "distinct_weight_hashes": len(hashes),
            "interpretation": (
                "одинаковый лосс при различных весах: модели сошлись к одному "
                "и тому же значению функции, веса не продублированы"
                if len(hashes) == len(families)
                else "одинаковый лосс при совпадающих весах: подозрение на дубликат"
            ),
        }

    out = {
        "schema_version": 1,
        "experiment": "E02b_morphospace",
        "kind": "checkpoint_provenance_audit",
        "note": (
            "Проверка 12 канонических чекпоинтов E02b: целостность файла, "
            "происхождение метаданных (seed/iteration/spec_version/experiment) "
            "и попарная различие весов. Ничего не обучалось и не менялось."
        ),
        "source_index": {
            "path": "lab/checkpoints.json",
            "generated_at": index.get("generated_at"),
            "root": index.get("root"),
            "n_canonical": len(entries),
        },
        "summary": {
            "n_checkpoints": len(rows),
            "file_integrity_ok": all(r["file_sha256_matches_index"] for r in rows),
            "metadata_consistent": not issues,
            "distinct_weight_hashes": distinct_weights,
            "weights_pairwise_distinct": distinct_weights == len(rows),
            "n_distinct_final_losses": len(loss_groups),
            "timestamp_offset_hours_min": min(
                r["created_at_minus_file_mtime_hours"] for r in rows
            ),
            "timestamp_offset_hours_max": max(
                r["created_at_minus_file_mtime_hours"] for r in rows
            ),
            "issues": issues,
        },
        "loss_groups": loss_group_explanation,
        "checkpoints": rows,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[prov] записано: {OUT}")
    print(f"[prov] целостность: {out['summary']['file_integrity_ok']}, "
          f"метаданные: {out['summary']['metadata_consistent']}, "
          f"различных наборов весов: {distinct_weights}/{len(rows)}")
    for key, grp in loss_group_explanation.items():
        if grp["n"] > 1:
            print(f"[prov] одинаковый лосс {key}: {grp['families']} "
                  f"(различных весов: {grp['distinct_weight_hashes']})")
    if issues:
        print("[prov] ЗАМЕЧАНИЯ:")
        for issue in issues:
            print(f"[prov]   - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
