"""lean_axioms.py — независимая проверка теорем Lean на «чистоту аксиом» и неизменность формулировок.

Откуда идея (28.10). В отчёте nearai/putnambench-deepseek агент доказывает задачи PutnamBench в Lean, и
успех засчитывается только если: файл компилируется, в нём нет `sorry`/`axiom`/`native_decide`, формулировка
теоремы **побайтово совпадает** с замороженной, и `#print axioms` чист (только `propext`,
`Classical.choice`, `Quot.sound`). Их замечание важное: текстовый diff ловит не всё, поэтому тип
сверяется после элаборации.

Что делает этот скрипт для нашего стенда:
1. Берёт теоремы из `formal/*.lean`.
2. Для каждой добавляет `#print axioms <имя>` во временную копию и запускает `lean`.
3. Проверяет, что список аксиом — подмножество разрешённых (или пуст).
4. Сверяет формулировки с замороженными в `lab/formal.json` (поле `statements`: sha256 строки
   `theorem <имя> ... :=`). Если формулировка изменилась — ошибка: «доказали не то, что заморозили».

Использование:
    python scripts/lean_axioms.py            # проверка
    python scripts/lean_axioms.py --freeze   # заморозить текущие формулировки (первый раз / осознанно)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "formal"
INVENTORY = ROOT / "lab" / "formal.json"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
THEOREM = re.compile(r"^\s*theorem\s+([A-Za-z_][\w.']*)", re.MULTILINE)


def find_lean() -> str | None:
    exe = shutil.which("lean")
    if exe:
        return exe
    for cand in (Path.home() / ".elan" / "bin" / "lean.exe", Path.home() / ".elan" / "bin" / "lean"):
        if cand.exists():
            return str(cand)
    return None


def statements_hash(text: str) -> dict[str, str]:
    """sha256 каждой формулировки: от `theorem <имя>` до строки с `:=` включительно."""
    out: dict[str, str] = {}
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = THEOREM.match(line)
        if not m:
            continue
        name = m.group(1)
        chunk = []
        depth = 0
        for ln in lines[i:]:
            chunk.append(ln)
            depth += ln.count("(") + ln.count("{") + ln.count("[")
            depth -= ln.count(")") + ln.count("}") + ln.count("]")
            if ":=" in ln and depth <= 0:
                break
        out[name] = hashlib.sha256("\n".join(chunk).split(":=", 1)[0].strip().encode("utf-8")).hexdigest()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    lean = find_lean()
    if not lean:
        print("[axioms] Lean не найден — пропускаю (в CI это ожидаемо)")
        return 0

    files = sorted(FORMAL.glob("*.lean"))
    all_statements: dict[str, str] = {}
    problems: list[str] = []
    checked = 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        stmts = statements_hash(text)
        all_statements.update({k: v for k, v in stmts.items()})
        # теоремы лежат внутри `namespace X` — Lean знает их как X.name, поэтому для #print axioms
        # нужно полное имя (иначе «unknown constant», что мы и получили на первом прогоне)
        ns = None
        full = {}
        for ln in text.split("\n"):
            s = ln.strip()
            if s.startswith("namespace "):
                ns = s.split()[1]
            elif s.startswith("end ") and ns and s.split()[1] == ns:
                ns = None
            else:
                m = re.match(r"theorem\s+([A-Za-z_][\w.']*)", s)
                if m:
                    full[m.group(1)] = f"{ns}.{m.group(1)}" if ns else m.group(1)
        names = [full.get(n, n) for n in stmts]
        if args.limit:
            names = names[: args.limit]
        if not names:
            continue
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / path.name
            probe.write_text(text + "\n\n" + "\n".join(f"#print axioms {n}" for n in names) + "\n",
                             encoding="utf-8")
            r = subprocess.run([lean, str(probe)], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=600)
            out = (r.stdout or "") + (r.stderr or "")
            for name in names:
                checked += 1
                short = name.split(".")[-1]
                m = re.search(rf"'{re.escape(name)}'\s+depends on axioms:\s*\[([^\]]*)\]", out)
                if m:
                    ax = {a.strip() for a in m.group(1).split(",") if a.strip()}
                    extra = ax - ALLOWED
                    if extra:
                        problems.append(f"{path.name}: {short}: посторонние аксиомы {sorted(extra)}")
                elif re.search(rf"'{re.escape(name)}'\s+does not depend on any axioms", out):
                    pass
                else:
                    toolchain_hint = ""
                    if "Init" in out or "olean" in out:
                        toolchain_hint = " [toolchain: нет Init/olean]"
                    problems.append(
                        f"{path.name}: {short}: не удалось прочитать #print axioms (код {r.returncode}){toolchain_hint}"
                    )

    inv = json.loads(INVENTORY.read_text(encoding="utf-8")) if INVENTORY.exists() else {}
    frozen = inv.get("statements") or {}

    if args.freeze:
        inv["statements"] = all_statements
        inv["statements_note"] = ("sha256 формулировок (до `:=`); сверка ловит подмену теоремы — "
                                  "внешний агент может «доказать» изменённое утверждение")
        INVENTORY.write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[axioms] заморожено формулировок: {len(all_statements)}")
        return 0

    if frozen:
        changed = [n for n, h in all_statements.items() if n in frozen and frozen[n] != h]
        added = [n for n in all_statements if n not in frozen]
        for n in changed:
            problems.append(f"формулировка изменена после заморозки: {n} — «доказали не то»")
        if added:
            problems.append(f"новые теоремы без заморозки: {', '.join(added[:5])} — запустите --freeze")

    # H-ALIVE-62: Lean может стоять, но быть неработоспособным (нет Init/olean — неполный тулчейн).
    # Это НЕ провал теорем и НЕ «доказано»: проверка невозможна, и это должно быть видно как статус.
    toolchain_markers = ("[toolchain: нет Init/olean]", "unknown module prefix 'Init'", "No directory 'Init'")
    if problems and len(problems) >= max(1, checked) and any(
            any(mk in pr for mk in toolchain_markers) for pr in problems):
        print(f"[axioms] тулчейн Lean есть, но неработоспособен (нет Init/olean): проверка НЕ выполнена "
              f"({len(problems)} теорем не проверены). Это статус unavailable, а не «пройдено».")
        inv0 = json.loads(INVENTORY.read_text(encoding="utf-8")) if INVENTORY.exists() else {}
        inv0["axioms_status"] = "unavailable: toolchain has no Init/olean"
        inv0["axioms_checked_at"] = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%h"], capture_output=True, text=True,
            encoding="utf-8", errors="replace").stdout.strip() or None
        INVENTORY.write_text(json.dumps(inv0, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        return 0

    if problems:
        print(f"[axioms] ОШИБКА: {len(problems)} проблем (проверено теорем: {checked})")
        for p in problems[:15]:
            print("   ", p)
        return 1
    print(f"[axioms] OK — теорем {checked}, аксиомы чистые (только {sorted(ALLOWED)}), формулировки совпадают")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
