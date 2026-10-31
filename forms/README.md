# Human-study forms: fixture build

Status: fixture only. Dummy cases from the validation split, placeholders marked [TBD].
Nothing here is published. Do not run with real cases before the final test run.

## Files
- build_spec.py: builds the case pack, four form specs (A1, A2, B1, B2), and the assignment list (50 main slots, 4 spares (one per form) and 1 pilot link on Form 3; delete the pilot's response row after the pilot).
- test_spec.py: checks the spec (profile fields, validation-only cases, seeded orders, A/B parity, leak scan, assignment).
- render_forms.gs: Apps Script renderer. Creates the six forms and a links sheet.
- out/: generated outputs. Ignored by git (private lookup and codes).

## Run
1. python3 forms/build_spec.py
2. python3 forms/test_spec.py   (must print PASS)
3. Upload out/form_spec.json and out/assignment_fixture.csv to the team's restricted Drive folder.
4. Apps Script (script.google.com, team account): new project, paste render_forms.gs, fill CONFIG, run renderAll(), approve.
5. Check the six forms against the W2.6 checks. Forms stay closed (ACCEPTING_RESPONSES false) until the pilot.

## Placeholders to replace before real use
Consent time, withdrawal deadline, contacts, retention date, instructor name, legend wording (W5.3),
direction in P.B1, study seeds and allocation seed, slots per variant (50 vs 25 conflict).

## Decisions pending (also listed in form_spec.json)
See decisions_pending in out/form_spec.json.
