# W5 (Lucas): explanation images, assignment lists, demo card, scoring script

Owner: Lucas. Reviewer: see `docs/TASK_SPLIT.md` section 10. Task definitions and deadlines are in
`docs/TASK_SPLIT.md` section 4 (W5); this page says where the work lives and how to run it.

## Status

| ID | Task | Where | Status |
|---|---|---|---|
| W5.8 | Seeded assignment list (50 slots + 4 spares, 25/25) | `scripts/make_assignment_list.py`, `tests/test_assignment_list.py` | Done, PR #2 in review |
| W5.3 | Image renderer (Group B charts, optional profile cards) | `forms/render_images.py`, `tests/test_render_images.py` | Done, PR #3 in review |
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
- Forms: A1/A2 = Group A (seeded order / exact reverse), B1/B2 = Group B (same).
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