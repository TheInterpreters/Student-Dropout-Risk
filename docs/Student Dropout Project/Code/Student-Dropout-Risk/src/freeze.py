"""Local, content-addressed freeze evidence without requiring a Git commit or tag."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def input_files(root: Path) -> list[Path]:
    files = [root / "requirements.txt", root / "artifacts" / "split_ids.csv",
             root / "eda_uci_data" / "data" / "dropout_data.csv"]
    for folder in ("src", "scripts", "forms", "config"):
        files.extend(p for p in (root / folder).rglob("*")
                     if p.is_file() and p.suffix in (".py", ".gs", ".json", ".csv")
                     and "__pycache__" not in p.parts
                     and not p.is_relative_to(root / "forms" / "out"))
    return sorted(set(files))


def create_snapshot(root: Path, destination: Path, checkpoint: Path, note: str) -> Path:
    if not note.strip():
        raise ValueError("record the incomplete checks and reason for using a local freeze")
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)
    destination.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for source in input_files(root):
        relative = source.relative_to(root)
        target = destination / "inputs" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        hashes[relative.as_posix()] = file_hash(target)
    frozen_checkpoint = destination / "checkpoint" / checkpoint.name
    frozen_checkpoint.parent.mkdir()
    shutil.copyfile(checkpoint, frozen_checkpoint)
    manifest = {
        "mode": "local_snapshot", "created_at": datetime.now(timezone.utc).isoformat(),
        "review_status": "not independently approved",
        "incomplete_checks_and_deviation": note,
        "files_sha256": hashes,
        "checkpoint": {"file": frozen_checkpoint.relative_to(destination).as_posix(),
                       "sha256": file_hash(frozen_checkpoint)},
    }
    path = destination / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    verify_snapshot(root, path)
    return path


def verify_snapshot(root: Path, manifest_path: Path) -> Path:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mode") != "local_snapshot" or not manifest.get("incomplete_checks_and_deviation", "").strip():
        raise ValueError("invalid local-freeze manifest or missing deviation record")
    actual = {p.relative_to(root).as_posix() for p in input_files(root)}
    if actual != set(manifest["files_sha256"]):
        raise ValueError("local-freeze input file set changed")
    for name, expected in manifest["files_sha256"].items():
        for base in (root, manifest_path.parent / "inputs"):
            path = base / name
            if not path.resolve().is_relative_to(base.resolve()) or file_hash(path) != expected:
                raise ValueError("local-freeze input changed: " + name)
    checkpoint = manifest_path.parent / manifest["checkpoint"]["file"]
    if not checkpoint.resolve().is_relative_to(manifest_path.parent.resolve()):
        raise ValueError("checkpoint must be inside the local snapshot")
    if file_hash(checkpoint) != manifest["checkpoint"]["sha256"]:
        raise ValueError("frozen checkpoint changed")
    return checkpoint
