# Astra Pro 到货验收与现场试运行

本文档用于两个奥比中光 Astra Pro 到货后的第一轮验证。目标不是一次性追求最高精度，而是先确认硬件、驱动、深度图、仓库单号追溯和历史导出都能跑通。

## 1. 到货前软件状态

- EXE 保持轻量化，深度 SDK 仍为可选依赖。
- `GET /api/depth/status` 会检查教程资料目录、OpenNI2 运行时、Orbbec 驱动 DLL、Windows 驱动安装包和 `pyorbbecsdk`。
- `GET /api/depth/capture/capabilities` 会报告当前可用的采集后端，判断是否需要等相机到货后安装 `pyorbbecsdk` 或走 OpenNI2 探测。
- `POST /api/depth/capture/probe` 会返回选中后端、探测状态、`field_diagnosis` 现场诊断和下一步动作，适合现场人员插相机前后各跑一次。
- `GET /api/depth/demo-object` 可在没有硬件时验证异形件点云测量逻辑。
- `POST /api/depth/demo-object/save` 可在没有硬件时验证单号、行业分类、历史记录和 CSV 导出。

## 2. 到货后第一小时检查

1. 插入相机，先确认店铺资料里的 Windows 驱动已安装；本机当前已检测到 `SensorDriver V4.3.0.17`。
2. 打开奥比中光上位机 `D:\app\orbbec-astra-pro\启动上位机.bat`，确认彩色、深度、红外和点云都有画面。
3. 关闭上位机，避免它继续占用相机。
4. 运行：

```powershell
.\scripts\check_astra_depth_status.ps1
```

5. 打开 PackVision，确认 OpenNI2、驱动安装状态、上位机工具和设备守护状态。
6. 点击“采集探测”，记录 `backend_selected`、`status`、`field_diagnosis.severity` 和 `field_diagnosis.primary_actions`。
7. 点击“验收计划”，确认普通纸箱、长条件、异形件和异常材质的抽检数量。
8. 用“保存演示记录”先生成一条深度记录，确认历史和 CSV 能导出。

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
- `material_hint`
- `actual_weight_kg`
- `save_to_history`

当 `save_to_history=true` 时，结果会进入 SQLite 历史库，并可通过 `GET /api/history/export.csv` 导出给 Excel/WMS。

## 6.1 采集探测现场诊断

`POST /api/depth/capture/probe` 现在不仅返回开发者看的 backend/status，也会返回仓库现场能理解的 `field_diagnosis`：

| 字段 | 用途 |
| --- | --- |
| `severity` | 当前严重程度：`ready`、`waiting_for_camera`、`validation_required`、`action_required`、`blocked`。 |
| `operator_summary_key` | UI 多语言文案键，例如 `probe_no_camera` 或 `probe_ready`。 |
| `primary_actions` | 下一步动作，按顺序提示插 USB、打开 OrbbecViewer、重新探测或采集深度帧。 |
| `evidence.device_count` | OpenNI 当前看到的相机数量。 |
| `can_continue_photo_fallback` | 相机没就绪时，是否仍可先用照片兜底流程继续业务演练。 |

现场判断口径：

- `ready_for_capture`：可以采集一帧深度图，再测已知纸箱。
- `openni_runtime_ready_no_device`：驱动和运行库没问题，先查 USB 数据线、相机供电和上位机画面。
- `driver_ready_capture_backend_missing`：驱动/运行库在，但当前 Python/EXE 采集适配还缺组件。
- `capture_backend_missing`：先处理驱动、资料路径或运行库，再进入测量。

## 7. 现场风险

- 反光膜、透明袋、黑色吸光材质会降低深度质量。录入 `material_hint` 后，系统会在行业画像中标出材质风险，并把流程切到“表面检查 + 重拍或人工复核”。
- 建议到货第一天专门抽检 `reflective`、`transparent`、`dark_absorbing`、`deformable` 四类异常材质，每类至少 2 件。
- 相机倾斜和桌面不平会影响高度，第一版先用背景 ROI 估计桌面深度。
- 深度相机到货前不要把 `pyorbbecsdk` 做成强依赖，否则 EXE 会变重且更难部署。

## 8. 验收计划接口

```text
GET /api/validation/trial-plan
POST /api/validation/evaluate
GET /api/validation/trial-template.csv
POST /api/validation/evaluate-csv
```

默认最小抽检：

- 标准纸箱：5 件，最大尺寸误差不超过 8 mm 或 3%。
- 长条件：5 件，最大尺寸误差不超过 12 mm 或 2.5%。
- 异形/软包：10 件，最大尺寸误差不超过 18 mm 或 6%。
- 大件异形：4 件，最大尺寸误差不超过 20 mm 或 6%。
- 反光、透明、深黑吸光、易变形材质：每类至少 2 件，并保留人工复核。

`POST /api/validation/evaluate` 输入每件的 `measured` 和人工真值 `truth`，会返回每件误差、失败样本、复核样本和是否可以进入现场试运行。

如果现场人员习惯用 WPS/Excel，可以先下载 `GET /api/validation/trial-template.csv`。模板已经按普通纸箱、长条件、异形/软包、大件异形，以及反光、透明、深黑吸光、易变形材质预留样本行。现场只需要填写单号、系统测量值、卷尺/卡尺真值和备注，再把 CSV 上传到 `POST /api/validation/evaluate-csv`，系统会复用同一套容差规则给出批量验收结论。

## 9. 到货调试清单接口

```text
GET /api/depth/workflow-guide
```

这个接口把摄像头到货前后的准备工作落到软件里：USB 数据延长线、有源 USB 3.0 Hub、固定支架、卷尺/卡尺、哑光桌面、稳定室内光线、官方 Viewer 先验深度图。它也会按 `package_class`、`material_class`、`camera_count` 给出采集步骤。

示例：

```text
GET /api/depth/workflow-guide?package_class=long_part&material_class=reflective&camera_count=2
```

返回结果会提示两台相机优先准备有源 Hub 和 1-2 米数据线，长条件走 `long_item_depth_roi`，反光件增加 `reflective_surface_cross_check`。当前结论是：调试初期不需要买主板；只有直连 USB、短数据线、有源 Hub 和不同 USB 口都不稳定时，再考虑 PCIe USB 扩展卡或更强主机。
