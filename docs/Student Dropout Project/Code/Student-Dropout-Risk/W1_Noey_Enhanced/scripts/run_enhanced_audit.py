"""W1 validation-only, restartable explanation audit for Student-Dropout-Risk.

This independent *full-validation-cohort* supplementary audit does not call the final-test runner, train on
test records or score test labels. It reads the common source CSV/split map only to
select the prescribed train and validation partitions. It never modifies the final-test
lock, previous W1 output or existing team result tables.

Install this W1_Noey_Enhanced/ folder at repository root, then run on Python 3.12:
  python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --check
  python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --run
  python W1_Noey_Enhanced/scripts/run_enhanced_audit.py --report

--run can be restarted. It saves each completed validation case atomically and skips
already completed cases only if their provenance matches the original run.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import sys
from time import monotonic
import traceback

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SCRIPT_VERSION = "3.2.0-verified-inference-cache"
SELECTED_SPLIT = "validation"  # NEVER change to test
EXPECTED_CASES = 544  # every validation student, not a sampled 20-case panel
CHECKPOINT_NAME = "tabicl-classifier-v2-20260212.ckpt"
# Expected checkpoint digest supplied in the original package's installer.
EXPECTED_CHECKPOINT_SHA256 = "bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_ready(value):
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, (np.ndarray, tuple, list)):
        return [json_ready(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def atomic_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(json.dumps(json_ready(value), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    os.replace(tmp, path)


def audit_paths(repo: Path) -> dict:
    return {
        "lock": repo / "artifacts" / "final_test.lock",
        "surrogate": repo / "W1_Noey_Enhanced" / "scripts" / "surrogate_comparison.py",
        "simulator": repo / "W1_Noey_Enhanced" / "scripts" / "student_improvement_simulation.py",
        "protocol": repo / "config" / "evaluation_protocol.json",
        "split": repo / "artifacts" / "split_ids.csv",
        "data": repo / "eda_uci_data" / "data" / "dropout_data.csv",
        "runner": repo / "scripts" / "run_explanation_audit.py",
        "explain": repo / "src" / "explanations.py",
        "modeling": repo / "src" / "modeling.py",
        "evaluation": repo / "src" / "evaluation.py",
        "population": repo / "W1_Noey_Enhanced/scripts/development_population.py",
        "actual_audit": repo / "W1_Noey_Enhanced/scripts/actual_data_audit.py",
        "artifacts": repo / "W1_Noey_Enhanced" / "outputs" / "cases",
        "tables": repo / "W1_Noey_Enhanced" / "outputs" / "tables",
        "figures": repo / "W1_Noey_Enhanced" / "outputs" / "figures",
    }


def preflight(repo: Path):
    paths = audit_paths(repo)
    must_exist = ["lock", "protocol", "split", "data", "runner", "explain", "modeling", "evaluation", "surrogate", "simulator", "population", "actual_audit"]
    missing = [str(paths[key]) for key in must_exist if not paths[key].is_file()]
    if missing:
        raise FileNotFoundError("Missing required files in cloned repository:\n  " + "\n  ".join(missing))
    if sys.version_info[:2] != (3, 12):
        print(f"WARNING: repository pins Python 3.12; current version is {sys.version.split()[0]}")
    protocol = json.loads(paths["protocol"].read_text(encoding="utf-8"))
    # Do not alter the frozen team's original 20-case settings. This *supplementary*
    # protocol explicitly extends the population to every validation student.
    if protocol["faithfulness"]["cases"] != 20 or protocol["stability"]["cases"] != 20:
        raise ValueError("Frozen original protocol differs from the documented 20-case baseline")
    enhanced_config = json.loads((repo / "W1_Noey_Enhanced" / "config" / "full_cohort_protocol.json").read_text(encoding="utf-8"))
    if enhanced_config.get("scope") != "all_validation_rows" or enhanced_config.get("expected_validation_rows") != EXPECTED_CASES:
        raise ValueError("Enhanced scope configuration does not match expected entire validation cohort")
    if protocol["shap"]["display_top_k"] != 5 or protocol["shap"]["background_size"] != 25:
        raise ValueError("Unexpected SHAP configuration: manual review of enhanced protocol needed")
    if protocol["model"]["name"] != "tabicl":
        raise ValueError("Frozen model is not TabICL; stop and document the discrepancy.")
    if protocol["faithfulness"]["case_selection_split"] != "validation":
        raise ValueError("W1 must use validation cases only.")
    if protocol["stability"]["case_selection_split"] != "validation":
        raise ValueError("W1 stability must use validation only.")
    source = paths["runner"].read_text(encoding="utf-8")
    if 'development_frames("validation")' not in source:
        raise ValueError("Original runner changed; independent audit review required.")
    signatures = {k: sha256(paths[k]) for k in must_exist}
    signatures["enhanced_runner"] = sha256(Path(__file__).resolve())
    signatures["enhanced_scope"] = sha256(repo / "W1_Noey_Enhanced" / "config" / "full_cohort_protocol.json")
    print("W1 preflight: original 20-case protocol is untouched; new full-cohort add-on selects EVERY validation row.")
    print("Final-test lock present (will not be edited). SHA256:", signatures["lock"])
    print("Protocol SHA256:", signatures["protocol"])
    print("Use --run ONLY with the original frozen Python environment; no test commands are needed.")
    return paths, protocol, signatures


def source_rankings(case: pd.Series, background: pd.DataFrame, columns, groups,
                    predict, shap_settings, seeds: list[int]):
    from src.explanations import aggregate_shap_by_group, permutation_shap_values
    vals = []
    ranks = []
    for seed in seeds:
        shap_result = permutation_shap_values(
            predict, background, case.to_frame().T,
            max_evals=shap_settings["max_evals"], seed=seed,
        )
        arr = np.asarray(shap_result.values)
        if arr.shape != (1, len(columns)) or not np.isfinite(arr).all():
            raise ValueError(f"Invalid SHAP shape/values at seed {seed}: {arr.shape}")
        table = aggregate_shap_by_group(arr[0], columns, groups)
        rank = table["feature_group"].tolist()
        if not np.isfinite(table["signed_shap"].to_numpy(float)).all():
            raise ValueError("Non-finite grouped SHAP contributions")
        ranks.append(rank)
        vals.append(table)
    return ranks, vals


def rank_correlation(rankings: list[list[str]]) -> float | None:
    if len(rankings) < 2:
        return None
    baseline = rankings[0]
    if any(set(x) != set(baseline) for x in rankings):
        raise ValueError("Ranking groups differ across explanations")
    corr = [float(spearmanr(
        [left.index(g) for g in baseline],
        [right.index(g) for g in baseline],
    ).statistic) for left, right in combinations(rankings, 2)]
    return float(np.mean(corr)) if corr else None


def _predict_one(predict, row: pd.Series) -> float:
    """Return the dropout probability with strict shape/range checks."""
    probs = np.asarray(predict(row.to_frame().T), dtype=float)
    if probs.shape != (1, 2) or not np.isfinite(probs).all():
        raise ValueError(f"Prediction must have finite (1, 2) probabilities, got {probs.shape}")
    p = float(probs[0, 1])
    if not 0 <= p <= 1:
        raise ValueError("Invalid dropout probability")
    return p


def mask_group_union(case: pd.Series, selected_groups, groups, references,
                     recompute=None) -> pd.Series:
    """Mask one or several *complete semantic groups* to training references.

    This is a model reliance probe, NOT a feasible student intervention.
    """
    if recompute is None:
        from src.explanations import recompute_first_semester_features
        recompute = recompute_first_semester_features
    masked = case.copy()
    for group in selected_groups:
        if group not in groups:
            raise KeyError(f"Unknown semantic group: {group}")
        for member in groups[group]:
            if member not in masked.index or member not in references.index:
                raise KeyError(f"Missing group member: {member}")
            masked[member] = references[member]
    return recompute(masked.to_frame().T).iloc[0]


def pair_deletion_audit(predict, case: pd.Series, groups, references, top_groups,
                        recompute=None) -> list[dict]:
    """Probe all pairwise combinations of top-five semantic groups.

    I_AB=f(mask_AB)-f(mask_A)-f(mask_B)+f(original) is the nonadditive
    response under THIS reference-masking intervention, not SHAP interaction
    values, a causal effect, or a proof of a biological/educational interaction.
    """
    names = list(dict.fromkeys(top_groups))
    if len(names) < 2:
        return []
    original = _predict_one(predict, case)
    singly = {
        group: _predict_one(predict, mask_group_union(case, [group], groups,
                             references, recompute)) for group in names
    }
    rows = []
    for left, right in combinations(names, 2):
        joint = _predict_one(predict, mask_group_union(case, [left, right], groups,
                            references, recompute))
        delta_left = singly[left] - original
        delta_right = singly[right] - original
        delta_joint = joint - original
        interaction = joint - singly[left] - singly[right] + original
        rows.append({
            "feature_group_a": left, "feature_group_b": right,
            "original_probability": original,
            "masked_a_probability": singly[left],
            "masked_b_probability": singly[right],
            "masked_both_probability": joint,
            "delta_a": delta_left, "delta_b": delta_right,
            "delta_joint": delta_joint,
            "nonadditive_effect": interaction,
            "abs_nonadditive_effect": abs(interaction),
            "joint_change_larger_than_each_single":
                bool(abs(delta_joint) > max(abs(delta_left), abs(delta_right)) + 1e-12),
            "interpretation_scope": "model reference-masking response only",
        })
    return sorted(rows, key=lambda item: (-item["abs_nonadditive_effect"],
                         item["feature_group_a"], item["feature_group_b"]))


def model_recourse_scenarios(predict, case, cohort_probabilities, case_position,
                             capacity=0.20):
    """Enumerate *all* plausible status-resolution scenarios, even failures.

    No actual behavioral/intervention success or causal claim is implied.
    """
    from src.modeling import capacity_predictions
    orig_flags, _ = capacity_predictions(cohort_probabilities, capacity=capacity)
    original = float(cohort_probabilities[case_position])
    if int(orig_flags[case_position]) != 1:
        return [{"status": "not_flagged", "changed_features": "", "n_changes": 0,
                 "original_probability": original, "scenario_probability": original,
                 "delta_probability": 0.0, "flagged_after": False,
                 "capacity_rank_after": None, "scenario_kind": "not_applicable"}]
    allowed = {"debtor": 0, "tuition_fees_up_to_date": 1}
    mutable = [key for key,target in allowed.items()
               if key in case.index and int(case[key]) != target]
    if not mutable:
        return [{"status": "no_change_available", "changed_features": "", "n_changes": 0,
                 "original_probability": original, "scenario_probability": original,
                 "delta_probability": 0.0, "flagged_after": True,
                 "capacity_rank_after": None, "scenario_kind": "no_available_status_resolution"}]
    cohort = np.asarray(cohort_probabilities, dtype=float)
    out = []
    for k in range(1, len(mutable)+1):
        for names in combinations(mutable, k):
            altered = case.copy()
            for name in names:
                altered[name] = allowed[name]
            p = _predict_one(predict, altered)
            new_scores = cohort.copy()
            new_scores[case_position] = p
            new_flags, _ = capacity_predictions(new_scores, capacity=capacity)
            rank = int(np.flatnonzero(np.lexsort((np.arange(len(new_scores)), -new_scores))
                                      == case_position)[0] + 1)
            success = not bool(new_flags[case_position])
            out.append({"status": "leaves_flagged_group" if success else "still_flagged",
                        "changed_features": ", ".join(names), "n_changes": k,
                        "original_probability": original, "scenario_probability": p,
                        "delta_probability": p-original, "flagged_after": not success,
                        "capacity_rank_after": rank,
                        "scenario_kind": "combined_status_resolution" if k>1 else "single_status_resolution"})
    return out


def support_options_from_grouped_shap(group_table, case):
    """Non-prescriptive referral topics for a human adviser, not recourse estimates."""
    top = group_table.head(5).set_index("feature_group")
    positives = set(top.index[top["signed_shap"].astype(float) > 0])
    suggestions = []
    if positives & {"first_semester_progress", "first_semester_participation"}:
        suggestions.append("Review first-semester academic evidence and discuss optional tutoring/advising")
    if "tuition_fees_up_to_date" in positives and "tuition_fees_up_to_date" in case.index and int(case["tuition_fees_up_to_date"]) == 0:
        suggestions.append("Verify tuition status; discuss financial support or payment-plan information")
    if "debtor" in positives and "debtor" in case.index and int(case["debtor"]) == 1:
        suggestions.append("Verify debt record; offer financial counselling/referral")
    if not suggestions:
        suggestions.append("Human adviser reviews context and asks the student about needs; no automated intervention inferred")
    return suggestions


def eligible_grade_perturbations(predict, case: pd.Series, train: pd.DataFrame,
                                 candidate_columns, proposals=10, seed=42,
                                 fraction_of_training_sd=0.01,
                                 probability_tolerance=0.01) -> pd.DataFrame:
    """Try ten small, range-clipped grade changes as *robustness probes* only.

    Each proposal is a separate deterministic random draw. It is not an actual
    student intervention, and a proposal is accepted only if it genuinely changes
    the input without changing model dropout probability by > 0.01. Historical
    grade records must never be treated as mutable recourse actions.
    """
    from src.explanations import recompute_first_semester_features
    if not candidate_columns:
        raise ValueError("Need one or more measured grade columns")
    rng = np.random.default_rng(seed)
    original_p = _predict_one(predict, case)
    rows = []
    for i in range(proposals):
        feature = candidate_columns[i % len(candidate_columns)]
        train_values = pd.to_numeric(train[feature], errors="raise").to_numpy(float)
        scale = fraction_of_training_sd * float(np.std(train_values))
        original = float(case[feature])
        updated = float(np.clip(original + rng.normal(0.0, scale),
                                train_values.min(), train_values.max()))
        altered = case.copy()
        altered[feature] = updated
        altered = recompute_first_semester_features(altered.to_frame().T).iloc[0]
        actual = float(altered[feature])
        prob = _predict_one(predict, altered)
        difference = abs(prob - original_p)
        effective = abs(actual - original) > 1e-10
        rows.append({
            "proposal": i + 1, "feature": feature,
            "original_value": original, "perturbed_value": actual,
            "original_probability": original_p, "perturbed_probability": prob,
            "absolute_probability_change": difference,
            "effective_change": effective,
            "accepted": bool(effective and difference <= probability_tolerance),
            "grade_only_sensitivity_probe": True,
        })
    return pd.DataFrame(rows)


def compute_one_case(*, pos: int, train: pd.DataFrame, validation: pd.DataFrame,
                     xtrain: pd.DataFrame, xval: pd.DataFrame, columns, groups,
                     background, references, model, probabilities, flags,
                     protocol, baseline_rank=None, baseline_table=None):
    from src.explanations import (
        deletion_curve, recompute_first_semester_features, top_k_overlap,
    )
    from src.modeling import prepare_tfm_frame, capacity_predictions

    def predict(frame):
        restored = recompute_first_semester_features(frame)
        return model.predict_proba(prepare_tfm_frame(restored, columns))

    seed_base = 42
    settings = protocol["shap"]
    runs = protocol["stability"]["runs_per_case"]
    case = xval.iloc[pos]
    sid = int(validation.iloc[pos]["source_row_id"])
    if baseline_rank is None:
        rankings, tabs = source_rankings(case, background, columns, groups,
                                        predict, settings, [seed_base])
        baseline_rank, baseline_table = rankings[0], tabs[0]
    top_five = baseline_rank[:settings["display_top_k"]]

    curve = deletion_curve(
        predict, case, top_five, references,
        random_repetitions=protocol["faithfulness"]["random_deletion_repetitions"],
        seed=seed_base, feature_groups=groups,
    )
    area = float(curve.attrs["area_between_curves"])
    if not np.isfinite(area):
        raise ValueError("Non-finite faithfulness area")

    # Pairs are inspected among the baseline local SHAP top-five semantic groups.
    # The nonadditive effect is conditional on reference masking: NOT interaction SHAP.
    paired = pair_deletion_audit(predict, case, groups, references, top_five)
    if len(paired) != 10 or any(not np.isfinite(v["nonadditive_effect"]) for v in paired):
        raise ValueError("Expected exactly 10 finite pairwise reference-masking results")
    suggested_support = support_options_from_grouped_shap(baseline_table, case)

    # W1.2 optional post-hoc SURROGATE comparisons: OLS, Ridge, Lasso,
    # each with/without pair terms. No changes to TabICL/final test are made.
    from surrogate_comparison import run_masking_surrogates
    surrogate = run_masking_surrogates(
        predict, case, groups, references, top_five, mask_group_union)

    # An explicit exploratory amendment: perturb only measured continuous grades;
    # exclude integer counts, protected/discrete variables and cohort-level economics.
    # These are sensitivity probes, NOT feasible post-semester interventions.
    continuous = [c for c in ("admission_grade", "previous_qualification_grade",
                               "curricular_units_1st_sem_grade") if c in columns]
    if len(continuous) < 2:
        raise ValueError("Too few domain-valid continuous perturbation candidates")
    perturbs = eligible_grade_perturbations(
        predict, case, train, continuous, proposals=runs, seed=seed_base,
        fraction_of_training_sd=protocol["stability"]["continuous_perturbation_fraction"],
        probability_tolerance=protocol["stability"]["prediction_tolerance_absolute_probability"],
    )
    accepted = perturbs.loc[perturbs["accepted"]].head(runs)
    stability = []
    raw_ranks = {}
    for mode in ["seed", "background", "perturbation"]:
        mode_ranks = []
        for i in range(runs):
            bg, changed, seed = background, case, seed_base
            if mode == "seed":
                seed = seed_base + i
            elif mode == "background":
                bg = xtrain.sample(n=settings["background_size"], random_state=seed_base+i)
            else:
                if i >= len(accepted):
                    break
                row = accepted.iloc[i]
                changed = case.copy()
                changed[row["feature"]] = row["perturbed_value"]
                changed = recompute_first_semester_features(changed.to_frame().T).iloc[0]
            if mode == "seed" and i == 0:
                rank = baseline_rank
            elif mode == "background" and i == 0:
                rank = baseline_rank
            else:
                rank = source_rankings(changed, bg, columns, groups,
                                       predict, settings, [seed])[0][0]
            mode_ranks.append(rank)
        overlap = float(top_k_overlap(mode_ranks, k=5)) if len(mode_ranks) >= 2 else None
        stability.append({
            "source_row_id": sid, "variation": mode, "valid_runs": len(mode_ranks),
            "top_5_overlap": overlap,
            "rank_spearman": rank_correlation(mode_ranks),
            "low_stability": bool(overlap < .80) if overlap is not None else None,
            "status": "ok" if len(mode_ranks) >= 2 else "insufficient accepted perturbations",
        })
        raw_ranks[mode] = [r[:5] for r in mode_ranks]

    # Pair-effect rankings re-tested under accepted continuous-grade perturbations.
    # This does NOT test pair stability under seed/background (masking itself is deterministic).
    pair_effect_rankings = [
        [tuple(sorted((r["feature_group_a"], r["feature_group_b"]))) for r in paired]
    ]
    pair_repeats = []
    for _, sample in accepted.iterrows():
        altered = case.copy()
        altered[sample["feature"]] = sample["perturbed_value"]
        from src.explanations import recompute_first_semester_features
        altered = recompute_first_semester_features(altered.to_frame().T).iloc[0]
        effect = pair_deletion_audit(predict, altered, groups, references, top_five)
        pair_effect_rankings.append([
            tuple(sorted((r["feature_group_a"], r["feature_group_b"]))) for r in effect
        ])
        pair_repeats.append({
            "feature_perturbed": sample["feature"],
            "top_pair": " + ".join(pair_effect_rankings[-1][0]),
            "max_pairwise_nonadditivity": effect[0]["abs_nonadditive_effect"],
        })
    pair_top3_overlap = None
    if len(pair_effect_rankings) >= 2:
        pair_sets = [set(p[:3]) for p in pair_effect_rankings]
        pair_top3_overlap = float(np.mean([
            len(left & right) / 3 for left, right in combinations(pair_sets, 2)
        ]))

    recourse_scenarios = model_recourse_scenarios(
        predict, case, probabilities, int(pos), capacity=0.20)

    # Additional feature-first numerical demonstrations for EVERY validation student.
    # These are input-sensitivity scenarios, not claims of feasible grade improvements.
    from student_improvement_simulation import proposal_scenarios
    improvement = []
    cohort = np.asarray(probabilities, dtype=float)
    for label, altered, kind in proposal_scenarios(case, recompute_first_semester_features):
        updated_p = float(cohort[pos]) if label == "Original profile" else _predict_one(predict, altered)
        changed_cohort = cohort.copy()
        changed_cohort[int(pos)] = updated_p
        updated_flags, _ = capacity_predictions(changed_cohort, capacity=0.20)
        index_order = np.lexsort((np.arange(len(changed_cohort)), -changed_cohort))
        rank = int(np.flatnonzero(index_order == int(pos))[0] + 1)
        improvement.append({
            "scenario": label, "category": kind,
            "original_probability": float(cohort[pos]),
            "scenario_probability": updated_p,
            "change_probability_points": 100 * (updated_p - float(cohort[pos])),
            "flagged_before": int(flags[pos]),
            "flagged_after": int(updated_flags[int(pos)]),
            "cohort_rank_after": rank,
            "original_grade": float(case.get("curricular_units_1st_sem_grade", float("nan"))),
            "new_grade": float(altered.get("curricular_units_1st_sem_grade", float("nan"))),
            "original_approved_units": int(case.get("curricular_units_1st_sem_approved", 0)),
            "new_approved_units": int(altered.get("curricular_units_1st_sem_approved", 0)),
            "original_tuition_paid": int(case.get("tuition_fees_up_to_date", 0)),
            "new_tuition_paid": int(altered.get("tuition_fees_up_to_date", 0)),
            "original_debtor": int(case.get("debtor", 0)),
            "new_debtor": int(altered.get("debtor", 0)),
            "interpretation": "model input sensitivity, not measured real-world intervention efficacy",
        })
    recourse = []
    if int(flags[pos]) != 1:
        recourse = [{"source_row_id": sid, "status": "not_flagged",
                     "n_changes": None, "changed_features": None,
                     "dropout_probability": None, "capacity_rank": None,
                     "capacity_boundary": None}]
    else:
        successes = [r for r in recourse_scenarios if r["status"] == "leaves_flagged_group"]
        if not successes:
            recourse = [{"source_row_id": sid, "status": "no_recourse",
                         "n_changes": None, "changed_features": None,
                         "dropout_probability": None, "capacity_rank": None,
                         "capacity_boundary": None}]
        else:
            for row in successes:
                recourse.append({"source_row_id": sid, "status": "recourse_found",
                                 "n_changes": row["n_changes"],
                                 "changed_features": row["changed_features"],
                                 "dropout_probability": row["scenario_probability"],
                                 "capacity_rank": row["capacity_rank_after"],
                                 "capacity_boundary": None})
    curve.insert(0, "source_row_id", sid)
    return {
        "source_row_id": sid,
        "validation_position": int(pos),
        "predicted_probability": float(probabilities[pos]),
        "flagged": int(flags[pos]),
        "faithfulness_area": area,
        "baseline_top_five_groups": top_five,
        "baseline_group_contributions": baseline_table.head(5).to_dict("records"),
        "baseline_group_contributions_all": baseline_table.to_dict("records"),
        "curve": curve.to_dict("records"),
        "stability": stability,
        "top_five_rankings": raw_ranks,
        "recourse": recourse,
        "perturbations": perturbs.assign(source_row_id=sid).to_dict("records"),
        "pairwise_reference_masking": paired,
        "surrogate_comparison": surrogate,
        "pair_top3_overlap_under_accepted_perturbations": pair_top3_overlap,
        "pair_stability_repeats": pair_repeats,
        "recourse_scenarios": recourse_scenarios,
        "individual_combined_improvement_scenarios": improvement,
        "support_topics_for_human_review": suggested_support,
        "perturbation_columns_audited": continuous,
    }


def bootstrap_interval(areas, n_boot=2000, seed=42):
    x = np.asarray(areas, dtype=float)
    if not len(x) or not np.isfinite(x).all():
        return None
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), size=(n_boot, len(x)))].mean(axis=1)
    return {"n_cases": int(len(x)), "mean_area": float(x.mean()),
            "ci_lower_95": float(np.quantile(means, .025)),
            "ci_upper_95": float(np.quantile(means, .975))}


def load_cases(artifacts: Path):
    cases = []
    for fp in sorted(artifacts.glob("case_*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        if not isinstance(data.get("source_row_id"), int):
            raise ValueError(f"Malformed saved case {fp}")
        cases.append(data)
    ids = [d["source_row_id"] for d in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source row IDs in saved audit case files")
    return cases


def report(paths, allow_partial=False):
    a, t, f = paths["artifacts"], paths["tables"], paths["figures"]
    manifest_path = a / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("First run --run to generate the case-by-case audit evidence")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = load_cases(a)
    requested_ids = manifest["selected_source_row_ids"]
    if not set(d["source_row_id"] for d in cases).issubset(set(requested_ids)):
        raise ValueError("Saved cases contain IDs outside the protocol-selected validation panel")
    complete = len(cases) == EXPECTED_CASES and set(d["source_row_id"] for d in cases) == set(requested_ids)
    if not complete and not allow_partial:
        raise RuntimeError(f"Only {len(cases)}/{EXPECTED_CASES} cases saved. Re-run --run to resume, or use --report-partial for an explicitly incomplete preview.")
    if not cases:
        raise ValueError("No completed validation cases yet; a partial report needs at least one saved case")
    current_lock_sha = sha256(paths["lock"])
    if current_lock_sha != manifest["hashes"]["lock"]:
        raise RuntimeError("CRITICAL: final-test lock hash changed; STOP, do not overwrite or rerun final-test")
    t.mkdir(parents=True, exist_ok=True)
    f.mkdir(parents=True, exist_ok=True)
    faith = pd.DataFrame([{"source_row_id": x["source_row_id"],
                           "area_between_curves": x["faithfulness_area"]} for x in cases])
    stability = pd.DataFrame([r for x in cases for r in x["stability"]])
    recourse = pd.DataFrame([r for x in cases for r in x["recourse"]])
    perturbations = pd.DataFrame([r for x in cases for r in x["perturbations"]])
    curves = pd.DataFrame([r for x in cases for r in x["curve"]])
    ranked = pd.DataFrame([{
        "source_row_id": x["source_row_id"], "flagged": x["flagged"],
        "baseline_top_five": " | ".join(x["baseline_top_five_groups"]),
    } for x in cases])
    # W1.1/W1.2: retain every group's local SHAP value per audited student.
    # Average |SHAP| is descriptive across the entire validation cohort, not causal importance.
    shap_rows = []
    top_five_sets = {x["source_row_id"]: set(x["baseline_top_five_groups"]) for x in cases}
    for x in cases:
        if "baseline_group_contributions_all" not in x:
            raise ValueError("Old case format lacks full local SHAP groups; rerun/reconcile, do not invent W1.2 results")
        for item in x["baseline_group_contributions_all"]:
            shap_rows.append({
                "source_row_id": x["source_row_id"],
                "flagged": x["flagged"],
                "feature_group": item["feature_group"],
                "members": item["members"],
                "signed_shap": float(item["signed_shap"]),
                "absolute_group_shap": float(item["absolute_group_shap"]),
                "in_top_five": int(item["feature_group"] in top_five_sets[x["source_row_id"]]),
            })
    shap_detail = pd.DataFrame(shap_rows)
    if shap_detail.groupby("source_row_id")["feature_group"].nunique().nunique() != 1:
        raise ValueError("Cases have inconsistent SHAP semantic-feature-group coverage")
    local_summary = shap_detail.groupby("feature_group", as_index=False).agg(
        n_cases=("source_row_id", "nunique"),
        mean_absolute_group_shap=("absolute_group_shap", "mean"),
        median_absolute_group_shap=("absolute_group_shap", "median"),
        mean_signed_group_shap=("signed_shap", "mean"),
        top_five_frequency=("in_top_five", "mean"),
    ).sort_values("mean_absolute_group_shap", ascending=False, ignore_index=True)
    # W1.2: 10 pairwise probes per student; W1.3 pair-rank robustness.
    if any("pairwise_reference_masking" not in x or "recourse_scenarios" not in x for x in cases):
        raise ValueError("Old non-pair audit case outputs cannot be used as enhanced evidence")
    pairs = pd.DataFrame([
        {"source_row_id": x["source_row_id"], "flagged": x["flagged"], **r}
        for x in cases for r in x["pairwise_reference_masking"]
    ])
    if len(pairs) != 10 * len(cases):
        raise ValueError("Each case must have exactly 10 pairwise reference-masking probes")
    if not np.isfinite(pairs["nonadditive_effect"].to_numpy(float)).all():
        raise ValueError("Non-finite pairwise nonadditive effects")
    pair_summary = pairs.groupby(["feature_group_a", "feature_group_b"], as_index=False).agg(
        cases_observed=("source_row_id", "nunique"),
        mean_absolute_nonadditive_effect=("abs_nonadditive_effect", "mean"),
        mean_signed_nonadditive_effect=("nonadditive_effect", "mean"),
        mean_absolute_joint_probability_change=("delta_joint", lambda s: float(s.abs().mean())),
        joint_exceeds_single_fraction=("joint_change_larger_than_each_single", "mean"),
    ).sort_values("mean_absolute_nonadditive_effect", ascending=False, ignore_index=True)
    pair_stability = pd.DataFrame([{
        "source_row_id": x["source_row_id"],
        "n_pair_rankings": 1 + len(x.get("pair_stability_repeats", [])),
        "top3_pair_overlap": x["pair_top3_overlap_under_accepted_perturbations"],
        "status": "ok" if x["pair_top3_overlap_under_accepted_perturbations"] is not None else "insufficient accepted perturbations",
    } for x in cases])
    recourse_scenarios = pd.DataFrame([
        {"source_row_id": x["source_row_id"], **r}
        for x in cases for r in x["recourse_scenarios"]
    ])
    if any("individual_combined_improvement_scenarios" not in x for x in cases):
        raise ValueError("Improvement scenario rows missing: do not mix old cases with the new full-cohort output")
    improvement_scenarios = pd.DataFrame([
        {"source_row_id": x["source_row_id"], **r}
        for x in cases for r in x["individual_combined_improvement_scenarios"]
    ])
    # Surrogate comparison is about mimicking TabICL on held-out mask patterns,
    # not predicting actual dropout, proving SHAP accuracy, or finding causality.
    helper_dir = str((paths["artifacts"].parents[1] / "scripts").resolve())
    if helper_dir not in sys.path:
        sys.path.insert(0, helper_dir)
    from surrogate_comparison import aggregate_surrogate_comparisons
    surrogate_by_case, surrogate_heldout, surrogate_overall = aggregate_surrogate_comparisons(cases)
    support_topics = pd.DataFrame([
        {"source_row_id": x["source_row_id"], "support_topic": suggestion,
         "role": "human-adviser discussion only; not tested intervention"}
        for x in cases for suggestion in x["support_topics_for_human_review"]
    ])
    for name, df in [
        ("pairwise_reference_masking_by_case_validation", pairs),
        ("pairwise_reference_masking_summary_validation", pair_summary),
        ("pair_rank_stability_validation", pair_stability),
        ("recourse_all_scenarios_validation", recourse_scenarios),
        ("individual_and_combined_improvement_scenarios_validation", improvement_scenarios),
        ("human_support_topics_validation", support_topics),
        ("surrogate_six_variants_by_case_validation", surrogate_by_case),
        ("surrogate_six_variants_heldout_patterns_validation", surrogate_heldout),
        ("surrogate_six_variants_overall_validation", surrogate_overall),
        ("faithfulness_validation", faith), ("faithfulness_curves_validation", curves),
        ("stability_validation", stability), ("recourse_validation", recourse),
        ("perturbations_validation", perturbations), ("baseline_rankings_validation", ranked),
        ("w1_local_shap_by_case_validation", shap_detail),
        ("w1_local_shap_summary_validation", local_summary),
    ]:
        df.to_csv(t / (name + ".csv"), index=False)

    interval = bootstrap_interval(faith["area_between_curves"].values)
    summary = {
        "split": "validation", "n_cases": len(cases), "expected_cases": EXPECTED_CASES,
        "model_provenance": manifest.get("model_provenance"),
        "full_audit_completed": complete, "test_evaluated": False,
        "faithfulness": interval,
        "w1_local_shap_top_five_by_mean_absolute": local_summary.head(5)[
            ["feature_group", "mean_absolute_group_shap", "top_five_frequency"]
        ].to_dict("records"),
        "faithfulness_positive_cases": int((faith["area_between_curves"] > 0).sum()),
        "stability": {},
        "recourse": {
            "n_flagged_cases": int(sum(x["flagged"] for x in cases)),
            "n_cases_with_recourse": int(recourse.loc[recourse.status.eq("recourse_found"), "source_row_id"].nunique()),
            "n_flagged_without_recourse": int(recourse.loc[recourse.status.eq("no_recourse"), "source_row_id"].nunique()),
        },
        "pairwise_reference_masking": {
            "n_pairs_evaluated": int(len(pairs)),
            "n_unique_pairs": int(len(pair_summary)),
            "mean_absolute_nonadditive_effect": float(pairs["abs_nonadditive_effect"].mean()),
            "largest_mean_absolute_effect_pairs": pair_summary.head(5).to_dict("records"),
            "pair_top3_stability_cases_with_two_or_more_rankings": int(pair_stability["top3_pair_overlap"].notna().sum()),
            "mean_top3_pair_rank_overlap": float(pair_stability["top3_pair_overlap"].mean()) if pair_stability["top3_pair_overlap"].notna().any() else None,
        },
        "improvement_scenarios": {
            "n_scenarios": int(len(improvement_scenarios)),
            "n_cases": int(improvement_scenarios["source_row_id"].nunique()),
            "n_flagged_cases_with_simulated_change": int(improvement_scenarios.loc[
                (improvement_scenarios["flagged_before"] == 1) &
                (improvement_scenarios["scenario"] != "Original profile"), "source_row_id"].nunique()),
            "interpretation": "input-sensitivity scenarios only; historical grade changes are not future interventions",
        },
        "recourse_scenarios": {
            "all_scenarios_count": int(len(recourse_scenarios)),
            "combined_scenarios_count": int(recourse_scenarios["scenario_kind"].eq("combined_status_resolution").sum()),
            "successful_combined_scenarios_count": int((recourse_scenarios["scenario_kind"].eq("combined_status_resolution") & recourse_scenarios["status"].eq("leaves_flagged_group")).sum()),
        },
        "surrogate_comparison": {
            "selection_metric": "lowest pooled holdout MAE vs unchanged TabICL on held-out masking patterns",
            "best_fit_surrogate_variant": str(surrogate_overall.iloc[0]["variant"]),
            "best_pooled_holdout_mae": float(surrogate_overall.iloc[0]["pooled_holdout_mae"]),
            "comparison": surrogate_overall.to_dict("records"),
            "limits": "Not an explanation-quality certification; masks may be off-manifold; full validation cohort comparison is descriptive; no causal or human-outcome claims",
        },
        "warnings": [
            "Linear/Ridge/Lasso are explanatory post-hoc surrogates, not alternative student-dropout prediction models.",
            "Surrogate fidelity is scored on eight higher-order masking patterns held out within each validation case; this measures one kind of local approximation fidelity, not explanation truth.",
            "Ridge/Lasso penalties are chosen by inner training-fold CV only; holdout masking patterns are not used for alpha selection.",
            "Pairwise masking nonadditivity is NOT SHAP interaction values and is NOT a causal interaction.",
            "The top-five selection may change under alternative SHAP seeds/backgrounds; pair results are selection-conditional.",
        "Academic grade/credit input changes are retrospective sensitivity tests, not achievable after first-semester support or causal benefits.",
            "Pair probes may represent off-manifold student feature combinations.",
            "Perturbation stability for pair effects checks up to ten grade-only probes; it is exploratory and not the original broader perturbation population.",
            "Ranked deletion is a model reliance stress test, not causal attribution.",
            "Training-reference masking can create off-manifold student profiles.",
            "The add-on restricts continuous perturbations to measured grade variables and range-clips them, but this cannot guarantee joint real-world plausibility.",
            "Recourse concerns a 20% cohort-ranking policy and only debtor/tuition resolutions; it does not establish feasibility or real-world impact.",
            "This validation audit does not replace human-study or protected-group fairness evidence.",
        ],
    }
    for mode, part in stability.groupby("variation"):
        ok = part.loc[part["top_5_overlap"].notna()]
        summary["stability"][mode] = {
            "cases_with_pairwise_overlap": int(len(ok)),
            "mean_top_5_overlap": float(ok["top_5_overlap"].mean()) if len(ok) else None,
            "cases_below_0_80": int((ok["top_5_overlap"] < .80).sum()),
            "cases_with_insufficient_runs": int(part["top_5_overlap"].isna().sum()),
            "mean_spearman": float(ok["rank_spearman"].mean()) if len(ok) else None,
        }
    atomic_json(t / "summary.json", summary)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    grouped = curves.groupby("features_deleted").mean(numeric_only=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(grouped.index, grouped["ranked_absolute_probability_change"], marker="o", label="SHAP-ranked deletion")
    ax.plot(grouped.index, grouped["random_absolute_probability_change_mean"], marker="o", label="Mean random deletion")
    ax.set(title="W1: Deletion faithfulness — validation cases", xlabel="Semantic groups deleted",
           ylabel="Absolute change in model dropout probability")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f / "deletion_faithfulness_validation.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for mode, group in stability.groupby("variation"):
        ax.scatter(group["source_row_id"], group["top_5_overlap"], label=mode)
    ax.axhline(.80, ls="--", label="0.80 warning threshold")
    ax.set(title="W1: Explanation stability — validation cases", xlabel="Validation source-row ID",
           ylabel="Mean pairwise top-five overlap", ylim=(0, 1.05))
    ax.legend()
    fig.tight_layout()
    fig.savefig(f / "stability_validation.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    top_groups = local_summary.head(10).iloc[::-1]
    ax.barh(top_groups["feature_group"], top_groups["mean_absolute_group_shap"])
    ax.set(title="W1.2: Average absolute grouped SHAP across audited validation cases",
           xlabel="Mean |grouped SHAP| in model dropout-probability units")
    fig.tight_layout()
    fig.savefig(f / "local_shap_importance_validation.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    top_pairs = pair_summary.head(8).copy().iloc[::-1]
    labels = (top_pairs["feature_group_a"] + " + " + top_pairs["feature_group_b"]).str.slice(0, 73)
    ax.barh(labels, top_pairs["mean_absolute_nonadditive_effect"])
    ax.set(title="W1.2: Exploratory paired-group reference-masking nonadditivity",
           xlabel="Mean absolute nonadditive probability response across audited cases")
    fig.tight_layout()
    fig.savefig(f / "pairwise_reference_masking_validation.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    order = surrogate_overall.iloc[::-1]
    ax.barh(order["variant"], order["pooled_holdout_mae"])
    ax.set(title="W1.2: Surrogate fidelity to frozen TabICL on withheld masks",
           xlabel="Mean absolute probability error (lower = more faithful surrogate)")
    fig.tight_layout()
    fig.savefig(f / "surrogate_six_variants_holdout_mae_validation.png", dpi=160)
    plt.close(fig)

    lower = interval["ci_lower_95"] if interval else None
    if interval is None:
        faith_text = "Unavailable"
    else:
        faith_text = f"Mean ranked-minus-random area = {interval['mean_area']:.5f}; 95% bootstrap interval [{interval['ci_lower_95']:.5f}, {interval['ci_upper_95']:.5f}]."
    faith_interpretation = (
        "The mean area is positive and its case-level bootstrap interval excludes zero; this supports reliance on the ranked groups under this masking test."
        if lower is not None and lower > 0 else
        "The interval does not establish that ranked masking changes predictions more than random masking on average."
    )
    stab_lines = []
    for mode in ["seed", "background", "perturbation"]:
        v = summary["stability"].get(mode)
        if v:
            avg = "not available" if v["mean_top_5_overlap"] is None else f'{v["mean_top_5_overlap"]:.3f}'
            stab_lines.append(f"- {mode}: mean overlap {avg}; {v['cases_below_0_80']} below 0.80; {v['cases_with_insufficient_runs']} insufficient.")
    shap_bullets = "\n".join(
        f"- **{item['feature_group']}**: mean |grouped SHAP| = {item['mean_absolute_group_shap']:.4f}; "
        f"in top five for {item['top_five_frequency']:.0%} of audited cases."
        for item in summary["w1_local_shap_top_five_by_mean_absolute"]
    )
    pair_bullets = "\n".join(
        f"- **{v['feature_group_a']} + {v['feature_group_b']}**: mean absolute nonadditivity "
        f"{v['mean_absolute_nonadditive_effect']:.4f}, across {v['cases_observed']} audited cases."
        for v in summary["pairwise_reference_masking"]["largest_mean_absolute_effect_pairs"]
    )
    surrogate_lines = "\n".join(
        f"- **{r['variant']}**: held-out MAE = {r['pooled_holdout_mae']:.5f}; "
        f"mean nonzero terms = {r['mean_nonzero_terms']:.1f}; "
        f"out-of-range forecast share = {r['mean_out_of_range_fraction']:.1%}."
        for r in summary["surrogate_comparison"]["comparison"]
    )
    body = f"""# W1 Noey — Full Validation Explanation Audit ({'COMPLETE' if complete else 'PARTIAL'})

