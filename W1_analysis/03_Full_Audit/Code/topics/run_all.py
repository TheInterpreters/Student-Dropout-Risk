"""Run W1.1-W1.5 using completed case files. No model or SHAP is executed."""
import argparse
from pathlib import Path
import json
import pandas as pd
from common import load_completed, write_json
from w1_1_local_explanations.analysis import analyse as local_explanations
from w1_2_single_vs_pairs.analysis import compare_pairs, compare_surrogates
from w1_3_robustness.analysis import analyse as robustness
from w1_4_human_support.analysis import analyse as human_support
from w1_4_human_support.scenarios import analyse_scenarios
from w1_5_feature_selection.analysis import select_panel

ROOT = Path(__file__).resolve().parent
POLICY = json.loads((ROOT / 'policy.json').read_text(encoding='utf-8'))
TOPIC_NAMES = ['w1_1_local_explanations', 'w1_2_single_vs_pairs', 'w1_3_robustness',
               'w1_4_human_support', 'w1_5_feature_selection']


def run(cases=None, output_root=None):
    inputs = load_completed(cases)
    records = inputs.records
    output_root = Path(output_root) if output_root else ROOT
    local = local_explanations(records)
    pair = compare_pairs(records, min_cases=POLICY['minimum_pair_cases'], bootstrap=POLICY['student_bootstrap_resamples'], seed=POLICY['seed'])
    surrogate = compare_surrogates(records, bootstrap=POLICY['student_bootstrap_resamples'], seed=POLICY['seed'])
    stable = robustness(records, POLICY['stability_warning_threshold'], POLICY['numerical_tolerance'])
    support = human_support(records)
    scenarios = analyse_scenarios(records)
    panel = select_panel(local['feature_summary'], pair['summary'], surrogate['variant_summary'],
                         POLICY['top_main_groups'], POLICY['top_pairs'], POLICY['minimum_pair_cases'])
    panel['fit_warning_evidence'] = {k: v for k, v in inputs.warnings.items() if k != 'warning_count_by_source_row_id'}
    panel['feature_stability'] = stable['group_retention'].loc[stable['group_retention'].feature_group.isin([r['feature_group'] for r in panel['selected_main_groups']])].to_dict('records')
    tables = {
        'w1_1_local_explanations': {'local_shap_by_case.csv': local['by_case'], 'feature_importance.csv': local['feature_summary'],
                                    'all_33_feature_definitions.csv': local['feature_dictionary']},
        'w1_2_single_vs_pairs': {'pair_responses_by_case.csv': pair['by_case'], 'single_vs_pair_summary.csv': pair['summary'],
                                'surrogate_errors_by_case.csv': surrogate['by_case'], 'six_variants.csv': surrogate['variant_summary'],
                                'matched_main_vs_pairs.csv': surrogate['main_vs_pairs']},
        'w1_3_robustness': {'stability_by_case.csv': stable['by_case'], 'stability_summary.csv': stable['overall'],
                           'conditional_feature_retention.csv': stable['group_retention']},
        'w1_4_human_support': {'support_catalogue.csv': support['catalogue'],
                              'recorded_scenarios_by_case.csv': scenarios['by_case'],
                              'recorded_administrative_scenarios_by_case.csv': scenarios['administrative_by_case'],
                              'recorded_scenario_summary.csv': scenarios['summary'], 'review_prompts_by_case.csv': support['case_review'],
                              'future_retention_follow_up_template.csv': pd.DataFrame(columns=support['follow_up_columns'])},
        'w1_5_feature_selection': {'selected_main_groups.csv': pd.DataFrame(panel['selected_main_groups']),
                                  'selected_pairs.csv': pd.DataFrame(panel['selected_pairs']),
                                  'selected_group_stability.csv': pd.DataFrame(panel['feature_stability'])},
    }
    for topic, exports in tables.items():
        folder = output_root / topic / 'results'
        folder.mkdir(parents=True, exist_ok=True)
        for name, frame in exports.items():
            frame.to_csv(folder / name, index=False)
    write_json(output_root / 'w1_5_feature_selection/results/selected_explanatory_panel.json', panel)
    provenance = {'source_cases': str(inputs.cases_path), 'complete_cases': 544,
                  'model_and_shap_rerun': False, 'prediction_model_modified': False,
                  'source_probability_identity': inputs.manifest['validation_probability_sha256'],
                  'source_code_hashes': inputs.manifest['hashes'], 'policy': POLICY,
                  'raw_case_fingerprints_file': 'input_provenance_by_case.json',
                  'scope_note': 'Feature/pair choices are explanatory reporting choices, not newly validated predictive inputs or intervention effects.'}
    write_json(output_root / 'analysis_provenance.json', provenance)
    write_json(output_root / 'input_provenance_by_case.json', inputs.fingerprints)
    best = surrogate['variant_summary'].iloc[0]
    lines = ['# W1 topic analysis from saved full-audit evidence', '',
             '**544/544 students covered. No TabICL, SHAP or case audit was rerun.**', '',
             f"Lowest recorded local surrogate MAE: {best.variant}, {best.pooled_holdout_mae:.5f}.", '',
             '## Matched main-only versus pair-augmented surrogates', '',
             '| Family | Main MAE | Pair MAE | Mean MAE reduction | 95% student-bootstrap interval | Pair win fraction |',
             '| --- | ---: | ---: | ---: | --- | ---: |']
    for row in surrogate['main_vs_pairs'].itertuples():
        lines.append(f'| {row.family} | {row.main_only_mae:.5f} | {row.with_pairs_mae:.5f} | {row.mean_mae_reduction:.5f} | [{row.ci_lower_95:.5f}, {row.ci_upper_95:.5f}] | {row.pair_win_fraction:.1%} |')
    lines += ['', 'Resampling is by student, keeping that student’s eight masking tests together. Intervals are descriptive per-family intervals; selection is exploratory and is not a new independent predictive test.', '',
              '## Selected explanatory panel', '',
              'Main groups: ' + ', '.join(r['feature_group'] for r in panel['selected_main_groups']) + '.', '',
              'Pairs: ' + ('; '.join(r['group_a']+' + '+r['group_b'] for r in panel['selected_pairs']) or 'none preferred under the current reporting policy') + '.', '',
              'These are a report shortlist. The original predictor still uses all its original inputs. Exact nonzero Lasso coefficient identities were not saved in the old case format; this output does not invent them.', '',
              '## Feature contribution → change in model output → human action', '',
              'The feature guide defines all 33 inputs. Signed SHAP is saved for 27 groups: positive raises the local probability relative to the training background; negative lowers it. Individual member values were not retained for the two multi-input academic groups. No global monotonic or causal direction is inferred.', '',
              f"All {len(scenarios['by_case'])} broad scenario rows (including 544 original profiles) and {len(scenarios['administrative_by_case'])} administrative rows are preserved in derived case exports. Scenario summaries exclude baselines and not-applicable/no-change placeholders. Compare before/after within each student: scenario populations differ.", '',
              'Grade/credit edits are retrospective input sensitivity. Verified financial assistance and practical tutoring/access support target real barriers and future study, with no estimated local causal effect on dropout. A separate optional callback can score new permitted edits using an already-fitted model; it does not fit or rerun this audit.', '',
              '## Robustness and human action', '',
              'The robustness topic preserves original warning counts and also reports a 1e-12 numerical tolerance at the 0.80 boundary. Original case JSON is unchanged.', '',
              'Academic, financial and combined support are proposed human-reviewed actions. Ask students about current barriers, target future course engagement and assistance, and monitor actual continued enrollment/completion. Model masking responses do not estimate programme benefits.', '',
              'The human-support topic includes an empty prospective follow-up template. There are no future intervention outcome records in this audit.', '',
              '## Evidence limits', '',
              'The 24/8 local masking design and its six saved variants are reused. Pair effects are conditional on each student’s SHAP-selected top five groups. Rare pairs remain in the summary with their counts but are excluded from the reporting panel below the declared support threshold.', '',
              'Convergence warnings, background/seed instability, off-manifold masking and the absent original private fitted-model bundle remain limitations. No retention improvement or causal effect is inferred from these files.', '']
    report = '\n'.join(lines)
    (output_root / 'W1_SUMMARY.md').write_text(report, encoding='utf-8')
    return {'inputs': inputs, 'local': local, 'pairs': pair, 'surrogates': surrogate,
            'stability': stable, 'support': support, 'scenarios': scenarios, 'selection': panel, 'output_root': output_root}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', help='Folder holding manifest.json and all 544 case_*.json records.')
    parser.add_argument('--output-root', type=Path, help='Optional export folder; default keeps each topic’s code and results together.')
    args = parser.parse_args()
    result = run(args.cases, args.output_root)
    print(f"W1.1-W1.5 finished from {len(result['inputs'].records)} saved cases. No model/SHAP rerun.")
    print('Report:', result['output_root'] / 'W1_SUMMARY.md')
