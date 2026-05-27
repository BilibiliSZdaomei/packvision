# PackVision Local

本地包装尺寸检测工具：上传手机照片，识别顶部长宽、侧面高度候选，支持无校准卡估算、手动修正框、单号/条码追溯和本地历史记录。目标是先在没有摄像头、没有深度相机的仓库环境里跑起来，再逐步接入相机、扫码枪、YOLO/深度模型。

## 当前能力

- 本地 Web UI，支持中文、English、Українська 和明亮/深色/石墨主题。
- `POST /api/measure` 支持顶部照片、侧面照片、ArUco 标记、人工高度、相机距离、等效焦距、手动框选范围。
- 没有校准卡时，可基于相机距离 + EXIF/手动 35mm 等效焦距做尺寸估算。
- 侧面照片会单独识别轮廓，并生成高度候选。
- 支持手动修正顶部/侧面标注框，适合异形件、软包、边缘识别失败场景。
- 支持单号录入、扫码枪文本输入、上传条码/二维码图片识别单号。
- SQLite 本地历史记录，保存时间戳、单号、尺寸、置信度、上传图和标注图。
- `GET /api/demo-image.jpg` 可在没有摄像头时一键试测。
- PyInstaller 打包为 Windows EXE。

## 运行

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m packvision.main
```

打开：

```text
http://127.0.0.1:8765
```

## 打包 EXE

```powershell
.\scripts\build_exe.ps1
```

输出：

```text
D:\Documents\包装尺寸检测\dist\PackVision.exe
```

## API 摘要

- `GET /api/health`：运行状态。
- `GET /api/demo-image.jpg`：演示图片。
- `GET /api/calibration-card.svg`：A4 ArUco 校准卡。
- `POST /api/measure`：测量图片。
- `GET /api/history`：历史记录列表。
- `GET /api/history/export.csv`：按单号筛选导出 CSV。
- `GET /api/history/{measurement_id}`：单条记录详情。
- `GET /api/usage/summary`：后台使用统计，返回总调用次数、测量次数、成功/失败次数、按接口和日期汇总。
- `GET /api/usage/events`：后台调用日志明细。
- `GET /api/usage/export.csv`：导出使用日志 CSV，方便汇报。
- `POST /api/orders/scan`：扫码枪/手工单号标准化接口。
- `POST /api/orders/decode-image`：上传条码或二维码图片识别单号。

## 对标路线

当前轻量 EXE 先集成 OpenCV ArUco、OpenCV 条码/二维码识别和传统轮廓检测。对标方向记录在：

```text
D:\Documents\包装尺寸检测\docs_cn\02_对标开源方案与本地落地.md
```

重点结论：YOLO/OBB/分割适合提升包装或异形件边界识别；Depth Anything V2 适合做单目深度插件；但两者都会增加模型文件和运行依赖，不适合直接塞进当前轻量 EXE 主包。

## 现实边界

单张普通手机照片只有二维投影。只靠焦距、光圈、EXIF 不能稳定恢复真实三维尺寸，因为缺少拍摄距离、物体深度和姿态信息。当前实现把“精确”和“估算”分开：

1. 有 ArUco 标记：作为优先高置信比例来源。
2. 无标记但有距离和焦距：给出可追溯估算，并降低置信度。
3. 有侧面照片：补充高度候选。
4. 识别不准：用手动框修正并重新测量。
5. 异形件：先支持手动框选，后续可接 YOLO/分割模型。

## Astra Pro 深度相机分支

深度相机开发在分支：

```text
codex/astra-pro-depth-camera
```

店铺附赠教程资料默认读取：

```text
D:\BaiduNetdiskDownload\奥比中光Astra Pro
```

本分支新增：

- `GET /api/depth/status`：检查 Astra Pro 教程资料、OpenNI2 运行时、Windows 驱动和可选 `pyorbbecsdk`。
- `GET /api/depth/vendor-profile`：返回 Astra Pro 厂商规格、上位机验收流程、厂商优先标定策略和 ROS/OpenNI 推荐接口。
- `GET /api/depth/astra/tutorial-playbook`：返回二次审计后的厂商教程适配手册，包括 ROS2 曝光/增益/镜像/激光/流控制服务、多相机 `device_num`、`cleanup_shm_node`、D2C/点云和标定 URL 映射。
- `POST /api/depth/camera-info/normalize`：把 ROS `/camera/depth/camera_info` 或标定 YAML 转成测量接口可直接使用的 `fx/fy/cx/cy` 内参，避免仓库员工手动输入参数。
- `GET /api/depth/workflow-guide`：按包装类型、材质和相机数量返回到货调试清单、USB/支架/线材准备项和采集步骤；默认不要求购买主板。
- `GET /api/depth/capture/capabilities`：报告可选采集后端、OpenNI2/OpenCV 探测能力和当前推荐路径。
- `POST /api/depth/capture/probe`：到货前后都可运行的采集探测接口，返回状态、选中后端和下一步动作。
- `GET /api/depth/demo-object`：无硬件时运行合成异形件深度测量演示。
- `POST /api/depth/demo-object/save`：把深度演示按单号保存到历史记录，方便验证追溯流程。
- `POST /api/depth/measure-roi`：用深度图、相机内参、ROI 和桌面深度计算真实长宽高。
- `POST /api/depth/quality`：检查深度孔洞、稀疏有效点、ROI 噪声和台面背景稳定性，提前暴露反光、透明、深黑材质风险。
- `POST /api/depth/measure-object`：用桌面深度分离物体 mask，再用点云范围测异形件；长条件可传 `footprint_method=principal_axes` 按主轴方向测真实长度。
- `POST /api/depth/measure-roi` 和 `POST /api/depth/measure-object` 支持 `order_id`、`barcode_text`、`part_category`、`package_hint`、`material_hint`、`actual_weight_kg`、`save_to_history`，真实相机接入后可直接进入同一套历史追溯和 CSV 导出。
- `POST /api/industry/profile`：按汽车备件场景判断标准纸箱、长条件、软包/异形件、异常材质风险和计费重。
- `GET /api/validation/trial-plan`：返回 Astra Pro 到货后普通纸箱、长条件、异形件和异常材质的最小抽检计划。
- `POST /api/validation/evaluate`：输入人工真值和系统测量值，输出误差、失败样本、复核样本和是否可进入现场试运行。
- `GET /api/validation/trial-template.csv`：下载 WPS/Excel 可直接填写的现场验收模板，覆盖普通包装、长条件、异形件和异常材质样本。
- `POST /api/validation/evaluate-csv`：上传填写后的 CSV，批量计算误差、复核项和现场试运行结论。
- `scripts\check_astra_depth_status.ps1`：本地检查深度相机资料和 SDK 状态。
- `docs_cn\08_Astra_Pro_深度相机分支计划.md`：到货后的驱动、上位机、SDK、实测清单。
- `docs_cn\09_汽车备件测量落地方案.md`：汽车备件仓库的普通包装、异形包装和异常材质落地流程。
- `docs_cn\10_Astra_Pro_到货验收与现场试运行.md`：两台 Astra Pro 到货后的第一小时验收、标准纸箱/长条件/异形件试运行流程。
- `docs_cn\16_Astra_Pro_厂商资料学习笔记.md`：基于店铺附赠资料包重新梳理的厂商工具链、标定策略和 PackVision 修正方向。
