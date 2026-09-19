"""Leakage-safe data preparation, splitting, baselines, and evaluation."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "eda_uci_data" / "data" / "dropout_data.csv"
ARTIFACT_DIR = ROOT / "artifacts"
TABLE_DIR = ROOT / "tables"
SEED = 42
OUTREACH_CAPACITY = 0.20

CATEGORICAL_COLUMNS = [
    "marital_status",
    "application_mode",
    "course",
    "daytime_evening_attendance",
    "previous_qualification",
    "nacionality",
    "mothers_qualification",
    "fathers_qualification",
    "mothers_occupation",
    "fathers_occupation",
    "displaced",
    "educational_special_needs",
    "debtor",
    "tuition_fees_up_to_date",
    "gender",
    "scholarship_holder",
    "international",
]


@dataclass(frozen=True)
class DataSplits:
    train_ids: np.ndarray
    validation_ids: np.ndarray
    test_ids: np.ndarray


def set_global_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


def clean_column_name(column: str) -> str:
    return (
        column.strip()
        .replace("'", "")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "_")
        .replace(" ", "_")
        .lower()
    )


def load_primary_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load UCI data, preserve source row IDs, and apply the fixed binary target."""
    frame = pd.read_csv(path).rename(columns=clean_column_name)
    frame.insert(0, "source_row_id", np.arange(len(frame), dtype=int))
    frame = frame[frame["target"].isin(["Dropout", "Graduate"])].copy()
    frame["target"] = frame["target"].map({"Graduate": 0, "Dropout": 1}).astype(int)
    return frame.reset_index(drop=True)


def feature_columns(frame: pd.DataFrame, window: str = "first_semester") -> list[str]:
    """Return a pre-specified feature window; second-semester fields are never eligible."""
    excluded = {"source_row_id", "target"}
    columns = [
        column
        for column in frame.columns
        if column not in excluded and not column.startswith("curricular_units_2nd_sem")
    ]
    if window == "enrollment":
        columns = [
            column
            for column in columns
            if not column.startswith("curricular_units_1st_sem")
            and not column.startswith("first_semester_")
        ]
    elif window != "first_semester":
        raise ValueError("window must be 'enrollment' or 'first_semester'")
    return columns


