#!/usr/bin/env python3
"""Human-first VFX option gate for an Agent-created recommendation package.

This DOES NOT infer effects from images or arbitrary prose itself. The Agent
inspects the user's actual scene/image, reads upstream VFX knowledge, and
proposes 3-5 explainable alternatives. This tool validates their structure
and enforces that there is NO final VFX prompt until the user selects.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/schemas/recommendation-package.schema.json"
BANK = ROOT / "third_party/skill-movie/vfx-effect-construction-engine/references/vfx-atoms.json"
MODELS = ROOT / "data/model_profiles.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_pack(pack):
    schema = read(SCHEMA)
    problems = []
    for problem in sorted(Draft202012Validator(schema).iter_errors(pack),
                          key=lambda e: ("/".join(map(str, e.path)), e.message)):
        problems.append("schema [%s]: %s" % ("/".join(map(str, problem.path)) or "$", problem.message))
    if problems:
        raise ValueError("; ".join(problems))
    available = set(read(BANK)["atoms"][i]["id"] for i in range(566))
    models = read(MODELS)["models"]
    if pack["model"] not in models:
        raise ValueError("Unknown model; supported: minimax-h3, seedance")
    if pack["model_selection_source"] == "default" and pack["model"] != read(MODELS)["default_model"]:
        raise ValueError("An unspecified user model must default to MiniMax H3")
    ids = [x["id"] for x in pack["options"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate recommendation option IDs")
    for option in pack["options"]:
        missing = set(option["atom_ids"]) - available
        if missing:
            raise ValueError("Unknown upstream VFX atoms for %s: %s" %
                             (option["id"], ", ".join(sorted(missing))))
    selected = pack.get("selected_option_id")
    if pack["selection_state"] == "awaiting-user-selection" and selected is not None:
        raise ValueError("Cannot preselect a VFX option without a user choice")
    if pack["selection_state"] == "user-selected" and selected not in ids:
        raise ValueError("Selected option does not exist")
    return pack


def offer(pack):
    validate_pack(pack)
    if pack["selection_state"] != "awaiting-user-selection":
        raise ValueError("Offer requires an awaiting-user-selection package")
    # Deliberately do not return vfx_delta, Effect Card, or integrated prompt.
    return {
        "model": pack["model"],
        "model_selection_source": pack["model_selection_source"],
        "summary": pack["input"]["observed_content"],
        "uncertain_details": list(pack["input"]["uncertain_details"]),
        "options": [{
            "id": x["id"], "title": x["title"], "visual_result": x["visual_result"],
            "why_it_fits": x["why_it_fits"], "possible_downside": x["possible_downside"],
            "intensity": x["intensity"]
        } for x in pack["options"]],
        "stage": "awaiting-user-selection",
        "next": "Ask user to select one option (or explicitly request a combination). Do not generate final VFX prompt yet.",
    }


def select(pack, option_id, *, user_confirmed=False):
    validate_pack(pack)
    if pack["selection_state"] != "awaiting-user-selection":
        raise ValueError("A proposal cannot be selected twice")
    if not user_confirmed:
        raise PermissionError("User must explicitly choose before an option can be selected")
    chosen = [x for x in pack["options"] if x["id"] == option_id]
    if len(chosen) != 1:
        raise ValueError("Unknown or ambiguous option: " + option_id)
    # Gate stays a structured brief; actual Effect Card/visual prompt requires
    # the Agent to apply the user's specific shot and timing constraints.
    return {
        "request_id": pack["request_id"], "model": pack["model"],
        "model_selection_source": pack["model_selection_source"],
        "selection_state": "user-selected", "selected_option_id": option_id,
        "selected_option": chosen[0],
        "source_input": pack["input"],
        "scene_facts": pack["scene_facts"],
        "immutable_constraints": pack["immutable_constraints"],
        "next": "Create one approved Effect Card grounded in the selected option and source shot, then use scripts/adapt_prompt.py. Preserve the original.",
    }


def render_offers(result):
    lines = ["已分析画面/场景，推荐以下特效方向（模型：%s）：" % result["model"]]
    for opt in result["options"]:
        lines.extend([
            "%s. %s（%s）" % (opt["id"], opt["title"], opt["intensity"]),
            "   画面变化：%s" % opt["visual_result"],
            "   适合原因：%s" % opt["why_it_fits"],
            "   需要注意：%s" % opt["possible_downside"],
        ])
    if result["uncertain_details"]:
        lines.append("尚不确定：" + "；".join(result["uncertain_details"]))
    lines.append("请选择方案编号；也可以说希望结合哪些方案或保持不加特效。当前未生成最终视频提示词。")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Offer 3-5 Agent-curated VFX options and require user selection")
    p.add_argument("--package", type=Path, required=True)
    p.add_argument("--select", help="User-selected option ID")
    p.add_argument("--user-confirmed", action="store_true",
                   help="Only when the user actually selected the option in conversation")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        pack = read(args.package)
        result = (select(pack, args.select, user_confirmed=args.user_confirmed)
                  if args.select else offer(pack))
    except (ValueError, PermissionError, OSError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    if args.json or args.select:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_offers(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
