#!/usr/bin/env python
"""check_agents_size.py — контракт обязан влезать в бюджет загрузки.

Зачем: AGENTS.md дважды за сутки превысил 65536 байт и был усечён при загрузке —
часть правил молча исчезла. Усечение опаснее ошибки: контракт выглядит целым.
Бюджет 60000 (запас 5 КБ), превышение — ошибка, а не предупреждение.
"""
from __future__ import annotations

import sys
from pathlib import Path

LIMIT = 60000
p = Path(__file__).resolve().parents[1] / "AGENTS.md"
size = len(p.read_text(encoding="utf-8").encode())
if size <= LIMIT:
    print(f"[agents-size] {size} байт ≤ {LIMIT} — ок")
    sys.exit(0)
print(f"[agents-size] ОШИБКА: {size} байт > {LIMIT} — контракт будет усечён при загрузке. "
      f"Вынесите подробности в docs/ и оставьте в AGENTS правило + ссылку")
sys.exit(1)
