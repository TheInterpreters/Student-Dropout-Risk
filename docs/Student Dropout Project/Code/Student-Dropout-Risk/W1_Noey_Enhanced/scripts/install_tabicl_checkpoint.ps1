# Noey W1 Enhanced - pinned TabICL / checkpoint setup for Windows PowerShell.
# Safe scope: installs into repo-local .venv-core and downloads checkpoint to Hugging Face cache.
# Does NOT access test data, refit the final-test evaluation, or change original project code.
param(
    [switch]$SkipPackageInstall
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location $repoRoot
Write-Host "Project root: $repoRoot"

if (-not (Test-Path '.\requirements.txt')) {
    throw 'Could not find requirements.txt. Copy W1_Noey_Enhanced next to src/ in the project repository.'
}
$python = Join-Path $repoRoot '.venv-core\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'Creating Python 3.12 environment .venv-core ...'
    & py -3.12 -m venv .venv-core
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 is required. Install it and retry.' }
}
& $python --version
if ($LASTEXITCODE -ne 0) { throw 'Virtual-environment Python is not working.' }
& $python -c "import sys; assert sys.version_info[:2] == (3,12), f'Project requires Python 3.12; found {sys.version}'"
if ($LASTEXITCODE -ne 0) { throw 'Existing .venv-core is not Python 3.12. Back it up and create a fresh 3.12 environment.' }

if (-not $SkipPackageInstall) {
    Write-Host 'Installing exact project requirements (may download PyTorch) ...'
    & $python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Project package installation failed. Copy the error for troubleshooting.' }
}
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Installed dependencies are inconsistent. See pip check output.' }

$pythonScript = @'
import hashlib
from pathlib import Path
from importlib.metadata import version
import torch
from tabicl import TabICLClassifier
from huggingface_hub import hf_hub_download

print('TabICL:', version('tabicl'))
print('PyTorch:', torch.__version__)
assert version('tabicl') == '2.2.0', 'Expected TabICL 2.2.0, do not continue with different version.'
name = 'tabicl-classifier-v2-20260212.ckpt'
p = Path(hf_hub_download(repo_id='jingang/TabICL', filename=name))
sha = hashlib.sha256()
with p.open('rb') as stream:
    for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
        sha.update(block)
expected = 'bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0'
print('Checkpoint file:', p)
print('Checkpoint bytes:', p.stat().st_size)
print('Checkpoint SHA256:', sha.hexdigest())
if sha.hexdigest().lower() != expected:
    raise SystemExit('Checkpoint hash mismatch against published source; check with model owner before using.')
print('TabICL checkpoint downloaded and verified. No model fit or test evaluation was performed.')
'@
Write-Host 'Downloading/verifying public TabICL checkpoint from Hugging Face cache ...'
& $python -c $pythonScript
if ($LASTEXITCODE -ne 0) { throw 'Checkpoint verification failed. See error above.' }
Write-Host 'READY: You can now run the W1 enhanced validation-only scripts.'
