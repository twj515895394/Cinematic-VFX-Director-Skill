#!/usr/bin/env python3
"""Verify multi-shot VFX state without inventing storyline continuity.

Continue: exact same effect identity/status/color/anchor/scale at the cut.
Independent: do not infer links or enforce a previous state.
Reset: requires an explicit stated reset reason; no inherited effect state.

This is structural state checking, not pixel-level continuity verification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/schemas/shot-sequence.schema.json"
MODELS = ROOT / "data/model_profiles.json"
STATE_FIELDS = ("id", "status", "color", "anchor", "scale")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_sequence(sequence):
    schema = read(SCHEMA)
    errors = sorted(Draft202012Validator(schema).iter_errors(sequence),
                    key=lambda e: ("/".join(map(str, e.absolute_path)), e.message))
    if errors:
        raise ValueError("Invalid sequence schema: " + errors[0].message)
    profiles = read(MODELS)
    if sequence["model"] not in profiles["models"]:
        raise ValueError("Unsupported video model")
    shots = sequence["shots"]
    ids = [s["shot_id"] for s in shots]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate shot IDs")
    problems = []
    connections = []
    prev = None
    for shot in shots:
        mode = shot["continuity_mode"]
        if mode == "continue":
            if prev is None:
                problems.append("%s: cannot continue without a previous shot" % shot["shot_id"])
            elif prev["effect_state_out"] is None or shot["effect_state_in"] is None:
                problems.append("%s: continue requires previous out + current in state" % shot["shot_id"])
            else:
                a, b = prev["effect_state_out"], shot["effect_state_in"]
                mismatched = [
                    key for key in STATE_FIELDS if a.get(key) != b.get(key)
                ]
                if mismatched:
                    problems.append("%s: state continuity mismatch with %s: %s" %
                                    (shot["shot_id"], prev["shot_id"], ", ".join(mismatched)))
                else:
                    connections.append([prev["shot_id"], shot["shot_id"]])
        elif mode == "reset":
            if not shot.get("reset_reason", "").strip():
                problems.append("%s: reset requires an explicit reset reason" % shot["shot_id"])
        # The user decides independent; even if two adjacent states coincidentally
        # look identical, do not turn montage edits into continuation.
        prev = shot
    return {
        "sequence_id": sequence["sequence_id"], "model": sequence["model"],
        "editing": sequence["intended_editing"], "shot_count": len(shots),
        "connections": connections, "issues": problems,
        "valid": not problems,
    }


def main():
    p = argparse.ArgumentParser(description="Check VFX continuity vs independent montage cuts")
    p.add_argument("--file", type=Path, required=True, help="One sequence JSON")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        result = validate_sequence(read(args.file))
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Sequence %s (%s): %d shots; %d explicit links" %
              (result["sequence_id"], result["editing"], result["shot_count"],
               len(result["connections"])))
        for issue in result["issues"]:
            print("FAIL: " + issue)
        if not result["issues"]:
            print("PASS: all explicitly requested continuity boundaries are consistent")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
