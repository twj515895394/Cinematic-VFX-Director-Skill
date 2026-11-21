#!/usr/bin/env python3
"""Search 90 external Sakuga cases from the normalized source-derived metadata.

This is a metadata search, NOT an automatic video visual analysis. Source
assets and original catalog remain unchanged under third_party/.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/cases.json"


def read_cases(path=CATALOG):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["cases"]


def search(query="", *, element=None, form=None, family=None, medium=None,
           genre=None, style=None, tag=None, use_case=None, paired_with=None,
           loop=None, limit=20, cases=None):
    items = list(cases) if cases is not None else read_cases()
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ValueError("limit must be an integer between 1 and 100")
    terms = query.casefold().split()
    tag = tag.casefold() if tag else None
    use_case = use_case.casefold() if use_case else None
    if paired_with and paired_with.startswith("sakuga."):
        paired_with = paired_with.split(".", 1)[1]
    results = []
    for c in items:
        meta = c.get("source_metadata", {})
        if element and meta.get("element") != element:
            continue
        if form and meta.get("form") != form:
            continue
        if family and family not in c.get("family_ids", []):
            continue
        # Unlike P2's upstream atom routing context, here medium/style are
        # REAL case metadata filters. Do not broaden anime-game cases into
        # live-action or claim genre where source gives no grounded genre.
        if medium and c.get("medium") != medium:
            continue
        if genre and genre not in c.get("genres", []):
            continue
        if style and style not in c.get("style_profiles", []):
            continue
        if tag and tag not in {v.casefold() for v in meta.get("source_tags", [])}:
            continue
        if use_case and not any(use_case in v.casefold() for v in meta.get("source_use_cases", [])):
            continue
        if paired_with and paired_with not in meta.get("paired_source_ids", []):
            continue
        if loop is not None and meta.get("loop") != loop:
            continue
        haystack = " ".join([c["case_id"], c["title"], c["description"],
                            meta.get("element", ""), meta.get("form", "")]
                           + meta.get("source_tags", []) + meta.get("source_use_cases", [])).casefold()
        if not all(term in haystack for term in terms):
            continue
        results.append(c)
        if len(results) >= limit:
            break
    return results


def main():
    p = argparse.ArgumentParser(description="Search source-grounded Sakuga VFX reference cases")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--element")
    p.add_argument("--form")
    p.add_argument("--family")
    p.add_argument("--medium")
    p.add_argument("--genre")
    p.add_argument("--style")
    p.add_argument("--tag")
    p.add_argument("--use-case", dest="use_case")
    p.add_argument("--paired-with", dest="paired_with")
    p.add_argument("--loop", choices=["yes", "no"], help="Only looping/non-looping source animations")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    args = vars(p.parse_args())
    as_json = args.pop("json")
    if args["loop"] is not None:
        args["loop"] = args["loop"] == "yes"
    try:
        matches = search(**args)
    except ValueError as exc:
        p.error(str(exc))
    if as_json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
    else:
        for c in matches:
            m = c["source_metadata"]
            print("%s | %s/%s | %d frames @ %s fps | %s" %
                  (c["case_id"], m["element"], m["form"], m["frames"], m["fps"], c["source_url"]))
        if not matches:
            print("No matching indexed cases (this corpus contains anime-style game VFX only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
