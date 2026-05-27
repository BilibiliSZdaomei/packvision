# Vendor Camera Assets

This directory is the long-term index for camera vendor packages used by PackVision.

## Policy

- Keep vendor package metadata, notes, checksums, and integration instructions in normal Git.
- Keep raw drivers, SDK archives, DLLs, large PDFs, and bundled examples out of normal Git history unless redistribution is clearly allowed.
- If a binary mirror is needed, use Git LFS or private release assets under a vendor-specific `binaries/` folder.
- Every new camera vendor should get its own subfolder with a README and manifest.

## Current Vendors

| Vendor package | Folder | Status |
| --- | --- | --- |
| Orbbec Astra Pro seller tutorial package | `vendor_assets/orbbec-astra-pro` | Metadata tracked; raw package stays local/ignored. |

## Generate Manifest

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\inventory_vendor_package.ps1
```

The manifest records file sizes and SHA-256 hashes so the local vendor package can be verified without committing the full raw package into normal Git.
