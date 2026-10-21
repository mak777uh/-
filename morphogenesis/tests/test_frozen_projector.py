"""Замороженный проектор снимков: устойчивость, не зависящая от состава переписи.

Ward обучается внутри переписи, поэтому кластер 2 в одной переписи называется
`struct_1`, а в другой — `struct_2`; «устойчивость» по такому разбиению
несравнима между прогонами. Проекция на замороженные центроиды E02b от состава
не зависит — эти тесты фиксируют её математику.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MORPH = ROOT / "morphogenesis"
FROZEN = MORPH / "experiments" / "E02b_morphospace" / "class_centroids_frozen.json"


def load_module(name: str, path: Path):
    if str(MORPH) not in sys.path:
        sys.path.insert(0, str(MORPH))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_projector():
    return {
        "mean": np.zeros(1),
        "std": np.ones(1),
        "centroids": np.array([[0.0], [10.0]]),
        "labels": np.array([1, 2]),
        "class_names": ["low", "high"],
    }


def test_nearest_frozen_centroid_labels() -> None:
    e02b = load_module("e02b_morphospace_proj", MORPH / "e02b_morphospace.py")
    traj = np.array([[0.1], [0.2], [9.9], [10.1]])
    labels = e02b.frozen_labels_for_trajectory(traj, fake_projector())
    assert labels.tolist() == [1, 1, 2, 2]
    assert e02b.frozen_class_name(1, fake_projector()) == "low"
    assert e02b.frozen_class_name(2, fake_projector()) == "high"


def test_stability_counts_last_quarter_against_final_label() -> None:
    e02b = load_module("e02b_morphospace_stab", MORPH / "e02b_morphospace.py")
    labels = np.array([1, 1, 1, 1, 1, 2, 2, 2, 2, 2])
    stability, start_index = e02b.trajectory_stability(labels)
    assert stability == 1.0
    assert start_index == 5

    mixed = np.array([1, 1, 1, 2, 2, 2, 1, 1])
    stability2, start2 = e02b.trajectory_stability(mixed)
    assert stability2 == 1.0
    assert start2 == 6


def test_empty_trajectory_gives_zero_stability() -> None:
    e02b = load_module("e02b_morphospace_empty", MORPH / "e02b_morphospace.py")
    stability, start = e02b.trajectory_stability(np.array([], dtype=int))
    assert stability == 0.0
    assert start is None


def test_real_frozen_file_loads_and_projects_selfcheck() -> None:
    e02b = load_module("e02b_morphospace_real", MORPH / "e02b_morphospace.py")
    projector = e02b.load_frozen_projector(str(FROZEN))
    assert projector["class_names"][projector["labels"].tolist().index(5)] == "struct_2"
    payload = json.loads(FROZEN.read_text(encoding="utf-8"))
    assert len(projector["centroids"]) == len(payload["labels_valid"]) == 5
