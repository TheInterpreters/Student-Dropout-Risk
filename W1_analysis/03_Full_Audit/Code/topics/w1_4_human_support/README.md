# W1.4 — Human support to improve the opportunity to remain enrolled

`analysis.py` creates a support catalogue and case review prompts. It does not estimate how many dropouts an action prevents. Confirmed student needs and preferences take precedence over SHAP signals. Protected/background attributes do not become instructions to change the student. Support remains open to unflagged students.

## Single support options and coordinated pairs

| Confirmed barrier | Practical human action | Coordinated pair to consider |
| --- | --- | --- |
| Learning/course progress | Tutor identifies specific future-course difficulties; agree attainable study and assignment goals. | Academic tutoring + practical engagement support. |
| Participation/access | Adviser asks about timetable, work, caring, transport, accessibility and wellbeing barriers; arrange feasible support/referrals. | Engagement support + financial assistance where affordability is a confirmed barrier. |
| Affordability/registration | Aid adviser checks bursaries, emergency assistance, allowed payment plans and hold resolution. | Academic tutoring + financial-aid coordination where both needs are confirmed. |
| Course fit/workload | Discuss programme/timetable options; check funding and programme requirements before changes. | Personalised academic advising + relevant support chosen with the student. |

Use one coordinating adviser, propose first contact within one week, agree the student's priorities, and review after two weeks. Timelines are operational suggestions, not model-derived rules. Historical first-semester grades cannot be changed prospectively; target future study conditions, engagement and completion.

The original financial-status recourse moved 17 of 108 flagged students out of the model's capacity set. Fifty flagged students had no available tuition/debt change under that restricted test. These counts measure a model experiment, not the effectiveness of human support.

## Measure the actual outcome

The empty `results/future_retention_follow_up_template.csv` records confirmed needs, support offered/accepted and later enrollment/completion. Record baseline information before support. Do not use later support/outcome variables as baseline predictors. Distinguish graduation, approved leave and transfer from dropout, and agree the outcome window before evaluation.

To compare real single and combined supports, evaluate additional academic support, additional financial/navigation support, both, and usual available support in a prospective design appropriate to the institution. Standard necessary services should remain available. This audit does not select a causally best intervention arm or assign students to a programme.

## Evidence informing proposals

- [What Works Clearinghouse: Effective Advising for Postsecondary Students](https://ies.ed.gov/ncee/wwc/PracticeGuide/28) recommends comprehensive integrated academic/non-academic advising, sustained personalised relationships, mentoring and coaching.
- [MDRC: Doubling Graduation Rates](https://www.mdrc.org/work/publications/doubling-graduation-rates) reports a randomized evaluation of CUNY ASAP's comprehensive programme, including advising, tutoring and financial supports. Its three-year degree results were 40% versus 22% in that setting. This is evidence about that programme bundle, not an estimate for this institution or isolated proof that a particular pair of supports is best.

Current data contain no intervention assignments or future retention outcomes. The support options are student-confirmed proposals requiring local evaluation, not guaranteed prevention.

## Read in this order

1. `w1_1_local_explanations/feature_guide.py` defines all 33 model inputs; `results/all_33_feature_definitions.csv` lists meanings and action context. `explain_case(record)` shows all 27 signed contributions for a selected student. Positive means a higher model probability relative to the SHAP background; negative means a lower probability. The two academic groups have only group totals saved, so separate contributions for their members are unavailable.
2. `w1_4_human_support/scenarios.py` validates saved before/after probabilities and exports `results/recorded_scenario_summary.csv`. All 2,508 broad rows and 590 administrative rows remain in the case exports inside the full ZIP. Original/no-change rows are not effect experiments. The scenario cohorts differ; this is not an intervention-efficacy ranking.
3. `make_support_plan(record)` proposes human review and practical support; use confirmed needs to choose single or combined assistance. Historical grade/credit edits are not prospective actions. Monitor future enrollment and progress rather than treating a flag change as success.

The executed W1 notebook provides the full sequence, a named-case example and an optional prediction-only wrapper for new four-input edits. The optional function needs an already-fitted model, does not fit/download anything and never overwrites audit evidence. Other feature edits were not exhaustively simulated in the recorded scenarios; their SHAP/masking contributions are not substitutes for a new prediction.
