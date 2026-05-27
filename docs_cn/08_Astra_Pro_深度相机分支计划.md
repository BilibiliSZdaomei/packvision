# Astra Pro 深度相机分支开发计划

本分支：`codex/astra-pro-depth-camera`

本地教程资料位置：

```text
D:\BaiduNetdiskDownload\奥比中光Astra Pro
```

## 目标

主线版本继续保留手机图片、ArUco、无卡估算、侧面照和手动修正能力。本分支专门准备奥比中光 Astra Pro 深度相机接入，等两台实物到货后直接连接验证。

深度相机版本要解决的问题：

1. 不再依赖手机拍摄距离和 EXIF 估算。
2. 顶部俯拍时，用深度图直接计算物体长、宽、高。
3. 对纸箱、软包、异形件，都能用 ROI 或后续分割结果求最大外廓尺寸。
4. 保持现有单号、历史记录、UI 和 API 体系。

## 本地教程资料提取结论

店铺资料包含：

- Windows 驱动：`上位机软件\Window 驱动\SensorDriver_V4.3.0.17.exe`
- Windows 上位机：`上位机软件\上位机软件\OrbbecViewer.exe`
- OpenNI2 运行时：`上位机软件\上位机软件\OpenNI2.dll`
- Orbbec OpenNI 驱动：`上位机软件\上位机软件\OpenNI2\Drivers\orbbec.dll`
- Astra Pro 产品规格书：`产品规格书-Astra Pro_Datasheet _v2.0.pdf`
- 棋盘格标定板：`棋盘格标定200x160_7x10.pdf`
- Linux AstraSDK：`Linux_SDK\AstraSDK-v2.1.3-Ubuntu18.04-x86_64.tar.gz`
- ROS1/ROS2 教程、点云、标定、OpenCV 示例

教程里的重要命令和资料方向：

- ROS 启动 Astra Pro：`roslaunch astra_camera astrapro.launch`
- 点云话题：`/camera/depth_registered/points`
- 点云转 PCD：`rosrun pcl_ros pointcloud_to_pcd input:=/camera/depth_registered/points`
- 相机标定教程使用 ROS `camera_calibration`

## 当前分支已落地内容

### 1. 深度相机状态诊断

接口：

```text
GET /api/depth/status
GET /api/depth/workflow-guide
```

返回内容包括：

- 是否发现店铺教程目录
- 是否发现 OpenNI2.dll
- 是否发现 orbbec.dll
- 是否发现 Windows 驱动安装包
- 是否安装了可选 Python SDK `pyorbbecsdk`
- 推荐后端：`pyorbbecsdk`、`openni2_vendor_runtime` 或 `not_ready`

`GET /api/depth/workflow-guide` 用于到货前后准备现场调试。它会根据包装类型、材质和相机数量返回 USB 数据线、有源 USB 3.0 Hub、支架、卷尺/卡尺、光线和官方上位机验证步骤。两台相机优先用直连 USB、短数据线和有源 Hub 排查，不默认要求购买主板；只有这些方案都不稳定时，再考虑 PCIe USB 扩展卡或更强主机。

### 2. 深度 ROI 测量算法

接口：

```text
POST /api/depth/measure-roi
```

输入：

- `depth_frame`：二维深度数组，单位毫米
- `intrinsics`：相机内参 `fx`、`fy`、`cx`、`cy`、宽、高、深度比例
- `roi`：物体区域 `[x1, y1, x2, y2]`
- `background_roi` 或 `table_depth_mm`：桌面/背景深度

计算方式：

1. 在 ROI 内过滤无效深度。
2. 用稳健中位数得到物体顶部深度。
3. 根据内参把像素宽高投影成毫米。
4. 用桌面深度减物体顶部深度得到高度。
5. 输出长、宽、高、体积、置信度和质量标记。

这层算法已经可用合成深度图测试，不需要等硬件。

## 等相机到货后的验证步骤

### 第一步：先验证官方/店铺工具

1. 安装驱动：

```text
D:\BaiduNetdiskDownload\奥比中光Astra Pro\上位机软件\Window 驱动\SensorDriver_V4.3.0.17.exe
```

2. 插入单台 Astra Pro。
3. 打开：

```text
D:\BaiduNetdiskDownload\奥比中光Astra Pro\上位机软件\上位机软件\OrbbecViewer.exe
```

4. 确认能看到 RGB 和 Depth 画面。
5. 再插第二台，确认 Windows 能区分两个设备。注意 USB 带宽，优先使用不同 USB 控制器或不同扩展坞。

### 第二步：验证 PackVision 状态接口

启动 PackVision 后访问：

```text
http://127.0.0.1:8765/api/depth/status
```

或运行脚本：

```powershell
.\scripts\check_astra_depth_status.ps1
```

期望：

- `ready_for_hardware_trial = true`
- `openni_dll_found = true`
- `orbbec_driver_found = true`

如果后续安装 `pyorbbecsdk`，则 `recommended_backend` 应变成 `pyorbbecsdk`。

### 第三步：接 SDK 采集帧

优先路线：

1. 优先尝试官方 Python SDK：`pyorbbecsdk`
2. 如果 Astra Pro 型号或 Windows 环境不兼容，再走 OpenNI2 运行时封装。
3. 采集彩色图、深度图、相机内参。
4. 把深度帧接到 `measure_depth_roi()`。

### 第四步：仓库实测清单

至少准备：

- 标准纸箱 3 个：小、中、大
- 异形件 3 个：软包、圆柱/卷材、不规则包装
- 黑色/反光/透明材质各 1 个，用来确认深度相机边界
- 卷尺或游标卡尺作为人工真值

每件记录：

- 单号
- 人工长宽高
- PackVision 深度相机长宽高
- 相对误差
- RGB 图
- 深度图
- ROI/分割图

## 下一步编码计划

1. 相机到货后，先确认 Windows 驱动和 OrbbecViewer。
2. 增加 `pyorbbecsdk` 可选采集后端。
3. UI 增加“深度相机”模式和实时预览。
4. ROI 先用手动框选复用现有交互。
5. 后续接 YOLO/分割模型，让异形件 ROI 自动化。
6. 双相机阶段再做设备选择、序列号绑定和多机防冲突。

## 参考来源

- 店铺教程本地资料：`D:\BaiduNetdiskDownload\奥比中光Astra Pro`
- Orbbec 开发者入口：https://www.orbbec.com/developers/
- Orbbec ROS Astra Camera：https://github.com/orbbec/ros_astra_camera
- Orbbec Python SDK：https://github.com/orbbec/pyorbbecsdk
