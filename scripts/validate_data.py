#!/usr/bin/env python3
"""P1 integrity checks without extra dependencies. Full schema engines are P2 scope."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "third_party/skill-movie/vfx-effect-construction-engine/references/vfx-atoms.json"
TAXONOMY = ROOT / "data/taxonomy.json"
MAPPING = ROOT / "adapters/skill_movie_family_map.json"
CURATED = ROOT / "data/curated_atoms.json"
CARDS = ROOT / "examples/effect-cards.json"
SCHEMAS = ROOT / "data/schemas"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify():
    problems = []
    taxonomy, bank, mapping, curated, cards = (
        load(TAXONOMY), load(BANK), load(MAPPING), load(CURATED), load(CARDS)
    )
    atoms = bank["atoms"]
    ids = [a["id"] for a in atoms]
    by_id = {a["id"]: a for a in atoms}
    source_families = set(a["family"] for a in atoms)
    family_map = mapping["family_map"]
    if bank["count"] != len(atoms) or len(atoms) != 566:
        problems.append("Upstream declared atom count differs from 566 / actual length")
    if len(set(ids)) != len(ids):
        problems.append("Duplicate upstream atom IDs")
    if set(family_map) != source_families:
        problems.append("Mapping does not exactly cover upstream families")
    if not all(set(items).issubset(set(taxonomy["families"])) for items in family_map.values()):
        problems.append("Mapping references project families not in taxonomy")
    for schema_name in ["atom", "effect-card", "case"]:
        schema = load(SCHEMAS / (schema_name + ".schema.json"))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            problems.append("Invalid schema declaration: " + schema_name)
        if schema.get("type") != "object":
            problems.append("Non-object root schema: " + schema_name)
    seen = set()
    for row in curated["entries"]:
        aid = row["atom_id"]
        if aid in seen:
            problems.append("Duplicate curated ID " + aid)
        seen.add(aid)
        if aid not in by_id:
            problems.append("Missing curated source ID " + aid)
        elif (row["name_zh"], row["name_en"], row["source_family"]) != (
            by_id[aid]["zh"], by_id[aid]["en"], by_id[aid]["family"]
        ):
            problems.append("Curated copy inconsistent: " + aid)
    if len(curated["entries"]) < 16:
        problems.append("Fewer than 16 curated references")
    card_schema = load(SCHEMAS / "effect-card.schema.json")
    required = set(card_schema["required"])
    allowed = set(card_schema["properties"])
    event_required = set(card_schema["$defs"]["event"]["required"])
    for c in cards["cards"]:
        cid = c.get("card_id", "unknown")
        if not required.issubset(c):
            problems.append("Missing fields on card " + cid)
        if set(c) - allowed:
            problems.append("Undeclared fields on card " + cid)
        for field, domain in [("medium", "mediums"), ("family", "families"),
                              ("intensity", "intensity_levels"), ("continuity_mode", "continuity_modes")]:
            if c.get(field) not in taxonomy[domain]:
                problems.append("Unknown " + field + " on " + cid)
        if set(c.get("genres", [])) - set(taxonomy["genres"]):
            problems.append("Unknown genres on " + cid)
        if set(c.get("style_profiles", [])) - set(taxonomy["style_profiles"]):
            problems.append("Unknown styles on " + cid)
        if set(c.get("related_atom_ids", [])) - set(ids):
            problems.append("Unknown atom references on " + cid)
        for e in c.get("events", []):
            if not event_required.issubset(e):
                problems.append("Incomplete event on " + cid)
            if e.get("phase") not in taxonomy["lifecycle_phases"]:
                problems.append("Unknown lifecycle phase on " + cid)
    if len(cards["cards"]) < 5:
        problems.append("Fewer than 5 cross-genre cards")
    return problems, {"source_atoms": len(atoms), "curated_refs": len(curated["entries"]),
                      "effect_cards": len(cards["cards"]), "families": len(source_families)}


if __name__ == "__main__":
    failures, stats = verify()
    print("Validation:", stats)
    if failures:
        for failure in failures:
            print("FAIL:", failure)
        raise SystemExit(1)
    print("PASS: P1 dataset and routing integrity")
