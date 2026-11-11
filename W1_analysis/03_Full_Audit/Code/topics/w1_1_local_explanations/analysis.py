import pandas as pd
from .feature_guide import feature_dictionary


def analyse(records):
    rows = [{"source_row_id": case['source_row_id'],
             "flagged": case['flagged'], **row,
             "in_baseline_top_five": row['feature_group'] in case['baseline_top_five_groups']}
            for case in records for row in case['baseline_group_contributions_all']]
    detail = pd.DataFrame(rows)
    if detail.duplicated(['source_row_id', 'feature_group']).any():
        raise ValueError('Duplicate local feature-group explanation.')
    if (detail.groupby('feature_group').members.nunique() != 1).any():
        raise ValueError('Group membership must be constant across students.')
    guide = feature_dictionary()
    recorded_members = {c.strip() for value in detail.members.unique() for c in value.split(',')}
    if recorded_members != set(guide.model_column):
        raise ValueError('The 33-column guide differs from the recorded feature members.')
    detail['raises_prediction'] = detail.signed_shap > 0
    detail['lowers_prediction'] = detail.signed_shap < 0
    summary = detail.groupby('feature_group', as_index=False).agg(
        cases_observed=('source_row_id', 'nunique'), members=('members', 'first'),
        mean_absolute_group_shap=('absolute_group_shap', 'mean'),
        median_absolute_group_shap=('absolute_group_shap', 'median'),
        mean_signed_group_shap=('signed_shap', 'mean'),
        fraction_raising_prediction=('raises_prediction', 'mean'),
        fraction_lowering_prediction=('lowers_prediction', 'mean'),
        baseline_top5_fraction=('in_baseline_top_five', 'mean'))
    if (summary.cases_observed != len(records)).any():
        raise ValueError('Every feature group must cover every selected student.')
    return {'feature_dictionary': guide, 'by_case': detail, 'feature_summary': summary.sort_values('mean_absolute_group_shap', ascending=False)}
