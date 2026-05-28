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
- `GET /api/integrations/outbox/export.csv`
- `POST /api/integrations/outbox/{event_id}`

## 状态

- `pending`：等待推送。
- `failed`：推送失败，记录错误和重试次数。
- `sent`：已被目标系统确认。

## 下一步

- 接真实 WMS/TMS URL 和认证。
- 增加后台自动推送 worker。
- 按国家仓库做字段映射。
