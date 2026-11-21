"""P7 release checks and local review-prep behavior (no actual video model calls)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import release_check
import prepare_visual_evidence
import check_visual_evidence


class P7ReleaseTests(unittest.TestCase):
    def test_all_owned_documentation_links_resolve(self):
        issues, count = release_check.local_link_issues(ROOT)
        self.assertGreater(count, 20)
        self.assertEqual(issues, [])

    def test_five_actual_upstream_snapshots_match_registry(self):
        self.assertEqual(release_check.snapshot_issues(ROOT), [])

    def test_pre_acceptance_release_scope_is_h3_default_and_seedance(self):
        self.assertEqual(release_check.guardrail_issues(ROOT), [])
        issues, stats = release_check.verify(ROOT)
        self.assertEqual(issues, [])
        self.assertEqual(stats["version"], "0.1.0-rc.2")

    def test_skill_has_unique_name_and_bilingual_description(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\\nname: Cinematic-VFX-Director-Skill\\n".replace("\\n", "\n")))
        self.assertIn("description: >-", skill)
        self.assertIn("  中文：", skill)
        self.assertIn("  English:", skill)
        self.assertIn("**中文简介：**", skill)
        self.assertIn("**English overview:**", skill)
        self.assertTrue(readme.startswith("# Cinematic-VFX-Director-Skill\\n".replace("\\n", "\n")))
        self.assertIn("**中文简介：**", readme)
        self.assertIn("**English introduction:**", readme)
        # The original upstream Skill keeps its own identity.
        upstream = (ROOT / "third_party/skill-movie/cinematic-vfx-director/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("cinematic-vfx-director", upstream)
        self.assertNotEqual(skill.split("name:", 1)[1].splitlines()[0].strip(), "cinematic-vfx-director")

    def test_user_acceptance_has_no_misleading_render_pass_claim(self):
        text = (ROOT / "docs/USER_ACCEPTANCE.md").read_text(encoding="utf-8")
        self.assertIn("未", text)
        self.assertIn("Seedance", text)
        self.assertIn("MiniMax H3", text)
        self.assertIn("ffmpeg", text)
        self.assertIn("3–5", text)


class P7VisualEvidenceTests(unittest.TestCase):
    def test_sampling_uses_actual_video_duration(self):
        pts = prepare_visual_evidence.sample_times(12.5, 9)
        self.assertEqual(len(pts), 9)
        self.assertEqual(pts[0], 0.0)
        self.assertGreater(pts[-1], 12.0)
        self.assertTrue(all(pts[i] < pts[i+1] for i in range(8)))

    def test_invalid_sampling_rejected(self):
        for duration, count in [(0, 9), (-1, 9), (2, 1), (2, 31), (90000, 5)]:
            with self.subTest(duration=duration, count=count), self.assertRaises(ValueError):
                prepare_visual_evidence.sample_times(duration, count)

    def test_real_frame_preparation_format_with_mocked_extractor(self):
        """Temporary fake ffmpeg output proves file provenance logic, NOT real video quality."""
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "source.mp4"
            video.write_bytes(b"FAKE VIDEO BYTES - offline test only")
            outdir = Path(d) / "review"
            def fake_run(argv, **kwargs):
                Path(argv[-1]).write_bytes(("FAKE FRAME " + argv[argv.index("-ss")+1]).encode())
                return subprocess.CompletedProcess(argv, 0, "", "")
            with mock.patch.object(prepare_visual_evidence.shutil, "which", return_value="/usr/bin/fake-tool"), \
                 mock.patch.object(prepare_visual_evidence, "probe_video",
                                   return_value={"duration_seconds": 4, "fps": 24, "frame_width": 1920, "frame_height": 1080}), \
                 mock.patch.object(prepare_visual_evidence.subprocess, "run", side_effect=fake_run):
                manifest = prepare_visual_evidence.prepare(video, outdir, "minimax-h3", "S01", count=5)
            self.assertEqual(manifest["review_status"], "not-reviewed")
            self.assertEqual(manifest["actually_inspected_frame_ids"], [])
            self.assertEqual(len(manifest["candidate_frames"]), 5)
            self.assertEqual(manifest["source_sha256"], prepare_visual_evidence.sha256(video))
            self.assertTrue((outdir / "evidence-manifest.json").is_file())
            self.assertFalse((outdir / "qc-report.json").exists())
            for frame in manifest["candidate_frames"]:
                path = outdir / frame["filename"]
                self.assertTrue(path.is_file())
                self.assertEqual(frame["sha256"], prepare_visual_evidence.sha256(path))
            problems, stats = check_visual_evidence.verify(outdir / "evidence-manifest.json", video)
            self.assertEqual(problems, [])
            self.assertEqual(stats["frames"], 5)
            # Byte-level tampering is detected, but the tool does not inspect pixels.
            (outdir / manifest["candidate_frames"][0]["filename"]).write_bytes(b"MODIFIED")
            problems, _ = check_visual_evidence.verify(outdir / "evidence-manifest.json", video)
            self.assertTrue(any("differs" in issue for issue in problems), problems)


    def test_missing_video_does_not_claim_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "review"
            with self.assertRaises(FileNotFoundError):
                prepare_visual_evidence.prepare(Path(d) / "missing.mp4", out,
                                                "minimax-h3", "S01")
            self.assertFalse((out / "evidence-manifest.json").exists())

    def test_models_and_safe_shot_identifier(self):
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "src.mp4"
            video.write_bytes(b"test fixture")
            with self.assertRaises(ValueError):
                prepare_visual_evidence.prepare(video, Path(d) / "out", "kling", "S01")
            with self.assertRaises(ValueError):
                prepare_visual_evidence.prepare(video, Path(d) / "out", "seedance", "../escape")

    def test_no_ffmpeg_returns_explicit_error(self):
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "src.mp4"
            video.write_bytes(b"test fixture")
            with mock.patch.object(prepare_visual_evidence.shutil, "which", return_value=None):
                with self.assertRaisesRegex(FileNotFoundError, "Install ffprobe and ffmpeg"):
                    prepare_visual_evidence.prepare(video, Path(d) / "review", "seedance", "S01")


if __name__ == "__main__":
    unittest.main()
