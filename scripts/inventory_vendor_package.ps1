param(
    [string]$VendorRoot = "",
    [string]$OutputPath = "",
    [string]$VendorId = "orbbec-astra-pro",
    [string]$DisplayName = "Orbbec Astra Pro seller tutorial package"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not $OutputPath) {
    $OutputPath = Join-Path $RepoRoot "vendor_assets\orbbec-astra-pro\manifest.json"
}

if (-not $VendorRoot) {
    $candidateRoots = @($RepoRoot, "D:\BaiduNetdiskDownload") |
        Where-Object { Test-Path -LiteralPath $_ }

    $VendorRoot = $candidateRoots |
        ForEach-Object {
            Get-ChildItem -LiteralPath $_ -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -like "*Astra Pro*" }
        } |
        Select-Object -First 1 -ExpandProperty FullName
}

if (-not $VendorRoot -or -not (Test-Path -LiteralPath $VendorRoot)) {
    throw "VendorRoot does not exist. Pass -VendorRoot explicitly or place the folder under the repo root."
}

$resolvedVendorRoot = (Resolve-Path -LiteralPath $VendorRoot).Path
$files = Get-ChildItem -LiteralPath $resolvedVendorRoot -Recurse -File | Sort-Object FullName
$totalBytes = ($files | Measure-Object Length -Sum).Sum
$largest = $files | Sort-Object Length -Descending | Select-Object -First 20
$extensions = $files |
    Group-Object Extension |
    ForEach-Object {
        $sum = ($_.Group | Measure-Object Length -Sum).Sum
        [ordered]@{
            extension = if ($_.Name) { $_.Name } else { "(none)" }
            count = $_.Count
            size_bytes = [int64]$sum
            size_mb = [math]::Round($sum / 1MB, 2)
        }
    } |
    Sort-Object size_bytes -Descending

$fileEntries = foreach ($file in $files) {
    $relative = $file.FullName.Substring($resolvedVendorRoot.Length).TrimStart("\")
    [ordered]@{
        path = $relative
        size_bytes = [int64]$file.Length
        size_mb = [math]::Round($file.Length / 1MB, 2)
        sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$manifest = [ordered]@{
    schema_version = 1
    vendor_id = $VendorId
    display_name = $DisplayName
    source_root = $resolvedVendorRoot
    generated_at = (Get-Date).ToString("o")
    policy = [ordered]@{
        normal_git = "Track manifest, notes, checksums and integration docs."
        binary_mirror = "Use Git LFS or private release assets for drivers, SDK archives and other large/proprietary files."
        public_repo_warning = "Do not redistribute vendor drivers/SDKs publicly unless the vendor license allows it."
    }
    summary = [ordered]@{
        file_count = $files.Count
        total_size_bytes = [int64]$totalBytes
        total_size_mb = [math]::Round($totalBytes / 1MB, 2)
        max_file_size_mb = [math]::Round(($largest | Select-Object -First 1).Length / 1MB, 2)
        files_over_100mb = @($files | Where-Object { $_.Length -gt 100MB }).Count
    }
    extensions = @($extensions)
    largest_files = @(
        foreach ($file in $largest) {
            [ordered]@{
                path = $file.FullName.Substring($resolvedVendorRoot.Length).TrimStart("\")
                size_bytes = [int64]$file.Length
                size_mb = [math]::Round($file.Length / 1MB, 2)
            }
        }
    )
    files = @($fileEntries)
}

$output = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $output | Out-Null
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host "Wrote vendor manifest: $OutputPath"
