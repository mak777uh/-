"""Собрать приложение-таблицу артефактов с хешами (manuscript/SUPPLEMENT.md).

Зачем: §7 рукописи перечисляет артефакты прозой, но при подаче нужен
машинно-проверяемый список: путь → размер → sha256 → тип. Таблица собирается
обходом каталогов (а не по памяти), поэтому её нельзя «забыть обновить»: тест
сверяет файл с тем, что даёт эта функция.

Категории (по имени файла):

- `canonical` — то, на чём держатся числа: `census.json`,
  `class_centroids_frozen.json`, `perturbations.json`;
- `derived` — агрегаты и сводки: `summary_*.json`, `seed_grid*.json`,
  `census_*.json` (переписи отдельных прогонов);
- `experimental` — exploratory-артефакты `*_exploratory.json`;
- `figure` — PNG в `reports/figures/`;
- `index` — `lab/checkpoints.json`, `lab/registry.json`.

Запуск (из корня):

    python scripts/make_artifact_table.py           # напечатать
    python scripts/make_artifact_table.py --write   # переписать SUPPLEMENT.md
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "manuscript" / "SUPPLEMENT.md"
START = "<!-- artifacts:start -->"
END = "<!-- artifacts:end -->"

DIRS = [
    REPO / "morphogenesis" / "experiments",
    REPO / "reports" / "figures",
]
EXTRA = [REPO / "lab" / "checkpoints.json", REPO / "lab" / "registry.json"]

# Служебные файлы, которые переписываются при каждом прогоне фермы и каждого health-цикла.
# В таблице артефактов им не место: они не научные данные, а статус, и именно они держали
# SUPPLEMENT в состоянии «отстал от диска» — тест падал в CI снова и снова.
VOLATILE = {
    "morphogenesis/experiments/E09_pond/analysis/farm-status.json",
    "morphogenesis/experiments/E09_pond/provenance-legacy.json",
}


TEXT_SUFFIXES = {".json"}  # см. .gitattributes: `*.json text eol=lf`


def normalized_bytes(path: Path) -> bytes:
    """Байты артефакта в канонической форме git: CRLF → LF для текстовых файлов.

    `.gitattributes` объявляет `*.json text eol=lf`, поэтому в свежем клоне рабочая
    копия приходит с LF, а на Windows-машине без нормализации — с CRLF. Хеш и размер
    считаются по нормализованным байтам, иначе таблица расходится между платформами
    (проверено на чистом клоне: тест падал на каждом CRLF-артефакте). Бинарные
    артефакты (.png) не нормализуются никогда.
    """
    data = path.read_bytes()
    if path.suffix in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


_BLOB_CACHE: dict[str, bytes | None] = {}


def prefetch_blobs(paths: list[Path]) -> None:
    """Один вызов `git cat-file --batch` на все файлы: по одному процессу на файл слишком медленно
    (сотни файлов → минуты). Кеш общий, поэтому render() и sha256() берут уже прочитанное."""
    todo = [p.relative_to(REPO).as_posix() for p in paths
            if p.relative_to(REPO).as_posix() not in _BLOB_CACHE]
    if not todo:
        return
    try:
        proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=REPO,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError:
        return
    payload = ("".join(f"HEAD:{rel}\n" for rel in todo)).encode()
    out, _ = proc.communicate(payload)
    pos = 0
    for rel in todo:
        nl = out.find(b"\n", pos)
        if nl < 0:
            break
        header = out[pos:nl].decode("utf-8", "replace")
        pos = nl + 1
        parts = header.split()
        if len(parts) < 3 or parts[1] == "missing":
            _BLOB_CACHE[rel] = None
            continue
        size = int(parts[2])
        _BLOB_CACHE[rel] = out[pos:pos + size]
        pos += size + 1  # блоб + перевод строки


def git_blob(path: Path) -> bytes | None:
    """Содержимое файла ИЗ COMMIT (HEAD), а не с диска.

    Почему: таблица должна воспроизводиться в чистом клоне. Пока хеши считались по диску,
    любая незакоммиченная правка (или файл, обновляемый прогоном вне git) делала SUPPLEMENT
    невоспроизводимым — тест `test_supplement_matches_disk` падал в CI четвёртый раз за сутки,
    а локально проходил. Источник истины для артефакта — коммит.
    """
    rel = path.relative_to(REPO).as_posix()
    if rel not in _BLOB_CACHE:
        prefetch_blobs([path])
    return _BLOB_CACHE.get(rel)


def content_bytes(path: Path) -> bytes:
    """Байты из HEAD (нормализованные), с откатом на диск вне git."""
    blob = git_blob(path)
    if blob is None:
        return normalized_bytes(path)
    if path.suffix in TEXT_SUFFIXES:
        return blob.replace(b"\r\n", b"\n")
    return blob


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(content_bytes(path))
    return h.hexdigest()


def kind_of(path: Path) -> str:
    name = path.name
    if path.suffix == ".png":
        return "figure"
    if name in ("census.json", "class_centroids_frozen.json", "perturbations.json"):
        return "canonical"
    if name in ("checkpoints.json", "registry.json"):
        return "index"
    if name.startswith("summary_") or name.startswith("seed_grid"):
        return "derived"
    if name.startswith("census_"):
        return "derived"
    if name.endswith("_exploratory.json"):
        return "experimental"
    return "other"


def git_tracked() -> set[str] | None:
    """Пути, которые реально есть в git (posix, относительно корня). None — git недоступен.

    Таблица обязана совпадать со свежим клоном: локальные кадры и прочие файлы, которые
    по §5a в git не едут, в неё попадать не должны.
    """
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p for p in out.stdout.decode("utf-8", "replace").split("\0") if p}


def collect() -> list[Path]:
    files: list[Path] = []
    for directory in DIRS:
        if directory.is_dir():
            files.extend(p for p in directory.rglob("*") if p.is_file())
    files.extend(p for p in EXTRA if p.is_file())
    # строки *_rows.jsonl локальные (в git не едут) — их в таблице нет
    files = [p for p in files if p.suffix in (".json", ".png")]
    files = [p for p in files if p.relative_to(REPO).as_posix() not in VOLATILE]
    tracked = git_tracked()
    if tracked is not None:
        files = [p for p in files if p.relative_to(REPO).as_posix() in tracked]
    files = sorted(files)
    prefetch_blobs(files)  # один процесс git на всю таблицу
    return files


def link(path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    return f"[`{rel}`](../{rel})"


def render(files: list[Path] | None = None) -> str:
    files = files if files is not None else collect()
    rows = [
        "| Артефакт | Тип | Байт | sha256 |",
        "| --- | --- | ---: | --- |",
    ]
    for path in files:
        rows.append(
            "| {link} | {kind} | {size} | `{sha}` |".format(
                link=link(path),
                kind=kind_of(path),
                size=len(content_bytes(path)),
                sha=sha256(path),
            )
        )
    return START + "\n" + "\n".join(rows) + "\n" + END


def replace_block(text: str, table: str) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"в {OUT.name} нет маркеров")
    return pattern.sub(lambda _m: table, text)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="переписать manuscript/SUPPLEMENT.md")
    args = ap.parse_args(argv)

    table = render()
    if args.write:
        if not OUT.is_file():
            raise SystemExit(f"нет {OUT}: сначала создайте файл с маркерами")
        OUT.write_text(
            replace_block(OUT.read_text(encoding="utf-8"), table) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"обновлено: {OUT}")
    else:
        print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
