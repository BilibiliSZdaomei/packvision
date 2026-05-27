param(
    [int]$MaxZipMB = 100,
    [string]$PackageName = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$DistExe = Join-Path $Root "dist\PackVision.exe"
$ReleaseDir = Join-Path $Root "release"

if (-not (Test-Path $DistExe)) {
    throw "PackVision.exe not found. Run scripts\build_exe.ps1 first."
}

if (-not $PackageName) {
    $PackageName = "PackVision_Field_Kit_{0}" -f (Get-Date -Format "yyyyMMdd_HHmm")
}

$KitDir = Join-Path $ReleaseDir $PackageName
$ZipPath = Join-Path $ReleaseDir ($PackageName + ".zip")

if (Test-Path $KitDir) {
    Remove-Item -LiteralPath $KitDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $KitDir | Out-Null

Copy-Item -LiteralPath $DistExe -Destination (Join-Path $KitDir "PackVision.exe") -Force
Copy-Item -LiteralPath (Join-Path $Root "scripts\check_astra_depth_status.ps1") -Destination $KitDir -Force

$DocsDir = Join-Path $KitDir "docs_cn"
$NotesDir = Join-Path $KitDir "docs_obsidian\PackVision"
New-Item -ItemType Directory -Force -Path $DocsDir | Out-Null
New-Item -ItemType Directory -Force -Path $NotesDir | Out-Null
Copy-Item -LiteralPath (Join-Path $Root "docs_cn") -Destination $KitDir -Recurse -Force
Copy-Item -LiteralPath (Join-Path $Root "docs_obsidian\PackVision") -Destination (Join-Path $KitDir "docs_obsidian") -Recurse -Force

$Readme = @(
    "PackVision Field Handoff Kit",
    "",
    "1. Confirm the target PC has the Astra Pro Windows driver installed.",
    "2. Plug in one Astra Pro and confirm color/depth/IR/point-cloud streams in OrbbecViewer.",
    "3. Start PackVision.exe, then run check_astra_depth_status.ps1 and resolve blockers.",
    "4. Open http://127.0.0.1:8765.",
    "5. Validate standard cartons first, then long parts, irregular parts, and reflective/dark/transparent samples.",
    ("6. Keep each zip package below {0} MB for transfer." -f $MaxZipMB),
    "",
    "Chinese details: docs_cn\21_海外仓开箱即用交付方案.md"
) -join [Environment]::NewLine

Set-Content -LiteralPath (Join-Path $KitDir "START_HERE.txt") -Value $Readme -Encoding UTF8

if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -Path (Join-Path $KitDir "*") -DestinationPath $ZipPath -Force

$ZipSizeMB = [Math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
if ($ZipSizeMB -gt $MaxZipMB) {
    throw "Handoff zip is $ZipSizeMB MB, over the $MaxZipMB MB limit: $ZipPath"
}

Write-Host "Built handoff package: $ZipPath ($ZipSizeMB MB)"
