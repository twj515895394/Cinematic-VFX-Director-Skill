#!/usr/bin/env python3
"""Two-model VFX prompt packaging; default MiniMax H3.

No model API execution. This adapter consumes a reviewed Effect Card using
the existing P3 compiler and emits an additive VFX-only insertion, NOT a
fabricated complete H3/Seedance script. The upstream official H3 prompt skill
is vendored and must be used by an Agent composing a full final prompt.

Example:
 python scripts/adapt_prompt.py --card sample.sword-activation --json
 python scripts/adapt_prompt.py --card sample.rainy-street --model seedance
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from compile_prompt import ROOT, compile_card, choose_card, load_cards

MODEL_PROFILES = ROOT / "data/model_profiles.json"


def model_info(model=None, *, input_mode="text", references_provided=False):
    profiles = json.loads(MODEL_PROFILES.read_text(encoding="utf-8"))
    model = profiles["default_model"] if model is None else model
    if model not in profiles["models"]:
        raise ValueError("Unsupported video model %r; choose MiniMax H3 ('minimax-h3') or Seedance ('seedance')" % model)
    p = profiles["models"][model]
    if input_mode not in p["supported_input_modes"]:
        raise ValueError("Input mode %r not supported by %s" % (input_mode, model))
    if input_mode != "text" and not references_provided:
        raise ValueError("Input mode %r needs actual supplied reference media; do not invent attachments" % input_mode)
    return model, p


def make_patch(card, *, model=None, input_mode="text", references_provided=False,
               integrated=False, approved=False):
    """Return the original (unchanged) + model-aware *insertion* after approval.

    It intentionally does not rewrite scene/camera/shot structure or translate
    Chinese delta into unverified English, and does not invent image labels.
    """
    model, profile = model_info(model, input_mode=input_mode,
                                references_provided=references_provided)
    base = compile_card(card, mode="integrated" if integrated else "delta", approved=approved)
    delta = base["vfx_delta"]
    if model == "minimax-h3":
        # The official full structured prompt has three fields or six Ref2VA
        # fields, plus optional alignment lines. This is explicitly a PATCH.
        insertion = "VFX-only detail for the existing shot (not a new shot): " + delta
        target = ("detailed_description" if input_mode == "reference"
                  else "integrated_multimodal_description")
    else:
        insertion = "仅增强已有镜头的视觉特效，不改变人物、剧情、动作、机位与原声音：" + delta
        target = "existing shot VFX instructions"
    return {
        **base,
        "model": model,
        "model_label": profile["label"],
        "input_mode": input_mode,
        "official_mode": profile["official_modes"][input_mode],
        "prompt_language_policy": profile["prompt_language"],
        "vfx_insertion_target": target,
        "model_vfx_insert": insertion,
        "model_mode_guidance": profile["rules"][input_mode],
        "guardrails": list(profile["guardrails"]),
        "source_guides": list(profile["source_guides"]),
        "output_scope": "model-specific insert; not a complete generated video prompt",
    }


def render_text(package):
    result = [
        "模型：" + package["model_label"] + "（" + package["official_mode"] + "）",
        "添加到 " + package["vfx_insertion_target"] + " 的 VFX 补充：",
        package["model_vfx_insert"],
    ]
    if package["source_prompt"] is not None:
        result.extend(["", "原始内容（完整保留，供最终整合使用）：", package["source_prompt"]])
    result.extend(["", "适配注意：" + package["model_mode_guidance"]])
    return "\n".join(result)


def main():
    p = argparse.ArgumentParser(description="Package verified VFX delta for MiniMax H3 (default) or Seedance")
    p.add_argument("--cards", type=Path, default=ROOT / "examples/effect-cards.json")
    p.add_argument("--card", required=True)
    p.add_argument("--model", help="minimax-h3 (default) or seedance")
    p.add_argument("--input-mode", default="text",
                   choices=["text","first-frame","first-last-frame","last-frame",
                            "reference","video-edit","extension"])
    p.add_argument("--references-provided", action="store_true",
                   help="Only if actual source media was supplied by user")
    p.add_argument("--integrated", action="store_true",
                   help="P3 append-only original+VFX integration (needs card scope and approval)")
    p.add_argument("--approved", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        card = choose_card(load_cards(args.cards), args.card)
        result = make_patch(card, model=args.model, input_mode=args.input_mode,
                            references_provided=args.references_provided,
                            integrated=args.integrated, approved=args.approved)
    except (ValueError, PermissionError, FileNotFoundError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
