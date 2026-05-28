# Astra Pro 驱动与上位机说明

更新日期：2026-05-28

## 当前电脑检查结论

本机已经安装 Astra Pro 的 Windows 驱动：

- 程序列表：`SensorDriver V4.3.0.17`
- 发布者：`SHENZHEN ORBBEC CO., LTD.`
- DriverStore：`oem221.inf`
- 原始驱动：`obdrv4.inf`
- Provider：`Orbbec`
- Driver Version：`10/20/2020 4.3.0.17`

当前没有真实 Astra Pro 接入，所以设备枚举里还看不到 Astra/Orbbec 相机。相机到货后，接上 USB 数据线再跑验收。

## 资料包里的文件

| 文件 | 作用 |
| --- | --- |
| `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\Window 驱动\SensorDriver_V4.3.0.17.exe` | Windows 相机驱动安装包 |
| `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\上位机软件\OrbbecViewer.exe` | 厂商上位机，也就是官方相机查看和验收工具 |
| `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\上位机软件\OpenNI2.dll` | OpenNI2 运行库 |
| `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\上位机软件\OpenNI2\Drivers\orbbec.dll` | Orbbec OpenNI 驱动 |
| `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\上位机使用说明.pdf` | 上位机使用说明 |

已整理到 `D:\app` 的现场目录：

```text
D:\app\orbbec-astra-pro
D:\app\orbbec-astra-pro\driver\SensorDriver_V4.3.0.17.exe
D:\app\orbbec-astra-pro\viewer\OrbbecViewer.exe
D:\app\orbbec-astra-pro\启动上位机.bat
D:\app\orbbec-astra-pro\检查Astra安装.ps1
```

## 上位机软件是什么

这里的“上位机软件”就是奥比中光提供的 `OrbbecViewer`。

它不是 PackVision 的替代品，也不是仓库员工每天用来录单的软件。它的定位是：

- 验证驱动是否安装成功。
- 验证相机 USB、供电和数据传输是否正常。
- 查看 Color、Depth、IR、Point Cloud 画面。
- 排查 PackVision 接不通相机时，是硬件/驱动问题，还是 PackVision 采集后端问题。

判断逻辑很简单：

| 现象 | 结论 |
| --- | --- |
| OrbbecViewer 都没有深度画面 | 先查驱动、USB 线、USB 口、供电、相机本体。 |
| OrbbecViewer 有深度画面，PackVision 没有 | 再查 PackVision 的 OpenNI/采集后端。 |
| OrbbecViewer 和 PackVision 都有画面 | 可以进入已知纸箱和汽车备件样本验收。 |

## 到货后的正确使用顺序

1. 先直连电脑 USB 口，不要一开始就接 Hub。
2. 打开：

```text
D:\app\orbbec-astra-pro\启动上位机.bat
```

3. 在 OrbbecViewer 中确认 Color、Depth、IR、Point Cloud 都能出图。
4. 关闭 OrbbecViewer，避免它占用相机。
5. 启动 PackVision。
6. 运行 PackVision 的到货验收、设备守护和采集探测。
7. 用已知纸箱、长条件、异形件、黑色/反光/透明件做第一批真值验收。

## 和 PackVision 的关系

PackVision 应该把 OrbbecViewer 当成“官方验机工具”，而不是日常工作台。

PackVision 已经接入：

- `/api/depth/status`：检查资料包、驱动安装包、驱动安装状态、上位机、OpenNI 运行库。
- `/api/deployment/readiness`：海外仓开箱即用体检。
- `/api/device/watchdog`：设备守护和恢复动作。
- `/api/depth/capture/probe`：相机采集后端探测。

下一步现场验证时，先用 OrbbecViewer 证明硬件可用，再用 PackVision 证明测量、记录、体积重、历史和导出可用。
