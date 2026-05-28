# WMS/TMS 本地集成队列

PackVision 现在先实现本地 outbox 队列，而不是让测量流程直接依赖海外仓网络或某一个 WMS/TMS 厂商接口。

## 为什么这样做

- 仓库现场测量不能因为 WMS 网络慢、接口挂了、账号失效而卡住。
- 每次保存测量历史时，系统同步生成一条 `measurement.created` 待推送事件。
- 接入具体国家仓库的 WMS/TMS 时，可以配置轻量 HTTP 推送器消费 outbox 队列，成功后标记 `sent`，失败后标记 `failed` 并设置下次重试时间。

## 已提供接口

```text
GET  /api/integrations/outbox
GET  /api/integrations/outbox/summary
GET  /api/integrations/dispatch/status
GET  /api/integrations/outbox/export.csv
POST /api/integrations/outbox/dispatch
POST /api/integrations/outbox/{event_id}
```

## HTTP 推送器

默认不配置目标接口，PackVision 只保留本地 outbox 和 CSV 导出，不会误把事件标记为已推送。

现场 WMS/TMS 接口准备好后，设置：

```text
PACKVISION_INTEGRATION_HTTP_URL=https://wms.example.com/api/packvision/events
PACKVISION_INTEGRATION_HTTP_TOKEN=可选token
PACKVISION_INTEGRATION_TARGET=wms_tms
PACKVISION_INTEGRATION_TIMEOUT_MS=3000
```

测试现场流程但不想真的打 WMS/TMS 时，可以设置：

```text
PACKVISION_INTEGRATION_DRY_RUN=1
```

推送 payload 使用统一 envelope：

```json
{
  "schema": "packvision.integration_event.v1",
  "event_id": "wms_tms-...",
  "event_type": "measurement.created",
  "target": "wms_tms",
  "payload": {
    "schema": "packvision.measurement.v1",
    "order_id": "SO-001",
    "dimensions": {},
    "billing": {}
  }
}
```

## 事件状态

- `pending`：已保存到本地，等待推送。
- `failed`：推送失败，保留错误信息和重试次数。
- `sent`：目标系统已确认接收。

## 事件内容

事件包含：

- 单号、条码、测量记录 ID。
- 长宽高、体积、置信度、测量来源。
- 实重、体积重、计费重、体积重规则。
- 包装类型、材质线索、推荐采集方式。
- 本地图片/点云等证据路径。

## 现场使用方式

1. 仓库人员正常扫码、放件、记录稳定结果。
2. PackVision 保存历史记录，同时写入本地 outbox。
3. 数据中心可以查看“集成队列”，点击“推送到 WMS/TMS”，也可以导出 CSV。
4. WMS/TMS 不通时事件保留为 `failed`，到重试时间后继续推送，不影响现场继续测量。

## 尚未完成

- 还没有具体国家仓库的真实 WMS/TMS URL、认证方式和字段映射。
- 后台常驻自动推送 worker 仍建议等现场接口稳定后再启用；当前先用 API/UI 手动触发。
- 多国家仓库需要按实际系统补字段映射和重试策略。
