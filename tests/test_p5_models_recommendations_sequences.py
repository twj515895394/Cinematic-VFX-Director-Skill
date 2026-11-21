"""P5: exactly two model adapters, novice 3-5 option gate, and shot continuity."""
from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import adapt_prompt
import check_shot_states
import compile_prompt
import recommend_options

OPTIONS = ROOT / "examples/recommendations"
SEQUENCES = ROOT / "examples/sequences"


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


class P5ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = compile_prompt.load_cards()[0]

    def test_default_is_minimax_h3(self):
        result = adapt_prompt.make_patch(self.card)
        self.assertEqual(result["model"], "minimax-h3")
        self.assertEqual(result["official_mode"], "T2VA")
        self.assertEqual(result["vfx_insertion_target"], "integrated_multimodal_description")

    def test_explicit_seedance_uses_its_own_insertion(self):
        result = adapt_prompt.make_patch(self.card, model="seedance")
        self.assertEqual(result["model"], "seedance")
        self.assertNotEqual(result["model_vfx_insert"], adapt_prompt.make_patch(self.card)["model_vfx_insert"])
        self.assertIn(self.card["vfx_delta"], result["model_vfx_insert"])

    def test_only_two_models_even_when_old_model_name_provided(self):
        profiles = read(adapt_prompt.MODEL_PROFILES)
        self.assertEqual(set(profiles["models"]), {"minimax-h3", "seedance"})
        for model in ["kling", "veo", "wan", "generic", "minimax-h2"]:
            with self.subTest(model=model), self.assertRaises(ValueError):
                adapt_prompt.make_patch(self.card, model=model)

    def test_h3_input_modes_follow_official_skill(self):
        expected = {
            "text": "T2VA", "first-frame": "I2VA", "first-last-frame": "FL2VA",
            "last-frame": "L2VA", "reference": "Ref2VA",
        }
        for mode, name in expected.items():
            with self.subTest(mode=mode):
                result = adapt_prompt.make_patch(self.card, input_mode=mode,
                                                  references_provided=mode != "text")
                self.assertEqual(result["official_mode"], name)
        with self.assertRaises(ValueError):
            adapt_prompt.make_patch(self.card, input_mode="video-edit", references_provided=True)

    def test_seedance_reference_and_edit_modes(self):
        for mode in ["reference", "video-edit", "extension", "first-frame"]:
            with self.subTest(mode=mode):
                r = adapt_prompt.make_patch(self.card, model="seedance", input_mode=mode,
                                            references_provided=True)
                self.assertEqual(r["model"], "seedance")

    def test_image_without_actual_media_is_rejected(self):
        for model in ["minimax-h3", "seedance"]:
            with self.subTest(model=model), self.assertRaisesRegex(ValueError, "actual supplied reference"):
                adapt_prompt.make_patch(self.card, model=model, input_mode="first-frame")

    def test_model_adapter_never_mutates_source_card(self):
        card = deepcopy(self.card)
        baseline = deepcopy(card)
        for model in ["minimax-h3", "seedance"]:
            package = adapt_prompt.make_patch(card, model=model)
            self.assertEqual(package["source_prompt"], baseline["source_prompt"])
            self.assertEqual(package["vfx_delta"], baseline["vfx_delta"])
            self.assertEqual(package["compiled_prompt"], baseline["vfx_delta"])
            self.assertNotIn("vfx_term_", package["model_vfx_insert"])
        self.assertEqual(card, baseline)

    def test_integrated_prompt_still_requires_p3_double_gate(self):
        with self.assertRaises(PermissionError):
            adapt_prompt.make_patch(self.card, integrated=True, approved=True)
        card = deepcopy(self.card)
        card["editable_scope"] = "explicitly-approved-integration"
        with self.assertRaises(PermissionError):
            adapt_prompt.make_patch(card, integrated=True)
        result = adapt_prompt.make_patch(card, integrated=True, approved=True)
        self.assertTrue(result["compiled_prompt"].startswith(card["source_prompt"]))
        self.assertEqual(result["mode"], "integrated")

    def test_model_guides_resolve_locally_or_are_genuine_official_links(self):
        profiles = read(adapt_prompt.MODEL_PROFILES)
        for model in profiles["models"].values():
            for guide in model["source_guides"]:
                if guide.startswith("https://"):
                    self.assertTrue(guide.startswith("https://seed.bytedance.com/"))
                else:
                    self.assertTrue((ROOT / guide).is_file(), guide)


