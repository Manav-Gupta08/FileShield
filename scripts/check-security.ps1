$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& ./.venv/Scripts/python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Python tests failed.' }
& ./.venv/Scripts/python.exe -m pip_audit -r requirements.txt --progress-spinner off
if ($LASTEXITCODE -ne 0) { throw 'Dependency audit failed.' }
npm --prefix frontend run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
npm --prefix frontend audit --audit-level=high
if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency audit failed.' }