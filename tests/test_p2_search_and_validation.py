"""P2 tests: filtered retrieval, schema validation, cross-file references.

Failure injection uses in-memory overrides; no vendor files are ever changed.
"""
from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import search_atoms
import validate_data


def example_case():
    """Synthetic schema fixture only: NOT a verified real VFX asset."""
    return {
        "case_id": "fixture.synthetic-rain",
        "title": "Synthetic rainy environment schema fixture",
        "medium": "photoreal-live-action",
        "genres": ["environmental"],
        "style_profiles": ["natural-cinematic"],
        "family_ids": ["environment-weather"],
        "atom_ids": ["vfx_term_134"],
        "description": "Fixture to validate a rain splash reference case structure",
        "source_url": "https://github.com/twj515895394/Cinematic-VFX-Director-Skill",
        "source_id": "skill-movie",
        "license_notes": "Synthetic test-only record; no upstream media embedded",
        "static_preview_url": None,
        "motion_preview_url": None,
        "time_markers": [
            {"label": "start", "description": "Rain begins", "time_seconds": 0.0},
            {"label": "impact", "description": "Drop hits a puddle", "time_seconds": 0.4}
        ],
        "observed_strengths": [],
        "failure_modes": [],
        "reproduction_notes": "Do not publish as a real-world VFX case",
        "asset_distribution": "external-link-only",
    }


class P2SearchTests(unittest.TestCase):
    def test_exact_curated_tag_filter(self):
        result = search_atoms.search("雨滴", tags=["rain"], limit=8)
        self.assertEqual([x["id"] for x in result], ["vfx_term_134"])
        self.assertEqual(result[0]["tags"], ["rain", "weather", "water", "environment", "non-combat"])

    def test_multiple_tags_use_and(self):
        matched = search_atoms.search(tags=["rain", "weather"])
        self.assertEqual([x["id"] for x in matched], ["vfx_term_134"])
        self.assertEqual(search_atoms.search(tags=["rain", "laser"]), [])

    def test_curated_only_never_mutates_original(self):
        items = search_atoms.search(curated_only=True, limit=100)
        self.assertEqual(len(items), 31)
        self.assertTrue(all(x["curated"] and x["tags"] for x in items))

    def test_unannotated_bank_stays_searchable(self):
        x = search_atoms.search(limit=100)
        self.assertTrue(any(not entry["curated"] for entry in x))

    def test_invalid_tag_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown curated tags"):
            search_atoms.search(tags=["definitely-not-a-tag"])

    def test_invalid_role_category_and_limit(self):
        for key, value in [("role", "wrong-role"), ("category", "wrong-category")]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                search_atoms.search(**{key: value})
        for limit in [0, -1, 101, 1.1, True]:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                search_atoms.search(limit=limit)

    def test_invalid_tag_payload(self):
        for tags in ["rain", ["rain", ""], [42]]:
            with self.subTest(tags=tags), self.assertRaises(ValueError):
                search_atoms.search(tags=tags)

    def test_empty_query_stable_order(self):
        results = search_atoms.search("", limit=3)
        self.assertEqual([v["id"] for v in results],
                         ["vfx_term_001", "vfx_term_002", "vfx_term_003"])

    def test_no_match_is_empty(self):
        self.assertEqual(search_atoms.search("term_that_cannot_match_any_atom_923754"), [])

    def test_category_and_family_compatible(self):
        matches = search_atoms.search("雨滴", category="自然", family="environment-weather")
        self.assertEqual(matches[0]["id"], "vfx_term_134")

    def test_upstream_algorithm_matches_unfiltered_order(self):
        upstream = search_atoms.load_upstream_module()
        raw = json.loads(search_atoms.UPSTREAM_BANK.read_text(encoding="utf-8"))["atoms"]
        terms = upstream.query_terms("剑气")
        expected = sorted([(upstream.score(row, terms), row["id"]) for row in raw
                           if upstream.score(row, terms) > 0],
                          key=lambda pair: (-pair[0], int(pair[1].split("_")[-1])))
        actual = search_atoms.search("剑气", limit=10)
        self.assertEqual([x["id"] for x in actual],
                         [item[1] for item in expected[:10]])

    def test_medium_genre_style_are_context_not_false_filters(self):
        base = search_atoms.search("辉光", limit=5)
        framed = search_atoms.search("辉光", medium="anime-2d",
                                     genre="xianxia", style="graphic-ink", limit=5)
        self.assertEqual([x["id"] for x in base], [x["id"] for x in framed])
        self.assertEqual(framed[0]["context"],
                         {"medium": "anime-2d", "genre": "xianxia", "style": "graphic-ink"})


