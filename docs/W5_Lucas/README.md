# W5 (Lucas): explanation images, assignment lists, demo card, scoring script

Owner: Lucas. Reviewer: see `docs/TASK_SPLIT.md` section 10. Task definitions and deadlines are in
`docs/TASK_SPLIT.md` section 4 (W5); this page says where the work lives and how to run it.

## Status

| ID | Task | Where | Status |
|---|---|---|---|
| W5.8 | Seeded assignment list (50 main + 4 spares + 1 pilot, 25/25 main groups) | `scripts/make_assignment_list.py`, `tests/test_assignment_list.py` | Implemented in PR #2; CLI/schema/pilot fixes and 8 passing tests verified by Yolanda on 2 Nov. Private seed/list sealing remains |
| W5.3 | Image renderer (Group B charts, optional profile cards) | `forms/render_images.py`, `tests/test_render_images.py` | Implemented in PR #3; 6 tests pass and sample charts/profile inspected by Yolanda on 2 Nov. Live form insertion/checks remain |
| W5.6 | Scoring and analysis script | not started | Due Fri 6 Nov |
| W5.9 | Coding assignment and agreement script | not started | Due Fri 6 Nov |
| W5.1 | Static demo card (from a validation fixture) | not started | Due Wed 11 Nov |
| W5.5 | Audit figures (deletion curves, stability plots) | not started | Due Wed 11 Nov |
| W3.8 | Clean-clone verification | not started | Due Wed 18 Nov |

Update this table when a task changes.

## W5.8: assignment list

    python scripts/make_assignment_list.py --seed <SEED>
    python -m unittest tests.test_assignment_list -v

- Writes `data/human_study/assignment_list.csv` and `assignment_list_RULES.txt` (git-ignored).
- CSV columns match W2: `slot,participant_code,variant_id,group,role`. The pilot is `PILOT-01`
  on B1, excluded from the 50 main participants and removed from study analysis.
- Forms: A1/A2 = Group A (seeded order / exact reverse), B1/B2 = Group B (same).
- This block-randomised assignment differs from the W2 builder's default even with the same seed.
  Agree and seal ONE list before links are distributed. If adopting W5, use this CSV as
  `ASSIGNMENT_FILE_ID` in `forms/render_forms.gs` and the same CSV with
  `forms/transform_responses.py --assignment`. Do not mix or replace lists after sending links.
- The 8 tests include CLI execution, mocked Apps Script pre-filled links and synthetic response
  CSV transformation for all four forms, spares and pilot. They do not replace live acceptance checks.
- **The real seed, the CSV and the codes are not in the repo.** Anyone with the seed can rebuild the
  list and see each participant's group. They are held by the W4 owner and the W4 reviewer only
  (rule 4 in `docs/TASK_SPLIT.md`). Tests use a dummy seed.

## W5.3: images

    python forms/build_spec.py
    python forms/render_images.py forms/out/case_pack_fixture.json [--profiles]
    python -m unittest tests.test_render_images -v

- `chart_<case_id>.png`: the Group B contribution chart. Right = more worried, left = less worried,
  longer bar = bigger effect. No numbers, no base value, probability, score, capacity boundary,
  class or case ID. `check_chart_text()` refuses to save a chart whose text would reveal them.
- `profile_<case_id>.png` (only with `--profiles`): not used in the forms. The form builder writes
  the profile as text from `forms/labels.py`. Kept for the W5.1 demo card and report screenshots.
- Always use the default `--scale pack` (one shared scale for all 11 charts). Never `--scale case`,
  otherwise "longer = bigger effect" stops being true across students.
- The legend stays on every chart. P.B1 and P.B2 are therefore reading checks, reported
  descriptively; nobody is excluded because of them.
- Fixture bars are placeholders, not results. Images go to `forms/out/images_<kind>/` (git-ignored).
  Study images show real test cases and are never committed.