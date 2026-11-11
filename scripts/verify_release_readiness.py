"""Verify saved evidence and report assets without fitting models or opening the final test."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(manifest_path, base, field="files_sha256"):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    failures = []
    for name, expected in manifest[field].items():
        path = ROOT / name if Path(name).parts[0] in {"tables", "figures"} else Path(base) / name
        if not path.is_file():
            failures.append(f"missing: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        elif file_hash(path) != expected:
            failures.append(f"hash mismatch: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return failures


def main():
    checks = {}
    final_manifest = ROOT / "tables" / "final_test" / "manifest.json"
    checks["final_test_22_hashes"] = not verify_manifest(final_manifest, final_manifest.parent)
    lock = json.loads((ROOT / "artifacts" / "final_test.lock").read_text(encoding="utf-8"))
    checks["final_test_lock_completed"] = lock.get("status") == "completed" and lock.get("evaluation_cases") == 545

    cases = list((ROOT / "W1_analysis" / "03_Full_Audit" / "Cases").glob("case_*.json"))
    completion = json.loads((ROOT / "W1_analysis" / "05_Provenance" /
                             "full_audit_completion_validation.json").read_text(encoding="utf-8"))
    checks["w1_544_unique_cases"] = len(cases) == 544 and len({path.stem for path in cases}) == 544
    checks["w1_completion_record"] = completion.get("full_report_ready") is True and completion.get("job_return_code") == 0

    human_summary = json.loads((ROOT / "tables" / "human_study" / "summary.json").read_text(encoding="utf-8"))
    checks["human_study_50_balanced"] = (human_summary.get("included_participants") == 50 and
                                           human_summary.get("groups") == {"A": 25, "B": 25})
    human_manifest = ROOT / "tables" / "human_study" / "manifest.json"
    checks["human_aggregate_hashes"] = not verify_manifest(
        human_manifest, ROOT, field="aggregate_outputs_sha256")
    report_manifest = ROOT / "tables" / "report_ready" / "manifest.json"
    checks["report_asset_hashes"] = not verify_manifest(report_manifest, ROOT)
    demo = json.loads((ROOT / "figures" / "demo_card" / "demo_card_validation.json").read_text(encoding="utf-8"))
    checks["demo_card_validation_only"] = (
        demo.get("split") == "validation" and demo.get("test_split_accessed") is False
        and (ROOT / "figures" / "demo_card" / "demo_card_validation.png").is_file())
    demo_copy = ROOT / "figures" / "report_ready" / "demo_card_validation.png"
    checks["demo_card_matches_report_copy"] = (
        demo_copy.is_file()
        and file_hash(demo_copy) == file_hash(ROOT / "figures" / "demo_card" / "demo_card_validation.png"))

    page_path = ROOT / "interface" / "student_support_demo.html"
    page = page_path.read_text(encoding="utf-8") if page_path.is_file() else ""
    checks["interface_validation_only"] = "validation only" in page and "108/108 identical flags" in page

    sensitivity_path = ROOT / "tables" / "sensitivity" / "enrolled_summary.json"
    sensitivity = json.loads(sensitivity_path.read_text(encoding="utf-8")) if sensitivity_path.is_file() else {}
    checks["enrolled_sensitivity_validation_only"] = (
        sensitivity.get("test_split_accessed") is False and sensitivity.get("final_model_changed") is False)
    identity_path = ROOT / "artifacts" / "w1_refit_identity.json"
    identity = json.loads(identity_path.read_text(encoding="utf-8")) if identity_path.is_file() else {}
    checks["w1_refit_matches_frozen_on_validation"] = (
        identity.get("identical_within_tolerance") is True and identity.get("n_cases") == 544
        and identity.get("test_split_accessed") is False
        and identity.get("model_bundle_sha256") == lock.get("model_bundle_sha256"))

    # Qualitative coding is reported as a status, not a pass/fail gate, until the team completes it.
    coding_dir = ROOT / "data" / "human_study" / "coding"
    committed = ROOT / "tables" / "report_ready"
    if not (coding_dir / "theme_by_group_study.csv").is_file() and (
            committed / "human_study_theme_by_group.csv").is_file():
        # Clean clone: private coding files are absent; judge from the committed aggregate copies.
        coding_dir = None
    if coding_dir is None:
        coding_status = ("completed with measured inter-coder agreement"
                         if (committed / "human_study_agreement.csv").is_file()
                         else "completed in a single pass; inter-coder agreement not measured")
    elif not (coding_dir / "theme_by_group_study.csv").is_file():
        coding_status = "pending: assignments generated; coding not done"
    elif (coding_dir / "agreement_study.csv").is_file():
        coding_status = "completed with measured inter-coder agreement"
    else:
        coding_status = "completed in a single pass; inter-coder agreement not measured"

    tracked = subprocess.run(["git", "ls-files", "--", "*.xlsx", "*.xls", "*.ods", "data/human_study"],
                             cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    checks["private_responses_not_tracked"] = tracked == ""
    privacy = json.loads((ROOT / "artifacts" / "human_study_privacy_audit.json").read_text(encoding="utf-8"))
    checks["privacy_pattern_screen_passed"] = (
        privacy.get("status") == "pass" and not any(privacy.get("pattern_match_rows", {}).values()))
    codebook = (ROOT / "docs" / "QUALITATIVE_CODEBOOK.md").read_text(encoding="utf-8")
    checks["qualitative_codebook_ready"] = "unclear_other" in codebook and "20%" in codebook
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    checks["completion_documented"] = (
        "collection is complete" in (ROOT / "docs" / "HUMAN_STUDY_RESULTS.md").read_text(encoding="utf-8").lower()
        and "human study:" in readme and "all 50 assigned main participants" in readme)

    result = {"status": "pass" if all(checks.values()) else "fail", "checks": checks,
              "qualitative_coding": coding_status,
              "note": "Read-only evidence verification; no model fitting or final-test access."}
    destination = ROOT / "artifacts" / "release_readiness.json"
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
