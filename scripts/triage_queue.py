"""Триаж очереди: оставить работающее, остальное — в пул с условием возврата.

Почему. 31.10 в `lab/queue.json` было 64 планируемых пункта, и **ни один** из них не брали ни разу
(`claimed_at` пуст у всех). Часть — от закрытых линий (NCA-обучение, петля с железом, W2-bud), часть устарела
(перекрыта сделанными опытами). Очередь, которую никто не начинает, хуже отсутствия очереди: она выглядит планом.

Правило разбора: в очереди остаётся то, что относится к **текущей линии** и может быть начато в пределах недели;
остальное уходит в `lab/pool.json` со **условием возврата** (как требует контракт), ничего не удаляется.

Запуск (сухой прогон по умолчанию):
    python scripts/triage_queue.py
    python scripts/triage_queue.py --write
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "lab" / "queue.json"
POOL = ROOT / "lab" / "pool.json"

# Остаются в очереди: текущая линия (поле, пруд, утверждения, инфраструктура чисел)
KEEP = {
    "X53_pond_omission": "следующий опыт линии: пропущенное событие в пруду",
    "X54_checkpoint_manifest_gap": "ждёт решения владельца по каноническим весам",
    "X52_spatial_optimum": "механизм удержания вариации — следующая линия",
    "X28_factorial_F": "наш собственный долг: фрагментация против неоднородности",
    "X31_equivalence_tests": "60 сидов: закрыть ослабленные утверждения",
    "X35_restore_claim_artifacts": "провенанс: вернуть артефакты строкам CLAIMS",
    "X3_claims_expect_column": "инфраструктура чисел: колонка ожидаемого значения",
    "X29_eas_flow_lenia": "Q1: прибор активности есть, измерение не сделано",
    "X38_transplant_replication": "мощность для утверждения о переносе формы",
    "X30_env_without_constructors": "решающий опыт наследования: среда без конструкторов",
    "E6_field_confirm": "подтверждение критерия поля на новых параметрах",
    "X7_dose_confirmation": "подтверждение дозы неоднородности",
}

# Перекрыты сделанными опытами
SUPERSEDED = {
    "X24_durable_metric": "сделано: X23 ввёл метрику времён жизни, §10dc",
    "X25_recheck_claim": "сделано: §10cw перепроверен метрикой долгоживущих структур",
    "X21_pattern_vs_globalnoise": "сделано: 30 сидов, +1.86 CI [0.43; 3.93], §10dh",
    "X20_amp02_more_seeds": "сделано: амплитуда 0.2 проверена, §10di",
    "X6a_board_text": "доска: замечания разобраны библиотекарем, X6b/X6c остаются",
}

# В пул: линии закрыты или отложены, с условием возврата
POOL_RULES = [
    (("E02c_", "E02d_", "night_repro"), "NCA-линия закрыта решением владельца",
     "если владелец откроет линию NCA заново"),
    (("H6", "H7", "E5", "V1", "V2", "V3", "V5", "V9", "K1", "K2", "K3", "P1", "P2", "P5", "B2b"),
     "линия петли с железом и наследования среды заморожена (WP5 закрыт)",
     "если WP5 будет открыт или появится внешний сигнал, которого у нас нет"),
    (("W2bud_",), "W2-bud закрыт: воспроизведение и метрики проверены",
     "если результат W2-bud будет оспорен извне"),
    (("E11", "E14", "X13_board", "X6b_board", "X6c_board"),
     "замечания доски по экспериментам и инвазии: не текущая линия",
     "когда доска станет текущей работой"),
    (("conditions_measure", "metrics_library_common"),
     "инфраструктурные идеи общего масштаба",
     "когда появится второй мир, для которого мера должна быть общей"),
]


def classify(item_id: str) -> tuple[str, str, str]:
    if item_id in KEEP:
        return "keep", "", KEEP[item_id]
    if item_id in SUPERSEDED:
        return "superseded", "", SUPERSEDED[item_id]
    for prefixes, why, trigger in POOL_RULES:
        if any(item_id.startswith(p) for p in prefixes):
            return "pool", why, trigger
    return "keep", "", "не подошёл ни под одно правило — оставлен, разобрать вручную"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="триаж очереди")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    pool = json.loads(POOL.read_text(encoding="utf-8")) if POOL.is_file() else {"items": []}
    have = {i.get("id") for i in pool.get("items", [])}

    keep, pooled, sup, manual = [], [], [], []
    # ВАЖНО: итерация по копии — иначе remove() во время цикла пропускает элементы
    for item in list(q["items"]):
        if item.get("status") != "planned":
            continue
        decision, why, note = classify(item["id"])
        if decision == "keep":
            keep.append(item["id"])
            if note.startswith("не подошёл"):
                manual.append(item["id"])
        elif decision == "superseded":
            item["status"] = "superseded"
            item["note"] = (item.get("note") or "") + f" | ПЕРЕКРЫТО: {note}"
            sup.append(item["id"])
        else:
            q["items"].remove(item)
            if item["id"] not in have:
                pool.setdefault("items", []).append({
                    "id": item["id"], "title": item.get("title"), "status": "deferred",
                    "why": why, "trigger": note,
                    "from": "lab/queue.json", "moved_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                })
            pooled.append(item["id"])

    print(f"осталось в очереди: {len(keep)}")
    print(f"перекрыто: {len(sup)} -> {', '.join(sup) if sup else '—'}")
    print(f"в пул: {len(pooled)}")
    if manual:
        print("разобрать вручную:", ", ".join(manual))

    if args.write:
        q["items"].sort(key=lambda i: (i.get("status") != "running", i.get("status") != "planned"))
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        pool["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        POOL.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("записано: lab/queue.json, lab/pool.json")
    else:
        print("(сухой прогон; добавьте --write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
