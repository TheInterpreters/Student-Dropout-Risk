"""Explain every model input without inventing unsaved member-level SHAP values."""
import numpy as np
import pandas as pd

# Labels describe source columns, not a global direction or a causal relationship.
FEATURES = [
    ('curricular_units_1st_sem_approved', 'first_semester_progress', 'First-semester curricular units passed', 'Historical academic record'),
    ('curricular_units_1st_sem_grade', 'first_semester_progress', 'First-semester average grade (0–20)', 'Historical academic record'),
    ('first_semester_pass_rate', 'first_semester_progress', 'Approved / enrolled units; zero when enrollment is zero', 'Derived; recompute from source units'),
    ('curricular_units_1st_sem_enrolled', 'first_semester_participation', 'Number of first-semester curricular units enrolled', 'Historical enrollment record'),
    ('curricular_units_1st_sem_evaluations', 'first_semester_participation', 'Number of first-semester evaluations recorded', 'Historical assessment record; not classroom attendance'),
    ('curricular_units_1st_sem_without_evaluations', 'first_semester_participation', 'First-semester units without evaluations', 'Historical assessment record'),
    ('first_semester_no_enrollment', 'first_semester_participation', 'Indicator that first-semester enrollment is zero', 'Derived; recompute from enrollment'),
    ('first_semester_no_evaluations', 'first_semester_participation', 'Indicator that first-semester evaluation count is zero', 'Derived; recompute from evaluations'),
    ('tuition_fees_up_to_date', 'tuition_fees_up_to_date', 'Tuition fees up to date: 1=yes, 0=no', 'Administrative status; verify balance and assistance options'),
    ('debtor', 'debtor', 'Recorded debtor status: 1=yes, 0=no', 'Administrative status; verify with finance office'),
    ('scholarship_holder', 'scholarship_holder', 'Recorded scholarship holder: 1=yes, 0=no', 'Check eligibility; receiving aid is not a guaranteed score effect'),
    ('course', 'course', 'Programme/course category code', 'Category, not a numeric attainment scale; discuss fit with adviser'),
    ('gender', 'gender', 'Recorded gender category', 'Personal attribute; never a recommended change'),
    ('displaced', 'displaced', 'Recorded displaced-status indicator', 'Context; ask about practical access needs, not changing identity/status to lower risk'),
    ('unemployment_rate', 'unemployment_rate', 'Recorded unemployment-rate context', 'Macroeconomic context; not controlled by a student'),
    ('previous_qualification_grade', 'previous_qualification_grade', 'Grade for the qualification held before enrollment', 'Historical attainment record'),
    ('age_at_enrollment', 'age_at_enrollment', 'Age when the student enrolled', 'Historical/personal attribute; not an action target'),
    ('fathers_qualification', 'fathers_qualification', 'Father’s qualification category', 'Family background; not an action target'),
    ('curricular_units_1st_sem_credited', 'curricular_units_1st_sem_credited', 'First-semester curricular units credited/recognized', 'Historical credit recognition; verify records if incorrect'),
    ('mothers_qualification', 'mothers_qualification', 'Mother’s qualification category', 'Family background; not an action target'),
    ('application_mode', 'application_mode', 'Admission/application route category', 'Historical admission record'),
    ('daytime_evening_attendance', 'daytime_evening_attendance', 'Daytime/evening study regime', 'Study-regime category; not measured attendance frequency'),
    ('gdp', 'gdp', 'Recorded GDP economic context', 'Macroeconomic context; not controlled by a student'),
    ('mothers_occupation', 'mothers_occupation', 'Mother’s occupation category', 'Family background; not an action target'),
    ('fathers_occupation', 'fathers_occupation', 'Father’s occupation category', 'Family background; not an action target'),
    ('admission_grade', 'admission_grade', 'Grade used at admission', 'Historical attainment record'),
    ('application_order', 'application_order', 'Order of the programme in application preferences', 'Historical application record'),
    ('inflation_rate', 'inflation_rate', 'Recorded inflation-rate context', 'Macroeconomic context; not controlled by a student'),
    ('marital_status', 'marital_status', 'Recorded marital-status category', 'Personal context; not an action target'),
    ('previous_qualification', 'previous_qualification', 'Previous qualification category', 'Historical education record'),
    ('nacionality', 'nacionality', 'Recorded nationality category (source spelling retained)', 'Personal attribute; not an action target'),
    ('educational_special_needs', 'educational_special_needs', 'Recorded educational special-needs indicator', 'Check accessibility/support preferences; not an attribute to change'),
    ('international', 'international', 'Recorded international-student indicator', 'Personal/context attribute; offer relevant support without changing identity'),
]


def feature_dictionary():
    guide = pd.DataFrame(FEATURES, columns=['model_column', 'feature_group', 'meaning', 'action_context'])
    grouped = guide.feature_group.isin(['first_semester_progress', 'first_semester_participation'])
    guide['attribution_available'] = np.where(grouped,
        'Group total only; individual member SHAP not saved', 'Individual feature (singleton group)')
    return guide


def explain_case(record):
    """Signed contributions are relative to the SHAP training background, in probability units.

    Member-level SHAP was not retained for the two multi-input groups. The group
    total must not be assigned in full to each member or treated as a causal effect.
    """
    guide = feature_dictionary()
    meanings = guide.groupby('feature_group', sort=False).meaning.agg('; '.join).to_dict()
    rows = []
    for row in record['baseline_group_contributions_all']:
        value = float(row['signed_shap'])
        if not np.isfinite(value):
            raise ValueError('Signed contribution must be finite.')
        members = [c.strip() for c in row['members'].split(',')]
        rows.append({'source_row_id': record['source_row_id'], 'feature_group': row['feature_group'],
                     'members': row['members'], 'meaning': meanings[row['feature_group']],
                     'signed_shap': value, 'contribution_percentage_points': 100*value,
                     'direction': ('Raises this predicted probability' if value > 0 else
                                   'Lowers this predicted probability' if value < 0 else 'Zero recorded contribution'),
                     'attribution_level': 'Group total; member values not saved' if len(members) > 1 else 'Individual feature'})
    return pd.DataFrame(rows).sort_values('signed_shap', key=abs, ascending=False)
