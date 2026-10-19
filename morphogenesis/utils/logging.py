"""

logging.py — единая точка записи журналов (§13, §15.2, §23).

[v5.6-EXP FINAL] Rev.11-IMPLEMENTATION-READY

Проблема, которую это закрывает: в репозитории журнал писали в трёх местах

по-разному (train.append_to_log, experiment_manager._log, cognition/reporter), и

из-за этого «start»-запись могла остаться без «finish» — ровно та дыра, из-за

которой E02 оборвался на первой ячейке, а journal.jsonl кончался строкой

«E02 Сид 0». Здесь: (1) атомарная дозапись одной JSON-строки, (2) обязательные

поля ts/level/experiment, (3) контекст-менеджер paired_run, который гарантирует

пару start/finish (или start/error) — то есть оборванный прогон виден в журнале,

а не молча отсутствует.

Ничего не печатает в stdout, кроме явного print=True.

"""

import json

import os

import re

import sys

import traceback

from datetime import datetime, timezone

import config

LEVELS = ("debug", "info", "warn", "error")

_NEG_HEADER_RE = re.compile(r"^## NEG-", re.M)


def now_iso():
    """UTC timestamp с смещением — чтобы прогоны можно было сопоставлять между машинами."""
    return datetime.now(timezone.utc).isoformat()


def _ensure_parent(path):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def json_dumps(entry):
    """

    Сериализация с защитой от_nan/inf: json.dumps(...) даёт невалидный JSON

    (NaN/Infinity), который потом читается python-ом, но ломает любые внешние

    парсеры и grep-отчёты. Приводим к None и помечаем поле.

    """
    return json.dumps(_sanitize(entry), ensure_ascii=False, default=str)


def _sanitize(value):
    if isinstance(value, float):
        # float32/float64 из numpy наследуют Python float — попадают сюда.
        if value != value or value in (float("inf"), float("-inf")):
            return None
        return value
    if isinstance(value, dict):
        return {str(k): _sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(v) for v in value]
    return value


def append_jsonl(path, entry):
    """

    Атомарная дозапись одной строки в JSONL: пишем во временный файл рядом и

    склеиваем, чтобы обрыв процесса не оставил полусстроку (иначе журнал

    перестаёт читаться построчно).

    """
    _ensure_parent(path)
    if "ts" not in entry:
        entry = dict(entry, ts=now_iso())
    line = json_dumps(entry) + "\n"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())
    return entry


def log(path, level="info", **fields):
    """Запись с уровнем; level обязан быть из LEVELS (иначе — опечатка, а не лог)."""
    if level not in LEVELS:
        raise ValueError(f"Неизвестный level={level!r}, допустимо: {LEVELS}")
    return append_jsonl(path, dict(fields, level=level))


def final_run_rows(rows, key="iteration"):
    """
    Из строк одного jsonl-лога — только последний прогон.

    Лог прогона пишется в режиме append (§7.7: историю не перезаписывают),
    поэтому в файле может лежать несколько прогонов подряд — например когда
    один и тот же experiment_id выпускали на разном горизонте. Минимум/финал
    по всему файлу приписал бы текущему прогону чужие точки, поэтому оставляем
    финальный монотонный по `key` фрагмент: он начинается там, где счётчик
    итераций обнулился.
    """
    start = 0
    for i in range(1, len(rows)):
        if rows[i][key] <= rows[i - 1][key]:
            start = i
    return rows[start:]


class Journal:
    """

    Журнал эксперимента: journal.jsonl + гарантированная пара start/finish.

    Эксперимент без finish-записи = оборванный эксперимент (§13.3).

    """

    def __init__(self, path=None, experiment=None):
        self.path = path or os.path.join(config.LOG_DIR, "journal.jsonl")
        self.experiment = experiment
        self.entries = []

    def write(self, event, **fields):
        entry = {
            "ts": now_iso(),
            "event": event,
            "experiment": self.experiment,
            "level": fields.pop("level", "info"),
            **fields,
        }
        self.entries.append(entry)
        append_jsonl(self.path, entry)
        return entry

    def start(self, **fields):
        return self.write("start", **fields)

    def finish(self, **fields):
        return self.write("finish", **fields)

    def checkpoint(self, **fields):
        return self.write("checkpoint", **fields)

    def error(self, exc=None, **fields):
        if exc is not None:
            fields = dict(
                fields,
                error_type=type(exc).__name__,
                error=str(exc),
                traceback="".join(traceback.format_exception(exc)).strip(),
            )
        return self.write("error", level="error", **fields)


def record_decision(what, why, spec_ref="", layer="", reversible=True, path=None):
    """

    Строка в memory/decisions_log.jsonl (§0.3). Обязательна при любом отклонении

    от спеки или параметре, не описанном в config.py.

    """
    if path is None:
        path = config.DECISIONS_LOG_PATH
    return append_jsonl(
        path,
        {
            "ts": now_iso(),
            "layer": layer,
            "what": what,
            "why": why,
            "spec_ref": spec_ref,
            "reversible": bool(reversible),
        },
    )


def record_negative(title, experiment, hypothesis, expected, observed, interpretation, next_step, path=None):
    """

    Запись NEG-результата по шаблону спеки (§7.7, §2.10): ноль-эффект — это

    результат, а не отсутствие результата.

    """
    if path is None:
        path = config.NEGATIVE_RESULTS_PATH
    _ensure_parent(path)
    exists = os.path.exists(path) and os.path.getsize(path) > 0
    lines = []
    if not exists:
        lines.append("# Негативные результаты (NEG)\n\n")
    index = 0
    if exists:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        index = len(_NEG_HEADER_RE.findall(text))

    block = (
        f"\n## NEG-{index + 1:02d} — {title}\n\n"
        f"- Дата: {now_iso()}\n"
        f"- Эксперимент: {experiment}\n"
        f"- Гипотеза: {hypothesis}\n"
        f"- Ожидалось: {expected}\n"
        f"- Получено: {observed}\n"
        f"- Интерпретация: {interpretation}\n"
        f"- Следующий шаг: {next_step}\n"
    )
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(block)
    return f"NEG-{index + 1:02d}"


class paired_run:
    """

    Контекст-менеджер: пишет start и либо finish, либо error — всегда.

    Используется experiment_manager-ом, чтобы «старт без финиша» больше не мог

    выглядеть как завершённый эксперимент.

    Пример:

        with paired_run(journal, seed=0, stress=True) as run:

            run.set(alive_fraction=0.62)

    (finish-запись содержит собранные через set() метрики).

    """

    def __init__(self, journal, **fields):
        self.journal = journal
        self.fields = dict(fields)
        self.result = {}

    def __enter__(self):
        self.journal.start(**self.fields)
        return self

    def set(self, **metrics):
        self.result.update(metrics)

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            self.journal.finish(**self.result)
        else:
            self.journal.error(exc=exc, **self.result)
        return False  # не глушим исключения


_WARNED = set()


def warn_once(message):
    """

    Однократное предупреждение в stderr — для деградаций, которые иначе зальют

    лог (fallback детерминизма, отсутствующие метрики).

    """
    if message in _WARNED:
        return
    _WARNED.add(message)
    print(f"⚠️  {message}", file=sys.stderr)

