#!/usr/bin/env python
"""Регрессионные тесты инструментов библиотеки.

Проверяют три вещи: claim_audit ловит дефекты пакета, result_scan ловит переходы
по данным (включая пересекающиеся glob и исчезнувшие артефакты), lib_cycle
соблюдает приоритет/блокеры/запреты. Всё работает в temp-каталоге.

Запуск: python scripts/test_lib_tools.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable
FAILED: list[str] = []


def run(*args, cwd=REPO) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        FAILED.append(name)


CLAIMS_TABLE = """# тест

| # | Утверждение | Артефакт | Контроль | Эффект | Граница | Якорь | Встречный тест | Пробел |
|---|---|---|---|---|---|---|---|---|
| C1 | хороший | {good_artifact} | контроль | 10 ± 2 | W1 | {good_anchor} | тест | пробел есть |
| C2 | плохой артефакт | morphogenesis/__нет__.json | контроль | 10 ± 2 | W1 | {good_anchor} | тест | пробел |
| C3 | плохой якорь | {good_artifact} | контроль | 10 ± 2 | W1 | P999 | тест | пробел |
| C4 | пустой пробел | {good_artifact} | контроль | 10 ± 2 | W1 | {good_anchor} | тест | нет |
| C5 | без интервала | {good_artifact} | контроль | 10 | W1 | {good_anchor} | тест | пробел |
"""


def test_claim_audit(tmp: Path) -> None:
    table = tmp / "claims.md"
    table.write_text(CLAIMS_TABLE.format(
        good_artifact="library/conditions.md", good_anchor="P43"), encoding="utf-8")
    res = run("scripts/claim_audit.py", "--table", str(table))
    check("claim_audit: ловит артефакт/якорь/пробел", res.returncode == 1, res.stdout[-200:])
    check("claim_audit: C1 чистый", "C1: ok" in res.stdout, res.stdout)
    check("claim_audit: C2 artifact", "C2: artifact" in res.stdout, res.stdout)
    check("claim_audit: C3 anchor", "C3: anchor" in res.stdout, res.stdout)
    check("claim_audit: C4 gap", "C4: gap" in res.stdout, res.stdout)
    multi = tmp / "claims_multi.md"
    multi.write_text(CLAIMS_TABLE.format(good_artifact="library/conditions.md",
                                         good_anchor="P43, P44").replace("{good_anchor}", "P43, P44"),
                     encoding="utf-8")
    res = run("scripts/claim_audit.py", "--table", str(multi))
    check("claim_audit: несколько якорей через запятую", "C1: ok" in res.stdout, res.stdout)
    res2 = run("scripts/claim_audit.py", "--table", str(table), "--strict")
    check("claim_audit --strict: C5 interval", "C5: interval" in res2.stdout, res2.stdout)


def scan(tmp: Path, src: Path, cfg: Path, state: Path) -> str:
    res = run("scripts/result_scan.py", "--src", str(src), "--map", str(cfg),
              "--state", str(state), "--inbox", str(tmp / "inbox.jsonl"), "--no-queue")
    if res.returncode != 0:
        return "ОШИБКА: " + (res.stderr or res.stdout)[-300:]
    return res.stdout


def write_cfg(path: Path) -> None:
    cfg = {"claims": [
        {"id": "C6", "title": "инвазия", "question": "критерии инвазии?",
         "globs": ["colinv3_*.json"]},
        {"id": "C2", "title": "affordance", "question": "affordance?",
         "globs": ["shared_*.json"]},
        {"id": "C3", "title": "placebo", "question": "placebo?",
         "globs": ["shared_*.json"]}],
        "arms": ["inherit", "random"],
        "rules": {"C6_min_start": 0.05, "C5_generation": 165}}
    path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")


def test_result_scan(tmp: Path) -> None:
    src = tmp / "art"
    src.mkdir()
    cfg = tmp / "map.json"
    write_cfg(cfg)
    state = tmp / "state.json"

    shared = src / "shared_a.json"
    shared.write_text(json.dumps({"median": 1}), encoding="utf-8")
    inv = src / "colinv3_fd0_BinvA_inherit_seed1.json"
    inv.write_text(json.dumps({"summary": {"injection_share_actual": 0.002,
                                          "a_share_final": 0.0}}), encoding="utf-8")
    out = scan(tmp, src, cfg, state)
    check("scan: первый прогон без сюрпризов", "переходов: 0" in out, out)

    # 1) изменение чисел -> запись changed, без перехода
    inv.write_text(json.dumps({"summary": {"injection_share_actual": 0.002,
                                          "a_share_final": 0.8}}), encoding="utf-8")
    out = scan(tmp, src, cfg, state)
    check("scan: verdict по фиксации редкого инвайдера", "verdict" in out and "0.0020" in out, out)
    inbox = (tmp / "inbox.jsonl").read_text(encoding="utf-8").splitlines()
    check("scan: запись в inbox", len(inbox) >= 1 and "changed" in inbox[-1], inbox[-1] if inbox else "")

    # 2) новый режим в имени файла
    newmode = src / "colinv3_fd0_BinvA_immune_seed1.json"
    newmode.write_text(json.dumps({"summary": {"injection_share_actual": 0.3,
                                              "a_share_final": 0.1}}), encoding="utf-8")
    out = scan(tmp, src, cfg, state)
    check("scan: новый режим пойман", "new_mode" in out and "immune" in out, out)

    # 3) невалидный прогон
    inv2 = src / "colinv3_fd0_BinvA_random_seed2.json"
    inv2.write_text(json.dumps({"summary": {"injection_share_actual": 0.4,
                                           "a_share_final": 0.1,
                                           "invalid_reason": "переворот компонента"}}),
                    encoding="utf-8")
    out = scan(tmp, src, cfg, state)
    check("scan: невалидный поймал", "invalid" in out, out)

    # 4) пересекающиеся glob: один файл — два утверждения
    shared.write_text(json.dumps({"median": 2}), encoding="utf-8")
    out = scan(tmp, src, cfg, state)
    inbox_lines = (tmp / "inbox.jsonl").read_text(encoding="utf-8").splitlines()
    recs = [json.loads(line) for line in inbox_lines]
    claims = {r["claim"] for r in recs if r.get("file", "").endswith("shared_a.json")}
    check("scan: пересекающиеся glob дают оба утверждения", {"C2", "C3"} <= claims, str(claims))

    # 5) markdown не должен давать new_mode
    md = src / "notes_design_doc.md"
    md.write_text("# заголовок\n", encoding="utf-8")
    out_md = scan(tmp, src, cfg, state)
    check("scan: markdown не даёт new_mode", "new_mode" not in out_md.split("notes_design_doc")[0][-200:], out_md)

    # 6) исчезнувший артефакт
    newmode.unlink()
    out = scan(tmp, src, cfg, state)
    check("scan: исчезнувший артефакт пойман", "removed" in out, out)


def test_lib_cycle(tmp: Path) -> None:
    q = tmp / "queue.json"
    log = tmp / "log.md"
    st = tmp / "state.json"
    opts = ["--queue-path", str(q), "--log-path", str(log), "--state-path", str(st)]

    def call(*args) -> subprocess.CompletedProcess:
        return run("scripts/lib_cycle.py", *opts, *args)

    check("lib_cycle: impact вне 1..5 отклонён",
          call("add", "review", "плохой", "--id", "X1", "--impact", "9").returncode == 2)
    check("lib_cycle: добавление работает",
          call("add", "review", "низкий", "--id", "X1", "--impact", "2", "--effort", "2").returncode == 0)
    check("lib_cycle: дубль id отклонён",
          call("add", "review", "снова", "--id", "X1", "--impact", "3").returncode == 2)
    check("lib_cycle: второе добавление",
          call("add", "claim", "высокий", "--id", "X2", "--impact", "5", "--effort", "1").returncode == 0)
    check("lib_cycle: третье с блокером",
          call("add", "lit", "заблокированный", "--id", "X3", "--impact", "5", "--effort", "1",
               "--blocked-by", "X2").returncode == 0)

    out = call("next").stdout
    check("lib_cycle: next выбирает максимальный impact/effort", '"X2"' in out, out)

    check("lib_cycle: done без заметки отклонён", call("done", "X2").returncode == 2)
    check("lib_cycle: done с заметкой", call("done", "X2", "--note", "сделано").returncode == 0)
    out2 = call("next").stdout
    check("lib_cycle: после закрытия блокер снят", '"X3"' in out2, out2)
    check("lib_cycle: журнал заполняется", log.exists() and "X2" in log.read_text(encoding="utf-8"))


def test_notices(tmp: Path) -> None:
    notices = tmp / "notices.md"
    notices.write_text("""### 2026-10-24, 10:00 — библиотекарь → **учёному**
