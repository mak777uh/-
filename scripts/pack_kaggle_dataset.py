"""Собрать каталог для Kaggle Dataset из portable-пакета E02b.

Kaggle Dataset хранит файлы плоско, а portable-пакет — дерево каталогов
(`morphogenesis/checkpoints/...`). Поэтому пакет упаковывается в один архив
`e02b-portable.zip`, а notebook распаковывает его в `/kaggle/working`.

Запуск (из корня репозитория):

    python scripts/pack_kaggle_dataset.py \
        --package dist/e02b-portable \
        --out dist/kaggle-dataset

Результат:
    dist/kaggle-dataset/dataset-metadata.json
    dist/kaggle-dataset/e02b-portable.zip

Затем:
    kaggle datasets create -p dist/kaggle-dataset
    kaggle datasets version -p dist/kaggle-dataset -m "..."
"""
import argparse
import hashlib
import json
import os
import shutil
import zipfile

SKIP_DIRS = {"__pycache__", ".pytest_cache"}
SKIP_FILES = {"dataset-metadata.json", "verify_report.json"}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--package", default="dist/e02b-portable")
    ap.add_argument("--out", default="dist/kaggle-dataset")
    ap.add_argument(
        "--metadata",
        default="kaggle/dataset-metadata.json",
        help="dataset-metadata.json (slug владельца Kaggle, не GitHub)",
    )
    args = ap.parse_args(argv)

    package = os.path.abspath(args.package)
    out = os.path.abspath(args.out)
    if not os.path.isdir(package):
        raise SystemExit(f"нет portable-пакета: {package}")
    if not os.path.isfile(os.path.join(package, "portable_manifest.json")):
        raise SystemExit(f"в пакете нет portable_manifest.json: {package}")

    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    meta = json.load(open(args.metadata, encoding="utf-8"))
    meta_path = os.path.join(out, "dataset-metadata.json")
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    zip_path = os.path.join(out, "e02b-portable.zip")
    n_files = 0
    n_bytes = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(package):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(files):
                if name in SKIP_FILES or name.endswith(".pyc"):
                    continue
                src = os.path.join(root, name)
                rel = os.path.relpath(src, package)
                zf.write(src, rel)
                n_files += 1
                n_bytes += os.path.getsize(src)

    print(f"[kaggle-pack] dataset id: {meta.get('id')}")
    print(f"[kaggle-pack] zip: {zip_path}")
    print(f"[kaggle-pack] files={n_files} unpacked_bytes={n_bytes} zip_bytes={os.path.getsize(zip_path)}")
    print(f"[kaggle-pack] zip_sha256={sha256_file(zip_path)}")
    print(f"[kaggle-pack] metadata: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
