#!/usr/bin/env python3
"""Read one P4 cinematic direction profile, or list IDs by axis.

An exact, source-linked routing tool. It does NOT infer a user's genre from
a script and does not misclassify all Sakuga cases as photoreal-film effects.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data/profiles/cinematic_profiles.json"
AXES = {"family": "families", "medium": "mediums",
        "genre": "genres", "style": "styles"}


def get_profile(axis, identifier=None, data=None):
    if axis not in AXES:
        raise ValueError("Unknown axis: " + axis)
    all_profiles = (data if data is not None else json.loads(PROFILES.read_text(encoding="utf-8")))["profiles"][AXES[axis]]
    if identifier is None:
        return [{"id": p["id"]} for p in all_profiles]
    matches = [p for p in all_profiles if p["id"] == identifier]
    if len(matches) != 1:
        raise ValueError("Unknown %s profile: %s" % (axis, identifier))
    return matches[0]


def main():
    p = argparse.ArgumentParser(description="Get verified P4 family/medium/genre/style guidance")
    p.add_argument("--axis", required=True, choices=list(AXES))
    p.add_argument("--id", help="Exact taxonomy ID; omit for a list of available IDs")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        result = get_profile(args.axis, args.id)
    except ValueError as exc:
        p.error(str(exc))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif isinstance(result, list):
        print("\n".join(x["id"] for x in result))
    else:
        for key, value in result.items():
            print("%s: %s" % (key, "、".join(value) if isinstance(value, list) else value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
