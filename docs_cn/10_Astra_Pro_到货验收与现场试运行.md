# Astra Pro 到货验收与现场试运行

本文档用于两个奥比中光 Astra Pro 到货后的第一轮验证。目标不是一次性追求最高精度，而是先确认硬件、驱动、深度图、仓库单号追溯和历史导出都能跑通。

## 1. 到货前软件状态

- EXE 保持轻量化，深度 SDK 仍为可选依赖。
- `GET /api/depth/status` 会检查教程资料目录、OpenNI2 运行时、Orbbec 驱动 DLL、Windows 驱动安装包和 `pyorbbecsdk`。
- `GET /api/depth/capture/capabilities` 会报告当前可用的采集后端，判断是否需要等相机到货后安装 `pyorbbecsdk` 或走 OpenNI2 探测。
- `POST /api/depth/capture/probe` 会返回选中后端、探测状态和下一步动作，适合现场人员插相机前后各跑一次。
- `GET /api/depth/demo-object` 可在没有硬件时验证异形件点云测量逻辑。
- `POST /api/depth/demo-object/save` 可在没有硬件时验证单号、行业分类、历史记录和 CSV 导出。

## 2. 到货后第一小时检查

1. 插入相机，先安装店铺资料里的 Windows 驱动。
2. 打开奥比中光上位机，确认彩色图和深度图都有画面。
3. 运行：

```powershell
.\scripts\check_astra_depth_status.ps1
```

4. 打开 PackVision，进入“深度”工作区，确认 OpenNI2 和驱动状态为可用。
5. 点击“采集探测”，记录 `backend_selected`、`status` 和 `next_actions`。
6. 用“保存演示记录”先生成一条深度记录，确认历史和 CSV 能导出。

## 3. 标准纸箱试运行

- 推荐模式：`top_plus_side_or_depth_roi`。
- 放置方式：纸箱平放在稳定桌面，长边尽量与画面水平。
- 采集数据：订单号、条码、实重、深度 ROI、桌面背景 ROI。
- 验收标准：长宽高与卷尺抽检误差进入仓库可接受范围后，再扩大样本量。

## 4. 长条件试运行

- 推荐模式：`depth_roi_long_item`。
- 典型备件：减震器、排气管、饰条、长条包装。
- 放置方式：长轴完整入画；必要时斜放，但 ROI 要覆盖整个物体。
- 关注点：是否触发 `oversize_length`，计费重量是否大于实重。

## 5. 异形件试运行

- 推荐模式：`depth_object_mask`。
- 典型备件：保险杠、翼子板、中网、软包裹件。
- 放置方式：尽量使用纯色桌面或托盘，背景 ROI 必须选在空桌面。
- 关注点：`object_pixel_ratio` 过小时要重新摆放或扩大 ROI；软包件仍保留人工复核。

## 6. 追溯字段

深度测量接口支持：

- `order_id`
- `barcode_text`
- `part_category`
- `package_hint`
- `actual_weight_kg`
- `save_to_history`

当 `save_to_history=true` 时，结果会进入 SQLite 历史库，并可通过 `GET /api/history/export.csv` 导出给 Excel/WMS。

## 7. 现场风险

- 反光膜、透明袋、黑色吸光材质会降低深度质量。
- 相机倾斜和桌面不平会影响高度，第一版先用背景 ROI 估计桌面深度。
- 深度相机到货前不要把 `pyorbbecsdk` 做成强依赖，否则 EXE 会变重且更难部署。
