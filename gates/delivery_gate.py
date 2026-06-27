from __future__ import annotations

from pathlib import Path

from harness.context import JsonDict, RunContext


def run_delivery_gate(ctx: RunContext, brief: JsonDict, assembly: JsonDict) -> JsonDict:
    required_keys = ["render_path", "subtitle_path", "manifest_path"]
    for output in assembly.get("outputs", []):
        for key in required_keys:
            path = Path(output[key])
            if not path.exists():
                return {"name": "delivery-gate", "status": "fail", "message": f"Missing {key}: {path}"}
            if key == "render_path" and path.stat().st_size == 0:
                return {"name": "delivery-gate", "status": "fail", "message": f"Empty render file: {path}"}
    return {"name": "delivery-gate", "status": "pass", "message": "Render, subtitle, and manifest files exist."}

