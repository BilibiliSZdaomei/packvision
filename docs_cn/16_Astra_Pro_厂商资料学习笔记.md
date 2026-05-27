# Astra Pro 厂商资料学习笔记与开发修正

更新日期：2026-05-27

资料来源：`D:\Documents\包装尺寸检测\奥比中光Astra Pro`

## 结论

Astra Pro 分支要以厂商链路为主：Windows 驱动和 OrbbecViewer 做硬件验收，OpenNI/ROS2 读取设备相机参数、`camera_info` 和点云，PackVision 在这些可靠数据之上做汽车备件尺寸测量。我们自己的标定逻辑只能作为非 Astra 手机照片兜底、工程复核或异常排查，不能替代厂商 SDK/OpenNI 的相机参数。

## 已学习的资料范围

| 资料 | 关键结论 |
| --- | --- |
| `产品规格书-Astra Pro_Datasheet _v2.0.pdf` | USB2.0，深度范围 0.6m-8m，1m 标称 +/-3mm，深度 640x480@30FPS，彩色 1280x720@30FPS |
| `上位机软件\上位机使用说明.pdf` | 先装 `SensorDriver_V4.3.0.17.exe`，再用 `OrbbecViewer.exe` 检查深度、彩色、红外、点云 |
| `ROS1系列教程\1、Astra相机标定` | ROS `camera_calibration` 标定流程，示例 `9x6` 内角点、`0.02m` 方格 |
| `ROS1系列教程\5、数据转换和点云` | 支持 `/camera/depth_registered/points`、PCD、PCL、点云可视化 |
| `ROS1系列教程\7、ARTag` | ARTag 依赖 `camera_info`，可用于工程定位/复核，不适合作为仓库日常强制动作 |
| `ROS1系列教程\8、Astra颜色识别与物体跟踪` | HSV、OpenCV 跟踪、KCF 等可以借鉴给前景分割/人工修正，但不是尺寸主链路 |
| `ROS2系列教程\OpenNI_ROS2_SDK...tar` | 暴露 `get_camera_params`、`get_camera_info`、`camera_info` topic、点云和 D2C 参数 |
| `上位机软件\上位机软件\OpenNI2\Drivers\orbbec.ini` | 可配置深度/彩色/IR 分辨率、Registration、SoftFilter、深度范围等 |
| `相关例程源码\OpenNI-Linux-x64-2.3.0.66.zip` | OpenNI 提供 `CoordinateConverter`，可做 depth/world/color 坐标转换 |

## Astra Pro 核心参数

| 项目 | 参数 |
| --- | --- |
| 成像原理 | 单目结构光 3D 成像 |
| 接口 | USB2.0，建议接电脑稳定 USB3.x 口或高质量供电 hub |
| 深度工作距离 | 0.6m - 8m |
| 深度分辨率 | 1280x1024@7FPS、640x480@30FPS、320x240@30FPS、160x120@30FPS |
| 彩色分辨率 | 1280x720@30FPS、640x480@30FPS、320x240@30FPS |
| 深度精度 | 1m: +/-3mm |
| 深度 FOV | H58.4°, V45.5° |
| 彩色 FOV | H66.1°, V40.2° |
| 功耗 | 2.5W MAX，峰值 500mA MAX |

## 厂商验收流程

1. 安装 `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\Window 驱动\SensorDriver_V4.3.0.17.exe`。
2. 插入 Astra Pro，在设备管理器中确认出现 `orbbec` 设备。
3. 运行 `D:\Documents\包装尺寸检测\奥比中光Astra Pro\上位机软件\上位机软件\OrbbecViewer.exe`。
4. 依次打开深度、彩色、红外、点云。
5. 红外异常时，选择 `640*480@30 (RGB 888)`。
6. 四路图像都正常，再进入 PackVision 调试。

## 标定策略修正

ROS 标定教程命令：

```bash
rosrun camera_calibration cameracalibrator.py image:=/camera/rgb/image_raw camera:=/camera/rgb --size 9x6 --square 0.02
rosrun camera_calibration cameracalibrator.py image:=/camera/ir/image camera:=/camera/ir --size 9x6 --square 0.02
```

PackVision 的策略：

- 仓库日常不做棋盘格标定。
- 工程师调试时才使用厂商随包棋盘格和 ROS 标定流程。
- Astra Pro 主流程优先读设备/SDK/ROS 的相机参数。
- 支持导入 ROS 标定 YAML，彩色相机名为 `rgb_camera`，深度/IR 相机名为 `ir_camera`。
- 手机照片模式不能要求仓库员工输入焦距、光圈、内参，只能自动读 EXIF、使用历史设备库、参考物和置信度。

## ROS2/OpenNI 关键接口

推荐优先接入：

```bash
ros2 topic echo /camera/depth/camera_info
ros2 topic echo /camera/color/camera_info
ros2 service call /camera/get_camera_info astra_camera_msgs/srv/GetCameraInfo '{}'
ros2 service call /camera/get_camera_params astra_camera_msgs/srv/GetCameraParams '{}'
ros2 service call /camera/get_device_info astra_camera_msgs/srv/GetDeviceInfo '{}'
ros2 service call /camera/get_sdk_version astra_camera_msgs/srv/GetString '{}'
```

`GetCameraParams` 包含：

- `l_intr_p`
- `r_intr_p`
- `r2l_r`
- `r2l_t`
- `l_k`
- `r_k`

ROS2 源码中 `ob_camera_info.cpp` 会通过 `openni::OBEXTENSION_ID_CAM_PARAMS` 读取厂商参数，再生成 ROS `CameraInfo`。点云源码使用 `CameraInfo` 的 `fx/fy/cx/cy` 将深度图转换成三维点云，`16UC1` 深度值按毫米转米。

OpenNI 可用坐标转换：

- `convertDepthToWorld`
- `convertWorldToDepth`
- `convertDepthToColor`
- `convertC2DCoordinateByIntrinsic`
- `convertD2CCoordinateByIntrinsic`

## 对 PackVision 的落地要求

必须新增：

- Astra 设备验收状态：驱动、OrbbecViewer、深度/彩色/红外/点云四路通过。
- 厂商参数读取状态：设备序列号、SDK 版本、`camera_info`、`get_camera_params`。
- 标定 YAML 导入接口：工程师模式，不暴露给仓库主流程。
- 深度质量门控：距离范围、空洞率、点云密度、黑色/反光/透明风险。
- 自动测量：不让仓库员工选择普通包装/异形件/长条件，由算法自动判断。
- 后台审计：记录测量次数、单号、设备、参数来源、置信度和异常原因。

## 材质和光照风险

厂商标定教程明确列出红外深度相机弱点：

- 黑色物体吸收红外线。
- 镜面反射物体容易测距失败或过曝。
- 透明物体红外可穿透。
- 太近物体不适合精确测距。

汽车备件场景应特别关注黑色橡胶、亮面金属、透明袋、油污反光包装。软件不能只输出尺寸，还要输出“为什么不可信”的质量原因。

## 后续开发顺序

1. 增加 Astra 厂商参数模型和导入 API。
2. 增加 `camera_info`/`get_camera_params` 解析测试。
3. UI 增加工程调试入口，主流程仍保持自动测量。
4. 点云测量算法改为厂商参数优先。
5. 保留自研标定为兜底，不再作为 Astra Pro 默认路径。
