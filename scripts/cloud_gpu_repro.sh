#!/usr/bin/env bash
# H-REPRO-9: повтор сида 42 на чужом GPU с контролем точности.
#
# Зачем: на нашей RTX 3070 (Ampere, TF32 есть) seed42 даёт struct_2 64/64, а при
# выключенном TF32 — struct_1 64/64. Если механизм верен, то на карте БЕЗ TF32
# (V100, Volta) класса не будет даже с флагом «включено», а на карте С TF32 (L4,
# Ada) он должен вернуться. Один скрипт, два режима, две карты — и вопрос закрыт
# без нашей машины.
#
# Использование (на инстансе, от пользователя с sudo/интернетом):
#
#   curl -fsSL https://raw.githubusercontent.com/mak777uh/-/main/scripts/cloud_gpu_repro.sh -o repro.sh
#   bash repro.sh tf32     # TF32 включён (по умолчанию; на Volta его нет — смотри вывод)
#   bash repro.sh fp32     # TF32 выключен (MORPH_TF32=0)
#
# Скрипт печатает блок FROM_CLOUD_JSON ... TO_CLOUD_JSON — его можно скопировать
# в чат целиком: там стек, sha256 весов и классы переписи.
set -euo pipefail

MODE="${1:-tf32}"
SEED="${SEED:-42}"
STEPS="${STEPS:-2000}"
SEEDS_COUNT="${SEEDS_COUNT:-0-63}"
WORK="${WORK:-$HOME/morphogenesis-repro}"
REPO_URL="${REPO_URL:-https://github.com/mak777uh/-.git}"
FAM="E02c_seeddec_init42_data${SEED}"

case "$MODE" in
  tf32) export MORPH_TF32=1 ;;
  fp32) export MORPH_TF32=0 ;;
  *) echo "режим должен быть tf32 или fp32, получено: $MODE" >&2; exit 2 ;;
esac

echo "=== режим: $MODE (MORPH_TF32=$MORPH_TF32), сид $SEED, шагов $STEPS ==="

if [ ! -d "$WORK/.git" ]; then
  echo "=== клонирую репозиторий в $WORK ==="
  git clone --depth 1 "$REPO_URL" "$WORK"
fi
cd "$WORK"
COMMIT="$(git rev-parse --short HEAD)"

echo "=== ставлю зависимости (torch 2.6.0: под него заморожен протокол) ==="
python3 -m pip install -q --upgrade pip || true
# Если облако не даёт поставить 2.6.0 (нет сети до PyPI, свой индекс, pinned
# образ), не падаем: работаем на том torch, что есть, и честно фиксируем версию в
# итоговом JSON — тогда сравнение остаётся валидным с оговоркой.
if ! python3 -m pip install -q "torch==2.6.0" numpy scipy tensorboard; then
  echo "!!! torch 2.6.0 не встал — использую предустановленный" >&2
  python3 -m pip install -q numpy scipy tensorboard || true
fi
python3 -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda)"

cd "$WORK/morphogenesis"

echo "=== обучение ==="
python3 -u e02c_seed_decomposition.py --init-seed "$SEED" --data-seed "$SEED" --steps "$STEPS"

echo "=== перепись ==="
python3 -u e02c_census.py \
  --seeds "$SEEDS_COUNT" --steps 2000 \
  --families "$FAM" --allow-missing-control \
  --out "../cloud_census_${MODE}.json" \
  --summary-out "../cloud_summary_${MODE}.json"

echo "=== сводка ==="
MODE="$MODE" COMMIT="$COMMIT" SEED="$SEED" python3 - <<'PY'
import hashlib, json, os, platform

mode = os.environ["MODE"]
seed = int(os.environ["SEED"])

import torch

ckpt = f"checkpoints/E02c_seeddec_init42_data{seed}/nca_final.pt"
h = hashlib.sha256()
with open(ckpt, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
        h.update(chunk)

summary = json.load(open(f"../cloud_summary_{mode}.json", encoding="utf-8"))
stats = summary.get("stats", {})
family = next((k for k in stats if k.startswith("E02c_seeddec")), None)

payload = {
    "kind": "cloud_gpu_repro",
    "mode": mode,
    "commit": os.environ["COMMIT"],
    "seed": seed,
    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no-cuda",
    "capability": list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else None,
    "torch": torch.__version__,
    "cuda": torch.version.cuda,
    "python": platform.python_version(),
    "tf32_cudnn": bool(torch.backends.cudnn.allow_tf32),
    "weights_sha256": h.hexdigest(),
    "family": family,
    "class_counts": stats.get(family, {}).get("frozen_class_counts"),
    "struct_2": stats.get(family, {}).get("struct_2"),
    "positive_control_present": summary.get("positive_control_present"),
}
print("FROM_CLOUD_JSON")
print(json.dumps(payload, ensure_ascii=False))
print("TO_CLOUD_JSON")
PY

echo "=== готово: скопируй блок FROM_CLOUD_JSON ... TO_CLOUD_JSON в чат ==="
