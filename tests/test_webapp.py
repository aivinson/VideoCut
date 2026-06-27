from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from webapp.server import build_brief, safe_upload_filename, unique_destination, resolve_user_path


class WebAppTest(unittest.TestCase):
    def test_build_brief_from_form_payload(self) -> None:
        brief = build_brief(
            {
                "project": "demo",
                "topic": "coffee workflow",
                "platform": "xiaohongshu",
                "target_count": 3,
                "duration_min": 10,
                "duration_max": 45,
                "width": 1080,
                "height": 1920,
            }
        )

        self.assertEqual(brief["topic"], "coffee workflow")
        self.assertEqual(brief["target_count"], 3)
        self.assertEqual(brief["duration_seconds"], {"min": 10, "max": 45})
        self.assertEqual(brief["resolution"], {"width": 1080, "height": 1920})

    def test_build_brief_rejects_bad_duration(self) -> None:
        with self.assertRaises(ValueError):
            build_brief({"topic": "bad", "duration_min": 60, "duration_max": 15})

    def test_resolve_user_path_accepts_relative_paths(self) -> None:
        path = resolve_user_path("inputs/videos", Path("/tmp/default"))
        self.assertTrue(str(path).endswith("inputs/videos"))

    def test_safe_upload_filename_flattens_folder_paths(self) -> None:
        self.assertEqual(safe_upload_filename("folder/sub folder/clip 01.mp4"), "clip 01.mp4")
        self.assertEqual(safe_upload_filename("../bad:name.mov"), "bad_name.mov")

    def test_unique_destination_adds_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.assertEqual(unique_destination(directory, "clip.mp4"), directory / "clip.mp4")
            (directory / "clip.mp4").write_text("x", encoding="utf-8")
            self.assertEqual(unique_destination(directory, "clip.mp4"), directory / "clip_2.mp4")


if __name__ == "__main__":
    unittest.main()
