from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from packvision import __version__


def build_field_trial_report(
    *,
    readiness: dict[str, Any] | None = None,
    station: dict[str, Any] | None = None,
    history_items: list[dict[str, Any]] | None = None,
    review: dict[str, Any] | None = None,
    usage: dict[str, Any] | None = None,
    scale: dict[str, Any] | None = None,
    integration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    readiness = readiness or {}
    station = station or {}
    history_items = history_items or []
    review = review or {}
    usage = usage or {}
    scale = scale or {}
    integration = integration or {}

    scorecard = _scorecard(
        readiness=readiness,
        station=station,
        history_items=history_items,
        review=review,
        usage=usage,
        scale=scale,
        integration=integration,
    )
    verdict = _verdict(scorecard, readiness)
    return {
        "report_type": "packvision_field_trial_report",
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "scorecard": scorecard,
        "summary": {
            "score_percent": _score_percent(scorecard),
            "history_records": len(history_items),
            "review_samples": int((review.get("summary") or {}).get("total_review_samples") or 0),
            "measurement_calls": int(usage.get("measurement_calls") or 0),
            "failed_calls": int(usage.get("failed_calls") or 0),
            "station_status": station.get("station_status") or "unknown",
            "scale_status": scale.get("status") or "unknown",
            "integration_status": (integration.get("dispatch") or {}).get("status") or "local_outbox",
        },
        "evidence": {
            "readiness": _compact_readiness(readiness),
            "station": _compact_station(station),
            "latest_records": [_compact_history(item) for item in history_items[:5]],
            "review": review.get("summary") or {},
            "usage": _compact_usage(usage),
            "scale": _compact_scale(scale),
            "integration": _compact_integration(integration),
        },
        "next_actions": _next_actions(scorecard, readiness, station),
    }


def field_trial_report_markdown(report: dict[str, Any]) -> str:
    verdict = report.get("verdict") or {}
    summary = report.get("summary") or {}
    lines = [
        "# PackVision 现场试运行报告",
        "",
        f"- 生成时间：{report.get('generated_at')}",
        f"- 软件版本：{report.get('version')}",
        f"- 结论：{verdict.get('label')}",
        f"- 说明：{verdict.get('message')}",
        f"- 证据得分：{summary.get('score_percent')}%",
        f"- 历史记录：{summary.get('history_records')}",
        f"- 复核样本：{summary.get('review_samples')}",
        f"- 测量调用：{summary.get('measurement_calls')}",
        "",
        "## 验收项",
        "",
        "| 项目 | 状态 | 证据 |",
        "| --- | --- | --- |",
    ]
    for item in report.get("scorecard") or []:
        lines.append(f"| {item.get('label')} | {item.get('status')} | {item.get('evidence')} |")
    lines.extend(["", "## 下一步", ""])
    for action in report.get("next_actions") or []:
        lines.append(f"- {action.get('label')}: {action.get('detail')}")
    return "\n".join(lines) + "\n"


def _scorecard(
    *,
    readiness: dict[str, Any],
    station: dict[str, Any],
    history_items: list[dict[str, Any]],
    review: dict[str, Any],
    usage: dict[str, Any],
    scale: dict[str, Any],
    integration: dict[str, Any],
) -> list[dict[str, Any]]:
    modes = readiness.get("readiness_modes") or {}
    summary = readiness.get("summary") or {}
    station_score = station.get("professional_score") or {}
    live_status = station.get("station_status") or "unknown"
    watchdog = station.get("device_watchdog") or {}
    review_summary = review.get("summary") or {}
    dispatch = integration.get("dispatch") or {}
    integration_status = dispatch.get("status") or "not_configured"
    latest = history_items[0] if history_items else {}

    return [
        _item(
            "local_app",
            "本地程序和 UI",
            "pass" if (modes.get("image_only") or {}).get("ready") else "fail",
            "图片版、UI、历史目录和 OpenCV 运行时",
        ),
        _item(
            "depth_preinstall",
            "Astra Pro 驱动和上位机",
            "pass" if (modes.get("depth_preinstall") or {}).get("ready") else "attention",
            f"driver/viewer/OpenNI 预装={bool((modes.get('depth_preinstall') or {}).get('ready'))}",
        ),
        _item(
            "camera_hardware",
            "真实深度相机连接",
            "pass" if (modes.get("camera_trial") or {}).get("ready") else "pending_hardware",
            f"connected_devices={(modes.get('camera_trial') or {}).get('openni_device_count')}",
        ),
        _item(
            "live_monitor",
            "实时监控和自动测量",
            "pass" if live_status in {"ready_to_record", "measuring", "waiting_for_object", "needs_review"} else "attention",
            f"station_status={live_status}; score={station_score.get('percent')}",
        ),
        _item(
            "stable_record",
            "稳定结果记录",
            "pass" if latest.get("measurement_id") else "needs_sample",
            latest.get("measurement_id") or "还需要保存一条现场样本记录",
        ),
        _item(
            "scale",
            "实重和电子秤",
            "pass" if scale.get("status") == "auto_weight_ready" else "manual_fallback",
            f"scale_status={scale.get('status') or 'unknown'}; configured={bool(scale.get('configured'))}",
        ),
        _item(
            "history",
            "历史追溯",
            "pass" if history_items else "needs_sample",
            f"records={len(history_items)}",
        ),
        _item(
            "review_pool",
            "复核样本池",
            "pass",
            f"review_samples={int(review_summary.get('total_review_samples') or 0)}",
        ),
        _item(
            "usage",
            "后台调用和测量次数",
            "pass" if int(usage.get("total_calls") or 0) > 0 else "attention",
            f"total_calls={int(usage.get('total_calls') or 0)}; measurement_calls={int(usage.get('measurement_calls') or 0)}",
        ),
        _item(
            "integration",
            "WMS/TMS 集成队列",
            "pass" if integration_status == "ready" else "local_outbox_ready",
            f"dispatch={integration_status}; pending={int(integration.get('pending') or 0)}; failed={int(integration.get('failed') or 0)}",
        ),
        _item(
            "supportability",
            "现场支持和恢复",
            "pass" if int(summary.get("blocker_count") or 0) == 0 else "fail",
            f"readiness={readiness.get('status')}; watchdog={watchdog.get('status') or 'unknown'}",
        ),
    ]


def _verdict(scorecard: list[dict[str, Any]], readiness: dict[str, Any]) -> dict[str, Any]:
    statuses = {item["id"]: item["status"] for item in scorecard}
    if any(status == "fail" for status in statuses.values()):
        return {
            "status": "needs_attention",
            "label": "需要先处理阻断项",
            "message": "本机基础运行条件还有阻断项，暂不进入现场试运行。",
        }
    if statuses.get("camera_hardware") == "pending_hardware":
        return {
            "status": "pre_hardware_ready",
            "label": "相机到货前准备就绪",
            "message": "软件、驱动和上位机链路已可验收；真实尺寸精度仍需接入 Astra Pro 后验证。",
        }
    if statuses.get("stable_record") == "pass" and statuses.get("history") == "pass":
        return {
            "status": "field_trial_ready",
            "label": "可进入现场试运行",
            "message": "已具备实时测量、记录、追溯和支持包证据；继续按真值样本做精度验收。",
        }
    return {
        "status": "sample_collection_needed",
        "label": "需要补充现场样本",
        "message": "运行链路可用，但还需要保存标准纸箱、长条件、异形件和异常材质样本记录。",
    }


def _score_percent(scorecard: list[dict[str, Any]]) -> int:
    strong = {"pass", "local_outbox_ready", "manual_fallback"}
    total = max(1, len(scorecard))
    return round(sum(1 for item in scorecard if item["status"] in strong) / total * 100)


def _next_actions(
    scorecard: list[dict[str, Any]],
    readiness: dict[str, Any],
    station: dict[str, Any],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    status_by_id = {item["id"]: item["status"] for item in scorecard}
    if status_by_id.get("camera_hardware") == "pending_hardware":
        actions.append(
            _action("connect_astra_pro", "接入真实 Astra Pro", "先用 OrbbecViewer 验深度画面，再回到 PackVision 采集探测。")
        )
    if status_by_id.get("stable_record") != "pass":
        actions.append(_action("save_truth_sample", "保存第一条真值样本", "用已知纸箱输入单号和实重，记录稳定结果。"))
    if status_by_id.get("scale") == "manual_fallback":
        actions.append(_action("scale_adapter", "接入电子秤", "现场可先手动输入实重，后续再配置 RS232/HID 电子秤。"))
    if status_by_id.get("integration") == "local_outbox_ready":
        actions.append(_action("configure_wms", "配置 WMS/TMS 推送", "设置接口 URL 和 token；未配置时本地队列和 CSV 仍可追溯。"))
    for item in (station.get("production_gaps") or [])[:3]:
        actions.append(_action(item.get("code") or "station_gap", "工位缺口", item.get("message") or "继续按工位提示处理。"))
    if not actions:
        actions.append(_action("continue_truth_trials", "继续真值验收", "按标准纸箱、长条件、异形件、异常材质分组采样。"))
    return actions


def _compact_readiness(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": readiness.get("status"),
        "summary": readiness.get("summary") or {},
        "readiness_modes": readiness.get("readiness_modes") or {},
        "blockers": readiness.get("blockers") or [],
        "warnings": readiness.get("warnings") or [],
    }


def _compact_station(station: dict[str, Any]) -> dict[str, Any]:
    return {
        "station_status": station.get("station_status"),
        "operator_mode": station.get("operator_mode"),
        "professional_score": station.get("professional_score") or {},
        "current_candidate": station.get("current_candidate") or {},
        "latest_record": station.get("latest_record") or {},
        "production_gaps": station.get("production_gaps") or [],
    }


def _compact_history(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "measurement_id": item.get("measurement_id"),
        "created_at": item.get("created_at"),
        "order_id": item.get("order_id"),
        "status": item.get("status"),
        "confidence": item.get("confidence"),
        "length_mm": item.get("length_mm"),
        "width_mm": item.get("width_mm"),
        "height_mm": item.get("height_mm"),
        "chargeable_weight_kg": item.get("chargeable_weight_kg"),
    }


def _compact_usage(usage: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_calls": usage.get("total_calls"),
        "measurement_calls": usage.get("measurement_calls"),
        "failed_calls": usage.get("failed_calls"),
        "success_rate": usage.get("success_rate"),
        "today_measurements": usage.get("today_measurements"),
    }


def _compact_scale(scale: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": scale.get("status"),
        "source": scale.get("source"),
        "configured": bool(scale.get("configured")),
        "weight_kg": scale.get("weight_kg"),
        "stable": bool(scale.get("stable")),
    }


def _compact_integration(integration: dict[str, Any]) -> dict[str, Any]:
    return {
        "delivery_mode": integration.get("delivery_mode"),
        "dispatch": integration.get("dispatch") or {},
        "total": integration.get("total"),
        "pending": integration.get("pending"),
        "failed": integration.get("failed"),
        "due_for_retry": integration.get("due_for_retry"),
    }


def _item(item_id: str, label: str, status: str, evidence: str) -> dict[str, str]:
    return {"id": item_id, "label": label, "status": status, "evidence": evidence}


def _action(action_id: str, label: str, detail: str) -> dict[str, str]:
    return {"id": action_id, "label": label, "detail": detail}
