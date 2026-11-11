from itertools import combinations
import numpy as np
import pandas as pd


def materially_below(value, threshold=.8, tolerance=1e-12):
    return bool(value < threshold-tolerance) if value is not None else None


def analyse(records, threshold=.8, tolerance=1e-12):
    rows, retention = [], []
    for case in records:
        for item in case['stability']:
            mode = item['variation']
            rankings = case['top_five_rankings'][mode]
            if len(rankings) != item['valid_runs'] or any(len(set(r)) != 5 for r in rankings):
                raise ValueError('Stored ranking repeats disagree with their stability metadata.')
            overlaps = [len(set(a) & set(b))/5 for a, b in combinations(rankings, 2)]
            reconstructed = float(np.mean(overlaps)) if overlaps else None
            recorded = item['top_5_overlap']
            if reconstructed is not None and not np.isclose(reconstructed, recorded, atol=1e-12):
                raise ValueError('Recorded stability cannot be reconstructed from saved rankings.')
            rows.append({**item, 'reconstructed_top5_overlap': reconstructed,
                         'original_below_threshold': item['low_stability'],
                         'materially_below_threshold': materially_below(recorded, threshold, tolerance),
                         'at_threshold_within_rounding_tolerance': abs(recorded-threshold) <= tolerance if recorded is not None else None})
            for group in case['baseline_top_five_groups']:
                retention.append({'source_row_id': case['source_row_id'], 'feature_group': group,
                                  'variation': mode, 'runs': len(rankings),
                                  'retained_runs': sum(group in rank for rank in rankings)})
    detail = pd.DataFrame(rows)
    group = pd.DataFrame(retention).groupby(['feature_group', 'variation'], as_index=False).agg(
        baseline_top5_cases=('source_row_id', 'nunique'), valid_runs=('runs', 'sum'), retained_runs=('retained_runs', 'sum'))
    group['conditional_top5_retention'] = group.retained_runs/group.valid_runs.replace(0, np.nan)
    overall = detail.groupby('variation', as_index=False).agg(
        students=('source_row_id', 'nunique'), mean_top5_overlap=('top_5_overlap', 'mean'),
        original_warning_cases=('original_below_threshold', 'sum'),
        materially_below_threshold_cases=('materially_below_threshold', 'sum'),
        at_threshold_cases=('at_threshold_within_rounding_tolerance', 'sum'))
    return {'by_case': detail, 'group_retention': group, 'overall': overall,
            'threshold': threshold, 'rounding_tolerance': tolerance}
