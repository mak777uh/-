"""test_atomic_save.py — сохранение чекпоинта не падает от транзиентной блокировки.

На Windows Defender открывает только что записанный 539-МБ nca_best.pt, и
следующий os.replace получает PermissionError. Это не ошибка модели и не повод
терять 2000-шаговый прогон, поэтому atomic_save повторяет замену. Тест
фиксирует оба конца контракта: транзиентная ошибка переживается, постоянная —
поднимается, а tmp-файл в обоих случаях не остаётся мусором.
"""

import os
import tempfile
import unittest
from unittest import mock

import train
from train import atomic_save


class TestAtomicSaveRetry(unittest.TestCase):
    def test_transient_permission_error_is_retried(self):
        real_replace = os.replace
        calls = {"n": 0}

        def flaky_replace(src, dst):
            calls["n"] += 1
            if calls["n"] < 3:
                raise PermissionError(13, "file is temporarily locked", dst)
            return real_replace(src, dst)

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "ckpt.pt")
            with mock.patch.object(train.os, "replace", side_effect=flaky_replace):
                with mock.patch.object(train.time, "sleep", return_value=None):
                    atomic_save({"value": 1}, path)

            self.assertTrue(os.path.exists(path))
            self.assertEqual(calls["n"], 3)
            leftovers = [name for name in os.listdir(tmp_dir) if name.endswith(".tmp")]
            self.assertEqual(leftovers, [])

    def test_persistent_permission_error_raises_and_cleans_tmp(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "ckpt.pt")
            with mock.patch.object(
                train.os,
                "replace",
                side_effect=PermissionError(13, "still locked", path),
            ) as replace_mock:
                with mock.patch.object(train.time, "sleep", return_value=None):
                    with self.assertRaises(PermissionError):
                        atomic_save({"value": 1}, path)

            self.assertEqual(replace_mock.call_count, train._REPLACE_RETRIES)
            self.assertFalse(os.path.exists(path))
            leftovers = [name for name in os.listdir(tmp_dir) if name.endswith(".tmp")]
            self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
