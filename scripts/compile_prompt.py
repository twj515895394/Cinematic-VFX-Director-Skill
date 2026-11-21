#!/usr/bin/env python3
"""P3 VFX Effect Card -> safe prompt text compiler.

This is deliberately a deterministic compilation step, NOT a story model,
effect selector, or visual QC engine. The director Agent approves the card.
The original upstream VFX skills and 566-atom source bank remain unchanged.

Install: python -m pip install -r requirements-dev.txt
Run: python scripts/compile_prompt.py --card sample.sword-activation
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CARD_FILE = ROOT / "examples" / "effect-cards.json"
SCHEMA_FILE = ROOT / "data" / "schemas" / "effect-card.schema.json"
BANK_FILE = (ROOT / "third_party" / "skill-movie" /
             "vfx-effect-construction-engine" / "references" / "vfx-atoms.json")

MARKER = "【VFX 特效补充】"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_cards(path=CARD_FILE):
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("cards"), list):
        raise ValueError("Card collection requires an object with a cards list")
    return data["cards"]


def choose_card(cards, card_id):
    matches = [item for item in cards if item.get("card_id") == card_id]
    if len(matches) != 1:
        raise ValueError("Expected one matching card ID, found %d: %s"
                         % (len(matches), card_id))
    return matches[0]


def compile_card(card, *, mode="delta", approved=False):
    """Compile only an already approved Effect Card.

    Delta: source_prompt returned separately without modification.
    Integrated: source bytes are preserved as the exact text prefix, and
    only an explicitly approved VFX appendix is added.
    """
    if mode not in ("delta", "integrated"):
        raise ValueError("Unknown output mode: %s" % mode)
    schema = load_json(SCHEMA_FILE)
    errors = sorted(Draft202012Validator(schema).iter_errors(card),
                    key=lambda e: (list(map(str, e.absolute_path)), e.message))
    if errors:
        first = errors[0]
        location = "/".join(map(str, first.absolute_path)) or "$"
        raise ValueError("Invalid Effect Card [%s]: %s" % (location, first.message))

    bank = load_json(BANK_FILE)["atoms"]
    bank_ids = {row["id"] for row in bank}
    atom_ids = card.get("related_atom_ids", [])
    if len(atom_ids) != len(set(atom_ids)):
        raise ValueError("Duplicate selected atom IDs")
    unknown = sorted(set(atom_ids) - bank_ids)
    if unknown:
        raise ValueError("Unknown upstream atom IDs: " + ", ".join(unknown))

    source = card["source_prompt"]
    delta = card["vfx_delta"]
    if not delta.strip():
        raise ValueError("Empty VFX delta")
    if mode == "integrated":
        if not approved:
            raise PermissionError("Integrated prompt requires explicit --approved")
        if card["editable_scope"] != "explicitly-approved-integration":
            raise PermissionError("Effect Card scope does not authorize integration")
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Integrated prompt requires a nonempty source_prompt")
        compiled = source + "\n\n" + MARKER + "\n" + delta
    else:
        compiled = delta

    # The metadata below is for internal audit / JSON output only. It does
    # not get inserted into the final copyable prompt.
    return {
        "card_id": card["card_id"],
        "mode": mode,
        "source_prompt": source,  # Exact original text (no strip, no rewrite).
        "vfx_delta": delta,
        "compiled_prompt": compiled,
        "immutable_constraints": list(card["immutable_constraints"]),
        "atom_ids_for_audit": list(atom_ids),
        "phase_summary": [
            {"phase": e["phase"], "trigger": e["trigger"], "anchor": e["anchor"]}
            for e in card["events"]
        ],
    }


def render_text(result):
    if result["mode"] == "integrated":
        return result["compiled_prompt"]
    chunks = []
    if result["source_prompt"] is not None:
        chunks.extend(["原始提示词（原文保留）", result["source_prompt"], ""])
    chunks.extend(["建议附加的 VFX 描述", result["vfx_delta"]])
    if result["immutable_constraints"]:
        chunks.extend(["", "不得修改的既有约束（审核备注）",
                       "；".join(result["immutable_constraints"])])
    return "\n".join(chunks)


def main():
    parser = argparse.ArgumentParser(
        description="Compile approved cinematic VFX Effect Card, preserving original text")
    parser.add_argument("--cards", type=Path, default=CARD_FILE,
                        help="JSON object containing cards[] (default examples/effect-cards.json)")
    parser.add_argument("--card", required=True, help="Existing card_id")
    parser.add_argument("--integrated", action="store_true",
                        help="Append VFX delta to original, without rewriting it")
    parser.add_argument("--approved", action="store_true",
                        help="Explicit user approval for integrated output")
    parser.add_argument("--json", action="store_true",
                        help="Return structured audit metadata")
    args = parser.parse_args()
    try:
        card = choose_card(load_cards(args.cards), args.card)
        outcome = compile_card(
            card, mode="integrated" if args.integrated else "delta",
            approved=args.approved)
    except (ValueError, PermissionError, FileNotFoundError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
    else:
        print(render_text(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
