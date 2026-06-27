from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gates.transcript_gate import run_transcript_gate
from gates.visual_gate import run_visual_gate
from harness.context import RunContext


class GateTest(unittest.TestCase):
    def _ctx(self, root: Path, dry_run: bool = False) -> RunContext:
        return RunContext(
            root=root,
            brief_path=root / "brief.json",
            videos_dir=root / "videos",
            audio_dir=root / "audio",
            outputs_dir=root / "outputs",
            logs_dir=root / "logs",
            dry_run=dry_run,
        )

    def test_transcript_gate_rejects_reversed_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_transcript_gate(
                self._ctx(Path(tmp)),
                {},
                {"transcripts": [{"audio_id": "a", "segments": [{"start": 5, "end": 4, "text": "bad"}]}]},
            )
            self.assertEqual(result["status"], "fail")

    def test_visual_gate_rejects_wrong_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_visual_gate(
                self._ctx(Path(tmp)),
                {"resolution": {"width": 1080, "height": 1920}},
                {"outputs": [{"id": "short_01", "resolution": {"width": 1920, "height": 1080}}]},
            )
            self.assertEqual(result["status"], "fail")


if __name__ == "__main__":
    unittest.main()

