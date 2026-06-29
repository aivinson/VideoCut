from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from webapp.server import build_brief, safe_upload_filename, unique_destination, resolve_user_path
from webapp.video_workflow import analyze_assets, create_hyperframes_project


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

    def test_analyze_assets_counts_uploaded_media(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "inputs" / "videos").mkdir(parents=True)
            (root / "inputs" / "audio").mkdir(parents=True)
            (root / "inputs" / "videos" / "clip.mp4").write_bytes(b"video")
            (root / "inputs" / "audio" / "voice.mp3").write_bytes(b"audio")

            analysis = analyze_assets(root, {"topic": "demo", "target_count": 1})

            self.assertEqual(len(analysis["videos"]), 1)
            self.assertEqual(len(analysis["audio"]), 1)
            self.assertTrue(analysis["suggestions"])

    def test_create_hyperframes_project_writes_composition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "inputs" / "videos").mkdir(parents=True)
            (root / "inputs" / "audio").mkdir(parents=True)
            (root / "inputs" / "videos" / "clip.mp4").write_bytes(b"video")

            manifest = create_hyperframes_project(
                root,
                {
                    "project": "Demo Project",
                    "topic": "demo topic",
                    "platform": "douyin",
                    "target_count": 1,
                    "duration_seconds": {"min": 10, "max": 20},
                    "resolution": {"width": 1080, "height": 1920},
                },
                "Make it energetic.",
            )

            html = Path(manifest["index_html"]).read_text(encoding="utf-8")
            self.assertIn('data-composition-id="videocut-main"', html)
            self.assertIn("Make it energetic.", html)


if __name__ == "__main__":
    unittest.main()
