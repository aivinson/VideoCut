from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac"}


@dataclass(frozen=True)
class RenderEnvironment:
    hyperframes_available: bool
    ffmpeg_available: bool
    ffprobe_available: bool
    node_available: bool
    notes: list[str]

    @property
    def can_render(self) -> bool:
        return self.hyperframes_available and self.ffmpeg_available and self.ffprobe_available


def list_media(directory: Path, extensions: set[str]) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    items = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        items.append(
            {
                "name": path.name,
                "path": str(path),
                "extension": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "mb": round(path.stat().st_size / 1024 / 1024, 2),
            }
        )
    return items


def analyze_assets(root: Path, brief: dict[str, Any]) -> dict[str, Any]:
    videos = list_media(root / "inputs" / "videos", VIDEO_EXTENSIONS)
    audio = list_media(root / "inputs" / "audio", AUDIO_EXTENSIONS)
    env = inspect_render_environment()
    suggestions = build_suggestions(videos, audio, brief, env)
    return {
        "videos": videos,
        "audio": audio,
        "brief": brief,
        "environment": {
            "hyperframes_available": env.hyperframes_available,
            "ffmpeg_available": env.ffmpeg_available,
            "ffprobe_available": env.ffprobe_available,
            "node_available": env.node_available,
            "can_render": env.can_render,
            "notes": env.notes,
        },
        "suggestions": suggestions,
    }


def build_suggestions(
    videos: list[dict[str, Any]],
    audio: list[dict[str, Any]],
    brief: dict[str, Any],
    env: RenderEnvironment,
) -> list[str]:
    suggestions = []
    target_count = brief.get("target_count", 1)
    topic = brief.get("topic", "当前题材")
    if videos:
        suggestions.append(f"已导入 {len(videos)} 个视频素材，可先剪 1 条围绕“{topic}”的竖屏草稿。")
    else:
        suggestions.append("还没有视频素材。请先导入视频文件，才能生成完整成片。")
    if audio:
        suggestions.append(f"已导入 {len(audio)} 个音频素材，可作为旁白或主音轨。")
    else:
        suggestions.append("还没有音频素材。本轮会优先使用视频画面和字幕卡，后续可补旁白。")
    if target_count > 1:
        suggestions.append(f"目标数量是 {target_count} 条，建议先生成第 1 条样片，确认风格后再批量扩展。")
    suggestions.append("建议结构：开场钩子 3 秒，主体展示 8-20 秒，结尾总结或行动号召 3 秒。")
    if not env.can_render:
        suggestions.append("当前缺少 FFmpeg/FFprobe，HyperFrames 工程可以生成，但最终 MP4 渲染会被门禁拦截。")
    return suggestions


def inspect_render_environment() -> RenderEnvironment:
    ffmpeg = shutil.which("ffmpeg") is not None
    ffprobe = shutil.which("ffprobe") is not None
    node = shutil.which("node") is not None or Path("/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node").exists()
    pnpm = Path("/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm")
    hyperframes = pnpm.exists()
    notes = []
    if not ffmpeg:
        notes.append("缺少 FFmpeg：无法编码最终 MP4。")
    if not ffprobe:
        notes.append("缺少 FFprobe：无法读取真实媒体时长和编码信息。")
    if not hyperframes:
        notes.append("缺少 HyperFrames CLI 入口：无法调用 HyperFrames render。")
    return RenderEnvironment(
        hyperframes_available=hyperframes,
        ffmpeg_available=ffmpeg,
        ffprobe_available=ffprobe,
        node_available=node,
        notes=notes,
    )


