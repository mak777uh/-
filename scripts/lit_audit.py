"""Аудит DOI в библиотеке: резолвятся ли и совпадает ли название.

Зачем в CI: DOI — единственная машинная связь библиотеки с внешним миром; битая ссылка
не находится глазами и не видна в git. Задача дешёвая по CPU, но требует сети — поэтому
локально или в nightly, а не в каждом PR.

    python scripts/lit_audit.py                 # все DOI, отчёт
    python scripts/lit_audit.py --limit 10      # первые 10 (быстрая проверка)
    python scripts/lit_audit.py --json out.json # машиночитаемо

Правила:
* берём `https://doi.org/...` из `library/**/*.md`, чистим хвост `.`/`,`/`;` и
  несбалансированную `)`;
* Crossref `works/<DOI>`; для `10.48550/arXiv.*` — DataCite;
* при ошибке сети — один повтор; HTTP 404 считаем битой ссылкой, а не ошибкой сети;
* сравниваем название: DOI-запись против заголовка ссылки (Jaccard по словам), слабое
  совпадение (<0.6) — предупреждение, а не ошибка (бывают переименования и подзаголовки);
* код возврата 1, если есть 404/несовпадение DOI-структуры; сетевые сбои — 0 с пометкой.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = "."
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
UA = "morphogenesis-lit-audit/1.0 (mailto:lab@example.org)"


def norm(text: str) -> set[str]:
    text = re.sub(r"<[^>]+>", " ", text or "").lower()
    text = re.sub(r"[^a-z0-9а-яё ]+", " ", text)
    return {w for w in text.split() if len(w) > 2}


def collect(root: str) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in glob.glob(f"{root}/library/**/*.md", recursive=True):
        try:
            text = io.open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in re.finditer(r"https://doi\.org/([^\s\"'<>\]]+)", text):
            raw = m.group(1)
            for d in DOI_RE.finditer(raw):
                doi = d.group(0)
                changed = True
                while changed:
                    changed = False
                    stripped = doi.rstrip(".,;")
                    if stripped != doi:
                        doi, changed = stripped, True
                    while doi.endswith(")") and doi.count("(") < doi.count(")"):
                        doi, changed = doi[:-1], True
                found.setdefault(doi, set()).add(path)
    return found


def fetch(doi: str) -> tuple[dict | None, str | None]:
    url = ("https://api.datacite.org/dois/" if doi.startswith("10.48550/")
           else "https://api.crossref.org/works/") + doi
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code == 404:
                return None, last
        except Exception as e:  # сеть
            last = type(e).__name__
        time.sleep(0.8)
    return None, last


def title_of(payload: dict, doi: str) -> str:
    if doi.startswith("10.48550/"):
        attrs = (payload.get("data") or {}).get("attributes") or {}
        titles = attrs.get("titles") or []
        parts = [t.get("title", "") if isinstance(t, dict) else str(t) for t in titles]
        return " ".join(p for p in parts if p)
    msg = payload.get("message") or {}
    parts = list(msg.get("title") or []) + list(msg.get("subtitle") or [])
    return " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Аудит DOI библиотеки")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    found = collect(args.root)
    dois = sorted(found)
    if args.limit:
        dois = dois[: args.limit]
    bad, weak, network = [], [], []
    for doi in dois:
        payload, err = fetch(doi)
        if payload is None:
            (network if err and err != "HTTP 404" else bad).append((doi, err))
            continue
        got = title_of(payload, doi)
        # заголовок ссылки в markdown: **[...] или [...]
        link_title = ""
        for path in found[doi]:
            text = io.open(path, encoding="utf-8", errors="ignore").read()
            url = re.escape("https://doi.org/" + doi) + r"(?=[)\s]|$)"
            # сначала жирный заголовок (наш формат **[Title](url)**), иначе — обычная ссылка,
            # но не подпись-цитата вида «Автор, 2020, Журнал»
            m = re.search(r"\*\*\[([^\]]+)\]\(" + url, text)
            if not m:
                m = re.search(r"\[([^\]]+)\]\(" + url, text)
            if m:
                candidate = m.group(1)
                if (re.search(r"(19|20)\d{2}", candidate) or "et al" in candidate
                        or candidate.count(",") >= 1 or re.match(r"^(10\.|DOI|с\.)", candidate)
                        or candidate in {"Оригинал", "Источник", "PDF", "текст", "статья"}):
                    continue
                link_title = candidate
                break
        if link_title and got:
            a, b = norm(link_title), norm(got)
            if a and b and not (a <= b or b <= a) and len(a & b) / len(a | b) < 0.6:
                weak.append((doi, link_title[:70], got[:70]))
    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline="\n").write(
            json.dumps({"total": len(dois), "bad": bad, "weak": weak, "network": network},
                       ensure_ascii=False, indent=2) + "\n"
        )
    print(f"проверено DOI: {len(dois)}")
    if bad:
        print(f"битые (404/структура): {len(bad)}")
        for doi, err in bad:
            print(f"  - {doi} [{err}]")
    if network:
        print(f"сетевые сбои (не считаем битыми): {len(network)}")
        for doi, err in network:
            print(f"  ~ {doi} [{err}]")
    if weak:
        print(f"слабые совпадения названий: {len(weak)}")
        for doi, lt, gt in weak:
            print(f"  ? {doi}\n      ссылка: {lt}\n      запись: {gt}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
