from __future__ import annotations

from datetime import datetime, timezone

from harness.context import JsonDict, RunContext
from harness.io import write_text


class LearningAgent:
    name = "learning-agent"

    def run(self, ctx: RunContext, brief: JsonDict, gates: JsonDict) -> JsonDict:
        failed = [check for check in gates["checks"] if check["status"] != "pass"]
        skill_candidates = []
        gate_candidates = []

        if failed:
            gate_candidates.extend(check["name"] for check in failed)
        if brief.get("style"):
            skill_candidates.append("Codify recurring style preferences from the brief after human review.")

        lines = [
            "# Retrospective",
            "",
            f"- Run time: {datetime.now(timezone.utc).isoformat()}",
            f"- Topic: {brief.get('topic', 'unknown')}",
            f"- Gate status: {gates['status']}",
            "",
            "## Failed checks",
            "",
        ]
        lines.extend([f"- {check['name']}: {check['message']}" for check in failed] or ["- None"])
        lines.extend(["", "## Skill candidates", ""])
        lines.extend([f"- {item}" for item in skill_candidates] or ["- None"])
        lines.extend(["", "## Gate candidates", ""])
        lines.extend([f"- {item}" for item in gate_candidates] or ["- None"])

        path = ctx.logs_dir / "retrospective.md"
        write_text(path, "\n".join(lines) + "\n")
        return {"agent": self.name, "path": str(path)}

