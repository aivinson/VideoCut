from __future__ import annotations

from pathlib import Path

from harness.context import JsonDict, RunContext, artifact_path
from harness.io import write_json


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac"}


class AssetIngestAgent:
    name = "asset-ingest-agent"

    def run(self, ctx: RunContext, brief: JsonDict) -> JsonDict:
        videos = [self._record(path, "video") for path in sorted(ctx.videos_dir.glob("*")) if path.suffix.lower() in VIDEO_EXTENSIONS]
        audio = [self._record(path, "audio") for path in sorted(ctx.audio_dir.glob("*")) if path.suffix.lower() in AUDIO_EXTENSIONS]

        result = {
            "agent": self.name,
            "videos": videos,
            "audio": audio,
            "counts": {"videos": len(videos), "audio": len(audio)},
            "warnings": self._warnings(videos, audio, ctx.dry_run),
        }
        write_json(artifact_path(ctx, "assets.json"), result)
        return result

    def _record(self, path: Path, kind: str) -> JsonDict:
        stat = path.stat()
        return {
            "id": path.stem,
            "kind": kind,
            "path": str(path),
            "extension": path.suffix.lower(),
            "bytes": stat.st_size,
            "readable": path.is_file() and stat.st_size >= 0,
            "probe": {
                "duration_seconds": None,
                "width": None,
                "height": None,
                "codec": None,
                "source": "filesystem",
            },
        }

    def _warnings(self, videos: list[JsonDict], audio: list[JsonDict], dry_run: bool) -> list[str]:
        warnings = []
        if not videos:
            warnings.append("No video assets found; dry-run placeholder renders will be used.")
        if not audio:
            warnings.append("No audio assets found; filename-based placeholder transcripts will be used.")
        if not dry_run and (not videos or not audio):
            warnings.append("Run is not dry-run, but required assets are missing.")
        return warnings

