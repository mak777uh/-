"""E02b, exploratory: насколько классы переписи устойчивы к самой кластеризации.

Гипотезы E02b проверялись на фиксированных метках Ward (k=5), выбранных по
silhouette. Здесь проверяется, не является ли граница `struct_2` артефактом
именно этого k, конкретной выборки сидов или одного признака:

1. sweep k=2..10: ARI с каноническими метками и Jaccard каждого класса;
2. bootstrap 200 ресэмплов при фиксированном k=5: ARI и Jaccard;
3. jackknife по 18 признакам: удалить один — пересчитать Ward(k=5);
4. шум признаков 1/5/10% стандартного масштаба.

Это не переписывает census и не меняет канонические метки: все числа — только
диагностика устойчивости уже опубликованного разбиения.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))

import e02b_morphospace as e02b  # noqa: E402

CENSUS = EXP / "census.json"
OUT = EXP / "cluster_robustness_exploratory.json"
FIXED_K = 5
K_RANGE = range(2, 11)
SELECT_K_RANGE = range(3, 8)
N_BOOT = 200
N_BOOT_K = 100
N_NOISE = 50
NOISE_SIGMAS = (0.01, 0.05, 0.10)
RNG = np.random.default_rng(20261021)

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
if int(cl["k"]) != FIXED_K:
    raise SystemExit(f"ожидался канонический k={FIXED_K}, в census {cl['k']}")
learned = [r for r in census["runs"] if not r.get("is_control")]
X = np.vstack([e02b.descriptor_vector(r["final"]) for r in learned])
mean = np.asarray(cl["scaler_mean"], dtype=float)
std = np.asarray(cl["scaler_std"], dtype=float)
Z = (X - mean) / std
valid = [int(v) for v in cl["labels_valid"]]
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}
y = np.asarray([int(r["cluster"]) for r in learned], dtype=int)
classes = {cid: names[cid] for cid in valid}
if len(learned) != 704:
    raise SystemExit(f"ожидалось 704 выученных прогона, получено {len(learned)}")
for cid in valid:
    if int((y == cid).sum()) != int(cl["sizes"][valid.index(cid)]):
        raise SystemExit(f"размер класса {cid} не совпал с census")


def fit_k(data, k):
    if len(data) < 2 or k < 2:
        return np.zeros(len(data), dtype=int)
    tree = linkage(data, method="ward")
    return fcluster(tree, k, criterion="maxclust").astype(int)


def jaccard_for_class(reference, predicted, cid):
    """Jaccard канонического класса с наиболее перекрывающимся кластером."""
    a = set(np.where(reference == cid)[0].tolist())
    if not a:
        return None
    best = 0
    for c in np.unique(predicted):
        b = set(np.where(predicted == c)[0].tolist())
        best = max(best, len(a & b) / len(a | b))
    return float(best)


def summarize(reference, predicted, mask=None):
    if mask is not None:
        reference = reference[mask]
        predicted = predicted[mask]
    return {
        "ari": float(e02b._adjusted_rand(reference, predicted)),
        "jaccard": {
            classes[cid]: jaccard_for_class(reference, predicted, cid) for cid in valid
        },
    }


# 0. Полный пересчёт должен воспроизвести канонические метки.
full = fit_k(Z, FIXED_K)
base = summarize(y, full)
base["label_matches"] = int((full == y).sum())
print(f"[robust] full refit k={FIXED_K}: ARI={base['ari']:.4f} matches={base['label_matches']}/{len(y)}", flush=True)

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_cluster_robustness",
    "note": (
        "диагностика устойчивости Ward-разбиения; не меняет канонические метки "
        "и не является новой проверкой H1–H4"
    ),
    "n_runs": len(learned),
    "canonical": {
        "k": int(cl["k"]),
        "silhouette": float(cl["silhouette"]),
        "classes": {str(cid): classes[cid] for cid in valid},
        "sizes": {classes[cid]: int((y == cid).sum()) for cid in valid},
    },
    "full_refit": base,
    "k_sweep": [],
    "bootstrap_k5": {},
    "bootstrap_k_selection": {},
    "leave_one_feature_out": [],
    "feature_noise": [],
}

# 1. Sweep k.
for k in K_RANGE:
    labels = fit_k(Z, k)
    sil = e02b._silhouette(Z, labels) if len(set(labels)) >= 2 else 0.0
    row = {"k": int(k), "silhouette": float(sil), "sizes": sorted(Counter(labels.tolist()).values(), reverse=True)}
    row.update(summarize(y, labels))
    result["k_sweep"].append(row)
    print(
        f"[robust] k={k:2d} sil={sil:.3f} ARI={row['ari']:.3f} "
        f"J(struct_2)={row['jaccard']['struct_2']:.3f}",
        flush=True,
    )

# 2. Bootstrap при фиксированном k=5.
ari = []
jac = {classes[cid]: [] for cid in valid}
for _ in range(N_BOOT):
    idx = RNG.integers(0, len(Z), size=len(Z))
    labels = fit_k(Z[idx], FIXED_K)
    unique = np.unique(idx)
    ref = y[unique]
    # Для уникальных индексов берём метку из любого вхождения: дубликаты одного
    # и того же прогона всегда попадают в один кластер, поэтому метка согласована.
    pos = {int(v): i for i, v in enumerate(idx)}
    pred = np.asarray([labels[pos[int(v)]] for v in unique], dtype=int)
    ari.append(float(e02b._adjusted_rand(ref, pred)))
    for cid in valid:
        jac[classes[cid]].append(jaccard_for_class(ref, pred, cid))
result["bootstrap_k5"] = {
    "n": N_BOOT,
    "ari_median": float(np.median(ari)),
    "ari_p05": float(np.percentile(ari, 5)),
    "jaccard_median": {k: float(np.median(v)) for k, v in jac.items()},
    "jaccard_p05": {k: float(np.percentile(v, 5)) for k, v in jac.items()},
}
print(
    f"[robust] bootstrap k=5: ARI med={np.median(ari):.3f} "
    f"J(struct_2) med={np.median(jac['struct_2']):.3f}",
    flush=True,
)

# 3. Bootstrap выбора k по silhouette (та же процедура, что в census).
ks = []
for _ in range(N_BOOT_K):
    idx = RNG.integers(0, len(Z), size=len(Z))
    data = Z[idx]
    tree = linkage(data, method="ward")
    best = None
    for k in SELECT_K_RANGE:
        labels = fcluster(tree, k, criterion="maxclust").astype(int)
        sizes = np.bincount(labels)[1:]
        if sizes.size == 0 or int(sizes.min()) < 5:
            continue
        sil = e02b._silhouette(data, labels)
        if best is None or sil > best[0]:
            best = (sil, k)
    if best is not None:
        ks.append(int(best[1]))
result["bootstrap_k_selection"] = {
    "n": len(ks),
    "range": [min(SELECT_K_RANGE), max(SELECT_K_RANGE)],
    "counts": {str(k): int(v) for k, v in sorted(Counter(ks).items())},
    "selected_k_median": float(np.median(ks)) if ks else None,
    "share_k5": float(np.mean(np.asarray(ks) == FIXED_K)) if ks else None,
}
print(f"[robust] bootstrap k-select: {dict(sorted(Counter(ks).items()))}", flush=True)

# 4. Jackknife по признакам.
for j, feature in enumerate(cl["features"]):
    keep = [i for i in range(Z.shape[1]) if i != j]
    sub = Z[:, keep]
    sub = (sub - sub.mean(axis=0)) / np.where(sub.std(axis=0) < 1e-9, 1.0, sub.std(axis=0))
    labels = fit_k(sub, FIXED_K)
    row = {"feature": feature}
    row.update(summarize(y, labels))
    result["leave_one_feature_out"].append(row)
    print(
        f"[robust] -{feature:24s} ARI={row['ari']:.3f} "
        f"J(struct_2)={row['jaccard']['struct_2']:.3f}",
        flush=True,
    )

# 5. Шум признаков.
for sigma in NOISE_SIGMAS:
    ari_n = []
    jac_n = {classes[cid]: [] for cid in valid}
    for _ in range(N_NOISE):
        labels = fit_k(Z + RNG.normal(0.0, sigma, size=Z.shape), FIXED_K)
        ari_n.append(float(e02b._adjusted_rand(y, labels)))
        for cid in valid:
            jac_n[classes[cid]].append(jaccard_for_class(y, labels, cid))
    result["feature_noise"].append(
        {
            "sigma": float(sigma),
            "n": N_NOISE,
            "ari_median": float(np.median(ari_n)),
            "ari_p05": float(np.percentile(ari_n, 5)),
            "jaccard_median": {k: float(np.median(v)) for k, v in jac_n.items()},
            "jaccard_p05": {k: float(np.percentile(v, 5)) for k, v in jac_n.items()},
        }
    )
    print(
        f"[robust] noise sigma={sigma:.2f}: ARI={np.median(ari_n):.3f} "
        f"J(struct_2)={np.median(jac_n['struct_2']):.3f}",
        flush=True,
    )

result["summary"] = {
    "k5_selected_in_full": base["ari"] >= 0.999,
    "struct_2_jaccard_min_over_k": min(
        row["jaccard"]["struct_2"] for row in result["k_sweep"]
        if row["jaccard"]["struct_2"] is not None
    ),
    "struct_2_bootstrap_jaccard_p05": result["bootstrap_k5"]["jaccard_p05"]["struct_2"],
    "struct_2_lofo_jaccard_min": min(
        row["jaccard"]["struct_2"] for row in result["leave_one_feature_out"]
    ),
    "struct_2_noise_jaccard_min": min(
        row["jaccard_median"]["struct_2"] for row in result["feature_noise"]
    ),
}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
print(f"[robust] saved {OUT}", flush=True)
