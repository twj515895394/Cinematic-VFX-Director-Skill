#!/usr/bin/env python3
"""Thin cinematic routing adapter around the unchanged skill-movie search algorithm.

Upstream bank and query/score functions are reused, not reimplemented.
Example:
  python scripts/search_atoms.py "剑气" --family weapon --limit 8
  python scripts/search_atoms.py "rain" --genre environmental --style soft-diffused --json
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


def load_upstream_module():
    spec = importlib.util.spec_from_file_location("upstream_vfx_search", UPSTREAM_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing upstream search script: " + str(UPSTREAM_SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def search(query="", family=None, role=None, medium=None, genre=None, style=None, limit=8):
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    mapping = json.loads(MAP.read_text(encoding="utf-8"))["family_map"]
    for value, key in [(family, "families"), (medium, "mediums"), (genre, "genres"), (style, "style_profiles")]:
        if value and value not in taxonomy[key]:
            raise ValueError("Unknown " + key + ": " + value)
    bank = json.loads(UPSTREAM_BANK.read_text(encoding="utf-8"))["atoms"]
    upstream = load_upstream_module()
    terms = upstream.query_terms(query)
    ranked = []
    for atom in bank:
        candidates = mapping.get(atom["family"], [])
        if family and family not in candidates:
            continue
        if role and atom["role"] != role:
            continue
        score = upstream.score(atom, terms) if terms else 1
        if score:
            ranked.append((score, atom, candidates))
    ranked.sort(key=lambda v: (-v[0], int(v[1]["id"].rsplit("_", 1)[1])))
    return [
        {
            **atom,
            "score": score,
            "project_families": candidates,
            "source_id": "skill-movie",
            "context": {key: value for key, value in
                [("medium", medium), ("genre", genre), ("style", style)] if value},
        }
        for score, atom, candidates in ranked[: max(1, limit)]
    ]


def main():
    p = argparse.ArgumentParser(description="Search upstream 566 VFX atoms with cinematic taxonomy")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--family")
    p.add_argument("--role")
    p.add_argument("--medium")
    p.add_argument("--genre")
    p.add_argument("--style")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        results = search(**{k: v for k, v in vars(args).items() if k != "json"})
    except (ValueError, FileNotFoundError) as ex:
        p.error(str(ex))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("No matching VFX atoms.")
            return 1
        print("ID\tProject Family\tRole\tChinese\tEnglish\tScore")
        for a in results:
            print("%s\t%s\t%s\t%s\t%s\t%s" % (
                a["id"], ",".join(a["project_families"]), a["role"],
                a["zh"], a["en"], a["score"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