**Evidence date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  
**Validation cases:** {len(cases)}/{EXPECTED_CASES}; **test partition:** not evaluated.  
**Final-test lock:** unchanged and checked against the audit manifest.  
**Important:** These are validation-only explanation-quality diagnostics. They do not change final-test results or the frozen predictive model.

## Actual observations and predictive comparison

The audit cases are all 544 held-out validation observations. The 2,541 training rows supply fitting and explanation references only; they are excluded from audit-case counts and predictive evaluation. Actual-versus-model predictions, confusion matrix, ROC-AUC, Brier score, calibration error, capacity precision/recall and balanced accuracy are saved separately in `outputs/actual_validation/`. Outreach flags follow the fixed top-20% policy; they are not a universal 0.5 classification rule. Predictive accuracy and explanation fidelity answer different questions.

Model origin: `{manifest.get('model_provenance', {}).get('origin', 'not recorded')}`. The original private fitted-model/freeze bundle was not supplied. A refit using the recorded settings and verified checkpoint must not be described as loading that original serialized model.

## W1.1 — Case selection and local explanations

This {'completed audit includes' if complete else 'PARTIAL run currently includes'} {len(cases)} of the {EXPECTED_CASES} eligible validation cases. The configured full run selects every case rather than a 20-case sample. Original feature values, SHAP values and group summaries are saved at case level. Signed grouped SHAP indicates direction of the model's probability contribution relative to the SHAP background, not the cause of dropout.

