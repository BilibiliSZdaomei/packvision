---
title: PackVision 术语表
date: 2026-05-28
tags:
  - PackVision
  - 术语表
aliases:
  - 深度相机术语
status: active
---

# PackVision 术语表

[[00 PackVision 知识地图|返回知识地图]]

## 深度图

每个像素不是颜色，而是距离。

PackVision 用它算物体的长宽高。

## OpenNI

一种深度相机通用接口。

Astra Pro 可以通过厂商 OpenNI runtime 被 PackVision 读取。

## OrbbecViewer

奥比中光官方上位机。

它不是仓库员工日常软件，而是工程师验收和排错工具。

## camera_id

PackVision 给每台相机起的名字。

例：`astra-pro-top-01`

## role

相机在工位里的角色。

常用：

- `top`：顶视图。
- `front`：前视图。
- `left` / `right`：侧视图。

## intrinsics / 内参

相机内部参数。

仓库员工不需要懂，也不需要手动填。

## camera_info

ROS 或相机驱动输出的相机参数。

比人工猜焦距可靠。

## ROI

框选区域。

意思是告诉系统：“只看这块区域”。

## object-mask

把物体从背景里分出来。

异形件更适合用这个。

## point cloud / 点云

把深度图转换成 3D 点。

适合测异形件和长条件。

## conservative_max

多视角融合策略。

意思是：多个角度测出来不一样时，长宽高取更保守的最大值，避免低估物流尺寸。

## quality_flags

质量标记。

例如：

- 深度点太少。
- 材质可能反光。
- 结果需要复核。

## save_to_history

是否保存到历史记录。

现场正式测量应保存，调试演示可以不保存。
