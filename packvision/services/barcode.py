from __future__ import annotations

from typing import Any

try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]


def detect_codes(image_bytes: bytes) -> dict[str, Any]:
    if cv2 is None or np is None:
        return {"codes": [], "engines": [], "error": "OpenCV is unavailable."}

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        return {"codes": [], "engines": [], "error": "Unable to decode image."}

    codes: list[dict[str, Any]] = []
    engines: list[str] = []

    qr = cv2.QRCodeDetector()
    try:
        ok, decoded_info, points, _ = qr.detectAndDecodeMulti(image)
        engines.append("opencv_qrcode")
        if ok:
            for index, text in enumerate(decoded_info):
                if text:
                    codes.append(
                        {
                            "text": text,
                            "type": "QR",
                            "engine": "opencv_qrcode",
                            "points": _points(points[index]) if points is not None else None,
                        }
                    )
    except Exception as exc:  # pragma: no cover - OpenCV variants differ.
        engines.append(f"opencv_qrcode_error:{exc}")

    if hasattr(cv2, "barcode"):
        try:
            detector = cv2.barcode.BarcodeDetector()
            result = detector.detectAndDecode(image)
            engines.append("opencv_barcode")
            texts, types, points = _parse_barcode_result(result)
            for text, code_type, point_set in zip(texts, types, points):
                if text:
                    codes.append(
                        {
                            "text": text,
                            "type": code_type or "BARCODE",
                            "engine": "opencv_barcode",
                            "points": _points(point_set),
                        }
                    )
        except Exception as exc:  # pragma: no cover - OpenCV variants differ.
            engines.append(f"opencv_barcode_error:{exc}")

    unique = []
    seen = set()
    for code in codes:
        key = (code["text"], code["type"])
        if key not in seen:
            unique.append(code)
            seen.add(key)
    return {"codes": unique, "engines": engines}


def _parse_barcode_result(result: Any) -> tuple[list[str], list[str], list[Any]]:
    if not isinstance(result, tuple):
        return [], [], []
    if len(result) == 4:
        ok, decoded_info, decoded_type, points = result
        if not ok:
            return [], [], []
        return list(decoded_info or []), list(decoded_type or []), list(points or [])
    if len(result) == 3:
        decoded_info, decoded_type, points = result
        if isinstance(decoded_info, str):
            return [decoded_info], [decoded_type or ""], [points]
        return list(decoded_info or []), list(decoded_type or []), list(points or [])
    return [], [], []


def _points(points: Any) -> list[list[float]] | None:
    if points is None:
        return None
    arr = np.array(points, dtype=float).reshape(-1, 2)
    return arr.round(2).tolist()
