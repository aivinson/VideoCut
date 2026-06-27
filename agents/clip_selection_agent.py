from __future__ import annotations

from harness.context import JsonDict, RunContext, artifact_path
from harness.io import write_json


class ClipSelectionAgent:
    name = "clip-selection-agent"

    def run(self, ctx: RunContext, brief: JsonDict, assets: JsonDict, plans: JsonDict) -> JsonDict:
        videos = assets.get("videos") or [self._placeholder_video()]
        selections = []

        for index, plan in enumerate(plans["plans"]):
            opening_video = videos[index % len(videos)]
            supporting_video = videos[(index + 1) % len(videos)]
            selections.append(
                {
                    "plan_id": plan["id"],
                    "opening_source_id": opening_video["id"],
                    "clips": [
                        self._clip(opening_video, "hook", 0.0, 3.0),
                        self._clip(supporting_video, "proof", 3.0, 12.0),
                        self._clip(opening_video, "close", 12.0, 16.0),
                    ],
                }
            )

        result = {"agent": self.name, "selections": selections}
        write_json(artifact_path(ctx, "selections.json"), result)
        return result

    def _placeholder_video(self) -> JsonDict:
        return {
            "id": "placeholder_visual",
            "path": "",
            "probe": {"width": 1080, "height": 1920, "duration_seconds": 16},
        }

    def _clip(self, video: JsonDict, beat: str, start: float, end: float) -> JsonDict:
        return {
            "source_id": video["id"],
            "source_path": video.get("path", ""),
            "beat": beat,
            "timeline_start": start,
            "timeline_end": end,
            "source_start": 0.0,
            "source_end": end - start,
        }