def add_first_semester_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add leakage-safe derived features with explicit zero-denominator behavior."""
    result = frame.copy()
    enrolled = result["curricular_units_1st_sem_enrolled"]
    approved = result["curricular_units_1st_sem_approved"]
    evaluations = result["curricular_units_1st_sem_evaluations"]
    result["first_semester_pass_rate"] = np.divide(
        approved,
        enrolled,
        out=np.zeros(len(result), dtype=float),
        where=enrolled.to_numpy() > 0,
    )
    result["first_semester_no_enrollment"] = (enrolled == 0).astype(int)
    result["first_semester_no_evaluations"] = (evaluations == 0).astype(int)
    return result


def make_splits(
    frame: pd.DataFrame,
    seed: int = SEED,
    train_size: float = 0.70,
    validation_size: float = 0.15,
) -> DataSplits:
    """Create a 70/15/15 stratified split using stable source row IDs."""
    if not np.isclose(train_size + validation_size, 0.85):
        raise ValueError("this project pre-specifies a 70/15/15 split")
    train, remainder = train_test_split(
        frame,
        train_size=train_size,
        random_state=seed,
        stratify=frame["target"],
    )
    validation, test = train_test_split(
        remainder,
        train_size=validation_size / (1 - train_size),
        random_state=seed,
        stratify=remainder["target"],
    )
    return DataSplits(
        train_ids=train["source_row_id"].to_numpy(),
        validation_ids=validation["source_row_id"].to_numpy(),
        test_ids=test["source_row_id"].to_numpy(),
    )


def save_splits(splits: DataSplits, path: Path = ARTIFACT_DIR / "split_ids.csv") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for split_name, ids in (
        ("train", splits.train_ids),
        ("validation", splits.validation_ids),
        ("test", splits.test_ids),
    ):
        rows.extend({"source_row_id": int(row_id), "split": split_name} for row_id in ids)
    pd.DataFrame(rows).sort_values("source_row_id").to_csv(path, index=False)


def select_split(frame: pd.DataFrame, ids: np.ndarray) -> pd.DataFrame:
    indexed = frame.set_index("source_row_id", drop=False)
    return indexed.loc[ids].reset_index(drop=True)


def baseline_preprocessor(columns: list[str]) -> ColumnTransformer:
    categorical = [column for column in columns if column in CATEGORICAL_COLUMNS]
    numerical = [column for column in columns if column not in categorical]
    return ColumnTransformer(
        [
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
            (
                "numerical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numerical,
            ),
        ]
    )


def build_baselines(columns: list[str]) -> dict[str, Pipeline]:
    from xgboost import XGBClassifier

    def pipeline(model) -> Pipeline:
        return Pipeline([("preprocess", baseline_preprocessor(columns)), ("model", model)])

    return {
        "logistic_regression": pipeline(
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED)
        ),
        "decision_tree_depth_3": pipeline(
            DecisionTreeClassifier(max_depth=3, class_weight="balanced", random_state=SEED)
        ),
        "xgboost": pipeline(
            XGBClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                eval_metric="logloss",
                random_state=SEED,
                n_jobs=4,
            )
        ),
    }


def capacity_threshold(probabilities, capacity: float = OUTREACH_CAPACITY) -> float:
    """Return a deterministic threshold that flags at most the requested share.

    The threshold is chosen without labels. Ties at the boundary can make the flag
    rate smaller than the nominal capacity, which is preferable to exceeding a fixed
    outreach budget.
    """
    values = np.asarray(probabilities, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("probabilities must be a non-empty one-dimensional array")
    if not 0 < capacity < 1:
        raise ValueError("capacity must be between zero and one")
    n_flag = max(1, int(np.floor(values.size * capacity)))
    ordered = np.sort(values)[::-1]
    boundary = ordered[n_flag - 1]
    if int(np.sum(values >= boundary)) > n_flag:
        return float(np.nextafter(boundary, np.inf))
    return float(boundary)


def capacity_predictions(probabilities, capacity: float = OUTREACH_CAPACITY) -> tuple[np.ndarray, float]:
    """Select exactly the top-capacity cases with stable index-order tie breaking.

    The operating policy is cohort ranking, rather than a universal probability cutoff.
    The returned boundary is retained for auditing and approximate counterfactual search.
    """
    values = np.asarray(probabilities, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("probabilities must be a non-empty one-dimensional array")
    if not 0 < capacity < 1:
        raise ValueError("capacity must be between zero and one")
    n_flag = max(1, int(np.floor(values.size * capacity)))
    order = np.lexsort((np.arange(values.size), -values))
    predictions = np.zeros(values.size, dtype=int)
    predictions[order[:n_flag]] = 1
    return predictions, float(values[order[n_flag - 1]])


def expected_calibration_error(y_true, probabilities, n_bins: int = 10) -> float:
    """Compute equal-width expected calibration error."""
    truth = np.asarray(y_true, dtype=int)
    values = np.asarray(probabilities, dtype=float)
    if truth.shape != values.shape:
        raise ValueError("y_true and probabilities must have the same shape")
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.minimum(np.digitize(values, edges[1:-1]), n_bins - 1)
    error = 0.0
    for bin_id in range(n_bins):
        mask = bin_ids == bin_id
        if mask.any():
            error += mask.mean() * abs(truth[mask].mean() - values[mask].mean())
    return float(error)


def evaluate_predictions(y_true, predictions, probabilities) -> dict[str, object]:
    return {
        "balanced_accuracy": balanced_accuracy_score(y_true, predictions),
        "macro_f1": f1_score(y_true, predictions, average="macro"),
        "roc_auc": roc_auc_score(y_true, probabilities),
        "dropout_recall": recall_score(y_true, predictions, pos_label=1),
        "dropout_precision": precision_score(
            y_true, predictions, pos_label=1, zero_division=0
        ),
        "flag_rate": float(np.mean(np.asarray(predictions) == 1)),
        "brier_score": brier_score_loss(y_true, probabilities),
        "expected_calibration_error_10bin": expected_calibration_error(
            y_true, probabilities, n_bins=10
        ),
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
    }


def fit_and_evaluate(
    model,
    train,
    evaluation,
    columns: list[str],
    threshold: float | None = None,
) -> dict[str, object]:
    start = perf_counter()
    model.fit(train[columns], train["target"])
    fit_seconds = perf_counter() - start
    probabilities = model.predict_proba(evaluation[columns])[:, 1]
    if threshold is None:
        predictions, threshold = capacity_predictions(probabilities)
    else:
        predictions = (probabilities >= threshold).astype(int)
    metrics = evaluate_predictions(evaluation["target"], predictions, probabilities)
    metrics["threshold"] = float(threshold)
    metrics["fit_seconds"] = fit_seconds
    return metrics


def prepare_tfm_frame(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Represent coded categoricals explicitly while preserving feature names.

    Both candidate TFM libraries accept pandas frames. Marking administrative code
    columns as categorical prevents them from being interpreted as ordered quantities.
    """
    result = frame[columns].copy()
    for column in set(columns).intersection(CATEGORICAL_COLUMNS):
        result[column] = result[column].astype("category")
    return result


