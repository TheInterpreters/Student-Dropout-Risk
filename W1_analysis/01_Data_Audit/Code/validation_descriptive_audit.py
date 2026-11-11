"""Independent W1 validation-only descriptive audit on real UCI outcomes.

No predictive model is fit. Uses the exact original saved split IDs and prevents
accidental inclusion of held-out test observations. Observed dropout percentages
are *not* local SHAP, model probabilities, or intervention effects.

Run from repository root:
    python W1_Noey_Enhanced/scripts/validation_descriptive_audit.py --run
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'W1_Noey_Enhanced' / 'outputs' / 'observed_validation'


def validation_only(data: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    # Match the project src.modeling.clean_column_name normalization while
    # keeping this descriptive module independently testable without TabICL.
    def clean_column_name(column):
        return (column.strip().replace("'", "").replace("/", "_")
                .replace("(", "").replace(")", "").replace("-", "_")
                .replace(" ", "_").lower())
    df = data.rename(columns=clean_column_name).copy()
    df.insert(0, 'source_row_id', np.arange(len(df), dtype=int))
    required_splits={'source_row_id','split'}
    if set(splits.columns)!=required_splits or splits.source_row_id.duplicated().any():
        raise ValueError('Saved split map invalid or duplicate source IDs')
    if len(df[df.target.isin(['Dropout','Graduate'])])!=len(splits):
        raise ValueError('Split map must cover exactly the 3,630 binary-task observations')
    binary = df.loc[df.target.isin(['Dropout','Graduate'])].copy()
    merged=binary.merge(splits,on='source_row_id',validate='one_to_one')
    if len(merged)!=len(binary) or set(merged.split)!={'train','validation','test'}:
        raise ValueError('Saved split map does not cover binary dataset')
    validation=merged.loc[merged.split.eq('validation')].copy()
    validation['dropout']=(validation.target=='Dropout').astype(int)
    if not set(validation['dropout'].unique()).issubset({0,1}):
        raise ValueError('Invalid binary target')
    return validation


def observed_groups(validation: pd.DataFrame) -> pd.DataFrame:
    df=validation
    enrolled=df['curricular_units_1st_sem_enrolled'].astype(float)
    approved=df['curricular_units_1st_sem_approved'].astype(float)
    ratio=approved.div(enrolled.where(enrolled>0,np.nan))
    grade=df['curricular_units_1st_sem_grade'].astype(float)
    tuition=df['tuition_fees_up_to_date'].astype(int)
    debtor=df['debtor'].astype(int)
    valid=(enrolled>0)
    m={
      'All eligible validation students':np.ones(len(df),bool),
      'Grade below 10 (includes zeros)':grade<10,
      'Grade at least 10':grade>=10,
      'Pass rate below 50%, enrolled>0':valid & (ratio<.5),
      'Pass rate at least 50%, enrolled>0':valid & (ratio>=.5),
      'Tuition overdue':tuition==0,
      'Tuition up to date':tuition==1,
      'Debtor':debtor==1,
      'Not debtor':debtor==0,
      'Grade below 10 + tuition overdue':(grade<10)&(tuition==0),
      'Grade below 10 + tuition paid':(grade<10)&(tuition==1),
      'Grade at least 10 + tuition overdue':(grade>=10)&(tuition==0),
      'Grade at least 10 + tuition paid':(grade>=10)&(tuition==1),
      'Low pass rate + tuition overdue':valid & (ratio<.5) & (tuition==0),
      'Low pass rate + tuition paid':valid & (ratio<.5) & (tuition==1),
    }
    rows=[]
    for title,mask in m.items():
        sample=df.loc[mask]
        rows.append({'group':title,'n':int(len(sample)), 'dropouts':int(sample.dropout.sum()),
                     'observed_dropout_rate_pct':float(round(100*sample.dropout.mean(),4)) if len(sample) else None,
                     'type':'observed validation subgroup; not model predictions or causal effects'})
    return pd.DataFrame(rows)


def run(root: Path = ROOT, output: Path = OUTPUT):
    data_path=root/'eda_uci_data'/'data'/'dropout_data.csv'
    split_path=root/'artifacts'/'split_ids.csv'
    for p in [data_path,split_path]:
        if not p.is_file():raise FileNotFoundError(p)
    raw=pd.read_csv(data_path)
    split=pd.read_csv(split_path)
    val=validation_only(raw,split)
    if len(val)!=544:
        raise ValueError(f'Expected original 544-row validation partition, got {len(val)}')
    result=observed_groups(val)
    # Development-only training summary; NEVER use or expose locked test outcomes.
    binary=raw.rename(columns=lambda c: c.strip().replace("'", "").replace("/", "_")
                            .replace("(", "").replace(")", "").replace("-", "_")
                            .replace(" ", "_").lower()).copy()
    binary.insert(0, 'source_row_id', np.arange(len(binary), dtype=int))
    binary=binary.loc[binary['target'].isin(['Dropout','Graduate'])]
    combined=binary.merge(split,on='source_row_id',validate='one_to_one')
    training=combined.loc[combined['split'].eq('train')].copy()
    training['dropout']=(training['target']=='Dropout').astype(int)
    if len(training)!=2541 or len(val)!=544 or len(combined)!=3630:
        raise ValueError('Unexpected original development-data split counts')
    train_result=observed_groups(training)
    output.mkdir(parents=True,exist_ok=True)
    result.to_csv(output/'actual_validation_subgroups.csv',index=False)
    train_result.to_csv(output/'actual_training_subgroups.csv',index=False)
    audit={'source':'repository CSV and saved split_ids.csv','analysis_split':'validation',
           'n_raw':len(raw),'n_binary':len(split),'n_train':len(training),'n_validation':len(val),
           'training_dropouts':int(training.dropout.sum()),
           'validation_dropouts':int(val.dropout.sum()),
           'test_labels_used':False,'model_retrained':False,
           'data_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest(),
           'split_sha256':hashlib.sha256(split_path.read_bytes()).hexdigest(),
           'disclaimer':'Observed associations; no estimated intervention effects, model probabilities, SHAP, or causal claims.'}
    (output/'provenance.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(result[['group','n','dropouts','observed_dropout_rate_pct']].to_string(index=False))
    print(f'Validated train={len(training)}, validation={len(val)}; TEST OUTCOMES NOT READ; saved to {output}')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true',required=True)
    args=parser.parse_args();sys.path.insert(0,str(ROOT));run()
