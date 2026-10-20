"""test_e02b_morphospace.py — дескрипторы и кластеризация E02b без GPU.

Проверяем то, что легко сделать неправильно и что потом трудно заметить в
отчёте: бинаризация должна совпадать с topology.get_binary_mask; кольцо и
пятно должны различаться топологией; Ward должен находить три хорошо
разделимых группы; контроли не должны попадать в H1.
"""

import os
import sys
import unittest

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import e02b_morphospace as e02b
from target_patterns import create_target
from topology import get_binary_mask


def _state_from_masks(mask: np.ndarray, alive: bool = True) -> torch.Tensor:
    state = torch.zeros(1, config.N_CHANNELS, config.GRID_SIZE, config.GRID_SIZE)
    m = torch.as_tensor(mask, dtype=torch.float32)
    state[0, config.VISIBLE_CHANNEL] = 4.0 * (2.0 * m - 1.0)
    state[0, config.ALIVE_CHANNEL] = 4.0 if alive else -4.0
    return state


class TestDescriptors(unittest.TestCase):
    def test_binary_matches_topology_source_of_truth(self):
        ring = create_target(device="cpu")[0, 0].numpy() > 0.5
        state = _state_from_masks(ring)
        alive, binary, _, _, _ = e02b._state_arrays(state)
        expected = get_binary_mask(state).astype(bool)
        self.assertTrue(np.array_equal(binary, expected))
        self.assertTrue(alive.all())  # alpha=4 везде: живы все, маску задаёт visible

    def test_ring_has_hole_disk_does_not(self):
        ring = create_target(device="cpu")[0, 0].numpy() > 0.5
        yy, xx = np.indices(ring.shape)
        disk = ((yy - 31.5) ** 2 + (xx - 31.5) ** 2) <= 10 ** 2
        ring_desc = e02b.describe_state(_state_from_masks(ring))
        disk_desc = e02b.describe_state(_state_from_masks(disk))
        self.assertGreaterEqual(ring_desc["b1"], 1)
        self.assertEqual(disk_desc["b1"], 0)
        self.assertEqual(ring_desc["b0"], 1)
        self.assertEqual(disk_desc["b0"], 1)
        # Кольцо пустое в центре, пятно заполнено; профиль нормирован на радиус
        # самой маски, поэтому это свойство формы, а не размера.
        self.assertLess(ring_desc["radial_center_occupancy"], disk_desc["radial_center_occupancy"])
        self.assertGreater(ring_desc["radial_var"], disk_desc["radial_var"])

    def test_death_is_not_structured(self):
        empty = np.zeros((config.GRID_SIZE, config.GRID_SIZE), dtype=bool)
        desc = e02b.describe_state(_state_from_masks(empty, alive=False))
        self.assertLess(desc["alive_fraction"], 0.01)
        self.assertEqual(e02b._cluster_semantic(desc), "death")


