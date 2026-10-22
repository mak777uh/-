"""test_check_links.py — проверка относительных ссылок в markdown.

`scripts/check_links.py` — то, что ловит «артефакт переименовали, ссылку забыли».
`lab.py validate` проверяет журнал README и карту рукописи, но не ссылки, поэтому
этот тест держит линтер честным, а второй тест — сами публичные документы: если
в рукописи или отчётах появится ссылка в пустоту, тест упадёт.

Проверяется: рабочая ссылка, битая ссылка, внешние URL и чисто якорные ссылки
пропускаются, содержимое блоков кода не сканируется, ссылка на каталог допустима,
и отсутствие цели даёт код возврата 1.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_links.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_links_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def test_existing_relative_links_are_ok(tmp_path):
    module = load_module()
    write(tmp_path / "target.md", "# target\n")
    (tmp_path / "sub").mkdir()
    write(tmp_path / "sub" / "deep.md", "# deep\n")
    doc = write(
        tmp_path / "doc.md",
        "[ok](target.md)\n[dir](sub/)\n[deep](sub/deep.md)\n[anchor](target.md#part)\n",
    )
    checked, broken = module.check([doc])
    assert (checked, broken) == (4, [])


def test_broken_link_is_reported_with_line(tmp_path):
    module = load_module()
    doc = write(tmp_path / "doc.md", "текст\n[нет](missing.md)\n")
    checked, broken = module.check([doc])
    assert checked == 1
    assert len(broken) == 1 and ":2:" in broken[0] and "missing.md" in broken[0]


def test_external_and_anchor_only_links_are_skipped(tmp_path):
    module = load_module()
    doc = write(
        tmp_path / "doc.md",
        "[web](https://example.org/x)\n[mail](mailto:a@b.c)\n[local](#section)\n",
    )
    checked, broken = module.check([doc])
    assert (checked, broken) == (0, [])


def test_code_fences_are_not_scanned(tmp_path):
    module = load_module()
    doc = write(
        tmp_path / "doc.md",
        "```bash\npython x.py --out ../nope.md\n```\n~~~\n[fake](missing.md)\n~~~\n[real](missing2.md)\n",
    )
    checked, broken = module.check([doc])
    assert checked == 1, "ссылка внутри блока кода не должна считаться"
    assert "missing2.md" in broken[0]


def test_main_returns_one_on_broken_link(tmp_path, capsys):
    module = load_module()
    write(tmp_path / "doc.md", "[нет](nope.md)\n")
    assert module.main([str(tmp_path / "doc.md")]) == 1
    assert "битых: 1" in capsys.readouterr().out


def test_main_returns_two_for_missing_input(capsys):
    module = load_module()
    assert module.main(["definitely/not/here.md"]) == 2
    assert "нет файла/каталога" in capsys.readouterr().out


def test_public_documents_have_no_broken_links():
    """Публичные документы репозитория: каждая относительная ссылка ведёт в файл."""
    module = load_module()
    targets = [module.REPO / p for p in module.DEFAULT_TARGETS if (module.REPO / p).is_file()]
    assert targets, "список публичных документов пуст — проверь DEFAULT_TARGETS"
    paths = []
    for target in targets:
        paths.extend(module.iter_markdown(target))
    checked, broken = module.check(paths)
    assert checked > 100, f"подозрительно мало ссылок: {checked}"
    assert broken == []
