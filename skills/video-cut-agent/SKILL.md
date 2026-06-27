---
name: video-cut-agent
description: Use when turning batches of video and voice assets into multiple same-topic short videos through a reusable Skill + Gates + Multi-Agent Harness workflow. Supports asset ingestion, transcription, story planning, clip selection, rough assembly, quality gates, and learning retrospectives.
---

# Video Cut Agent

Use this skill for repeatable short-video production from a folder of video
assets, audio/voice assets, and a brief. The system favors a harness-led,
multi-agent workflow where each agent owns one module and communicates through
JSON artifacts.

## Workflow

1. Read the task brief and platform target.
2. Run `asset-ingest-agent` to scan videos and audio.
3. Run `transcript-agent` to create transcripts, subtitle seeds, and keywords.
4. Run `story-planning-agent` to create multiple same-topic short structures.
5. Run `clip-selection-agent` to assign source material to each planned short.
6. Run `edit-assembly-agent` to create rough cuts, subtitles, and manifests.
7. Run `quality-gate-agent` before delivery.
8. Run `learning-agent` to produce a retrospective and Skill/Gate candidates.

## Required references

- Read `references/agent-contracts.md` before changing agent boundaries.
- Read `references/platforms.md` before implementing platform-specific output.
- Read `references/editing-principles.md` before changing planning or assembly.
- Read `references/failure-patterns.md` before adding or changing gates.

## Directory contract

- `inputs/videos/`: source video files.
- `inputs/audio/`: voice, narration, or music files.
- `inputs/brief.example.json`: editable brief template.
- `outputs/`: renders, manifests, subtitles, and gate reports.
- `logs/`: run logs and retrospectives.
- `agents/`: single-responsibility agent implementations.
- `gates/`: reusable automated gate checks.
- `harness/`: workflow orchestration.

## Operating rules

- Keep reusable knowledge in this skill or its references.
- Promote repeated failures to `references/failure-patterns.md`.
- Promote automatically detectable repeated failures to gate scripts.
- Let only the harness own cross-agent run state.
- Agents must write module-scoped artifacts and return structured results.
- Human review remains required until quality gates prove reliable for a topic.

