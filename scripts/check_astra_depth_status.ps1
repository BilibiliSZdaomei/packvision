$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (Test-Path ".\.venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
} else {
    $python = "python"
}

$code = @'
from __future__ import annotations

import json

from packvision.services.depth_camera import depth_camera_status


print(json.dumps(depth_camera_status(), ensure_ascii=False, indent=2))
'@

$code | & $python -