## W1.2 — Which features influence predictions? (local SHAP and deletion check)

**Mean absolute grouped SHAP on the {'full 544-case validation cohort' if complete else 'PARTIAL available validation cases only'} (not a causal claim):**

{shap_bullets}

The repository also has a *separate* global permutation-importance result on 100 sampled validation rows (`tables/grouped_permutation_importance_validation.csv`). Do not conflate that ROC-AUC-loss metric with grouped SHAP values (probability units). Use both to triangulate model reliance and inspect disagreements.

**Faithfulness: SHAP-ranked vs. random feature deletion**

{faith_text}

{faith_interpretation} Positive areas among cases: {summary['faithfulness_positive_cases']}/{len(cases)}. The conclusion concerns reliance under training-reference masking, not causality or actual student interventions.

**Exploratory pairwise feature-group masking (not SHAP interaction values)**

For each case, the 10 pairs among its local top-five groups are masked jointly and separately. The nonadditive model response is `p(mask A+B) - p(mask A) - p(mask B) + p(original)`; a nonzero value indicates that joint masking differs from the sum of single masking effects under the selected reference values. It does **not** prove a causal interaction. It can depend on correlated features and off-manifold combinations.

{pair_bullets}

Among the audited cases, mean absolute nonadditive response is {summary['pairwise_reference_masking']['mean_absolute_nonadditive_effect']:.4f} probability units. These are descriptive exploratory findings, not pre-specified confirmatory outcomes. Joint change magnitude and signed direction are also saved case by case.

