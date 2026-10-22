"""Проверка целостности портативного пакета E02b против его манифеста.

Что проверяется:

1. каждый файл из `portable_manifest.json` → `files[*].sha256` существует и
   совпадает по хешу и размеру (не только «файл есть»);
2. нет лишних файлов, которых нет в манифесте (кроме отчётов прогона, они и не
   должны там быть);
3. `portable_manifest.json` → `datasets.census.sha256` совпадает с фактическим
   хешем упакованного census, а `source_sha256` — с каноническим `census.json`
   в репозитории (проверка «пакетированный не равен каноническому, но оба
   записаны»);
4. ни в одном файле пакета не осталось абсолютных путей автора (`C:\\`, `/Users/`,
   `/content/`) — требование санитизации из DATASET_CARD, ограничение 10.

Печатает отчёт и возвращает 0/1. Ничего не пишет на диск: это проверка, а не
сборка.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "dist" / "e02b-portable"
CANON_CENSUS = REPO / "morphogenesis" / "experiments" / "E02b_morphospace" / "census.json"
ABS_PATH_RE = re.compile(r"(?:[A-Za-z]:\\\\|[A-Za-z]:\\|/Users/|/content/|/home/[a-z])")
SKIP_PREFIXES = ("verify_report",)  # отчёты прогона в манифест не входят
# Санитизация касается текстовых метаданных (census.json и т.п.), а не весов:
# в бинарных .pt случайные байты дают ложные совпадения с шаблоном путей.
TEXT_SUFFIXES = (".json", ".md", ".txt", ".py", ".yaml", ".yml", ".html", ".csv", ".ipynb")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors, warnings = [], []
    manifest_path = PKG / "portable_manifest.json"
    if not manifest_path.is_file():
        print(f"НЕТ манифеста: {manifest_path}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files") or []
    if not files:
        errors.append("в манифесте нет files[]")

    expected = {}
    for entry in files:
        rel = entry.get("path")
        if not rel:
            errors.append("запись манифеста без path")
            continue
        expected[rel] = entry
        path = PKG / rel
        if not path.is_file():
            errors.append(f"нет файла: {rel}")
            continue
        if entry.get("sha256") and sha256(path) != entry["sha256"]:
            errors.append(f"sha256 не совпал: {rel}")
        if entry.get("bytes") is not None and path.stat().st_size != entry["bytes"]:
            errors.append(f"размер не совпал: {rel} ({path.stat().st_size} != {entry['bytes']})")

    # Лишние файлы: всё, что не в манифесте и не отчёт прогона/сам манифест.
    on_disk = {
        p.relative_to(PKG).as_posix()
        for p in PKG.rglob("*")
        if p.is_file()
        and not p.name.startswith(SKIP_PREFIXES)
        and p.name != "portable_manifest.json"
    }
    extra = sorted(on_disk - set(expected))
    if extra:
        warnings.append(f"файлы вне манифеста: {extra}")

    # Хеши census: пакетированный и канонический.
    datasets = manifest.get("datasets") or {}
    census_rel = (datasets.get("census") or {}).get("path")
    packaged_sha = (datasets.get("census") or {}).get("sha256")
    source_sha = (datasets.get("census") or {}).get("source_sha256")
    if census_rel:
        packaged = PKG / census_rel
        if not packaged.is_file():
            errors.append(f"нет упакованного census: {census_rel}")
        else:
            actual = sha256(packaged)
            if packaged_sha and actual != packaged_sha:
                errors.append(f"datasets.census.sha256 не совпал с файлом ({actual[:12]}…)")
            print(f"OK   census упакованный: {actual[:12]}… ({packaged.stat().st_size} Б)")
    if source_sha:
        if not CANON_CENSUS.is_file():
            warnings.append("канонический census.json отсутствует — source_sha256 не проверен")
        else:
            actual_source = sha256(CANON_CENSUS)
            if actual_source != source_sha:
                errors.append(
                    f"source_sha256 канонического census не совпал: "
                    f"{actual_source[:12]}… != {source_sha[:12]}…"
                )
            else:
                print(f"OK   census канонический: {actual_source[:12]}… (не переписан)")

    # Абсолютные пути автора внутри текстовых файлов пакета.
    abs_hits = []
    scanned, skipped = 0, 0
    for rel in sorted(on_disk):
        if not rel.endswith(TEXT_SUFFIXES):
            skipped += 1
            continue
        scanned += 1
        path = PKG / rel
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if ABS_PATH_RE.search(text):
            abs_hits.append(rel)
    if abs_hits:
        errors.append(f"абсолютные пути остались в: {abs_hits}")
    else:
        print(
            f"OK   абсолютных путей автора нет в {scanned} текстовых файлах "
            f"(бинарные не сканируются: {skipped})"
        )

    print(f"файлов в манифесте: {len(expected)}, на диске: {len(on_disk)}")
    for err in errors:
        print(f"ОШИБКА {err}")
    for warn in warnings:
        print(f"ВНИМАНИЕ {warn}")
    print(f"ИТОГ: {len(errors)} ошибок, {len(warnings)} предупреждений")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
