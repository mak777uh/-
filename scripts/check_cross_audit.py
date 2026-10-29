"""check_cross_audit.py — аудиты обязаны быть помечены как внешние утверждения.

Откуда (29.10, крестовый аудит `herness`, находка 2): файлы в `cross-audit/` содержат числа и утверждения,
но их не читал ни один страж — `grep -rl "cross-audit" scripts/*.py` был пуст. Риск не в том, что аудит врёт,
а в том, что его числа начинают жить как наши: текст рядом с нашими артефактами читается как наш вывод.

Правило: каждый `.md` в `cross-audit/` (кроме служебных README/outgoing/method) обязан нести маркер внешнего
происхождения — либо HTML-комментарий с «внешн» / «аудит», либо явную строку с автором. Иначе страж падает.

Проверка нарочно дешёвая: смысл не в содержании, а в том, чтобы файл нельзя было положить молча.

Использование:
    python scripts/check_cross_audit.py [--ci]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "cross-audit"
SERVICE = {"README.md", "outgoing.md", "method.md"}

# «cross-audit» в заголовке не считается: это имя папки, а не пометка происхождения.
MARKERS = re.compile(r"внешн|рецензент|не наше утверждение|аудит от|external audit", re.IGNORECASE)


def offenders() -> list[str]:
    bad: list[str] = []
    if not AUDIT_DIR.exists():
        return bad
    for f in sorted(AUDIT_DIR.rglob("*.md")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith("cross-audit/outgoing/") or f.name in SERVICE:
            continue
        head = "\n".join(f.read_text(encoding="utf-8", errors="replace").splitlines()[:25])
        if not MARKERS.search(head):
            bad.append(rel)
    return bad


def resolve_commit(sha: str) -> bool:
    """Существует ли коммит в нашей истории (короткий хеш ≥7 символов)."""
    import subprocess
    r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-t", sha],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0


def provenance_warnings() -> list[str]:
    """Входящий аудит обязан называть коммит и дату; нерезолвящийся коммит — предупреждение.

    Откуда (30.10): рецензия lexspec была снята с клона месячной давности, но в шапке стоял только хеш, и
    читатель читал «в дереве» как «сейчас». Правило их же: первая строка называет коммит И его дату, а
    нерезолвящийся коммит виден до чтения.
    """
    import re
    out: list[str] = []
    if not AUDIT_DIR.exists():
        return out
    for f in sorted(AUDIT_DIR.rglob("*.md")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith("cross-audit/outgoing/") or f.name in SERVICE:
            continue
        head = "\n".join(f.read_text(encoding="utf-8", errors="replace").splitlines()[:25])
        for sha in set(re.findall(r"\b[0-9a-f]{7,40}\b", head)):
            if not resolve_commit(sha):
                out.append(f"{rel}: коммит {sha} не резолвится в нашей истории — снимок чужой или устаревший")
        if not re.search(r"\d{1,2}[.\-]\d{1,2}[.\-]\d{2,4}|дата|date", head, re.IGNORECASE):
            out.append(f"{rel}: в шапке нет даты")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="аудиты помечены как внешние")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    bad = offenders()
    warns = provenance_warnings()
    for w in warns:
        print("[cross-audit] предупреждение:", w)

    if bad:
        print(f"[cross-audit] файлов без маркера внешнего происхождения: {len(bad)}")
        for b in bad:
            print("   ", b)
        print("[cross-audit] добавьте в первые строки пометку: автор, дата, «внешнее мнение, не наше утверждение»")
        return 1
    print("[cross-audit] все аудиты помечены как внешние")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
