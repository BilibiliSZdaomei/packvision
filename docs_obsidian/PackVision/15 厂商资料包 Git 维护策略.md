---
title: 厂商资料包 Git 维护策略
date: 2026-05-28
tags:
  - PackVision
  - 厂商资料
  - Git
  - GitLFS
  - 深度相机
status: active
---

# 厂商资料包 Git 维护策略

> [!summary] 结论
> Astra Pro 资料包技术上可以进 Git，因为没有单文件超过 100 MB；但整包约 367.44 MB，且包含驱动、DLL、SDK 和 PDF。推荐普通 Git 保存清单和校验，二进制只在私有仓库/Git LFS/Release 资产中镜像。

## 当前资料包

```text
D:\Documents\包装尺寸检测\奥比中光Astra Pro
```

统计：

- 文件数：158
- 总大小：367.44 MB
- 最大单文件：82.61 MB
- 超过 100 MB 的文件：0

## 当前项目做法

新增目录：

```text
D:\Documents\包装尺寸检测\vendor_assets
```

新增脚本：

```powershell
PowerShell -ExecutionPolicy Bypass -File "D:\Documents\包装尺寸检测\scripts\inventory_vendor_package.ps1"
```

生成清单：

```text
D:\Documents\包装尺寸检测\vendor_assets\orbbec-astra-pro\manifest.json
```

## 为什么不默认全量进普通 Git

- 仓库会膨胀。
- 二进制进入 Git 历史后很难清理。
- 公开仓库可能有厂商再分发授权风险。
- 后续新增多个相机后会更难维护。
- 海外仓交付包目标是 100 MB 内，不应每次带完整厂商包。

## 什么时候可以全量传

满足这些条件时可以：

1. 仓库是私有仓库。
2. 厂商资料允许团队内部保存。
3. 用 Git LFS 或 Release Assets。
4. 放到 `vendor_assets/<camera-id>/binaries/`。

## 相关

- [[00 PackVision 知识地图]]
- [[14 PackVision 完整项目报告]]
- [[12 海外仓开箱即用交付方案]]
