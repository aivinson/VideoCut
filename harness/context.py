from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunContext:
    root: Path
    brief_path: Path
    videos_dir: Path
    audio_dir: Path
    outputs_dir: Path
    logs_dir: Path
    dry_run: bool = False

    @property
    def artifacts_dir(self) -> Path:
        return self.outputs_dir / "artifacts"

    @property
    def renders_dir(self) -> Path:
        return self.outputs_dir / "renders"

    @property
    def subtitles_dir(self) -> Path:
        return self.outputs_dir / "subtitles"

    @property
    def manifests_dir(self) -> Path:
        return self.outputs_dir / "manifests"

    def ensure_dirs(self) -> None:
        for path in [
            self.videos_dir,
            self.audio_dir,
            self.outputs_dir,
            self.logs_dir,
            self.artifacts_dir,
            self.renders_dir,
            self.subtitles_dir,
            self.manifests_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


def artifact_path(ctx: RunContext, name: str) -> Path:
    return ctx.artifacts_dir / name


JsonDict = dict[str, Any]

