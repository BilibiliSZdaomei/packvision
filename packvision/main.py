from __future__ import annotations

import argparse
import multiprocessing
import socket
import threading
import time
import traceback
import webbrowser

import uvicorn

from packvision.services.storage import app_data_dir


def main() -> None:
    multiprocessing.freeze_support()
    try:
        _run()
    except Exception:
        _log(traceback.format_exc())
        raise


def _run() -> None:
    parser = argparse.ArgumentParser(description="PackVision Local desktop launcher")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    _log("PackVision startup requested.")
    port = _available_port(args.host, args.port)
    url = f"http://{args.host}:{port}"
    _log(f"Selected local URL: {url}")
    _log("Loading application.")
    from packvision.app import create_app

    app = create_app()
    _log("Application loaded.")
    config = uvicorn.Config(
        app,
        host=args.host,
        port=port,
        log_level="warning",
        access_log=False,
        log_config=None,
    )
    server = uvicorn.Server(config)

    if not args.no_browser:
        threading.Thread(target=_open_when_ready, args=(url,), daemon=True).start()

    _log(f"Starting server at {url}")
    print(f"PackVision Local is running at {url}")
    server.run()


def _available_port(host: str, preferred: int) -> int:
    for port in range(preferred, preferred + 40):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError("No available local port found.")


def _open_when_ready(url: str) -> None:
    time.sleep(1.0)
    webbrowser.open(url)


def _log(message: str) -> None:
    path = app_data_dir() / "PackVision.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


if __name__ == "__main__":
    main()
