from __future__ import annotations

from harness.context import JsonDict, RunContext


def run_material_gate(ctx: RunContext, brief: JsonDict, assets: JsonDict) -> JsonDict:
    if ctx.dry_run:
        return {"name": "material-gate", "status": "pass", "message": "Dry-run allows missing source assets."}
    if not assets.get("videos"):
        return {"name": "material-gate", "status": "fail", "message": "No video assets found."}
    if not assets.get("audio"):
        return {"name": "material-gate", "status": "fail", "message": "No audio assets found."}
    unreadable = [asset["path"] for asset in assets["videos"] + assets["audio"] if not asset.get("readable")]
    if unreadable:
        return {"name": "material-gate", "status": "fail", "message": f"Unreadable assets: {unreadable}"}
    return {"name": "material-gate", "status": "pass", "message": "Source assets are present and readable."}