**Exploratory six-surrogate comparison: with/without pair terms and with/without regularization**

For each student, 32 patterns of masking the locally top-five groups are scored using the *unchanged* TabICL model. Six surrogate variants (ordinary least squares, Ridge, Lasso; main effects only or main + 10 pair terms) approximate these 32 model outputs. The fit uses 24 patterns and independently scores eight held-out higher-order masks. Ridge/Lasso penalty selection uses three-fold CV **inside** the 24 fitting patterns. Coefficient regularization is not performed on or used to change TabICL.

{surrogate_lines}

**Lowest held-out masking-pattern MAE on this {'completed cohort' if complete else 'partial case subset'}:** {summary['surrogate_comparison']['best_fit_surrogate_variant']}. This means it most faithfully approximated TabICL *for this particular masking test*, NOT that it is the best human explanation, a causal model, or a superior student-dropout predictor. Evaluate parsimony, out-of-range values and stability of pair importance as well. The comparison is exploratory and was added after the original final evaluation; it cannot retroactively establish the initial protocol gate.

## W1.3 — Explanation stability

{chr(10).join(stab_lines)}

The 0.80 threshold is a pre-specified warning heuristic, not proof of explanation validity. Seed, background and perturbation results must be discussed separately; cases with fewer than two accepted perturbation explanations are insufficient, not passes.

