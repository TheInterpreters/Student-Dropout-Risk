"""Select report features/pairs from saved evidence without changing TabICL."""
def select_panel(features, pairs, variants, main_k=5, pair_k=3, min_pair_cases=30):
    if main_k < 1 or pair_k < 0 or min_pair_cases < 1:
        raise ValueError('Panel sizes/support thresholds must be valid.')
    chosen = features.sort_values('mean_absolute_group_shap', ascending=False).head(main_k)
    names = set(chosen.feature_group)
    main_variants = variants.loc[variants.variant.str.endswith('+main')]
    pair_variants = variants.loc[variants.variant.str.endswith('+pairs')]
    if main_variants.empty or pair_variants.empty:
        raise ValueError('Both main-only and pair-augmented model families must be compared.')
    main_best = main_variants.sort_values('pooled_holdout_mae').iloc[0]
    pair_best = pair_variants.sort_values('pooled_holdout_mae').iloc[0]
    prefer_pairs = pair_best.pooled_holdout_mae < main_best.pooled_holdout_mae
    eligible = pairs.loc[(pairs.cases_observed >= min_pair_cases) & pairs.group_a.isin(names) & pairs.group_b.isin(names)]
    eligible = eligible.sort_values(['mean_abs_nonadditivity', 'cases_observed'], ascending=False)
    selected = eligible.head(pair_k) if prefer_pairs else eligible.head(0)
    groups = chosen.to_dict('records')
    columns = sorted({member.strip() for row in groups for member in row['members'].split(',')})
    return {'selection_scope': 'explanatory_reporting_only', 'prediction_model_changed': False,
            'status': 'provisional_explanatory_panel', 'uses_actual_outcome_labels_for_selection': False,
            'selected_main_groups': groups, 'selected_model_columns': columns,
            'selected_pairs': selected.to_dict('records'),
            'best_recorded_main_variant': main_best.variant, 'best_recorded_pair_variant': pair_best.variant,
            'best_main_holdout_mae': float(main_best.pooled_holdout_mae),
            'best_pair_holdout_mae': float(pair_best.pooled_holdout_mae),
            'pair_family_preferred_for_local_approximation': bool(prefer_pairs),
            'policy': {'top_main_groups': main_k, 'top_pairs': pair_k, 'minimum_pair_cases': min_pair_cases,
                       'main_rank': 'Mean absolute grouped SHAP over every validation case.',
                       'pair_rank': 'Mean absolute reference-masking nonadditivity, among selected groups with sufficient support.'},
            'limits': ['Reporting shortlist, not validated input selection for a new dropout predictor.',
                       'Selected groups/pairs are not the exact nonzero Lasso coefficient identities; those were not saved.',
                       'Family selection on recorded holdouts is exploratory, not a new independent test.',
                       'Model response strength and surrogate fidelity do not measure real intervention benefit.',
                       'Background/seed instability and recorded convergence warnings require review.']}
