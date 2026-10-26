# Один вход для проверок: `make verify` — гейт перед отправкой.
PY ?= .venv/Scripts/python.exe

.PHONY: verify test claims contract repro

verify:
	$(PY) scripts/verify.py

test:
	cd morphogenesis && $(PY) -m pytest -q tests

claims:
	$(PY) scripts/claims_lint.py

contract:
	$(PY) scripts/lab.py validate

repro:
	$(PY) run_tests.py --quick

# здоровье лаборатории одной командой: гейты + CI + очереди + серии + ресурсы
health:
	python scripts/lab_health.py --full --github

