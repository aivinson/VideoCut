from __future__ import annotations

from gates.delivery_gate import run_delivery_gate
from gates.diversity_gate import run_diversity_gate
from gates.material_gate import run_material_gate
from gates.subtitle_gate import run_subtitle_gate
from gates.transcript_gate import run_transcript_gate
from gates.visual_gate import run_visual_gate
from harness.context import JsonDict, RunContext, artifact_path
from harness.io import write_json


class QualityGateAgent:
    name = "quality-gate-agent"

    def run(
        self,
        ctx: RunContext,
        brief: JsonDict,
        assets: JsonDict,
        transcripts: JsonDict,
        plans: JsonDict,
        selections: JsonDict,
        assembly: JsonDict,
    ) -> JsonDict:
        checks = [
            run_material_gate(ctx, brief, assets),
            run_transcript_gate(ctx, brief, transcripts),
            run_visual_gate(ctx, brief, assembly),
            run_subtitle_gate(ctx, brief, assembly),
            run_diversity_gate(ctx, brief, selections),
            run_delivery_gate(ctx, brief, assembly),
        ]
        status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
        result = {"agent": self.name, "status": status, "checks": checks}
        write_json(artifact_path(ctx, "gate-report.json"), result)
        return result

