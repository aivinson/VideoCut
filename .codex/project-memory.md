# Project Memory

## Repository

- GitHub remote: `https://github.com/aivinson/VideoCut.git`
- This workspace is the long-lived home for the VideoCut agent system.

## Product Direction

- Build a reusable short-video production agent system, not a one-off editing script.
- Use a Skill + Gates + Multi-Agent Harness architecture.
- Stable knowledge belongs in `skills/video-cut-agent/`.
- Repeated failures belong in `skills/video-cut-agent/references/failure-patterns.md`.
- Automatically detectable repeated failures should become gate checks in `gates/`.
- Agents should own one module each and exchange structured JSON artifacts through the harness.
- The harness owns cross-agent state, logs, manifests, quality gates, and retrospectives.

## Current Defaults

- Default workflow mode: semi-automatic batch editing with human review.
- Default platform shape: vertical short video, `1080x1920`, `9:16`.
- Default MVP mode: dry-run capable before Whisper, FFmpeg, Auto-Editor, or MoviePy are installed.
- Generated outputs and local media inputs should not be committed unless explicitly requested.

