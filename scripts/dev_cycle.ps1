param(
    [switch]$BuildPackage
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Python venv not found. Run scripts\build_exe.ps1 once to create .venv and install requirements."
}

Push-Location $Root
try {
    Write-Host "== PackVision dev cycle =="
    git status --short --branch

    Write-Host "`n== pytest =="
    & $Python -m pytest -q

    Write-Host "`n== readiness =="
    & (Join-Path $Root "scripts\check_astra_depth_status.ps1") | Out-Host

    if ($BuildPackage) {
        Write-Host "`n== build exe =="
        & (Join-Path $Root "scripts\build_exe.ps1")

        Write-Host "`n== build handoff package =="
        & (Join-Path $Root "scripts\build_handoff_package.ps1")
    }

    Write-Host "`n== final git status =="
    git status --short --branch
}
finally {
    Pop-Location
}
