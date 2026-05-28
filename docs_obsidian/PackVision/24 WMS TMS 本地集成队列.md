# WMS/TMS 本地集成队列

[[14 PackVision 完整项目报告]] | [[22 工业级架构评估与中型升级方案]]

PackVision 先落地本地 outbox 队列：测量记录保存成功后，自动生成 `measurement.created` 待推送事件。

## 作用

- 现场测量不断流。
- WMS/TMS 不在线时不丢数据。
- 后续国家仓库接口不同，也可以复用同一个本地队列。

## 接口

- `GET /api/integrations/outbox`
- `GET /api/integrations/outbox/summary`
- `GET /api/integrations/dispatch/status`
- `GET /api/integrations/outbox/export.csv`
- `POST /api/integrations/outbox/dispatch`
- `POST /api/integrations/outbox/{event_id}`

## 状态

- `pending`：等待推送。
- `failed`：推送失败，记录错误和重试次数。
- `sent`：已被目标系统确认。

## HTTP 推送器

默认不配置目标接口，系统只保留本地 outbox，不误标已推送。

现场接口准备好后配置：

```text
PACKVISION_INTEGRATION_HTTP_URL=https://wms.example.com/api/packvision/events
PACKVISION_INTEGRATION_HTTP_TOKEN=可选token
PACKVISION_INTEGRATION_TARGET=wms_tms
```

测试时可以用：

```text
PACKVISION_INTEGRATION_DRY_RUN=1
```

UI 的“推送到 WMS/TMS”会调用 `POST /api/integrations/outbox/dispatch`。成功标记 `sent`；失败标记 `failed` 并保留下次重试时间。

## 还要按现场补的

- 真实 WMS/TMS URL 和认证。
- 各国家仓库字段映射。
- 接口稳定后再启用后台常驻自动推送 worker。
