from __future__ import annotations

from harness.context import JsonDict, RunContext


def run_transcript_gate(ctx: RunContext, brief: JsonDict, transcripts: JsonDict) -> JsonDict:
    for transcript in transcripts.get("transcripts", []):
        if not transcript.get("segments"):
            return {"name": "transcript-gate", "status": "fail", "message": f"Missing segments for {transcript.get('audio_id')}."}
        for segment in transcript["segments"]:
            if segment["end"] <= segment["start"]:
                return {"name": "transcript-gate", "status": "fail", "message": "Subtitle segment timestamp is invalid."}
    return {"name": "transcript-gate", "status": "pass", "message": "Transcripts and timestamps are usable."}

