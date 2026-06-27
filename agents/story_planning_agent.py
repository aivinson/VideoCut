from __future__ import annotations

from harness.context import JsonDict, RunContext, artifact_path
from harness.io import write_json


class StoryPlanningAgent:
    name = "story-planning-agent"

    def run(self, ctx: RunContext, brief: JsonDict, transcripts: JsonDict) -> JsonDict:
        target_count = int(brief.get("target_count", 2))
        topic = brief.get("topic", "short-video topic")
        duration = brief.get("duration_seconds", {})
        max_duration = int(duration.get("max", 60))

        plans = []
        for index in range(target_count):
            transcript = transcripts["transcripts"][index % len(transcripts["transcripts"])]
            plans.append(
                {
                    "id": f"short_{index + 1:02d}",
                    "topic": topic,
                    "variant_angle": self._angle(index),
                    "target_duration_seconds": min(max_duration, 30 + index * 5),
                    "opening_strategy": self._opening(index),
                    "transcript_audio_id": transcript["audio_id"],
                    "beats": [
                        {"name": "hook", "start": 0, "end": 3},
                        {"name": "proof", "start": 3, "end": 12},
                        {"name": "close", "start": 12, "end": 16},
                    ],
                }
            )

        result = {"agent": self.name, "plans": plans}
        write_json(artifact_path(ctx, "plans.json"), result)
        return result

    def _angle(self, index: int) -> str:
        angles = ["problem-solution", "before-after", "three-step-tip", "mistake-to-fix"]
        return angles[index % len(angles)]

    def _opening(self, index: int) -> str:
        openings = ["direct question", "surprising claim", "fast visual contrast", "pain point"]
        return openings[index % len(openings)]

