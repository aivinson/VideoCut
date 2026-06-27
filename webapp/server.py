from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from harness.context import RunContext
from harness.io import read_json, write_json
from harness.run import run


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "webapp" / "static"


class VideoCutHandler(SimpleHTTPRequestHandler):
    server_version = "VideoCutWeb/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.path = "/index.html"
            return super().do_GET()
        if parsed.path == "/api/status":
            return self._send_json(self._status_payload())
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            return self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

        try:
            payload = self._read_json_body()
            brief = build_brief(payload)
            brief_path = ROOT / "inputs" / "brief.web.json"
            write_json(brief_path, brief)

            ctx = RunContext(
                root=ROOT,
                brief_path=brief_path,
                videos_dir=resolve_user_path(payload.get("videos_dir"), ROOT / "inputs" / "videos"),
                audio_dir=resolve_user_path(payload.get("audio_dir"), ROOT / "inputs" / "audio"),
                outputs_dir=resolve_user_path(payload.get("outputs_dir"), ROOT / "outputs"),
                logs_dir=resolve_user_path(payload.get("logs_dir"), ROOT / "logs"),
                dry_run=bool(payload.get("dry_run", True)),
            )
            summary = run(ctx)
            result = {
                "ok": True,
                "summary": summary,
                "gates": read_json(Path(summary["artifacts"]["gates"])),
                "brief_path": str(brief_path),
            }
            self._send_json(result)
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body or "{}")

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _status_payload(self) -> dict:
        return {
            "root": str(ROOT),
            "default_videos_dir": str(ROOT / "inputs" / "videos"),
            "default_audio_dir": str(ROOT / "inputs" / "audio"),
            "default_outputs_dir": str(ROOT / "outputs"),
            "default_logs_dir": str(ROOT / "logs"),
            "last_summary_exists": (ROOT / "outputs" / "artifacts" / "run-summary.json").exists(),
        }


def resolve_user_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def build_brief(payload: dict) -> dict:
    target_count = int(payload.get("target_count") or 2)
    min_duration = int(payload.get("duration_min") or 15)
    max_duration = int(payload.get("duration_max") or 60)
    width = int(payload.get("width") or 1080)
    height = int(payload.get("height") or 1920)
    topic = str(payload.get("topic") or "short-video topic").strip()

    if target_count < 1:
        raise ValueError("target_count must be at least 1")
    if min_duration < 1 or max_duration < min_duration:
        raise ValueError("duration range is invalid")
    if width < 1 or height < 1:
        raise ValueError("resolution is invalid")
    if not topic:
        raise ValueError("topic is required")

    return {
        "project": str(payload.get("project") or "web-run").strip() or "web-run",
        "topic": topic,
        "platform": str(payload.get("platform") or "douyin"),
        "target_count": target_count,
        "duration_seconds": {"min": min_duration, "max": max_duration},
        "aspect_ratio": str(payload.get("aspect_ratio") or "9:16"),
        "resolution": {"width": width, "height": height},
        "style": {
            "pace": str(payload.get("pace") or "fast"),
            "subtitle": str(payload.get("subtitle_style") or "large safe-area captions"),
            "opening": str(payload.get("opening") or "strong hook in first 3 seconds"),
        },
        "constraints": {
            "avoid_repeated_opening": bool(payload.get("avoid_repeated_opening", True)),
            "human_review_required": bool(payload.get("human_review_required", True)),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start the VideoCut local web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    server = ThreadingHTTPServer((args.host, args.port), VideoCutHandler)
    print(f"VideoCut web UI: http://{args.host}:{args.port}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
