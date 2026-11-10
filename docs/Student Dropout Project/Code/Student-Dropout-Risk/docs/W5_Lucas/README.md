# W5 (Lucas): explanation images, assignment lists, demo card, scoring script

Owner: Lucas. Reviewer: see `docs/TASK_SPLIT.md` section 10. Task definitions and deadlines are in
`docs/TASK_SPLIT.md` section 4 (W5); this page says where the work lives and how to run it.

## Status

Updated 2 Nov, evening. **Completed by Yolanda** identifies work she performed;
**integrated and verified by Yolanda** identifies integration/checking of Lucas's existing
implementations. Original generator/renderer authorship is preserved; neither label claims
Lucas's independent approval. Operational review remains separate from implementation/tests.

| ID | Task | Where | Status |
|---|---|---|---|
| W5.8 | Seeded assignment list (50 main + 4 spares + 1 pilot, 25/25 main groups) | `scripts/make_assignment_list.py`, `tests/test_assignment_list.py` | **Canonical assignment completed by Yolanda.** Lucas's PR #2 generator integrated and verified by Yolanda, with CLI/schema/pilot fixes; CSV generated once, exact seed/hash reproduced, 8 tests pass. Local seal records owner authorization, not independent review; Harry/Lucas acknowledgement pending |
| W5.3 | Renderer and 11 genuine Group B charts | `forms/render_images.py`, `tests/test_render_images.py` | **Lucas's PR #3 renderer integrated and verified by Yolanda; genuine chart generation completed by Yolanda.** Text checks pass; one real chart inspected. Remaining: full visual/profile/order parity and live insertion |
| W5.6 | Scoring and analysis script | `scripts/analyze_human_study.py` | **Implementation and synthetic scoring/exclusion/practice-check tests completed by Yolanda.** Remaining: Lucas's independent review and actual study-data analysis after collection |
| W5.9 | Coding assignment and agreement script | `scripts/assign_human_coding.py` | **Implementation and synthetic assignment/agreement tests completed by Yolanda.** Remaining: codebook/training, independent review and actual coding |
| W5.1 | Static demo card (validation fixture only) | not verified complete | **Pending**; original due Wed 11 Nov |
| W5.5 | Full-audit deletion/stability figures | `scripts/run_explanation_audit.py` | **Omitted** with full audit; no completed empirical figures claimed; disclose reduced evidence |
| W3.8 | Independent clean-clone verification | not verified complete | **Pending**; original due Wed 18 Nov; verify saved final evidence, never repeat final evaluation |

Update this table when a task changes.

## W5.8: assignment list

    python -m unittest tests.test_assignment_list -v

- **Already generated; do not rerun the generator.** Use the exact files in ignored
  `data/human_study/`: `assignment_list.csv`, `assignment_list_RULES.txt` (private seed/hash/rules)
  and `assignment_seal.json` (owner-authorized local sealing, no independent sign-off).
- The existing generator command `python scripts/make_assignment_list.py --seed <SEED>` overwrites
  files; it is not a remaining step and must not be used on the canonical output. Verify the
  CSV against its private seal/rules instead. Tests above use temporary/dummy data only.
- CSV columns match W2: `slot,participant_code,variant_id,group,role`. The pilot is `PILOT-01`
  on B1, excluded from the 50 main participants and removed from study analysis.
- Forms: A1/A2 = Group A (seeded order / exact reverse), B1/B2 = Group B (same).
- This block-randomised assignment differs from the W2 builder's default even with the same seed.
  The one canonical list is now locally sealed. Use this CSV as
  `ASSIGNMENT_FILE_ID` in `forms/render_forms.gs` and the same CSV with
  `forms/transform_responses.py --assignment`. Do not mix or replace lists after sending links.
- The 8 tests include CLI execution, mocked Apps Script pre-filled links and synthetic response
  CSV transformation for all four forms, spares and pilot. They do not replace live acceptance checks.
- **The real seed, the CSV and the codes are not in the repo.** Anyone with the seed can rebuild the
  list and see each participant's group. They are currently in local ignored storage; restricted
  handover to the coordinator/designated reviewer remains to be acknowledged.
  Tests use a dummy seed.

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

  ## W5.6 and W5.9 handover

  Commands and input shapes are in `docs/HANDOFF.md` section 12. Use `--label dummy` for fake tests,
  never publish them as study findings. Analysis produces participant accuracy across exactly ten cases
  and descriptive group means, not 500 independent observations or significance tests. Exclusions are
  logged; practice mistakes do not cause automatic exclusion. Group B practice-check counts include denominators.

  Coding uses five pseudonymous member IDs (M1-M5), a private send log with `participant_code,recruiter`,
  one primary coder who is not the recruiter and a random 20% second coder who is neither recruiter nor
  primary. Counts are greedily balanced among eligible coders; recruitment constraints can prevent exact
  balance. Worksheets omit group/recruiter columns, but free text is still sensitive and may reveal group.
  Distribute only each coder's own worksheet through restricted storage. Fill one agreed code per text item
  according to the pre-agreed codebook; do not mix differing multi-code conventions. The agreement command
  requires every double-coded case/field pair and reports exact raw agreement, not chance-corrected agreement.

  Synthetic checks are not an independent review of these new scripts. Keep a different reviewer in the
  loop before using their outputs in the report. Static demo card W5.1 and clean-clone verification W3.8
  remain operational deliverables; they are not claimed complete.