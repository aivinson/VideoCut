from __future__ import annotations

from harness.context import JsonDict, RunContext


def run_visual_gate(ctx: RunContext, brief: JsonDict, assembly: JsonDict) -> JsonDict:
    expected = brief.get("resolution", {"width": 1080, "height": 1920})
    for output in assembly.get("outputs", []):
        actual = output.get("resolution", {})
        if actual.get("width") != expected.get("width") or actual.get("height") != expected.get("height"):
            return {
                "name": "visual-gate",
                "status": "fail",
                "message": f"{output.get('id')} resolution {actual} does not match {expected}.",
            }
    return {"name": "visual-gate", "status": "pass", "message": "Output resolution matches brief."}

