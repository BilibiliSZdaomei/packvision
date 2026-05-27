# Astra Pro 教程二次审计与项目适配

本次复查的目标不是把厂商教程原样搬进 PackVision，而是把对仓库测量有价值的内容，转成项目能调用、能展示、能追溯的接口和配置。

## 这次补上的遗漏

### 1. ROS2 控制服务

厂商 ROS2 教程里有一组容易被忽略的服务：

- `/camera/set_ir_exposure`
- `/camera/get_ir_exposure`
- `/camera/set_ir_gain`
- `/camera/get_ir_gain`
- `/camera/set_color_exposure`
- `/camera/set_color_auto_exposure`
- `/camera/set_color_auto_white_balance`
- `/camera/set_depth_mirror`
- `/camera/set_color_mirror`
- `/camera/set_laser_enable`
- `/camera/toggle_depth`
- `/camera/toggle_color`

这些不应该直接暴露给仓库员工，因为他们的工作流应该是自动测量。但它们必须进入项目，供工程调试使用：光照导致深度孔洞、相机倒装导致画面翻转、反光件导致 IR 噪声、RGB 预览和条码图不稳定时，都需要查这些参数。

项目新增接口：

```text
GET /api/depth/astra/tutorial-playbook
```

返回内容包括 ROS2 控制服务目录、适合 PackVision 的用途、是否工程师专用、默认安全策略。

### 2. 多相机启动逻辑

厂商教程里明确提到多相机要处理：

- `device_num`
- serial number
- `multi_astra.launch.xml`
- `cleanup_shm_node`

这对我们后续两台、三台深度相机很关键。PackVision 现在会在相机配置里自动带上 `ros2_profile`，并在：

```text
GET /api/depth/cameras
```

里返回多相机 ROS2 建议：

```text
ros2 run astra_camera list_devices_node
ros2 run astra_camera cleanup_shm_node
ros2 launch astra_camera astra_pro.launch.xml
ros2 launch astra_camera multi_astra.launch.xml
```

现场逻辑是：

1. 先单台相机验证。
2. 记录每台相机序列号和物理位置。
3. 配置 `top / front / left_or_right` 角色。
4. 多相机启动前设置 `device_num`。
5. 如果 ROS2 多相机启动失败，先跑 `cleanup_shm_node` 再重试。

### 3. 内参与标定导入

仓库员工不能手动输入焦距、光圈、内参。项目继续坚持这个策略：

1. 优先读取 `/camera/depth/camera_info`。
2. 其次导入厂商 ROS 标定 YAML。
3. 最后才使用 Astra Pro FOV 估算作为工程兜底。

厂商教程里 `ir_info_url` 和 `color_info_url` 的规则已经映射到 PackVision：

- 深度/IR：`camera_name` 应为 `ir_camera`
- 彩色/RGB：`camera_name` 应为 `rgb_camera`
- 统一通过 `POST /api/depth/camera-info/normalize` 转成测量接口可用的 `fx/fy/cx/cy`

### 4. 点云和 D2C 对齐

厂商教程里的 `enable_point_cloud`、`enable_colored_point_cloud`、`depth_registration`、`color_depth_synchronization` 已经进入 `ros2_profile`。

默认策略：

- 仓库日常测量：不开复杂 RGB 点云，保持轻量。
- 工程验证：可以开启点云，用来证明异形件、长条件和多视角融合的几何逻辑。
- 需要 RGB/深度叠图时，再启用 D2C 对齐。

## 和 PackVision 的适配关系

| 厂商资料内容 | PackVision 落地位置 |
| --- | --- |
| ROS2 服务控制 | `GET /api/depth/astra/tutorial-playbook` |
| 多相机 `device_num` | `GET /api/depth/cameras` 与相机配置 `target_camera_count` |
| serial number | 相机配置 `cameras[].serial_hint` |
| `cleanup_shm_node` | 多相机排错建议 |
| `ir_info_url` / `color_info_url` | `POST /api/depth/camera-info/normalize` |
| 点云 / D2C | `cameras[].ros2_profile.point_cloud` |
| ROS1 QR/条码教程 | 已由 `/api/orders/scan` 和 `/api/orders/decode-image` 覆盖 |
| 麦克风教程 | 与尺寸测量无关，暂不纳入产品功能 |

## 对仓库现场的原则

- 员工只做：扫码、放货、拍摄/采集、确认、保存。
- 自动测量优先，不让员工选择复杂模式。
- 工程师才看曝光、增益、镜像、点云、D2C、ROS2 启动参数。
- 后续相机升级时，仍保持 `camera_id + role + backend + serial_hint + ros2_profile` 这个配置结构。

## 相关文件

```text
D:\Documents\包装尺寸检测\packvision\services\astra_tutorials.py
D:\Documents\包装尺寸检测\packvision\services\depth_devices.py
D:\Documents\包装尺寸检测\packvision\services\astra_vendor.py
D:\Documents\包装尺寸检测\docs_cn\18_Astra_Pro_教程二次审计与项目适配.md
```
