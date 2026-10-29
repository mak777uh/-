"""check_readme_commands.py — команды из README должны запускаться в CI, а не только существовать.

Откуда (30.10, входящий аудит `herness`, принцип M-1): «тесты зелёные» — это утверждение о последнем запуске
автора, а не о дереве. Ровно тот же дефект возможен с командами: README объявляет `make health`,
`python scripts/lab.py validate`, `pytest tests`, а workflow может не содержать ни одного из них — и никто не
заметит, потому что гейт «команда есть в README» не проверяет «команда есть в CI».

Правило. Для каждой команды из блока `## 9. Быстрые команды` в `AGENTS.md` (и из README, если там есть
командные блоки) проверяется: встречается ли её исполняемая часть хотя бы в одном файле `.github/workflows/*.yml`
**или** явно помечена в реестре как ручная (`lab/manual_commands.json`). Иначе — предупреждение, а не падение:
часть команд по замыслу ручная (например `make repro` требует GPU, которого в CI нет).

Использование:
    python scripts/check_readme_commands.py            # отчёт
    python scripts/check_readme_commands.py --ci       # падение при непомеченных
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "lab" / "manual_commands.json"
WORKFLOWS = ROOT / ".github" / "workflows"

CMD_RE = re.compile(r"^\s*(?:#\s*)?((?:python|make|bash|node|pytest)\s[^\n#]*)$")


def commands_from(path: Path) -> set[str]:
    """Команды из fenced-блоков и строк, начинающихся с известного исполнителя."""
    if not path.exists():
        return set()
    out: set[str] = set()
    inside = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            continue
        m = CMD_RE.match(line)
        if m:
            cmd = m.group(1).strip()
            if cmd and not cmd.startswith("#"):
                out.add(cmd)
    return out


def key_of(cmd: str) -> str:
    """Ключ для сверки: первые два слова, без путей и аргументов-значений."""
    parts = cmd.split()
    if not parts:
        return ""
    if parts[0] == "python" and len(parts) > 2:
        return " ".join(parts[:3])
    if parts[0] == "python" and len(parts) > 1:
        return " ".join(parts[:2])
    return " ".join(parts[:2])


def workflow_text() -> str:
    if not WORKFLOWS.exists():
        return ""
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(WORKFLOWS.glob("*.yml")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="команды из документации запускаются в CI")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    manual = {}
    if MANUAL.exists():
        manual = json.loads(MANUAL.read_text(encoding="utf-8")).get("manual", {})

    cmds = commands_from(ROOT / "AGENTS.md") | commands_from(ROOT / "README.md")
    wf = workflow_text()
    missing = []
    for cmd in sorted(cmds):
        k = key_of(cmd)
        if not k:
            continue
        if k in manual:
            continue
        # ищем исполняемую часть в workflows
        probe = k.replace("python ", "").replace("make ", "").strip()
        if probe and probe in wf:
            continue
        missing.append(cmd)

    print(f"[readme-commands] команд в документации: {len(cmds)}, ручных по реестру: {len(manual)}")
    if missing:
        print(f"[readme-commands] не найдены в CI и не помечены как ручные: {len(missing)}")
        for m in missing[:15]:
            print("   ", m)
    else:
        print("[readme-commands] все команды либо в CI, либо помечены как ручные")

    if args.ci and missing:
        print("[readme-commands] добавьте команду шагом в .github/workflows/*.yml или пометьте в lab/manual_commands.json")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
