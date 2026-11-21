"""Regression checks for P1 upstream reuse and thin cinematic routing."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import search_atoms
import validate_data


class UpstreamReuseTests(unittest.TestCase):
    def test_original_upstream_atom_count(self):
        bank = json.loads(search_atoms.UPSTREAM_BANK.read_text(encoding="utf-8"))
        self.assertEqual(bank["count"], 566)
        self.assertEqual(len(bank["atoms"]), 566)
        self.assertEqual(len({a["id"] for a in bank["atoms"]}), 566)

    def test_original_algorithm_loaded_without_rewriting(self):
        upstream = search_atoms.load_upstream_module()
        self.assertTrue(callable(upstream.query_terms))
        self.assertTrue(callable(upstream.score))
        self.assertGreater(upstream.score({"zh": "剑气", "en": "Sword Slash",
            "category": "斩击", "role": "contact-peak", "family": "weapon-motion"},
            upstream.query_terms("剑气")), 0)

    def test_weapon_slash(self):
        matches = search_atoms.search("剑气", family="weapon", limit=8)
        self.assertTrue(matches)
        self.assertTrue(all("weapon" in a["project_families"] for a in matches))

    def test_environmental_rain(self):
        matches = search_atoms.search("雨滴", family="environment-weather", limit=8)
        self.assertTrue(any(a["zh"] == "雨滴扩散" for a in matches))

    def test_sci_fi_technology(self):
        matches = search_atoms.search("laser", family="technology", limit=8)
        self.assertTrue(matches)

    def test_style_is_context_not_fake_atom_filter(self):
        result = search_atoms.search("辉光", medium="semi-realistic-japanese-cg",
                                     style="mj-dreamlike", limit=2)
        self.assertTrue(result)
        self.assertEqual(result[0]["context"]["style"], "mj-dreamlike")

    def test_unknown_category_rejected(self):
        with self.assertRaises(ValueError):
            search_atoms.search("spark", style="unregistered-style")

    def test_data_integrity(self):
        failures, stats = validate_data.verify()
        self.assertEqual(failures, [])
        self.assertGreaterEqual(stats["curated_refs"], 16)
        self.assertGreaterEqual(stats["effect_cards"], 5)


if __name__ == "__main__":
    unittest.main()