class P2IntegrityTests(unittest.TestCase):
    def test_all_current_data_validates(self):
        problems, stats = validate_data.verify()
        self.assertEqual(problems, [])
        self.assertEqual(stats["source_atoms"], 566)
        self.assertGreaterEqual(stats["schemas_checked"], 5)

    def test_duplicate_upstream_id_is_rejected(self):
        bank = deepcopy(validate_data.load(validate_data.BANK))
        bank["atoms"][1]["id"] = bank["atoms"][0]["id"]
        problems, _ = validate_data.verify(overrides={"bank": bank})
        self.assertTrue(any("Duplicate" in p for p in problems), problems)

    def test_dangling_curated_id_is_rejected(self):
        curated = deepcopy(validate_data.load(validate_data.CURATED))
        curated["entries"][0]["atom_id"] = "vfx_term_999"
        problems, _ = validate_data.verify(overrides={"curated": curated})
        self.assertTrue(any("Missing upstream atom reference" in p for p in problems), problems)

    def test_curated_source_must_exist(self):
        curated = deepcopy(validate_data.load(validate_data.CURATED))
        curated["entries"][0]["source_id"] = "unknown-example-source"
        problems, _ = validate_data.verify(overrides={"curated": curated})
        self.assertTrue(any("Unknown source ID on curated" in p for p in problems), problems)

    def test_duplicate_curated_tags_fail_schema(self):
        curated = deepcopy(validate_data.load(validate_data.CURATED))
        curated["entries"][0]["tags"] = ["rain", "rain"]
        problems, _ = validate_data.verify(overrides={"curated": curated})
        self.assertTrue(any("unique" in p.lower() for p in problems), problems)

    def test_effect_card_illegal_intensity_fails_schema(self):
        cards = deepcopy(validate_data.load(validate_data.CARDS))
        cards["cards"][0]["intensity"] = "L999"
        problems, _ = validate_data.verify(overrides={"cards": cards})
        self.assertTrue(any("L999" in p for p in problems), problems)

    def test_effect_card_missing_event_field_fails_schema(self):
        cards = deepcopy(validate_data.load(validate_data.CARDS))
        del cards["cards"][0]["events"][0]["trigger"]
        problems, _ = validate_data.verify(overrides={"cards": cards})
        self.assertTrue(any("trigger" in p for p in problems), problems)

    def test_effect_card_unknown_atom_reference_fails(self):
        cards = deepcopy(validate_data.load(validate_data.CARDS))
        cards["cards"][0]["related_atom_ids"] = ["vfx_term_999"]
        problems, _ = validate_data.verify(overrides={"cards": cards})
        self.assertTrue(any("Unknown atom ID" in p for p in problems), problems)

    def test_continue_state_id_cannot_change(self):
        cards = deepcopy(validate_data.load(validate_data.CARDS))
        active = next(c for c in cards["cards"] if c["continuity_mode"] == "continue")
        active["effect_state_out"]["id"] = "totally-new-object"
        problems, _ = validate_data.verify(overrides={"cards": cards})
        self.assertTrue(any("Effect state ID changed" in p for p in problems), problems)

    def test_continue_requires_state_in_and_out(self):
        cards = deepcopy(validate_data.load(validate_data.CARDS))
        active = next(c for c in cards["cards"] if c["continuity_mode"] == "continue")
        del active["effect_state_in"]
        problems, _ = validate_data.verify(overrides={"cards": cards})
        self.assertTrue(any("requires both effect states" in p for p in problems), problems)

    def test_taxonomy_mismatch_fails(self):
        taxonomy = deepcopy(validate_data.load(validate_data.TAXONOMY))
        taxonomy["families"].append("fake-family")
        problems, _ = validate_data.verify(overrides={"taxonomy": taxonomy})
        self.assertTrue(any("enum differs" in p for p in problems), problems)

    def test_wrong_vendor_count_fails(self):
        sources = deepcopy(validate_data.load(validate_data.SOURCES))
        entry = next(s for s in sources["sources"] if s["id"] == "skill-movie")
        entry["vendored_file_count"] += 1
        problems, _ = validate_data.verify(overrides={"sources": sources})
        self.assertTrue(any("Vendored file count drift" in p for p in problems), problems)

    def test_valid_synthetic_case_schema(self):
        catalog = {"schema_version": "1.0", "cases": [example_case()]}
        problems, stats = validate_data.verify(overrides={"catalog": catalog})
        self.assertEqual(problems, [])
        self.assertEqual(stats["catalog_cases"], 1)

    def test_invalid_case_url_is_rejected(self):
        case = example_case()
        case["source_url"] = "not-a-uri"
        problems, _ = validate_data.verify(overrides={
            "catalog": {"schema_version": "1.0", "cases": [case]}
        })
        self.assertTrue(any("source_url" in p for p in problems), problems)

    def test_case_timeline_must_be_ordered(self):
        case = example_case()
        case["time_markers"].reverse()
        problems, _ = validate_data.verify(overrides={
            "catalog": {"schema_version": "1.0", "cases": [case]}
        })
        self.assertTrue(any("out of order" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
