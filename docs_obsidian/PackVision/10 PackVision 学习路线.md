---
title: PackVision 学习路线
date: 2026-05-28
tags:
  - PackVision
  - 学习路线
aliases:
  - PackVision 怎么学
status: active
---

# PackVision 学习路线

[[00 PackVision 知识地图|返回知识地图]]

## 只想会用

按顺序读：

1. [[01 PackVision 项目一句话说明]]
2. [[02 仓库日常操作流程]]
3. [[04 Astra Pro 到货验收清单]]
4. [[08 现场排错手册]]

## 想理解深度相机

按顺序读：

1. [[03 Astra Pro 深度相机新手教程]]
2. [[09 PackVision 术语表]]
3. [[Astra Pro 厂商资料学习笔记]]

## 想继续开发项目

按顺序读：

1. [[05 PackVision 接口与数据流]]
2. [[06 多相机三视图方案]]
3. `D:\Documents\包装尺寸检测\docs_cn\17_深度相机数据接入与多视图冗余.md`
4. `D:\Documents\包装尺寸检测\packvision\services\depth_devices.py`
5. `D:\Documents\包装尺寸检测\packvision\services\depth_capture.py`
6. `D:\Documents\包装尺寸检测\packvision\services\depth_fusion.py`

## 想做现场验收

准备：

- Astra Pro 相机。
- USB 数据线。
- 稳定支架。
- 卷尺或卡尺。
- 标准纸箱、长条件、异形件样品。

按顺序做：

1. [[04 Astra Pro 到货验收清单]]
2. [[07 汽车备件测量场景]]
3. [[08 现场排错手册]]

## 最重要的原则

> 仓库员工要简单，工程复杂度放在系统和工程师这边。

也就是说：

- 员工不填相机参数。
- 员工不选算法。
- 员工不管理接口。
- 系统自动判断，异常才提示复核。
