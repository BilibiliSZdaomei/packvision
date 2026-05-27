from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packvision.services.depth_simulation import simulate_astra_depth_measurement_from_image
from packvision.services.storage import app_data_dir


DEFAULT_SAMPLE_URL = "https://clubs.github.io/gif/box_000.gif"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download a real RGB sample image and run PackVision Astra-depth dry-run measurement."
    )
    parser.add_argument("--url", default=DEFAULT_SAMPLE_URL)
    parser.add_argument("--name", default="clubs_box_000")
    parser.add_argument("--frame-index", type=int, default=3)
    parser.add_argument("--table-depth-mm", type=float, default=1200.0)
    parser.add_argument("--object-depth-mm", type=float, default=850.0)
    parser.add_argument("--roi-json", default=None, help="Optional [x1,y1,x2,y2] ROI after resizing.")
    args = parser.parse_args()

    output_dir = app_data_dir() / "simulation_samples" / args.name
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / _filename_from_url(args.url)
    if not raw_path.exists():
        print(f"Downloading sample: {args.url}")
        urllib.request.urlretrieve(args.url, raw_path)

    roi = json.loads(args.roi_json) if args.roi_json else None
    simulated = simulate_astra_depth_measurement_from_image(
        raw_path.read_bytes(),
        filename=raw_path.name,
        source_url=args.url,
        roi=roi,
        table_depth_mm=args.table_depth_mm,
        object_depth_mm=args.object_depth_mm,
        frame_index=args.frame_index,
    )

    source_path = output_dir / f"{args.name}_source_frame.png"
    overlay_path = output_dir / f"{args.name}_overlay.png"
    depth_preview_path = output_dir / f"{args.name}_depth_preview.png"
    result_path = output_dir / f"{args.name}_measurement.json"
    source_path.write_bytes(simulated.artifacts.source_png)
    overlay_path.write_bytes(simulated.artifacts.overlay_png)
    depth_preview_path.write_bytes(simulated.artifacts.depth_preview_png)

    result = dict(simulated.result)
    result["local_artifacts"] = {
        "raw_download": str(raw_path),
        "source_frame": str(source_path),
        "overlay": str(overlay_path),
        "depth_preview": str(depth_preview_path),
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    dimensions = result["dimensions"]
    print("PackVision Astra dry-run measurement complete.")
    print(f"Result JSON: {result_path}")
    print(f"Overlay: {overlay_path}")
    print(
        "Dimensions: "
        f"L={dimensions['length_mm']} mm, "
        f"W={dimensions['width_mm']} mm, "
        f"H={dimensions['height_mm']} mm"
    )
    print(f"Simulation flags: {', '.join(result['simulation']['quality_flags'])}")
    return 0


def _filename_from_url(url: str) -> str:
    name = url.rstrip("/").split("/")[-1] or "sample_image"
    if "." not in name:
        name += ".img"
    return name


if __name__ == "__main__":
    raise SystemExit(main())
