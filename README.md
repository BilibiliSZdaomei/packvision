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
- `GET /api/history/{measurement_id}`：单条记录详情。
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
