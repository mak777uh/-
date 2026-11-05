"""zenodo_deposit_030.py — deposit the article 030 archive on Zenodo through the records API.

Why not the legacy deposition API: that API cannot store a file name containing a slash, so `data/aggregates/x.json`
answers 404 and a loop over the unpacked tree stops at the first data file. The records API keeps the tree, which is what
`MANIFEST.sha256`, the article's links and the README all assume.

Usage:
    python scripts/zenodo_deposit_030.py --archive _exports/030-gap-switches-fusion
    python scripts/zenodo_deposit_030.py --archive _exports/030-gap-switches-fusion --verify
    python scripts/zenodo_deposit_030.py --archive _exports/030-gap-switches-fusion --publish

The token comes from `$ZENODO_TOKEN` or `--token-file`. The draft id is kept in the state file so that `--verify` and
`--publish` work in a later shell; `--publish` refuses if any uploaded file differs from the local copy.

Nothing here publishes unless `--publish` is passed, and the brief says that needs the author's written go-ahead.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://zenodo.org/api"
ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "_exports" / "zenodo-030-state.json"
RELATION = "issupplementto"   # used only if zenodo.json asks for it; 030 uses `references`


def token(args) -> str:
    if args.token_file:
        return pathlib.Path(args.token_file).read_text(encoding="utf-8").strip()
    value = os.environ.get("ZENODO_TOKEN", "").strip()
    if not value:
        sys.exit("[zenodo] no token: set $ZENODO_TOKEN or pass --token-file")
    return value


class Client:
    def __init__(self, token_value: str):
        self.token = token_value

    def call(self, method: str, url: str, data: bytes | None = None,
             content_type: str = "application/json") -> tuple[int, dict | list]:
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", "Bearer " + self.token)
        if data is not None:
            request.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                body = response.read()
                return response.status, (json.loads(body.decode("utf-8")) if body else {})
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            sys.exit(f"[zenodo] {method} {url} -> {exc.code}\n{detail}")


def map_metadata(legacy: dict, keywords: list[str] | None) -> dict:
    """Translate the legacy `zenodo.json` fields into the records API schema."""
    creators = []
    for creator in legacy["creators"]:
        name = creator["name"]
        if "," in name:
            family, given = [part.strip() for part in name.split(",", 1)]
        else:
            family, given = name.strip(), ""
        person = {"type": "personal", "family_name": family, "name": name}
        if given:
            person["given_name"] = given
        creators.append({"person_or_org": person})
    upload_type = legacy.get("upload_type", "publication")
    publication_type = legacy.get("publication_type", "preprint")
    resource_id = f"{upload_type}-{publication_type}" if publication_type else upload_type
    metadata = {
        "title": legacy["title"],
        "publication_date": legacy.get("publication_date") or datetime.date.today().isoformat(),
        "description": legacy["description"],
        "creators": creators,
        "resource_type": {"id": resource_id},
        "publisher": "Zenodo",
        "version": legacy.get("version", ""),
    }
    licence = legacy.get("license") or legacy.get("license_id")
    if licence:
        metadata["rights"] = [{"id": licence.lower().replace("cc-by-4.0", "cc-by-4.0")}]
    if keywords:
        # free-text keywords travel as `subjects` on this server; a `keywords` list is silently dropped
        metadata["subjects"] = [{"subject": word.strip()} for word in keywords if word.strip()]
    related = []
    for item in legacy.get("related_identifiers", []):
        related.append({
            "identifier": item["identifier"],
            "scheme": item.get("scheme", "doi"),
            "relation_type": {"id": {"references": "references", "isSupplementTo": "issupplementto",
                                     "isSupplementedBy": "issupplementedby", "isVersionOf": "isversionof"}
                              .get(item.get("relation", ""), item.get("relation", ""))},
        })
    if related:
        metadata["related_identifiers"] = related
    return {"access": {"record": "public", "files": "public"},
            "files": {"enabled": True},
            "metadata": metadata}


def archive_files(archive: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    """Every file to deposit: zenodo.json describes the record, it is not part of it."""
    files = [(p.relative_to(archive).as_posix(), p) for p in sorted(archive.rglob("*"))
             if p.is_file() and p.name != "zenodo.json"]
    if not files:
        sys.exit(f"[zenodo] no files under {archive}")
    return files


def md5(path: pathlib.Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entries_of(payload: dict) -> list[dict]:
    files = payload.get("files")
    if isinstance(files, dict):
        return files.get("entries", [])
    return files or []


def check(client: Client, record_id: str, files: list[tuple[str, pathlib.Path]]) -> list[dict]:
    _, draft = client.call("GET", f"{API}/records/{record_id}/draft")
    local = dict(files)
    problems = []
    uploaded = entries_of(draft)
    for entry in uploaded:
        key = entry["key"]
        path = local.get(key)
        if path is None:
            problems.append({"file": key, "problem": "not in the local archive"})
            continue
        if entry["size"] != path.stat().st_size:
            problems.append({"file": key, "problem": "size differs", "zenodo": entry["size"],
                             "local": path.stat().st_size})
        checksum = (entry.get("checksum") or "").removeprefix("md5:")
        if checksum and checksum != md5(path):
            problems.append({"file": key, "problem": "md5 differs", "zenodo": checksum, "local": md5(path)})
    missing = sorted(set(local) - {e["key"] for e in uploaded})
    for key in missing:
        problems.append({"file": key, "problem": "not uploaded"})
    print(f"[zenodo] server holds {len(uploaded)} files, archive has {len(files)}; problems: {len(problems)}")
    for problem in problems:
        print("   ", problem)
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="deposit the article 030 archive on Zenodo (records API)")
    ap.add_argument("--archive", required=True, help="unpacked archive directory (holds zenodo.json)")
    ap.add_argument("--state", default=str(DEFAULT_STATE), help="where the draft id is remembered")
    ap.add_argument("--token-file", default=None)
    ap.add_argument("--keywords", default=None,
                    help="comma-separated keywords; default: the `keywords` field of zenodo.json")
    ap.add_argument("--verify", action="store_true", help="only compare the draft with the local archive")
    ap.add_argument("--publish", action="store_true", help="publish the verified draft (irreversible)")
    args = ap.parse_args(argv)

    archive = pathlib.Path(args.archive)
    if not (archive / "zenodo.json").exists():
        sys.exit(f"[zenodo] {archive} has no zenodo.json — pass the unpacked archive directory")
    client = Client(token(args))
    state_path = pathlib.Path(args.state)
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    files = archive_files(archive)

    if args.verify or args.publish:
        if "id" not in state:
            sys.exit(f"[zenodo] no draft in {state_path}; run without --verify/--publish first")
        problems = check(client, state["id"], files)
        state["problems"] = problems
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        if args.publish:
            if problems:
                sys.exit("[zenodo] refusing to publish: the draft does not match the archive")
            _, published = client.call("POST", f"{API}/records/{state['id']}/draft/actions/publish")
            state["published"] = {key: published.get(key) for key in ("id", "doi", "links", "created")}
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
            print(json.dumps({"doi": published.get("doi"),
                              "url": published.get("links", {}).get("self_html")}, ensure_ascii=False, indent=1))
        return 0

    legacy = json.loads((archive / "zenodo.json").read_text(encoding="utf-8"))
    keywords = args.keywords.split(",") if args.keywords else legacy.get("keywords")
    _, draft = client.call("POST", f"{API}/records", json.dumps(map_metadata(legacy, keywords)).encode("utf-8"))
    record_id = draft["id"]
    print(f"[zenodo] draft {record_id} — {draft.get('links', {}).get('self_html')}")

    _, entries = client.call("POST", f"{API}/records/{record_id}/draft/files",
                             json.dumps([{"key": key} for key, _ in files]).encode("utf-8"))
    by_key = {entry["key"]: entry for entry in entries["entries"]}
    for key, path in files:
        client.call("PUT", by_key[key]["links"]["content"], path.read_bytes(), "application/octet-stream")
        client.call("POST", f"{API}/records/{record_id}/draft/files/{urllib.parse.quote(key, safe='')}/commit")
    state = {"id": record_id, "doi": None,
             "html": draft.get("links", {}).get("self_html"),
             "files": len(files), "bytes": sum(p.stat().st_size for _, p in files)}
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    problems = check(client, record_id, files)
    state["problems"] = problems
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[zenodo] state written to {state_path}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