def create_hyperframes_project(root: Path, brief: dict[str, Any], requirements: str) -> dict[str, Any]:
    analysis = analyze_assets(root, brief)
    project_slug = safe_slug(brief.get("project") or "videocut")
    project_dir = root / "outputs" / "hyperframes" / project_slug
    media_dir = project_dir / "media"
    project_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)

    copied_videos = copy_media(analysis["videos"], media_dir)
    copied_audio = copy_media(analysis["audio"], media_dir)
    design_path = project_dir / "DESIGN.md"
    index_path = project_dir / "index.html"
    manifest_path = project_dir / "videocut_manifest.json"

    design_path.write_text(build_design_doc(brief), encoding="utf-8")
    index_path.write_text(build_hyperframes_html(brief, requirements, copied_videos, copied_audio), encoding="utf-8")
    manifest = {
        "project": brief.get("project"),
        "topic": brief.get("topic"),
        "requirements": requirements,
        "project_dir": str(project_dir),
        "index_html": str(index_path),
        "design": str(design_path),
        "videos": copied_videos,
        "audio": copied_audio,
        "analysis": analysis,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def copy_media(items: list[dict[str, Any]], media_dir: Path) -> list[dict[str, Any]]:
    copied = []
    for item in items:
        source = Path(item["path"])
        target = unique_destination(media_dir, source.name)
        shutil.copy2(source, target)
        copied.append({**item, "project_path": str(target), "relative_path": f"media/{target.name}"})
    return copied


def build_design_doc(brief: dict[str, Any]) -> str:
    return f"""# VideoCut HyperFrames Design

## Style Prompt

Clean editorial vertical short-video control style for {brief.get("platform", "short video")} drafts. The composition should feel practical, modern, and readable, with strong captions and restrained motion.

## Colors

- Canvas: #F3F6FB
- Ink: #172033
- Accent: #2563EB
- Soft panel: #FFFFFF
- Success: #14804A

## Typography

- Font family: sans-serif

## What NOT to Do

- Do not use one-note purple gradients.
- Do not place text outside the 9:16 safe area.
- Do not use tiny captions.
- Do not rely on decorative backgrounds instead of the provided素材.
"""


def build_hyperframes_html(
    brief: dict[str, Any],
    requirements: str,
    videos: list[dict[str, Any]],
    audio: list[dict[str, Any]],
) -> str:
    width = int(brief.get("resolution", {}).get("width", 1080))
    height = int(brief.get("resolution", {}).get("height", 1920))
    target_duration = min(int(brief.get("duration_seconds", {}).get("max", 30)), max(12, len(videos) * 5 or 12))
    scene_duration = max(4, target_duration // max(1, min(len(videos), 4)))
    video_tags = []
    for index, video in enumerate(videos[:4]):
        start = index * scene_duration
        video_tags.append(
            f'<video id="video-{index + 1}" class="source-video" data-start="{start}" data-duration="{scene_duration}" data-track-index="0" src="{video["relative_path"]}" muted playsinline></video>'
        )
    audio_tag = ""
    if audio:
        audio_tag = f'<audio id="main-audio" data-start="0" data-duration="{target_duration}" data-track-index="3" src="{audio[0]["relative_path"]}" data-volume="1"></audio>'
    fallback = ""
    if not videos:
        fallback = '<div id="fallback-card" class="fallback" data-start="0" data-duration="12" data-track-index="0">请先导入视频素材</div>'

    escaped_topic = html_escape(str(brief.get("topic", "VideoCut 成片")))
    escaped_requirements = html_escape(requirements or "根据素材生成一条清晰、节奏稳定的短视频。")
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>VideoCut HyperFrames Composition</title>
    <style>
      body {{ margin: 0; background: #f3f6fb; }}
      #videocut-main {{
        width: {width}px;
        height: {height}px;
        overflow: hidden;
        background: #f3f6fb;
        color: #172033;
        font-family: sans-serif;
        position: relative;
      }}
      .source-video {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }}
      .caption-panel {{
        position: absolute;
        left: 56px;
        right: 56px;
        bottom: 96px;
        z-index: 5;
        border-radius: 8px;
        padding: 28px 32px;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 0 14px 40px rgba(23, 32, 51, 0.20);
      }}
      .caption-panel h1 {{
        margin: 0 0 12px;
        font-size: 54px;
        line-height: 1.08;
        letter-spacing: 0;
      }}
      .caption-panel p {{
        margin: 0;
        color: #39465c;
        font-size: 26px;
        line-height: 1.36;
      }}
      .fallback {{
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 80px;
        text-align: center;
        font-size: 56px;
      }}
    </style>
  </head>
  <body>
    <div id="videocut-main" data-composition-id="videocut-main" data-start="0" data-width="{width}" data-height="{height}">
      {"".join(video_tags)}
      {audio_tag}
      {fallback}
      <div id="caption" class="clip caption-panel" data-start="0" data-duration="{target_duration}" data-track-index="2">
        <h1>{escaped_topic}</h1>
        <p>{escaped_requirements}</p>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.from("#caption", {{ y: 80, opacity: 0, duration: 0.7, ease: "power3.out" }}, 0.2);
      tl.to("#caption", {{ opacity: 0, duration: 0.5, ease: "power2.in" }}, {max(1, target_duration - 0.7)});
      window.__timelines["videocut-main"] = tl;
    </script>
  </body>
</html>
"""


def render_hyperframes(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    env = inspect_render_environment()
    output = root / "outputs" / "renders" / "hyperframes_final.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    if not env.can_render:
        return {
            "status": "blocked",
            "output": str(output),
            "message": "HyperFrames 工程已生成，但缺少 FFmpeg/FFprobe，无法渲染最终 MP4。",
            "environment": env.__dict__,
        }

    pnpm = "/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm"
    command = [pnpm, "dlx", "hyperframes", "render", "--output", str(output), "--quality", "draft"]
    completed = subprocess.run(
        command,
        cwd=manifest["project_dir"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=600,
        check=False,
    )
    return {
        "status": "complete" if completed.returncode == 0 else "failed",
        "output": str(output),
        "returncode": completed.returncode,
        "log": completed.stdout[-4000:],
    }


def safe_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return slug or "videocut"


def unique_destination(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        candidate = directory / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
