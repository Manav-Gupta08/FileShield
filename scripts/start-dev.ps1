param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv/Scripts/python.exe')) { throw 'Create .venv and install requirements-dev.txt first.' }
if (-not $env:FILESHIELD_SECRET_KEY) {
    $bytes = New-Object byte[] 32
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $generator.GetBytes($bytes)
    $generator.Dispose()
    $env:FILESHIELD_SECRET_KEY = ([BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
}
$env:FILESHIELD_ENV = 'development'
$env:REQUIRE_SCAN = 'false'
$env:PUBLIC_ORIGIN = 'http://localhost:5173'
Write-Host 'Development only: antivirus disabled; use non-sensitive test files.'
& ./.venv/Scripts/python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port $Port --no-access-log
exit $LASTEXITCODE