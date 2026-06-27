from __future__ import annotations

from harness.context import JsonDict, RunContext


def run_diversity_gate(ctx: RunContext, brief: JsonDict, selections: JsonDict) -> JsonDict:
    if not brief.get("constraints", {}).get("avoid_repeated_opening", True):
        return {"name": "diversity-gate", "status": "pass", "message": "Opening diversity disabled by brief."}
    openings = [selection["opening_source_id"] for selection in selections.get("selections", [])]
    if len(openings) > 1 and len(set(openings)) == 1 and not ctx.dry_run:
        return {"name": "diversity-gate", "status": "fail", "message": "All variants use the same opening source."}
    return {"name": "diversity-gate", "status": "pass", "message": "Variant openings are acceptable for this run."}

