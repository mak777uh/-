#!/usr/bin/env python
"""zenodo_upload.py — депозит новой версии в Zenodo одной командой (без ручной загрузки в браузере).

Зачем: ручная загрузка 6.5 ГБ через браузер — работа, которую нельзя повторять часто, и именно
поэтому веса до сих пор не депонированы. Здесь: токен читается из файла ВНЕ репозитория,
скрипт сам создаёт депозицию, заливает файлы, публикует и возвращает DOI.

Токен (не в git, не в чат):
    1. Zenodo → Settings → Applications → New token (scopes: deposit:write, deposit:actions)
    2. положить в файл:  ..\\_zenodo\\.token        (одна строка, без кавычек)
    3. chmod/ACL: доступ только у владельца

Команды:
    python scripts/zenodo_upload.py --plan            # что будет залито, без сети
    python scripts/zenodo_upload.py --check-token     # проверить токен и квоту
    python scripts/zenodo_upload.py --upload --files weights
    python scripts/zenodo_upload.py --publish <deposition_id>

После публикации DOI вставляется в репозиторий:
    python scripts/zenodo_link.py --weights-doi 10.5281/zenodo.XXXXXXX --concept-doi ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT.parent / "_zenodo" / ".token"
API = "https://zenodo.org/api"
BUNDLE = ROOT.parent / "_zenodo" / "checkpoints-v1.1"

# что заливаем: имена берём из инвентаря, а не из головы
WEIGHTS_FROM = ROOT / "morphogenesis" / "checkpoints"
WEIGHTS_INDEX = ROOT / "docs" / "checkpoints-v1.1.json"


def token() -> str | None:
    if not TOKEN_FILE.exists():
        return None
    raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
    return raw or None


def call(method: str, url: str, tok: str, data: dict | None = None, raw: bytes | None = None,
         content_type: str = "application/json") -> dict:
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise SystemExit(f"[zenodo] HTTP {exc.code}: {detail}")


def weights_files() -> list[Path]:
    index = json.loads(WEIGHTS_INDEX.read_text(encoding="utf-8"))
    out = []
    for entry in index.get("checkpoints") or []:
        p = ROOT / entry["path"]
        if p.exists():
            out.append(p)
    return out


def plan() -> int:
    w = weights_files()
    total = sum(p.stat().st_size for p in w)
    print(f"[zenodo] веса: {len(w)} файлов, {total / 1e9:.2f} ГБ")
    for p in w[:3]:
        print(f"   {p.relative_to(ROOT)} ({p.stat().st_size / 1e6:.0f} МБ)")
    print("   …")
    docs = sorted(BUNDLE.glob("*")) if BUNDLE.exists() else []
    print(f"[zenodo] метаданные: {len(docs)} файлов из {BUNDLE}")
    for p in docs:
        print(f"   {p.name}")
    if not docs:
        print("[zenodo] ВНИМАНИЕ: пакет метаданных не найден — создайте _zenodo/checkpoints-v1.1/")
    print(f"[zenodo] токен: {'найден' if token() else 'НЕ найден → ' + str(TOKEN_FILE)}")
    return 0


def check_token() -> int:
    tok = token()
    if not tok:
        print(f"[zenodo] токена нет: {TOKEN_FILE}")
        return 1
    try:
        who = call("GET", f"{API}/deposit/depositions?size=1", tok)
    except SystemExit as exc:
        print(exc)
        return 1
    print(f"[zenodo] токен работает; последних депозиций доступно: {len(who) if isinstance(who, list) else '?'}")
    return 0


def upload(meta: dict) -> int:
    tok = token()
    if not tok:
        print(f"[zenodo] токена нет: {TOKEN_FILE}")
        return 1
    dep = call("POST", f"{API}/deposit/depositions", tok, {"metadata": meta})
    dep_id, bucket = dep["id"], dep["links"]["bucket"]
    print(f"[zenodo] создана депозиция {dep_id} (черновик)")
    files = [(p, p.name) for p in weights_files()]
    files += [(p, p.name) for p in sorted(BUNDLE.glob("*"))] if BUNDLE.exists() else []
    for path, name in files:
        print(f"   загружаю {name} ({path.stat().st_size / 1e6:.0f} МБ)…")
        with open(path, "rb") as fh:
            call("PUT", f"{bucket}/{name}", tok, raw=fh.read(), content_type="application/octet-stream")
    print(f"[zenodo] загружено {len(files)} файлов. Проверьте в браузере и публикуйте:")
    print(f"   python scripts/zenodo_upload.py --publish {dep_id}")
    return 0


def publish(dep_id: str) -> int:
    tok = token()
    if not tok:
        print(f"[zenodo] токена нет: {TOKEN_FILE}")
        return 1
    out = call("POST", f"{API}/deposit/depositions/{dep_id}/actions/publish", tok)
    doi = (out.get("doi") or "").replace("10.5281/zenodo.", "")
    print(f"[zenodo] опубликовано. DOI: {out.get('doi')}")
    print(f"[zenodo] вставьте в репозиторий: python scripts/zenodo_link.py --weights-doi {out.get('doi')}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="депозит в Zenodo без браузера")
    ap.add_argument("--plan", action="store_true", help="показать состав, не ходить в сеть")
    ap.add_argument("--check-token", action="store_true", help="проверить токен")
    ap.add_argument("--upload", action="store_true", help="создать депозицию и залить файлы")
    ap.add_argument("--publish", metavar="ID", help="опубликовать депозицию")
    args = ap.parse_args(argv)

    if args.plan:
        return plan()
    if args.check_token:
        return check_token()
    if args.upload:
        meta = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
        deposit = meta.get("deposit") or {}
        payload = {
            "title": deposit.get("title", "Morphogenesis — canonical checkpoints"),
            "upload_type": "dataset",
            "description": "Канонические веса NCA. См. README_ZENODO.md и CHECKPOINTS.md в этой записи.",
            "creators": [{"name": deposit.get("author", "Ilya Vladimirov"),
                          "affiliation": deposit.get("affiliation", "Independent researcher")}],
            "license": "MIT",
            "version": deposit.get("version", "1.1.0"),
        }
        return upload(payload)
    if args.publish:
        return publish(args.publish)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
