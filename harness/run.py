from __future__ import annotations

import argparse
from pathlib import Path

from agents.asset_ingest_agent import AssetIngestAgent
from agents.clip_selection_agent import ClipSelectionAgent
from agents.edit_assembly_agent import EditAssemblyAgent
from agents.learning_agent import LearningAgent
from agents.quality_gate_agent import QualityGateAgent
from agents.story_planning_agent import StoryPlanningAgent
from agents.transcript_agent import TranscriptAgent
from harness.context import RunContext, artifact_path
from harness.io import read_json, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the VideoCut multi-agent harness.")
    parser.add_argument("--brief", default="inputs/brief.example.json")
    parser.add_argument("--videos", default="inputs/videos")
    parser.add_argument("--audio", default="inputs/audio")
    parser.add_argument("--outputs", default="outputs")
    parser.add_argument("--logs", default="logs")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def run(ctx: RunContext) -> dict:
    ctx.ensure_dirs()
    brief = read_json(ctx.brief_path)

    assets = AssetIngestAgent().run(ctx, brief)
    transcripts = TranscriptAgent().run(ctx, brief, assets)
    plans = StoryPlanningAgent().run(ctx, brief, transcripts)
    selections = ClipSelectionAgent().run(ctx, brief, assets, plans)
    assembly = EditAssemblyAgent().run(ctx, brief, selections, transcripts)
    gates = QualityGateAgent().run(ctx, brief, assets, transcripts, plans, selections, assembly)
    retrospective = LearningAgent().run(ctx, brief, gates)

    run_summary = {
        "brief": str(ctx.brief_path),
        "dry_run": ctx.dry_run,
        "artifacts": {
            "assets": str(artifact_path(ctx, "assets.json")),
            "transcripts": str(artifact_path(ctx, "transcripts.json")),
            "plans": str(artifact_path(ctx, "plans.json")),
            "selections": str(artifact_path(ctx, "selections.json")),
            "assembly": str(artifact_path(ctx, "assembly.json")),
            "gates": str(artifact_path(ctx, "gate-report.json")),
            "retrospective": str(retrospective["path"]),
        },
        "gate_status": gates["status"],
    }
    write_json(artifact_path(ctx, "run-summary.json"), run_summary)
    return run_summary


def main() -> None:
    args = build_parser().parse_args()
    root = Path.cwd()
    ctx = RunContext(
        root=root,
        brief_path=(root / args.brief).resolve(),
        videos_dir=(root / args.videos).resolve(),
        audio_dir=(root / args.audio).resolve(),
        outputs_dir=(root / args.outputs).resolve(),
        logs_dir=(root / args.logs).resolve(),
        dry_run=args.dry_run,
    )
    summary = run(ctx)
    print(f"VideoCut run complete: gates={summary['gate_status']}")
    print(f"Summary: {summary['artifacts']['gates']}")


if __name__ == "__main__":
    main()

