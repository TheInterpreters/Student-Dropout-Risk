# Student Dropout Notebook Kit

1. Extract this entire ZIP before opening it.
2. Open Student_Dropout_Project.ipynb in Jupyter or VS Code with a Python 3.12 kernel.
3. Read RUN_NOTEBOOK.md for the execution sequence and dependency instructions.

This notebook is the user's 10 November upload, including saved outputs and the
final saved KeyboardInterrupt. It has not been rerun for this package update.
Opening it is sufficient to read the retained results. The final cell explicitly
starts/resumes a FULL 544-case audit if executed; an earlier preview setting does
not disable that final cell. For a preview, stop at Checks before the final cell.

The original CSV, saved split and existing final-test lock are included, unchanged.
Their public upstream source and checksums are in PUBLIC_INPUT_PROVENANCE.json.
The kit contains no cloud case JSON files, fitted-model bundle, Python environment
or pretrained checkpoint weights. Saved notebook outputs are retained; the local
case folder starts empty. The running cloud audit remains separate and untouched.

The model checkpoint cell uses Path.home() / "tabicl_model" and verifies SHA256.
No Hugging Face API token is needed for the public checkpoint.
Scope: all 544 validation students, with 2,541 training rows used for context.
Final-test execution is not part of this audit.
