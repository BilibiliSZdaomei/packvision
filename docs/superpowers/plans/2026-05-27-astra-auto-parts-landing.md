# Astra Pro Auto Parts Landing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the next PackVision depth-camera branch layer for automotive spare-parts warehouse measurement, covering standard cartons, long parts, soft/irregular packaging, and exception handling before the Astra Pro hardware arrives.

**Architecture:** Keep the existing image-measurement path intact. Add small, testable services for automotive packaging profiling and irregular-object depth measurement, expose them through FastAPI endpoints, and document the hardware validation workflow. Hardware SDK imports remain optional so CI and the current EXE stay lightweight.

**Tech Stack:** Python 3.11, FastAPI, NumPy, OpenCV/Pillow already in the project, pytest, optional Orbbec OpenNI2/pyorbbecsdk later.

---

## File Structure

- `packvision/services/industry.py`: Automotive spare-parts packaging classifier and measurement-mode recommender.
- `packvision/services/depth_geometry.py`: Extend depth ROI math with object-mask/point-cloud extent measurement for irregular packages.
- `packvision/app.py`: Add `/api/industry/profile` and `/api/depth/measure-object`.
- `tests/test_industry.py`: Unit tests for package profiles, mode selection, and freight/handling flags.
- `tests/test_depth_geometry.py`: Add tests for irregular-object depth mask measurement.
- `tests/test_api.py`: Add endpoint tests.
- `docs_cn/09_汽车备件测量落地方案.md`: Chinese landing playbook for warehouse operation.
- `README.md`: Link the new automotive landing mode.

---

### Task 1: Automotive Packaging Profile

**Files:**
- Create: `packvision/services/industry.py`
- Create: `tests/test_industry.py`
- Modify: `packvision/app.py`

- [ ] **Step 1: Write tests for standard carton, long part, and irregular soft package**

```python
from packvision.services.industry import build_packaging_profile


def test_standard_carton_profile():
    profile = build_packaging_profile(
        {"length_mm": 420, "width_mm": 280, "height_mm": 160, "volume_l": 18.816},
        part_category="filter",
        package_hint="carton",
        actual_weight_kg=3.2,
    )
    assert profile["package_class"] == "standard_carton"
    assert profile["recommended_capture_mode"] == "top_plus_side_or_depth_roi"
    assert profile["chargeable_weight_kg"] == 3.2


def test_long_part_profile():
    profile = build_packaging_profile(
        {"length_mm": 1300, "width_mm": 180, "height_mm": 120, "volume_l": 28.08},
        part_category="shock_absorber",
        package_hint="long_part",
    )
    assert profile["package_class"] == "long_part"
    assert "oversize_length" in profile["handling_flags"]
    assert profile["recommended_capture_mode"] == "depth_roi_long_item"


def test_irregular_soft_package_profile():
    profile = build_packaging_profile(
        {"length_mm": 620, "width_mm": 430, "height_mm": None, "volume_l": None},
        part_category="bumper_trim",
        package_hint="irregular",
    )
    assert profile["package_class"] == "irregular_or_soft_pack"
    assert "needs_depth_or_manual_height" in profile["handling_flags"]
    assert profile["recommended_capture_mode"] == "depth_object_mask"
```

- [ ] **Step 2: Implement `build_packaging_profile()`**

Use deterministic rules:
- longest side >= 1200 mm -> `long_part`
- missing height or package hint `irregular`/`soft` -> `irregular_or_soft_pack`
- all dimensions present and coefficient under 1.8 -> `standard_carton`
- otherwise -> `bulky_irregular`

Compute volumetric weight using `volume_l / 6` for domestic express-style dimensional weight approximation.

- [ ] **Step 3: Add `IndustryProfilePayload` and `/api/industry/profile`**

Request fields:
- `dimensions`
- `part_category`
- `package_hint`
- `actual_weight_kg`

Return `build_packaging_profile()`.

---

### Task 2: Irregular Depth Object Mask

**Files:**
- Modify: `packvision/services/depth_geometry.py`
- Modify: `tests/test_depth_geometry.py`
- Modify: `packvision/app.py`

- [ ] **Step 1: Add failing test for an L-shaped object**

Create a depth frame with table depth 1000 mm and object depth 760 mm in an L-shaped mask. The measured footprint should use the mask extent, not the full ROI rectangle, and height should be 240 mm.

- [ ] **Step 2: Implement `DepthObjectConfig` and `measure_depth_object_mask()`**

Algorithm:
- Normalize depth to millimeters.
- Determine table depth from `table_depth_mm` or `background_roi`.
- Build object mask where depth is at least `object_min_height_mm` closer than table.
- Project mask pixels with intrinsics into X/Y/Z coordinates.
- Use quantile trimming for X/Y extents to reduce edge noise.
- Report length, width, height, volume, object pixel count, valid ratio, and flags.

- [ ] **Step 3: Add `/api/depth/measure-object`**

This endpoint accepts the same depth frame and intrinsics as `/api/depth/measure-roi`, plus `object_min_height_mm`.

---

### Task 3: Automotive Landing Documentation

**Files:**
- Create: `docs_cn/09_汽车备件测量落地方案.md`
- Modify: `README.md`

- [ ] **Step 1: Document warehouse modes**

Include:
- 标准纸箱
- 长条件
- 软包/异形件
- 易碎/反光/黑色/透明件
- 双相机预留

- [ ] **Step 2: Document operational flow**

Flow:
扫码/录单 -> 选择或自动判断包装类型 -> 深度测量 -> 人工复核异常 -> 保存历史 -> 出库/计费/异常复测。

---

### Task 4: Verification and Push

**Files:**
- All changed files

- [ ] **Step 1: Run tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run depth status script**

Run:

```powershell
.\scripts\check_astra_depth_status.ps1
```

Expected: finds the vendor tutorial path, OpenNI2.dll, orbbec.dll, and Windows driver installer.

- [ ] **Step 3: Commit and push**

Run:

```powershell
git add README.md docs docs_cn packvision scripts tests
git commit -m "Add auto parts depth measurement modes"
git push
```

Expected: branch `codex/astra-pro-depth-camera` updates on GitHub.

---

## Self-Review

Spec coverage:
- Automotive spare-parts industry needs: Task 1 and Task 3.
- Standard packaging: Task 1 standard carton profile.
- Irregular packaging: Task 2 depth object mask and Task 3 workflow.
- Continue depth-camera branch without hardware: Task 2 synthetic depth tests and Task 4 diagnostics.
- Existing project background: Task 1 plugs into current dimensions/order workflow without replacing it.

Placeholder scan:
- No TBD/TODO placeholders in planned deliverables.

Type consistency:
- `DepthIntrinsics` remains the shared intrinsics type.
- New endpoint payloads mirror existing `/api/depth/measure-roi` payload shape.