class TestClustering(unittest.TestCase):
    def _runs(self):
        runs = []
        groups = [
            dict(alive_fraction=0.50, binary_fraction=0.30, b0=2, b1=1, bright_fraction=0.30,
                 soft_mean=0.30, entropy=0.60, log1p_b0=np.log1p(2), log1p_b1=np.log1p(1),
                 chi=1, bbox_fill=0.60, largest_component_fraction=0.20, radial_var=0.02,
                 radial_peak_bin=6, radial_center_occupancy=0.10, symmetry_rot_centered=0.8,
                 symmetry_reflect_centered=0.9, autocorr_lag1=0.5, autocorr_lag4=0.3,
                 edge_fraction=0.0),
            dict(alive_fraction=0.90, binary_fraction=0.80, b0=1, b1=0, bright_fraction=0.80,
                 soft_mean=0.80, entropy=0.30, log1p_b0=np.log1p(1), log1p_b1=0.0,
                 chi=1, bbox_fill=0.90, largest_component_fraction=0.80, radial_var=0.005,
                 radial_peak_bin=1, radial_center_occupancy=0.95, symmetry_rot_centered=0.6,
                 symmetry_reflect_centered=0.6, autocorr_lag1=0.9, autocorr_lag4=0.7,
                 edge_fraction=0.0),
            dict(alive_fraction=0.0, binary_fraction=0.0, b0=0, b1=0, bright_fraction=0.0,
                 soft_mean=0.0, entropy=0.0, log1p_b0=0.0, log1p_b1=0.0, chi=0,
                 bbox_fill=0.0, largest_component_fraction=0.0, radial_var=0.0,
                 radial_peak_bin=-1, radial_center_occupancy=0.0, symmetry_rot_centered=0.0,
                 symmetry_reflect_centered=0.0, autocorr_lag1=0.0, autocorr_lag4=0.0,
                 edge_fraction=0.0),
        ]
        for gi, base in enumerate(groups):
            for j in range(6):
                final = dict(base)
                final["alive_fraction"] += 0.001 * j
                runs.append({"family": f"F{gi}", "seed": j, "final": final})
        return runs

    def test_ward_finds_three_separated_groups(self):
        runs = self._runs()
        c = e02b.fit_clusters(runs, min_size=5, max_k=10)
        self.assertEqual(c["k"], 3)
        self.assertEqual(c["sizes"], [6, 6, 6])
        self.assertEqual(sum(1 for s in c["semantic"] if s == "structured"), 2)
        self.assertEqual(sum(1 for s in c["semantic"] if s == "death"), 1)
        self.assertIsNotNone(c["silhouette"])
        self.assertGreater(c["silhouette"], 0.5)

    def test_controls_are_projected_not_fitted(self):
        base_runs = self._runs()
        # Контроли: H-P1 похож на «кольцо», untrained — на «пятно». Если бы они
        # участвовали в Ward, размеры классов изменились бы.
        control_like = [dict(base_runs[0]["final"]), dict(base_runs[6]["final"])]
        runs = base_runs + [
            {"family": "WP4_H-P1_s2000_seed42", "is_control": True, "final": control_like[0]},
            {"family": "untrained", "is_control": True, "final": control_like[1]},
        ]
        for r in runs:
            r["traj_features"] = e02b.descriptor_vector(r["final"]).reshape(1, -1)
            r["trajectory"] = [{"step": 50}]
        fit_indices = [i for i, r in enumerate(runs) if not r.get("is_control")]
        c = e02b.fit_clusters([runs[i] for i in fit_indices], min_size=5, max_k=10)
        e02b._apply_clustering(runs, c, fit_indices)
        self.assertEqual(sorted(c["sizes"]), [6, 6, 6])
        for r in runs[18:]:
            self.assertIn(r["cluster"], c["labels_valid"])
            self.assertFalse(r["is_outlier"])
        self.assertNotIn("traj_features", runs[0])

    def test_h1_excludes_controls(self):
        runs = []
        for _ in range(64):
            runs.append(
                {
                    "family": "WP4_R-9_s2000_seed42",
                    "arm": "R-9",
                    "is_control": False,
                    "cluster": 1,
                    "semantic": "structured",
                    "class_name": "struct_1",
                    "stability_last_quarter": 0.95,
                }
            )
        for _ in range(10):
            runs.append(
                {
                    "family": "WP4_H-P1_s2000_seed42",
                    "arm": "H-P1",
                    "is_control": True,
                    "cluster": 1,
                    "semantic": "structured",
                    "class_name": "struct_1",
                    "stability_last_quarter": 1.0,
                }
            )
        h1 = e02b.evaluate_h1(runs, ["WP4_R-9_s2000_seed42", "WP4_H-P1_s2000_seed42"])
        self.assertEqual(h1["evaluated_runs"], 64)
        self.assertTrue(h1["supported"])
        self.assertFalse(h1["refuted"])

    def test_outcome_ignores_controls(self):
        runs = []
        for _ in range(64):
            runs.append({"is_control": False, "semantic": "structured"})
        for _ in range(64):
            runs.append({"is_control": True, "semantic": "uniform_dark"})
        out = e02b._outcome(
            {"struct_max_fraction_by_family": {"R-9": 0.9}},
            {"status": "supported"},
            {"by_class": {"1": {"recovery_fraction": 0.6}}, "max_recovery_fraction": 0.6},
            runs,
            [1, 2],
        )
        self.assertEqual(out["n_runs"], 64)
        self.assertEqual(out["death_or_uniform_fraction"], 0.0)

    def test_adjusted_rand_identical_is_one(self):
        a = np.array([0, 0, 1, 1, 2, 2])
        self.assertAlmostEqual(e02b._adjusted_rand(a, a), 1.0)


