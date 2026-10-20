"""
test_journal_pairing.py — целостность журнала §13.3 (условие гейта WP4).

Гейт WP4 сформулирован не про метрики, а про дисциплину: «в journal.jsonl на
каждую start-строку есть finish-строка». Причина историческая — E02 оборвался на
первой ячейке, а журнал кончился строкой «E02 Сид 0»: старт без финиша выглядел
как завершённый эксперимент (замерено в NEG-11: 39 run_start и 0 run_finish).

Отсюда три обязанности кода, которые проверяют тесты ниже.

  1. Инструмент (wp4_report._journal_integrity) обязан честно различать «пары
     есть», «старт без финиша», «журнала нет вообще» и «прогон старше самого
     механизма пар» — иначе условие гейта проверяется на глазок.
  2. Прогоны, запущенные ДО починки, не считаются нарушителями постфактум: у
     них нет отметки emits_run_finish в run_start, и дорисовать им finish нельзя
     (§7.7). Но и «выполнено» на их основании не объявляется: требует хотя бы
     один прогон актуального поколения.
  3. Эмитент (train.py) обязан писать finish и при штатной остановке, и при
     обрыве процесса (atexit-маркер stop_reason=aborted).
"""

import json

import os

import tempfile

import unittest

# §9.2: config раньше torch (torch здесь вообще не нужен).
import config


def _write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


STAMPED = {"emits_run_finish": True}


