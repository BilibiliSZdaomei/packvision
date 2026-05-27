# 厂商资料包 Git 维护策略

> 日期：2026-05-28  
> 结论：可以维护进项目，但不要默认把完整原始二进制资料包塞进普通 Git 历史。推荐做法是：普通 Git 保存资料清单、校验、说明和适配文档；驱动/SDK/DLL/大 PDF 走 Git LFS、私有 Release 或本地资料镜像。

## 1. 当前 Astra Pro 资料包情况

本地资料包：

```text
D:\Documents\包装尺寸检测\奥比中光Astra Pro
```

统计：

| 项目 | 数值 |
| --- | ---: |
| 文件数 | 158 |
| 总大小 | 367.44 MB |
| 最大单文件 | 82.61 MB |
| 超过 GitHub 普通 100 MB 单文件限制 | 0 |

技术上，这个包能被 GitHub 普通仓库接收，因为没有单文件超过 100 MB。  
但它会让仓库一次性增加约 367 MB，而且里面包含驱动、DLL、SDK 压缩包、字体、PDF、示例源码等内容。

## 2. 为什么不建议直接全量进普通 Git

1. **仓库会迅速膨胀**：后面如果再加新相机资料包，仓库会很快变成数 GB。
2. **Git 历史不好清理**：二进制文件一旦进历史，即使删除，历史里仍然存在。
3. **公开仓库有授权风险**：用户无所谓不等于厂商允许公开再分发驱动和 SDK。
4. **CI/克隆变慢**：以后任何人 clone 项目都会下载这些资料。
5. **交付包目标不同**：海外仓交付包要小于 100 MB，厂商完整资料包不是每次都应该带上。

## 3. 推荐策略

### 默认策略

普通 Git 追踪：

- 厂商资料 README。
- 文件清单。
- SHA-256 校验。
- 安装和适配说明。
- PackVision 中使用哪些文件的说明。

普通 Git 不追踪：

- 完整驱动安装包。
- SDK 压缩包。
- DLL、LIB、PDB。
- 大型 PDF、视频、示例包。
- 厂商上位机完整目录。

### 如果一定要把完整包放到 GitHub

建议只在满足这些条件时做：

1. GitHub 仓库是私有仓库。
2. 确认厂商资料允许团队内部保存和同步。
3. 使用 Git LFS 或 Release Assets，不走普通 Git blob。
4. 每个厂商相机单独目录，不混在主代码目录。

## 4. 当前项目已配置

新增目录：

```text
D:\Documents\包装尺寸检测\vendor_assets
```

当前 Astra Pro：

```text
D:\Documents\包装尺寸检测\vendor_assets\orbbec-astra-pro
```

新增脚本：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\inventory_vendor_package.ps1
```

作用：

- 扫描厂商资料包。
- 生成文件清单。
- 计算每个文件 SHA-256。
- 记录总大小、最大文件、扩展名大小分布。

当前生成：

```text
D:\Documents\包装尺寸检测\vendor_assets\orbbec-astra-pro\manifest.json
```

## 5. 以后新增厂商相机怎么做

假设未来买了更好的深度相机，建议目录结构：

```text
vendor_assets/
  orbbec-astra-pro/
    README.md
    manifest.json
  realsense-d455/
    README.md
    manifest.json
  orbbec-gemini-2/
    README.md
    manifest.json
```

如果要镜像二进制：

```text
vendor_assets/<camera-id>/binaries/
```

`binaries` 目录下的大文件由 `.gitattributes` 配置为 Git LFS。

## 6. 我的建议

当前先不要把 `奥比中光Astra Pro` 原始资料包全量提交进普通 Git。  
我们已经把资料清单、校验和维护策略放进仓库，足够支持开发、排错和交接。

如果后面你确认仓库是私有的，并且愿意承担 Git LFS 存储/流量成本，我再把完整厂商资料包迁入：

```text
vendor_assets/orbbec-astra-pro/binaries/
```

这样既方便维护，也不会让主代码仓库变得不可控。