**Exploratory pair-rank robustness:** {summary['pairwise_reference_masking']['pair_top3_stability_cases_with_two_or_more_rankings']}/{len(cases)} cases had at least one accepted grade perturbation to compare their top-three joint-masking rankings. Mean overlap across eligible cases: {summary['pairwise_reference_masking']['mean_top3_pair_rank_overlap']}. This is NOT full interaction-SHAP stability and must not be generalized to all perturbations or settings.

## W1.4 — Model-level recourse and possible support

Flagged validation cases: {summary['recourse']['n_flagged_cases']}; cases with at least one model-level recourse candidate: {summary['recourse']['n_cases_with_recourse']}; flagged cases with no candidate under the allowed changes: {summary['recourse']['n_flagged_without_recourse']}.

Only administrative debt/tuition-status resolutions are examined, individually and together where applicable, with the top-20% cohort ranking recalculated. Across all selected cases, {summary['recourse_scenarios']['combined_scenarios_count']} combined-status scenarios were evaluated; {summary['recourse_scenarios']['successful_combined_scenarios_count']} resulted in leaving the flagged set in this model. This is a hypothetical model response, not a promise that a real student can make the change or avoid dropping out. Every scenario (including unsuccessful ones) is saved and identified explicitly.

**Permissible support interpretation:** If the model identifies debt or overdue tuition status, a student-support officer could *verify the record* and offer financial aid advice, payment-plan information or a referral to the appropriate service. If the explanation highlights academic progress, the officer can consider tutoring/advising, but this is **not a tested counterfactual** here: recorded grades are historical, not mutable. SHAP is not a causal intervention selector. Do not advise a student to manipulate records merely to avoid a model flag.