- ЗАПРОС: пересобрать агрегат fd10 (B-035)
- ЗАПРОС: серия с мутацией типа (W13)

### 2026-10-24, 11:00 — библиотекарь → **ведущему**
ОТВЕТ: агрегат пересобран (B-035).

### 2026-10-20, 09:00 — библиотекарь → **учёному**
- ЗАПРОС: старый запрос без ответа (B-999)
""", encoding="utf-8")
    res = run("scripts/notices_status.py", "--notices", str(notices), "--max-hours", "24")
    out = res.stdout
    check("notices: запросы найдены", "запросов: 3" in out, out)
    check("notices: ОТВЕТ по ссылке закрывает нужный запрос",
          out.count("answered") >= 1 or "closed(очередь)" in out, out)
    check("notices: старый запрос помечен", "старше 24 ч: 1" in out and "B-999" in out, out)
    check("notices: код возврата 1 при просрочке", res.returncode == 1, str(res.returncode))
    check("notices: упоминание B-### не закрывает запрос", "closed(доска)" not in out, out)
    notices2 = tmp / "notices2.md"
    notices2.write_text("""### 2026-10-24, 10:00 — ведущий → **библиотекарю**
- ЗАПРОС: зафиксировать шкалу fd

### 2026-10-24, 11:00 — библиотекарь → **ведущему**
ЗАКРЫТО: зафиксировать шкалу fd — сделано планом colinv4
""", encoding="utf-8")
    res2 = run("scripts/notices_status.py", "--notices", str(notices2))
    check("notices: ЗАКРЫТО по фрагменту", "открытых: 0" in res2.stdout, res2.stdout)


def test_trait_metrics(tmp: Path) -> None:
    out = tmp / "metrics.json"
    res = run("library/tools/trait_metrics.py", "--src", "library/tools/fixtures",
              "--glob", "*.json", "--json", str(out))
    check("trait_metrics: код 0", res.returncode == 0, res.stdout + res.stderr)
    data = json.loads(out.read_text(encoding="utf-8"))
    by_name = {r["artifact"]: r for r in data["results"]}
    valid = by_name.get("valid_mut.json", {})
    check("trait_metrics: Shannon посчитан", (valid.get("shannon_median") or 0) > 0.1, str(valid))
    check("trait_metrics: новизна посчитана", (valid.get("novelty_flux") or 0) >= 1, str(valid))
    check("trait_metrics: Спирмен посчитан", valid.get("spearman_trait_births") is not None, str(valid))
    missing = by_name.get("missing_fields.json", {})
    m0 = by_name.get("m0_control.json", {})
    check("trait_metrics: при m=0 новизна строго 0", m0.get("novelty_flux") == 0, str(m0))
    check("trait_metrics: предковая метка исключена",
          m0.get("novelty_ancestral_excluded") == ["A"] and m0.get("types_total") == 1, str(m0))
    ref_out = tmp / "ref_metrics.json"
    ref = run("scripts/trait_metrics.py", "--src", "library/tools/fixtures",
              "--glob", "*.json", "--json", str(ref_out))
    if ref.returncode == 0 and ref_out.exists():
        ref_data = json.loads(ref_out.read_text(encoding="utf-8"))
        ref_by = {r["artifact"]: r for r in (ref_data.get("results") or ref_data.get("rows") or [])}
        agree = all(
            abs((by_name.get(n, {}).get("shannon_median") or 0) - (ref_by.get(n, {}).get("shannon_median") or 0)) < 1e-9
            and by_name.get(n, {}).get("novelty_flux") == ref_by.get(n, {}).get("novelty_flux")
            for n in ("valid_mut.json", "m0_control.json") if n in ref_by)
        check("trait_metrics: согласие с референсом учёного", agree, str(ref_by))
    check("trait_metrics: отсутствие полей = invalid, не ноль",
          missing.get("valid") is False and "type_counts_series" in (missing.get("invalid_reason") or ""),
          str(missing))


def test_wake_notices(tmp: Path) -> None:
    root = tmp / "wake_root"
    (root / "lab").mkdir(parents=True)
    notices = root / "lab" / "notices.md"
    notices.write_text("### 2026-10-24, 10:00 — ведущий → **библиотекарю**\n"
                       "- ЗАПРОС: проверить агрегат\n", encoding="utf-8")
    (root / "lab" / "queue.json").write_text(json.dumps({"items": []}), encoding="utf-8")
    res = run("scripts/library_wake.py", "--root", str(root), "--show")
    data = json.loads(res.stdout)
    check("wake: просьба библиотекарю видна в отпечатке",
          data["notices_to_me"]["requests"] == 1, res.stdout[:200])
    check("wake: очередь ведущего в отпечатке", data["lead_queue"]["exists"] is True, res.stdout[:200])

    notices.write_text("### 2026-10-24, 10:00 — ведущий → **библиотекарю**\n"
                       "- ЗАПРОС: проверить агрегат\n"
                       "- ЗАПРОС: собрать интервалы\n", encoding="utf-8")
    res2 = run("scripts/library_wake.py", "--root", str(root), "--show")
    data2 = json.loads(res2.stdout)
    check("wake: новый запрос меняет digest",
          data2["notices_to_me"]["digest"] != data["notices_to_me"]["digest"], "digest не изменился")
    check("wake: счётчик запросов растёт", data2["notices_to_me"]["requests"] == 2, res2.stdout[:200])


def test_series_provenance(tmp: Path) -> None:
    src = tmp / "series"
    src.mkdir()
    good = {"config": {"git_commit": "abc123def456", "dirty": False}}
    (src / "s1.json").write_text(json.dumps(good), encoding="utf-8")
    (src / "s2.json").write_text(json.dumps(good), encoding="utf-8")
    res = run("library/tools/series_provenance.py", "--src", str(src))
    check("provenance: один коммит = ок", res.returncode == 0, res.stdout)
    (src / "s3.json").write_text(json.dumps({"config": {"git_commit": "999999", "dirty": False}}),
                                 encoding="utf-8")
    res = run("library/tools/series_provenance.py", "--src", str(src))
    check("provenance: два коммита = провал", res.returncode == 1 and "невалидна" in res.stdout, res.stdout)
    (src / "s4.json").write_text(json.dumps({"config": {"dirty": True}}), encoding="utf-8")
    res = run("library/tools/series_provenance.py", "--src", str(src))
    check("provenance: без провенанса ловится", "БЕЗ ПРОВЕНАНСА" in res.stdout, res.stdout)


def test_v8_matrix(tmp: Path) -> None:
    res = run("library/tools/v8_matrix.py", "--src", "library/tools/fixtures/v8")
    check("v8: неполные плечи — вердикт не выносится",
          "плечи неполные" in res.stdout and "вердикт не выносится" in res.stdout, res.stdout[-300:])
    out = tmp / "v8.json"
    res = run("library/tools/v8_matrix.py", "--src", "library/tools/fixtures/v8", "--json", str(out))
    data = json.loads(out.read_text(encoding="utf-8"))
    check("v8: семантика инвайдера = 1 - a_share",
          any(r["invader_share_final"] == 1.0 for r in data["rows"]), str(data["rows"][:1]))


def test_wake_series_keys(tmp: Path) -> None:
    res = run("-c", "import sys; sys.path.insert(0,'scripts'); "
                   "from library_wake import is_series_only, is_significant; "
                   "print(is_series_only(['journal']), is_series_only(['journal','runs']), "
                   "is_series_only(['journal','manuscript']), is_significant(['notices_to_me']))")
    check("wake: journal/runs — прогресс серии (settle), рукопись — сразу",
          res.stdout.strip() == "True True False True", res.stdout + res.stderr)


def test_wake_lock(tmp: Path) -> None:
    root = tmp / "lock_root"
    (root / "lab").mkdir(parents=True)
    (root / "library").mkdir(parents=True)
    (root / "lab" / "notices.md").write_text("# пусто\n", encoding="utf-8")
    lock = root / "library" / ".wake.pid"
    lock.write_text("99999", encoding="utf-8")
    res = run("scripts/library_wake.py", "--root", str(root), "--state", str(tmp / "st.json"),
              "--wait", "--timeout", "3", "--interval", "1")
    check("wake lock: свежий замок блокирует", "уже работает" in res.stdout, res.stdout)
    import os, time
    old = time.time() - 600
    os.utime(lock, (old, old))
    res2 = run("scripts/library_wake.py", "--root", str(root), "--state", str(tmp / "st.json"),
               "--wait", "--timeout", "5", "--interval", "1")
    check("wake lock: устаревший замок снимается сам", "уже работает" not in res2.stdout, res2.stdout)
    lock.write_text("99999", encoding="utf-8")
    res3 = run("scripts/library_wake.py", "--root", str(root), "--state", str(tmp / "st.json"),
               "--wait", "--timeout", "5", "--interval", "1", "--force")
    check("wake lock: --force снимает свежий замок", "уже работает" not in res3.stdout, res3.stdout)
    check("wake lock: замок снят после выхода", not lock.exists(), "замок остался")


def test_lit_pressure(tmp: Path) -> None:
    out = tmp / "lp.json"
    res = run("scripts/lit_pressure.py", "--threshold", "1", "--json", str(out))
    data = json.loads(out.read_text(encoding="utf-8"))
    check("lit_pressure: считает давление и решает", "pressure" in data and "need" in data, str(data)[:200])
    check("lit_pressure: при пороге 1 слот нужен (долг есть)", data["need"] is True, str(data)[:200])
    out2 = tmp / "lp2.json"
    res2 = run("scripts/lit_pressure.py", "--threshold", "99", "--json", str(out2))
    data2 = json.loads(out2.read_text(encoding="utf-8"))
    check("lit_pressure: при высоком пороге слот не нужен", data2["need"] is False, str(data2)[:200])
    check("lit_pressure: код возврата отражает вердикт",
          (res.returncode == 1) == data["need"] and (res2.returncode == 0) == (not data2["need"]),
          f"{res.returncode}/{res2.returncode}")


def main() -> int:
    with tempfile.TemporaryDirectory() as tdir:
        tmp = Path(tdir)
        print("== claim_audit ==")
        test_claim_audit(tmp)
        print("== result_scan ==")
        test_result_scan(tmp)
        print("== lib_cycle ==")
        test_lib_cycle(tmp)
        print("== notices ==")
        test_notices(tmp)
        print("== trait_metrics ==")
        test_trait_metrics(tmp)
        print("== wake notices ==")
        test_wake_notices(tmp)
        print("== provenance ==")
        test_series_provenance(tmp)
        print("== v8 ==")
        test_v8_matrix(tmp)
        print("== wake series keys ==")
        test_wake_series_keys(tmp)
        print("== wake lock ==")
        test_wake_lock(tmp)
        print("== lit pressure ==")
        test_lit_pressure(tmp)
    print(f"\nпровалено: {len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
