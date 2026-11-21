"""P6 tests: real rubric decision logic, synthetic negatives, evidence gate, one-fix policy.

All stored input fixtures are explicitly prompt-design-only. In-memory
"rendered" objects below are schema/logic simulations, NOT video audits.
"""
from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import review_vfx

FILES = ROOT / "tests/fixtures/qc"


def fixtures():
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in FILES.glob("*.json")}


def fake_render_report(name="design-good-sword", role="independent"):
    """Simulate asserted evidence refs; no media has been opened."""
    x = deepcopy(fixtures()[name])
    x["reviewer"]["role"] = role
    x["evidence"] = {
        "kind": "rendered-frames",
        "description": "FAKE evidence for exercising validator only; not actual video frames",
        "asset_refs": ["fixture://not-a-real-asset"],
        "observed_frame_ids": [0, 12, 24],
        "asset_version": "synthetic-test",
    }
    for d in x["scores"].values():
        d["evidence_refs"] = ["frame:12"]
    for issue in x["hard_failures"] + x["findings"]:
        issue["evidence_refs"] = ["frame:12"]
    return x


class P6RubricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = fixtures()

    def test_six_axes_and_nontrivial_positive_and_negative_corpus(self):
        self.assertEqual(len(review_vfx.AXES), 6)
        self.assertEqual(len(self.cases), 16)
        self.assertEqual(sum(name.startswith("design-good-") for name in self.cases), 7)
        self.assertEqual(sum(name.startswith("design-bad-") for name in self.cases), 9)
        self.assertEqual(len({item["shot_id"] for item in self.cases.values()}), 16)

    def test_positive_design_reports_do_not_claim_visual_pass(self):
        for name, item in self.cases.items():
            if not name.startswith("design-good"):
                continue
            with self.subTest(name=name):
                r = review_vfx.evaluate(item)
                self.assertTrue(r["rubric_passed"])
                self.assertGreaterEqual(r["score_total"], 10)
                self.assertEqual(r["verdict"], "design-pass-pending-rendered-review")
                self.assertFalse(r["rendered_video_independently_verified_by_tool"])
                self.assertIsNone(r["next_fix"])

    def test_negative_design_cases_block_and_produce_single_fix(self):
        for name, item in self.cases.items():
            if not name.startswith("design-bad"):
                continue
            with self.subTest(name=name):
                r = review_vfx.evaluate(item)
                self.assertFalse(r["rubric_passed"])
                self.assertEqual(r["verdict"], "design-needs-repair")
                self.assertEqual(len(r["hard_failure_codes"]), 1)
                self.assertEqual(r["next_fix"]["source"], "hard-failure")
                self.assertTrue(r["next_fix"]["suggested_minimal_change"])
                self.assertEqual(r["original_source_prompt"], item["source_prompt"])
                self.assertEqual(r["immutable_constraints"], item["immutable_constraints"])

    def test_hard_failures_block_even_with_twelve_points(self):
        r = review_vfx.evaluate(self.cases["design-bad-no-choice"])
        self.assertEqual(r["score_total"], 12)
        self.assertEqual(r["hard_failure_codes"], ["UNCONFIRMED_CHOICE"])
        self.assertFalse(r["rubric_passed"])

    def test_zero_axis_blocks_even_with_high_total(self):
        x = deepcopy(self.cases["design-good-sword"])
        x["scores"]["timing"]["score"] = 0
        r = review_vfx.evaluate(x)
        self.assertFalse(r["rubric_passed"])
        self.assertIn("timing", r["zero_axes"])
        self.assertEqual(r["next_fix"]["code"], "timing")

    def test_nine_points_requires_repair_but_ten_can_pass(self):
        x = deepcopy(self.cases["design-good-sword"])
        for k in ["space", "timing", "environment"]:
            x["scores"][k]["score"] = 1
        r = review_vfx.evaluate(x)
        self.assertEqual(r["score_total"], 9)
        self.assertFalse(r["rubric_passed"])
        x["scores"]["space"]["score"] = 2
        self.assertEqual(review_vfx.evaluate(x)["score_total"], 10)
        self.assertTrue(review_vfx.evaluate(x)["rubric_passed"])

    def test_findings_override_generic_repair_wording(self):
        x = deepcopy(self.cases["design-good-sword"])
        x["scores"]["timing"]["score"] = 0
        x["findings"].append({
            "axis": "timing", "problem": "Wrong VFX beat",
            "target": "actual sword contact", "minimal_change": "move peak to actual grip closure",
            "evidence_refs": ["script-brief"], "priority": 1,
        })
        r = review_vfx.evaluate(x)
        self.assertEqual(r["next_fix"]["target"], "actual sword contact")
        self.assertEqual(r["next_fix"]["suggested_minimal_change"], "move peak to actual grip closure")

    def test_unknown_hard_code_and_score_not_integer_fail_schema(self):
        for edit in ("code", "score"):
            x = deepcopy(self.cases["design-good-sword"])
            if edit == "code":
                x["hard_failures"] = [{"code": "UNKNOWN", "observation": "test", "evidence_refs": []}]
            else:
                x["scores"]["space"]["score"] = 1.5
            with self.subTest(edit=edit), self.assertRaisesRegex(ValueError, "Invalid QC review"):
                review_vfx.evaluate(x)

    def test_duplicate_hard_failure_code_rejected(self):
        x = deepcopy(self.cases["design-bad-no-choice"])
        x["hard_failures"].append(deepcopy(x["hard_failures"][0]))
        with self.assertRaises(ValueError):
            review_vfx.evaluate(x)

    def test_no_model_beyond_minimax_h3_or_seedance(self):
        x = deepcopy(self.cases["design-good-rain"])
        x["model"] = "veo"
        with self.assertRaisesRegex(ValueError, "Invalid QC review"):
            review_vfx.evaluate(x)


