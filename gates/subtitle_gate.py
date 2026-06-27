from __future__ import annotations

from pathlib import Path

from harness.context import JsonDict, RunContext


def run_subtitle_gate(ctx: RunContext, brief: JsonDict, assembly: JsonDict) -> JsonDict:
    for output in assembly.get("outputs", []):
        subtitle_path = Path(output["subtitle_path"])
        if not subtitle_path.exists():
            return {"name": "subtitle-gate", "status": "fail", "message": f"Missing subtitle file: {subtitle_path}"}
        for line in subtitle_path.read_text(encoding="utf-8").splitlines():
            if "-->" not in line and len(line) > 42:
                return {"name": "subtitle-gate", "status": "fail", "message": f"Subtitle line too long in {subtitle_path}."}
    return {"name": "subtitle-gate", "status": "pass", "message": "Subtitle files exist and line lengths are within the first safe limit."}

