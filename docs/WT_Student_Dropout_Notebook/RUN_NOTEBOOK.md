# Run Student Dropout Project in Jupyter

[Download the current Notebook Kit](https://github.com/Witchayada-T/Data-Science/raw/refs/heads/main/Downloads/Student_Dropout_Notebook_Kit.zip), extract the whole ZIP, and open `Student_Dropout_Project.ipynb` inside it. You can also [view the notebook in GitHub](Student_Dropout_Project.ipynb).

## Current notebook version

The notebook matches the user's 10 November upload byte for byte, including all 23 saved outputs, cell execution counts and metadata. Its last saved output is a `KeyboardInterrupt` from an interrupted local run. These retained outputs are historical local results, not the current cloud audit's progress. No cells were executed during the Git update.

**The final code cell explicitly sets `AUDIT_MODE="full"` and starts/resumes all 544 validation cases.** This happens even though the earlier configuration cell defaults to preview mode. Open the notebook to read its results without running cells. For a setup/model check, run the cells through the **Checks** section and stop before the final audit cell.

## Run locally

1. Keep the extracted notebook beside the extracted `Student Dropout Project` folder.
2. Select a Python 3.12 kernel with the project's dependencies installed.
3. If folder detection fails, set `PROJECT_FOLDER` to the exact `Student-Dropout-Risk` code folder, for example:

   ```python
   PROJECT_FOLDER = "C:/Users/your-name/Downloads/Student_Dropout_Notebook_Kit/Student Dropout Project/Code/Student-Dropout-Risk"
   ```

4. Run setup, data and model cells in order. The checkpoint cell downloads the official model to `Path.home() / "tabicl_model"` and verifies its SHA256. No Hugging Face API token is required.
5. To start or resume the full local explanation audit, deliberately run the final code cell. It uses UTF-8 direct file logging and saves each completed case. Avoid duplicate local jobs.
6. After all 544 case files exist, rerun the report cell with `REPORT_MODE="auto"` to display the complete report. The audit driver also generates it automatically on successful completion.

The kit includes the original CSV, saved split and existing final-test lock, with their upstream provenance. It excludes a fitted-model bundle, pretrained checkpoint weights, Python environments and case JSON files from the cloud run. Its saved notebook outputs are preserved from the upload; its case-output folder starts empty.

The scope is every one of the 544 validation students. The 2,541 training students provide fitting context and explanation references. Final-test execution is outside this workflow. Predictions use a refit with recorded settings; the original private saved fitted model was not supplied.

## Current cloud audit

The ongoing cloud audit runs from a separate source snapshot. Updating this notebook or downloading the kit does not restart it or change its files. See the [current process and file guide](Student%20Dropout%20Project/CURRENT_PROCESS_AND_FILE_GUIDE.md) for its live progress location.

A new local run has its own provenance. Do not merge case JSON files across machines or bypass a probability/source-hash mismatch.

## Install from a Windows PowerShell terminal

If the notebook reports missing or mismatched package versions, paste this in
**VS Code → Terminal → New Terminal** using PowerShell. It creates a dedicated
Python 3.12 environment and registers a selectable notebook kernel.

```powershell
py -3.12 -m venv .venv-dropout
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 is required. Install it and retry." }
$dropoutPython = (Resolve-Path ".venv-dropout\Scripts\python.exe").Path

& $dropoutPython -m pip install --upgrade pip
& $dropoutPython -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0
& $dropoutPython -m pip install pandas==3.0.5 numpy==2.5.3 scipy==1.18.1 scikit-learn==1.9.1 joblib==1.6.0 matplotlib==3.11.2 seaborn==0.13.2 tabicl==2.2.0 xgboost==3.4.1 interpret==0.7.8 shap==0.52.0 jupyter==1.1.1 ipykernel==7.3.0 python-docx==1.2.0
& $dropoutPython -m pip check
& $dropoutPython -m ipykernel install --user --name student-dropout --display-name "Student Dropout (Python 3.12)"
```

After successful installation, select **Student Dropout (Python 3.12)** in the
notebook's **Select Kernel** menu, restart the kernel, and run from the top.
The terminal's Python and the selected notebook kernel can otherwise be different.