class TestJournalIntegrityInstrument(unittest.TestCase):
    def setUp(self):
        from wp4_report import _journal_integrity

        self.probe = _journal_integrity
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _run_log(self, experiment, rows):
        _write_jsonl(os.path.join(self.dir, f"{experiment}_log.jsonl"), rows)

    def _clean_fresh_run(self, experiment="X_clean"):
        """Прогон актуального поколения с закрытой парой: базовый «зелёый» фон."""
        self._run_log(
            experiment,
            [
                dict({"event": "run_start", "experiment_id": experiment}, **STAMPED),
                {"iteration": 1, "loss": 0.5},
                {
                    "event": "run_finish",
                    "experiment_id": experiment,
                    "stop_reason": "max_steps",
                },
            ],
        )

    def test_absent_logs_are_reported_as_absent(self):
        """Пустой каталог != «всё в порядке»: инструмент обязан это различать."""
        report = self.probe(log_dir=self.dir)
        self.assertFalse(report["journal"]["present"])
        self.assertEqual(report["per_run_logs"]["files"], 0)
        self.assertEqual(report["per_run_logs"]["run_starts"], 0)
        # И тем более нельзя объявить выполненным то, что ещё не измерялось.
        self.assertEqual(report["fresh_start_rows"], 0)
        self.assertFalse(report["all_starts_paired"])

    def test_legacy_start_without_finish_is_history_not_violation(self):
        """Прогоны волн WP4 запускались кодом без finish: их пары не появляются
        задним числом (§7.7), поэтому они считаются строками старого поколения,
        а не висячими нарушениями."""
        self._run_log("X_old", [{"event": "run_start", "experiment_id": "X_old"}])
        report = self.probe(log_dir=self.dir)
        pl = report["per_run_logs"]
        self.assertEqual(pl["run_starts"], 1)
        self.assertEqual(pl["legacy_start_rows"], 1)
        self.assertEqual(pl["supported_starts"], 0)
        self.assertEqual(pl["supported_unpaired"], [])
        # Но условие гейта от этого не становится истинным.
        self.assertFalse(report["all_starts_paired"])

    def test_stamped_start_without_finish_is_violation(self):
        """Висячий start актуального поколения — ровно та дыра §13.3, из-за
        которой E02 считался завершённым экспериментом."""
        self._clean_fresh_run()
        self._run_log(
            "X_hang",
            [dict({"event": "run_start", "experiment_id": "X_hang"}, **STAMPED)],
        )
        report = self.probe(log_dir=self.dir)
        self.assertEqual(report["per_run_logs"]["supported_unpaired"], ["X_hang"])
        self.assertFalse(report["all_starts_paired"])

    def test_paired_fresh_run_counts_as_paired(self):
        self._clean_fresh_run()
        report = self.probe(log_dir=self.dir)
        pl = report["per_run_logs"]
        self.assertEqual(pl["supported_unpaired"], [])
        self.assertEqual(pl["paired"], ["X_clean"])
        self.assertEqual(report["fresh_start_rows"], 1)
        self.assertTrue(report["all_starts_paired"])

    def test_second_fresh_run_without_finish_breaks_pairing(self):
        """Лог пишется append (§7.7): второй прогон без finish обязан быть виден,
        а не «первый же finish закрыл файл»."""
        self._run_log(
            "X_twice",
            [
                dict({"event": "run_start", "experiment_id": "X_twice"}, **STAMPED),
                {"event": "run_finish", "experiment_id": "X_twice", "stop_reason": "max_steps"},
                dict({"event": "run_start", "experiment_id": "X_twice"}, **STAMPED),
            ],
        )
        report = self.probe(log_dir=self.dir)
        pl = report["per_run_logs"]
        self.assertEqual(pl["run_starts"], 2)
        self.assertEqual(pl["run_finishes"], 1)
        self.assertEqual(pl["supported_unpaired"], ["X_twice"])
        self.assertFalse(report["all_starts_paired"])

    def test_killed_attempt_before_successful_rerun_is_superseded(self):
        """Убитый извне прогон и затем перезапущенный под тем же id.

        Так выглядит Р-7 на практике: процесс сняли без SIGTERM-обработки,
        atexit-маркер «aborted» не отработал, старт остался без финиша; затем
        прогон повторили, и он закрылся. Нарушение §13.3 остаётся нарушением
        (пара обязана быть на каждый старт), но диагностика обязана показывать,
        что эмитент работает, а дыра — от способа остановки: иначе вывод
        «train.py перестал писать finish» уводит разбор в неверную сторону.
        """
        self._run_log(
            "X_killed_then_ok",
            [
                dict({"event": "run_start", "experiment_id": "X_killed_then_ok"}, **STAMPED),
                dict({"event": "run_start", "experiment_id": "X_killed_then_ok"}, **STAMPED),
                {
                    "event": "run_finish",
                    "experiment_id": "X_killed_then_ok",
                    "stop_reason": "max_steps",
                },
            ],
        )
        report = self.probe(log_dir=self.dir)
        pl = report["per_run_logs"]
        self.assertEqual(pl["supported_unpaired"], ["X_killed_then_ok"])
        self.assertEqual(pl["supported_unpaired_superseded"], ["X_killed_then_ok"])
        self.assertEqual(pl["supported_unpaired_hard"], [])
        self.assertFalse(report["all_starts_paired"])

    def test_run_without_any_finish_is_hard_violation(self):
        """Если у эксперимента нет НИ ОДНОГО финиша, это нарушение эмитента, а
        не снятый оператором процесс — различие должно быть видно в тех же
        полях."""
        self._run_log(
            "X_never_closed",
            [dict({"event": "run_start", "experiment_id": "X_never_closed"}, **STAMPED)],
        )
        pl = self.probe(log_dir=self.dir)["per_run_logs"]
        self.assertEqual(pl["supported_unpaired_hard"], ["X_never_closed"])
        self.assertEqual(pl["supported_unpaired_superseded"], [])

    def test_stop_reason_survives_from_finish_row(self):
        self._run_log(
            "X_collapse",
            [
                dict({"event": "run_start", "experiment_id": "X_collapse"}, **STAMPED),
                {
                    "event": "run_finish",
                    "experiment_id": "X_collapse",
                    "stop_reason": "collapse_fuse",
                },
            ],
        )
        report = self.probe(log_dir=self.dir)
        runs = report["per_run_logs"]
        self.assertEqual(runs["paired"], ["X_collapse"])
        # stop_reason обязан доезжать до отчёта: иначе «почему встал прогон»
        # приходится пересчитывать по чужим полям.
        self.assertEqual(runs["detail"]["X_collapse"], "collapse_fuse")

    def test_pre_fix_run_has_no_stop_reason(self):
        self._run_log("X_old", [{"event": "run_start", "experiment_id": "X_old"}])
        report = self.probe(log_dir=self.dir)
        self.assertIsNone(report["per_run_logs"]["detail"]["X_old"])

    def test_broken_tail_line_is_counted_not_fatal(self):
        """Обрыв записи оставил бы полустоку; читатель обязан её сосчитать,
        а не уронить отчёт (иначе гейт не соберётся вовсе)."""
        path = os.path.join(self.dir, "X_tail_log.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(dict({"event": "run_start", "experiment_id": "X_tail"}, **STAMPED)) + "\n")
            fh.write('{"event": "run_finish", "experiment_id": "X_tai')
        report = self.probe(log_dir=self.dir)
        self.assertEqual(report["per_run_logs"]["malformed_lines"], 1)
        self.assertEqual(report["per_run_logs"]["run_starts"], 1)
        self.assertEqual(report["per_run_logs"]["supported_unpaired"], ["X_tail"])

    def test_journal_jsonl_pairs_are_paired_by_experiment(self):
        """Единый журнал: error тоже закрывает start (оборванный прогон виден),
        а не оставляет висячий хвост."""
        _write_jsonl(
            os.path.join(self.dir, "journal.jsonl"),
            [
                dict({"event": "start", "experiment": "J_a"}, **STAMPED),
                {"event": "finish", "experiment": "J_a"},
                dict({"event": "start", "experiment": "J_b"}, **STAMPED),
                {"event": "error", "experiment": "J_b"},
            ],
        )
        report = self.probe(log_dir=self.dir)
        j = report["journal"]
        self.assertTrue(j["present"])
        self.assertEqual(j["starts"], 2)
        self.assertEqual(j["finishes"], 1)
        self.assertEqual(j["errors"], 1)
        self.assertEqual(j["supported_starts"], 2)
        self.assertEqual(j["supported_unpaired_experiments"], [])

    def test_journal_hang_is_listed(self):
        _write_jsonl(
            os.path.join(self.dir, "journal.jsonl"),
            [dict({"event": "start", "experiment": "J_hang"}, **STAMPED)],
        )
        report = self.probe(log_dir=self.dir)
        self.assertEqual(report["journal"]["supported_unpaired_experiments"], ["J_hang"])
        self.assertFalse(report["all_starts_paired"])

    def test_journal_start_without_stamp_is_not_supported(self):
        """Старая start-строка (без отметки) не создаёт «актуального поколения»:
        иначе один дописанный журнал обнулил бы историю нарушений."""
        _write_jsonl(
            os.path.join(self.dir, "journal.jsonl"),
            [{"event": "start", "experiment": "J_old"}],
        )
        report = self.probe(log_dir=self.dir)
        self.assertEqual(report["journal"]["supported_starts"], 0)
        self.assertEqual(report["journal"]["unpaired_experiments"], ["J_old"])
        self.assertFalse(report["all_starts_paired"])

    def test_manager_journal_legacy_hang_is_history_not_current_violation(self):
        """Тот самый «E02 Сид 0» из Rev.7: висячая пара обязана быть видна, но
        считаться историей (§7.7), а не нарушением на текущей версии спеки."""
        legacy = os.path.join(self.dir, "journal_manager.jsonl")
        _write_jsonl(
            legacy,
            [
                {
                    "experiment": "E01",
                    "message": "Начало: критичность",
                    "spec_version": "v5.5-EXP FINAL",
                },
                {
                    "experiment": "E01",
                    "message": "Завершено. λ=-0.0084, success=True",
                    "spec_version": "v5.5-EXP FINAL",
                },
                {
                    "experiment": "E02",
                    "message": "Начало: парная абляция стресса на 6 сидах",
                    "spec_version": "v5.5-EXP FINAL",
                },
                {
                    "experiment": "E02",
                    "message": "Сид 0: стресс включён",
                    "spec_version": "v5.5-EXP FINAL",
                },
            ],
        )
        self._clean_fresh_run()
        report = self.probe(log_dir=self.dir, manager_journal_path=legacy)
        mj = report["manager_journal"]
        self.assertEqual(mj["starts"], 2)
        self.assertEqual(mj["finishes"], 1)
        self.assertEqual([r["experiment"] for r in mj["unpaired"]], ["E02"])
        self.assertEqual(mj["unpaired_current_spec"], [])
        self.assertEqual(report["legacy_unpaired_records"], 1)
        # История сама по себе гейт не валит — валят незакрытые прогоны текущей спеки.
        self.assertTrue(report["all_starts_paired"])

    def test_manager_journal_hang_on_current_spec_breaks_gate(self):
        legacy = os.path.join(self.dir, "journal_manager.jsonl")
        _write_jsonl(
            legacy,
            [
                {
                    "experiment": "E02",
                    "message": "Начало: парная абляция",
                    "spec_version": config.SPEC_VERSION,
                }
            ],
        )
        self._clean_fresh_run()
        report = self.probe(log_dir=self.dir, manager_journal_path=legacy)
        self.assertEqual(len(report["manager_journal"]["unpaired_current_spec"]), 1)
        self.assertFalse(report["all_starts_paired"])

    def test_real_wp4_artifacts_admit_missing_finish(self):
        """Прогоны волн WP4 запускались кодом без finish — отчёт обязан признать
        и число строк старого поколения, и то, что условие ещё не выполнено."""
        if not os.path.isdir(config.LOG_DIR):
            self.skipTest("каталог логов не создан")
        report = self.probe(log_dir=config.LOG_DIR)
        pl = report["per_run_logs"]
        if pl["run_starts"] == 0:
            self.skipTest("прогонов с run_start в логах нет")
        # Инвариант честности: пока есть start-строки без отметки, они не могут
        # «исчезнуть» из отчёта — они учтены как legacy.
        self.assertGreaterEqual(pl["legacy_start_rows"], 1)
        self.assertEqual(
            pl["supported_starts"] + pl["legacy_start_rows"], pl["run_starts"]
        )
        if pl["supported_unpaired"] or report["fresh_start_rows"] == 0:
            self.assertFalse(report["all_starts_paired"])


class TestEmitterIsWired(unittest.TestCase):
    """train.py обязан эмитировать обе части пары; иначе ноль finish-записей в
    артефактах означает «журнала нет», а не «прогоны старые»."""

    def test_train_py_writes_start_finish_and_atexit_marker(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "train.py"), "r", encoding="utf-8") as fh:
            src = fh.read()
        for needle in (
            "journal.start(",
            "journal.finish(",
            '"run_finish"',
            "atexit.register(_finish_marker)",
            '"emits_run_finish"',
        ):
            self.assertIn(needle, src, f"train.py не пишет {needle!r}")

    def test_code_pairing_field_reflects_train_py(self):
        """Поле code_pairing в отчёте = факт из train.py, а не заглушка: если
        эмитент пропадёт, условие гейта §13.3 начнёт врать «журнала нет»."""
        from wp4_report import _journal_integrity

        with tempfile.TemporaryDirectory() as tmp:
            pairing = _journal_integrity(log_dir=tmp)["code_pairing"]
        self.assertEqual(
            pairing,
            {
                "journal_start": True,
                "journal_finish": True,
                "run_finish_event": True,
                "atexit_abort_marker": True,
                "run_start_stamp": True,
            },
        )


