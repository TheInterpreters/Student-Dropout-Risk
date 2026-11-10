# TabICL 2.2.0 / checkpoint installation for Noey W1 (Windows)

**Source:** Official TabICL pretrained model `jingang/TabICL`, file `tabicl-classifier-v2-20260212.ckpt`. The official Python API downloads it to the Hugging Face cache when used, or you can download it before the first model fit. Published file checksum SHA-256: `bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0` (check against owner-provided frozen manifest too).

## Automatic installation

1. In Windows PowerShell, navigate to your clone of `TheInterpreters/Student-Dropout-Risk`.
2. Place the **complete** `W1_Noey_Enhanced` folder beside the repo's `src/` folder.
3. Run:

```powershell
.\W1_Noey_Enhanced\scripts\install_tabicl_checkpoint.ps1
```

If Windows blocks `.ps1` scripts, use one-time process-local permission only:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\W1_Noey_Enhanced\scripts\install_tabicl_checkpoint.ps1
```

The installer uses existing `.venv-core` if present; otherwise it creates one with Python 3.12. It installs versions from `requirements.txt`, verifies dependencies and retrieves the official checkpoint, without fitting a model or accessing the test split. If packages are already installed, use `-SkipPackageInstall`.

## Manual alternative

```powershell
py -3.12 --version
py -3.12 -m venv .venv-core
.\.venv-core\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-core\Scripts\python.exe -c "from huggingface_hub import hf_hub_download; print(hf_hub_download(repo_id='jingang/TabICL', filename='tabicl-classifier-v2-20260212.ckpt'))"
```

If `.venv-core` already exists, **skip the venv creation command** and simply use its Python.

## After the checkpoint downloads

```powershell
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\run_enhanced_audit.py --check
.\.venv-core\Scripts\python.exe W1_Noey_Enhanced\scripts\student_improvement_simulation.py --run
```

The second command performs real TabICL train/validation-only work; it does not run the final-test script. Do not run the final test again. Full enhanced audit (`--run`) is more computationally intensive and should be performed only after verifying available storage and runtime.

## Common issues

- `No suitable Python runtime`: install 64-bit Python 3.12, then retry.
- `ModuleNotFoundError: tabicl`: make sure every command uses `.\.venv-core\Scripts\python.exe`, **not** an unrelated global Python / Jupyter kernel.
- Connection error / 401 / SSL: checkpoint download requires access to `https://huggingface.co/jingang/TabICL`; inspect network/proxy settings and try again. Do not use untrusted model mirrors.
- Can't find `requirements.txt`: run from the correct repository root and copy the W1 folder next to `src/`, not into `src/`.
- CUDA unavailable: the project's selected TabICL is configured with `device='cpu'`; GPU is not necessary.
- SHA mismatch: stop; compare the published file checksum and Yolanda's frozen checkpoint manifest before running audits.

References: https://tabicl.readthedocs.io/en/latest/api.html ; https://huggingface.co/jingang/TabICL/blob/main/tabicl-classifier-v2-20260212.ckpt
