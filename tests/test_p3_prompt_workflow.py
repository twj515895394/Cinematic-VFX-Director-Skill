"""P3 functional tests: opt-in integrated output, no input rewrites, ten genres."""
from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import compile_prompt


def scenarios():
    data = json.loads((ROOT / "tests/fixtures/p3_scenarios.json").read_text(encoding="utf-8"))
    samples = compile_prompt.load_cards()
    cards = {card["card_id"]: card for card in samples + data["additional_cards"]}
    return data["scenarios"], cards


class DirectorCompilerTests(unittest.TestCase):
    def test_published_ten_card_catalog_is_directly_runnable(self):
        checks, cards = scenarios()
        published = compile_prompt.load_cards(ROOT / "examples/p3-ten-cards.json")
        self.assertEqual(len(published), 10)
        self.assertEqual({item["card_id"] for item in published},
                         {case["card_id"] for case in checks})
        for card in published:
            with self.subTest(card=card["card_id"]):
                self.assertEqual(card, cards[card["card_id"]])
                result = compile_prompt.compile_card(card)
                self.assertEqual(result["compiled_prompt"], card["vfx_delta"])

    def test_ten_unique_shots_cover_combat_and_noncombat(self):
        checks, cards = scenarios()
        self.assertEqual(len(checks), 10)
        self.assertEqual(len({x["card_id"] for x in checks}), 10)
        genres = set()
        for check in checks:
            card = cards[check["card_id"]]
            self.assertEqual(card["medium"], check["medium"])
            genres.update(card["genres"])
        self.assertGreaterEqual(len(genres), 8)
        self.assertIn("wuxia", genres)
        self.assertIn("environmental", genres)
        self.assertIn("transformation", genres)

    def test_ten_scenarios_compile_without_changing_originals(self):
        checks, cards = scenarios()
        for check in checks:
            with self.subTest(case=check["card_id"]):
                card = deepcopy(cards[check["card_id"]])
                before = deepcopy(card)
                rendered = compile_prompt.compile_card(card)
                self.assertEqual(card, before, "Compiler must not mutate input")
                self.assertEqual(rendered["source_prompt"], card["source_prompt"])
                self.assertEqual(rendered["compiled_prompt"], card["vfx_delta"])
                self.assertTrue(rendered["compiled_prompt"].strip())
                self.assertEqual(rendered["mode"], "delta")
                self.assertNotIn("vfx_term_", rendered["compiled_prompt"])
                self.assertEqual(rendered["phase_summary"][0]["phase"], card["events"][0]["phase"])

    def test_delta_allows_no_original_prompt(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.rainy-street"])
        card["source_prompt"] = None
        result = compile_prompt.compile_card(card)
        self.assertIsNone(result["source_prompt"])
        self.assertEqual(result["compiled_prompt"], card["vfx_delta"])
        self.assertNotIn("原始提示词", compile_prompt.render_text(result))

    def test_integrated_requires_explicit_flag(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["editable_scope"] = "explicitly-approved-integration"
        with self.assertRaises(PermissionError):
            compile_prompt.compile_card(card, mode="integrated")

    def test_integrated_refuses_scope_even_if_flag_given(self):
        _, cards = scenarios()
        with self.assertRaises(PermissionError):
            compile_prompt.compile_card(cards["sample.sword-activation"],
                                        mode="integrated", approved=True)

    def test_integrated_append_only_preserves_original_exactly(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["editable_scope"] = "explicitly-approved-integration"
        card["source_prompt"] = "镜头：右手握住剑柄。\n台词：“不要动！” 5秒。\n "
        before = deepcopy(card)
        result = compile_prompt.compile_card(card, mode="integrated", approved=True)
        self.assertEqual(card, before)
        self.assertEqual(result["source_prompt"], before["source_prompt"])
        self.assertEqual(
            result["compiled_prompt"],
            before["source_prompt"] + "\n\n" + compile_prompt.MARKER + "\n" + before["vfx_delta"],
        )
        self.assertEqual(compile_prompt.render_text(result), result["compiled_prompt"])
        self.assertNotIn("vfx_term_", result["compiled_prompt"])

    def test_integrated_requires_nonempty_original(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["editable_scope"] = "explicitly-approved-integration"
        card["source_prompt"] = None
        with self.assertRaisesRegex(ValueError, "nonempty source_prompt"):
            compile_prompt.compile_card(card, mode="integrated", approved=True)

    def test_invalid_atom_reference_is_rejected(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["related_atom_ids"].append("vfx_term_999")
        with self.assertRaisesRegex(ValueError, "Unknown upstream atom"):
            compile_prompt.compile_card(card)

    def test_duplicate_atom_reference_is_rejected(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["related_atom_ids"].append(card["related_atom_ids"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate selected atom"):
            compile_prompt.compile_card(card)

    def test_invalid_card_structure_is_rejected(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["events"][0].pop("trigger")
        with self.assertRaisesRegex(ValueError, "Invalid Effect Card"):
            compile_prompt.compile_card(card)

    def test_empty_delta_is_rejected(self):
        _, cards = scenarios()
        card = deepcopy(cards["sample.sword-activation"])
        card["vfx_delta"] = "   "
        with self.assertRaisesRegex(ValueError, "Empty VFX delta"):
            compile_prompt.compile_card(card)

    def test_invalid_mode_is_rejected(self):
        _, cards = scenarios()
        with self.assertRaisesRegex(ValueError, "Unknown output mode"):
            compile_prompt.compile_card(cards["sample.sword-activation"], mode="overwrite")

    def test_cannot_select_duplicate_or_missing_card(self):
        _, cards = scenarios()
        example = cards["sample.sword-activation"]
        with self.assertRaisesRegex(ValueError, "Expected one"):
            compile_prompt.choose_card([example, example], example["card_id"])
        with self.assertRaisesRegex(ValueError, "Expected one"):
            compile_prompt.choose_card([example], "missing")

    def test_text_mode_keeps_audit_ids_out_of_prompt(self):
        _, cards = scenarios()
        result = compile_prompt.compile_card(cards["sample.mecha-sequence"])
        visible = compile_prompt.render_text(result)
        self.assertIn("原始提示词（原文保留）", visible)
        self.assertIn("建议附加的 VFX 描述", visible)
        self.assertIn(cards["sample.mecha-sequence"]["source_prompt"], visible)
        self.assertNotIn("vfx_term_", visible)
        self.assertNotIn("effect_state_in", visible)


if __name__ == "__main__":
    unittest.main()
