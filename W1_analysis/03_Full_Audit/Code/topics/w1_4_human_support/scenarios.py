"""Recorded feature-change responses, plus bounded optional prediction-only edits."""
import numpy as np
import pandas as pd


def _checked_probabilities(record, row, delta_key, multiplier):
    before, after = float(row['original_probability']), float(row['scenario_probability'])
    if not np.isfinite([before, after]).all() or not 0 <= before <= 1 or not 0 <= after <= 1:
        raise ValueError('Saved scenario probabilities must lie in [0, 1].')
    if not np.isclose(before, record['predicted_probability'], atol=1e-10, rtol=0):
        raise ValueError('Saved scenario baseline differs from the audited model probability.')
    delta = multiplier * (after-before)
    if not np.isclose(delta, float(row[delta_key]), atol=1e-8, rtol=0):
        raise ValueError('Saved scenario delta contradicts its before/after probabilities.')
    return before, after


def analyse_scenarios(records):
    """Keep all original rows; summarize actual probes separately from baseline/placeholders."""
    broad, admin = [], []
    for record in records:
        for row in record['individual_combined_improvement_scenarios']:
            before, after = _checked_probabilities(record, row, 'change_probability_points', 100)
            historical = 'retrospective' in row['category']
            broad.append({'source_row_id': record['source_row_id'], **row,
                          'is_evaluated_change': row['scenario'] != 'Original profile',
                          'evidence_type': 'Historical input sensitivity' if historical else
                              'Observed baseline' if row['scenario'] == 'Original profile' else 'Status-resolution simulation; verify feasibility',
                          'actual_dropout_effect_estimated': False})
        for row in record['recourse_scenarios']:
            before, after = _checked_probabilities(record, row, 'delta_probability', 1)
            admin.append({'source_row_id': record['source_row_id'], **row,
                          'change_probability_points': 100*(after-before),
                          'is_evaluated_change': row['status'] not in ['not_flagged', 'no_change_available'],
                          'actual_dropout_effect_estimated': False})
    detail = pd.DataFrame(broad)
    if detail.duplicated(['source_row_id', 'scenario']).any():
        raise ValueError('Duplicate saved scenario for a student.')
    probes = detail.loc[detail.is_evaluated_change].copy()
    probes['probability_decreased'] = probes.change_probability_points < 0
    probes['left_flagged_group'] = (probes.flagged_before == 1) & (probes.flagged_after == 0)
    summary = probes.groupby(['scenario', 'evidence_type'], as_index=False).agg(
        students_tested=('source_row_id', 'nunique'),
        mean_probability_before=('original_probability', 'mean'),
        mean_probability_after=('scenario_probability', 'mean'),
        mean_change_percentage_points=('change_probability_points', 'mean'),
        median_change_percentage_points=('change_probability_points', 'median'),
        fraction_probability_decreased=('probability_decreased', 'mean'),
        students_flagged_before=('flagged_before', 'sum'),
        students_leaving_flagged_group=('left_flagged_group', 'sum'))
    # Scenario cohorts differ because unchanged or infeasible edits were skipped.
    summary['comparison_scope'] = 'Within-student before/after; scenario eligibility differs; not a between-scenario efficacy ranking'
    summary['actual_dropout_effect_estimated'] = False
    return {'by_case': detail, 'summary': summary, 'administrative_by_case': pd.DataFrame(admin)}


def predict_feature_changes(profile, scenarios, predict_dropout, *, allow_retrospective=False):
    """Optional: one batch of predictions from an ALREADY-FITTED model callback.

    No fitting, checkpoint loading, SHAP, cohort ranking or audit-file writes.
    ``predict_dropout(frame)`` must return one dropout probability per row.
    Only the four originally audited inputs can be edited here. Administrative
    edits are hypothetical until verified; academic edits need explicit opt-in.
    """
    grade = 'curricular_units_1st_sem_grade'
    approved = 'curricular_units_1st_sem_approved'
    enrolled = 'curricular_units_1st_sem_enrolled'
    evaluations = 'curricular_units_1st_sem_evaluations'
    allowed = {grade, approved, 'debtor', 'tuition_fees_up_to_date'}
    row = pd.Series(profile).copy(deep=True)
    labels, profiles, kinds = ['Original profile'], [row.copy()], ['Observed baseline']
    for label, edits in scenarios.items():
        if label == 'Original profile' or not edits or set(edits) - allowed:
            raise ValueError('Scenario must name an allowed nonempty feature edit; identity, context and derived edits are excluded.')
        if not set(edits).issubset(row.index):
            raise ValueError('Profile is missing an edited model input.')
        historical = bool(set(edits) & {grade, approved})
        if historical and not allow_retrospective:
            raise ValueError('Academic record edits are retrospective; explicitly set allow_retrospective=True.')
        new = row.copy(deep=True)
        for key, value in edits.items():
            if not np.isfinite(float(value)):
                raise ValueError('Edited values must be finite.')
            new[key] = value
        for key in ['debtor', 'tuition_fees_up_to_date']:
            if float(new[key]) not in (0, 1):
                raise ValueError('Administrative indicators must be exactly 0 or 1.')
        n, a, e, g = (float(new[key]) for key in [enrolled, approved, evaluations, grade])
        if not np.isfinite([n, a, e, g]).all() or any(v < 0 or not v.is_integer() for v in [n, a, e]):
            raise ValueError('Unit/evaluation counts must be finite nonnegative integers.')
        if a > n or not 0 <= g <= 20:
            raise ValueError('Approved units exceed enrollment or grade lies outside [0, 20].')
        if historical and ((g > 0 and (a == 0 or n == 0 or e == 0)) or (approved in edits and a > max(float(row[approved]), min(n, e)))):
            raise ValueError('Academic edit is inconsistent with enrollment/evaluation support.')
        if not any(float(new[key]) != float(row[key]) for key in edits):
            raise ValueError('Scenario makes no feature change.')
        new['first_semester_pass_rate'] = a/n if n > 0 else 0.
        new['first_semester_no_enrollment'] = int(n == 0)
        new['first_semester_no_evaluations'] = int(e == 0)
        profiles.append(new); labels.append(label)
        kinds.append('Historical input sensitivity' if historical else 'Status-resolution simulation; verify feasibility')
    probabilities = np.asarray(predict_dropout(pd.DataFrame(profiles).reset_index(drop=True)), dtype=float)
    if probabilities.shape != (len(profiles),) or not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError('Callback must return one finite dropout probability in [0, 1] per row.')
    return pd.DataFrame({'scenario': labels, 'evidence_type': kinds,
                         'predicted_dropout_probability': probabilities,
                         'change_percentage_points': 100*(probabilities-probabilities[0]),
                         'actual_dropout_effect_estimated': False})