class TestPerturbations(unittest.TestCase):
    def _ring_state(self):
        ring = create_target(device="cpu")[0, 0].numpy() > 0.5
        state = _state_from_masks(ring)
        # Дать всем каналам различимые значения: ампутация обязана обнулить
        # клетку целиком, а не только видимый канал.
        state += 0.01 * torch.arange(config.N_CHANNELS).view(1, -1, 1, 1)
        return state

    def test_amputation_zeroes_selected_cells_all_channels(self):
        state = self._ring_state()
        gen = config.create_deterministic_generator(7)
        out, meta = e02b._clone_perturbed_state(
            state, {"kind": "amputation", "fraction": 0.20}, gen, torch.device("cpu")
        )
        alive_before = torch.sigmoid(state[0, config.ALIVE_CHANNEL]) > config.ALIVE_THRESHOLD
        dead = (out[0].abs().sum(dim=0) == 0) & alive_before
        self.assertEqual(int(dead.sum()), meta["cells"])
        self.assertEqual(meta["zeroed"], "all_channels")
        self.assertTrue(torch.equal(out[0, :, ~dead], state[0, :, ~dead]))

    def test_cut_half_zeroes_left_half(self):
        state = self._ring_state()
        out, meta = e02b._clone_perturbed_state(
            state, {"kind": "cut_half"}, config.create_deterministic_generator(1), torch.device("cpu")
        )
        w = state.shape[-1]
        self.assertEqual(meta["cut"], w // 2)
        self.assertEqual(float(out[:, :, :, : w // 2].abs().sum()), 0.0)
        self.assertTrue(torch.equal(out[:, :, :, w // 2 :], state[:, :, :, w // 2 :]))

    def test_dead_control_is_zero(self):
        out, _ = e02b._clone_perturbed_state(
            self._ring_state(), {"kind": "dead_control"}, config.create_deterministic_generator(1),
            torch.device("cpu"),
        )
        self.assertEqual(float(out.abs().sum()), 0.0)

    def test_transplant_is_centered_and_skips_without_mask(self):
        state = self._ring_state()
        out, meta = e02b._clone_perturbed_state(
            state, {"kind": "transplant"}, config.create_deterministic_generator(1), torch.device("cpu")
        )
        self.assertFalse(meta.get("skipped"))
        ph, pw = meta["patch_shape"]
        dy = (state.shape[-2] - ph) // 2
        dx = (state.shape[-1] - pw) // 2
        self.assertTrue(torch.equal(out[:, :, dy : dy + ph, dx : dx + pw], state[:, :, meta["bbox"][1] : meta["bbox"][3] + 1, meta["bbox"][0] : meta["bbox"][2] + 1]))
        self.assertEqual(float(out.abs().sum(dim=1).gt(0).sum()), ph * pw)
        empty = torch.zeros_like(state)
        out2, meta2 = e02b._clone_perturbed_state(
            empty, {"kind": "transplant"}, config.create_deterministic_generator(1), torch.device("cpu")
        )
        self.assertTrue(meta2.get("skipped"))


class TestDynamics(unittest.TestCase):
    def test_fixed(self):
        points = [
            {"step": s, "alive_fraction": 0.5, "binary_fraction": 0.2, "b0": 1, "b1": 1,
             "radial_peak_bin": 5, "entropy": 0.5, "delta_per_step": 1e-6}
            for s in (50, 100, 150)
        ]
        self.assertEqual(e02b.classify_dynamics(points, 50)["class"], "fixed")

    def test_cycle(self):
        points = []
        for i in range(6):
            points.append(
                {
                    "step": (i + 1) * 50,
                    "alive_fraction": 0.5 if i % 2 == 0 else 0.6,
                    "binary_fraction": 0.2 if i % 2 == 0 else 0.3,
                    "b0": 1,
                    "b1": 1,
                    "radial_peak_bin": 5,
                    "entropy": 0.5 if i % 2 == 0 else 0.6,
                    "delta_per_step": 0.1,
                }
            )
        dyn = e02b.classify_dynamics(points, 50)
        self.assertEqual(dyn["class"], "cycle")
        self.assertEqual(dyn["period_steps"], 100)

    def test_settle_step(self):
        points = [
            {"step": 50, "alive_fraction": 0.9, "binary_fraction": 0.3, "b0": 1, "b1": 1, "radial_peak_bin": 5},
            {"step": 100, "alive_fraction": 0.5, "binary_fraction": 0.2, "b0": 1, "b1": 1, "radial_peak_bin": 5},
            {"step": 150, "alive_fraction": 0.5, "binary_fraction": 0.2, "b0": 1, "b1": 1, "radial_peak_bin": 5},
        ]
        self.assertEqual(e02b.settle_step(points), 100)


class TestMisc(unittest.TestCase):
    def test_parse_seeds(self):
        self.assertEqual(e02b._parse_seeds("0-2,5,5"), [0, 1, 2, 5])

    def test_alive_mask_from_overrides(self):
        self.assertFalse(e02b._alive_mask_from_overrides({"ALIVE_WARMUP_ITERS": 9999}, 2000))
        self.assertTrue(e02b._alive_mask_from_overrides({}, 2000))


if __name__ == "__main__":
    unittest.main()
