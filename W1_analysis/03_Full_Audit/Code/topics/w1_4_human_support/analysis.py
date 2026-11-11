"""Translate review signals into support conversations; never promise prevention."""
import pandas as pd

DOMAIN_GROUPS = {
    'academic': {'first_semester_progress'},
    'engagement': {'first_semester_participation'},
    'financial': {'tuition_fees_up_to_date', 'debtor', 'scholarship_holder'},
    'course_fit': {'course'},
}
CATALOGUE = [
    {'code': 'adviser_check_in', 'owner': 'Named student adviser',
     'verification_question': 'What is making continued study difficult, and what support does the student want?',
     'human_action': 'Agree a confidential support plan and one named contact; keep self-referral open to unflagged students.',
     'student_action': 'Choose priorities and preferred contact method; participation is voluntary.',
     'follow_up': 'Proposed first contact within one week; agree a review after two weeks.',
     'outcome_to_monitor': 'Support uptake, unresolved barriers, continued enrollment and completion.'},
    {'code': 'academic_support', 'owner': 'Adviser and course tutor',
     'verification_question': 'Which future course skills, assignments or study arrangements need support?',
     'human_action': 'Arrange targeted tutoring, an attainable study plan and instructor-approved catch-up options.',
     'student_action': 'Agree achievable weekly study/assignment goals and attend suitable support sessions.',
     'follow_up': 'Review engagement and future-course progress after two weeks.',
     'outcome_to_monitor': 'Future submissions, attendance, credits earned and continued enrollment.'},
    {'code': 'financial_support', 'owner': 'Financial-aid adviser',
     'verification_question': 'Are tuition, food, transport, books, caring costs or registration holds genuine barriers?',
     'human_action': 'Check grant/bursary eligibility, emergency assistance, permitted payment plans and registration-hold resolution.',
     'student_action': 'Choose acceptable assistance and provide only information needed for eligibility checks.',
     'follow_up': 'Review before relevant payment/registration deadlines.',
     'outcome_to_monitor': 'Support received, barriers resolved, registration and continued enrollment.'},
    {'code': 'engagement_support', 'owner': 'Student adviser and course staff',
     'verification_question': 'Are work, caring, transport, timetable, accessibility or wellbeing barriers limiting participation?',
     'human_action': 'Discuss feasible scheduling/accessibility arrangements and voluntary referral to relevant services.',
     'student_action': 'Identify practical barriers and choose a manageable participation plan.',
     'follow_up': 'Agree a short review cycle; avoid repeated contacts that add burden.',
     'outcome_to_monitor': 'Future participation, submissions, barrier resolution and continued enrollment.'},
    {'code': 'course_fit_support', 'owner': 'Programme adviser',
     'verification_question': 'Does the programme, timetable or workload fit the student’s goals and circumstances?',
     'human_action': 'Discuss feasible timetable, programme or workload options; check funding and programme rules before changes.',
     'student_action': 'Choose suitable options with an adviser rather than changing records to lower a score.',
     'follow_up': 'Review before programme/timetable deadlines.',
     'outcome_to_monitor': 'Agreed study plan, course engagement, transfer/completion/enrollment status.'},
    {'code': 'academic_financial_bundle', 'owner': 'One coordinating adviser plus tutor and aid adviser',
     'verification_question': 'Has the student confirmed both academic and financial barriers?',
     'human_action': 'Coordinate tutoring and practical financial assistance in one plan, with one follow-up contact.',
     'student_action': 'Agree the combined plan and say whether either component creates extra burden.',
     'follow_up': 'Proposed weekly check-ins initially, adjusted to student preference and need.',
     'outcome_to_monitor': 'Both barriers, support uptake and future enrollment/completion; not a change in model flag.'},
    {'code': 'academic_engagement_bundle', 'owner': 'One coordinating adviser and course tutor',
     'verification_question': 'Has the student confirmed both learning and participation barriers?',
     'human_action': 'Combine targeted tutoring with practical attendance/timetable support in one manageable plan.',
     'student_action': 'Agree realistic study and participation goals, adapted to circumstances.',
     'follow_up': 'Review progress and burden after two weeks.',
     'outcome_to_monitor': 'Future submissions, credits, participation and continued enrollment.'},
    {'code': 'engagement_financial_bundle', 'owner': 'Student adviser and financial-aid adviser',
     'verification_question': 'Has the student confirmed that affordability is limiting participation?',
     'human_action': 'Coordinate feasible financial assistance with access/timetable arrangements.',
     'student_action': 'Choose assistance that addresses the actual barrier.',
     'follow_up': 'Review assistance delivery and participation before relevant deadlines.',
     'outcome_to_monitor': 'Barrier resolution, attendance and continued enrollment/completion.'},
]


def make_support_plan(record, confirmed_needs=None):
    positive = {row['feature_group'] for row in record['baseline_group_contributions_all'] if row['signed_shap'] > 0}
    if confirmed_needs is None:
        needs = {domain: bool(positive & groups) for domain, groups in DOMAIN_GROUPS.items()}
        status = 'needs_student_confirmation'
    else:
        needs = {domain: confirmed_needs.get(domain) is True for domain in DOMAIN_GROUPS}
        status = 'human_confirmed_needs'
    codes = ['adviser_check_in']
    for domain, code in [('academic', 'academic_support'), ('engagement', 'engagement_support'), ('financial', 'financial_support'), ('course_fit', 'course_fit_support')]:
        if needs[domain]:
            codes.append(code)
    if needs['academic'] and needs['financial']:
        codes.append('academic_financial_bundle')
    if needs['academic'] and needs['engagement']:
        codes.append('academic_engagement_bundle')
    if needs['engagement'] and needs['financial']:
        codes.append('engagement_financial_bundle')
    return {'source_row_id': record['source_row_id'], 'model_outreach_flag': record.get('flagged'),
            'status': status, 'proposed_support_codes': codes,
            'intervention_effect_estimated': False,
            'note': 'Review prompts, not diagnoses, automatic resource decisions or estimated dropout reductions.'}


def analyse(records, intake=None):
    intake = intake or {}
    plans = [make_support_plan(r, intake.get(r['source_row_id'])) for r in records]
    counts = {row['code']: sum(row['code'] in p['proposed_support_codes'] for p in plans) for row in CATALOGUE}
    catalogue = pd.DataFrame([{**row, 'cases_with_review_prompt': counts[row['code']],
                               'effect_on_actual_dropout_estimated': False} for row in CATALOGUE])
    return {'catalogue': catalogue, 'case_review': pd.DataFrame(plans),
            'follow_up_columns': ['anonymous_student_id', 'intake_date', 'student_agreed_to_support',
                                 'confirmed_academic_need', 'confirmed_engagement_need', 'confirmed_financial_need', 'confirmed_course_fit_need',
                                 'support_offered', 'support_accepted', 'support_start_date', 'review_date',
                                 'future_assignment_completion', 'future_credits_earned', 'next_term_enrollment_status',
                                 'credential_completed', 'approved_leave_or_transfer', 'withdrawal_status']}
