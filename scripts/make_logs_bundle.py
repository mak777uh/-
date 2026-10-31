"""make_logs_bundle.py — собрать «логи вместе со статьёй» в один проверяемый архив.

Зачем. Владелец спросил: не пора ли написать статью и залить логи вместе с ней. Статья есть
(`articles/002-field-line/`), но «залить логи» должно значить **воспроизводимый пакет**, а не папку
файлов: внешний читатель должен получить архив, распаковать и увидеть, что каждый файл совпадает с
записанным хешем, а числа статьи пересчитываются из содержимого.

Что попадает в пакет:
  * `journal.jsonl` — канонический журнал (append-only, источник истины о прогонах);
  * `lab/runs/*.json` — манифесты прогонов;
  * агрегаты и утверждения линии поля (`l1_field_matrix.json`, `lab/claims/*.json`);
  * артефакты линии поля (`morphogenesis/experiments/L1_field/*.json`);
  * статья и ключевые разделы (`articles/002-field-line/README.md`, `docs/world-design.md`);
  * `MANIFEST.json` — путь, размер, sha256 каждого файла + сводный хеш содержимого.

Использование:
    python scripts/make_logs_bundle.py --out ../_exports/logs-2026-10-31.zip
    python scripts/make_logs_bundle.py --verify ../_exports/logs-2026-10-31.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUNDLE_README = """# Пакет данных к статье «Поле без заданных объектов» (v1.4)

Файлов: {count}, распакованный объём: {mib:.1f} МиБ, сводный sha256 содержимого: `{sha}`.

## Что внутри

- `articles/028-pole-bez-zadannyh-obektov.md` — статья;
- `reports/2026-10-31-publication-package.md` — инструкция по публикации и вычитке;
- `morphogenesis/experiments/L1_field/` — 251 артефакт линии поля и агрегат `l1_field_matrix.json`;
- `morphogenesis/experiments/E09_pond/habitable/` — 10 прогонов обитаемости и `habitable_matrix.json`;
- `morphogenesis/experiments/E09_pond/adequacy/` — 15 прогонов адекватности и `adequacy_matrix.json`;
- `lab/claims/` — утверждения с допущениями, бюджетом и ссылками на артефакты;
- `lab/runs/`, `morphogenesis/logs/journal.jsonl` — манифесты прогонов и канонический журнал;
- `docs/world-design.md` — полный план линии с оговорками;
- `scripts/` — код воспроизведения;
- `MANIFEST.json` — путь, размер и sha256 каждого файла.

## Как проверить целостность

Распаковать и сверить любой файл с `MANIFEST.json`, либо (если есть этот скрипт):

    python scripts/make_logs_bundle.py --verify <архив>.zip

Ожидаемый вывод: `битых 0, отсутствующих 0, сводный хеш совпадает: True`.

## Чего в пакете нет

Весов моделей (`.pt`), stdout-логов и чужих текстов: по контракту лаборатории в архив едет след, а не файлы
моделей. Отсутствие весов не мешает пересчитать все числа статьи — они считаются из JSON-артефактов.
"""

# Категории: (префикс в архиве, glob-шаблоны относительно корня репозитория)
PARTS: list[tuple[str, list[str]]] = [
    ("journal", ["morphogenesis/logs/journal.jsonl"]),
    ("runs", ["lab/runs/*.json"]),
    ("claims", ["lab/claims/*.json"]),
    ("aggregates", ["morphogenesis/experiments/L1_field/l1_field_matrix.json",
                    "lab/registry.json", "lab/queue.json", "lab/metrics.json"]),
    ("artifacts", ["morphogenesis/experiments/L1_field/*.json"]),
    ("habitable", ["morphogenesis/experiments/E09_pond/habitable/*.json"]),
    ("adequacy", ["morphogenesis/experiments/E09_pond/adequacy/*.json"]),
    ("article", ["articles/028-pole-bez-zadannyh-obektov.md",
                 "reports/2026-10-31-publication-package.md"]),
    ("docs", ["docs/world-design.md"]),
    ("legal", ["LICENSE", "CITATION.cff"]),
    ("code", ["scripts/field_track.py", "scripts/l1_field_matrix.py", "scripts/claim_comparator.py",
              "scripts/pond_probe_adequacy.py", "scripts/make_periodic_stream.py"]),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> list[Path]:
    seen: dict[Path, None] = {}
    for _, patterns in PARTS:
        for pat in patterns:
            for p in sorted(ROOT.glob(pat)):
                if p.is_file():
                    seen[p] = None
    return list(seen)


def build(out_path: Path) -> dict:
    files = collect()
    manifest = {"kind": "logs_bundle", "root": str(ROOT.name), "created_by": "scripts/make_logs_bundle.py",
                "files": [], "content_sha256": None}
    running = hashlib.sha256()
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        digest = sha256(p)
        manifest["files"].append({"path": rel, "bytes": p.stat().st_size, "sha256": digest})
        running.update(rel.encode("utf-8"))
        running.update(digest.encode("ascii"))
    manifest["content_sha256"] = running.hexdigest()
    manifest["total_bytes"] = sum(f["bytes"] for f in manifest["files"])
    manifest["file_count"] = len(manifest["files"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.relative_to(ROOT).as_posix())
        z.writestr("MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        z.writestr("README-BUNDLE.md", BUNDLE_README.format(count=manifest["file_count"],
                                                          mib=manifest["total_bytes"] / (1 << 20),
                                                          sha=manifest["content_sha256"]))
    return manifest


def verify(bundle: Path) -> int:
    with zipfile.ZipFile(bundle) as z:
        manifest = json.loads(z.read("MANIFEST.json").decode("utf-8"))
        bad, missing = [], []
        running = hashlib.sha256()
        for rec in manifest["files"]:
            try:
                data = z.read(rec["path"])
            except KeyError:
                missing.append(rec["path"])
                continue
            digest = hashlib.sha256(data).hexdigest()
            if digest != rec["sha256"]:
                bad.append(rec["path"])
            running.update(rec["path"].encode("utf-8"))
            running.update(digest.encode("ascii"))
        total_ok = running.hexdigest() == manifest["content_sha256"]
    print(f"[bundle] файлов {len(manifest['files'])}, "
          f"битых {len(bad)}, отсутствующих {len(missing)}, сводный хеш совпадает: {total_ok}")
    for b in bad[:5]:
        print("   битый:", b)
    for m in missing[:5]:
        print("   отсутствует:", m)
    return 0 if (not bad and not missing and total_ok) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сборка и проверка пакета логов")
    ap.add_argument("--out", default=None, help="куда положить архив")
    ap.add_argument("--verify", default=None, help="проверить существующий архив")
    args = ap.parse_args(argv)

    if args.verify:
        return verify(Path(args.verify))

    out = Path(args.out) if args.out else ROOT.parent / "_exports" / "logs-bundle.zip"
    m = build(out)
    print(f"[bundle] записано: {out}")
    print(f"[bundle] файлов {m['file_count']}, {m['total_bytes'] / 1024:.0f} КБ, "
          f"сводный sha256 {m['content_sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
