from __future__ import annotations

from harness.context import JsonDict, RunContext, artifact_path
from harness.io import write_json


class TranscriptAgent:
    name = "transcript-agent"

    def run(self, ctx: RunContext, brief: JsonDict, assets: JsonDict) -> JsonDict:
        audio_records = assets.get("audio", [])
        if not audio_records:
            audio_records = [{"id": "placeholder_voice", "path": "", "bytes": 0}]

        transcripts = [self._placeholder_transcript(record, index) for index, record in enumerate(audio_records)]
        result = {
            "agent": self.name,
            "engine": "placeholder-whisper-adapter",
            "transcripts": transcripts,
            "warnings": ["Whisper integration is adapter-ready; current run used deterministic placeholder text."],
        }
        write_json(artifact_path(ctx, "transcripts.json"), result)
        return result

    def _placeholder_transcript(self, audio: JsonDict, index: int) -> JsonDict:
        topic_words = audio.get("id") or f"voice_{index + 1}"
        text = f"Hook for {topic_words}. Main point with clear evidence. Closing call to action."
        return {
            "audio_id": audio.get("id", f"audio_{index + 1}"),
            "audio_path": audio.get("path", ""),
            "language": "auto",
            "keywords": [part for part in topic_words.replace("-", "_").split("_") if part],
            "segments": [
                {"start": 0.0, "end": 3.0, "text": f"Hook for {topic_words}."},
                {"start": 3.0, "end": 12.0, "text": "Main point with clear evidence."},
                {"start": 12.0, "end": 16.0, "text": "Closing call to action."},
            ],
            "text": text,
        }

