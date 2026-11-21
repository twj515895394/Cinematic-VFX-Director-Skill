#!/usr/bin/env python3
"""Thin cinematic search adapter: reuse skill-movie's original token and ranking logic.

The 566 upstream atoms are never rewritten. Project tags exist only on the
curated subset; medium/genre/style are routing context, NOT an atom filter.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "third_party" / "skill-movie" / "vfx-effect-construction-engine"
UPSTREAM_SCRIPT = VENDOR / "scripts" / "search_vfx_atoms.py"
UPSTREAM_BANK = VENDOR / "references" / "vfx-atoms.json"
MAP = ROOT / "adapters" / "skill_movie_family_map.json"
TAXONOMY = ROOT / "data" / "taxonomy.json"
CURATED = ROOT / "data" / "curated_atoms.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_upstream_module():
    spec = importlib.util.spec_from_file_location("upstream_vfx_search", UPSTREAM_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing upstream search script: " + str(UPSTREAM_SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def search(query="", family=None, role=None, medium=None, genre=None,
           style=None, limit=8, category=None, tags=None, curated_only=False):
    """Return upstream-ranked atoms, with optional project curated tag filters.

    Filters: family (mapped), role and category (native), tags (project curated).
    Context only: medium, genre, style -- upstream has no per-atom applicability.
    Multiple tags use AND. Search without a query retrieves original-ID order.
    """
    taxonomy = read_json(TAXONOMY)
    mapping = read_json(MAP)["family_map"]
    atoms = read_json(UPSTREAM_BANK)["atoms"]
    curated = {row["atom_id"]: row for row in read_json(CURATED)["entries"]}
    native_roles = {a["role"] for a in atoms}
    native_categories = {a["category"] for a in atoms}

    for value, domain in [(family, "families"), (medium, "mediums"),
                          (genre, "genres"), (style, "style_profiles")]:
        if value is not None and value not in taxonomy[domain]:
            raise ValueError("Unknown %s: %s" % (domain, value))
    if role is not None and role not in native_roles:
        raise ValueError("Unknown role: " + role)
    if category is not None and category not in native_categories:
        raise ValueError("Unknown category: " + category)
    if isinstance(limit, bool) or not isinstance(limit, int) or not (1 <= limit <= 100):
        raise ValueError("limit must be an integer from 1 to 100")
    if tags is None:
        tags = []
    if not isinstance(tags, (list, tuple)) or any(
        not isinstance(t, str) or not t.strip() for t in tags
    ):
        raise ValueError("tags must be a list of nonempty strings")
    wanted_tags = {t.strip().casefold() for t in tags}
    known_tags = {t.casefold() for row in curated.values() for t in row.get("tags", [])}
    unknown_tags = wanted_tags - known_tags
    if unknown_tags:
        raise ValueError("Unknown curated tags: " + ", ".join(sorted(unknown_tags)))

    # Keep the original upstream scoring algorithm and its bilingual aliases.
    upstream = load_upstream_module()
    terms = upstream.query_terms(query)
    ranked = []
    for atom in atoms:
        candidates = mapping.get(atom["family"], [])
        annotation = curated.get(atom["id"])
        if family and family not in candidates:
            continue
        if role and atom["role"] != role:
            continue
        if category and atom["category"] != category:
            continue
        if curated_only and annotation is None:
            continue
        atom_tags = {t.casefold() for t in annotation["tags"]} if annotation else set()
        if wanted_tags and not wanted_tags.issubset(atom_tags):
            continue
        rank = upstream.score(atom, terms) if terms else 1
        if rank:
            ranked.append((rank, atom, candidates, annotation))
    ranked.sort(key=lambda row: (-row[0], int(row[1]["id"].rsplit("_", 1)[1])))
    context = {k: v for k, v in [("medium", medium), ("genre", genre),
                                ("style", style)] if v is not None}
    return [
        {
            **atom, "score": score,
            "project_families": candidates, "source_id": "skill-movie",
            "curated": annotation is not None,
            "tags": list(annotation["tags"]) if annotation else [],
            "context": context,
        }
        for score, atom, candidates, annotation in ranked[:limit]
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Search original 566 bilingual VFX atoms with cinematic routing")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--family", help="Project family filter")
    parser.add_argument("--role", help="Exact upstream role filter")
    parser.add_argument("--category", help="Exact upstream category filter")
    parser.add_argument("--tag", action="append", dest="tags",
                        help="Curated tag filter (repeat for AND); only 31 annotated IDs")
    parser.add_argument("--curated-only", action="store_true",
                        help="Search only project-annotated upstream IDs")
    parser.add_argument("--medium", help="Medium routing context (not a filter)")
    parser.add_argument("--genre", help="Genre routing context (not a filter)")
    parser.add_argument("--style", help="Style routing context (not a filter)")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = search(**{k: v for k, v in vars(args).items() if k != "json"})
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if not result:
            print("No matching VFX atoms.")
            return 1
        print("ID\tProject Family\tRole\tChinese\tEnglish\tScore\tTags")
        for atom in result:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                atom["id"], ",".join(atom["project_families"]),
                atom["role"], atom["zh"], atom["en"],
                atom["score"], ",".join(atom["tags"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
