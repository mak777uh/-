"""corpus_manifest.py — манифест корпуса: что в нём, зачем и насколько прочитано.

Зачем. Полные тексты без метаданных превращаются в свалку: через неделю нельзя сказать, что это за работа, зачем она
здесь и читали ли её. Манифест отвечает на эти три вопроса и держит статус чтения отдельно от наличия файла —
потому что «файл скачан» и «работа прочитана» это разные вещи, и путать их мы себе больше не позволяем.

Запуск:
    python scripts/corpus_manifest.py --check     # сверить манифест с файлами корпуса
    python scripts/corpus_manifest.py --write     # пересобрать список файлов в манифесте
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "library" / "corpus"
TEXTS = CORPUS / "texts"
MANIFEST = CORPUS / "manifest.json"

# Метаданные ведём руками: DOI, год, зачем в корпусе, статус чтения.
# Статусы: read (полный текст прочитан), partial (аннотация + ключевые разделы), unread (скачан, не читался).
KNOWN = {
    "davis_bongard_2022_stepsize": {
        "doi": "10.1162/isal_a_00526", "year": 2022, "status": "read",
        "why": "шаг интегрирования в непрерывных CA: меньшее dt не точнее; прямой аналог нашего X56",
    },
    "davis_2024_alenia": {
        "doi": "10.1162/isal_a_00786", "year": 2024, "status": "read",
        "why": "контрпример к «исправлению» 2023 года: не-платоновость остаётся без clipping",
    },
    "davis_2023_nonplatonic": {
        "doi": "10.54854/imi2023.01", "year": 2023, "status": "read",
        "why": "формальное определение non-Platonic; разрешение в U-Skate задаётся как 1/dx² при диффузии (§10dx)",
    },
    "kojima_ikegami_2023_lenia": {
        "doi": "10.1162/isal_a_00638", "year": 2023, "status": "partial",
        "why": "асимптотическая Lenia не зависит от тика времени; конструктивный ответ — схема с пределом",
    },
    "pilat_2012_rounding": {
        "doi": "10.1007/s10015-012-0038-0", "year": 2012, "status": "read",
        "why": "округление протекает в фитнес; remedies: одинаковая стартовая позиция, дизайн фитнеса",
    },
    "huberman_glance_1993": {
        "doi": "10.1073/pnas.90.16.7716", "year": 1993, "status": "read",
        "why": "кооперация исчезает при асинхронном обновлении: гранулярность как источник результата",
    },
    "nowak_1994_spatial_games": {
        "doi": "10.1073/pnas.91.11.4877", "year": 1994, "status": "read",
        "why": "ответ, который СУЗИЛ утверждение, а не отменил: образец честного разбора частичного артефакта",
    },
    "woolley_2022_boundaries": {
        "doi": "10.1007/s11538-022-01055-x", "year": 2022, "status": "partial",
        "why": "граничные условия дают другую бифуркационную структуру: границы — это модель, а не точность",
    },
    "taylor_2014_alife_review": {
        "doi": "10.3389/frobt.2014.00008", "year": 2014, "status": "partial",
        "why": "обзор ALife: у поля нет собственной традиции V&V",
    },
    "wilson_2014_best_practices": {
        "doi": "10.1371/journal.pbio.1001745", "year": 2014, "status": "partial",
        "why": "практики научных вычислений: тесты, ревью, версии — дешёвая часть V&V",
    },
    "sandve_2013_ten_rules": {
        "doi": "10.1371/journal.pcbi.1003285", "year": 2013, "status": "partial",
        "why": "десять правил воспроизводимости; мы следуем большинству случайно, а не по правилу",
    },
    "mitchell_1993_edge_of_chaos": {
        "doi": "10.48550/arxiv.adap-org/9303003", "year": 1993, "status": "partial",
        "why": "перепроверка знаменитого результата с лучшей статистикой — образец того, как это делается",
    },
}


def build() -> dict:
    files = sorted(p.stem for p in TEXTS.glob("*.txt")) if TEXTS.is_dir() else []
    docs = {}
    for name in files:
        meta = dict(KNOWN.get(name, {}))
        meta.setdefault("doi", None)
        meta.setdefault("year", None)
        meta.setdefault("status", "unread")
        meta.setdefault("why", "не описано — добавить в KNOWN")
        meta["file"] = f"library/corpus/texts/{name}.txt"
        docs[name] = meta
    missing_from_corpus = sorted(set(KNOWN) - set(files))
    return {
        "kind": "corpus_manifest",
        "purpose": ("полные тексты, по которым ведётся поиск; статус чтения отделён от наличия файла"),
        "documents": docs,
        "counts": {
            "documents": len(docs),
            "read": sum(1 for d in docs.values() if d["status"] == "read"),
            "partial": sum(1 for d in docs.values() if d["status"] == "partial"),
            "unread": sum(1 for d in docs.values() if d["status"] == "unread"),
        },
        "known_but_absent": missing_from_corpus,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="манифест корпуса")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    c = data["counts"]
    print("корпус: документов %d | прочитано %d | частично %d | не читано %d" % (
        c["documents"], c["read"], c["partial"], c["unread"]))
    for name, d in data["documents"].items():
        print("  %-32s %-6s %-9s %s" % (name, d["year"] or "—", d["status"], (d["doi"] or "—")))
    if data["known_but_absent"]:
        print("  описаны, но файла нет:", ", ".join(data["known_but_absent"]))
    if args.write:
        MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[corpus] манифест записан: {MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
