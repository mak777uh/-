"""E02c: перепись новых чекпоинтов R-9 и проверка H-R1/R2/R3.

Читает `checkpoints/E02c_R-9_s<steps>_seed<seed>/nca_final.pt`, гоняет
64 детерминированных старта × 2000 шагов (как E02b), затем:

1. кластеризует новые прогоны независимым Ward (`e02b.run_census`);
2. проецирует каждый финальный дескриптор на замороженные центроиды E02b
   (`class_centroids_frozen.json`) — это основной способ назвать класс;
3. сравнивает два назначения и считает H-R1/R2/R3 по заранее записанному
   критерию: `struct_2` в >=52/64 стартов и устойчивость последней четверти
   >=0.80.

Положительный контроль — R-9 seed42 (тот же код переписи, но как control,
чтобы не задавать кластеры); отрицательный — untrained-архитектура.
Ни обучения, ни изменения весов здесь нет.

Запуск:
    python e02c_census.py --seeds 0-63 --steps 2000
    python e02c_census.py --families E02c_R-9_s2000_seed142  # частичный
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import replace

import config

import numpy as np
import torch

import e02b_morphospace as e02b
from utils.logging import Journal

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.join(HERE, "experiments", "E02c_replication")
CENSUS = os.path.join(HERE, "experiments", "E02b_morphospace", "census.json")
CENTROIDS = os.path.join(
    HERE, "experiments", "E02b_morphospace", "class_centroids_frozen.json"
)
CHECKPOINT_ROOT = os.path.join(HERE, "checkpoints")
DEFAULT_OUT = os.path.join(EXP_DIR, "census_e02c.json")
SUMMARY_OUT = os.path.join(EXP_DIR, "summary_e02c.json")
FAMILY_RE = re.compile(r"^E02c_(?P<arm>[A-Za-z0-9-]+)_s(?P<steps>\d+)_seed(?P<seed>\d+)$")
STRUCT2_MIN = 52
STABILITY_MIN = 0.80
DEAD_ALIVE = 0.05


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_seeds(spec):
    out = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(chunk))
    return sorted(set(out))


def discover_specs(families=None):
    specs = []
    for name in sorted(os.listdir(CHECKPOINT_ROOT)):
        if not name.startswith("E02c_"):
            continue
        match = FAMILY_RE.match(name)
        if not match:
            continue
        if families and name not in families:
            continue
        path = os.path.join(CHECKPOINT_ROOT, name, "nca_final.pt")
        if not os.path.exists(path):
            print(f"[e02c] пропуск {name}: нет nca_final.pt")
            continue
        specs.append(
            e02b.CheckpointSpec(
                id=name,
                arm="R-9",
                family=name,
                path=path,
                seed=int(match.group("seed")),
                steps_trained=int(match.group("steps")),
                sha256=sha256_file(path),
                alive_mask_enabled=True,
                overrides={},
                overrides_source="e02c_plan:ARMS[R-9]",
                kind="final",
                note="E02c replication",
            )
        )
    if not specs:
        raise SystemExit("[e02c] не найдено ни одного E02c-чекпоинта")

    # Положительный контроль: тот же код, но как control (не задаёт кластеры).
    control = e02b.load_checkpoint_specs(
        families=["WP4_R-9_s2000_seed42"], include_untrained=False
    )[0]
    specs.append(replace(control, arm="H-P1", note="positive control R-9 seed42"))

    specs.append(
        e02b.CheckpointSpec(
            id="untrained_current_arch",
            arm="untrained",
            family="untrained_current_arch",
            path=None,
            seed=42,
            steps_trained=0,
            sha256=None,
            alive_mask_enabled=True,
            overrides={},
            overrides_source="runtime",
            kind="runtime",
            note="untrained architecture control",
        )
    )
    return specs


def project_frozen(runs):
    data = json.load(open(CENTROIDS, encoding="utf-8"))
    mean = np.asarray(data["scaler_mean"], dtype=np.float64)
    std = np.asarray(data["scaler_std"], dtype=np.float64)
    centroids = np.asarray(data["centroids_z"], dtype=np.float64)
    valid = [int(x) for x in data["labels_valid"]]
    names = [str(x) for x in data["class_names"]]
    by_label = {label: names[i] for i, label in enumerate(valid)}
    for run in runs:
        x = e02b.descriptor_vector(run["final"]).reshape(1, -1)
        label = int(e02b.assign_to_clusters(x, mean, std, centroids, valid)[0])
        run["frozen_label"] = label
        run["frozen_class"] = by_label.get(label, "outlier")
    return data


def family_stats(runs, family):
    rows = [r for r in runs if r["family"] == family]
    n = len(rows)
    s2 = [r for r in rows if r.get("frozen_class") == "struct_2" and r["final"]["alive_fraction"] >= DEAD_ALIVE]
    stable = [r for r in s2 if float(r.get("stability_last_quarter") or 0.0) >= STABILITY_MIN]
    counts = {}
    for r in rows:
        key = r.get("frozen_class", "outlier")
        counts[key] = counts.get(key, 0) + 1
    return {
        "family": family,
        "n": n,
        "struct_2": len(s2),
        "struct_2_fraction": round(len(s2) / n, 4) if n else 0.0,
        "struct_2_stable": len(stable),
        "struct_2_stable_fraction": round(len(stable) / n, 4) if n else 0.0,
        "frozen_class_counts": counts,
        "ward_class_counts": {
            c: sum(1 for r in rows if r.get("class_name") == c)
            for c in sorted({str(r.get("class_name")) for r in rows})
        },
    }



def journal_label(args):
    """Имя эксперимента для журнала: E02c_census_<вариант>.

    Вариант берётся из имени файла сводки (`summary_e02c_seed42repro.json` ->
    `e02c_seed42repro`), чтобы частичная перепись не смешивалась с полной.
    """
    base = os.path.basename(args.summary_out)
    stem = base
    if base.startswith("summary_") and base.endswith(".json"):
        stem = base[len("summary_"):-len(".json")]
    elif base.endswith(".json"):
        stem = base[:-len(".json")]
    return "E02c_census_" + stem


def census_verdict(supported, n_families):
    """Вердикт E02c применим только к полному дизайну из трёх новых семейств.

    При фильтре `--families` (например, повтор одного seed42) «одно
    подтверждённое семейство из одного» — это не H-R2, а частичная перепись:
    вердикт не применяется, читать надо `stats`. Иначе артефакт, честный по
    числам, получает ложную метку гипотезы.
    """
    if n_families < 3:
        return "n/a_partial_census", False
    if len(supported) >= 2:
        return "H-R1_confirmed_struct2_is_recipe_property", True
    if len(supported) == 1:
        return "H-R2_confirmed_struct2_is_rare_but_reproducible", True
    return "H-R3_confirmed_struct2_not_reproduced", True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", default="0-63")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--every", type=int, default=50)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--families", default="", help="фильтр E02c_* через запятую")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument(
        "--summary-out",
        default=SUMMARY_OUT,
        help=(
            "куда писать сводку; по умолчанию общая сводка E02c. Отдельный путь "
            "нужен для прогонов по одному семейству (например, повтор seed42), "
            "чтобы не перезаписать артефакт закрытой серии"
        ),
    )
    args = ap.parse_args(argv)

    seeds = parse_seeds(args.seeds)
    families = [x.strip() for x in args.families.split(",") if x.strip()]
    specs = discover_specs(families or None)
    device = e02b._device_from_arg(args.device)
    print(
        f"[e02c] families={[s.family for s in specs]} seeds={len(seeds)} "
        f"steps={args.steps} every={args.every} device={device}"
    )
    journal = Journal(experiment=journal_label(args))
    started = time.time()
    journal.start(
        seeds=len(seeds),
        steps=args.steps,
        every=args.every,
        families=[s.family for s in specs],
        device=str(device),
        emits_run_finish=True,
        runner="e02c_census.py",
        out=args.out,
    )
    try:
        result = _census(args, seeds, specs, device)
    except BaseException as exc:  # start без finish = оборванный прогон (AGENTS §6)
        journal.error(exc, wall_seconds=round(time.time() - started, 1))
        raise
    journal.finish(
        stop_reason="finished",
        wall_seconds=round(time.time() - started, 1),
        n_runs=result["n_runs"],
        verdict=result["verdict"],
        families=result["families"],
        census=result["census"],
        summary=result["summary"],
    )
    return 0


def _census(args, seeds, specs, device):
    """Тело переписи: артефакты, сводка и вердикт — без журнала.

    Журнал пишет обёртка в `main`: пара start/finish обязательна (§6), а
    перепись может упасть на CUDA/OOM, поэтому error-строка тоже нужна.
    """
    # E02c — отдельная серия: 3 новых файла + положительный контроль, а не
    # 12 канонических E02b. Поэтому требование «12 файлов» снимаем, но sha256
    # и диск проверяем тем же _preflight.
    e02b._preflight(
        [s for s in specs if s.path], full_protocol=True, allow_missing=True
    )
    started = time.time()
    payload, clustering = e02b.run_census(
        specs, seeds, args.steps, args.every, device, pilot=False
    )
    payload["experiment"] = "E02c_replication"
    payload["protocol"] = "reports/2026-10-21-e02c-plan.md"
    payload["protocol_sha256"] = (
        "66b77b5e31b7c231c4bd0775ff2ae297360b33d9f2c95765ef4aedbfd219b2cc"
    )
    payload["census_source"] = {
        "path": CENSUS,
        "sha256": sha256_file(CENSUS),
    }
    frozen = project_frozen(payload["runs"])
    payload["frozen_centroids"] = {
        "path": CENTROIDS,
        "sha256": sha256_file(CENTROIDS),
        "k": frozen["k"],
        "class_names": frozen["class_names"],
    }
    payload["wall_seconds"] = round(time.time() - started, 1)

    new_families = [s.family for s in specs if s.arm == "R-9"]
    stats = {fam: family_stats(payload["runs"], fam) for fam in new_families}
    supported = [fam for fam, st in stats.items() if st["struct_2"] >= STRUCT2_MIN and st["struct_2_stable_fraction"] >= STABILITY_MIN]
    controls = {
        s.family: family_stats(payload["runs"], s.family)[
            "frozen_class_counts"
        ]
        for s in specs
        if s.arm in ("H-P1", "untrained")
    }
    verdict, verdict_applicable = census_verdict(supported, len(new_families))
    summary = {
        "schema_version": 1,
        "experiment": "E02c_replication",
        "protocol_sha256": payload["protocol_sha256"],
        "seeds": seeds,
        "steps": args.steps,
        "families": new_families,
        "stats": stats,
        "controls": controls,
        "verdict": verdict,
        "verdict_applicable": verdict_applicable,
        "verdict_note": None
        if verdict_applicable
        else (
            f"перепись покрывает {len(new_families)} семейств(а) из трёх по протоколу: "
            "вердикт H-R1/H-R2/H-R3 не применяется, читать stats"
        ),
        "supported_families": supported,
        "criterion": {
            "struct_2_min": STRUCT2_MIN,
            "stability_min": STABILITY_MIN,
            "n_seeds": len(seeds),
        },
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    os.makedirs(EXP_DIR, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    with open(args.summary_out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"[e02c] census: {args.out} ({os.path.getsize(args.out)/1e6:.1f} MB)")
    print(f"[e02c] summary: {args.summary_out}")
    if verdict_applicable:
        print(f"[e02c] verdict: {verdict}; supported={supported}")
    else:
        print(
            f"[e02c] verdict: n/a (частичная перепись, семейств {len(new_families)}); "
            f"supported={supported}"
        )
    for fam, st in stats.items():
        print(
            f"[e02c] {fam}: struct_2 {st['struct_2']}/{st['n']} "
            f"(stable {st['struct_2_stable']}), {st['frozen_class_counts']}"
        )
    print(f"[e02c] controls: {controls}")
    return {
        "n_runs": len(payload["runs"]),
        "verdict": verdict,
        "families": new_families,
        "census": args.out,
        "summary": args.summary_out,
    }


if __name__ == "__main__":
    raise SystemExit(main())
