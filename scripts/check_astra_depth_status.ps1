$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourcePackage = Join-Path $repoRoot "packvision"
$fieldExe = Join-Path $repoRoot "PackVision.exe"
$readyUrl = "http://127.0.0.1:8765/api/deployment/readiness"
Set-Location $repoRoot

if (Test-Path ".\.venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
} else {
    $python = "python"
}

$code = @'
from __future__ import annotations

import json

from packvision.services.deployment import build_deployment_readiness


print(json.dumps(build_deployment_readiness(), ensure_ascii=False, indent=2))
'@

if (Test-Path $sourcePackage) {
    $code | & $python -
} elseif (Test-Path $fieldExe) {
    try {
        Invoke-RestMethod -Uri $readyUrl -Method Get -TimeoutSec 3 | ConvertTo-Json -Depth 20
    } catch {
        [ordered]@{
            status = "packvision_not_running"
            message = "PackVision.exe was found, but the local readiness API is not responding yet."
            next_actions = @(
                "Double-click PackVision.exe.",
                "Wait until http://127.0.0.1:8765 opens.",
                "Run this script again."
            )
            exe_path = $fieldExe
            readiness_url = $readyUrl
        } | ConvertTo-Json -Depth 8
    }
} else {
    throw "Run this script from the project root or from the field handoff package folder."
}
