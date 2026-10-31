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
5. Read the log: `ROUTE BY HAND`, `SET BY HAND` or `CHART MISSING` lines mean something must be done by hand.
6. Open one link in a private window: the form must open without a sign-in. Keep
   `ACCEPTING_RESPONSES` false except during tests.

## Dry run (W2.5, Thu 5 Nov)
1. Turn responses on for the test only. Submit fake answers (write "fake" in the text boxes) through a
   few links from the links sheet, as a participant would online: at least one per form, one
   "I do not agree" and the pilot link.
2. In the response Sheet each form has its own tab. Download each tab as CSV.
3. `python3 forms/transform_responses.py <the CSVs> --assignment forms/out/assignment_fixture.csv --spec forms/out/form_spec.json --label dummy`
4. Check `forms/out/responses_long_dummy.csv` (10 rows per kept participant, right case order) and the
   dropped counts. Then delete the test responses in each form and in the Sheet, and turn responses off.

## Real forms (W2.7, Thu 12 Nov)
1. Check W3's export: `python3 forms/case_pack.py case_pack_study.json private_lookup_study.json` (must print PASS).
2. `python3 forms/build_spec.py --case-pack case_pack_study.json --private private_lookup_study.json`
   (refuses a pack that fails the check; same seeds, so the same codes and forms).
3. Put W5.3's `chart_<case>.png` files in one restricted Drive folder and set `CHART_FOLDER_ID`.
4. Set `RESPONSE_SHEET_ID` to the real restricted sheet (W4 owner and reviewer only), upload
   `out/form_spec.json` and `out/assignment_study.csv`, run `renderAll()`. Never upload the private file.
5. Repeat the A/B parity check and open each form once.

## Still open
Final seeds (W5.8, recorded before Mon 2 Nov) and `decisions_pending` in `out/form_spec.json`.
