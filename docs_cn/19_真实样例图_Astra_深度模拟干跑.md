# 真实样例图 Astra 深度模拟干跑

这一步用于相机到货前验证 PackVision 的深度测量链路。它和以前的纯绘制 demo 不一样：RGB 图像来自公开数据集的真实箱内场景，深度帧由软件按 Astra Pro 近似内参模拟生成。

## 数据来源

本轮默认使用 CLUBS Dataset 的箱内场景动图：

```text
https://clubs.github.io/gif/box_000.gif
```

CLUBS 项目页：

```text
https://clubs.github.io/
```

CLUBS 是 ETH Zurich Autonomous Systems Lab 发布的 RGB-D 数据集，项目页说明它包含 realistic warehouse box scenarios、RGB-D、2D/3D 标注和标定数据。这个场景比普通网页纸箱照片更适合我们做仓库模拟。

## 新增能力

### 1. 上传真实图片做深度干跑

接口：

```text
POST /api/depth/simulate-from-image
```

输入：

- `image`：真实图片，支持 jpg/png/webp/bmp/gif。
- `table_depth_mm`：模拟桌面/箱底深度，默认 `1200`。
- `object_depth_mm`：模拟物体表面深度，默认 `850`。
- `roi_json`：可选，格式 `[x1,y1,x2,y2]`。
- `frame_index`：GIF 或视频帧图像时抽第几帧，默认 `0`。
- `order_id`、`barcode_text`、`part_category` 等追溯字段照旧可用。

输出：

- Astra Pro FOV 推算内参。
- 合成深度帧测出的长宽高。
- `source_image_url`：抽帧后的真实 RGB 图。
- `simulation_overlay_url`：测量标注图。
- `depth_preview_url`：模拟深度预览图。
- `quality_flags` 会明确写入：
  - `hardware_not_connected`
  - `real_rgb_image_used`
  - `synthetic_depth_frame_used`
  - `astra_intrinsics_simulated_from_datasheet_fov`

### 2. 一键下载公开样例并跑测量

命令：

```powershell
.\scripts\run_real_sample_simulation.ps1
```

默认输出：

```text
D:\Documents\包装尺寸检测\data\simulation_samples\clubs_box_000\clubs_box_000_measurement.json
D:\Documents\包装尺寸检测\data\simulation_samples\clubs_box_000\clubs_box_000_overlay.png
D:\Documents\包装尺寸检测\data\simulation_samples\clubs_box_000\clubs_box_000_depth_preview.png
```

本次干跑结果：

```text
L=475.5 mm
W=296.7 mm
H=349.0 mm
```

注意：这个结果不是这张图的真实尺寸，只表示“真实 RGB 图片 + 模拟 Astra 内参 + 模拟深度帧”可以跑完整测量链路。

## 为什么这样做

深度相机还没到货时，我们没法得到真实 `depth_frame`。但我们可以先验证：

- 图片解码。
- 真实场景前景 mask。
- Astra Pro FOV 内参估算。
- 深度帧格式。
- `measure_depth_object_mask()`。
- 标注图生成。
- 后台调用统计。
- 后续历史记录字段兼容。

等 Astra Pro 到货后，把“合成深度帧”替换成真实 OpenNI/ROS2 深度帧即可，接口和测量逻辑不需要重写。

## 现场口径

这不是最终精度验证；最终精度必须用真实 Astra Pro 深度帧和人工真值对比。它的价值是提前验证软件链路，让相机到货后重点排查硬件、驱动、USB、光照和标定，而不是到现场才发现接口没打通。
