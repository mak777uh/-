"""

test_topology.py — Тесты топологических функций.

[v5.5-EXP FINAL Rev.7]

Проверяет:

- квадратное кольцо -> бета1 = 1;

- объект на границе -> бета1 = 0;

- три компоненты -> бета0 = 3;

- пустая маска -> бета0 = 0, бета1 = 0;

- полная маска -> бета0 = 1, бета1 = 0\.

"""

import sys

import os

import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from topology import (

    count_connected_components,

    count_holes,

    compute_euler_characteristic,

)

class TestTopology(unittest.TestCase):

    def test_square_ring(self):

        """Простое квадратное кольцо должно давать бета1 = 1."""

        mask = np.zeros((5, 5), dtype=np.uint8)

        mask[1:4, 1:4] = 1

        mask[2, 2] = 0

        b1 = count_holes(mask)

        self.assertEqual(b1, 1, f"Square ring: expected b1=1, got {b1}")

    def test_border_touching_object(self):

        """Объект, касающийся границы, не создаёт ложных дырок."""

        mask = np.zeros((16, 16), dtype=np.uint8)

        mask[0:5, 0:5] = 1

        b1 = count_holes(mask)

        self.assertEqual(b1, 0, f"Border object: expected b1=0, got {b1}")

    def test_three_components(self):

        """Три раздельных пятна должны давать бета0 = 3."""

        mask = np.zeros((24, 24), dtype=np.uint8)

        mask[4:7, 4:7] = 1

        mask[4:7, 16:19] = 1

        mask[16:19, 10:13] = 1

        b0 = count_connected_components(mask)

        self.assertEqual(b0, 3, f"Three components: expected b0=3, got {b0}")

    def test_empty_mask(self):

        """Пустая маска -> бета0 = 0, бета1 = 0."""

        mask = np.zeros((16, 16), dtype=np.uint8)

        b0 = count_connected_components(mask)

        b1 = count_holes(mask)

        self.assertEqual(b0, 0)

        self.assertEqual(b1, 0)

    def test_full_mask(self):

        """Полная маска -> бета0 = 1, бета1 = 0."""

        mask = np.ones((16, 16), dtype=np.uint8)

        b0 = count_connected_components(mask)

        b1 = count_holes(mask)

        self.assertEqual(b0, 1)

        self.assertEqual(b1, 0)

    def test_euler_characteristic(self):

        """chi = b0 - b1."""

        mask = np.zeros((24, 24), dtype=np.uint8)

        mask[4:7, 4:7] = 1

        mask[4:7, 16:19] = 1

        mask[16:19, 10:13] = 1

        chi = compute_euler_characteristic(mask)

        self.assertEqual(chi, 3)

    def test_ring_b1(self):

        """Кольцо должно давать бета1 = 1."""

        mask = np.zeros((32, 32), dtype=np.uint8)

        yy, xx = np.meshgrid(np.arange(32), np.arange(32), indexing="ij")

        center = 16

        dist = np.sqrt((xx - center) ** 2 + (yy - center) ** 2)

        mask[np.abs(dist - 8) <= 2] = 1

        b1 = count_holes(mask)

        self.assertEqual(b1, 1, f"Ring: expected b1=1, got {b1}")

    def test_two_rings_b1(self):

        """Два раздельных кольца -> бета1 = 2."""

        mask = np.zeros((48, 48), dtype=np.uint8)

        # Первое кольцо.

        yy, xx = np.meshgrid(np.arange(48), np.arange(48), indexing="ij")

        c1 = (12, 12)

        dist1 = np.sqrt((xx - c1[0]) ** 2 + (yy - c1[1]) ** 2)

        mask[np.abs(dist1 - 5) <= 1.5] = 1

        # Второе кольцо.

        c2 = (36, 36)

        dist2 = np.sqrt((xx - c2[0]) ** 2 + (yy - c2[1]) ** 2)

        mask[np.abs(dist2 - 5) <= 1.5] = 1

        b1 = count_holes(mask)

        self.assertEqual(b1, 2, f"Two rings: expected b1=2, got {b1}")

if __name__ == "__main__":

    unittest.main()