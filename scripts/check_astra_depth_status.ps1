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
from packvision.services.depth_capture import DepthCaptureConfig, probe_depth_capture


readiness = build_deployment_readiness()
try:
    capture_probe = probe_depth_capture(DepthCaptureConfig(backend="auto"))
except Exception as exc:
    capture_probe = {
        "status": "probe_error",
        "ready": False,
        "message": str(exc),
        "field_diagnosis": {
            "severity": "blocked",
            "operator_summary_key": "probe_error",
            "operator_summary": "Capture probe failed before hardware validation.",
            "operator_detail": str(exc),
            "primary_actions": [
                {
                    "key": "run_status_script",
                    "label": "run_status_script",
                    "detail": "Check Astra files, driver and OpenNI runtime.",
                }
            ],
        },
    }

print(json.dumps({
    "readiness": readiness,
    "capture_probe": capture_probe,
    "field_summary": {
        "readiness_status": readiness.get("status"),
        "capture_status": capture_probe.get("status"),
        "capture_severity": (capture_probe.get("field_diagnosis") or {}).get("severity"),
        "operator_summary": (capture_probe.get("field_diagnosis") or {}).get("operator_summary"),
        "primary_actions": (capture_probe.get("field_diagnosis") or {}).get("primary_actions") or [],
    },
}, ensure_ascii=False, indent=2))
'@

if (Test-Path $sourcePackage) {
    $code | & $python -
} elseif (Test-Path $fieldExe) {
    try {
        $readiness = Invoke-RestMethod -Uri $readyUrl -Method Get -TimeoutSec 3
        $probe = Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/depth/capture/probe" -Method Post -ContentType "application/json" -Body '{"backend":"auto"}' -TimeoutSec 5
        [ordered]@{
            readiness = $readiness
            capture_probe = $probe
            field_summary = [ordered]@{
                readiness_status = $readiness.status
                capture_status = $probe.status
                capture_severity = $probe.field_diagnosis.severity
                operator_summary = $probe.field_diagnosis.operator_summary
                primary_actions = $probe.field_diagnosis.primary_actions
            }
        } | ConvertTo-Json -Depth 20
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
