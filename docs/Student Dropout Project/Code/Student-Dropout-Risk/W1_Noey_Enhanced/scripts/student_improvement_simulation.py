"""Noey W1: validation-only feature-first student improvement simulation.

Run from the repository root, with W1_Noey_Enhanced/ inside it:
  .\\.venv-core\\Scripts\\python.exe W1_Noey_Enhanced\\scripts\\student_improvement_simulation.py --run
  .\\.venv-core\\Scripts\\python.exe W1_Noey_Enhanced\\scripts\\student_improvement_simulation.py --run --source-row-id 123
  python W1_Noey_Enhanced/scripts/student_improvement_simulation.py --demo

--demo uses an invented illustrative logistic formula and NO student data/model.
--run uses TabICL refitted from the original training split and NEVER loads test.
Grade/pass scenario updates are RETROSPECTIVE INPUT SENSITIVITY ONLY, not an
intervention that the student can now perform or a forecast of next semester.
No existing scripts, results, evaluation lock or scientific settings are changed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "W1_Noey_Enhanced" / "outputs" / "improvement_scenarios"


def example_probability(grade: float, passed: int, overdue: int, debt: int, enrolled: int=6) -> float:
    """Invented logistic example ONLY; coefficients are not fitted to the UCI data."""
    if enrolled <= 0:
        raise ValueError("enrolled must be > 0")
    z = (-2 + 1.4 * (1-grade/20) + 1.7*(1-passed/enrolled) +
         1.0*overdue + .6*debt + .7*(1-grade/20)*overdue)
    return 1/(1+math.exp(-z))


def toy_demonstration() -> pd.DataFrame:
    examples = [
        ("Original profile",9,2,1,1),
        ("Improve grade: 9 -> 12",12,2,1,1),
        ("Pass more units: 2 -> 4 of 6",9,4,1,1),
        ("Tuition status resolved",9,2,0,1),
        ("Debtor status resolved",9,2,1,0),
        ("Grade + passed units improved",12,4,1,1),
        ("Tuition + debtor status resolved",9,2,0,0),
        ("Grade + tuition status",12,2,0,1),
        ("All four attributes changed",12,4,0,0),
    ]
    baseline = example_probability(*examples[0][1:])
    return pd.DataFrame([{
        "scenario": label, "grade_of_20": grade, "passed_of_6": passed,
        "tuition_overdue": overdue, "debtor": debt,
        "illustrative_probability": example_probability(grade,passed,overdue,debt),
        "change_percentage_points": 100*(example_probability(grade,passed,overdue,debt)-baseline),
    } for label, grade, passed, overdue, debt in examples])


def recompute_and_validate(row: pd.Series, updates: dict[str,Any], recompute) -> pd.Series:
    """Change only explicitly selected first-semester/payment inputs, maintaining derived ratios."""
    allowed={"curricular_units_1st_sem_grade", "curricular_units_1st_sem_approved",
             "tuition_fees_up_to_date", "debtor"}
    if not set(updates).issubset(allowed):
        raise ValueError(f"Disallowed feature update: {set(updates)-allowed}")
    new=row.copy()
    for key,value in updates.items():
        if key not in row:
            raise KeyError(key)
        new[key]=value
    enrolled = int(new["curricular_units_1st_sem_enrolled"])
    approved = int(new["curricular_units_1st_sem_approved"])
    grade = float(new["curricular_units_1st_sem_grade"])
    if enrolled<0 or not 0<=approved<=enrolled or not 0<=grade<=20:
        raise ValueError("Impossible grade, approved-units or enrolled-units scenario")
    if enrolled==0 and approved:
        raise ValueError("Cannot approve units without enrolment")
    for flag in ("debtor", "tuition_fees_up_to_date"):
        if int(new[flag]) not in (0,1):
            raise ValueError(f"{flag} must be binary")
    return recompute(new.to_frame().T).iloc[0]


def proposal_scenarios(row: pd.Series, recompute) -> list[tuple[str,pd.Series,str]]:
    """Validated scenario inputs, *not* real prospective outcomes."""
    g="curricular_units_1st_sem_grade"; a="curricular_units_1st_sem_approved"
    grade=float(row[g]); approved=int(row[a]); enrolled=int(row["curricular_units_1st_sem_enrolled"])
    evaluated=int(row.get("curricular_units_1st_sem_evaluations", enrolled))
    feasible_approved_limit = max(approved, min(enrolled, evaluated))
    changes={
        "Grade +3/20 (historical input what-if)": {g:min(20,grade+3)},
        "Approved units +2 (historical input what-if)": {a:min(feasible_approved_limit,approved+2)},
        "Grade +3 AND approved units +2": {g:min(20,grade+3),a:min(feasible_approved_limit,approved+2)},
        "Resolve overdue tuition status": {"tuition_fees_up_to_date":1},
        "Resolve debtor status": {"debtor":0},
        "Resolve tuition AND debtor statuses": {"tuition_fees_up_to_date":1,"debtor":0},
        "Academic measures + both finance statuses": {
            g:min(20,grade+3),a:min(feasible_approved_limit,approved+2),
            "tuition_fees_up_to_date":1,"debtor":0},
    }
    results=[("Original profile", row.copy(), "observed profile")]
    for name,update in changes.items():
        # A positive grade cannot be supported by a row with zero enrolled/evaluated units.
        if (g in update or a in update) and (
                enrolled <= 0 or ("curricular_units_1st_sem_evaluations" in row
                                  and int(row["curricular_units_1st_sem_evaluations"]) <= 0)):
            continue
        new=recompute_and_validate(row, update, recompute)
        # Do not create a positive semester grade when no credit was approved;
        # these are already sensitivity probes, so avoid gratuitously impossible rows.
        if g in update and int(new[a]) == 0 and float(new[g]) > 0:
            continue
        changed=any(str(new[c]) != str(row[c]) for c in update)
        if not changed:
            continue
        kind=("retrospective grade/credit sensitivity" if g in update or a in update else
              "hypothetical administratively-feasible status resolution; requires verification")
        results.append((name,new,kind))
    return results


def _predict(model, row: pd.Series, cols:list[str]) -> float:
    from src.modeling import prepare_tfm_frame
    p=np.asarray(model.predict_proba(prepare_tfm_frame(row.to_frame().T,cols)),dtype=float)
    if p.shape!=(1,2) or not np.isfinite(p).all() or not 0<=p[0,1]<=1:
        raise ValueError("Invalid TabICL probability")
    return float(p[0,1])


def _rank_and_flag(probabilities:np.ndarray, changed_position:int, new_p:float) -> tuple[int,int]:
    from src.modeling import capacity_predictions
    changed=np.asarray(probabilities,float).copy()
    changed[changed_position]=new_p
    flags,_=capacity_predictions(changed,capacity=.20)
    rank=int(np.where(np.lexsort((np.arange(len(changed)),-changed))==changed_position)[0][0]+1)
    return rank,int(flags[changed_position])


def choose_case(validation: pd.DataFrame, probabilities:np.ndarray, selected_id: int|None) -> int:
    from src.modeling import capacity_predictions
    if selected_id is not None:
        matching=np.flatnonzero(validation["source_row_id"].to_numpy()==selected_id)
        if len(matching)!=1:
            raise ValueError("Requested source-row ID is not part of the validation split")
        return int(matching[0])
    flags,_=capacity_predictions(probabilities,capacity=.20)
    grade=validation["curricular_units_1st_sem_grade"].to_numpy(float)
    approved=validation["curricular_units_1st_sem_approved"].to_numpy(int)
    enrolled=validation["curricular_units_1st_sem_enrolled"].to_numpy(int)
    tuition=validation["tuition_fees_up_to_date"].to_numpy(int)
    debt=validation["debtor"].to_numpy(int)
    elig=(flags==1)&(grade>0)&(grade<12)&(approved<enrolled)&(enrolled>0)&((tuition==0)|(debt==1))
    ids=np.flatnonzero(elig)
    if not len(ids):
        elig=(flags==1)&(grade>0)&(enrolled>0)&(approved<enrolled)
        ids=np.flatnonzero(elig)
    if not len(ids):
        raise ValueError("No flagged validation profile matched example constraints. Supply --source-row-id.")
    return int(ids[np.argmax(probabilities[ids])])


def feature_support_map(grouped:pd.DataFrame) -> list[dict[str,str]]:
    mapping={
      "first_semester_progress": "Review academic results; plan tutoring and future assessment targets. Academic grade edits are only retrospective model sensitivity, not genuine after-semester recourse.",
      "first_semester_participation": "Check missing evaluations/enrollment information with the student; arrange advising. Engagement and attendance are not observed directly.",
      "tuition_fees_up_to_date": "Verify fee balances and eligibility for payment plans or financial aid; do not assume payment status can be changed without support.",
      "debtor": "Review debt status, payment assistance, and feasible repayment arrangements with the finance office.",
      "scholarship_holder": "Review eligibility for funding support; do not alter actual scholarship records as a simulated guaranteed intervention.",
    }
    out=[]
    for rec in grouped.to_dict('records'):
        g=rec['feature_group']; sign=float(rec['signed_shap'])
        if sign>0 and g in mapping:
            out.append({'feature_group':g,'positive_local_shap_probability_points':sign*100,
                        'possible_support_action':mapping[g]})
    return out


def run(source_row_id:int|None=None):
    required=[ROOT/'artifacts'/'final_test.lock', ROOT/'artifacts'/'split_ids.csv',ROOT/'eda_uci_data'/'data'/'dropout_data.csv',ROOT/'config'/'evaluation_protocol.json']
    for path in required:
        if not path.exists(): raise FileNotFoundError(f'Required project file missing: {path}')
    lock=required[0]; lock_hash=hashlib.sha256(lock.read_bytes()).hexdigest()
    sys.path.insert(0,str(ROOT))
    from src.evaluation import development_frames, selected_model, load_protocol
    from src.modeling import prepare_tfm_frame
    from src.explanations import (recompute_first_semester_features,permutation_shap_values,
                                   semantic_feature_groups,aggregate_shap_by_group)
    protocol=load_protocol()
    if protocol['model']['name']!='tabicl' or protocol['shap']['background_size']!=25:
        raise ValueError('Frozen model or background changed; stop and review')
    train, validation, cols=development_frames('validation')  # NEVER test
    model=selected_model(train,cols)  # train data only, original model settings
    probabilities=np.asarray(model.predict_proba(prepare_tfm_frame(validation,cols)),dtype=float)[:,1]
    if len(probabilities)!=len(validation) or not np.isfinite(probabilities).all():
        raise ValueError('Invalid validation predictions')
    idx=choose_case(validation,probabilities,source_row_id)
    row=validation.iloc[idx][cols].copy()
    sid=int(validation.iloc[idx]['source_row_id']); original_p=float(probabilities[idx])
    bg=prepare_tfm_frame(train,cols).sample(n=25,random_state=42)
    explanation=permutation_shap_values(model.predict_proba,bg,prepare_tfm_frame(row.to_frame().T,cols),
                                        max_evals=protocol['shap']['max_evals'],seed=42)
    values=np.asarray(explanation.values,dtype=float)
    if values.shape!=(1,len(cols)) or not np.isfinite(values).all():
        raise ValueError('Bad SHAP output')
    grouped=aggregate_shap_by_group(values[0],cols,semantic_feature_groups(cols))
    scenarios=proposal_scenarios(row,recompute_first_semester_features)
    results=[]
    for label,candidate,scenario_kind in scenarios:
        pred= original_p if label=='Original profile' else _predict(model,candidate,cols)
        rank,flag=_rank_and_flag(probabilities,idx,pred)
        results.append({
            'source_row_id':sid,'scenario':label,'category':scenario_kind,
            'original_probability':original_p,'new_probability':pred,
            'probability_change_pp':100*(pred-original_p),'cohort_rank_after':rank,
            'flagged_after_top_20pct':flag,
            'first_semester_grade':float(candidate['curricular_units_1st_sem_grade']),
            'approved_units':int(candidate['curricular_units_1st_sem_approved']),
            'enrolled_units':int(candidate['curricular_units_1st_sem_enrolled']),
            'pass_rate':float(candidate['first_semester_pass_rate']),
            'tuition_fees_up_to_date':int(candidate['tuition_fees_up_to_date']),
            'debtor':int(candidate['debtor']),
        })
    if hashlib.sha256(lock.read_bytes()).hexdigest()!=lock_hash:
        raise RuntimeError('Final-test lock changed unexpectedly, STOP')
    out=OUTPUT/str(sid);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(results).to_csv(out/'tabicl_feature_change_scenarios_VALIDATION_ONLY.csv',index=False)
    grouped.to_csv(out/'local_grouped_shap_VALIDATION_ONLY.csv',index=False)
    info={
      'status':'REAL validation-only TabICL simulation (NOT a new final test)',
      'source_row_id':sid,'split':'validation','final_test_lock_sha256_unchanged':lock_hash,
      'frozen_model':'tabicl','model_fit':'original train partition only',
      'n_validation':len(validation),'selected_top_five_local_groups':grouped.head(5).to_dict('records'),
      'positive_shap_groups_with_possible_support_actions':feature_support_map(grouped),
      'limitations':[
        'Historical first-semester grades/credits cannot be changed by future student action.',
        'Grade/approved-unit inputs in counterfactuals are retrospective model sensitivity, NOT prospective intervention-effect predictions.',
        'Tuition and debtor status changes require case-by-case feasibility verification.',
        'Top-20% flags are relative: one student moving down does not change the capacity policy.',
        'Model probability changes are associations; do not interpret as causal changes in dropout.',
        'SHAP contributions depend on the chosen training background and masking method.',
      ],
    }
    (out/'case_interpretation_and_support.json').write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Source row {sid}; validation student; original p={original_p:.4f}')
    print(pd.DataFrame(results)[['scenario','new_probability','probability_change_pp','cohort_rank_after','flagged_after_top_20pct']].to_string(index=False))
    print('Local SHAP (top 5 groups):')
    print(grouped[['feature_group','signed_shap']].head(5).to_string(index=False))
    print(f'Wrote actual TabICL validation scenarios to {out}')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo',action='store_true',help='self-contained illustrative numeric example (not model result)')
    group.add_argument('--run',action='store_true',help='real TabICL inference on saved validation split; never test')
    parser.add_argument('--source-row-id',type=int,help='optional existing validation row ID, not a test row')
    args=parser.parse_args(argv)
    if args.demo:
        data=toy_demonstration()
        print('ILLUSTRATIVE ONLY; coefficients are invented, NOT fitted to student data or TabICL')
        print(data[['scenario','illustrative_probability','change_percentage_points']].to_string(index=False))
        return 0
    run(source_row_id=args.source_row_id)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
