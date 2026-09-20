# Task List — Trustworthy Explanations for Student Dropout Risk

_Based on `handoff.md` (updated 2026-09-19). Status: proposal complete, methodology frozen. Tasks below are what's left to actually run the study. No task is assigned yet — to be split when the team meets._

## Core pipeline (in order, per handoff §4)

- [ ] **Faithfulness & stability audit** — run the pre-specified 20-case explanation faithfulness/stability audit on the validation split (deletion curves, 10 reruns per case, top-5 overlap, perturbation test).
- [ ] **Interface build** — build and pilot the two-mode browser interface from `docs/interface_spec.md`:
  - [ ] Decision-support demonstration view
  - [ ] Blinded A/B study view
  - [ ] Verify study mode reveals no answer/feedback until all 10 scored cases are complete
- [ ] **Final test evaluation** — once all acceptance checks pass, run all frozen models exactly once on the untouched test split (no re-tuning after).
- [ ] **Generate study artifacts** — produce explanations, faithfulness/stability results, constrained counterfactuals, subgroup diagnostics, and the 10 pre-specified study cases.
- [ ] **Human study**
  - [ ] Confirm with course instructor whether AIT ethics approval is required, and obtain it if so
  - [ ] Recruit participants (target 8–10, minimum 4), split as evenly as possible into Group A / Group B
  - [ ] Obtain consent from all participants
  - [ ] Run the study (1 unscored practice case + 10 scored cases, no feedback until all 10 are locked)
  - [ ] Code the qualitative responses (rationales, support actions, missing-info comments) using two reviewers on the agreed subset
  - [ ] Analyze accuracy/time descriptively (no significance claims — sample is small)
- [ ] **Model card & reproducibility**
  - [ ] Complete `docs/MODEL_CARD.md`
  - [ ] Provide one clean-clone command that regenerates all reported tables/figures

## Optional / time-permitting (per handoff §3)

- [ ] Sensitivity check: treat "Enrolled" as a third class or group it with non-dropout, and report how this changes results
- [ ] Sensitivity check: compare an admission-time feature window vs. the primary post-first-semester window

## Housekeeping / repo hygiene

- [ ] Keep final test set untouched until the model/explanation protocol is fully frozen (no peeking)
- [ ] Keep raw free-text human-study responses out of version control; report only aggregate/paraphrased results
- [ ] Verify `.venv-core` environment still reproduces all 26 tracked tests before final submission
- [ ] Confirm repo scope is clean — no OfS/text-analysis material re-included from the archived branch

---
_Not included: anything already done (EDA, split, baselines, TabICL integration, protocol v1.2 freeze, human-study instrument/schema drafting) — see handoff.md §2 for the full completed list._