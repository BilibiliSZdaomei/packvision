---
title: Astra Pro 到货验收清单
date: 2026-05-28
tags:
  - AstraPro
  - 到货验收
  - 深度相机
aliases:
  - 深度相机到货怎么测
status: active
---

# Astra Pro 到货验收清单

[[00 PackVision 知识地图|返回知识地图]]

> [!important] 目标
> 第一天不是追求最高精度，而是确认：驱动能装、上位机有画面、PackVision 能看到设备、能采集一帧深度数据。

## 已经安装好的东西

- 安装根目录：`D:\app\orbbec-astra-pro`
- 上位机：`D:\app\orbbec-astra-pro\viewer\OrbbecViewer.exe`
- 启动脚本：`D:\app\orbbec-astra-pro\启动上位机.bat`
- 检查脚本：`D:\app\orbbec-astra-pro\检查Astra安装.ps1`
- 相机配置：`D:\app\orbbec-astra-pro\packvision-depth-cameras.json`
- 安装说明：`D:\app\orbbec-astra-pro\安装说明.md`
- Windows 驱动：已检测到 `SensorDriver V4.3.0.17`，DriverStore 为 `oem221.inf` / `obdrv4.inf`

## 到货后 10 分钟检查

1. 插上 Astra Pro。
2. 优先插电脑本体 USB 口；不稳再用有源 USB Hub。
3. 双击 `D:\app\orbbec-astra-pro\启动上位机.bat`。
4. 在 OrbbecViewer 里确认 Color、Depth、IR、Point Cloud 都有画面。
5. 关闭 OrbbecViewer，避免它占用相机。
6. 运行检查脚本：

```powershell
PowerShell -ExecutionPolicy Bypass -File "D:\app\orbbec-astra-pro\检查Astra安装.ps1"
```

## 正常结果应该是什么

- 文件检查全部 OK。
- Windows 驱动库能看到 Orbbec。
- OpenNI runtime 显示初始化成功。
- 插相机后 `device_count` 应该从 `0` 变成 `1`。

上位机只是验机工具，日常测量、记录、体积重、历史和统计仍在 PackVision 里完成。详细解释见 [[26 Astra Pro 驱动与上位机说明]]。

## PackVision 接口检查

服务地址：

`http://127.0.0.1:8765`

关键接口：

```text
GET /api/depth/cameras
POST /api/depth/capture/probe
POST /api/depth/capture/frame
POST /api/depth/measure-capture
```

如果没插相机，`probe` 返回 `openni_runtime_ready_no_device` 是正常的。

如果插了相机，目标是看到 `ready_for_capture`。

现在 `probe` 还会返回 `field_diagnosis`。现场重点看：

- `severity=waiting_for_camera`：驱动和运行库正常，先插线、换 USB 口、打开 OrbbecViewer。
- `severity=ready`：PackVision 已看到相机，可以采集一帧深度图。
- `primary_actions`：照顺序执行，不用理解 backend 细节。
- `can_continue_photo_fallback=true`：相机还没好时，可以先用照片兜底演练单号、历史、体积重和复核流程。

## 第一批实物验证

建议准备：

- 标准纸箱 5 个。
- 长条件 5 个。
- 异形件/软包 10 个。
- 反光、透明、黑色、易变形材质各 2 个。

每个样品记录：

- 单号或测试编号。
- 人工卷尺真值。
- 系统测量值。
- 是否重拍。
- 是否人工复核。

相关流程：[[07 汽车备件测量场景]]
