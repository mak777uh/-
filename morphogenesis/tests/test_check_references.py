"""test_check_references.py — каждая ссылка References есть в индексе библиотеки.

Контракт: ссылка берётся из курированного индекса, а не из памяти. Тест держит
проверку честной: URL из References без строки в индексе — ошибка; ссылки вне
блока References не считаются; завершающая пунктуация и регистр хоста не ломают
сравнение; отсутствие блока — ошибка конфигурации, а не «всё хорошо».
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_references.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_references_under_test", SCRIPT)
    assert spec and spec.loader, f"не удалось загрузить {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = ROOT
    return module


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


PAPER = """# Paper

## 4. Results

См. источник https://doi.org/10.9999/outside — вне References не считается.

## References

- Mordvintsev et al. (2020). https://doi.org/10.23915/distill.00023
- Levin (2022). https://www.frontiersin.org/articles/10.3389/fnsys.2022.768201/full.
"""

INDEX = """# Index

| A1 | [Distill](https://doi.org/10.23915/distill.00023) |
| A6 | [TAME](https://www.frontiersin.org/articles/10.3389/fnsys.2022.768201/full) |
"""


def test_all_references_are_in_index(tmp_path):
    module = load_module()
    paper = write(tmp_path / "paper.md", PAPER)
    index = write(tmp_path / "index.md", INDEX)
    count, missing = module.check(paper, index)
    assert count == 2, "ссылка вне References не должна попадать в счёт"
    assert missing == []


def test_missing_reference_is_reported(tmp_path):
    module = load_module()
    paper = write(
        tmp_path / "paper.md",
        "## References\n\n- X (2026). https://doi.org/10.1000/unknown\n",
    )
    index = write(tmp_path / "index.md", INDEX)
    count, missing = module.check(paper, index)
    assert count == 1
    assert missing == ["https://doi.org/10.1000/unknown"]


def test_trailing_punctuation_and_host_case_are_ignored(tmp_path):
    module = load_module()
    paper = write(
        tmp_path / "paper.md",
        "## References\n\n- X (2026). https://DOI.org/10.23915/distill.00023.\n",
    )
    index = write(tmp_path / "index.md", "| a | https://doi.org/10.23915/distill.00023 |")
    _, missing = module.check(paper, index)
    assert missing == []


def test_missing_references_block_is_configuration_error(tmp_path, capsys):
    module = load_module()
    paper = write(tmp_path / "paper.md", "# Paper\n\nнет блока\n")
    index = write(tmp_path / "index.md", INDEX)
    assert module.main(["--paper", str(paper), "--index", str(index)]) == 2
    assert "нет блока" in capsys.readouterr().out


def test_main_codes(tmp_path):
    module = load_module()
    paper = write(tmp_path / "paper.md", PAPER)
    index = write(tmp_path / "index.md", INDEX)
    assert module.main(["--paper", str(paper), "--index", str(index)]) == 0
    bad = write(tmp_path / "bad.md", "## References\n\n- X https://doi.org/10.1/nope\n")
    assert module.main(["--paper", str(bad), "--index", str(index)]) == 1


def test_repository_manuscript_references_are_indexed():
    module = load_module()
    count, missing = module.check(ROOT / "manuscript" / "paper.md", ROOT / "library/publications/README.md")
    assert count >= 10, f"подозрительно мало ссылок в References: {count}"
    assert missing == []
