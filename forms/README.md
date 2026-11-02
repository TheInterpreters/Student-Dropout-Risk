# Human-study forms (W2)

Builds the four Google Forms for the human study from one spec. Python makes all content and runs all
checks; Apps Script only renders. What the forms contain: `docs/form_spec.md` (W2.1). Case file format:
`docs/case_pack_contract.md` (W2.2).

Status: test build on 11 dummy validation cases (fixture). The real forms are built on Thu 12 Nov from
the study case pack (W2.7). Nothing is open to participants before the pilot.

## Files
- `build_spec.py`: builds the fixture case pack, the four form specs (A1, A2 = Group A; B1, B2 = Group B)
  and the assignment list (50 main slots, 4 spares (one per form), 1 pilot link on Form 3; delete the
  pilot's response row after the pilot).
- `labels.py`: plain-language labels for the profile card (UCI codebook).
- `case_pack.py`: the W2.2 case-pack check. Also run it on W3's export.
- `transform_responses.py`: W2.8. Turns the response Sheet export into `responses_long_<label>.csv`
  (template columns) and `responses_participants_<label>.csv`; drops declines, the pilot code and bad codes.
- `test_spec.py`: checks everything; must print PASS.
- `render_forms.gs`: Apps Script renderer; makes the four forms and a links sheet.
- `out/`: generated files. Ignored by git (private lookup and participant codes).

## Test build (now)
1. `python3 forms/build_spec.py`
2. `python3 forms/test_spec.py` (must print PASS)
3. Upload `out/form_spec.json` and `out/assignment_fixture.csv` to the restricted Drive folder,
   overwriting the old copies so the file IDs stay the same.
4. Apps Script: paste `render_forms.gs`, fill CONFIG (file IDs, the TEST response sheet, optional
   `CHART_FOLDER_ID`), trash the old forms and links sheet, run `renderAll()`.
5. Each form is closed immediately after creation, before other settings/routing. A failure to
   close aborts the build: inspect the newly created form and close it manually before retrying.
   If opening the completed forms fails partway, the script attempts to close all four again and
   reports any that require manual closure. Do not distribute links after any error.
   `CHART MISSING` warnings are allowed only for fixtures, never real study builds.
6. Open one link in a private window: the form must open without a sign-in. Keep
   `ACCEPTING_RESPONSES` false except during tests.

## Dry run (W2.5, Thu 5 Nov)
1. Turn responses on for the test only. Submit fake answers (write "fake" in the text boxes) through a
   few links from the links sheet, as a participant would online: at least one per form, one
   "I do not agree" and the pilot link.
2. In the response Sheet each form has its own tab. Download each tab as CSV.
3. `python3 forms/transform_responses.py A1.csv A2.csv B1.csv B2.csv --variants A1 A2 B1 B2 --assignment forms/out/assignment_fixture.csv --spec forms/out/form_spec.json --label dummy`
4. Check `forms/out/responses_long_dummy.csv` (10 rows per kept participant, right case order) and the
   dropped counts. Then delete the test responses in each form and in the Sheet, and turn responses off.

## Real forms (W2.7, Thu 12 Nov)
1. Check W3's export: `python3 forms/case_pack.py case_pack_study.json private_lookup_study.json` (must print PASS).
2. `python3 forms/build_spec.py --case-pack case_pack_study.json --private private_lookup_study.json --assignment data/human_study/assignment_list.csv`
   (refuses invalid provenance or assignment; the sealed W5 codes are reused, not regenerated).
3. Put W5.3's `chart_<case>.png` files in one restricted Drive folder and set `CHART_FOLDER_ID`.
4. Set `RESPONSE_SHEET_ID` to the real restricted sheet (W4 owner and reviewer only), upload
   `out/form_spec.json` and `out/assignment_study.csv`, run `renderAll()`. Never upload the private file.
5. Repeat the A/B parity check and open each form once.

## Still open
Final order seed, privately sealed W5 assignment (W5.8), and `decisions_pending` in `out/form_spec.json`.
The code is ready for member validation; real-model dry runs and live acceptance are not certified.

## W5 block-randomised assignment option

Lucas's generator is available as `scripts/make_assignment_list.py`:

```
python scripts/make_assignment_list.py --seed <privately-agreed-seed>
python -m unittest tests.test_assignment_list -v
```

It writes `data/human_study/assignment_list.csv` and a private rules/hash file (git-ignored).
The CSV uses the W2 columns `slot,participant_code,variant_id,group,role`, with 50 main slots,
4 spares and `PILOT-01` on B1. Main slots use permuted blocks of four; codes use Lucas's
easy-to-read alphabet. W2's existing default assignment generation is unchanged.

**The study handoff uses W5; privately seal its assignment before distributing links.** The W5 algorithm produces different
codes and allocations from `build_spec.py`, even with the same seed. If adopting W5, upload this
CSV instead of `assignment_fixture.csv`/`assignment_study.csv` as `ASSIGNMENT_FILE_ID` for
`render_forms.gs`, and use this exact CSV with `transform_responses.py --assignment` in both the
dry run and study. Do not mix lists, regenerate with another seed or switch lists after links
have been sent. Rebuilds of the W2 form spec do not replace the chosen W5 assignment.
Use `build_spec.py --assignment data/human_study/assignment_list.csv` in the fixture dry run too,
so both the test and study builds exercise the same handoff. W2's default assignment remains only
for backwards-compatible fixture tests. W5 main form counts are A1=13, A2=12, B1=12, B2=13.

The integration test writes a dummy assignment, submits synthetic CSV exports for all four
form layouts (including spares and pilot), and checks response transformation and case order.
When Node.js is available, it also runs the actual `writeLinks_` Apps Script function with
mock Google services to verify that all 55 codes are routed to their assigned forms.
It does not replace the live Google Forms/Sheet acceptance checks.

## Source-form identity and fail-closed rendering

Export each actual form's response tab separately and record which tab belongs to A1/A2/B1/B2.
Pass one `--variants` value per export in the same order. Same-group forms have identical question
headers, so neither the file contents nor the editable participant code prove which form was used.
The transform rejects an incorrect source-group declaration and reports codes belonging to another
variant. Do not guess tab identity from participant codes or rename an unknown tab and continue.

The Apps Script now throws on essential routing/login-setting failures, and study builds refuse
missing charts before creating forms. All forms start closed; `ACCEPTING_RESPONSES` is applied only
after all four builds and link generation succeed. Set it false for initial rendering. A later
failure can leave partially created **closed** forms: inspect and remove those before retrying.
Google Drive permissions and draft-saving behaviour still need manual verification.

For private scoring/coding commands, final-run safeguards and member responsibilities see
`docs/HANDOFF.md` section 12. Only aggregate outputs may be shared; free text and participant codes
stay in the restricted store, including coding worksheets and exclusion files.