def build_tfm(name: str, columns: list[str], n_estimators: int = 4):
    """Build the selected TFM with a small, documented feasibility configuration."""
    if name == "tabicl":
        from tabicl import TabICLClassifier

        return TabICLClassifier(
            n_estimators=n_estimators,
            device="cpu",
            random_state=SEED,
            n_jobs=4,
            verbose=False,
        )
    raise ValueError("the frozen TFM name must be 'tabicl'")


def run_tfm_validation(
    candidates: tuple[str, ...] = ("tabicl",),
    window: str = "first_semester",
    n_estimators: int = 4,
) -> pd.DataFrame:
    """Run the pre-specified validation-only TFM feasibility gate.

    Model checkpoints may download on first use. This function deliberately never
    accesses the test labels and does not declare a winner automatically: the team must
    review validation metrics, runtime, determinism, and explanation compatibility.
    """
    set_global_seed()
    frame = add_first_semester_features(load_primary_data())
    columns = feature_columns(frame, window)
    splits = make_splits(frame)
    save_splits(splits)
    train = select_split(frame, splits.train_ids)
    validation = select_split(frame, splits.validation_ids)
    x_train = prepare_tfm_frame(train, columns)
    x_validation = prepare_tfm_frame(validation, columns)

    rows: list[dict[str, object]] = []
    for name in candidates:
        try:
            model = build_tfm(name, columns, n_estimators=n_estimators)
            start = perf_counter()
            model.fit(x_train, train["target"])
            fit_seconds = perf_counter() - start
            probabilities = model.predict_proba(x_validation)[:, 1]
            predictions, threshold = capacity_predictions(probabilities)
            repeat_probabilities = model.predict_proba(x_validation)[:, 1]
            metrics = evaluate_predictions(validation["target"], predictions, probabilities)
            rows.append(
                {
                    "model": name,
                    "status": "ok",
                    "split": "validation",
                    "n_estimators": n_estimators,
                    **metrics,
                    "threshold": threshold,
                    "fit_seconds": fit_seconds,
                    "repeat_prediction_max_abs_diff": float(
                        np.max(np.abs(probabilities - repeat_probabilities))
                    ),
                    "model_agnostic_probability_explainer": True,
                    "note": "",
                }
            )
        except (OSError, RuntimeError) as error:
            message = " ".join(str(error).split())[:300]
            rows.append(
                {
                    "model": name,
                    "status": "blocked",
                    "split": "validation",
                    "n_estimators": n_estimators,
                    "model_agnostic_probability_explainer": True,
                    "note": f"{type(error).__name__}: {message}",
                }
            )

    output = pd.DataFrame(rows)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(TABLE_DIR / "tfm_validation_metrics.csv", index=False)
    return output


def run_baseline_validation(window: str = "first_semester") -> pd.DataFrame:
    """Fit baselines on train and evaluate on validation—not on final test."""
    set_global_seed()
    frame = add_first_semester_features(load_primary_data())
    columns = feature_columns(frame, window)
    splits = make_splits(frame)
    save_splits(splits)
    train = select_split(frame, splits.train_ids)
    validation = select_split(frame, splits.validation_ids)
    rows = []
    for name, model in build_baselines(columns).items():
        metrics = fit_and_evaluate(model, train, validation, columns)
        rows.append({"model": name, "split": "validation", **metrics})
    output = pd.DataFrame(rows)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(TABLE_DIR / "baseline_validation_metrics.csv", index=False)
    metadata = {
        "seed": SEED,
        "feature_window": window,
        "n_features_before_encoding": len(columns),
        "target": "Dropout=1, Graduate=0; Enrolled excluded",
        "selection_rule": "TFM selection uses validation only; test remains untouched",
        "threshold_rule": (
            "validation-only capacity threshold; flag at most the top 20% highest-risk cases"
        ),
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return output
