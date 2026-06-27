# Agent Contracts

All agents receive a `RunContext` from the harness and return a JSON-serializable
dictionary. Agents must not mutate another agent's artifact directly.

## asset-ingest-agent

- Input: video folder, audio folder, brief.
- Output: `assets.json` with video/audio records and probe metadata.
- Owns: file discovery, readability checks, extension classification.

## transcript-agent

- Input: audio records.
- Output: `transcripts.json` and `.srt` seeds.
- Owns: voice transcription, keyword extraction, segment timestamps.

## story-planning-agent

- Input: brief, transcripts.
- Output: `plans.json`.
- Owns: hook, structure, target duration, topic consistency, variant intent.

## clip-selection-agent

- Input: plans, asset records.
- Output: `selections.json`.
- Owns: source clip assignment, reuse limits, rough timing.

## edit-assembly-agent

- Input: selections, transcripts, brief.
- Output: render files, subtitle files, per-short manifest files.
- Owns: FFmpeg/MoviePy/Auto-Editor integration and export settings.

## quality-gate-agent

- Input: manifests and all previous artifacts.
- Output: `gate-report.json`.
- Owns: pass/fail checks and actionable failure reasons.

## learning-agent

- Input: run summary, gate report, optional human feedback.
- Output: `retrospective.md`.
- Owns: learning notes, Skill candidates, Gate candidates.

