from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from harness.context import RunContext
from harness.io import write_json
from harness.run import run


class HarnessTest(unittest.TestCase):
    def test_dry_run_completes_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = root / "inputs" / "brief.json"
            write_json(
                brief,
                {
                    "topic": "test topic",
                    "target_count": 2,
                    "aspect_ratio": "9:16",
                    "resolution": {"width": 1080, "height": 1920},
                    "duration_seconds": {"min": 15, "max": 60},
                    "constraints": {"avoid_repeated_opening": True},
                },
            )
            ctx = RunContext(
                root=root,
                brief_path=brief,
                videos_dir=root / "inputs" / "videos",
                audio_dir=root / "inputs" / "audio",
                outputs_dir=root / "outputs",
                logs_dir=root / "logs",
                dry_run=True,
            )

            summary = run(ctx)

            self.assertEqual(summary["gate_status"], "pass")
            self.assertTrue((root / "outputs" / "artifacts" / "run-summary.json").exists())
            self.assertTrue((root / "outputs" / "renders" / "short_01.mp4").exists())
            self.assertTrue((root / "outputs" / "subtitles" / "short_01.srt").exists())
            self.assertTrue((root / "logs" / "retrospective.md").exists())


if __name__ == "__main__":
    unittest.main()

