#!/usr/bin/env python3
"""P2 validation: reuse Draft 2020-12 jsonschema, check all cross-file links.

Development dependency is only needed to validate; search stays standard library.
Run: python -m pip install -r requirements-dev.txt
     python scripts/validate_data.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from adapters.sakuga_catalog import build_catalog
import recommend_options
import check_shot_states  # unchanged source -> index

BANK = ROOT / "third_party/skill-movie/vfx-effect-construction-engine/references/vfx-atoms.json"
TAXONOMY = ROOT / "data/taxonomy.json"
MAPPING = ROOT / "adapters/skill_movie_family_map.json"
CURATED = ROOT / "data/curated_atoms.json"
CARDS = ROOT / "examples/effect-cards.json"
CATALOG = ROOT / "data/catalog/cases.json"
SOURCES = ROOT / "data/sources.json"
PROFILES = ROOT / "data/profiles/cinematic_profiles.json"
SAKUGA_BANK = ROOT / "third_party/kanaworks-sakuga-vfx/catalog.json"
SCHEMAS = ROOT / "data/schemas"
MODEL_PROFILES = ROOT / "data/model_profiles.json"
RECOMMENDATIONS_DIR = ROOT / "examples/recommendations"
SEQUENCES_DIR = ROOT / "examples/sequences"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _check(instance, schema, label, problems):
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance),
                    key=lambda e: ("/".join(str(x) for x in e.absolute_path), e.message))
    for e in errors:
        location = "/".join(str(x) for x in e.absolute_path) or "$"
        problems.append("%s [%s]: %s" % (label, location, e.message))


def verify(*, overrides=None):
    """Return problems and stats. Override datasets in tests without writing files."""
    overrides = overrides or {}
    data = {
        "taxonomy": load(TAXONOMY), "bank": load(BANK), "mapping": load(MAPPING),
        "curated": load(CURATED), "cards": load(CARDS),
        "catalog": load(CATALOG), "sources": load(SOURCES),
        "profiles": load(PROFILES),
    }
    data.update(overrides)
    taxonomy, bank, mapping, curated, cards, catalog, sources, profiles = (
        data[k] for k in ("taxonomy", "bank", "mapping", "curated",
                         "cards", "catalog", "sources", "profiles")
    )
    problems = []
    schemas = {}
    for f in sorted(SCHEMAS.glob("*.schema.json")):
        schema = load(f)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            problems.append("Invalid schema %s: %s" % (f.name, exc.message))
        schemas[f.name] = schema

    _check(bank, schemas["upstream-bank.schema.json"], "upstream bank", problems)
    _check(curated, schemas["curated-index.schema.json"], "curated index", problems)
    _check(profiles, schemas["cinematic-profiles.schema.json"], "cinematic profiles", problems)
    model_profiles = load(MODEL_PROFILES)
    _check(model_profiles, schemas["model-profiles.schema.json"], "model profiles", problems)
    if model_profiles.get("default_model") != "minimax-h3" or set(model_profiles.get("models", {})) != {"minimax-h3", "seedance"}:
        problems.append("P5 supports only MiniMax H3 / Seedance and must default to MiniMax H3")
    for mid, profile in model_profiles.get("models", {}).items():
        for mode in profile.get("supported_input_modes", []):
            if mode not in profile.get("official_modes", {}) or mode not in profile.get("rules", {}):
                problems.append("P5 missing model input-mode guidance: %s/%s" % (mid, mode))
        if (mid == "minimax-h3") != profile.get("default"):
            problems.append("P5 default flag inconsistent: " + mid)
        for ref in profile.get("source_guides", []):
            if ref.startswith("https://"):
                if not ref.startswith("https://seed.bytedance.com/"):
                    problems.append("Unexpected external model reference " + ref)
            elif not (ROOT / ref).is_file():
                problems.append("Missing official H3 guide file " + ref)

    # Native upstream atoms have six fields; do not force the richer project
    # atom schema on them. Validate only future local rich atom instances.
    if (ROOT / "data/atoms").exists():
        for path in sorted((ROOT / "data/atoms").glob("*.jsonl")):
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    try:
                        _check(json.loads(line), schemas["atom.schema.json"],
                               "%s:%d" % (path.name, i), problems)
                    except json.JSONDecodeError as exc:
                        problems.append("%s:%d invalid JSON: %s" % (path.name, i, exc))

    if not isinstance(bank, dict) or not isinstance(bank.get("atoms"), list):
        return problems + ["Missing upstream atoms list"], {}
    atoms = bank["atoms"]
    ids = [a.get("id") for a in atoms if isinstance(a, dict)]
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}
    source_families = {a["family"] for a in atoms if isinstance(a, dict) and "family" in a}
    if len(ids) != len(atoms) or len(ids) != len(set(ids)):
        problems.append("Duplicate or missing upstream atom IDs")
    if bank.get("count") != 566 or len(atoms) != 566:
        problems.append("Pinned skill-movie bank requires 566 original atoms")
    expected_families = set(mapping.get("family_map", {}))
    if expected_families != source_families:
        problems.append("Family mapping does not exactly cover upstream families")
    project_families = set(taxonomy.get("families", []))
    for src_family, mapped in mapping.get("family_map", {}).items():
        if not isinstance(mapped, list) or len(mapped) != len(set(mapped)):
            problems.append("Duplicate or non-array mapping for " + src_family)
        elif not set(mapped).issubset(project_families):
            problems.append("Unknown target family in mapping: " + src_family)

    atom_schema = schemas["atom.schema.json"]
    effect_schema = schemas["effect-card.schema.json"]
    case_schema = schemas["case.schema.json"]
    domain_enums = [
        (atom_schema["properties"]["family"]["enum"], "families", "Atom family"),
        (atom_schema["properties"]["lifecycle"]["items"]["enum"], "lifecycle_phases", "Atom lifecycle"),
        (atom_schema["properties"]["intensity_levels"]["items"]["enum"], "intensity_levels", "Atom intensity"),
        (atom_schema["properties"]["medium_notes"]["propertyNames"]["enum"], "mediums", "Atom medium"),
        (effect_schema["properties"]["medium"]["enum"], "mediums", "Card medium"),
        (effect_schema["properties"]["genres"]["items"]["enum"], "genres", "Card genres"),
        (effect_schema["properties"]["style_profiles"]["items"]["enum"], "style_profiles", "Card style"),
        (effect_schema["properties"]["family"]["enum"], "families", "Card family"),
        (effect_schema["properties"]["intensity"]["enum"], "intensity_levels", "Card intensity"),
        (effect_schema["properties"]["continuity_mode"]["enum"], "continuity_modes", "Card continuity"),
        (effect_schema["$defs"]["event"]["properties"]["phase"]["enum"], "lifecycle_phases", "Card event phase"),
        (case_schema["properties"]["medium"]["enum"], "mediums", "Case medium"),
        (case_schema["properties"]["genres"]["items"]["enum"], "genres", "Case genres"),
        (case_schema["properties"]["style_profiles"]["items"]["enum"], "style_profiles", "Case style"),
        (case_schema["properties"]["family_ids"]["items"]["enum"], "families", "Case families"),
    ]
    for enum, domain, label in domain_enums:
        if set(enum) != set(taxonomy.get(domain, [])):
            problems.append("%s schema enum differs from taxonomy.%s" % (label, domain))
    for domain, members in taxonomy.items():
        if isinstance(members, list) and (len(members) != len(set(members))
                                          or any(not isinstance(s, str) or not s for s in members)):
            problems.append("Duplicate/invalid taxonomy members in " + domain)

    source_ids = [x.get("id") for x in sources.get("sources", [])]
    if len(source_ids) != len(set(source_ids)):
        problems.append("Duplicate source IDs")
    source_set = set(source_ids)
    for source in sources.get("sources", []):
        sid = source.get("id", "unknown")
        if not source.get("url"):
            problems.append("Missing source URL: " + sid)
        if source.get("vendor_path"):
            vendor = ROOT / source["vendor_path"]
            if not vendor.is_dir() or not vendor.resolve().is_relative_to(ROOT.resolve()):
                problems.append("Vendor path missing or outside root: " + sid)
            elif source.get("vendored_file_count") != len([p for p in vendor.rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts
                    and p.suffix not in (".pyc", ".pyo")]):
                problems.append("Vendored file count drift: " + sid)
        for integration in source.get("integration", []):
            if not (ROOT / integration).is_file():
                problems.append("Missing integrated path: %s (%s)" % (integration, sid))

    curated_ids = set()
    for row in curated.get("entries", []):
        rid = row.get("atom_id", "")
        if rid in curated_ids:
            problems.append("Duplicate curated ID " + rid)
        curated_ids.add(rid)
        if row.get("source_id") not in source_set:
            problems.append("Unknown source ID on curated " + rid)
        if rid not in by_id:
            problems.append("Missing upstream atom reference " + rid)
        elif (row.get("name_zh"), row.get("name_en"), row.get("source_family")) != (
                by_id[rid].get("zh"), by_id[rid].get("en"), by_id[rid].get("family")):
            problems.append("Curated metadata differs from original upstream " + rid)

    # P4 profiles are thin cinematic adapters, each with a verifiable source path.
    profile_axes = {"families": "families", "mediums": "mediums",
                    "genres": "genres", "styles": "style_profiles"}
    for key, domain in profile_axes.items():
        items = profiles.get("profiles", {}).get(key, [])
        keys = [p.get("id") for p in items]
        if len(keys) != len(set(keys)) or set(keys) != set(taxonomy.get(domain, [])):
            problems.append("P4 %s coverage/duplicate profile IDs differ from taxonomy.%s" % (key, domain))
        for p in items:
            for ref in p.get("read_first", []):
                target = ROOT / ref
                if not target.is_file() or not target.resolve().is_relative_to(ROOT.resolve()):
                    problems.append("Missing upstream P4 reference: " + ref)
    for ref in profiles.get("upstream_primary_files", {}).values():
        if not (ROOT / ref).is_file():
            problems.append("P4 primary source reference missing: " + ref)

    # The 90 cases must stay a projection of the original pinned metadata.
    sakuga_source = load(SAKUGA_BANK)
    if len(sakuga_source.get("assets", [])) != 90:
        problems.append("Pinned Sakuga catalog must contain 90 assets")
    case_map = {a.get("id"): a for a in sakuga_source.get("assets", [])}
    if len(case_map) != len(sakuga_source.get("assets", [])):
        problems.append("Duplicate Sakuga source asset IDs")
    if "catalog" not in overrides and catalog != build_catalog(sakuga_source):
        problems.append("Normalized case index drifted from original Sakuga metadata")

    all_atom_ids = set(ids)
    card_ids = set()
    for i, card in enumerate(cards.get("cards", [])):
        cid = card.get("card_id", "<missing-%d>" % i)
        _check(card, effect_schema, "card " + cid, problems)
        if cid in card_ids:
            problems.append("Duplicate effect card ID " + cid)
        card_ids.add(cid)
        for aid in card.get("related_atom_ids", []):
            if aid not in all_atom_ids:
                problems.append("Unknown atom ID %s in card %s" % (aid, cid))
        in_state, out_state = card.get("effect_state_in"), card.get("effect_state_out")
        if card.get("continuity_mode") == "continue" and (
                not isinstance(in_state, dict) or not isinstance(out_state, dict)):
            problems.append("Continue card requires both effect states: " + cid)
        if isinstance(in_state, dict) and isinstance(out_state, dict) and (
                in_state.get("id") != out_state.get("id")):
            problems.append("Effect state ID changed within card " + cid)
    if len(cards.get("cards", [])) < 5:
        problems.append("Fewer than five cross-genre effect cards")

    case_ids = set()
    for i, case in enumerate(catalog.get("cases", [])):
        cid = case.get("case_id", "<missing-%d>" % i)
        _check(case, case_schema, "reference case " + cid, problems)
        if cid in case_ids:
            problems.append("Duplicate reference case ID " + cid)
        case_ids.add(cid)
        if case.get("source_id") not in source_set:
            problems.append("Unknown source ID on case " + cid)
        for aid in case.get("atom_ids", []):
            if aid not in all_atom_ids:
                problems.append("Unknown atom ID %s on case %s" % (aid, cid))
        meta = case.get("source_metadata")
        if case.get("source_id") == "sakuga-vfx":
            aid = case.get("source_asset_id")
            if aid not in case_map:
                problems.append("Missing Sakuga asset ID for " + cid)
            if not isinstance(meta, dict):
                problems.append("Missing source metadata for " + cid)
            elif not set(meta.get("paired_source_ids", [])).issubset(set(case_map)):
                problems.append("Broken Sakuga paired effect link for " + cid)
            if case.get("curation_status") != "metadata-only":
                problems.append("Unreviewed Sakuga case mislabelled as visually-reviewed: " + cid)
        times = [m["time_seconds"] for m in case.get("time_markers", [])
                 if "time_seconds" in m]
        if times != sorted(times):
            problems.append("Time markers out of order on case " + cid)

    # P5: validate the actual option-first workflow and all multi-shot samples.
    recommendation_files = sorted(RECOMMENDATIONS_DIR.glob("*.json"))
    sequence_files = sorted(SEQUENCES_DIR.glob("*.json"))
    if len(recommendation_files) < 3:
        problems.append("P5 requires at least 3 novice scene/image recommendation examples")
    if len(sequence_files) < 7:
        problems.append("P5 requires 3 continuous, 3 independent and one reset example")
    all_options = 0
    for path in recommendation_files:
        pack = load(path)
        _check(pack, schemas["recommendation-package.schema.json"], "recommendation " + path.name, problems)
        try:
            recommend_options.validate_pack(pack)
        except ValueError as exc:
            problems.append("Recommendation invalid (%s): %s" % (path.name, exc))
        if pack.get("selection_state") != "awaiting-user-selection" or pack.get("selected_option_id") is not None:
            problems.append("Recommendation must await explicit user selection: " + path.name)
        if pack.get("model") not in model_profiles.get("models", {}):
            problems.append("Recommendation uses unsupported model: " + path.name)
        all_options += len(pack.get("options", []))
    sequence_types = {}
    for path in sequence_files:
        seq = load(path)
        _check(seq, schemas["shot-sequence.schema.json"], "sequence " + path.name, problems)
        sequence_types[seq["intended_editing"]] = sequence_types.get(seq["intended_editing"], 0) + 1
        if seq.get("model") not in model_profiles.get("models", {}):
            problems.append("Sequence uses unsupported model: " + path.name)
        try:
            result = check_shot_states.validate_sequence(seq)
        except ValueError as exc:
            problems.append("Sequence invalid (%s): %s" % (path.name, exc))
        else:
            problems.extend(path.name + ": " + issue for issue in result["issues"])
    if sequence_types.get("continuous-story", 0) < 3 or sequence_types.get("independent-montage", 0) < 3:
        problems.append("P5 requires at least three continuous and three independent sequence examples")

    stats = {
        "source_atoms": len(atoms), "unique_atom_ids": len(set(ids)),
        "curated_refs": len(curated.get("entries", [])),
        "curated_tags": len({t for x in curated.get("entries", [])
                              for t in x.get("tags", [])}),
        "effect_cards": len(cards.get("cards", [])),
        "catalog_cases": len(catalog.get("cases", [])),
        "families": len(source_families), "schemas_checked": len(schemas),
        "p4_profiles": sum(len(p) for p in profiles.get("profiles", {}).values()),
        "sakuga_elements": len({x.get("element") for x in sakuga_source.get("assets", [])}),
        "p5_models": len(model_profiles["models"]),
        "p5_recommendation_packs": len(recommendation_files),
        "p5_option_count": all_options,
        "p5_shot_sequences": len(sequence_files),
    }
    return problems, stats


def main():
    try:
        problems, stats = verify()
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print("FAIL: unable to load or validate data: %s" % exc)
        return 1
    print("Validation:", stats)
    if problems:
        for item in problems:
            print("FAIL:", item)
        return 1
    print("PASS: upstream VFX, project schemas and cross-file integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
