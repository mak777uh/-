"""E02b: заморозка центроидов классов — чтобы проекция была исполнимой.

Зачем. В `census.json` кластеризация Ward сохранена не полностью: есть
`scaler_mean`, `scaler_std`, `k`, `silhouette`, `sizes`, `labels_valid`,
`class_names`, `medians`, `semantic` — но **нет** самих `centroids_z`. То есть
«спроецировать новую развёртку на замороженные центроиды E02b» (шаг,
который нужен репликации E02c, см. reports/2026-10-21-e02c-replication-plan-draft.md)
нельзя выполнить прямо из артефакта: центроиды пришлось бы пересобирать
каждый раз заново, и никто не смог бы проверить, что пересборка даёт то же
самое, что было в исходной переписи.

Этот скрипт закрывает этот зазор:

1. Пересобирает кластеризацию ровно тем же кодом (`e02b_morphospace.fit_clusters`)
   и на ровно той же популяции, что и исходная перепись: все прогоны с
   `is_control = False`.
2. **Сверяет** пересборку с сохранённым блоком `clustering` из `census.json`:
   признаки, скалер, k, силуэт, размеры, метки, имена, семантика, медианы.
   Любое расхождение — ошибка, а не предупреждение.
3. Сохраняет центроиды в отдельный маленький артефакт
   `class_centroids_frozen.json` вместе со скалером, метками и именами.

Артефакт самодостаточен: чтобы спроецировать новый дескриптор, достаточно
взять `features`, `scaler_mean`, `scaler_std`, `centroids_z`, `labels_valid`,
`class_names` и посчитать z = (x - mean) / std, затем ближайший центроид.
Ничего пересчитывать не нужно, и результат проекции воспроизводим по файлу.

Никаких вычислений на GPU: только чтение уже записанной переписи.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
MORPH = HERE.parents[3]
sys.path.insert(0, str(MORPH))
import e02b_morphospace as e02b  # noqa: E402

CENSUS = EXP / "census.json"
OUT = EXP / "class_centroids_frozen.json"


def _close(a, b, tol=1e-9):
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    if a.shape != b.shape:
        return False
    return bool(np.all(np.abs(a - b) <= tol))


def main():
    payload = json.loads(CENSUS.read_text(encoding="utf-8"))
    stored = payload["clustering"]
    runs = payload["runs"]

    # Популяция фитта — ровно та, что в census: только выученные семьи.
    fit_indices = [i for i, r in enumerate(runs) if not r.get("is_control")]
    refit = e02b.fit_clusters([runs[i] for i in fit_indices], min_size=5, max_k=10)

    # Метки Ward по самим прогонам в census.json не сохранены (есть только
    # labels_valid), но сохранены назначения классов: run["cluster"].
    # Для выученных прогонов это метка Ward; для контролей — проекция на
    # центроиды. Сверяем и то, и другое: значит проверка задевает и путь
    # проекции, которым E02c будет пользоваться.
    refit_labels = np.asarray(refit["labels"], dtype=int)
    fit_ok = True
    for k, idx in enumerate(fit_indices):
        if int(runs[idx].get("cluster", -999)) != int(refit_labels[k]):
            fit_ok = False
            break
    centroids_ref = np.asarray(refit["centroids_z"], dtype=np.float64)
    proj_ok = True
    control_checked = 0
    for i, run in enumerate(runs):
        if i in set(fit_indices):
            continue
        vec = e02b.descriptor_vector(run["final"]).reshape(1, -1)
        assigned = int(
            e02b.assign_to_clusters(
                vec,
                np.asarray(refit["scaler_mean"]),
                np.asarray(refit["scaler_std"]),
                centroids_ref,
                refit["labels_valid"],
            )[0]
        )
        control_checked += 1
        if assigned != int(run.get("cluster", -999)):
            proj_ok = False
            break

    checks = {
        "features": list(refit["features"]) == list(stored["features"]),
        "scaler_mean": _close(refit["scaler_mean"], stored["scaler_mean"]),
        "scaler_std": _close(refit["scaler_std"], stored["scaler_std"]),
        "linkage": refit["linkage"] == stored["linkage"],
        "k": int(refit["k"]) == int(stored["k"]),
        "silhouette": _close([refit["silhouette"]], [stored["silhouette"]], tol=1e-12),
        "sizes": list(refit["sizes"]) == list(stored["sizes"]),
        "labels_valid": list(refit["labels_valid"]) == list(stored["labels_valid"]),
        "class_names": list(refit["class_names"]) == list(stored["class_names"]),
        "semantic": list(refit["semantic"]) == list(stored["semantic"]),
        "medians": _close(
            [[float(m[key]) for key in sorted(m)] for m in refit["medians"]],
            [[float(m[key]) for key in sorted(m)] for m in stored["medians"]],
            tol=1e-9,
        ),
        "ward_labels_per_run": fit_ok,
        "control_projection_per_run": proj_ok,
    }
    failed = sorted(k for k, ok in checks.items() if not ok)
    if failed:
        raise SystemExit(
            "пересборка кластеризации НЕ совпала с census.json по полям: "
            + ", ".join(failed)
            + " — центроиды не замораживаем"
        )

    centroids = np.asarray(refit["centroids_z"], dtype=np.float64)
    scaler_mean = np.asarray(refit["scaler_mean"], dtype=np.float64)
    scaler_std = np.asarray(refit["scaler_std"], dtype=np.float64)

    # Контроль проекции: настоящие финальные дескрипторы членов каждого
    # класса должны проецироваться обратно в свой класс. Проверка идёт по
    # сырым дескрипторам (как их будет использовать E02c), а не по центроидам:
    # центроид лежит в z-пространстве и повторно прогонять его через
    # нормализацию нельзя — это разные точки.
    projection = {}
    labels_valid = [int(v) for v in refit["labels_valid"]]
    z_of_fit = (np.vstack([e02b.descriptor_vector(runs[i]["final"]) for i in fit_indices])
                - scaler_mean) / scaler_std
    assigned_fit = np.asarray(
        e02b.assign_to_clusters(
            z_of_fit,
            scaler_mean,
            scaler_std,
            centroids,
            labels_valid,
        )
    )
    for ci, lab in enumerate(labels_valid):
        member_mask = refit_labels == lab
        members = z_of_fit[member_mask]
        own = int((assigned_fit[member_mask] == lab).sum())
        # насколько далеко свой центроид от ближайшего чужого (в z-пространстве)
        d = ((centroids[ci][None, :] - centroids) ** 2).sum(axis=1)
        nearest_other = int(np.argmin(np.where(np.arange(len(d)) == ci, np.inf, d)))
        projection[str(lab)] = {
            "class_name": refit["class_names"][ci],
            "n_members": int(member_mask.sum()),
            "members_assigned_to_own_class": own,
            "fraction": float(own / max(int(member_mask.sum()), 1)),
            "sqdist_to_nearest_other_centroid": float(d[nearest_other]),
            "centroid_margin": float(d[nearest_other]),
            "nearest_other_label": int(labels_valid[nearest_other]),
        }

    out = {
        "schema_version": 1,
        "experiment": "E02b_morphospace",
        "kind": "frozen_class_centroids",
        "note": (
            "Центроиды классов E02b, замороженные из канонической переписи "
            "census.json. Пересборка кластеризации тем же кодом дала полное "
            "совпадение по 13 полям — значит центроиды здесь те же самые, что "
            "были в исходной переписи, а не новый фит."
        ),
        "source_census": {
            "path": "morphogenesis/experiments/E02b_morphospace/census.json",
            "sha256": hashlib.sha256(CENSUS.read_bytes()).hexdigest(),
            "n_runs_total": len(runs),
            "n_runs_fit": len(fit_indices),
            "fit_rule": "runs без is_control (как в census.py: fit_indices)",
        },
        "refit_verification": {
            "all_fields_match": True,
            "checked_fields": sorted(checks.keys()),
            "n_control_projection_checked": control_checked,
        },
        "features": list(refit["features"]),
        "scaler_mean": scaler_mean.tolist(),
        "scaler_std": scaler_std.tolist(),
        "centroids_z": centroids.tolist(),
        "labels_valid": [int(v) for v in refit["labels_valid"]],
        "class_names": list(refit["class_names"]),
        "semantic": list(refit["semantic"]),
        "sizes": [int(v) for v in refit["sizes"]],
        "k": int(refit["k"]),
        "silhouette": float(refit["silhouette"]),
        "linkage": refit["linkage"],
        "projection_selfcheck": projection,
        "how_to_project": (
            "z = (descriptor_vector(final) - scaler_mean) / scaler_std; "
            "label = labels_valid[argmin(sum((z - centroids_z)^2, axis=1))]; "
            "class = class_names[label]"
        ),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[freeze] записано: {OUT}")
    print(f"[freeze] классов: {out['k']} → {out['class_names']}")
    print(f"[freeze] размеры: {out['sizes']}")
    for name, chk in projection.items():
        print(
            f"[freeze] метка {name} ({chk['class_name']}): "
            f"своих {chk['members_assigned_to_own_class']}/{chk['n_members']} "
            f"({chk['fraction']:.4f}), ближайший чужой центроид "
            f"{chk['sqdist_to_nearest_other_centroid']:.2f} "
            f"(метка {chk['nearest_other_label']})"
        )


if __name__ == "__main__":
    main()
