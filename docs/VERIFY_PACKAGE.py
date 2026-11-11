"""Verify package files without training or running the audit."""
from pathlib import Path
import hashlib, json
root = Path(__file__).resolve().parent
manifest = json.loads((root / "PACKAGE_MANIFEST.json").read_text())
for relative, expected in manifest["sha256_by_file"].items():
    path = root / relative
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError(f"Missing or changed file: {relative}")
assert len(list((root / manifest["primary_case_folder"]).glob("case_*.json"))) == 544
print(f"Verified {len(manifest['sha256_by_file'])} files; all 544 case records are present.")