class TestGateWp4SelfCheck(unittest.TestCase):
    """Гейт WP4 сформулирован списком условий, поэтому отчёт обязан отдавать этот
    список поимённо и с числами — иначе «гейт почти пройден» печатается как
    «пройден»."""

    REQUIRED_CHECKS = {
        "primary_endpoint_coverage",
        "five_seeds",
        "effect_size_vs_baseline",
        "paired_wilcoxon",
        "journal_pairs_13_3",
    }

    @staticmethod
    def _results():
        path = os.path.join("experiments", "E02_pattern", "results.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def test_results_json_exposes_all_gate_conditions(self):
        results = self._results()
        if results is None:
            self.skipTest("results.json ещё не собран")
        checks = results["gate_wp4"]["checks"]
        self.assertEqual(set(checks), self.REQUIRED_CHECKS)
        self.assertIsInstance(results["gate_wp4"]["passed"], bool)
        # passed обязан быть конъюнкцией: если хоть одно условие ложно, passed ложь.
        self.assertEqual(
            results["gate_wp4"]["passed"], all(c["met"] for c in checks.values())
        )
        # Журнальное условие несёт фактические счётчики, а не opinion.
        j = checks["journal_pairs_13_3"]
        self.assertEqual(j["met"], results["journal_integrity"]["all_starts_paired"])
        self.assertIn("fresh_start_rows", j)
        self.assertIn("supported_unpaired", j)

    def test_conclusion_names_unmet_conditions(self):
        results = self._results()
        if results is None:
            self.skipTest("results.json ещё не собран")
        checks = results["gate_wp4"]["checks"]
        line = next((c for c in results["conclusions"] if c.startswith("Гейт WP4:")), None)
        self.assertIsNotNone(line, "в выводах нет строки про гейт WP4")
        for name, cond in checks.items():
            if not cond["met"]:
                self.assertIn(name, line)


class TestGateWp4Statistics(unittest.TestCase):
    """Статистические условия гейта WP4: их нельзя закрывать подсчётом ключей.

    «5 сидов» и «парный Уилксон» — единственные условия, которые легко
    удовлетворить формально: словарь пар заполняется и при одном сиде (тест там
    сознательно не запускается), а сида базлайн-плеча ≠ сида каждого arm'а. Тесты
    ниже фиксируют, что в гейт попадают только реально посчитанные тесты и что
    происхождение сида указано в самом отчёте.
    """

    def test_single_seed_pair_is_not_usable(self):
        from wp4_report import _paired_wilcoxon, _usable_wilcoxon_pairs

        pair = _paired_wilcoxon([0.52], [0.001])
        self.assertEqual(pair["n_pairs"], 1)
        self.assertFalse(pair["usable"])
        # Ровно это и было дырой: bool(paired) = True при одном сиде.
        self.assertEqual(_usable_wilcoxon_pairs({"H-K2_vs_H-A0_s400": pair}), {})

    def test_five_seed_pair_is_counted(self):
        from wp4_report import _paired_wilcoxon, _usable_wilcoxon_pairs

        pair = _paired_wilcoxon([0.50, 0.40, 0.30, 0.20, 0.10],
                                [0.45, 0.35, 0.25, 0.15, 0.05])
        self.assertTrue(pair["usable"])
        # Двусторонний точный минимум — 2^(1-n), а не 2^-n: на пяти парах это
        # 0.0625, то есть p<0.05 недостижим в принципе (знаковый ранговый тест,
        # два хвоста). Число попадает в артефакт и в текст отчёта, поэтому
        # проверяем его, а не только факт запуска.
        self.assertAlmostEqual(pair["min_two_sided_p"], 0.0625, places=6)
        self.assertEqual(_paired_wilcoxon([0.6] * 6, [0.1] * 6)["min_two_sided_p"], 0.03125)
        usable = _usable_wilcoxon_pairs({"H-X_vs_H-A0_s800": pair})
        self.assertEqual(list(usable), ["H-X_vs_H-A0_s800"])
        self.assertTrue("p_value" in usable["H-X_vs_H-A0_s800"]
                        or "error" in usable["H-X_vs_H-A0_s800"])

    def test_results_json_distinguishes_gate_seeds_from_arm_seeds(self):
        results = self._results_or_skip()
        five = results["gate_wp4"]["checks"]["five_seeds"]
        for key in ("n_seeds", "n_seeds_including_gate", "gate_seeds", "comment"):
            self.assertIn(key, five)
        # Число сидов аблаций не может вырасти за счёт чужого артефакта.
        self.assertEqual(
            five["n_seeds_including_gate"],
            len(set(five["gate_seeds"])
                | {r["seed"] for r in results["ablation_runs"]}),
        )
        if five["met"]:
            self.assertGreaterEqual(len(five["gate_seeds"]), 5,
                                    "гейт закрыт не сидами, а их списком в комментарии")

    def test_wilcoxon_met_matches_computed_pairs(self):
        results = self._results_or_skip()
        w = results["gate_wp4"]["checks"]["paired_wilcoxon"]
        # met смотрит на первичный эндпоинт, а не на любое посчитанное сравнение:
        # пары строятся по нескольким эндпоинтам сразу.
        self.assertEqual(
            w["met"], w["pairs_with_computed_test_on_primary"] > 0
        )
        self.assertEqual(
            w["pairs_with_computed_test_on_primary"], len(w["computed_primary_pairs"])
        )

    @staticmethod
    def _pair_run(arm, seed, steps, **fields):
        run = {"arm": arm, "seed": seed, "steps": steps}
        run.update(fields)
        return run

    def test_paired_runs_are_built_per_endpoint_and_keyed_by_field(self):
        """Пара обязана называть эндпоинт, по которому посчитана.

        Пока ряд строился только по alive_fraction_min, условие «Уилксон» гейта
        WP4 закрывалось статистикой по выживанию, хотя первичным эндпоинтом в том
        же отчёте объявлен coverage.f1. Ключ с именем поля — это единственное, что
        мешает подменить один эндпоинт другим.
        """
        from wp4_report import PAIRED_FIELDS, _build_paired_runs, _is_primary_pair

        seeds = [42, 101, 202, 303, 404]
        runs = []
        for i, seed in enumerate(seeds):
            runs.append(
                self._pair_run(
                    "H-A0", seed, 2000,
                    alive_fraction_min=0.01 + i / 100, f1_final=0.05 + i / 100,
                    f1_max=0.06, visible_mse_final=0.25,
                )
            )
            runs.append(
                self._pair_run(
                    "R-9", seed, 2000,
                    alive_fraction_min=0.40 + i / 100, f1_final=0.15 + i / 100,
                    f1_max=0.20, visible_mse_final=0.20,
                )
            )
        paired = _build_paired_runs(runs)
        self.assertEqual(
            set(paired), {f"R-9_vs_H-A0_s2000_{field}" for field in PAIRED_FIELDS}
        )
        for key, pair in paired.items():
            self.assertEqual(pair["n_pairs"], 5, key)
            self.assertTrue(pair["usable"], key)
        self.assertTrue(_is_primary_pair("R-9_vs_H-A0_s2000_f1_final"))
        self.assertFalse(_is_primary_pair("R-9_vs_H-A0_s2000_alive_fraction_min"))

    def test_missing_endpoint_value_drops_only_that_endpoint_pair(self):
        """Старые волны не записывали f1 — их пары по f1 должны отсутствовать, а
        не превращаться в нули или в молча пропущенное сравнение по выживанию."""
        from wp4_report import _build_paired_runs

        seeds = [42, 101, 202, 303, 404]
        runs = []
        for i, seed in enumerate(seeds):
            runs.append(
                self._pair_run(
                    "H-A0", seed, 400,
                    alive_fraction_min=0.01 + i / 100, f1_final=None,
                    f1_max=None, visible_mse_final=0.25,
                )
            )
            runs.append(
                self._pair_run(
                    "R-1", seed, 400,
                    alive_fraction_min=0.40 + i / 100, f1_final=None,
                    f1_max=None, visible_mse_final=0.20,
                )
            )
        paired = _build_paired_runs(runs)
        self.assertEqual(
            set(paired), {"R-1_vs_H-A0_s400_alive_fraction_min", "R-1_vs_H-A0_s400_visible_mse_final"}
        )

    def test_pair_needs_the_same_seed_on_the_baseline(self):
        """Arm без ровного ему базлайна на том же сиде и горизонте не даёт пары —
        иначе сравнение стало бы несравненным по построению."""
        from wp4_report import _build_paired_runs

        runs = [
            self._pair_run("H-A0", 42, 400, alive_fraction_min=0.01, f1_final=0.05,
                           f1_max=0.06, visible_mse_final=0.25),
            self._pair_run("R-1", 101, 400, alive_fraction_min=0.40, f1_final=0.15,
                           f1_max=0.20, visible_mse_final=0.20),
        ]
        self.assertEqual(_build_paired_runs(runs), {})

    @staticmethod
    def _results_or_skip():
        path = os.path.join("experiments", "E02_pattern", "results.json")
        if not os.path.exists(path):
            raise unittest.SkipTest("results.json ещё не собран")
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)


if __name__ == "__main__":
    unittest.main()
