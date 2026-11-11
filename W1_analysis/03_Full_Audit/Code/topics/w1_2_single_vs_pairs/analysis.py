"""Use saved TabICL responses; reference masking is not a causal intervention."""
import numpy as np
import pandas as pd
from common import VARIANTS, mean_interval


def compare_pairs(records, min_cases=30, bootstrap=2000, seed=42):
    rows = []
    for record in records:
        seen = set()
        for probe in record['pairwise_reference_masking']:
            a, b = probe['feature_group_a'], probe['feature_group_b']
            p, pa, pb, pab = [float(probe[k]) for k in ('original_probability', 'masked_a_probability', 'masked_b_probability', 'masked_both_probability')]
            if a == b or not all(np.isfinite([p, pa, pb, pab])) or not all(0 <= x <= 1 for x in [p, pa, pb, pab]):
                raise ValueError("Pair probes require distinct groups and valid saved probabilities.")
            interaction = pab-pa-pb+p
            if not np.isclose(interaction, probe['nonadditive_effect'], atol=1e-9, rtol=1e-9):
                raise ValueError("Recorded nonadditivity contradicts its saved probabilities.")
            if a > b:
                a, b, pa, pb = b, a, pb, pa
            if (a, b) in seen:
                raise ValueError("Repeated unordered pair within one student.")
            seen.add((a, b))
            da, db, joint = pa-p, pb-p, pab-p
            rows.append({'source_row_id': record['source_row_id'], 'group_a': a, 'group_b': b,
                         'single_a_change': da, 'single_b_change': db, 'joint_change': joint,
                         'abs_single_a_change': abs(da), 'abs_single_b_change': abs(db),
                         'abs_joint_change': abs(joint), 'nonadditivity': interaction,
                         'abs_nonadditivity': abs(interaction),
                         'joint_gain_over_best_single': abs(joint)-max(abs(da), abs(db))})
    detail = pd.DataFrame(rows)
    summaries = []
    for (a, b), values in detail.groupby(['group_a', 'group_b'], sort=True):
        gain, low, high = mean_interval(values.joint_gain_over_best_single, bootstrap, seed)
        summaries.append({'group_a': a, 'group_b': b, 'cases_observed': len(values),
                          'eligible_for_panel': len(values) >= min_cases,
                          'mean_abs_single_a_change': values.abs_single_a_change.mean(),
                          'mean_abs_single_b_change': values.abs_single_b_change.mean(),
                          'mean_abs_joint_change': values.abs_joint_change.mean(),
                          'mean_abs_nonadditivity': values.abs_nonadditivity.mean(),
                          'mean_signed_nonadditivity': values.nonadditivity.mean(),
                          'mean_joint_gain_over_best_single': gain, 'gain_ci_lower_95': low,
                          'gain_ci_upper_95': high,
                          'joint_exceeds_each_single_fraction': (values.joint_gain_over_best_single > 1e-12).mean()})
    summary = pd.DataFrame(summaries).sort_values(['mean_abs_nonadditivity', 'cases_observed'], ascending=False)
    return {'by_case': detail, 'summary': summary}


def compare_surrogates(records, bootstrap=2000, seed=42):
    rows = []
    for record in records:
        summary = record['surrogate_comparison']['summary']
        if len(summary) != 6 or {r['variant'] for r in summary} != VARIANTS:
            raise ValueError("Every student must have all six variants; incomplete students cannot be dropped.")
        for row in summary:
            if not np.isfinite(row['holdout_mae']) or row['holdout_mae'] < 0:
                raise ValueError("Invalid recorded holdout error.")
            rows.append({'source_row_id': record['source_row_id'], **row})
    detail = pd.DataFrame(rows)
    if detail.duplicated(['source_row_id', 'variant']).any():
        raise ValueError("Student/variant rows must be unique.")
    summary = detail.groupby('variant', as_index=False).agg(
        students=('source_row_id', 'nunique'), pooled_holdout_mae=('holdout_mae', 'mean'),
        median_case_mae=('holdout_mae', 'median'), mean_case_rmse=('holdout_rmse', 'mean'),
        mean_nonzero_terms=('nonzero_terms', 'mean'),
        mean_out_of_range_fraction=('fraction_outside_probability_range', 'mean'))
    summary = summary.sort_values('pooled_holdout_mae')
    wide = detail.pivot(index='source_row_id', columns='variant', values='holdout_mae')
    comparisons = []
    for family in ['OLS', 'Ridge', 'Lasso']:
        main, paired = wide[family+'+main'], wide[family+'+pairs']
        differences = main-paired
        mean, low, high = mean_interval(differences, bootstrap, seed)
        comparisons.append({'family': family, 'students_compared': len(wide),
                            'main_only_mae': main.mean(), 'with_pairs_mae': paired.mean(),
                            'mean_mae_reduction': mean, 'ci_lower_95': low, 'ci_upper_95': high,
                            'pair_win_fraction': (differences > 1e-12).mean(),
                            'pair_tie_fraction': (differences.abs() <= 1e-12).mean(),
                            'relative_mae_reduction_pct': 100*mean/main.mean() if main.mean() > 0 else float('nan')})
    return {'by_case': detail, 'variant_summary': summary,
            'main_vs_pairs': pd.DataFrame(comparisons)}
