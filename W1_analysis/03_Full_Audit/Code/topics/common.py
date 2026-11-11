"""Shared read-only inputs and student-level uncertainty for W1 saved analysis."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd

VARIANTS = {f"{family}+{terms}" for family in ("OLS", "Ridge", "Lasso")
            for terms in ("main", "pairs")}


def validate_coverage(ids, expected):
    if len(ids) != len(set(ids)) or len(expected) != len(set(expected)) or set(ids) != set(expected):
        raise ValueError("Saved cases must cover every expected validation ID exactly once; no sampling or mixing.")


def mean_interval(values, bootstrap=2000, seed=42):
    values = np.asarray(values, dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("Uncertainty calculation requires nonempty finite student-level values.")
    if bootstrap < 100:
        raise ValueError("Use at least 100 bootstrap resamples.")
    if len(values) == 1:
        return float(values.mean()), float('nan'), float('nan')
    rng = np.random.default_rng(seed)
    means = np.concatenate([values[rng.integers(0, len(values), size=(min(200, bootstrap-i), len(values)))].mean(axis=1)
                            for i in range(0, bootstrap, 200)])
    lower, upper = np.quantile(means, [.025, .975])
    return float(values.mean()), float(lower), float(upper)


def safe(value):
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if isinstance(value, np.generic):
        return safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(safe(value), indent=2, allow_nan=False) + '\n')


def find_cases(override=None):
    if override:
        candidates = [Path(override).expanduser()]
    else:
        bases = [Path.cwd(), *list(Path.cwd().parents)[:7], Path(__file__).resolve().parent,
                 *list(Path(__file__).resolve().parents)[:7]]
        suffixes = ['outputs/cases', 'W1_Noey_Enhanced/outputs/cases', '03_Full_Audit/Cases',
                    'Deliverables/Cloud_Audit_Current/project/W1_Noey_Enhanced/outputs/cases',
                    'Downloads/Student_Dropout_Full_Audit/03_Full_Audit/Cases']
        candidates = [base / suffix for base in bases for suffix in suffixes]
        pointer = Path('/workspace/student_dropout_runs/latest_run.txt')
        if pointer.is_file():
            run = Path(pointer.read_text().strip())
            metadata = json.loads((run / 'job.json').read_text())
            candidates.append(Path(metadata['code_root']) / 'W1_Noey_Enhanced/outputs/cases')
    for path in candidates:
        if (path / 'manifest.json').is_file() and len(list(path.glob('case_*.json'))) == 544:
            return path.resolve()
    raise ValueError("Need all 544 completed cases. Extract the full audit ZIP and pass --cases PATH/03_Full_Audit/Cases. No models will be fitted.")


@dataclass
class SavedAudit:
    records: list
    manifest: dict
    cases_path: Path
    predictions: pd.DataFrame
    warnings: dict
    fingerprints: dict


def load_completed(cases_path=None):
    folder = find_cases(cases_path)
    manifest = json.loads((folder / 'manifest.json').read_text())
    if manifest.get('split') != 'validation' or manifest.get('test_evaluated') is not False:
        raise ValueError("This extension only accepts the original validation audit.")
    expected = manifest['selected_source_row_ids']
    if len(expected) != 544:
        raise ValueError("Expected the complete original 544-student validation cohort.")
    records, fingerprints = [], {}
    for path in sorted(folder.glob('case_*.json')):
        raw = path.read_bytes()
        record = json.loads(raw)
        if path.name != f"case_{record['source_row_id']:05d}.json":
            raise ValueError("Case filename and source ID disagree.")
        records.append(record)
        fingerprints[path.name] = hashlib.sha256(raw).hexdigest()
    validate_coverage([r['source_row_id'] for r in records], expected)
    candidates = [folder.parent / 'actual_validation/actual_vs_model_validation.csv']
    candidates += [p / '02_Model_Evaluation/Reports/actual_vs_model_validation.csv' for p in folder.parents]
    prediction_file = next((p for p in candidates if p.is_file()), None)
    if prediction_file is None:
        raise ValueError("The saved prediction CSV is required to verify model probability identity. Use the complete audit ZIP.")
    predictions = pd.read_csv(prediction_file, float_precision='round_trip')
    if predictions.source_row_id.astype(int).tolist() != expected:
        raise ValueError("Prediction rows/order differ from the original validation manifest.")
    vector = predictions.predicted_dropout_probability.to_numpy(dtype='<f8')
    if hashlib.sha256(vector.tobytes()).hexdigest() != manifest['validation_probability_sha256']:
        raise ValueError("Saved probabilities differ from the recorded model; do not mix runs.")
    lookup = predictions.set_index('source_row_id')
    groups = None
    for record in records:
        if record['predicted_probability'] != lookup.loc[record['source_row_id'], 'predicted_dropout_probability']:
            raise ValueError("A case probability differs from its saved model vector.")
        if len(record['pairwise_reference_masking']) != 10:
            raise ValueError("Each case requires all ten saved pair probes.")
        group_names = [row['feature_group'] for row in record['baseline_group_contributions_all']]
        if len(group_names) != len(set(group_names)) or (groups is not None and set(group_names) != groups):
            raise ValueError("Inconsistent full grouped-SHAP coverage.")
        groups = set(group_names)
        surrogate = record['surrogate_comparison']
        if {r['variant'] for r in surrogate['summary']} != VARIANTS:
            raise ValueError("Every student requires all six recorded surrogate variants.")
        if (surrogate['train_pattern_count'], surrogate['holdout_pattern_count']) != (24, 8):
            raise ValueError("Original 24-training/8-holdout masking design is required.")
        details = pd.DataFrame(surrogate['holdout_predictions'])
        if len(details) != 48 or details.duplicated(['variant', 'pattern_index']).any():
            raise ValueError("Expected six variants on eight distinct held-out patterns.")
        pattern_sets = [set(details.loc[details.variant == variant, 'pattern_index']) for variant in VARIANTS]
        if len(pattern_sets[0]) != 8 or any(p != pattern_sets[0] for p in pattern_sets):
            raise ValueError("Variant comparisons require the same eight holdout masks for each student.")
        if any(int(index).bit_count() < 3 for index in pattern_sets[0]):
            raise ValueError("Holdout masks must be the recorded higher-order masking patterns.")
        if any(values.tabicl_probability.nunique() != 1 for _, values in details.groupby('pattern_index')):
            raise ValueError("Saved TabICL targets must agree across surrogate variants.")
        for variant in VARIANTS:
            rows = details.loc[details.variant == variant]
            target = next(r for r in surrogate['summary'] if r['variant'] == variant)['holdout_mae']
            actual = (rows.surrogate_probability-rows.tabicl_probability).abs().mean()
            if len(rows) != 8 or not np.isclose(actual, target, atol=1e-12, rtol=1e-10):
                raise ValueError("Recorded held-out MAE cannot be reproduced from saved predictions.")
    warning_candidates = [p / 'recorded_fit_warnings.json' for p in folder.parents]
    warning_candidates += [p / '05_Provenance/recorded_fit_warnings.json' for p in folder.parents]
    warning_file = next((p for p in warning_candidates if p.is_file()), None)
    warnings = json.loads(warning_file.read_text()) if warning_file else {'status': 'not supplied; fit warnings not verified'}
    return SavedAudit(records, manifest, folder, predictions, warnings, fingerprints)
