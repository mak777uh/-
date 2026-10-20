"""E02b, exploratory: 2D-карта морфопространства по 18 дескрипторам.

PCA строится только на 704 выученных развёртках (контроли проецируются, но не
задают оси). Цвет — класс Ward из census; чёрные контуры — центроиды классов.
Это визуализация уже опубликованной кластеризации, а не новая проверка гипотез.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
REPO = HERE.parents[4]
import sys  # noqa: E402

sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

CENSUS = EXP / "census.json"
OUT = REPO / "reports" / "figures" / "e02b_morphospace_pca.png"
COLORS = {
    "struct_1": "#1f77b4",
    "struct_2": "#2ca02c",
    "death": "#d62728",
    "uniform_dark": "#7f7f7f",
    "uniform_bright": "#e6a700",
}

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}
learned = [r for r in census["runs"] if not r.get("is_control")]
controls = [r for r in census["runs"] if r.get("is_control")]

X = np.vstack([e02b.descriptor_vector(r["final"]) for r in learned])
Z = (X - mean) / std
# PCA через SVD: sklearn в venv не установлен, а 704×18 считается мгновенно.
_u, s, vt = np.linalg.svd(Z - Z.mean(axis=0), full_matrices=False)
ratio = (s**2) / np.sum(s**2)
xy = (Z - Z.mean(axis=0)) @ vt[:2].T
ctrl_z = (np.vstack([e02b.descriptor_vector(r["final"]) for r in controls]) - mean) / std
ctrl_xy = (ctrl_z - Z.mean(axis=0)) @ vt[:2].T

centroids = []
for c in valid:
    members = [z for z, r in zip(Z, learned) if int(r["cluster"]) == int(c)]
    if members:
        centroids.append((int(c), np.asarray(members).mean(axis=0)))
cent_xy = (np.vstack([v for _c, v in centroids]) - Z.mean(axis=0)) @ vt[:2].T

fig, ax = plt.subplots(figsize=(8.2, 6.2))
for c in valid:
    name = names[int(c)]
    mask = np.array([int(r["cluster"]) == int(c) for r in learned])
    ax.scatter(
        xy[mask, 0],
        xy[mask, 1],
        s=16,
        alpha=0.72,
        color=COLORS.get(name, "#333333"),
        label=f"{name} ({int(mask.sum())})",
        linewidths=0,
    )
ax.scatter(
    ctrl_xy[:, 0],
    ctrl_xy[:, 1],
    s=26,
    facecolors="none",
    edgecolors="black",
    linewidths=0.6,
    alpha=0.55,
    label=f"контроли ({len(controls)})",
)
LABEL_POS = {
    "struct_1": (8, 5, "left"),
    "struct_2": (8, -12, "left"),
    "death": (8, -13, "left"),
    "uniform_dark": (0, 13, "center"),
    "uniform_bright": (-8, 5, "right"),
}
for (c, _v), (x, y) in zip(centroids, cent_xy):
    name = names[int(c)]
    ax.scatter([x], [y], s=120, marker="X", color=COLORS.get(name, "#333333"),
               edgecolors="black", linewidths=0.8, zorder=5)
    dx, dy, ha = LABEL_POS.get(name, (7, 5, "left"))
    ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx, dy), fontsize=9,
                fontweight="bold", ha=ha)
ax.margins(x=0.09, y=0.07)
ax.axhline(0, color="black", linewidth=0.4, alpha=0.25)
ax.axvline(0, color="black", linewidth=0.4, alpha=0.25)
ax.set_xlabel(f"PC1 ({ratio[0] * 100:.1f}%)")
ax.set_ylabel(f"PC2 ({ratio[1] * 100:.1f}%)")
ax.set_title(
    "E02b: 704 выученных развёртки, PCA 18 дескрипторов\n"
    f"суммарно {ratio[:2].sum() * 100:.1f}% дисперсии; X — центроиды"
)
ax.legend(loc="best", fontsize=8, frameon=True)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=160)
plt.close(fig)
print(f"[map] written {OUT} ({OUT.stat().st_size / 1e3:.0f} KB)", flush=True)
print(
    "[map] variance",
    [round(float(v), 4) for v in ratio[:2]],
    flush=True,
)
