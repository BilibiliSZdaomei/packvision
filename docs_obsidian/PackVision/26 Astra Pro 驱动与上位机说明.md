---
title: Astra Pro 驱动与上位机说明
date: 2026-05-28
tags:
  - PackVision
  - AstraPro
  - 驱动
  - 上位机
status: active
---

# Astra Pro 驱动与上位机说明

[[00 PackVision 知识地图|返回知识地图]]

> [!summary] 结论
> 这台电脑已经装好 Astra Pro Windows 驱动。资料包里的“上位机软件”是奥比中光 `OrbbecViewer`，用于验机和排错，不是仓库日常测量软件。

## 本机驱动状态

- 已安装：`SensorDriver V4.3.0.17`
- 发布者：`SHENZHEN ORBBEC CO., LTD.`
- DriverStore：`oem221.inf`
- 原始驱动：`obdrv4.inf`
- Provider：`Orbbec`
- Driver Version：`10/20/2020 4.3.0.17`

当前没有真实 Astra Pro 接入，所以设备列表里暂时看不到 Astra/Orbbec 相机。

## 上位机是什么

`OrbbecViewer` 是厂商官方相机查看工具。

它用来确认：

- 驱动是否真的装好。
- USB 数据线、USB 口、供电是否正常。
- Color、Depth、IR、Point Cloud 是否都有画面。
- 相机有没有被其他程序占用。

## 怎么打开

```text
D:\app\orbbec-astra-pro\启动上位机.bat
```

或者直接打开：

```text
D:\app\orbbec-astra-pro\viewer\OrbbecViewer.exe
```

## 和 PackVision 的边界

| 工具 | 用途 |
| --- | --- |
| OrbbecViewer | 到货验机、驱动/USB/画面排错 |
| PackVision | 实时测量、扫码/单号、体积重、历史记录、统计、WMS/TMS 队列 |

如果 OrbbecViewer 都没有深度画面，先别调 PackVision，优先查驱动、线、USB 口和相机。

如果 OrbbecViewer 有画面但 PackVision 没画面，再查 PackVision 的 OpenNI 采集后端。

## 到货后流程

1. 直连电脑 USB 口。
2. 打开 `D:\app\orbbec-astra-pro\启动上位机.bat`。
3. 确认 Color、Depth、IR、Point Cloud。
4. 关闭 OrbbecViewer，释放相机。
5. 启动 PackVision。
6. 看设备守护、采集探测和到货验收。
7. 用已知纸箱和汽车备件真值样本做验收。

## 相关笔记

- [[03 Astra Pro 深度相机新手教程]]
- [[04 Astra Pro 到货验收清单]]
- [[25 设备守护与现场恢复]]
- [[Astra Pro 厂商资料学习笔记]]
