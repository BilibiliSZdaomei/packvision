# 专业级 DWS 工位 UI 标准

## 判断标准

专业尺寸采集软件不是普通表单，而是 DWS 工位：

- Dimensioning：尺寸持续采集。
- Weighing：实重和体积重联动。
- Scanning：单号/条码绑定业务记录。
- Evidence：图片、深度图、点云或截图留证。
- Review：异常进入复核。
- Traceability：历史、统计、接口调用可追溯。

## PackVision 当前 UI 标准

- 首页第一屏必须显示工位状态条。
- 实时采集状态必须常驻。
- 结果区没有照片时显示深度证据面板。
- 体积重规则和计费重必须常驻。
- 工程设置和手动修正默认隐藏。

## 本轮新增

- 工位状态条：状态、单号、计费重、质检结论。
- Astra Pro 深度证据面板：长、宽、高、置信度、证据保存状态。
- 窄屏布局修正：重量监控不再压到结果区。
- 工位成熟度评分改为“能力覆盖 + 现场闸口扣分”：真实相机未验证、电子秤未接入、单号/WMS 缺口、设备 watchdog 异常都会降低首屏成熟度。

## 工位成熟度评分

`/api/station/snapshot` 的 `professional_score` 现在包含：

| 字段 | 说明 |
| --- | --- |
| `capability_percent` | 尺寸、称重、扫码、证据、接口、设备健康的能力覆盖分。 |
| `percent` | 扣除现场闸口后的实际成熟度，UI 默认显示这个值。 |
| `gate_penalties` | 扣分原因和扣分点数。 |
| `level` | `pre_hardware_ready`、`field_trial_limited`、`industrial_pilot_ready` 等。 |

> [!important]
> 模拟实时流只能说明业务链路能跑，不能算真实生产验收。真实相机、电子秤、单号/WMS 和设备健康都通过后，才应该显示更高成熟度。

## 对标对象

- DIMS-it
- Cargo Spectre
- Rice Lake iDimension
- SICK DWS
- Cubiscan

## 下一步

- 对接电子秤。
- 自动匹配国家/承运商体积重规则。
- 数据中心增加主管汇报视图。
- 用真实相机画面和点云证据替代模拟证据。
