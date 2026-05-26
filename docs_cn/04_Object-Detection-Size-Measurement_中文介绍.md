# Object-Detection-Size-Measurement 中文介绍

## 项目来源

仓库地址：`https://github.com/Ali619/Object-Detection-Size-Measurement`

这是一个基于 ArUco 标记的实时物体尺寸测量示例。作者没有使用激光测距或深度相机，而是用打印出来的 ArUco 标记作为尺度基准，再测量画面中的其他物体。

## 解决的问题

它解决的是“没有深度相机时，如何用普通摄像头和 ArUco 标记估算物体宽高”的问题。

这与 PackVision 当前 MVP 非常接近。

## 核心算法流程

主要脚本：

- `measure_object_size_camera.py`
- `object_detector.py`

流程如下：

1. 打开摄像头。
2. 使用 OpenCV ArUco 检测 5x5 字典中的标记。
3. 绘制标记边框。
4. 计算 ArUco 标记的周长像素值。
5. 因为示例标记实际尺寸是 5 cm × 5 cm，所以真实周长是 20 cm。
6. 用 `aruco_perimeter / 20` 得到 `pixel_cm_ratio`。
7. 通过对象检测器找出其他物体轮廓。
8. 对轮廓计算最小旋转外接矩形。
9. 用像素宽高除以 `pixel_cm_ratio` 得到厘米尺寸。
10. 在画面上显示宽和高。

## 运行方式

README 说明运行：

```powershell
python measure_object_size_camera.py
```

需要安装：

```powershell
pip install opencv-contrib-python
```

注意：必须安装 `opencv-contrib-python`，因为普通 `opencv-python` 可能没有 `cv2.aruco` 模块。

## 值得借鉴的地方

对 PackVision 有价值的点：

- 用 ArUco 替代普通参考物，稳定性更高。
- 通过标记周长换算像素到厘米。
- 实时摄像头方案可以作为 PackVision 后续接 USB 摄像头的参考。
- 代码结构简单，容易看懂。

## 局限

该项目更像教学示例，不是工程系统：

- 摄像头 ID 硬编码为 `1`。
- ArUco 尺寸写死为 5 cm × 5 cm。
- 只测画面中的二维宽高。
- 对背景和轮廓质量敏感。
- 没有上传接口。
- 没有结果记录和证据图保存。
- 没有多语言 UI。
- 没有高度测量策略。

## 对 PackVision 的整合建议

PackVision 已经吸收了这个项目最重要的思想：ArUco 标记作为尺度基准。

后续可以继续吸收：

- 增加实时摄像头采集模式。
- 允许用户选择摄像头。
- 增加摄像头画面中的标记检测状态提示。
- 在 UI 中实时提示“标记未检测到”“标记太小”“角度过斜”。
- 将 ArUco 标记尺寸做成可配置项。