## W1.5 — Can we trust the explanations? Limitations and reviewer follow-up

- The OLS/Ridge/Lasso comparison uses locally approximated TabICL probabilities for masked variants of the **same validation case**. Good surrogate fidelity does not validate feature causality, true outcome accuracy or human comprehension.
- Lasso may drop correlated/interacting terms while Ridge distributes weight across them; coefficients are scale- and masking-dependent. Compare the no-penalty OLS baseline explicitly, and do not use Lasso to delete model features.
- Interaction analysis is a reference-masking test, not formal SHAP interaction values, causal identification or an intervention effect. The trained model is unchanged and the pairwise investigation was added after the original final evaluation.
- Pairs are conditionally selected from each student's baseline top five; all possible feature pairs are NOT tested, and importance of an unselected pair cannot be ruled out.
- Deleting feature groups using median/mode replacements may produce implausible combinations.
- Grade-only perturbations may generate small fractional grade values; these are range-clipped numerical sensitivity probes, not feasible student actions. The original broad count perturbations are not repeated under this add-on.
- Top-five overlap does not measure direction, size or causality of SHAP contributions.
- Local SHAP contributions are relative to 25 sampled training-background rows; changes in reference distribution, correlations, semantic grouping or model calibration may change them.
- This supplementary validation-only audit followed the 2 Nov amendment and the completed final test. Do not describe it as an earlier passed freeze gate.
- The 544 validation cases are the entire validation partition, but the study is still from one source dataset and not externally validated.
- W1 does not assess real human comprehension, usefulness, causal interventions or deployment safety.
- The original full audit was omitted in the 2 November accelerated workflow. This file records a **separate subsequent validation-only analysis**, not retroactive evidence that the earlier audit passed.

