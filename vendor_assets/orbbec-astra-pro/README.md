# Orbbec Astra Pro Vendor Package

Local source package:

```text
D:\Documents\包装尺寸检测\奥比中光Astra Pro
```

Alternate source package:

```text
D:\BaiduNetdiskDownload\奥比中光Astra Pro
```

## Current Inventory

- Files: `158`
- Total size: `367.44 MB`
- Largest file: `82.61 MB`
- Files over GitHub's ordinary `100 MB` single-file limit: `0`

## Decision

The package can technically be committed to Git because no single file is over `100 MB`, but the whole folder is large and contains vendor drivers, SDK archives, DLLs, examples, and PDFs.

PackVision therefore tracks this folder as metadata first:

- `manifest.json`: file list, sizes, and SHA-256 hashes.
- README/docs: integration policy and maintenance notes.
- Raw package: stays local or moves to Git LFS/private release assets if redistribution is acceptable.

## Field Config Snapshots

- `packvision-depth-cameras.dual-astra-pro.20260528.json`: first verified two-camera field config for this workstation. It binds `top` to serial hint `17b3466a` and `front` to serial hint `371b6f72`. Copy it to `D:\app\orbbec-astra-pro\packvision-depth-cameras.json` on a matching workstation, then run PackVision readiness checks.
- If the physical top/front positions are swapped, swap the two `serial_hint` values instead of changing code.

## Important Files

| File | Size | Why it matters |
| --- | ---: | --- |
| `相关例程源码\astra_ws_src_230302.zip` | `82.61 MB` | Vendor ROS/examples source bundle. |
| `上位机软件\上位机软件\opencv_world410.dll` | `71.17 MB` | OrbbecViewer runtime dependency. |
| `上位机软件\上位机软件.zip` | `55.04 MB` | Vendor viewer package. |
| `ROS2系列教程\OpenNI_ROS2_SDK_v1.1.0_20230131_d6d939.tar` | `30.80 MB` | ROS2/OpenNI SDK reviewed by PackVision. |
| `Linux_SDK\AstraSDK-v2.1.3-Ubuntu18.04-x86_64.tar.gz` | `23.90 MB` | Linux SDK reference for future deployment modes. |
| `上位机软件\Window 驱动\SensorDriver_V4.3.0.17.exe` | `4.16 MB` | Windows driver installer for field PCs. |

## Future Cameras

For a new camera, create:

```text
vendor_assets/<vendor-camera-id>/README.md
vendor_assets/<vendor-camera-id>/manifest.json
vendor_assets/<vendor-camera-id>/binaries/   # optional Git LFS/private mirror only
```

Then update:

- `docs_cn`
- `docs_obsidian/PackVision`
- `packvision.services.depth_devices`
- `packvision.services.deployment`