class P5RecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packs = [read(p) for p in sorted(OPTIONS.glob("*.json"))]

    def test_three_realistic_test_input_situations_have_four_options(self):
        self.assertEqual(len(self.packs), 3)
        self.assertEqual({p["input"]["kind"] for p in self.packs},
                         {"image", "scene-text", "prompt-text"})
        for p in self.packs:
            self.assertEqual(len(p["options"]), 4)
            self.assertEqual(p["selection_state"], "awaiting-user-selection")

    def test_offers_await_user_selection_and_no_final_prompt(self):
        for p in self.packs:
            offered = recommend_options.offer(p)
            self.assertEqual(offered["stage"], "awaiting-user-selection")
            self.assertEqual(len(offered["options"]), 4)
            self.assertNotIn("vfx_delta", json.dumps(offered, ensure_ascii=False))
            self.assertNotIn("compiled_prompt", json.dumps(offered, ensure_ascii=False))
            visible = recommend_options.render_offers(offered)
            self.assertIn("请选择方案编号", visible)

    def test_requires_true_user_selection_confirmation(self):
        p = self.packs[0]
        with self.assertRaises(PermissionError):
            recommend_options.select(p, "A1")
        chosen = recommend_options.select(p, "A1", user_confirmed=True)
        self.assertEqual(chosen["selection_state"], "user-selected")
        self.assertEqual(chosen["selected_option_id"], "A1")
        self.assertEqual(chosen["model"], p["model"])
        self.assertEqual(chosen["source_input"], p["input"])

    def test_invalid_selected_option_rejected(self):
        p = self.packs[0]
        with self.assertRaises(ValueError):
            recommend_options.select(p, "A9", user_confirmed=True)

    def test_duplicate_options_rejected(self):
        p = deepcopy(self.packs[0])
        p["options"][1]["id"] = p["options"][0]["id"]
        with self.assertRaisesRegex(ValueError, "Duplicate recommendation option"):
            recommend_options.validate_pack(p)

    def test_option_count_must_be_3_to_5(self):
        for count in [2, 6]:
            p = deepcopy(self.packs[0])
            p["options"] = [deepcopy(p["options"][i % 4]) for i in range(count)]
            with self.subTest(count=count), self.assertRaises(ValueError):
                recommend_options.validate_pack(p)

    def test_unknown_atoms_and_unverified_options_rejected(self):
        p = deepcopy(self.packs[0])
        p["options"][0]["atom_ids"].append("vfx_term_999")
        with self.assertRaisesRegex(ValueError, "Unknown upstream VFX atoms"):
            recommend_options.validate_pack(p)

    def test_cannot_pretend_choice_already_made(self):
        p = deepcopy(self.packs[0])
        p["selected_option_id"] = "A1"
        with self.assertRaises(ValueError):
            recommend_options.validate_pack(p)
        p["selection_state"] = "user-selected"
        recommend_options.validate_pack(p)
        with self.assertRaises(ValueError):
            recommend_options.offer(p)

    def test_seedance_explicit_and_h3_default_in_fixtures(self):
        m = {p["request_id"]: p["model"] for p in self.packs}
        self.assertEqual(m["fixture.paper-flower"], "seedance")
        self.assertEqual(m["fixture.sword-image"], "minimax-h3")


class P5MultiShotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {p.stem: read(p) for p in SEQUENCES.glob("*.json")}

    def test_three_continuous_three_independent_and_reset(self):
        self.assertEqual(len(self.cases), 7)
        self.assertEqual(sum(p["intended_editing"] == "continuous-story" for p in self.cases.values()), 3)
        self.assertEqual(sum(p["intended_editing"] == "independent-montage" for p in self.cases.values()), 3)
        for p in self.cases.values():
            result = check_shot_states.validate_sequence(p)
            self.assertTrue(result["valid"], result["issues"])
            self.assertEqual(result["shot_count"], 3)

    def test_continuation_is_a_real_explicit_connection(self):
        case = self.cases["continuous-sword"]
        result = check_shot_states.validate_sequence(case)
        self.assertEqual(result["connections"], [["S01", "S02"], ["S02", "S03"]])

    def test_montage_never_infers_implicit_connections(self):
        for name in ["montage-weather", "montage-style", "montage-magic"]:
            with self.subTest(name=name):
                result = check_shot_states.validate_sequence(self.cases[name])
                self.assertEqual(result["connections"], [])

    def test_color_anchor_and_status_mismatch_detected(self):
        for key in ["color", "anchor", "status", "id", "scale"]:
            case = deepcopy(self.cases["continuous-sword"])
            case["shots"][1]["effect_state_in"][key] = "incorrect-value"
            with self.subTest(key=key):
                result = check_shot_states.validate_sequence(case)
                self.assertFalse(result["valid"])
                self.assertTrue(any(key in msg for msg in result["issues"]))

    def test_unnamed_reset_cannot_sneak_in(self):
        case = deepcopy(self.cases["mixed-explicit-reset"])
        del case["shots"][1]["reset_reason"]
        self.assertFalse(check_shot_states.validate_sequence(case)["valid"])

    def test_duplicate_shots_and_missing_continuation_rejected(self):
        case = deepcopy(self.cases["continuous-mecha"])
        case["shots"][1]["shot_id"] = case["shots"][0]["shot_id"]
        with self.assertRaisesRegex(ValueError, "Duplicate shot IDs"):
            check_shot_states.validate_sequence(case)
        case = deepcopy(self.cases["continuous-mecha"])
        case["shots"][1]["effect_state_in"] = None
        self.assertFalse(check_shot_states.validate_sequence(case)["valid"])

    def test_independent_accepts_changing_effects_without_forced_rewrite(self):
        case = self.cases["montage-style"]
        before = deepcopy(case)
        result = check_shot_states.validate_sequence(case)
        self.assertTrue(result["valid"])
        self.assertEqual(case, before)


if __name__ == "__main__":
    unittest.main()