## Review status

{'Complete computational outputs generated; independent human/team review still needed.' if complete else 'Incomplete: DO NOT PRESENT AS A FULL AUDIT. Continue with --run.'}

## Source files

All audit outputs reside only in `W1_Noey_Enhanced/outputs/`: `tables/` has local SHAP, deletion, stability, pairwise reference-masking, all recourse scenarios and summary JSON; `figures/` has five charts; `cases/` has the provenance manifest and 544 case-level JSON records. Original Yolanda-produced source/results files are unchanged.
"""
    out = t / ("W1_COMPLETE_REPORT.md" if complete else "W1_PARTIAL_PREVIEW.md")
    out.write_text(body, encoding="utf-8")
    print(f"{'FULL' if complete else 'PARTIAL'} audit: {len(cases)}/{EXPECTED_CASES} cases. Review: {out}")
    print(json.dumps(json_ready(summary), indent=2))
    return complete


def verified_checkpoint(checkpoint=None):
    """Retrieve the named official checkpoint and enforce the supplied digest."""
    if checkpoint is None:
        from huggingface_hub import hf_hub_download
        checkpoint = hf_hub_download(repo_id="jingang/TabICL", filename=CHECKPOINT_NAME)
    checkpoint = Path(checkpoint).resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Model checkpoint not found: {checkpoint}")
    digest = sha256(checkpoint)
    if digest != EXPECTED_CHECKPOINT_SHA256:
        raise ValueError("Checkpoint differs from the package's expected SHA256; do not run or substitute a different model")
    return checkpoint, digest


def validate_cache_agreement(reference, cached, tolerance=1e-4, check_flags=True):
    """Bound FP32 inference differences; this does not assert bitwise identity.

    1e-4 probability = 0.01 percentage points, 100x smaller than the frozen
    prediction-preserving perturbation tolerance (0.01 probability).
    """
    from src.modeling import capacity_predictions
    a, b = np.asarray(reference, dtype=float), np.asarray(cached, dtype=float)
    if a.ndim != 1 or a.shape != b.shape or not a.size:
        raise ValueError("Cache comparison requires aligned nonempty probability vectors")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any((a < 0) | (a > 1) | (b < 0) | (b > 1)):
        raise ValueError("Invalid cache-comparison probabilities")
    error = float(np.max(np.abs(a - b)))
    flags_equal = bool(np.array_equal(capacity_predictions(a)[0], capacity_predictions(b)[0]))
    if error > tolerance or (check_flags and not flags_equal):
        raise ValueError("Inference cache changes probabilities or outreach flags beyond the declared numerical agreement policy")
    return {"n_predictions": len(a), "absolute_probability_tolerance": tolerance,
            "maximum_absolute_probability_difference": error,
            "outreach_flags_equal": flags_equal, "flags_required_equal": check_flags,
            "bitwise_identical": bool(np.array_equal(a, b))}


def run(repo, paths, protocol, signatures, max_new_cases=None,
        comparison_only=False, checkpoint=None, inference_cache=False):
    # Import only after checking the repository and final lock. No test datasets/results are imported.
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    helper_dir = str((repo / "W1_Noey_Enhanced" / "scripts").resolve())
    if helper_dir not in sys.path:
        sys.path.insert(0, helper_dir)
    from importlib.metadata import version
    from development_population import load_population
    from actual_data_audit import data_audit, compare_actual_outcomes
    from src.explanations import (semantic_feature_groups, training_reference_values)
    from src.modeling import build_tfm, capacity_predictions, prepare_tfm_frame

    artifact_dir = paths["artifacts"]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = artifact_dir / "manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing["hashes"] != signatures or existing["version"] != SCRIPT_VERSION:
            raise RuntimeError("Repo inputs / lock / script changed since earlier audit. Stop; reconcile before resuming.")
        selected_ids = existing["selected_source_row_ids"]
    else:
        selected_ids = None

    print("Loading training and VALIDATION splits. The held-out test split will not be scored.", flush=True)
    frames, columns = load_population(repo)
    train, validation = frames["train"], frames["validation"]
    actual_dir = repo / "W1_Noey_Enhanced/outputs/actual_validation"
    data_audit({"validation": validation}, columns, actual_dir, root=repo)
    xtrain, xval = prepare_tfm_frame(train, columns), prepare_tfm_frame(validation, columns)
    if version("tabicl") != protocol["model"]["version"]:
        raise ValueError("Installed TabICL version differs from protocol")
    model_path, checkpoint_digest = verified_checkpoint(checkpoint)
    model_provenance = {
        "origin": "refit_on_original_training_rows_with_frozen_settings",
        "original_saved_fitted_model_loaded": False,
        "checkpoint_name": CHECKPOINT_NAME, "checkpoint_sha256": checkpoint_digest,
        "checkpoint_digest_source": "expected SHA256 in supplied package installer",
        "versions": {p: version(p) for p in ("tabicl", "torch", "numpy", "pandas", "scikit-learn", "shap")},
        "training_rows": len(train), "evaluation_rows": len(validation),
        "test_evaluated": False,
        "inference_cache": "kv" if inference_cache else "none",
        "limitation": "The private original fitted-model/freeze bundle was not supplied; this is a reproducible refit, not verified identity with that serialized model.",
    }
    if selected_ids is not None and existing.get("model_provenance") != model_provenance:
        raise RuntimeError("Model checkpoint/runtime identity changed; do not mix audit cases")
    print("Refitting TabICL on training only using recorded settings; not loading the original private fitted-model bundle.", flush=True)
    model = build_tfm(protocol["model"]["name"], columns,
                      n_estimators=protocol["model"]["n_estimators"])
    model.set_params(model_path=str(model_path), allow_auto_download=False)
    model.fit(xtrain, train["target"])
    if not np.array_equal(model.classes_, [0, 1]):
        raise ValueError("Unexpected model class order; dropout must be probability column 1")
    probabilities = np.asarray(model.predict_proba(xval))[:, 1]
    if not np.isfinite(probabilities).all() or np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("Invalid validation probabilities")
    if inference_cache:
        from sklearn.base import clone
        from surrogate_comparison import fixed_mask_holdout
        print("Checking supported KV inference cache against the uncached model on ALL 544 validation rows and 32 masked probes.", flush=True)
        cached_model = clone(model).set_params(kv_cache=True)
        cached_model.fit(xtrain, train["target"])
        cached_probabilities = np.asarray(cached_model.predict_proba(xval))[:, 1]
        tolerance = min(1e-4, protocol["stability"]["prediction_tolerance_absolute_probability"] / 100)
        agreement = validate_cache_agreement(probabilities, cached_probabilities, tolerance)
        cache_groups = semantic_feature_groups(columns)
        cache_refs = training_reference_values(train, columns)
        names = list(cache_groups)[:5]
        masks, _, _ = fixed_mask_holdout()
        probes = pd.DataFrame([
            mask_group_union(xval.iloc[0], [g for g, bit in zip(names, bits) if bit], cache_groups, cache_refs)
            for bits in masks
        ])
        probes = prepare_tfm_frame(probes, columns)
        masked_agreement = validate_cache_agreement(
            np.asarray(model.predict_proba(probes))[:, 1],
            np.asarray(cached_model.predict_proba(probes))[:, 1],
            tolerance, check_flags=False)
        atomic_json(actual_dir / "inference_cache_agreement.json", {
            "validation": agreement, "masked_probes": masked_agreement,
            "explanation": "Runtime caching only; same checkpoint, training rows and model hyperparameters. Small FP32 differences are bounded and disclosed; existing uncached case outputs must not be mixed.",
        })
        # Retain the uncached predictive comparison as the empirical reference.
        # Case explanations consistently use the separately identified cached runtime.
        baseline_performance = compare_actual_outcomes({"validation": validation}, {"validation": probabilities}, actual_dir)
        atomic_json(actual_dir / "uncached_actual_vs_model_summary.json", baseline_performance)
        model, probabilities = cached_model, cached_probabilities
        print(f"Cache check passed: max validation difference={agreement['maximum_absolute_probability_difference']:.3g}; all outreach flags unchanged.", flush=True)
    performance = compare_actual_outcomes({"validation": validation},
                                          {"validation": probabilities}, actual_dir)
    atomic_json(actual_dir / "model_provenance.json", model_provenance)
    print(f"Actual vs trained model: {len(validation)}/544 held-out validation rows scored.", flush=True)
    print(json.dumps(json_ready(performance), indent=2), flush=True)
    if comparison_only:
        print("Predictive comparison complete; the full explanation audit has not been completed by --compare.")
        return
    flags, _ = capacity_predictions(probabilities)
    pos = np.arange(len(validation), dtype=int)  # AUDIT EVERY validation observation
    current_ids = validation.iloc[pos]["source_row_id"].astype(int).tolist()
    if len(current_ids) != EXPECTED_CASES or len(set(current_ids)) != EXPECTED_CASES:
        raise ValueError("Validation cohort incomplete or duplicate; expected exactly 544 eligible rows")
    if selected_ids is not None and selected_ids != current_ids:
        raise RuntimeError("Validation case selection changed from the saved manifest. Stop; do not mix runs.")
    probability_sha = hashlib.sha256(np.asarray(probabilities, dtype="<f8").tobytes()).hexdigest()
    if selected_ids is not None and existing.get("validation_probability_sha256") != probability_sha:
        raise RuntimeError("Frozen validation model probabilities differ on resume. Stop; do not mix case outputs from different fits/checkpoints.")
    if selected_ids is None:
        atomic_json(manifest_path, {
            "version": SCRIPT_VERSION,
            "model_provenance": model_provenance,
            "mode": "all_544_validation_explanation_audit_with_surrogates",
            "split": SELECTED_SPLIT,
            "test_evaluated": False,
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "hashes": signatures,
            "validation_probability_sha256": probability_sha,
            "n_train": len(train), "n_validation": len(validation),
            "selected_source_row_ids": current_ids,
            "original_protocol_cases": protocol["faithfulness"]["cases"],
            "enhanced_full_cohort_cases": EXPECTED_CASES,
            "note": "New validation-only supplementary run after the 2 Nov scope amendment. Does not rewrite original status or final test.",
        })
    completed = {x["source_row_id"] for x in load_cases(artifact_dir)}
    if not completed.issubset(set(current_ids)):
        raise RuntimeError("Saved case files do not match protocol-selected validation cases")
    groups = semantic_feature_groups(columns)
    settings = protocol["shap"]
    background = xtrain.sample(n=settings["background_size"], random_state=42)
    refs = training_reference_values(train, columns)
    print(f"Resuming audit: {len(completed)}/{EXPECTED_CASES} saved cases", flush=True)
    newly_completed = 0
    for i, p in enumerate(pos, start=1):
        sid = int(validation.iloc[p]["source_row_id"])
        if sid in completed:
            print(f"[{i}/{EXPECTED_CASES}] source_row_id={sid}: already saved, skipping", flush=True)
            continue
        print(f"[{i}/{EXPECTED_CASES}] source_row_id={sid}: SHAP, pairs, six surrogates, stability, recourse ...", flush=True)
        case_started = monotonic()
        record = compute_one_case(
            pos=int(p), train=train, validation=validation, xtrain=xtrain,
            xval=xval, columns=columns, groups=groups, background=background,
            references=refs, model=model, probabilities=probabilities, flags=flags,
            protocol=protocol,
        )
        if sha256(paths["lock"]) != signatures["lock"]:
            raise RuntimeError("Final-test lock changed during audit, stopping before saving")
        atomic_json(artifact_dir / f"case_{sid:05d}.json", record)
        newly_completed += 1
        atomic_json(artifact_dir / "progress.json", {
            "completed_cases": len(completed) + newly_completed,
            "expected_cases": EXPECTED_CASES, "full_audit_completed": len(completed) + newly_completed == EXPECTED_CASES,
            "last_case_seconds": monotonic() - case_started,
            "updated_utc": datetime.now(timezone.utc).isoformat(),
            "test_evaluated": False,
        })
        print(f"[{i}/{EXPECTED_CASES}] saved; faithfulness area={record['faithfulness_area']:.5f}", flush=True)
        if max_new_cases is not None and newly_completed >= max_new_cases:
            print(f"Batch cap reached ({max_new_cases} new cases). Next --run resumes the remaining cases.", flush=True)
            break
    saved_count = len(load_cases(artifact_dir))
    if saved_count == EXPECTED_CASES:
        print("Entire 544-student validation cohort complete. Generating evidence tables, charts and report.", flush=True)
        report(paths)
    else:
        print(f"PROGRESS ONLY: {saved_count}/{EXPECTED_CASES}. Not a completed full audit; resume with --run or preview --report-partial.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true", help="Fast preflight; no model fitted")
    modes.add_argument("--run", action="store_true", help="Run/resume computationally expensive ALL-544 validation audit")
    modes.add_argument("--compare", action="store_true", help="Score ALL 544 actual validation outcomes against the trained model; no SHAP cases computed")
    modes.add_argument("--report", action="store_true", help="Compile only after all 544 case outputs exist")
    modes.add_argument("--report-partial", action="store_true", help="Clearly labeled partial report only")
    parser.add_argument("--max-new-cases", type=int, default=None,
        help="Optional batch cap, e.g. 5 new cases per run; resuming checks hashes (never marks a partial run complete)")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2], help="Root of cloned team repo (default: two directories above this script)")
    parser.add_argument("--checkpoint", type=Path, help="Existing checkpoint file; checked against the package's expected SHA256. Otherwise download the named official checkpoint.")
    parser.add_argument("--inference-cache", action="store_true", help="Use supported KV inference caching after comparison with uncached predictions on all 544 rows and 32 masked probes; records a distinct runtime identity")
    args = parser.parse_args()
    if args.max_new_cases is not None and (args.max_new_cases < 1 or not args.run):
        parser.error("--max-new-cases must be >=1 and requires --run")
    repo = args.repo.resolve()
    if not repo.is_dir():
        parser.error("Repository root does not exist")
    if args.report or args.report_partial:
        paths, protocol, signatures = preflight(repo)
        manifest_path = paths["artifacts"] / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError("No W1 run manifest; perform --run before requesting a report")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("hashes") != signatures or manifest.get("version") != SCRIPT_VERSION:
            raise RuntimeError("Source/script/lock hashes differ from recorded run. STOP; do not mix versions")
        report(paths, allow_partial=args.report_partial)
        return
    paths, protocol, signatures = preflight(repo)
    if args.check:
        return
    run(repo, paths, protocol, signatures, max_new_cases=args.max_new_cases,
        comparison_only=args.compare, checkpoint=args.checkpoint,
        inference_cache=args.inference_cache)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted. Completed case JSONs are retained; --run resumes safely.", file=sys.stderr)
        raise SystemExit(130)
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
