# Local research interface: user guide


The interface is a research demonstration of how the model could support decisions about whom to
offer a support contact. It is not a deployed service and must not be used for real students.

**Prerequisites:** from the repository root, activate the pinned environment (`.venv-core`, Python 3.12,
`pip install -r requirements.txt`). The saved page needs only files already in Git. What-if mode also
needs the private frozen model `data/final_evaluation/selected_model.joblib` (git-ignored, about 2 MB;
obtain it from the model owner and never commit it).

**1. Saved page (no model, works offline):**

```powershell
python scripts/launch_interface.py            # builds interface/student_support_demo.html and opens it
python scripts/launch_interface.py --no-open  # build only; open the HTML file yourself later
```

The HTML file is self-contained: double-click it, or send it to someone, to view it in any browser.
Section 5 (what-if) shows as unavailable in this mode.

**2. What-if mode (frozen model, local only):**

```powershell
python scripts/launch_interface.py --what-if              # opens http://127.0.0.1:8765/
python scripts/launch_interface.py --what-if --port 8766  # if port 8765 is busy
```

Startup takes about 20 seconds (it hash-checks the model against `artifacts/final_test.lock`, scores
the 544 validation students and builds the context cache described below). Keep the terminal open while you use the page; press Ctrl+C to stop.
The server listens only on your own computer (127.0.0.1).

**Using the page:**
1. Choose a student with the **Student** list, **◀ Previous / Next ▶**, the ← → keys, the **Example**
   menu, by clicking the risk curve, or with `#student=<record id>` in the address (e.g. `#student=174`).
2. Read sections 1–4: whether the student is flagged (top 108 of 544 = 20%), the five main reasons,
   how stable those reasons are, and whether clearing fees or debt would change the flag. Hover over
   the curve, bars, stability rows and **i** icons for explanations.
3. In section 5 (what-if mode only), change first-semester results or fee/debt/scholarship status, or
   use a quick example, then press **Predict** (under 1 second; a few seconds if "also recompute
   the reasons" is ticked). Startup takes about 20 seconds: the server scores all 544 students, then
   stores the training context in TabICL's in-memory cache and checks that it reproduces the frozen
   scores and ranking exactly before using it (otherwise it falls back to about 10 seconds per
   prediction). The result shows the new estimate, rank and flag, and a purple diamond on
   the section 1 curve. **Reset to recorded values** restores the student.

**What what-if mode allows:** only validation students, and only first-semester units, evaluations,
grade, fees, debt and scholarship can change; age, gender, nationality, family and background fields are
fixed. Impossible combinations (for example more units passed than enrolled) are rejected with a reason.
Other students' scores stay fixed. Nothing is saved or retrained and the test split is never read.
Results show how the model responds, not what would happen to a student or what they should do.

**Troubleshooting:**
- *Section 5 says "not available":* you opened the saved HTML file; start with `--what-if` and use the
  `http://127.0.0.1:8765/` address instead.
- *Blank or outdated page:* an older server may still hold the port. Close its terminal (or stop the
  Python process) and start again, or use `--port 8766`; then reload with Ctrl+F5. The server now
  refuses to start if the port is taken.
- *"needs the private frozen model file":* the model file is missing; the saved page still works.

**Checked (11 Nov, with the context cache on):** what-if reproduces all 104 saved fee/debt scenario
predictions, including the 27 that move a student out of the top 20% (largest probability difference
0.0000041, same ranks); an unedited student returns their saved rank, flag and score exactly; and
recomputed reasons for students 174 and 916 match the saved ones within 0.000001. Tests: `tests/test_interface.py`, `tests/test_whatif.py`.