class P6EvidenceTests(unittest.TestCase):
    def test_fake_report_never_claims_independent_verification(self):
        report = fake_render_report()
        r = review_vfx.evaluate(report)
        self.assertEqual(r["verdict"], "reviewer-reported-visual-pass")
        self.assertFalse(r["rendered_video_independently_verified_by_tool"])
        self.assertEqual(r["evidence_kind"], "rendered-frames")

    def test_self_review_stays_pending_independent_audit(self):
        r = review_vfx.evaluate(fake_render_report(role="author"))
        self.assertEqual(r["verdict"], "self-review-pending-independent-review")
        self.assertFalse(r["rendered_video_independently_verified_by_tool"])

    def test_claimed_render_without_inspected_frame_is_rejected(self):
        x = fake_render_report()
        x["evidence"]["observed_frame_ids"] = []
        with self.assertRaises(ValueError):
            review_vfx.evaluate(x)

    def test_claimed_render_without_asset_is_rejected(self):
        x = fake_render_report()
        x["evidence"]["asset_refs"] = []
        with self.assertRaises(ValueError):
            review_vfx.evaluate(x)

    def test_claimed_render_without_frame_specific_citation_is_rejected(self):
        x = fake_render_report()
        x["scores"]["causality"]["evidence_refs"] = []
        with self.assertRaisesRegex(ValueError, "needs evidence_refs"):
            review_vfx.evaluate(x)

    def test_made_up_unobserved_frame_rejected(self):
        x = fake_render_report()
        x["scores"]["space"]["evidence_refs"] = ["frame:999"]
        with self.assertRaisesRegex(ValueError, "Unknown inspected evidence"):
            review_vfx.evaluate(x)

    def test_design_only_report_cannot_claim_frames(self):
        x = deepcopy(fixtures()["design-good-sword"])
        x["evidence"]["observed_frame_ids"] = [0]
        with self.assertRaises(ValueError):
            review_vfx.evaluate(x)

    def test_original_source_prompt_never_mutated_by_audit(self):
        x = deepcopy(fixtures()["design-bad-identity"])
        original = deepcopy(x)
        r = review_vfx.evaluate(x)
        self.assertEqual(x, original)
        self.assertEqual(r["original_source_prompt"], original["source_prompt"])
        self.assertNotIn("compiled_prompt", r)
        self.assertNotIn("rewritten_prompt", r)

    def test_rendered_failure_even_with_independent_reviewer(self):
        x = fake_render_report("design-bad-early-contact")
        # Update each frame citation for a synthetic negative.
        r = review_vfx.evaluate(x)
        self.assertEqual(r["verdict"], "reported-visual-needs-repair")
        self.assertEqual(r["next_fix"]["code"], "EARLY_CONTACT")
        self.assertFalse(r["rendered_video_independently_verified_by_tool"])


if __name__ == "__main__":
    unittest.main()
