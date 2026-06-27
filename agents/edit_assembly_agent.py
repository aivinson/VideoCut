from __future__ import annotations

from pathlib import Path

from harness.context import JsonDict, RunContext, artifact_path
from harness.io import write_json, write_text


class EditAssemblyAgent:
    name = "edit-assembly-agent"

    def run(self, ctx: RunContext, brief: JsonDict, selections: JsonDict, transcripts: JsonDict) -> JsonDict:
        outputs = []
        resolution = brief.get("resolution", {"width": 1080, "height": 1920})

        for selection in selections["selections"]:
            plan_id = selection["plan_id"]
            render_path = ctx.renders_dir / f"{plan_id}.mp4"
            subtitle_path = ctx.subtitles_dir / f"{plan_id}.srt"
            manifest_path = ctx.manifests_dir / f"{plan_id}.json"

            transcript = self._matching_transcript(transcripts, selection)
            self._write_srt(subtitle_path, transcript["segments"])
            self._write_placeholder_render(render_path, plan_id, brief, selection)

            manifest = {
                "id": plan_id,
                "render_path": str(render_path),
                "subtitle_path": str(subtitle_path),
                "resolution": resolution,
                "aspect_ratio": brief.get("aspect_ratio", "9:16"),
                "duration_seconds": max(clip["timeline_end"] for clip in selection["clips"]),
                "opening_source_id": selection["opening_source_id"],
                "clips": selection["clips"],
                "dry_run": ctx.dry_run,
            }
            write_json(manifest_path, manifest)
            outputs.append({**manifest, "manifest_path": str(manifest_path)})

        result = {
            "agent": self.name,
            "adapter": "placeholder-render-adapter",
            "outputs": outputs,
            "warnings": ["Render files are placeholder MP4-named artifacts until FFmpeg assembly is enabled."],
        }
        write_json(artifact_path(ctx, "assembly.json"), result)
        return result

    def _matching_transcript(self, transcripts: JsonDict, selection: JsonDict) -> JsonDict:
        return transcripts["transcripts"][0]

    def _write_srt(self, path: Path, segments: list[JsonDict]) -> None:
        lines = []
        for index, segment in enumerate(segments, start=1):
            lines.extend(
                [
                    str(index),
                    f"{self._srt_time(segment['start'])} --> {self._srt_time(segment['end'])}",
                    segment["text"],
                    "",
                ]
            )
        write_text(path, "\n".join(lines))

    def _write_placeholder_render(self, path: Path, plan_id: str, brief: JsonDict, selection: JsonDict) -> None:
        content = {
            "placeholder": True,
            "plan_id": plan_id,
            "topic": brief.get("topic"),
            "selection": selection,
        }
        write_json(path, content)

    def _srt_time(self, seconds: float) -> str:
        millis = int(round(seconds * 1000))
        hours, remainder = divmod(millis, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        secs, ms = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

