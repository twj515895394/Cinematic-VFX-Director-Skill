"""P4 regression: 90 source-grounded Sakuga references and 46 routing profiles."""
from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from adapters import sakuga_catalog
import search_cases
import lookup_profile
import validate_data


class P4CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(search_cases.CATALOG.read_text(encoding="utf-8"))
        cls.source = json.loads(sakuga_catalog.UPSTREAM.read_text(encoding="utf-8"))

    def test_imported_catalog_is_exactly_90_source_assets(self):
        self.assertEqual(len(self.source["assets"]), 90)
        self.assertEqual(len(self.catalog["cases"]), 90)
        self.assertEqual(len({x["case_id"] for x in self.catalog["cases"]}), 90)
        self.assertEqual(
            {a["id"] for a in self.source["assets"]},
            {c["source_asset_id"] for c in self.catalog["cases"]},
        )

    def test_pinned_upstream_rebuild_matches_committed_cases(self):
        self.assertEqual(sakuga_catalog.build_catalog(self.source), self.catalog)

    def test_nine_elements_and_ten_cases_per_element(self):
        count = {}
        for x in self.catalog["cases"]:
            name = x["source_metadata"]["element"]
            count[name] = count.get(name, 0) + 1
        self.assertEqual(len(count), 9)
        self.assertEqual(set(count.values()), {10})

    def test_animation_metadata_and_external_preview_are_not_fabricated(self):
        for case in self.catalog["cases"]:
            with self.subTest(case=case["case_id"]):
                aid = case["source_asset_id"]
                raw = next(a for a in self.source["assets"] if a["id"] == aid)
                meta = case["source_metadata"]
                self.assertEqual(meta["frames"], raw["frames"])
                self.assertEqual(meta["fps"], raw["fps"])
                self.assertEqual(meta["loop"], raw["loop"])
                self.assertEqual(meta["source_use_cases"], raw["use_cases"])
                self.assertIn("/assets/", case["static_preview_url"])
                self.assertIsNone(case["motion_preview_url"])
                self.assertEqual(case["curation_status"], "metadata-only")
                self.assertEqual(case["atom_ids"], [])
                self.assertEqual(case["genres"], [])

    def test_search_by_original_element_and_form(self):
        self.assertEqual(len(search_cases.search(element="water", limit=100)), 10)
        self.assertEqual(len(search_cases.search(form="impact", limit=100)), 27)
        hits = search_cases.search("water impact", element="water", form="impact")
        self.assertTrue(hits)
        self.assertTrue(all(c["source_metadata"]["element"] == "water" for c in hits))

    def test_search_tag_and_use_cases(self):
        hits = search_cases.search(tag="ice", use_case="spell", limit=100)
        self.assertTrue(hits)
        self.assertTrue(all("ice" in c["source_metadata"]["source_tags"] for c in hits))
        self.assertTrue(all(any("spell" in u for u in c["source_metadata"]["source_use_cases"]) for c in hits))

    def test_search_pairs_reuse_actual_upstream_relation(self):
        results = search_cases.search(paired_with="water_charge_01", limit=100)
        self.assertTrue(any(c["case_id"] == "sakuga.water_column_01" for c in results))
        self.assertEqual(
            [c["case_id"] for c in results],
            [c["case_id"] for c in search_cases.search(paired_with="sakuga.water_charge_01", limit=100)],
        )

    def test_real_case_metadata_filters_do_not_claim_photoreal_support(self):
        self.assertEqual(search_cases.search(medium="photoreal-live-action"), [])
        self.assertEqual(search_cases.search(genre="xianxia"), [])
        self.assertEqual(len(search_cases.search(medium="anime-2d", limit=100)), 90)
        self.assertEqual(len(search_cases.search(style="anime-sakuga", limit=100)), 90)

    def test_case_source_license_and_unknown_visual_review(self):
        for case in self.catalog["cases"]:
            self.assertEqual(case["source_id"], "sakuga-vfx")
            self.assertIn(sakuga_catalog.UPSTREAM_COMMIT, case["source_url"])
            self.assertIn("KanaWorks_AI", case["license_notes"])
            self.assertFalse(case["observed_strengths"])
            self.assertFalse(case["failure_modes"])

    def test_limit_and_loop_filters(self):
        self.assertEqual(len(search_cases.search(limit=5)), 5)
        self.assertTrue(all(c["source_metadata"]["loop"] for c in search_cases.search(loop=True)))
        self.assertTrue(all(not c["source_metadata"]["loop"] for c in search_cases.search(loop=False)))
        for lim in [0, 101, -1, True, "5"]:
            with self.subTest(limit=lim), self.assertRaises(ValueError):
                search_cases.search(limit=lim)


class P4ProfilesTests(unittest.TestCase):
    def test_full_taxonomy_coverage(self):
        p = json.loads(lookup_profile.PROFILES.read_text(encoding="utf-8"))
        t = json.loads(validate_data.TAXONOMY.read_text(encoding="utf-8"))
        for axis, t_axis in [("families", "families"), ("mediums", "mediums"),
                             ("genres", "genres"), ("styles", "style_profiles")]:
            self.assertEqual(set(x["id"] for x in p["profiles"][axis]), set(t[t_axis]))
        self.assertEqual(sum(len(x) for x in p["profiles"].values()), 46)

    def test_source_references_are_present(self):
        p = json.loads(lookup_profile.PROFILES.read_text(encoding="utf-8"))
        for collection in p["profiles"].values():
            for item in collection:
                self.assertTrue(item["read_first"])
                for ref in item["read_first"]:
                    self.assertTrue((ROOT / ref).is_file(), ref)

    def test_exact_profile_lookup_without_unverified_fuzzy_inference(self):
        profile = lookup_profile.get_profile("style", "mj-dreamlike")
        self.assertIn("体积光", profile["vfx_treatment"])
        self.assertEqual(profile["id"], "mj-dreamlike")
        self.assertEqual(len(lookup_profile.get_profile("family")), 14)
        self.assertEqual(len(lookup_profile.get_profile("medium")), 9)
        with self.assertRaises(ValueError):
            lookup_profile.get_profile("style", "unknown-MJ-style")

    def test_validator_accepts_all_real_p4_data(self):
        problems, stats = validate_data.verify()
        self.assertEqual(problems, [])
        self.assertEqual(stats["catalog_cases"], 90)
        self.assertEqual(stats["p4_profiles"], 46)
        self.assertEqual(stats["sakuga_elements"], 9)

    def test_invalid_case_review_label_fails_schema_and_source_gate(self):
        data = deepcopy(json.loads(search_cases.CATALOG.read_text(encoding="utf-8")))
        data["cases"][0]["curation_status"] = "verified-render"
        problems, _ = validate_data.verify(overrides={"catalog": data})
        self.assertTrue(any("Unreviewed Sakuga" in p for p in problems), problems)

    def test_missing_source_pair_is_detected(self):
        data = deepcopy(json.loads(search_cases.CATALOG.read_text(encoding="utf-8")))
        data["cases"][0]["source_metadata"]["paired_source_ids"].append("nonexistent_effect")
        problems, _ = validate_data.verify(overrides={"catalog": data})
        self.assertTrue(any("Broken Sakuga paired effect link" in p for p in problems), problems)

    def test_profile_duplicate_id_is_rejected(self):
        data = deepcopy(json.loads(lookup_profile.PROFILES.read_text(encoding="utf-8")))
        data["profiles"]["families"][1]["id"] = data["profiles"]["families"][0]["id"]
        problems, _ = validate_data.verify(overrides={"profiles": data})
        self.assertTrue(any("coverage/duplicate profile IDs" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
