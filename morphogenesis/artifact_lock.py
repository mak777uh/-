"""artifact_lock.py — замок на артефакт, а не на имя прогона.

Зачем: 22.10.2026 две обёртки запустили одну и ту же перепись одновременно.
У `lab.py` замок ключуется именем эксперимента, поэтому `--experiment
E02c_seeddec_census_wave2` и `--experiment E02c_seeddec_census_wave2_run`
получили **разные** замки и не увидели друг друга. Оба процесса писали одни
и те же `--out`/`--summary-out`; один из них убили как дубль, вместе с ним
(общий pipe stdout у раннера) умер и рабочий — 55 минут GPU без артефакта.

Здесь замок ключуется путём результата (`<artifact>.lock` рядом с файлом),
поэтому ловится любой способ запуска: через `lab.py run`, напрямую, из
скрипта или из ноутбука. Замок висит на pid: чужой живой pid — отказ,
мёртвый pid — замок считается брошенным и забирается.

Использование:
    with artifact_guard(args.out, args.summary_out):
        ...
"""
from __future__ import annotations

import contextlib
import json
import os
import time


def _pid_alive(pid: int) -> bool:
    """Живой ли процесс. На Windows `os.kill(pid, 0)` не годится.

    `os.kill(pid, 0)` на Windows не проверяет, а завершает процесс (и при
    отсутствии прав бросает PermissionError) — так выглядели ложные «мёртвые
    pid» в часовом мониторе. Здесь используется Win32: OpenProcess +
    GetExitCodeProcess == STILL_ACTIVE.
    """
    pid = int(pid)
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    import ctypes
    from ctypes import wintypes

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    try:
        code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


def _read_holder(lock_path: str) -> dict:
    try:
        with open(lock_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


@contextlib.contextmanager
def artifact_guard(*artifacts: str | os.PathLike | None):
    """Взять замки на пути артефактов; на живого держателя — SystemExit.

    Пустые аргументы игнорируются. Замки снимаются в любом случае, кроме
    жёсткого убийства процесса — тогда их забирает следующий запуск (pid мёртв).
    """
    held: list[str] = []
    try:
        for artifact in artifacts:
            if not artifact:
                continue
            target = os.path.abspath(str(artifact))
            lock = target + ".lock"
            parent = os.path.dirname(lock)
            if parent:
                os.makedirs(parent, exist_ok=True)
            payload = {
                "pid": os.getpid(),
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "artifact": target,
                "argv": " ".join(os.sys.argv[1:]),
            }
            for attempt in (0, 1):
                try:
                    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                except FileExistsError:
                    holder = _read_holder(lock)
                    pid = int(holder.get("pid") or 0)
                    if pid and pid != os.getpid() and _pid_alive(pid):
                        raise SystemExit(
                            f"[lock] отказ: {target} уже пишет процесс pid={pid} "
                            f"(старт {holder.get('started_at')}, argv={holder.get('argv')}). "
                            "Дождись его завершения или останови его явно."
                        )
                    # Брошенный (мёртвый pid) или битый замок — забираем.
                    try:
                        os.unlink(lock)
                    except OSError:
                        pass
                    if attempt == 1:
                        raise SystemExit(f"[lock] не удалось забрать замок {lock}")
                    continue
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    json.dump(payload, fh, ensure_ascii=False)
                held.append(lock)
                break
        yield held
    finally:
        for lock in held:
            try:
                os.unlink(lock)
            except OSError:
                pass
